# CortexVerse: 通用 Agent 工厂开发指南 (Developer Guide)

**文档版本：** v3.0
**所属模块：** Core Engine (核心引擎层)
**核心技术栈：** Python 3.13+ | `instructor` | `litellm` | `pydantic v2` | `PyYAML`

## 一、 架构概述 (Architecture Overview)

CortexVerse 采用 **配置驱动 (Config-Driven) + 注册表 (Registry) + 工厂 (Factory)** 三位一体模式管理所有大语言模型 (LLM) 智能体。

本工厂为**跨阶段通用基建**：对任何具体业务阶段（世界观构建、角色引擎、叙事规划、剧本翻译）零耦合。阶段差异只体现在四处——领域模型、Schema 注册、YAML 条目、`workflows/` 编排，工厂与产出的 Agent 本身完全复用。

核心职责边界（必须严格遵守）：

1. **AgentFactory：只生产，不推理。** 读取配置 + 绑定 Schema，产出 `CortexAgent` 实例。
2. **CortexAgent.run()：单次纯推理。** 一次 LLM 调用 → 一次 `instructor` 校验，无状态、不循环。
3. **workflows 编排层：驱动循环。** 语义/关系级失败的 refine 重试由编排层驱动，符合"纯状态机 + 无状态 Agent"原则。

设计要解决的痛点：

1. **Prompt 资产化：** 将 Prompt 从业务代码剥离，实现 Prompt-as-Code，便于版本控制与策划独立调优。
2. **强类型约束：** 所有 Agent 输出强制映射到 `Pydantic` 实体（支持单体 `Model` 或 `list[Model]`），100% JSON Schema 校验。
3. **单一事实源：** Schema 绑定通过装饰器集中注册，启动时与 YAML 做一致性断言，根除配置漂移。
4. **依赖倒置与热更新：** 业务层只调度工厂产出的 `CortexAgent`，不关心底层是 OpenAI 还是 Claude（经 `litellm` 路由），并支持运行时重载配置。

---

## 二、 目录结构规范

```text
cortexverse/
├── config/                          # 【资产层】agents.yaml 配置文件
├── domain/                          # 【实体层】纯 Pydantic 模型，禁业务逻辑
│   ├── macro.py
│   ├── micro.py
│   └── world_asset.py
├── infrastructure/                  # 【基建层】核心工程能力
│   ├── agent_factory/               # 通用工厂目录
│   │   ├── __init__.py              # 导出 AgentFactory / register_schema
│   │   ├── registry.py              # @register_schema 装饰器 + SCHEMA_REGISTRY
│   │   ├── rendering.py             # ${var} 渲染引擎 + 非字符串序列化
│   │   └── factory.py              # AgentFactory(生产) + CortexAgent(单次推理)
│   ├── llm_clients/                 # Instructor 客户端配置
│   │   └── client.py
│   └── repositories/                # 世界资产持久化
├── agents/                          # 【装配层】Schema 注册声明 + 业务封装
└── workflows/                       # 【编排层】DAG 编排 + refine 循环驱动
```

> **关键调整：** 注册表从 `domain/` 移至 `infrastructure/agent_factory/`，保证 `domain/` 仅含纯 Pydantic 模型（遵循项目约束）。

---

## 三、 核心模块实现详解

### 3.1 资产层：`config/agents.yaml`

所有 Agent 的系统设定在此维护。Prompt 中使用 `${变量名}` 作为动态占位符，由调度端在运行时注入。采用 `${}` 而非 `{}`，避免与 prompt 文本中的字面量 `{`/`}`（如 JSON 示例、SD 视觉 Tag）冲突。

