from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


class DataSchema(BaseModel):
    """Base schema for all data models"""


T = TypeVar("T", bound=BaseModel)


class ResponseSchema(BaseModel, Generic[T]):
    """Standardized response format"""

    success: bool
    code: int = 200
    message: str = ""
    data: Optional[T] = None
