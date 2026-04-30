from typing import List

import numpy as np


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """计算两个向量的余弦相似度"""
    a = np.array(v1)
    b = np.array(v2)

    # 防止分母为 0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def rank_chunks(
    query_vector: List[float], chunks: List[dict], top_k: int = 5
) -> List[dict]:
    """
    根据向量相似度对分片进行排序
    chunks 格式: [{"content": str, "embedding": List[float], "doc_id": str, ...}]
    """
    if not chunks:
        return []

    query_vec = np.array(query_vector)

    # 提取所有分片的向量并转换为 numpy 矩阵以提高计算效率
    chunk_embeddings = np.array([item["embedding"] for item in chunks])

    # 计算余弦相似度: (A · B) / (||A|| * ||B||)
    # 计算点积
    dot_products = np.dot(chunk_embeddings, query_vec)

    # 计算范数
    chunk_norms = np.linalg.norm(chunk_embeddings, axis=1)
    query_norm = np.linalg.norm(query_vec)

    # 防止除以 0
    chunk_norms[chunk_norms == 0] = 1e-10
    if query_norm == 0:
        query_norm = 1e-10

    similarities = dot_products / (chunk_norms * query_norm)

    # 结合分片信息
    results = []
    for i, score in enumerate(similarities):
        results.append(
            {
                "content": chunks[i]["content"],
                "doc_id": chunks[i]["doc_id"],
                "score": float(score),
            }
        )

    # 按得分从高到低排序
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]
