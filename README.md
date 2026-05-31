# 🤖 AI 对话助手 (ollamatest)

基于 **Ollama 本地大模型** 的多场景 AI 对话工具，支持命令行和 Web 两种交互方式。

---

## 目录

1. [项目整体架构设计](#1-项目整体架构设计)
2. [环境安装与配置](#2-环境安装与配置)
3. [项目配置说明](#3-项目配置说明)
4. [项目运行方式](#4-项目运行方式)
5. [硬件要求与部署](#5-硬件要求与部署)
6. [API 接口文档](#6-api-接口文档)
7. [常见问题](#7-常见问题)

---

## 1. 项目整体架构设计

### 1.1 项目概述

本项目是一个基于 Ollama 本地大模型的 AI 对话助手，支持多场景对话、多模型切换、会话管理等功能。所有数据本地运行，无需联网，安全可控。

### 1.2 核心功能

| 功能模块 | 说明 |
|---------|------|
| **本地运行** | 基于 Ollama，数据不出本地，无需联网 |
| **多模型切换** | 根据任务复杂度选择不同模型（代码专用 / 通用 / 复杂任务） |
| **6 大场景** | 通用对话、Python、Java、SQL、调试排错、Shell 脚本 |
| **上下文记忆** | 多轮对话保持上下文，支持追问和连续聊天 |
| **会话管理** | 多会话切换、持久化存储、会话上限保护、置顶、重命名、搜索 |
| **Markdown 渲染** | 代码高亮、表格、列表等完美显示 |
| **双模交互** | 命令行模式（轻量快速）+ Web 页面（可视化美观） |
| **日志系统** | 应用日志 + 启动日志，支持自动压缩 |

### 1.3 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                               │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   命令行模式 (CLI)   │    │        Web 页面 (Flask)         │ │
│  │ tests/03_chat_memory │    │     templates/index.html        │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         业务逻辑层                               │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   会话管理器        │    │        LLM 调用客户端            │ │
│  │ core/chat_manager   │    │       core/llm_client            │ │
│  │  - 持久化存储       │    │   - 单轮对话                     │ │
│  │  - 场景切换         │    │   - 多轮对话                     │ │
│  │  - 会话计数         │    │   - 流式对话                     │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         提示词层                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    prompts/                                  ││
│  │  general.py │ python.py │ java.py │ sql.py │ debug.py │ shell.py ││
│  └─────────────────────────────────────────────────────────────┐│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         配置层                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    config/settings.py                        ││
│  │   - Ollama 服务配置                                          ││
│  │   - 模型配置                                                 ││
│  │   - 生成参数                                                 ││
│  │   - 硬件配置                                                 ││
│  │   - 日志配置                                                 ││
│  └─────────────────────────────────────────────────────────────┐│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据存储层                               │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   会话持久化        │    │           日志文件               │ │
│  │   data/sessions/    │    │           logs/                  │ │
│  │   - JSON 格式       │    │   - app.log (应用日志)           │ │
│  │   - 自动保存        │    │   - appBoot.log (启动日志)       │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         外部服务                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Ollama 服务                                ││
│  │              http://localhost:11434                           ││
│  │   - qwen2.5-coder:7b (代码专用)                              ││
│  │   - deepseek-r1:1.5b (通用场景)                              ││
│  │   - deepseek-r1:8b (复杂任务)                                ││
│  └─────────────────────────────────────────────────────────────┐│
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 项目目录结构

```
ollamatest/
├── config/
│   └── settings.py          # 统一配置文件（模型、日志、硬件等）
├── core/
│   ├── __init__.py
│   ├── chat_manager.py      # 会话管理器（持久化、场景切换、会话管理）
│   └── llm_client.py        # LLM 调用客户端（单轮/多轮/流式）
├── prompts/                 # 6 大场景提示词库
│   ├── __init__.py
│   ├── prompt_library.py    # 提示词注册中心
│   ├── general.py           # 通用对话
│   ├── python.py            # Python 代码
│   ├── java.py              # Java 后端
│   ├── sql.py               # SQL 查询
│   ├── debug.py             # 调试排错
│   └── shell.py             # Shell 脚本
├── data/
│   └── sessions/            # 会话持久化文件（JSON 格式）
├── templates/
│   └── index.html           # Web 前端页面（Markdown 渲染 + 代码高亮）
├── web/
│   └── webpage.py           # Flask 后端（REST API + 流式响应）
├── logs/
│   ├── app.log              # 应用日志（最大 200MB，自动压缩）
│   └── appBoot.log          # 启动日志（最大 50MB，自动压缩）
├── tests/                   # 测试脚本
│   ├── 02_prompt_scene.py   # 场景切换测试
│   ├── 03_chat_memory.py    # 命令行对话测试
│   └── test_ollama.py       # Ollama 连接测试
├── examples/
│   └ call_llama.py          # 调用示例
├── utils/
│   ├── __init__.py
│   └ common_utils.py        # 工具函数
├── requirements.txt         # Python 依赖
├── README.md                # 项目文档
└── main.py                  # 项目入口（示例）
```

---

## 2. 环境安装与配置

### 2.1 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 10/11、Linux、macOS |
| **Python** | Python 3.10+ |
| **内存** | 最低 8GB，推荐 16GB+ |
| **GPU** | 推荐 NVIDIA GPU（显存 6GB+），无 GPU 也可运行（速度较慢） |
| **硬盘** | 至少 20GB 可用空间（用于存储模型） |

### 2.2 安装步骤

#### 步骤 1：安装 Python

**Windows:**
1. 访问 [Python 官网](https://www.python.org/downloads/) 下载 Python 3.10+ 安装包
2. 运行安装程序，勾选 "Add Python to PATH"
3. 验证安装：
   ```bash
   python --version
   pip --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3-pip
python3 --version
```

**macOS:**
```bash
brew install python@3.10
python3 --version
```

#### 步骤 2：安装 Ollama

**Windows:**
1. 访问 [Ollama 官网](https://ollama.com/download) 下载 Windows 安装包
2. 运行安装程序，按提示完成安装
3. 安装完成后，Ollama 会自动启动服务

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

#### 步骤 3：下载模型

安装 Ollama 后，需要下载所需的大语言模型：

```bash
# 代码专用模型（约 4.7GB）
ollama pull qwen2.5-coder:7b

# 通用场景模型（约 1.1GB）
ollama pull deepseek-r1:1.5b

# 复杂任务模型（约 4.9GB）
ollama pull deepseek-r1:8b
```

**模型说明：**

| 模型 | 大小 | 适用场景 | 显存要求 |
|------|------|----------|---------|
| `qwen2.5-coder:7b` | ~4.7GB | 代码生成、补全 | 6GB+ |
| `deepseek-r1:1.5b` | ~1.1GB | 通用对话、轻量任务 | 2GB+ |
| `deepseek-r1:8b` | ~4.9GB | 复杂推理、长文本 | 8GB+ |

#### 步骤 4：验证 Ollama 服务

```bash
# 检查 Ollama 服务状态
ollama list

# 测试模型运行
ollama run qwen2.5-coder:7b "你好，请介绍一下你自己"
```

Ollama 服务默认运行在 `http://localhost:11434`。

#### 步骤 5：安装项目依赖

```bash
# 克隆或下载项目
cd D:\Pycharm\Code\ollamatest

# 安装 Python 依赖
pip install -r requirements.txt
```

**依赖说明：**

| 包名 | 版本 | 说明 |
|------|------|------|
| `ollama` | >=0.3.0 | Ollama Python SDK |
| `flask` | >=3.0.0 | Web 框架 |
| `flask-cors` | >=4.0.0 | 跨域支持 |
| `openai` | >=1.0.0 | OpenAI SDK（兼容接口） |
| `python-dotenv` | >=1.0.0 | 环境变量管理 |

---

## 3. 项目配置说明

### 3.1 配置文件位置

所有配置统一在 `config/settings.py` 文件中管理。

### 3.2 Ollama 服务配置

```python
# Ollama 服务地址
OLLAMA_HOST = "http://localhost:11434"
```

如果 Ollama 服务运行在其他地址或端口，请修改此配置。

### 3.3 模型配置

```python
# 模型配置（按场景分级）
CODE_MODEL = "qwen2.5-coder:7b"     # 代码专用
GENERAL_MODEL = "deepseek-r1:1.5b"  # 通用场景
ADVANCED_MODEL = "deepseek-r1:8b"   # 复杂任务
```

可根据需要更换为其他 Ollama 支持的模型，如：
- `llama3:8b`
- `mistral:7b`
- `codellama:7b`

### 3.4 生成参数配置

```python
# 生成参数
GENERATION_CONFIG = {
    'temperature': 0.5,   # 创造性（代码补全 0.2-0.3 / 算法 0.4-0.5 / 调试 0.1-0.2）
    'top_p': 0.9,         # 输出多样性
    'num_ctx': 4096,      # 上下文窗口大小
    'stop': ["\n###"],    # 停止标记
}
```

**参数说明：**

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `temperature` | 控制输出创造性，值越高越随机 | 代码：0.2-0.3，对话：0.5-0.7 |
| `top_p` | 控制输出多样性 | 0.9 |
| `num_ctx` | 上下文窗口大小，影响记忆长度 | 4096（可增至 8192） |

### 3.5 会话上限配置

```python
# 会话上限
MAX_SESSIONS = 20  # 最多保留的会话数，超出后新建会话会提示删除历史
```

### 3.6 硬件配置

```python
# 硬件配置
HARDWARE_CONFIG = {
    'gpu_layers': 30,                        # GPU 加速层数
    'main_gpu': 0,                           # 主 GPU 索引
    'cpu_threads': min(6, os.cpu_count() - 1),  # CPU 线程数
    'cpu_cores': 2,                          # CPU 核心数
}
```

### 3.7 日志配置

```python
# 应用日志配置
LOGGING_CONFIG = {
    'level': 'INFO',                          # 日志级别
    'log_dir': 'logs',                        # 日志目录
    'file_name': 'app.log',                   # 日志文件名
    'backup_count': 30,                       # 保留历史日志文件数
    'max_file_size': 200 * 1024 * 1024,       # 单个日志文件最大大小（200MB）
    'compress': True,                         # 是否压缩历史日志文件
}

# 启动日志配置（用于排查启动失败问题）
BOOT_LOGGING_CONFIG = {
    'level': 'DEBUG',                         # 启动日志级别
    'file_name': 'appBoot.log',               # 启动日志文件名
    'backup_count': 10,                       # 保留历史启动日志数
    'max_file_size': 50 * 1024 * 1024,        # 单个启动日志最大大小（50MB）
    'compress': True,                         # 是否压缩历史日志文件
}
```

---

## 4. 项目运行方式

### 4.1 方式一：Web 页面（推荐日常使用）

```bash
# 启动 Web 服务
python web/webpage.py
```

启动成功后，浏览器访问：`http://127.0.0.1:5000`

**Web 功能：**
- 模型切换（代码专用 / 通用 / 复杂任务）
- 场景切换（通用、Python、Java、SQL、调试、Shell）
- 多会话管理（新建、切换、删除、重命名、置顶）
- 会话搜索（按名称、场景、模型搜索）
- 流式响应（实时显示 AI 回复）
- Markdown 渲染（代码高亮、表格、列表）

### 4.2 方式二：命令行交互（推荐尝鲜测试）

```bash
# 启动命令行对话
python tests/03_chat_memory.py
```

**命令行交互命令：**

| 输入 | 效果 |
|------|------|
| 你的问题 | 发送给 AI |
| `switch=java` | 切换到 Java 场景 |
| `switch=python` | 切换到 Python 场景 |
| `switch=debug` | 切换到调试场景 |
| `switch=sql` | 切换到 SQL 场景 |
| `switch=shell` | 切换到 Shell 场景 |
| `switch=general` | 切换到通用场景 |
| `clear` | 清空对话历史 |
| `exit` | 退出程序 |

### 4.3 方式三：单轮对话测试

```bash
# 测试单轮对话（无上下文记忆）
python tests/test_ollama.py
```

### 4.4 场景说明

| 场景标识 | 说明 | 适用场景 |
|---------|------|---------|
| `general` | 通用对话 | 日常聊天、问答 |
| `python` | Python 代码助手 | Python 开发、代码生成 |
| `java` | Java 代码助手 | Java 后端开发 |
| `sql` | SQL 查询助手 | 数据库查询、SQL 编写 |
| `debug` | 调试排错专家 | Bug 排查、错误分析 |
| `shell` | Shell 脚本助手 | Linux 命令、脚本编写 |

---

## 5. 硬件要求与部署

### 5.1 硬件要求

#### 最低配置（无 GPU）

| 项目 | 要求 |
|------|------|
| CPU | 4 核以上 |
| 内存 | 8GB+ |
| 硬盘 | 20GB+ 可用空间 |
| 模型 | 仅使用 `deepseek-r1:1.5b` |

**注意：** 无 GPU 时，模型推理速度较慢（约 2-5 tokens/秒）。

#### 推荐配置（有 GPU）

| 项目 | 要求 |
|------|------|
| CPU | 6 核以上 |
| 内存 | 16GB+ |
| GPU | NVIDIA GPU，显存 6GB+ |
| 硬盘 | 50GB+ 可用空间 |
| 模型 | 可使用所有模型 |

**GPU 推理速度：** 约 20-50 tokens/秒。

#### 高性能配置

| 项目 | 要求 |
|------|------|
| CPU | 8 核以上 |
| 内存 | 32GB+ |
| GPU | NVIDIA GPU，显存 12GB+ |
| 硬盘 | 100GB+ 可用空间 |
| 模型 | 可使用更大模型（如 `qwen2.5-coder:14b`） |

### 5.2 GPU 配置

**NVIDIA GPU:**
1. 安装 [NVIDIA 驱动](https://www.nvidia.com/Download/index.aspx)
2. 安装 [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)（可选，Ollama 会自动检测）
3. 验证 GPU：
   ```bash
   nvidia-smi
   ```

**macOS (Apple Silicon):**
- Ollama 自动使用 Metal 加速，无需额外配置

### 5.3 生产环境部署

#### 5.3.1 修改端口

编辑 `web/webpage.py`，修改端口：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)  # 修改端口为 8080
```

#### 5.3.2 使用生产服务器

推荐使用 `gunicorn` 或 `nginx` 部署：

```bash
# 安装 gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn -w 4 -b 0.0.0.0:5000 web.webpage:app
```

#### 5.3.3 配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 6. API 接口文档

### 6.1 接入说明

#### 6.1.1 基础信息

| 项目 | 说明 |
|------|------|
| **服务地址** | `http://127.0.0.1:5000` |
| **Content-Type** | `application/json` |
| **字符编码** | UTF-8 |
| **认证方式** | 无需认证（仅限本地使用） |

#### 6.1.2 统一响应格式

**成功响应：**
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "error": "错误描述",
  "error_code": 400,
  "details": { ... }
}
```

---

### 6.2 基础接口

#### 6.2.1 获取可用模型列表

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/api/get_models` |
| 说明 | 获取所有可用的模型列表 |

**响应示例：**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "code",
        "name": "代码助手 (qwen2.5-coder:7b)",
        "value": "qwen2.5-coder:7b"
      },
      {
        "id": "general",
        "name": "通用助手 (deepseek-r1:1.5b)",
        "value": "deepseek-r1:1.5b"
      },
      {
        "id": "advanced",
        "name": "高级助手 (deepseek-r1:8b)",
        "value": "deepseek-r1:8b"
      }
    ]
  }
}
```

#### 6.2.2 获取可用场景列表

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/api/get_scenes` |

**响应示例：**
```json
{
  "success": true,
  "data": {
    "scenes": ["general", "python", "java", "sql", "debug", "shell"]
  }
}
```

---

### 6.3 对话接口

#### 6.3.1 发送消息

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/chat` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message | string | 是 | 用户发送的消息内容 |

**请求示例：**
```json
{
  "message": "你好，请用Python写一个快速排序算法"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "reply": "好的，这是一个Python实现的快速排序算法...\n\n```python\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# 测试\narr = [3, 6, 8, 10, 1, 2, 1]\nprint(quick_sort(arr))\n```",
    "current_scene": "python",
    "current_model": "qwen2.5-coder:7b"
  }
}
```

#### 6.3.2 获取对话历史

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/api/get_history` |

**响应示例：**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "role": "user",
        "content": "你好，请用Python写一个快速排序"
      },
      {
        "role": "assistant",
        "content": "好的，这是一个Python实现的快速排序..."
      }
    ],
    "current_scene": "python"
  }
}
```

#### 6.3.3 清空对话历史

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/clear_history` |

