from typing import List

from pydantic import RootModel

from server.schema.base import DataSchema, ResponseSchema


class ContextSource(DataSchema):
    content: str
    doc_id: str
    score: float


class QueryData(DataSchema):
    answer: str
    context: List[ContextSource]


class QueryResponse(ResponseSchema[QueryData]):
    pass


class MatchedData(DataSchema, RootModel[List[ContextSource]]):
    pass


class MatchResponse(ResponseSchema[MatchedData]):
    pass
