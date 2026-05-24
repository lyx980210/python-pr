import ollama
from config.settings import OLLAMA_HOST, CODE_MODEL, GENERATION_CONFIG
from prompts import PROMPT_MAP

# 创建全局 Ollama 客户端
client = ollama.Client(host=OLLAMA_HOST)


# ==============================================
# 函数1：单轮对话（无记忆，基础调用）
# 适合：一次性提问、测试、简单需求
# ==============================================
def get_llm_response(user_input, scene="general", model=CODE_MODEL):
    """
    单轮对话调用（无上下文记忆）
    :param user_input: 用户问题
    :param scene: 场景标识
    :param model: 模型名称
    :return: AI 回复字符串
    """
    system_prompt = PROMPT_MAP.get(scene, PROMPT_MAP["general"])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    try:
        response = client.chat(
            model=model,
            messages=messages,
            options={
                'temperature': GENERATION_CONFIG.get('temperature', 0.7),
                'top_p': GENERATION_CONFIG.get('top_p', 0.9),
            }
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        return f"Ollama 响应错误 (status={e.status_code}): {e.error}"
    except ollama.RequestError as e:
        return f"无法连接 Ollama 服务 ({OLLAMA_HOST})，请确认服务已启动。详情: {e}"
    except Exception as e:
        return f"调用失败: {str(e)}"


# ==============================================
# 函数2：多轮对话（带上下文记忆，命令行模式使用）
# 适合：连续聊天、追问、上下文连贯对话
# ==============================================
def chat_with_memory(chat_manager, model=None):
    """
    带上下文记忆的对话调用（命令行模式）
    :param chat_manager: 对话管理器（自带历史）
    :param model: 模型名称，默认使用 chat_manager.model
    :return: AI 回复字符串
    """
    selected_model = model or chat_manager.model
    try:
        response = client.chat(
            model=selected_model,
            messages=chat_manager.get_history(),
            options={
                'temperature': GENERATION_CONFIG.get('temperature', 0.7),
                'top_p': GENERATION_CONFIG.get('top_p', 0.9),
            }
        )
        return response["message"]["content"]
    except ollama.ResponseError as e:
        return f"Ollama 响应错误 (status={e.status_code}): {e.error}"
    except ollama.RequestError as e:
        return f"无法连接 Ollama 服务 ({OLLAMA_HOST})，请确认服务已启动。详情: {e}"
    except Exception as e:
        return f"调用失败: {str(e)}"


# ==============================================
# 函数3：流式对话（打字机效果）
# 适合：需要实时输出、提升用户体验
# ==============================================
def chat_stream(chat_manager, model=None):
    """
    流式对话（yield 逐 token 输出）
    :param chat_manager: 对话管理器
    :param model: 模型名称
    :yield: 逐 token 字符串
    """
    selected_model = model or chat_manager.model
    try:
        stream = client.chat(
            model=selected_model,
            messages=chat_manager.get_history(),
            options={
                'temperature': GENERATION_CONFIG.get('temperature', 0.7),
                'top_p': GENERATION_CONFIG.get('top_p', 0.9),
            },
            stream=True
        )
        full_reply = ""
        for chunk in stream:
            token = chunk["message"]["content"]
            full_reply += token
            yield token
        # 流结束后将完整回复加入历史并持久化
        chat_manager.add_ai_message(full_reply)
        chat_manager._save_to_file()
    except ollama.ResponseError as e:
        yield f"\n[Ollama 响应错误 (status={e.status_code}): {e.error}]"
    except ollama.RequestError as e:
        yield f"\n[无法连接 Ollama 服务 ({OLLAMA_HOST})，请确认服务已启动]"
    except Exception as e:
        yield f"\n[调用失败: {str(e)}]"
