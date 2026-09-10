import { z } from "zod";

const SearchInput = z.object({
  question: z.string().trim().min(1).max(2000),
  top_k: z.number().int().min(1).max(5).default(3),
}).strict();

const SearchHit = z.object({
  chunk_id: z.string(),
  source: z.string(),
  section: z.string(),
  text: z.string(),
  score: z.number().finite(),
});

export async function searchKnowledge(input: unknown) {
  const args = SearchInput.parse(input);

  const baseURL =
    process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

  const response = await fetch(
    new URL("/knowledge/search", baseURL),
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(args),
      signal: AbortSignal.timeout(120_000),
    },
  );

  if (!response.ok) {
    throw new Error(`知识检索失败，HTTP ${response.status}`);
  }

  const raw: unknown = await response.json();
  const hits = z.array(SearchHit).parse(raw);

  return {
    question: args.question,
    hits,
  };
}