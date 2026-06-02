"""通用 Agent 工厂 — 生产与推理职责分离。"""

from pathlib import Path
from typing import Any

import instructor
import yaml
from loguru import logger

from cortexverse.infrastructure.agent_factory.registry import SCHEMA_REGISTRY
from cortexverse.infrastructure.agent_factory.rendering import render_prompt
from cortexverse.infrastructure.llm_clients.factory import LLMClientFactory

_DEFAULT_CONFIG = Path(__file__).resolve().parents[3] / "config" / "agents.yaml"
_DEFAULT_PROVIDERS_PATH = Path(__file__).resolve().parents[3] / "config" / "llm_providers.yaml"


class CortexAgent:
    """工厂产出的可执行体。run() 为单次纯推理，不含任何循环。"""

    def __init__(
        self,
        name: str,
        spec: dict[str, Any],
        response_model: Any,
        client: instructor.AsyncInstructor,
    ) -> None:
        self.name = name
        self.spec = spec
        self.response_model = response_model
        self.client = client

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
        # 提取 provider 特有参数（reasoning_effort 等）
        if model_settings.get("reasoning_effort"):
            kwargs["reasoning_effort"] = model_settings["reasoning_effort"]
        if model_settings.get("extra_body"):
            kwargs["extra_body"] = model_settings["extra_body"]

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

    def __init__(self, configs: dict[str, Any], client_factory: LLMClientFactory) -> None:
        self._configs = configs
        self._client_factory = client_factory

    @classmethod
    def from_config(
        cls,
        config_path: str | Path | None = None,
        providers_path: str | Path | None = None,
    ) -> "AgentFactory":
        """加载 YAML 配置并执行启动期一致性断言。

        Args:
            config_path: Agent 配置文件路径；默认使用包内锚定路径。
            providers_path: Provider 配置文件路径；默认使用包内锚定路径。

        Returns:
            就绪的 AgentFactory 实例。

        Raises:
            ValueError: 当 YAML 与注册表的 Key 集合不一致时。
        """
        # 确保 Schema 注册表在一致性断言前完成加载
        import cortexverse.agents._schema_bindings  # noqa: F401

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

        providers_config_path = Path(providers_path) if providers_path else _DEFAULT_PROVIDERS_PATH
        client_factory = LLMClientFactory.from_config(providers_config_path)
        return cls(configs, client_factory)

    def create_agent(self, agent_key: str) -> CortexAgent:
        """根据配置与注册表生产 Agent 实例。

        Args:
            agent_key: Agent 名称，必须同时存在于配置与注册表。

        Returns:
            可执行的 CortexAgent 实例。

        Raises:
            ValueError: 配置中未找到该 Agent 或缺少 provider 字段。
            KeyError: 注册表中未注册该 Agent 的输出模型。
        """
        spec = self._configs.get(agent_key)
        if not spec:
            raise ValueError(f"Agent Config Error: 未找到配置 `{agent_key}`")
        response_model = SCHEMA_REGISTRY.get(agent_key)
        if response_model is None:
            raise KeyError(f"Registry Error: 未注册实体 `{agent_key}`")

        # 从 spec 中读取 provider，创建对应客户端
        provider_name = spec.get("provider")
        if not provider_name:
            raise ValueError(f"Agent 配置错误：`{agent_key}` 缺少 `provider` 字段")
        client = self._client_factory.get_client(provider_name)

        return CortexAgent(name=agent_key, spec=spec, response_model=response_model, client=client)

    def reload(
        self,
        config_path: str | Path | None = None,
        providers_path: str | Path | None = None,
    ) -> None:
        """运行时重载配置（热更新 model/temperature/prompt）。"""
        new_factory = AgentFactory.from_config(config_path, providers_path)
        self._configs = new_factory._configs
        self._client_factory = new_factory._client_factory
