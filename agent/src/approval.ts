import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";


export async function confirmAction(
  details: unknown,
): Promise<boolean> {
  if (!stdin.isTTY || !stdout.isTTY) {
    throw new Error("写操作需要交互式终端确认");
  }

  console.log("\n待确认操作：");
  console.log(JSON.stringify(details, null, 2));

  const terminal = createInterface({
    input: stdin,
    output: stdout,
  });

  try {
    const answer = await terminal.question(
      "输入 yes 执行，其他输入取消：",
    );

    return answer.trim() === "yes";
  } finally {
    terminal.close();
  }
}