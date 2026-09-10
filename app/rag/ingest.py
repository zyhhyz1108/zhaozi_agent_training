import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENT_DIR = PROJECT_ROOT / "data" / "documents"
OUTPUT_FILE = PROJECT_ROOT / "data" / "chunks.json"


def split_markdown(
    text: str,
    source: str,
    chunk_size: int = 600,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    chunks = []
    headings = []
    buffer = []
    in_code_block = False

    def flush():
        content = "\n".join(buffer).strip()
        buffer.clear()

        if not content:
            return

        # 长章节进一步按字符数切分
        for start in range(0, len(content), chunk_size):
            piece = content[start:start + chunk_size].strip()

            if piece:
                chunks.append(
                    {
                        "chunk_id": f"{source}::{len(chunks) + 1}",
                        "source": source,
                        "section": " / ".join(
                            title for _, title in headings
                        ) or "正文",
                        "text": piece,
                    }
                )

    for line in text.splitlines():
        # 避免把代码块里的 # 当成章节标题
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            buffer.append(line)
            continue

        heading = None
        if not in_code_block:
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)

        if heading:
            # 先保存上一章节，再更新章节路径
            flush()

            level = len(heading.group(1))
            title = heading.group(2).strip()

            while headings and headings[-1][0] >= level:
                headings.pop()

            headings.append((level, title))
        else:
            buffer.append(line)

    flush()
    return chunks


def main():
    files = sorted(DOCUMENT_DIR.glob("*.md"))

    if not files:
        raise FileNotFoundError(
            f"没有找到 Markdown 文档，请检查：{DOCUMENT_DIR}"
        )

    all_chunks = []

    for path in files:
        text = path.read_text(encoding="utf-8-sig")
        chunks = split_markdown(text, source=path.name)
        all_chunks.extend(chunks)

        print(f"{path.name}：生成 {len(chunks)} 个片段")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"总片段数：{len(all_chunks)}")
    print(f"输出文件：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()