# 从各个场景文件导入提示词（统一入口，方便调用）
from .general import GENERAL_PROMPT
from .python import PYTHON_PROMPT
from .java import JAVA_PROMPT
from .sql import SQL_PROMPT
from .debug import DEBUG_PROMPT
from .shell import SHELL_PROMPT

# 场景映射表（用标识快速切换）
PROMPT_MAP = {
    "general": GENERAL_PROMPT,
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "sql": SQL_PROMPT,
    "debug": DEBUG_PROMPT,
    "shell": SHELL_PROMPT
}