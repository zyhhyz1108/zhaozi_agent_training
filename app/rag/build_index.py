import json
import os
from pathlib import Path

from app.rag.embedding import embed_texts


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "chunks.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "embeddings.json"

# 每次提交 5 个片段
BATCH_SIZE = 5


def main():
    chunks = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    if not isinstance(chunks, list) or not chunks:
        raise ValueError("chunks.json 必须是非空的片段列表")

    # 在调用模型之前，先检查全部片段
    seen_ids = set()

    for chunk in chunks:
        for field in ("chunk_id", "source", "section", "text"):
            if not isinstance(chunk.get(field), str):
                raise ValueError(f"片段缺少有效字段：{field}")

        if not chunk["text"].strip():
            raise ValueError(f"片段内容为空：{chunk['chunk_id']}")

        if chunk["chunk_id"] in seen_ids:
            raise ValueError(f"片段编号重复：{chunk['chunk_id']}")

        seen_ids.add(chunk["chunk_id"])

    records = []
    total = len(chunks)

    for start in range(0, total, BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [chunk["text"] for chunk in batch]

        vectors = embed_texts(texts)

        for chunk, vector in zip(batch, vectors):
            records.append(
                {
                    **chunk,
                    "embedding": vector,
                }
            )

        print(f"已完成：{len(records)}/{total}")

    index = {
        "model": os.environ["EMBEDDING_MODEL"],
        "dimensions": int(os.getenv("EMBEDDING_DIMENSIONS", "1024")),
        "count": len(records),
        "chunks": records,
    }

    # 全部成功后再替换正式文件，避免留下不完整索引
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(OUTPUT_FILE)

    print(f"索引已保存：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()