**响应示例：**
```json
{
  "success": true,
  "message": "对话历史已清空"
}
```

---

### 6.4 模型/场景切换

#### 6.4.1 切换模型

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/switch_model` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| model_id | string | 是 | 模型标识（code/general/advanced） |

**请求示例：**
```json
{
  "model_id": "code"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "current_model": "qwen2.5-coder:7b"
  },
  "message": "已切换模型：代码助手 (qwen2.5-coder:7b)"
}
```

#### 6.4.2 切换场景

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/switch_scene` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| scene | string | 是 | 场景名称（general/python/java/sql/debug/shell） |

**请求示例：**
```json
{
  "scene": "python"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "current_scene": "python"
  },
  "message": "已切换场景：python，对话历史已重置"
}
```

---

### 6.5 会话管理

#### 6.5.1 创建新会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/reset_session` |

**响应示例（成功）：**
```json
{
  "success": true,
  "data": {
    "new_session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "message": "会话已重置"
}
```

**响应示例（超过上限）：**
```json
{
  "success": false,
  "error": "会话已超过最大值 20，请先删除历史会话。",
  "error_code": 400,
  "details": {
    "session_limit_reached": true,
    "max_sessions": 20,
    "current_count": 20
  }
}
```

#### 6.5.2 列出所有会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/api/list_sessions` |

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "scene": "python",
        "model": "qwen2.5-coder:7b",
        "summary": "Python快速排序算法实现",
        "pinned": true,
        "custom_name": "排序算法",
        "msg_count": 4,
        "created_at": "2026-05-28T10:30:00",
        "updated_at": "2026-05-28T14:20:00"
      },
      {
        "session_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
        "scene": "general",
        "model": "deepseek-r1:1.5b",
        "summary": "日常对话",
        "pinned": false,
        "custom_name": "",
        "msg_count": 2,
        "created_at": "2026-05-27T09:00:00",
        "updated_at": "2026-05-28T11:15:00"
      }
    ]
  }
}
```

#### 6.5.3 切换会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/load_session` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 要切换的会话 ID |

