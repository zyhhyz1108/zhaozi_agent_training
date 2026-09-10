import {
  listCourses,
  updateCourseStatus,
} from "./training-client.js";
import { searchKnowledge } from "./knowledge-client.js";

export async function executeTool(
  name: string,
  args: unknown,
) {
  switch (name) {
    case "list_courses":
      return await listCourses(args);

    case "search_training_knowledge":
      return await searchKnowledge(args);
    case "update_course_status":
      return await updateCourseStatus(args);
    default:
      throw new Error(`不支持的工具：${name}`);
  }
}