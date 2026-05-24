import ollama

# 【关键修改】显式创建客户端，强制指定 Ollama 的本地地址
client = ollama.Client(host='http://localhost:11434')

# 初始化对话历史，加一段代码生成提示词
messages = [
    {
        "role": "system",
        "content": """你是一名资深工业级开发工程师，严格遵守以下规则输出：
1.  只输出可直接编译/运行的代码，代码符合对应语言的行业规范，无语法错误
2.  代码内带清晰、简洁的中文注释，关键逻辑必须标注，不写无效废话注释
3.  先输出完整代码块，代码结束后，仅补充1-2条核心运行说明/注意事项，不解释基础语法
4.  禁止输出任何与代码需求无关的冗余内容、客套话、无关科普"""
    }
]

while True:
    user_input = input("你: ")
    if user_input.lower() == "exit":
        break
    messages.append({"role": "user", "content": user_input})

    # 【关键修改】用显式创建的 client 调用模型
    response = client.chat(
        model="deepseek-r1:1.5b",  # 你也可以换成 deepseek-r1:8b
        messages=messages
    )

    ai_response = response["message"]["content"]
    print(f"AI: {ai_response}")
    messages.append({"role": "assistant", "content": ai_response})