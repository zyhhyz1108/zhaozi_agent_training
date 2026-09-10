import json
import os
import sys
from pathlib import Path

import numpy as np

from app.rag.embedding import embed_texts


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_FILE = PROJECT_ROOT / "data" / "embeddings.json"


def search_knowledge(question: str, top_k: int = 3) -> list[dict]:
    if not question.strip():
        raise ValueError("问题不能为空")

    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")

    index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    chunks = index["chunks"]

    if not chunks:
        raise ValueError("索引中没有片段，请先生成索引")

    # 文档与问题必须使用相同的模型和维度
    current_model = os.getenv("EMBEDDING_MODEL")
    current_dimensions = int(
        os.getenv("EMBEDDING_DIMENSIONS", "1024")
    )

    if (
        index["model"] != current_model
        or index["dimensions"] != current_dimensions
    ):
        raise ValueError("当前模型配置与索引不一致，请恢复配置或重新建索引")

    document_vectors = np.asarray(
        [chunk["embedding"] for chunk in chunks],
        dtype=np.float64,
    )

    if document_vectors.shape != (len(chunks), current_dimensions):
        raise ValueError("索引向量的形状不正确")

    document_norms = np.linalg.norm(document_vectors, axis=1)

    if (
        not np.isfinite(document_vectors).all()
        or np.any(document_norms == 0)
    ):
        raise ValueError("索引包含无效向量")

    question_vector = np.asarray(
        embed_texts([question])[0],
        dtype=np.float64,
    )
    question_norm = np.linalg.norm(question_vector)

    if not np.isfinite(question_vector).all() or question_norm == 0:
        raise ValueError("问题向量无效")

    # 计算问题与每个文档片段的余弦相似度
    scores = (document_vectors @ question_vector) / (
        document_norms * question_norm
    )

    # 按分数从高到低选出前 top_k 个片段
    best_indices = np.argsort(-scores)[:top_k]

    results = []

    for position in best_indices:
        chunk = chunks[int(position)]

        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "source": chunk["source"],
                "section": chunk["section"],
                "text": chunk["text"],
                "score": float(scores[position]),
            }
        )

    return results


def main():
    question = " ".join(sys.argv[1:]).strip()

    if not question:
        question = input("请输入问题：").strip()

    results = search_knowledge(question)

    for rank, result in enumerate(results, start=1):
        print(f"\n--- 第 {rank} 名 ---")
        print(f"相似度：{result['score']:.4f}")
        print(f"来源：{result['source']}")
        print(f"章节：{result['section']}")
        print(f"片段编号：{result['chunk_id']}")
        print(f"内容：\n{result['text']}")


if __name__ == "__main__":
    main()