from core.llm_client import get_llm_response

user_question=input("请输入内容：")

print(get_llm_response(user_question, "python"))
