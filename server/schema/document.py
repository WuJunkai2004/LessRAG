from datetime import datetime
from typing import Optional

from server.schema.base import DataSchema, ResponseSchema


class DocumentInfo(DataSchema):
    doc_id: str
    filename: str
    status: str
    created_at: datetime


class InfoResponse(ResponseSchema[DocumentInfo]):
    pass


class DocumentDetail(DocumentInfo):
    chunks_count: int
    error_message: Optional[str] = None


class DetailResponse(ResponseSchema[DocumentDetail]):
    pass
