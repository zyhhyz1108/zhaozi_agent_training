import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("CHAT_API_KEY")
    base_url = os.getenv("CHAT_BASE_URL")
    model = os.getenv("CHAT_MODEL")

    if not api_key or not base_url or not model:
        raise ValueError("请配置 CHAT_API_KEY、CHAT_BASE_URL 和 CHAT_MODEL")

    with OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
        max_retries=2,
    ) as client:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

    if not response.choices:
        raise ValueError("模型没有返回候选回答")

    answer = response.choices[0].message.content

    if not answer or not answer.strip():
        raise ValueError("模型返回了空回答")

    return answer.strip()


if __name__ == "__main__":
    answer = generate_answer(
        system_prompt="请使用简洁的中文回答。",
        user_prompt="用一句话说明什么是培训课程。",
    )
    print(answer)