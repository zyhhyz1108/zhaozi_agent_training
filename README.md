# 培训课程管理后端

用于练习课程增删改查，后续接入培训知识 RAG 和 Agent 工具调用。

## 技术栈

- Python（3.11.9）
- uv
- FastAPI
- SQLAlchemy
- SQLite
- pytest

## 启动

安装依赖：

    uv sync

启动服务：

    uv run uvicorn app.main:app --reload --reload-dir app

接口文档：http://127.0.0.1:8000/docs

## 接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | /courses | 新增课程 |
| GET | /courses | 查询课程列表 |
| GET | /courses/{course_id} | 查询课程详情 |
| PATCH | /courses/{course_id} | 局部修改课程 |
| DELETE | /courses/{course_id} | 删除课程 |

## 数据与规则

- 数据保存到项目根目录 training.db。
- 课程状态：not_started、in_progress、completed。
- 允许课程同名。
- 修改时只更新提交的字段。
- 删除为真实删除。
- 当前为个人本地练习，不包含登录和多用户权限。
- 当前使用 create_all 建表，不支持自动更新已有表结构。

## 测试

    uv run python -m pytest -q

测试使用临时 SQLite 数据库。