```yaml
# config/agents.yaml
world_builder:
  model: "gpt-4o-2024-08-06"
  retries: 3
  model_settings:
    temperature: 0.7
    max_tokens: 4096
  system_instructions:
    - "你是一个专业世界观架构师。"
    - "根据用户的题材标签和创作意图，生成完整、自洽、可商业化的世界观资产。"
    - "所有实体 ID 必须遵循命名规范，所有关系引用必须完整且合法。"
  user_prompt_templates:
    generate_world:
      - "请根据以下要求生成一个完整的世界观资产："
      - "题材标签：${genre_tags}"
      - "创作意图：${creative_intent}"
    refine_world:
      - "上一次生成未通过关系校验。错误信息如下："
      - "${feedback}"
      - "请根据反馈修正世界观资产。"

economy_subagent:
  model: "gpt-4o-2024-08-06"
  retries: 3
  model_settings:
    temperature: 0.2
  system_instructions:
    - "你是一位残酷的经济精算师与阶级设计师。"
    - "严格遵循以下宏观世界法则进行推演："
    - "${macro_context}"
  user_prompt_templates:
    generate_economy:
      - "请基于当前世界观，产出带有明确晋升代价的阶级系统列表。"
    refine_economy:
      - "上一次推演未通过质检。质检反馈如下："
      - "${feedback}"
      - "请根据反馈修正阶级表。"
```

### 3.2 注册表：`infrastructure/agent_factory/registry.py`

建立配置 `Key` 与 Python 强类型 `Pydantic Class` 的硬连接。采用**装饰器注册**实现单一事实源，并支持 `list[Model]` 产出形态（SubAgent 产出原子节点列表，由编排层合并进父聚合）。

```python
# cortexverse/infrastructure/agent_factory/registry.py
"""Agent 输出 Schema 注册表 — 单一事实源。"""

from typing import Any

from pydantic import BaseModel

# 配置 Key → 响应模型（Model 或 list[Model]）
SCHEMA_REGISTRY: dict[str, Any] = {}


def register_schema(agent_key: str, *, many: bool = False):
    """将 Pydantic 模型注册到指定 agent_key。

    Args:
        agent_key: 与 agents.yaml 中的节点 Key 对应。
        many: 为 True 时产出形态为 list[Model]，用于产出原子节点列表的 SubAgent。

    Returns:
        类装饰器；不改变被装饰类本身。
    """
    def decorator(model: type[BaseModel]) -> type[BaseModel]:
        SCHEMA_REGISTRY[agent_key] = list[model] if many else model
        return model
    return decorator
```

### 3.3 装配层：Schema 注册声明

为保持 `domain/` 纯净，注册声明集中在 `agents/` 装配模块中显式触发（导入领域模型并注册），而非污染 domain 文件。

```python
# cortexverse/agents/_schema_bindings.py
"""集中注册所有 Agent 的输出 Schema（导入即生效）。"""

from cortexverse.domain.micro import MicroPowerTier
from cortexverse.domain.world_asset import WorldAsset
from cortexverse.infrastructure.agent_factory.registry import register_schema

# 单体聚合：一次产出完整 WorldAsset
register_schema("world_builder")(WorldAsset)

# 列表产出：SubAgent 产出原子节点列表 → list[MicroPowerTier]
register_schema("economy_subagent", many=True)(MicroPowerTier)
```

### 3.4 严格渲染引擎：`infrastructure/agent_factory/rendering.py`

`${var}` 占位 + 缺失变量熔断 + 非字符串上下文自动序列化（如 `MacroPhilosophy` 对象 → JSON）。

```python
# cortexverse/infrastructure/agent_factory/rendering.py
"""Prompt 渲染引擎 — ${var} 占位、缺失熔断、对象自动序列化。"""

import json
from string import Template
from typing import Any

from pydantic import BaseModel


def _to_text(value: Any) -> str:
    """将上下文值统一序列化为字符串。"""
    if isinstance(value, str):
        return value
    if isinstance(value, BaseModel):
        return value.model_dump_json()
    return json.dumps(value, ensure_ascii=False)


def render_prompt(prompt_lines: list[str], context: dict[str, Any]) -> str:
    """合并模板行并渲染 ${var} 变量。

    Args:
        prompt_lines: Prompt 模板行列表。
        context: 渲染上下文；非字符串值将被自动序列化。

    Returns:
        渲染后的完整 prompt 字符串。

    Raises:
        ValueError: 当缺失必须的上下文变量时。
    """
    raw_text = "\n".join(prompt_lines).strip()
    safe_context = {key: _to_text(val) for key, val in context.items()}
    try:
        # substitute 在缺失变量时抛 KeyError，实现严格熔断
        return Template(raw_text).substitute(safe_context)
    except KeyError as exc:
        raise ValueError(f"提示词渲染失败：缺失必须的上下文变量 {exc}") from exc
```

