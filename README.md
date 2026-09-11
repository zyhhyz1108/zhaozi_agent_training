# 培训课程管理与 Agent 学习项目

本项目实现课程管理、培训知识 RAG 和 TypeScript Agent 工具调用，并通过 Cordis 组织服务与插件。DSH 课程查询与知识检索插件复用现有后端能力。

## 当前功能

| 部分 | 已实现内容 |
|---|---|
| 课程后端 | 新增、分页查询、详情查询、修改、删除，参数校验和 SQLite 持久化 |
| RAG | Markdown 切分、批量向量化、JSON 索引、相似度检索、带引用编号的问答 |
| 自写 Agent | 模型选择工具、执行结果回传、循环限制、JSONL 运行日志 |
| Agent 工具 | 课程查询、知识检索、课程状态修改；修改前终端 yes/no 确认 |
| Cordis | training 服务、Agent 插件、加载与清理 |
| DSH 插件 | 注册只读的 list_courses 和 search_training_knowledge 工具 |

DSH 网页端课程修改审批尚未接入。插件文件存在不等于运行验证通过，应按下文检查实际调用轨迹。

## 模块与调用关系

```text
命令行 main.ts → 自写 loop.ts → tools.ts ───────────────┐
Cordis 入口 → agent-plugin → 自写 loop → training 服务 ─┤
DSH 网页 → DSH 自身循环 → dsh-training-plugin ─────────┤
                                                     ↓
                              training-client / knowledge-client
                                                     ↓ HTTP
                                   Python FastAPI → SQLite / RAG
```

DSH 插件直接复用 training-client 和 knowledge-client，不经过自写 loop 或 training 服务。

| 位置 | 职责 |
|---|---|
| `app/main.py` | 应用启动、建表、挂载路由 |
| `app/routes.py`、`schemas.py` | 课程 HTTP 接口与数据校验 |
| `app/repositories.py`、`models.py`、`database.py` | 数据操作、表结构与数据库会话 |
| `app/rag/` | 文档处理、向量索引、检索、问答和知识接口 |
| `agent/src/main.ts`、`loop.ts` | 自写 Agent 入口与模型工具循环 |
| `agent/src/*-client.ts`、`tools.ts` | 后端请求与工具分发 |
| `agent/src/approval.ts`、`trace.ts` | 终端审批与运行日志 |
| `agent/src/training-service.ts`、`agent-plugin.ts` | Cordis 服务与 Agent 插件 |
| `agent/src/training-plugin.ts` | 旧演示：加载后固定查询一次课程并打印 |
| `agent/src/cordis-main.ts` | 加载 training 服务和 Agent 插件 |
| `agent/src/dsh-training-plugin.ts` | 向 DSH 注册课程查询与知识检索工具 |
| `tests/`、`conftest.py` | 课程接口测试与临时数据库 fixture |
| `docs/baseline.md` | 基线范围和历史验证记录 |

## 环境与安装

需要 Python 3.11 或以上、uv、Node.js 和 npm。开发环境使用 Windows PowerShell；Node.js 建议使用与本地依赖匹配的 24 系列。Python 依赖由 uv.lock 管理，Agent 依赖由 agent/package-lock.json 管理。

以下命令从项目根目录执行，除非明确要求进入 agent。本机项目根目录为 `C:/Users/66413/Desktop/zhaozi_agent_loop`，其他机器替换为自己的克隆目录。

```powershell
uv sync
npm --prefix agent ci
```

首次配置时，将 `.env.example` 复制为 `.env`。已有 `.env` 时不要覆盖：

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

在编辑器中填写配置，不要将真实密钥提交到 Git。

| 配置 | 用途 |
|---|---|
| `DASHSCOPE_API_KEY`、`DASHSCOPE_BASE_URL` | 向量服务密钥和 OpenAI 兼容接口地址 |
| `EMBEDDING_MODEL`、`EMBEDDING_DIMENSIONS` | 实际可用的向量模型 ID 与支持的维度 |
| `CHAT_API_KEY`、`CHAT_BASE_URL`、`CHAT_MODEL` | Python 问答和自写 Agent 的聊天模型配置 |
| `BACKEND_URL` | TypeScript 客户端访问后端的地址，默认 http://127.0.0.1:8000 |

自写 Agent 的模型接口需要支持 Chat Completions 自定义 Function Calling。DSH 的聊天模型在 DSH 中单独配置。

## 启动后端

在项目根目录运行并保持终端开启：

```powershell
uv run uvicorn app.main:app --reload --reload-dir app
```

- 接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>
- `/` 未定义页面，访问根路径返回 404 不代表服务启动失败。

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | /health | 健康检查 |
| POST | /courses | 新增课程 |
| GET | /courses | 分页查询，offset 默认 0，limit 默认 20 |
| GET | /courses/{course_id} | 查询详情 |
| PATCH | /courses/{course_id} | 局部修改 |
| DELETE | /courses/{course_id} | 删除课程 |
| POST | /knowledge/search | 返回相关文档片段与相似度分数 |
| POST | /knowledge/ask | 返回生成答案和参考资料 |

可以在接口文档中创建课程，例如 `{"name":"Python 基础","description":"学习函数、类和异常处理"}`。

课程状态为 `not_started`、`in_progress`、`completed`；允许同名；修改只更新提交字段；删除为真实删除。数据库路径相对于启动目录，因此请始终从项目根目录启动。

## 建立知识库与问答

将 UTF-8 Markdown 文档放入项目的 `data/documents/`。当前只读取该目录第一层的 `.md` 文件，不递归读取子目录。原始资料若未纳入 Git，克隆后需自行提供。

