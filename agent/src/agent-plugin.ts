import type { Context } from "@deepseek-ai/cordis";
import { runAgent } from "./loop.js";

export const name = "training-agent";
export const inject = ["training"];

export interface Config {
  question: string;
}

export async function apply(ctx: Context, config: Config) {
  if (!config.question?.trim()) {
    throw new Error("Agent 插件需要非空的问题");
  }

  console.log("[Agent 插件] 开始执行");

  const answer = await runAgent(
    config.question,
    (name, args) => ctx.training.execute(name, args),
  );

  console.log("\n最终回答：");
  console.log(answer);
}