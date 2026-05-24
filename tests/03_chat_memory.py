from core.chat_manager import ChatManager
import uuid

if __name__ == '__main__':
    print("=== 带上下文记忆 + 持久化的连续对话 ===")
    print("指令：switch=场景 | clear=清空 | exit=退出")

    # 使用固定 session_id 实现持久化（重启后恢复历史）
    session_id = "cli_session"

    # 创建对话管理器（自动加载历史，如果存在的话）
    chat = ChatManager(default_scene="general", session_id=session_id)

    while True:
        user_input = input("你: ").strip()

        if user_input == "exit":
            print(f"💾 会话已保存到: data/sessions/{session_id}.json")
            break
        if user_input == "clear":
            chat.clear_history()
            continue
        if user_input.startswith("switch="):
            chat.switch_scene(user_input.split("=")[1])
            continue

        # 使用 ChatManager.chat() 统一入口（自动记忆检索 + 保存）
        ai_reply = chat.chat(user_input)

        print(f"AI: {ai_reply}")