配置向量服务后依次执行：

```powershell
uv run python -m app.rag.ingest
uv run python -m app.rag.build_index
```

第一步生成 `data/chunks.json`；第二步调用向量服务，生成 `data/embeddings.json`。文档和问题必须使用相同的向量模型与维度；更换模型、维度或文档后重新建立索引。

配置聊天模型后可直接运行问答，无需先启动 HTTP 服务：

```powershell
uv run python -m app.rag.ask "敏感操作前需要做什么？"
```

也可在接口文档调用 `/knowledge/search`：

```json
{"question":"敏感操作前需要做什么？","top_k":3}
```

`top_k` 范围为 1 到 5。`/knowledge/ask` 只需提交 question。建立索引、检索和问答会按各自需要调用外部模型服务。

## 运行自己的 Agent

先启动后端；知识检索还需先建立索引。以下命令在另一个终端执行。

普通命令行入口，从项目根目录运行：

```powershell
npm --prefix agent run dev -- "查询我的课程，告诉我哪些还没有完成"
```

Cordis 入口，先进入 agent：

```powershell
cd agent
npx tsx src/cordis-main.ts "查询我的课程，告诉我哪些还没有完成"
```

两种入口均运行自写 Agent 循环。Cordis 入口通过 training 服务执行工具，不会加载旧的 training-demo 演示插件。

可尝试“根据学习手册说明敏感操作前需要做什么”或“把 Python 基础课程改成学习中”。修改操作会在交互终端展示具体变更，输入 `yes` 才执行，其他输入取消；目标状态已经一致时会跳过修改。

运行日志写入 `agent/logs/` 的 JSONL 文件。这些日志用于排查，不是可恢复会话或长期记忆。

## 在 DSH 中加载课程查询与知识检索

当前插件注册 `list_courses` 和 `search_training_knowledge`，不注册修改工具。先安装 Agent 依赖并启动后端；知识检索还需配置后端向量服务并建立索引。新增知识工具沿用同一插件文件，已有加载配置无需增加第二条。

在编辑器中打开本机配置 `C:/Users/66413/.dsh/profiles/web/cordis.patch.yml`。其他机器使用对应用户目录。如果内容为 `[]`，替换为下方配置；已有配置时追加该条目，保留其他插件：

```yaml
- insert:
    - id: training-courses
      name: 'C:/Users/66413/Desktop/zhaozi_agent_loop/agent/src/dsh-training-plugin.ts'
```

插件路径必须换成当前机器的绝对路径。该配置位于用户目录，不随本仓库提交；换机器需重新配置。

DSH 插件不导入自写 Agent 的 config.ts，因此不会自动读取项目 `.env`。默认后端为 http://127.0.0.1:8000；使用其他地址时，在启动 DSH 的终端设置：

```powershell
$env:BACKEND_URL = "http://127.0.0.1:8000"
```

停止已有 DSH 进程后，使用本项目接入时的版本启动：

```powershell
npx @deepseek-ai/dsh@0.1.2-rc.1 web
```

在 DSH 中配置聊天模型，打开启动日志提供的网页地址，新建会话输入：

> 请调用 list_courses 工具，offset 为 0，limit 为 20，查询我的课程并列出学习状态。

验证轨迹中确实出现 list_courses，并核对工具返回数据与最终回答。只看到文字回答不足以证明插件调用成功。分页结果只代表本页，不能直接当作全部课程。

知识检索测试：

> 请调用 search_training_knowledge，question 为“敏感操作前需要做什么？”，top_k 为 3。根据原文回答并注明来源文件和章节；依据不足时明确说明。

检查轨迹中出现该工具，结果包含 hits，每个片段有 source、section、text 和 score。该工具调用 /knowledge/search，由 DSH 模型组织答案，不调用 /knowledge/ask。重启 DSH 后在新会话验证；代码和类型检查通过不代表实际模型、索引与服务连接已验证。

## 检查与验证

以下命令从项目根目录执行：

```powershell
uv run python -m pytest -q
npm --prefix agent run check
git diff --check
```

pytest 使用临时 SQLite 数据库；现有测试主要覆盖课程 CRUD 和非法输入。`check` 执行 `tsc --noEmit`，只检查 TypeScript 类型，不运行 Agent，也不验证后端、模型连接或 DSH 插件加载。`npm test` 目前仍为占位脚本。

手工验证应记录实际日期、场景和结果：

- 课程查询返回真实数据，分页与学习状态正确。
- 知识检索有相关片段；问答引用能对应本次参考资料。
- 终端修改分别测试批准和取消，随后查询确认数据库状态。
- DSH 轨迹显示真实 list_courses 和 search_training_knowledge 调用，检索回答与返回片段一致。
- 后端关闭或请求失败时明确报告错误，不编造结果。

## 数据、限制与后续工作

- `training.db` 保存课程；chunks.json 和 embeddings.json 保存知识片段及向量，两者用途不同。
- `.env`、本地数据库、依赖目录、运行日志和生成索引应保持在 Git 提交之外；原始文档需按内容决定是否提交。
- 当前为本地单用户练习，没有登录和多用户权限。create_all 只负责建表，不自动迁移已有表结构。
- RAG 尚未建立系统评测集；有引用编号不保证回答完全正确。
- 终端审批不能直接作为 DSH 网页审批使用。
- 后续依次验证 DSH 多工具协作、补充评测，再适配网页修改审批。
- 每个功能完成后记录实际验证结果并创建本地提交；push 是独立的远程上传操作。
