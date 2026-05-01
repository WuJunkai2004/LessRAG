# LessRAG

LessRAG is a "Concise and Intelligent" RAG (Retrieval-Augmented Generation) framework designed to move beyond traditional, brute-force text cutting.

## 🌟 Core Philosophy

Traditional RAG systems often rely on fixed-length or character-based chunking, which can break semantic continuity. LessRAG leverages Large Language Models (LLMs) to understand document structure and perform **Smart Chunking**, ensuring that each piece of information remains contextually coherent and semantically complete.

## ✨ Key Features

- **🧠 Intelligent Chunking**: Uses LLMs to identify logical boundaries and semantic shifts for superior document splitting.
- **🚀 Lightweight & Efficient**: Extremely low resource consumption. Unlike heavy frameworks (e.g., FastGPT), LessRAG can run smoothly in environments with as little as **2 Cores and 2GB RAM**.
- **⚡ Asynchronous Architecture**: Heavy tasks like document parsing, smart chunking, and embedding generation are handled by an internal async task manager, ensuring a responsive API.
- **📊 Status Tracking**: Real-time monitoring of document processing states (processing, completed, failed).
- **🔍 Dual Retrieval Modes**:
  - `Match`: Pure vector similarity search for quick verification.
  - `Query`: Full RAG pipeline with LLM-augmented generation.
- **🛠️ Built-in CLI**: Easy configuration and server management through a dedicated command-line interface.

## 🛠️ Tech Stack

- **Framework**: Python 3.10+, FastAPI
- **LLM/Embedding**: OpenAI API (compatible with any OpenAI-style provider)
- **Database**: SQLite (managed via Peewee ORM)
- **Parsing**: PyMuPDF (PDF), docx2txt (Word)
- **Package Management**: `uv`

## 🚀 Getting Started

### Installation

LessRAG is available on PyPI. It is recommended to use `uv` for the best experience:

**1. Run without installation (one-off):**
```bash
uvx lessrag config
uvx lessrag server
```

**2. Install as a global CLI tool:**
```bash
uv tool install lessrag
or
pip install lessrag

lessrag config
# edit the config.toml with your API keys and model preferences
lessrag server
```

**3. Install from source (for development):**
```bash
git clone https://github.com/yourusername/LessRAG.git
cd LessRAG
uv sync
```

### Configuration

LessRAG provides a convenient command to set up your configuration:

```bash
lessrag config
```

This will create a `config.toml` in your current directory. Open it and fill in your OpenAI API keys and preferred models:

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

### Running the Server

Start the LessRAG server with:

```bash
lessrag server
```

By default, the server runs on `http://0.0.0.0:15000`.

## 📖 API Usage

### Document Management
- `POST /api/v1/document/upload`: Upload a PDF or Word file.
- `GET /api/v1/document/list`: List all uploaded documents and their processing status.
- `GET /api/v1/document/{doc_id}`: Get details of a specific document.

### Retrieval & Generation
- `POST /api/v1/query`: Perform a RAG query to get an answer based on your documents.
- `POST /api/v1/match`: Find the most relevant document chunks without LLM generation.

## 📂 Project Structure

```text
├── app/                # CLI implementation and templates
├── server/             # FastAPI backend logic
│   ├── api/            # API Route definitions
│   ├── database/       # Models and database setup
│   ├── tasks/          # Async task manager and workers
│   └── utils/          # Config, parsing, and vector utilities
├── tests/              # API and unit tests
└── pyproject.toml      # Project metadata and dependencies
```

## ⚖️ License

[MIT License](LICENSE) (or specify your license)
