# LessRAG

## 项目目标
LessRAG 是一个专注于“精简与智能”的 RAG（检索增强生成）项目。
- **核心思路**：利用 LLM（大语言模型）进行文档的智能分片（Chunking），而非传统的基于字符或固定长度的暴力切分。
- **查询机制**：使用 Embedding 向量化技术进行高效检索。

## 技术栈
- **核心框架**：Python 3.10+
- **Web API**：FastAPI
- **LLM/Embedding**：OpenAI API
- **数据库**：SQLite (通过 Peewee ORM 管理)
- **文档解析**：
  - PDF: PyMuPDF (fitz)
  - Word: docx2txt
- **包管理**：uv

## 实现思路

### 1. 异步处理架构
为了保证系统的响应速度，文档的处理（解析、LLM 智能分片、Embedding 计算）将采用完全异步的架构。
- **任务队列**：引入内部 `asyncio.Queue` 或轻量级任务分配机制。当用户上传文档后，API 立即返回 `doc_id` 并将任务压入队列。
- **后台消费进程**：独立的后台 Worker（或 FastAPI 的 BackgroundTasks）从队列中获取任务，按序执行耗时的 Chunking 和 Embedding 操作。
- **状态追踪**：通过数据库中的 `status` 字段实时追踪文档处理进度（processing -> completed/failed）。

### 2. 智能分片 (LLM-based Chunking)
区别于传统的固定长度切分，LessRAG 利用 LLM 理解文档结构。
- 预处理文档提取文本。
- 调用 LLM 识别段落逻辑边界，生成具有语义完整性的分片。

### 3. 查询与匹配机制
- **同步检索**：`/query` 接口采用同步响应模式，请求到来后立即进行向量检索与 LLM 生成。
- **实时匹配**：`/match` 接口用于纯向量相似度匹配，返回最相关的文档分片而不进行 LLM 总结。这同样是同步实时的，方便用户快速验证检索效果。
- **向量匹配**：使用 OpenAI Embedding 转换查询词，并计算与数据库中 Chunk 的余弦相似度。
