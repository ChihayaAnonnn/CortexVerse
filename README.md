# CortexVerse

**系统驱动的虚拟内容生产线（Synthetic Content Pipeline）**

CortexVerse 采用"数值底座 + 主循环引擎（Game Loop）"架构，通过 Multi-Agent 系统、游戏循环机制、数值资源约束和持续反馈循环，生成无限且高度一致的短剧集。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12+ · FastAPI · Pydantic v2 · asyncio |
| LLM | instructor + 原生 SDK 直连（OpenAI/DeepSeek） |
| 前端 | React 18 · TypeScript · Vite · TailwindCSS |
| 数据库 | PostgreSQL（SQLAlchemy 2.0 Async） · Redis |
| 部署 | Docker · ARQ（任务队列） |

## 项目结构

```
CortexVerse/
├── config/
│   ├── agents.yaml              # Agent 配置（model、prompt 模板）
│   └── llm_providers.yaml       # LLM Provider 配置
├── cortexverse/                 # 后端
│   ├── domain/                  # 纯数据层（Pydantic 模型）
│   ├── agents/                  # Schema 注册
│   ├── workflows/               # 编排层（世界构建、剧集循环）
│   ├── infrastructure/          # Agent 工厂、LLM 客户端
│   └── interfaces/              # FastAPI 路由
├── web/                         # 前端（React）
│   └── src/
│       ├── api/                 # API 调用封装
│       ├── components/          # UI 组件
│       └── types/               # TypeScript 类型
├── tests/                       # 测试
└── docs/                        # 文档
```

## 快速开始

### 环境准备

```bash
# 安装 Python 依赖
uv sync

# 安装前端依赖
cd web && npm install && cd ..
```

### 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 在 `.env` 中设置 API Key：
```bash
DEEPSEEK_API_KEY=sk-xxx
```

### 启动服务

```bash
# 终端 1：启动后端
uv run uvicorn cortexverse.main:app --reload

# 终端 2：启动前端
cd web && npm run dev
```

访问 `http://localhost:5173`

## API 接口

### 世界构建

```bash
curl -X POST http://localhost:8000/api/world/generate \
  -H "Content-Type: application/json" \
  -d '{
    "world_name": "霓虹深渊",
    "genre_tags": ["赛博朋克", "废土"],
    "theme_input": "底层逆袭，打破阶级固化"
  }'
```

### 响应格式

```json
{
  "world_id": "world_a1b2c3d4",
  "status": "completed",
  "world_asset": {
    "world_id": "world_a1b2c3d4",
    "name": "霓虹深渊",
    "genre_tags": ["赛博朋克", "废土"],
    "macro_philosophy": { ... },
    "macro_history": { ... },
    "macro_growth": { ... },
    "micro_factions": [ ... ],
    "micro_characters": [ ... ],
    "micro_resources": [ ... ],
    "micro_conflicts": [ ... ],
    "micro_hierarchy": [ ... ],
    "micro_locations": [ ... ]
  }
}
```

## 架构设计

### 四阶段世界构建流水线

```
macro_architect → geography_subagent → economy_subagent → conflict_subagent
    (宏观哲学)        (地理节点)          (经济社会)          (冲突编排)
```

每个阶段输出经 Pydantic 严格校验，上游输出作为下游上下文。

### Agent 工厂模式

- **配置驱动**：`agents.yaml` 定义 model、prompt 模板、model_settings
- **Schema 注册**：`@register_schema` 装饰器将 Pydantic 模型注册到 `SCHEMA_REGISTRY`
- **一致性断言**：启动时 YAML key 集合必须与注册表严格一致

### LLM 客户端工厂

- **多 Provider 支持**：`llm_providers.yaml` 配置 OpenAI/DeepSeek 等
- **原生 SDK 直连**：不依赖 litellm，直接使用 openai SDK
- **实例缓存**：按 provider 名称缓存 instructor 客户端

## 测试

```bash
# 运行全量测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/infrastructure/test_factory.py
```

## 文档

- [统一领域模型设计](cortexverse/docs/prd/统一领域模型设计.md)
- [世界观构筑引擎 PRD](cortexverse/docs/prd/世界观构筑引擎%20(World%20Builder%20Engine)%20v%204.0.md)
- [AgentFactory 架构设计](cortexverse/docs/architecture/AgentFactory.md)

## License

MIT
