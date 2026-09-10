import { z } from "zod";
import { confirmAction } from "./approval.js";

const CourseSchema = z.object({
  id: z.number().int().positive(),
  name: z.string(),
  description: z.string(),
  status: z.enum([
    "not_started",
    "in_progress",
    "completed",
  ]),
});

export type Course = z.infer<typeof CourseSchema>;

export const ListCoursesInput = z.object({
  offset: z.number().int().min(0).default(0),
  limit: z.number().int().min(1).max(100).default(20),
}).strict();

const backendUrl =
  process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function listCourses(input: unknown) {
  const args = ListCoursesInput.parse(input);

  const url = new URL("/courses", backendUrl);
  url.searchParams.set("offset", String(args.offset));
  url.searchParams.set("limit", String(args.limit));

  const response = await fetch(url, {
    signal: AbortSignal.timeout(10_000),
  });

  if (!response.ok) {
    throw new Error(`查询课程失败，HTTP ${response.status}`);
  }

  const raw: unknown = await response.json();
  const courses = z.array(CourseSchema).parse(raw);

  return {
    courses,
    offset: args.offset,
    limit: args.limit,
    returned_count: courses.length,
  };
}


const UpdateStatusInput = z.object({
  course_id: z.number().int().positive(),
  status: z.enum([
    "not_started",
    "in_progress",
    "completed",
  ]),
}).strict();


export async function updateCourseStatus(input: unknown) {
  const args = UpdateStatusInput.parse(input);
  const url = new URL(
    `/courses/${args.course_id}`,
    backendUrl,
  );

  // 先查询，确认操作对象和当前状态
  const beforeResponse = await fetch(url, {
    signal: AbortSignal.timeout(10_000),
  });

  if (!beforeResponse.ok) {
    throw new Error(
      `查询待修改课程失败，HTTP ${beforeResponse.status}`,
    );
  }

  const raw: unknown = await beforeResponse.json();
  const before = CourseSchema.parse(raw);

  if (before.status === args.status) {
    return {
      outcome: "unchanged",
      course: before,
      message: "课程已处于目标状态，无需修改",
    };
  }

  const approved = await confirmAction({
    action: "修改课程学习状态",
    course_id: before.id,
    course_name: before.name,
    previous_status: before.status,
    new_status: args.status,
  });

  if (!approved) {
    return {
      outcome: "cancelled",
      message: "用户取消操作，未发送修改请求",
    };
  }

  const response = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      status: args.status,
    }),
    signal: AbortSignal.timeout(10_000),
  });

  if (!response.ok) {
    throw new Error(`修改课程失败，HTTP ${response.status}`);
  }

  const updated: unknown = await response.json();

  return {
    outcome: "updated",
    course: CourseSchema.parse(updated),
  };
}