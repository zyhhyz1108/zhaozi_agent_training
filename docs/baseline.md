# 项目基线记录

记录日期：2026-09-10

本记录在现有功能开发后补充，用于建立首次 Git 基线，
不代表开发时已逐阶段提交。

## 当前功能

- Python 课程 CRUD，使用 SQLite 保存数据。
- 本地 Markdown 资料切分、向量化、检索及知识问答。
- TypeScript Agent Loop，包含课程查询、知识检索、状态修改工具。
- Cordis 服务和插件组织。
- 状态修改前进行终端人工确认。
- JSONL 执行日志。

## 验证记录

- Python 课程接口测试：10 passed，1 条依赖弃用警告。
- TypeScript 类型检查：通过
- RAG 和 Agent 手工验证：没验证

## 当前边界

- 当前是手写 Agent Loop，项目内尚未完成 dsh 业务插件注册。
- 没有跨任务会话恢复和多用户权限。
- 人工确认仅控制 Agent 的修改路径。
- RAG 和 Agent 尚未完成完整自动化评测。

## 数据准备

培训资料自行放入 data/documents。
运行文档处理、索引构建命令生成 chunks.json 和 embeddings.json。
原始资料和生成索引不纳入本次基线提交。