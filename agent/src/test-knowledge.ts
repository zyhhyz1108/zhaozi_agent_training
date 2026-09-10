import { executeTool } from "./tools.js";

async function main() {
  const result = await executeTool(
    "search_training_knowledge",
    {
      question: "敏感操作前需要做什么？",
      top_k: 3,
    },
  );

  console.log(JSON.stringify(result, null, 2));
}

main().catch((error: unknown) => {
  console.error(
    error instanceof Error ? error.message : String(error),
  );
  process.exitCode = 1;
});