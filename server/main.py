from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.api.document import router as document_router
from server.api.health import router as health_router
from server.api.query import router as query_router
from server.database.setup import setup as setup_database
from server.tasks.manager import task_manager
from server.utils.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    log("app").info("Starting LessRAG Server...")
    setup_database()
    task_manager.start_worker()
    yield
    log("app").info("Shutting down LessRAG Server...")
    await task_manager.stop_worker()


app = FastAPI(title="LessRAG API", lifespan=lifespan)

# 注册路由
app.include_router(document_router, prefix="/api/v1")
app.include_router(query_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
