import shutil

from fastapi import APIRouter, File, Query, UploadFile
from pydantic import BaseModel

from server.database.models import Chunk, Document
from server.schema.base import ResponseSchema
from server.schema.document import (
    DetailData,
    DetailResponse,
    InfoData,
    InfoList,
    InfoListResponse,
    InfoResponse,
)
from server.tasks.manager import task_manager
from server.tasks.process import process_document_task
from server.utils.config import DATA_PATH

router = APIRouter(prefix="/document", tags=["document"])

UPLOAD_DIR = DATA_PATH / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


class DeleteRequest(BaseModel):
    doc_id: str


@router.post("/upload", response_model=InfoResponse)
async def upload_document(file: UploadFile = File(...)) -> InfoResponse:
    # 1. 保存文件到本地
    file_path = UPLOAD_DIR / f"{Document().doc_id}_{file.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. 创建数据库记录
    doc = Document.create(
        filename=file.filename, file_path=str(file_path), status="processing"
    )

    # 3. 提交后台异步处理任务
    await task_manager.add_task(process_document_task, doc.doc_id)

    return InfoResponse(
        success=True,
        data=InfoData(
            doc_id=str(doc.doc_id),
            filename=str(doc.filename),
            status=str(doc.status),
            created_at=doc.created_at,  # type: ignore
        ),
    )


@router.get("/list", response_model=InfoListResponse)
async def list_documents() -> InfoListResponse:
    docs = Document.select().order_by(Document.created_at.desc())
    data = [
        InfoData(
            doc_id=d.doc_id,
            filename=d.filename,
            status=d.status,
            created_at=d.created_at,
        )
        for d in docs
    ]
    return InfoListResponse(success=True, data=InfoList(data))


@router.get("/detail", response_model=DetailResponse)
async def get_document_detail(doc_id: str = Query()) -> DetailResponse:
    try:
        doc = Document.get(Document.doc_id == doc_id)
        chunks_count = Chunk.select().where(Chunk.document == doc).count()
        return DetailResponse(
            success=True,
            data=DetailData(
                doc_id=doc.doc_id,
                filename=doc.filename,
                status=doc.status,
                created_at=doc.created_at,
                chunks_count=chunks_count,
            ),
        )
    except Exception:
        return DetailResponse(success=False, code=404, message="Document not found")


@router.post("/delete")
async def delete_document(req: DeleteRequest):
    try:
        doc = Document.get(Document.doc_id == req.doc_id)
        doc.delete_instance(recursive=True)
        return ResponseSchema(success=True, message="document deleted successfully")
    except Exception:
        return ResponseSchema(success=False, code=404, message="Document not found")
