from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from core.chat_manager import ChatManager, DATA_DIR
from core.llm_client import chat_with_memory  # 保留兼容（命令行模式使用）
from prompts import PROMPT_MAP
from config.settings import CODE_MODEL, GENERAL_MODEL, ADVANCED_MODEL, MAX_SESSIONS
import uuid
from datetime import timedelta
import os
import sys
import json


# 获取当前文件所在目录（web 目录）
basedir = os.path.abspath(os.path.dirname(__file__))

# 获取项目根目录（向上一级）
project_root = os.path.abspath(os.path.join(basedir, '..'))

# 将项目根目录添加到 Python 路径（确保能导入 core 和 prompts）
sys.path.insert(0, project_root)

# 指定 templates 文件夹路径（在项目根目录下）
template_dir = os.path.join(project_root, 'templates')

# 创建 Flask 应用，指定模板文件夹
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
CORS(app)

# 存储每个会话的 ChatManager 实例
chat_sessions = {}

# 可用模型列表
AVAILABLE_MODELS = {
    'code': {'name': 'Qwen2.5-Coder 7B (代码专用)', 'value': CODE_MODEL},
    'general': {'name': 'DeepSeek-R1 1.5B (通用场景)', 'value': GENERAL_MODEL},
    'advanced': {'name': 'DeepSeek-R1 8B (复杂任务)', 'value': ADVANCED_MODEL}
}


