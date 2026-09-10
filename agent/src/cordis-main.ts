import "./config.js";

import { Context } from "@deepseek-ai/cordis";
import { TrainingService } from "./training-service.js";
import * as agentPlugin from "./agent-plugin.js";

async function main() {
  const question = process.argv.slice(2).join(" ").trim();

  if (!question) {
    throw new Error("请在命令后提供问题");
  }

  const root = new Context();

  try {
    await root.plugin(TrainingService);
    await root.plugin(agentPlugin, { question });
  } finally {
    await root.fiber.dispose();
    console.log("[主程序] Cordis 已清理");
  }
}

main().catch((error: unknown) => {
  console.error(
    error instanceof Error ? error.message : String(error),
  );
  process.exitCode = 1;
});