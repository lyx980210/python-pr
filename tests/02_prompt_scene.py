# 学习目标：调用独立分场景的提示词
from core.llm_client import get_llm_response

if __name__ == '__main__':
    print("=== 本地大模型 分场景独立提示词测试 ===")

    # 1. 通用场景
    print("\n【通用场景】")
    print(get_llm_response("大模型学习第一步做什么", scene="general"))

    # 2. Python场景（独立提示词）
    print("\n【Python代码场景】")
    print(get_llm_response("写一个批量重命名文件的脚本", scene="python"))

    # 3. Debug调试场景（独立提示词）
    print("\n【调试场景】")
    print(get_llm_response("Python报错：NameError: name 'a' is not defined", scene="debug"))

    # 4. Java场景（独立提示词）
    print("\n【Java场景】")
    print(get_llm_response("写一个SpringBoot接口", scene="java"))