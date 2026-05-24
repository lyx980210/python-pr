# 🤖 AI 对话助手 (ollamatest)

基于 **Ollama 本地大模型** 的多场景 AI 对话工具，支持命令行和 Web 两种交互方式。

---

## ✨ 核心特性

- **本地运行**：基于 Ollama，数据不出本地，无需联网
- **多模型切换**：根据任务复杂度选择不同模型（代码专用 / 通用 / 复杂任务）
- **6 大场景**：通用对话、Python、Java、SQL、调试排错、Shell 脚本
- **上下文记忆**：多轮对话保持上下文，支持追问和连续聊天
- **会话管理**：多会话切换、持久化存储、会话上限保护
- **Markdown 渲染**：代码高亮、表格、列表等完美显示
- **双模交互**：命令行模式（轻量快速）+ Web 页面（可视化美观）

---

## 🚀 快速开始

### 前提条件

1. 安装 [Ollama](https://ollama.com/) 并拉取所需模型：

```bash
ollama pull qwen2.5-coder:7b
ollama pull deepseek-r1:1.5b
ollama pull deepseek-r1:8b
```

2. 确保 Ollama 服务运行在 `http://localhost:11434`

### 安装依赖

```bash
cd D:\Pycharm\Code\ollamatest
pip install -r requirements.txt
```

### 启动

**方式一：命令行交互（推荐尝鲜）**

```bash
python tests/03_chat_memory.py
```

进入后对话命令：

| 输入 | 效果 |
|------|------|
| 你的问题 | 发送给 AI |
| `switch=java` | 切换到 Java 场景 |
| `switch=debug` | 切换到调试场景 |
| `clear` | 清空对话历史 |
| `exit` | 退出 |

**方式二：Web 页面（推荐日常使用）**

```bash
python web/webpage.py
```

浏览器打开 `http://127.0.0.1:5000`，支持模型切换、场景切换、多会话管理。

---

## 📦 项目结构

```
ollamatest/
├── config/
│   └── settings.py          # 模型配置、生成参数、硬件配置、会话上限
├── core/
│   ├── chat_manager.py      # 对话管理器（持久化、场景切换、会话计数）
│   └── llm_client.py        # LLM 调用客户端（单轮/多轮/流式）
├── prompts/                 # 6 大场景提示词库
│   ├── general.py           # 通用对话
│   ├── python.py            # Python 代码
│   ├── java.py              # Java 后端
│   ├── sql.py               # SQL 查询
│   ├── debug.py             # 调试排错
│   └── shell.py             # Shell 脚本
├── data/
│   └── sessions/            # 会话持久化文件（JSON）
├── templates/
│   └── index.html           # Web 前端页面（Markdown 渲染 + 代码高亮）
├── web/
│   └── webpage.py           # Flask 后端（REST API）
├── tests/                   # 测试脚本
├── examples/                # 调用示例
└── requirements.txt         # Python 依赖
```

---

## 🤖 模型配置

| 标识 | 模型 | 适用场景 |
|------|------|----------|
| `code` | `qwen2.5-coder:7b` | 代码生成、补全 |
| `general` | `deepseek-r1:1.5b` | 通用对话、轻量任务 |
| `advanced` | `deepseek-r1:8b` | 复杂推理、长文本 |

---

## 📝 场景列表

| 标识 | 说明 |
|------|------|
| `general` | 通用对话 |
| `python` | Python 代码助手 |
| `java` | Java 代码助手 |
| `sql` | SQL 查询助手 |
| `debug` | 调试排错专家 |
| `shell` | Shell 脚本助手 |

---

## 🌐 API 接口

启动 Web 服务后提供以下 REST API：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | Web 对话页面 |
| POST | `/api/chat` | 发送消息（带上下文记忆） |
| GET | `/api/get_models` | 获取可用模型列表 |
| POST | `/api/switch_model` | 切换模型 |
| POST | `/api/switch_scene` | 切换场景（清空历史） |
| GET | `/api/get_scenes` | 获取可用场景列表 |
| GET | `/api/get_history` | 获取对话历史 |
| POST | `/api/clear_history` | 清空对话（保留提示词） |
| POST | `/api/reset_session` | 创建新会话 |
| POST | `/api/load_session` | 切换到指定会话并加载历史 |
| GET | `/api/list_sessions` | 列出所有历史会话 |
| POST | `/api/delete_session` | 删除指定会话 |

---

## 🔧 配置说明

编辑 `config/settings.py`：

```python
# Ollama 服务地址
OLLAMA_HOST = "http://localhost:11434"

# 模型配置
CODE_MODEL = "qwen2.5-coder:7b"     # 代码专用
GENERAL_MODEL = "deepseek-r1:1.5b"  # 通用场景
ADVANCED_MODEL = "deepseek-r1:8b"   # 复杂任务

# 生成参数（可按场景微调）
GENERATION_CONFIG = {
    'temperature': 0.5,   # 创造性：代码补全 0.2-0.3 / 算法 0.4-0.5 / 调试 0.1-0.2
    'top_p': 0.9,         # 输出多样性
    'num_ctx': 4096,      # 上下文窗口大小
}

# 会话上限（超出后新建会话会提示删除历史）
MAX_SESSIONS = 50
```

---

## 📄 License


