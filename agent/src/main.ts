import { runAgent } from "./loop.js";
import { executeTool } from "./tools.js";

async function main() {
  const question = process.argv.slice(2).join(" ").trim();

  if (!question) {
    throw new Error(
      '请提供问题，例如：npm run dev -- "查询我的课程"',
    );
  }

  const answer = await runAgent(question, executeTool);

  console.log("\n最终回答：");
  console.log(answer);
}

main().catch((error: unknown) => {
  const message =
    error instanceof Error ? error.message : String(error);

  console.error(`Agent 执行失败：${message}`);
  process.exitCode = 1;
});