**请求示例：**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "role": "user",
        "content": "你好"
      },
      {
        "role": "assistant",
        "content": "你好，有什么可以帮助你的吗？"
      }
    ],
    "current_scene": "python",
    "current_model": "qwen2.5-coder:7b",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "message": "已切换到会话 a1b2c3d4"
}
```

#### 6.5.4 删除会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/delete_session` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 要删除的会话 ID |

**请求示例：**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "会话已删除"
}
```

#### 6.5.5 重命名会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/rename_session` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 ID |
| name | string | 是 | 新的会话名称 |

**请求示例：**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Python开发项目"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "name": "Python开发项目"
  },
  "message": "重命名成功"
}
```

#### 6.5.6 置顶/取消置顶会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/api/toggle_pin` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 ID |

**请求示例：**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "pinned": true
  },
  "message": "会话已置顶"
}
```

#### 6.5.7 搜索会话

**接口信息：**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/api/search_sessions` |

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | string | 是 | 搜索关键词 |

**请求示例：**
```
GET /api/search_sessions?keyword=Python
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "scene": "python",
        "model": "qwen2.5-coder:7b",
        "summary": "Python快速排序算法",
        "pinned": false,
        "custom_name": "排序算法"
      }
    ],
    "keyword": "Python",
    "total": 1
  }
}
```

