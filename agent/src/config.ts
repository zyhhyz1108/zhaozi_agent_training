import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({
  path: fileURLToPath(new URL("../../.env", import.meta.url)),
});

function required(name: string): string {
  const value = process.env[name]?.trim();

  if (!value) {
    throw new Error(`缺少环境变量：${name}`);
  }

  return value;
}

export const settings = {
  apiKey: required("CHAT_API_KEY"),
  baseURL: required("CHAT_BASE_URL"),
  model: required("CHAT_MODEL"),
};