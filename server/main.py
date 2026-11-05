from contextlib import asynccontextmanager

from a2wsgi import WSGIMiddleware
from fastapi import FastAPI

from server.api.document import router as document_router
from server.api.health import router as health_router
from server.api.query import router as query_router
from server.database.setup import setup as setup_database
from server.tasks.manager import task_manager
from server.utils.config import config
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


if getattr(config.args, "with_ui", False):
    try:
        import mesop.bin.bin as mesop_bin

        mesop_bin.add_app_module(".", "server.ui")
        mesop_app = mesop_bin.create_app(prod_mode=True)
        flask_app = mesop_app._flask_app

        app.mount("/", WSGIMiddleware(flask_app))
        log("app").info("Mesop UI mounted at /")
    except ImportError:
        log("app").error(
            "未安装 mesop，无法挂载 UI。请运行 'pip install lessrag[ui]' 安装。"
        )
        raise
