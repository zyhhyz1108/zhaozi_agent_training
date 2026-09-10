import { mkdir, appendFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const logDirectory = fileURLToPath(
  new URL("../logs/", import.meta.url),
);

export async function createTrace() {
  await mkdir(logDirectory, { recursive: true });

  const runId = randomUUID();
  const filePath = join(logDirectory, `${runId}.jsonl`);

  async function write(event: string, data: unknown) {
    const record = {
      run_id: runId,
      time: new Date().toISOString(),
      event,
      data,
    };

    await appendFile(
      filePath,
      JSON.stringify(record) + "\n",
      "utf8",
    );
  }

  return { runId, filePath, write };
}