def get_chat_manager():
    """获取或创建当前会话的 ChatManager"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True

    session_id = session['session_id']

    if session_id not in chat_sessions:
        # 从 session 中获取选择的模型，默认使用通用模型
        selected_model = session.get('selected_model', GENERAL_MODEL)
        # 传入 session_id 用于持久化，重启后可恢复历史
        chat_sessions[session_id] = ChatManager(default_scene="general", model=selected_model, session_id=session_id)

    return chat_sessions[session_id]


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/get_models', methods=['GET'])
def get_models():
    """获取所有可用模型"""
    try:
        models = [
            {'id': key, 'name': value['name'], 'value': value['value']}
            for key, value in AVAILABLE_MODELS.items()
        ]
        current_model = session.get('selected_model', GENERAL_MODEL)

        return jsonify({
            'success': True,
            'models': models,
            'current_model': current_model
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/switch_model', methods=['POST'])
def switch_model():
    """切换模型（会重置当前会话）"""
    try:
        data = request.get_json()
        model_id = data.get('model_id', '').strip()

        if not model_id or model_id not in AVAILABLE_MODELS:
            return jsonify({'error': '无效的模型ID'}), 400

        new_model = AVAILABLE_MODELS[model_id]['value']

        # 保存到 session
        session['selected_model'] = new_model

        # 重置当前会话的 ChatManager（传入 session_id 确保持久化）
        if 'session_id' in session:
            session_id = session['session_id']
            if session_id in chat_sessions:
                # 保留当前场景
                old_scene = chat_sessions[session_id].current_scene
                # 创建新的 ChatManager（带 session_id 实现持久化）
                chat_sessions[session_id] = ChatManager(default_scene=old_scene, model=new_model, session_id=session_id)

        return jsonify({
            'success': True,
            'message': f'已切换模型：{AVAILABLE_MODELS[model_id]["name"]}',
            'current_model': new_model
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求 - 使用 ChatManager.chat() 统一入口"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        chat_manager = get_chat_manager()

        # 统一使用 ChatManager.chat() → 内部用 Ollama SDK 调用 + 自动管理历史
        ai_reply = chat_manager.chat(user_message, model=chat_manager.model)

        return jsonify({
            'success': True,
            'reply': ai_reply,
            'current_scene': get_current_scene(chat_manager),
            'current_model': chat_manager.model
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/switch_scene', methods=['POST'])
def switch_scene():
    """切换场景 - 会清空历史并重新加载提示词"""
    try:
        data = request.get_json()
        scene = data.get('scene', '').strip()

        if not scene:
            return jsonify({'error': '场景名称不能为空'}), 400

        # 验证场景是否存在
        if scene not in PROMPT_MAP:
            available_scenes = ', '.join(PROMPT_MAP.keys())
            return jsonify({
                'error': f'场景 "{scene}" 不存在',
                'available_scenes': available_scenes
            }), 400

        chat_manager = get_chat_manager()
        chat_manager.switch_scene(scene)

        return jsonify({
            'success': True,
            'message': f'已切换场景：{scene}，对话历史已重置',
            'current_scene': scene
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """清空对话历史（保留系统提示词）"""
    try:
        chat_manager = get_chat_manager()
        chat_manager.clear_history()

        return jsonify({
            'success': True,
            'message': '对话历史已清空'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_history', methods=['GET'])
def get_history():
    """获取完整对话历史"""
    try:
        chat_manager = get_chat_manager()
        history = chat_manager.get_history()

        # 格式化历史记录，排除系统提示词
        formatted_history = []
        for msg in history[1:]:  # 跳过第一条系统提示
            formatted_history.append({
                'role': msg['role'],
                'content': msg['content']
            })

        return jsonify({
            'success': True,
            'history': formatted_history,
            'current_scene': get_current_scene(chat_manager)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_scenes', methods=['GET'])
def get_scenes():
    """获取所有可用场景"""
    try:
        scenes = list(PROMPT_MAP.keys())
        return jsonify({
            'success': True,
            'scenes': scenes
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """重置会话（完全清空）—— 立即创建新会话并落盘"""
    try:
        # 检查会话上限
        current_count = ChatManager.session_count()
        if current_count >= MAX_SESSIONS:
            return jsonify({
                'success': False,
                'session_limit_reached': True,
                'message': f'会话已超过最大值 {MAX_SESSIONS}，请先删除历史会话。',
                'max_sessions': MAX_SESSIONS,
                'current_count': current_count
            })

        if 'session_id' in session:
            old_session_id = session['session_id']
            if old_session_id in chat_sessions:
                del chat_sessions[old_session_id]
            session.pop('session_id', None)

        # 立即创建新会话（触发 get_chat_manager() → 生成新 UUID → ChatManager 落盘）
        new_mgr = get_chat_manager()
        new_session_id = new_mgr.session_id

        return jsonify({
            'success': True,
            'message': '会话已重置',
            'new_session_id': new_session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/list_sessions', methods=['GET'])
def list_sessions():
    """列出所有历史会话"""
    try:
        sessions = ChatManager.list_sessions()
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete_session', methods=['POST'])
def delete_session():
    """删除指定会话"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '').strip()
        if not session_id:
            return jsonify({'error': '会话 ID 不能为空'}), 400

        result = ChatManager.delete_session(session_id)
        return jsonify({
            'success': result,
            'message': '会话已删除' if result else '会话不存在'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/load_session', methods=['POST'])
def load_session():
    """
    加载指定会话：切换后端 session_id + 加载历史消息
    返回该会话的完整聊天记录（不含 system prompt）
    """
    try:
        data = request.get_json()
        target_session_id = data.get('session_id', '').strip()
        if not target_session_id:
            return jsonify({'error': '会话 ID 不能为空'}), 400

        # 1. 检查目标会话文件是否存在
        filepath = os.path.join(DATA_DIR, f"{target_session_id}.json")
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': '会话文件不存在'}), 404

        # 2. 清理旧会话，创建新 ChatManager（自动从文件加载）
        old_session_id = session.get('session_id', '')
        if old_session_id and old_session_id in chat_sessions:
            del chat_sessions[old_session_id]

        # 3. 更新 Flask session cookie 到目标会话
        session['session_id'] = target_session_id
        session.permanent = True

        # 4. 创建 ChatManager（内部 _load_from_file() → 完整恢复 messages）
        new_mgr = ChatManager(session_id=target_session_id)
        scene = new_mgr.current_scene
        model = new_mgr.model
        chat_sessions[target_session_id] = new_mgr

        # 5. 从 ChatManager.messages 提取历史（跳过 system prompt）
        history_messages = []
        for msg in new_mgr.messages[1:]:
            history_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        return jsonify({
            'success': True,
            'message': f'已切换到会话 {target_session_id}',
            'history': history_messages,
            'current_scene': scene,
            'current_model': model,
            'session_id': target_session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/rename_session', methods=['POST'])
def rename_session():
    """重命名指定会话"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '').strip()
        new_name = data.get('name', '').strip()
        if not session_id or not new_name:
            return jsonify({'error': '参数不能为空'}), 400
        result = ChatManager.rename_session(session_id, new_name)
        return jsonify({'success': result, 'name': new_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/toggle_pin', methods=['POST'])
def toggle_pin():
    """切换会话置顶状态"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '').strip()
        if not session_id:
            return jsonify({'error': '会话 ID 不能为空'}), 400
        new_pinned = ChatManager.toggle_pin(session_id)
        if new_pinned is None:
            return jsonify({'success': False, 'error': '会话文件不存在'}), 404
        return jsonify({'success': True, 'pinned': new_pinned})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_current_scene(chat_manager):
    """从系统提示词推断当前场景"""
    if not chat_manager.messages:
        return "unknown"

    system_prompt = chat_manager.messages[0].get('content', '')

    # 反向匹配场景
    for scene, prompt in PROMPT_MAP.items():
        if prompt == system_prompt:
            return scene

    return "custom"


if __name__ == '__main__':
    print(f"\n🚀 Flask 应用启动")
    print(f"📂 模板文件夹: {app.template_folder}")
    print(f"🤖 可用模型:")
    for key, value in AVAILABLE_MODELS.items():
        print(f"   - {value['name']}: {value['value']}")
    print(f"🌐 访问地址: http://127.0.0.1:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
