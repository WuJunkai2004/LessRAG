import json
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from server.database.models import Chunk, Document
from server.schema.query import (
    ContextSource,
    MatchedData,
    MatchResponse,
    QueryData,
    QueryResponse,
)
from server.utils.openai import ai_client
from server.utils.vector import rank_chunks

router = APIRouter(tags=["query"])


class QueryRequest(BaseModel):
    question: str
    stream: bool = False
    doc_ids: Optional[List[str]] = None


class MatchRequest(BaseModel):
    text: str
    top_k: int = 5
    doc_ids: Optional[List[str]] = None


async def _get_relevant_chunks(
    text: str, top_k: int = 5, doc_ids: Optional[List[str]] = None
) -> List[ContextSource]:
    """内部通用检索方法"""
    # 1. 将查询文本向量化
    query_vector = ai_client.get_embedding(text)

    # 2. 从数据库加载候选分片
    query = Chunk.select(Chunk, Document.doc_id).join(Document)
    if doc_ids:
        query = query.where(Document.doc_id << doc_ids)

    candidate_chunks = []
    for chunk in query:
        if chunk.embedding:
            candidate_chunks.append(
                {
                    "content": chunk.content,
                    "embedding": json.loads(chunk.embedding.decode("utf-8")),
                    "doc_id": chunk.document.doc_id,
                }
            )

    if not candidate_chunks:
        return []

    # 3. 计算相似度并排序
    ranked_results = rank_chunks(query_vector, candidate_chunks, top_k=top_k)

    return [
        ContextSource(content=r["content"], doc_id=r["doc_id"], score=r["score"])
        for r in ranked_results
    ]


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(req: QueryRequest) -> QueryResponse:
    # 1. 检索相关分片
    contexts = await _get_relevant_chunks(req.question, top_k=5, doc_ids=req.doc_ids)

    if not contexts:
        return QueryResponse(
            success=True,
            data=QueryData(
                answer="抱歉，在知识库中没有找到相关的背景信息来回答您的问题。",
                context=[],
            ),
        )

    # 2. 构建 Prompt 并调用 LLM 生成回答
    context_text = "\n---\n".join(
        [f"[来源文档: {c.doc_id}]\n{c.content}" for c in contexts]
    )

    system_prompt = """你是一个专业的 AI 助手。请根据提供的“背景资料”来回答用户的“问题”。
要求：
1. 仅根据背景资料中的内容进行回答，不要编造事实。
2. 如果背景资料中没有相关信息，请诚实告知。
3. 回答要简洁、专业、逻辑清晰。"""

    user_prompt = f"背景资料：\n{context_text}\n\n问题：{req.question}"

    try:
        response = ai_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        answer = response.choices[0].message.content or "抱歉，LLM 没有生成有效的回答。"

        return QueryResponse(
            success=True, data=QueryData(answer=answer, context=contexts)
        )
    except Exception as e:
        return QueryResponse(
            success=False, code=500, message=f"LLM generation failed: {str(e)}"
        )


@router.post("/match", response_model=MatchResponse)
async def match_chunks(req: MatchRequest) -> MatchResponse:
    contexts = await _get_relevant_chunks(
        req.text, top_k=req.top_k, doc_ids=req.doc_ids
    )
    return MatchResponse(success=True, data=MatchedData(contexts))
