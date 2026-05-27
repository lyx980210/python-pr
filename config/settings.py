# Ollama 服务配置
import os

OLLAMA_HOST = "http://localhost:11434"

# 模型配置（按场景分级）
CODE_MODEL = "qwen2.5-coder:7b"     # 代码专用
GENERAL_MODEL = "deepseek-r1:1.5b"  # 通用场景（之前尾部有多余空格已修复）
ADVANCED_MODEL = "deepseek-r1:8b"   # 复杂任务

# 生成参数
GENERATION_CONFIG = {
    'temperature': 0.5,   # 创造性（代码补全 0.2-0.3 / 算法 0.4-0.5 / 调试 0.1-0.2）
    'top_p': 0.9,         # 输出多样性
    'num_ctx': 4096,      # 上下文窗口
    'stop': ["\n###"],    # 停止标记
}

# 会话上限
MAX_SESSIONS = 20  # 最多保留的会话数，超出后新建会话会提示删除历史

# 硬件配置
HARDWARE_CONFIG = {
    'gpu_layers': 30,                        # GPU 加速层数
    'main_gpu': 0,                           # 主 GPU 索引
    'cpu_threads': min(6, os.cpu_count() - 1),  # CPU 线程数
    'cpu_cores': 2,                          # CPU 核心数
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',                          # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_dir': os.path.join(os.path.dirname(__file__), '..', 'logs'),  # 日志目录
    'file_name': 'app.log',                   # 日志文件名
    'backup_count': 30,                       # 保留历史日志文件数
    'encoding': 'utf-8',                      # 文件编码
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    'max_file_size': 200 * 1024 * 1024,       # 单个日志文件最大大小（200MB）
    'compress': True,                         # 是否压缩历史日志文件
}
