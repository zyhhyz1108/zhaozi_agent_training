import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts or any(not text.strip() for text in texts):
        raise ValueError("输入必须包含非空文本")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_BASE_URL")
    model = os.getenv("EMBEDDING_MODEL")
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))

    if not api_key or not base_url or not model:
        raise ValueError("请在 .env 中填写密钥、接口地址和模型名称")

    with OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=30.0,
        max_retries=2,
    ) as client:
        response = client.embeddings.create(
            model=model,
            input=texts,
            dimensions=dimensions,
            encoding_format="float",
        )

    # 按输入顺序排列返回的向量
    items = sorted(response.data, key=lambda item: item.index)
    vectors = [item.embedding for item in items]

    if len(vectors) != len(texts):
        raise ValueError("返回的向量数量与输入文本数量不一致")

    if any(len(vector) != dimensions for vector in vectors):
        raise ValueError("返回的向量维度与配置不一致")

    return vectors


def main():
    texts = [
        "课程学完后，将学习状态改为已完成。",
        "完成课程以后应该设置什么状态？",
    ]

    vectors = embed_texts(texts)

    print(f"输入文本数量：{len(texts)}")
    print(f"返回向量数量：{len(vectors)}")

    for index, vector in enumerate(vectors, start=1):
        print(f"第 {index} 个向量：维度={len(vector)}")
        print(f"前 5 个数值：{vector[:5]}")


if __name__ == "__main__":
    main()