---

### 6.6 错误码说明

#### 6.6.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

#### 6.6.2 业务错误码

| 错误码 | 说明 | 可能的解决方案 |
|--------|------|---------------|
| 400 | 请求参数为空或格式错误 | 检查请求 JSON 格式和必填参数 |
| 400 | 消息不能为空 | message 参数不能为空字符串 |
| 400 | 场景不存在 | 检查 scene 参数是否为有效值 |
| 400 | 无效的模型ID | 检查 model_id 是否为 code/general/advanced |
| 400 | 会话已超过最大值 | 删除历史会话后重试 |
| 400 | 搜索关键词不能为空 | keyword 参数不能为空 |
| 404 | 会话不存在 | 检查 session_id 是否正确 |
| 404 | 会话文件不存在 | 会话已被删除或 ID 错误 |
| 500 | Ollama 服务连接失败 | 检查 Ollama 服务是否启动 |
| 500 | 对话失败 | 查看服务端日志排查问题 |
| 500 | 切换模型失败 | 检查模型是否可用 |
| 500 | 切换场景失败 | 检查场景名称是否正确 |

#### 6.6.3 Ollama 错误

| 错误信息 | 说明 |
|----------|------|
| `无法连接 Ollama 服务` | Ollama 服务未启动或地址错误 |
| `Ollama 响应错误` | 模型调用失败，检查模型是否正确加载 |
| `Ollama RequestError` | 网络问题或服务无响应 |

