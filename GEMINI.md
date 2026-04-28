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
