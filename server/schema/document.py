from datetime import datetime
from typing import List, Optional

from pydantic import RootModel

from server.schema.base import DataSchema, ResponseSchema


class InfoData(DataSchema):
    doc_id: str
    filename: str
    status: str
    created_at: datetime


class InfoResponse(ResponseSchema[InfoData]):
    pass


class InfoList(DataSchema, RootModel[List[InfoData]]):
    pass


class InfoListResponse(ResponseSchema[InfoList]):
    pass


class DetailData(DataSchema):
    doc_id: str
    filename: str
    status: str
    created_at: datetime
    chunks_count: int
    error_message: Optional[str] = None


class DetailResponse(ResponseSchema[DetailData]):
    pass