---

### 6.7 完整 API 调用示例

#### 6.7.1 Python 调用示例

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# 1. 发送消息
def chat(message):
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": message}
    )
    return response.json()

# 2. 切换模型
def switch_model(model_id):
    response = requests.post(
        f"{BASE_URL}/api/switch_model",
        json={"model_id": model_id}
    )
    return response.json()

# 3. 切换场景
def switch_scene(scene):
    response = requests.post(
        f"{BASE_URL}/api/switch_scene",
        json={"scene": scene}
    )
    return response.json()

# 4. 列出所有会话
def list_sessions():
    response = requests.get(f"{BASE_URL}/api/list_sessions")
    return response.json()

# 5. 搜索会话
def search_sessions(keyword):
    response = requests.get(
        f"{BASE_URL}/api/search_sessions",
        params={"keyword": keyword}
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 发送消息
    result = chat("你好，请用Python写一个快速排序")
    print(result)

    # 切换到 Python 场景
    result = switch_scene("python")
    print(result)

    # 列出所有会话
    result = list_sessions()
    print(result)

    # 搜索会话
    result = search_sessions("排序")
    print(result)
```

#### 6.7.2 JavaScript 调用示例

```javascript
const BASE_URL = "http://127.0.0.1:5000";

// 发送消息
async function chat(message) {
    const response = await fetch(`${BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
    return response.json();
}

// 切换模型
async function switchModel(modelId) {
    const response = await fetch(`${BASE_URL}/api/switch_model`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
    });
    return response.json();
}

// 切换场景
async function switchScene(scene) {
    const response = await fetch(`${BASE_URL}/api/switch_scene`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scene })
    });
    return response.json();
}

// 获取历史
async function getHistory() {
    const response = await fetch(`${BASE_URL}/api/get_history`);
    return response.json();
}

// 列出所有会话
async function listSessions() {
    const response = await fetch(`${BASE_URL}/api/list_sessions`);
    return response.json();
}

// 搜索会话
async function searchSessions(keyword) {
    const response = await fetch(`${BASE_URL}/api/search_sessions?keyword=${encodeURIComponent(keyword)}`);
    return response.json();
}

// 使用示例
async function main() {
    // 发送消息
    let result = await chat("你好");
    console.log(result);

    // 切换场景
    result = await switchScene("python");
    console.log(result);

    // 获取历史
    result = await getHistory();
    console.log(result);

    // 列出所有会话
    result = await listSessions();
    console.log(result);

    // 搜索会话
    result = await searchSessions("排序");
    console.log(result);
}

main();
```

---

## 7. 常见问题

### Q1: Ollama 服务无法连接？

**解决方案：**
1. 检查 Ollama 服务是否启动：
   ```bash
   ollama list
   ```
2. 检查服务地址是否正确（默认 `http://localhost:11434`）
3. 如果服务运行在其他端口，修改 `config/settings.py` 中的 `OLLAMA_HOST`

### Q2: 模型下载失败？

**解决方案：**
1. 检查网络连接
2. 使用代理或镜像站：
   ```bash
   # 设置代理
   export OLLAMA_ORIGINS="*"
   ```
3. 手动下载模型文件

### Q3: GPU 不被识别？

**解决方案：**
1. 检查 NVIDIA 驱动是否安装：
   ```bash
   nvidia-smi
   ```
2. 安装 CUDA Toolkit
3. 检查 Ollama 日志：
   ```bash
   # Linux
   journalctl -u ollama -f
   ```

### Q4: 内存不足？

**解决方案：**
1. 使用更小的模型（如 `deepseek-r1:1.5b`）
2. 减少上下文窗口大小：
   ```python
   'num_ctx': 2048  # 从 4096 减少到 2048
   ```
3. 关闭其他占用内存的程序

### Q5: 响应速度慢？

**解决方案：**
1. 使用 GPU 加速
2. 使用更小的模型
3. 减少生成参数：
   ```python
   'temperature': 0.3  # 降低创造性可加快速度
   ```

### Q6: 会话数据丢失？

**解决方案：**
1. 检查 `data/sessions/` 目录是否存在
2. 检查日志文件 `logs/app.log` 和 `logs/appBoot.log`
3. 确保程序正常退出（不要强制关闭）

---

## 📄 License

MIT License

---

## 更新日志

- **2026-05-28**: 
  - 新增会话搜索功能
  - 新增启动日志 `appBoot.log`
  - 优化侧边栏样式和交互
  - 修复搜索会话乱码匹配问题
  - 更新 README.md 文档结构