> 文本中如需字面量 `$`，在模板里写 `$$`。字面量 `{`/`}` 不受影响。

### 3.5 核心工厂：`infrastructure/agent_factory/factory.py`

`AgentFactory` 只负责生产；`CortexAgent.run()` 只做单次推理。配置路径包内锚定，不依赖进程 CWD。

```python
# cortexverse/infrastructure/agent_factory/factory.py
"""通用 Agent 工厂 — 生产与推理职责分离。"""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from cortexverse.infrastructure.agent_factory.registry import SCHEMA_REGISTRY
from cortexverse.infrastructure.agent_factory.rendering import render_prompt
from cortexverse.infrastructure.llm_clients.client import get_instructor_client

_DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "agents.yaml"


class CortexAgent:
    """工厂产出的可执行体。run() 为单次纯推理，不含任何循环。"""

    def __init__(self, name: str, spec: dict[str, Any], response_model: Any):
        self.name = name
        self.spec = spec
        self.response_model = response_model
        self.client = get_instructor_client()

    async def run(self, template_name: str, **context: Any) -> Any:
        """执行单次结构化推理。

        Args:
            template_name: user_prompt_templates 中的键名。
            **context: 渲染 system 与 user prompt 的上下文变量。

        Returns:
            经 Pydantic 校验的结构化输出（Model 或 list[Model]）。
        """
        system_prompt = render_prompt(self.spec.get("system_instructions", []), context)
        templates = self.spec.get("user_prompt_templates", {})
        if template_name not in templates:
            raise KeyError(f"Template Error: Agent `{self.name}` 未定义模板 `{template_name}`")
        user_prompt = render_prompt(templates[template_name], context)

        model_settings = self.spec.get("model_settings", {})
        kwargs: dict[str, Any] = {"temperature": model_settings.get("temperature", 0.5)}
        # max_tokens 未配置时不传，避免部分 provider 对 None 报错
        if model_settings.get("max_tokens"):
            kwargs["max_tokens"] = model_settings["max_tokens"]

        logger.info("Agent [{}] 执行 template={}", self.name, template_name)

        # instructor 强类型请求；max_retries 仅兜底 JSON/schema 格式错误
        return await self.client.chat.completions.create(
            model=self.spec["model"],
            response_model=self.response_model,
            max_retries=self.spec.get("retries", 3),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )


class AgentFactory:
    """无状态生产线 — 仅装配 Agent，不参与推理。"""

    def __init__(self, configs: dict[str, Any]):
        self._configs = configs

    @classmethod
    def from_config(cls, config_path: str | Path | None = None) -> "AgentFactory":
        """加载 YAML 配置并执行启动期一致性断言。

        Args:
            config_path: 配置文件路径；默认使用包内锚定路径。

        Returns:
            就绪的 AgentFactory 实例。

        Raises:
            ValueError: 当 YAML 与注册表的 Key 集合不一致时。
        """
        path = Path(config_path) if config_path else _DEFAULT_CONFIG
        with open(path, "r", encoding="utf-8") as fp:
            configs: dict[str, Any] = yaml.safe_load(fp)

        # 单一事实源断言：YAML 与注册表必须严格对齐
        yaml_keys = set(configs.keys())
        registry_keys = set(SCHEMA_REGISTRY.keys())
        if yaml_keys != registry_keys:
            raise ValueError(
                "配置一致性校验失败："
                f"仅在 YAML：{yaml_keys - registry_keys}；"
                f"仅在注册表：{registry_keys - yaml_keys}"
            )
        return cls(configs)

    def create_agent(self, agent_key: str) -> CortexAgent:
        """根据配置与注册表生产 Agent 实例。

        Args:
            agent_key: Agent 名称，必须同时存在于配置与注册表。

        Returns:
            可执行的 CortexAgent 实例。

        Raises:
            ValueError: 配置中未找到该 Agent。
            KeyError: 注册表中未注册该 Agent 的输出模型。
        """
        spec = self._configs.get(agent_key)
        if not spec:
            raise ValueError(f"Agent Config Error: 未找到配置 `{agent_key}`")
        response_model = SCHEMA_REGISTRY.get(agent_key)
        if response_model is None:
            raise KeyError(f"Registry Error: 未注册实体 `{agent_key}`")
        return CortexAgent(name=agent_key, spec=spec, response_model=response_model)

    def reload(self, config_path: str | Path | None = None) -> None:
        """运行时重载配置（热更新 model/temperature/prompt）。"""
        self._configs = AgentFactory.from_config(config_path)._configs
```

