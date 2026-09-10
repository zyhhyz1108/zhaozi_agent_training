import { Service, type Context } from "@deepseek-ai/cordis";

import { executeTool } from "./tools.js";


declare module "@deepseek-ai/cordis" {
  interface Context {
    training: TrainingService;
  }
}


export class TrainingService extends Service {
  constructor(ctx: Context) {
    super(ctx, "training");
  }

  async execute(name: string, args: unknown) {
    return await executeTool(name, args);
  }
}