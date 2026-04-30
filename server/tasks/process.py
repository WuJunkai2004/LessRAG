import json

from server.database.models import Chunk, Document
from server.utils.logger import log
from server.utils.openai import ai_client
from server.utils.parser import DocumentParser


async def process_document_task(doc_id: str):
    try:
        doc = Document.get(Document.doc_id == doc_id)
        if not doc.file_path:
            raise ValueError(f"File path is missing for document {doc_id}")

        log("task").info(f"Processing document: {doc.filename} ({doc_id})")

        # 1. 解析文本
        text = DocumentParser.parse(doc.file_path)
        if not text.strip():
            log("task").warning(f"No text extracted from {doc.filename}")
            doc.status = "completed"  # 虽然没内容，但也算处理完
            doc.save()
            return

        # 2. 智能分片
        # 对于超长文档，可能需要循环调用智能分片，这里先做一次处理
        # 实际生产中可以根据文本长度分块后再调用 LLM 分片
        chunks_text = ai_client.smart_chunking(text)
        log("task").info(f"Document split into {len(chunks_text)} chunks")

        # 3 & 4. 向量化并存储
        for content in chunks_text:
            if not content.strip():
                continue

            # 获取 Embedding
            embedding_vector = ai_client.get_embedding(content)

            # 存入数据库 (将列表序列化为 bytes 存储)
            Chunk.create(
                document=doc,
                content=content,
                embedding=json.dumps(embedding_vector).encode("utf-8"),
            )

        doc.status = "completed"
        doc.save()
        log("task").info(f"Document processed successfully: {doc_id}")

    except Exception as e:
        log("task").error(f"Error processing document {doc_id}: {e}", exc_info=True)
        try:
            doc = Document.get(Document.doc_id == doc_id)
            doc.status = "failed"
            doc.save()
        except Exception:
            pass
