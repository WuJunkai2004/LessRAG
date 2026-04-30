import datetime
import uuid

from peewee import (
    AutoField,
    BlobField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    TextField,
)

from server.database.connect import Database


class BaseModel(Model):
    class Meta:
        database = Database()


class Collection(BaseModel):
    """文档集模型"""

    id = AutoField()
    name = CharField(unique=True)
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "collections"


class Document(BaseModel):
    """文档模型"""

    id = AutoField()
    doc_id = CharField(unique=True, default=lambda: str(uuid.uuid4()))
    collection = ForeignKeyField(
        Collection, backref="documents", null=True, on_delete="SET NULL"
    )
    filename = CharField()
    file_path = CharField(null=True)
    status = CharField(default="processing")
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "documents"


class Chunk(BaseModel):
    """分片模型"""

    id = AutoField()
    document = ForeignKeyField(Document, backref="chunks", on_delete="CASCADE")
    content = TextField()
    # 存储向量数据，通常可以存为 Blob
    embedding = BlobField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "chunks"
