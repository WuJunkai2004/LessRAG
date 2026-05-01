# LessRAG

LessRAG 是一个专注于“精简与智能”的 RAG（检索增强生成）框架，旨在打破传统的暴力文本切分模式。

## 🌟 核心理念

传统的 RAG 系统通常依赖于固定长度或基于字符的切分（Chunking），这往往会破坏语义的连贯性。LessRAG 利用大语言模型（LLM）来理解文档结构，进行**智能分片**，确保每一块信息在上下文上都是连贯且语义完整的。

## ✨ 核心特性

- **🧠 智能分片 (Smart Chunking)**：利用 LLM 识别逻辑边界和语义转折，实现更优的文档切分。
- **🚀 极致轻量化**：资源占用极低。相比 FastGPT 等重型框架，LessRAG 可以在低至 **2核2G** 的环境下流畅运行。
- **⚡ 异步处理架构**：文档解析、智能分片、向量化等耗时任务由内部异步任务管理器处理，保证 API 的极速响应。
- **📊 状态实时追踪**：支持实时查询文档的处理进度（处理中、已完成、失败）。
- **🔍 双重检索模式**：
  - `Match`: 纯向量相似度检索，用于快速验证匹配效果。
  - `Query`: 完整的 RAG 流程，结合 LLM 生成最终答案。
- **🛠️ 内置 CLI 工具**：通过专用命令行工具轻松完成配置生成和服务器管理。

## 🛠️ 技术栈

- **核心框架**: Python 3.10+, FastAPI
- **LLM/Embedding**: OpenAI API (兼容任何 OpenAI 格式的接口)
- **数据库**: SQLite (通过 Peewee ORM 管理)
- **文档解析**: PyMuPDF (PDF), docx2txt (Word)
- **包管理**: `uv`

## 🚀 快速上手

### 安装

LessRAG 已发布至 PyPI。推荐使用 `uv` 以获得最佳体验：

**1. 免安装直接运行 (一次性使用):**
```bash
uvx lessrag config
uvx lessrag server
```

**2. 作为全局 CLI 工具安装:**
```bash
uv tool install lessrag
or
pip install lessrag

lessrag config
# 编辑 config.toml，填入您的 API Key 和模型信息
lessrag server
```

**3. 从源码安装 (用于开发):**
```bash
git clone https://github.com/WuJunkai2004/LessRAG.git
cd LessRAG
uv sync
```

### 配置文件

LessRAG 提供了便捷的命令来初始化配置：

```bash
lessrag config
```

该命令会在当前目录下生成 `config.toml`。请打开文件并填入您的 API Key 和模型信息：

```toml
[model]
model="gpt-4"
api_url="https://api.openai.com/v1/chat/completions"
api_key="sk-..."

[embedding]
model="text-embedding-3-small"
api_url="https://api.openai.com/v1/embeddings"
api_key="sk-..."
```

### 启动服务

使用以下命令启动 LessRAG 服务器：

```bash
lessrag server
```

服务器默认运行在 `http://0.0.0.0:15000`。

## 📖 API 说明

### 文档管理
- `POST /api/v1/document/upload`: 上传 PDF 或 Word 文件。
- `GET /api/v1/document/list`: 获取所有文档及其处理状态。
- `GET /api/v1/document/{doc_id}`: 获取特定文档的详细信息。

### 检索与生成
- `POST /api/v1/query`: 执行 RAG 查询，基于文档库获取回答。
- `POST /api/v1/match`: 仅进行向量匹配，返回最相关的文档分片。

## 📂 项目结构

```text
├── app/                # CLI 实现与模板
├── server/             # FastAPI 后端逻辑
│   ├── api/            # 路由定义
│   ├── database/       # 模型定义与数据库初始化
│   ├── tasks/          # 异步任务管理与 Worker
│   └── utils/          # 配置、解析与向量工具类
├── tests/              # 接口与单元测试
└── pyproject.toml      # 项目元数据与依赖配置
```

## ⚖️ 开源协议

[MIT License](LICENSE)
