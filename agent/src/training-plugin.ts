import type { Context } from "@deepseek-ai/cordis";


export const name = "training-demo";
export const inject = ["training"];


export async function apply(ctx: Context) {
  console.log("[插件] training-demo 已启动");

  const result = await ctx.training.execute(
    "list_courses",
    {
      offset: 0,
      limit: 20,
    },
  );

  console.log("[插件] 课程查询结果：");
  console.log(JSON.stringify(result, null, 2));
}