# LessRAG

RAG system using LLM-based intelligent document chunking and embedding-based retrieval.

## Commands

```bash
uv install                          # install dependencies
lessrag config                      # generate config.toml in CWD from template
lessrag server [-p 15000] [-c path] # start FastAPI server (uvicorn with reload)
lessrag ui                          # start Mesop web UI (requires: uv install lessrag[ui])
```

Config priority: CLI args > config.toml > defaults. Config path also set via `LESSRAG_CONFIG` env var.

## Architecture

- `app/` — CLI entrypoint (`app/main.py` is the `lessrag` console script) and `config.example.toml` template
- `server/` — FastAPI application and all business logic
  - `server/main.py` — FastAPI app with lifespan (DB setup + task worker start/stop)
  - `server/api/` — route handlers (document, query, health) mounted under `/api/v1`
  - `server/tasks/manager.py` — asyncio.Queue-based async task worker (singleton)
  - `server/tasks/process.py` — document pipeline: parse → LLM chunk → embed → store
  - `server/utils/openai.py` — OpenAI client wrapper (singleton `ai_client`); handles `api_url` suffix stripping (`/chat/completions`, `/embeddings`)
  - `server/database/` — Peewee ORM models (Collection, Document, Chunk); SQLite at `datas/app.db`
  - `server/utils/vector.py` — numpy cosine similarity search (in-memory, no vector DB)
  - `server/utils/config.py` — TOML config singleton with dotted key access

## Key details

- **Config**: `config.toml` is gitignored (contains API keys). `model` and `embedding` sections require `model`, `api_url`, `api_key`.
- **Embeddings stored as bytes**: `Chunk.embedding` is a `BlobField` storing JSON-serialized float arrays.
- **Smart chunking**: LLM splits text into 300-800 char semantic chunks. Falls back to paragraph splitting on failure. Text is truncated to 4000 chars before sending to LLM.
- **No vector database**: similarity search is brute-force numpy cosine similarity over all chunks in SQLite.

## Testing

Tests are integration tests (httpx) against a running server — server must be up first:
```bash
lessrag server &           # start server on port 15000
python -m pytest tests/    # run integration tests
```

`tests/test_api.py` covers health check → upload → poll status → match → query → delete lifecycle.
