# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CortexVerse 是一个系统驱动的虚拟内容生产线（Synthetic Content Pipeline）。采用"数值底座 + 主循环引擎（Game Loop）"架构，通过 Multi-Agent 系统、游戏循环机制、数值资源约束和持续反馈循环，生成无限且高度一致的短剧集。

核心设计原则：
- **纯状态机编排** — 不使用 LangGraph、AutoGen、LangChain，用原生 Python `asyncio` 循环和自定义路由逻辑
- **数据驱动（DDD-Lite）** — 以 `domain/` 层为核心，所有实体（World、Character、Narrative Node）用 Pydantic v2 严格类型化
- **确定性 LLM 输出** — 所有 LLM 调用通过 `instructor` 库，输出必须符合 Pydantic schema 的严格 JSON
- **数值冲突驱动** — 剧情由系统规则驱动（如 $Resource < Threshold \rightarrow Trigger\_Conflict$），而非开放式 prompt

## Tech Stack

- **Language**: Python 3.10+（推荐 3.12+）
- **Package Manager**: `uv`
- **Data Modeling**: Pydantic v2
- **LLM Gateway**: `instructor` + `litellm`（所有 LLM 调用必须结构化并经 Pydantic 验证）
- **Async Engine**: 原生 Python `asyncio`
- **API Framework**: FastAPI
- **Task Queue**: ARQ（Async Redis Queue）
- **Database**: PostgreSQL（SQLAlchemy 2.0 Async + JSONB）
- **Cache/State**: Redis（WorldState 缓存 + ARQ 消息代理）
- **Media Generation**: ComfyUI（IP-Adapter/FaceID）+ TTS（CosyVoice/F5-TTS）
- **Frontend**: Next.js + TypeScript + Zustand + shadcn/ui + TailwindCSS + React Flow
- **Linting**: Ruff + mypy

## Project Structure

```
cortexverse/
├── domain/                  # 纯数据层 — Pydantic 模型（World、Character、Narrative、Script），不含 LLM 逻辑
├── agents/                  # 推理层 — 无状态异步函数（Node），输入 State → 输出更新后的 State
│   ├── world_builder/
│   ├── character_engine/
│   ├── narrative_planner/
│   └── script_translator/
├── workflows/               # 编排层 — Game Loop（episode_loop.py）
├── infrastructure/          # 外部集成 — LLM 客户端、ComfyUI 适配器、数据库 Repository
├── interfaces/              # API 层 — FastAPI 路由和后台任务 Worker
└── main.py                  # 入口
```

## Agent 编写模式

`agents/` 中的 Agent 不是复杂类层次，而是无状态异步函数：

```python
async def run_planner_node(current_state: WorldState) -> WorldState:
    # 1. 从 current_state 准备上下文
    # 2. 通过 instructor 调用 LLM 获取结构化更新
    # 3. 将更新应用到 current_state
    # 4. 返回 current_state
```

## 关键约束

- `domain/` 目录禁止写业务逻辑或 LLM 调用，只放 `pydantic.BaseModel` 类
- **禁止引入** LangChain、LangGraph、AutoGen、CrewAI；需要图路由时用 `while` + `match/case` 实现
- 多模态一致性：角色的 `visual_seed` / `character_face_id` 必须显式传递，Media Adapter（L5）依赖这些引用维持角色一致性
- LLM 调用统一通过 `instructor`，输出必须是符合 Pydantic schema 的 JSON

## Coding Conventions

### 代码注释语言

所有代码注释必须使用**中文**。技术术语、库名、API 名称可保留英文（如 `HTTP`、`OAuth`、`Redis`、`async/await`）。变量名/函数名/类名不受限制。

```python
# ❌ 错误
# Get the user session from Redis cache

# ✅ 正确
# 从 Redis 缓存中获取用户 session
```

### Python 风格（Google Python Style Guide）

- **缩进**: 4 空格，禁止 Tab
- **行长**: 最大 120 字符
- **命名**: `snake_case`（函数/模块）、`CapWords`（类）、`UPPER_SNAKE_CASE`（常量）
- **Import**: 每行一个模块；顺序：标准库 → 第三方 → 本地；禁止 `from module import *`
- **Docstring**: Google 风格，所有公共模块/类/函数必须有
- **类型注解**: 所有公共函数必须有
- **异常处理**: 禁止裸 `except:`；必须指定异常类型；禁止静默忽略
- **Lambda**: 禁止将 lambda 赋值给变量，用 `def` 替代
- **函数规模**: 单函数不超过 50 行
- **推导式**: 最多 2 层嵌套

### 工程规则

- 最小变更原则，优先 patch-style 编辑
- 未明确要求不重写大段代码
- 未获许可不引入新框架或依赖
- 未讨论不重组项目结构
- 可读性优先于巧妙性；最多 3 层嵌套
- 未明确要求不删除文件、不重构代码
- 不做纯格式化变更
- 所有公共类/函数必须有简洁的描述注释

### 前端设计

避免通用 "AI 模板化" 审美 — 不使用过度居中布局、紫色渐变、统一圆角或 Inter 字体。使用独特字体、大胆配色和创意布局。