---

## 四、 编排层调用规范 (Orchestrator Usage)

业务层通过工厂实例化 `CortexAgent` 后，以原生 `asyncio` 编排 DAG，并**在编排层驱动 refine 循环**：`run()` 始终单次推理，语义/关系级失败由编排层捕获后用 `refine_*` 模板重调。

```python
# workflows/world_gen.py
"""世界构建编排器 — 含关系校验驱动的 refine 循环。"""

from pydantic import ValidationError

from cortexverse.domain.world_asset import WorldAsset
from cortexverse.infrastructure.agent_factory.factory import AgentFactory

MAX_REFINE = 3


async def run_world_generation(genre_tags: list[str], creative_intent: str) -> WorldAsset:
    """执行世界构建流水线。

    Args:
        genre_tags: 题材标签列表。
        creative_intent: 创作意图。

    Returns:
        通过关系校验的世界观资产。
    """
    factory = AgentFactory.from_config()
    agent = factory.create_agent("world_builder")

    context: dict = {"genre_tags": genre_tags, "creative_intent": creative_intent}
    template = "generate_world"

    for _ in range(MAX_REFINE):
        candidate = await agent.run(template, **context)
        try:
            # WorldAsset 的 model_validator 在此触发企业级关系校验
            return WorldAsset.model_validate(candidate)
        except ValidationError as exc:
            # 关系级失败 instructor 修不了，交由编排层用 refine 模板重调
            context["feedback"] = str(exc)
            template = "refine_world"

    raise RuntimeError("世界构建在最大 refine 次数内仍未通过关系校验")
```

> **职责分层小结：**
> - `instructor max_retries`：单次 `run()` 内修复 JSON/schema 格式错误，对调用方透明。
> - 编排层 refine 循环：修复语义/关系级失败（如 `faction_id` 引用不存在）。

---

## 五、 新增 Agent 标准流程 (SOP)

新增任意阶段 Agent（如天气变异、叙事规划、剧本翻译）时，**无需改动 Factory**，仅四步：

1. **定义领域模型 (Domain)：** 在 `domain/` 下编写 `WeatherState(BaseModel)`。
2. **注册 Schema (Registry)：** 在装配模块中 `register_schema("weather_subagent")(WeatherState)`（产出列表则加 `many=True`）。
3. **配置资产 (Config)：** 在 `config/agents.yaml` 新增 `weather_subagent` 节点，撰写 System Prompt，预留 `${var}` 插值变量。
4. **业务编排 (Workflow)：** 在 `workflows/` 中 `factory.create_agent("weather_subagent")` 并按需驱动 refine 循环。

> 启动时若 YAML 与注册表 Key 不一致，`AgentFactory.from_config()` 会立即熔断，确保两侧同步。

---

## 六、 安全与持久化

- **Repository 模式：** `infrastructure/repositories/` 存放已持久化的世界资产；`CortexAgent` 运行结果应经 Repository 持久化。
- **渲染熔断：** `render_prompt` 缺失变量直接抛错，防止上下文丢失导致的 LLM 幻觉填充；`${}` 占位避免与文本字面量 `{}` 冲突。
- **配置热更新：** 调用 `AgentFactory.reload()` 即可刷新 model/temperature/prompt，无需重启；新增 Agent 仍需代码注册并重新部署。
- **多 provider 路由：** `model` 字段经 `litellm` 路由，业务层与底层供应商解耦。
```

