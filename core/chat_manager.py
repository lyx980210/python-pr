import ollama
import json
import os
import re
from datetime import datetime
from config.settings import OLLAMA_HOST, GENERAL_MODEL, GENERATION_CONFIG
from prompts import PROMPT_MAP

# 数据存储目录（项目根目录下）
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sessions")


class ChatManager:
    """
    对话上下文管理器 —— 带持久化记忆
    功能：自动保存/恢复对话历史、切换提示词、清空记忆、相似问题检索
    """

    def __init__(self, default_scene="general", model=None, session_id=None):
        """
        初始化对话管理器
        :param default_scene: 默认场景名称
        :param model: 使用的模型，默认为 GENERAL_MODEL
        :param session_id: 会话 ID，用于持久化（不传则自动生成）
        """
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.current_scene = default_scene
        self.model = model or GENERAL_MODEL
        self.messages = []
        self.session_id = session_id

        # 确保数据目录存在
        os.makedirs(DATA_DIR, exist_ok=True)

        # 尝试加载历史会话
        loaded = self._load_from_file() if self.session_id else False

        if not loaded:
            self._load_system_prompt()
            # 新创建的会话立即落盘（确保 list_sessions 能读到）
            self._save_to_file()

        print("\n" + "=" * 80)
        print("[INFO] ChatManager 初始化完成")
        print(f"[INFO] 当前场景: {self.current_scene}")
        print(f"[INFO] 使用模型: {self.model}")
        print(f"[INFO] 会话 ID: {self.session_id}")
        print(f"[INFO] 可用场景: {list(PROMPT_MAP.keys())}")
        print(f"[INFO] 历史消息数: {len(self.messages) - 1} 条" if loaded else "")
        print("=" * 80 + "\n")

    # ==================== 持久化核心 ====================

    def _get_filepath(self):
        """获取当前会话的存储文件路径"""
        return os.path.join(DATA_DIR, f"{self.session_id}.json")

    def _save_to_file(self):
        """保存当前对话到 JSON 文件"""
        if not self.session_id:
            return
        filepath = self._get_filepath()
        data = {
            "session_id": self.session_id,
            "scene": self.current_scene,
            "model": self.model,
            "messages": self.messages,
            "summary": self._generate_summary(),
            "pinned": getattr(self, 'pinned', False),
            "custom_name": getattr(self, 'custom_name', ''),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_from_file(self):
        """从 JSON 文件恢复对话历史"""
        filepath = self._get_filepath()
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.messages = data.get("messages", [])
            self.current_scene = data.get("scene", self.current_scene)
            self.model = data.get("model", self.model)
            self.pinned = data.get("pinned", False)
            self.custom_name = data.get("custom_name", "")
            print(f"[INFO] 已恢复上次会话 ({len(self.messages) - 1} 条历史消息)")
            return True
        except Exception as e:
            print(f"[WARN] 恢复会话失败: {e}")
            return False

    def _generate_summary(self):
        """生成会话摘要（取首条用户消息前 50 字）"""
        for msg in self.messages:
            if msg["role"] == "user":
                return msg["content"][:50]
        return "新会话"

    # ==================== 相似问题检索 ====================

    def _extract_keywords(self, text, top_n=5):
        """简单关键词提取（按词频）"""
        # 提取中文词（双字及以上）和英文词
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        english_words = re.findall(r'[a-zA-Z]{2,}', text.lower())
        all_words = chinese_words + english_words

        # 过滤停用词
        stopwords = {"什么", "怎么", "如何", "一个", "这个", "那个", "可以", "使用",
                     "the", "and", "for", "how", "what", "can", "that", "this"}
        filtered = [w for w in all_words if w not in stopwords]

        # 按频率排序
        from collections import Counter
        return [w for w, _ in Counter(filtered).most_common(top_n)]

    def _find_similar_qa(self, user_message, max_results=3):
        """
        在当前会话中搜索相似的历史问答
        :param user_message: 当前用户问题
        :param max_results: 最多返回几条
        :return: [{"q": "...", "a": "..."}, ...]
        """
        keywords = self._extract_keywords(user_message)
        if not keywords:
            return []

        scored = []
        history = self.messages[1:]  # 跳过系统提示词
        for i in range(len(history) - 1):
            if history[i]["role"] == "user" and history[i + 1]["role"] == "assistant":
                q_text = history[i]["content"]
                a_text = history[i + 1]["content"]

                # 关键词命中评分（忽略大小写）
                score = sum(1 for kw in keywords if kw.lower() in q_text.lower())
                if score > 0:
                    scored.append((score, q_text, a_text))

        # 按分数降序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"q": q, "a": a} for score, q, a in scored[:max_results]]

    # ==================== 对话核心 ====================

    def _load_system_prompt(self):
        """加载系统提示词"""
        system_prompt = PROMPT_MAP.get(self.current_scene, PROMPT_MAP["general"])
        self.messages = [{"role": "system", "content": system_prompt}]
        print(f"[INFO] 已加载场景 '{self.current_scene}' 的提示词 ({len(system_prompt)} 字符)\n")

    def switch_scene(self, scene):
        """切换场景（会清空历史，重新加载提示词）"""
        if scene not in PROMPT_MAP:
            print(f"[ERROR] 场景 '{scene}' 不存在！可用场景: {list(PROMPT_MAP.keys())}")
            return False

        self.current_scene = scene
        prompt = PROMPT_MAP[scene]
        self.messages = [{"role": "system", "content": prompt}]

        # 切换场景后自动保存
        self._save_to_file()

        print("\n" + "-" * 40)
        print(f"[INFO] 已切换场景：{scene}（历史已清空）")
        print("-" * 40 + "\n")
        return True

    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.messages.append({"role": role, "content": content})

    def chat(self, user_message: str, model: str = None) -> str:
        """
        发送消息并获取回复（带记忆增强）
        """
        try:
            # 1. 搜索历史中相似问答
            similar_qa = self._find_similar_qa(user_message, max_results=3)

            # 2. 构建消息列表
            messages = [self.messages[0]]  # 系统提示词

            # 如果有相似历史，注入记忆提示
            if similar_qa:
                memory_hint = "【历史记忆 - 你之前回答过类似问题，可参考以下对话内容】\n"
                for i, qa in enumerate(similar_qa, 1):
                    memory_hint += f"{i}. 用户问过: {qa['q'][:200]}\n   你当时回答: {qa['a'][:300]}\n"
                messages.append({"role": "system", "content": memory_hint})
                print(f"[INFO] 注入了 {len(similar_qa)} 条历史记忆到上下文")

            # 添加历史对话（不含系统提示词）
            messages.extend(self.messages[1:])

            # 添加当前问题
            self.add_message("user", user_message)
            messages.append({"role": "user", "content": user_message})

            # 3. 选择模型
            selected_model = model or self.model

            print("\n" + "=" * 80)
            print(f"[INFO] 当前场景: {self.current_scene}")
            print(f"[INFO] 使用模型: {selected_model}")
            print("=" * 80 + "\n")

            # 4. 调用 Ollama
            response = self.client.chat(
                model=selected_model,
                messages=messages,
                options={
                    'temperature': GENERATION_CONFIG.get('temperature', 0.7),
                    'top_p': GENERATION_CONFIG.get('top_p', 0.9),
                    'num_ctx': GENERATION_CONFIG.get('num_ctx', 4096),
                }
            )

            ai_reply = response["message"]["content"]
            self.add_message("assistant", ai_reply)

            # 5. 持久化保存
            self._save_to_file()

            return ai_reply

        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            print(f"[ERROR] {error_msg}\n")
            return error_msg

    def add_user_message(self, content):
        """添加用户问题"""
        self.add_message("user", content)

    def add_ai_message(self, content):
        """添加 AI 回复"""
        self.add_message("assistant", content)

    def get_history(self):
        """获取完整对话历史"""
        return self.messages

    def clear_history(self):
        """清空对话（除了提示词）"""
        system_prompt = self.messages[0]
        self.messages = [system_prompt]
        self._save_to_file()
        print("[INFO] 对话历史已清空（保留系统提示词）\n")

    # ==================== 记忆检索 ====================

    def search_history(self, keyword, limit=5):
        """
        在当前会话中搜索包含关键词的对话
        :param keyword: 搜索关键词
        :param limit: 最多返回条数
        :return: [{"role": "...", "content": "..."}, ...]
        """
        results = []
        for msg in self.messages[1:]:
            if keyword.lower() in msg["content"].lower():
                results.append({"role": msg["role"], "content": msg["content"][:200]})
                if len(results) >= limit:
                    break
        return results

    @staticmethod
    def list_sessions():
        """列出所有历史会话文件"""
        os.makedirs(DATA_DIR, exist_ok=True)
        sessions = []
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                fpath = os.path.join(DATA_DIR, fname)
                try:
                    # 获取文件时间戳
                    stat = os.stat(fpath)
                    created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id", fname[:-5]),
                        "scene": data.get("scene", "unknown"),
                        "model": data.get("model", "unknown"),
                        "summary": data.get("summary", ""),
                        "pinned": data.get("pinned", False),
                        "custom_name": data.get("custom_name", ""),
                        "msg_count": len(data.get("messages", [])) - 1,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    })
                except Exception:
                    pass
        # 按更新时间降序排序（最新的在前）
        # 置顶的排在前面，然后按更新时间降序
        sessions.sort(key=lambda x: (not x.get("pinned", False), x.get("updated_at", "")), reverse=False)
        # 上面用 reverse=False：pinned=True→(False,time)排前，pinned=False→(True,time)排后
        # 但时间需要降序，所以调整为：按 (not pinned, -time) 排
        sessions.sort(key=lambda x: (0 if x.get("pinned") else 1, ""), reverse=False)
        # 简化版：先分两组，再各自排序
        pinned_sessions = [s for s in sessions if s.get("pinned")]
        unpinned_sessions = [s for s in sessions if not s.get("pinned")]
        pinned_sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        unpinned_sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        sessions = pinned_sessions + unpinned_sessions
        return sessions

    @staticmethod
    def delete_session(session_id):
        """删除指定会话文件"""
        filepath = os.path.join(DATA_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    @staticmethod
    def rename_session(session_id, new_name):
        """重命名会话（更新 JSON 文件中的 custom_name）"""
        filepath = os.path.join(DATA_DIR, f"{session_id}.json")
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["custom_name"] = new_name.strip()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def toggle_pin(session_id):
        """切换会话的置顶状态，返回新的 pinned 值"""
        filepath = os.path.join(DATA_DIR, f"{session_id}.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            new_pinned = not data.get("pinned", False)
            data["pinned"] = new_pinned
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return new_pinned
        except Exception:
            return None

    @staticmethod
    def session_count():
        """统计当前会话文件总数"""
        os.makedirs(DATA_DIR, exist_ok=True)
        count = 0
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if not data.get("pinned", False):
                        count += 1
                except Exception:
                    count += 1  # 文件损坏也算
        return count
