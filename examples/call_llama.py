import ollama
from config.settings import OLLAMA_HOST, CODE_MODEL

ollama_client = ollama.Client(host=OLLAMA_HOST)
# 正确的调用方式 - messages 应该是字典列表
response = ollama_client.chat(
    model=CODE_MODEL,
    messages=[{'role': 'user', 'content': '你是什么模型'}],
    think='high'
)
print(response)
