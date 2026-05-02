from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

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

# 静态文件服务
dist_path = Path("web/dist")
if dist_path.exists():

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 排除 API 路由，避免它们被这个 catch-all 捕获并返回 index.html
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")

        # 检查请求的是否是真实存在的静态文件
        file_path = dist_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # 如果文件不存在且不是 API 请求，返回 index.html (支持 SPA History 模式)
        index_path = dist_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Not found")
else:
    log("app").warning(
        f"Frontend dist directory not found at {dist_path.resolve()}. WebUI will not be available."
    )
