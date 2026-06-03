"""Agent 元数据模型 — 定义 Agent 的身份、能力画像与执行配置。"""

from typing import Any

from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    """Agent 的完整元数据，用于 Coordinator 调度和 Worker 执行。

    包含基础身份、调度认知、运行控制、输出约束和扩展槽五大模块。
    """

    # ==========================================
    # 1. 基础身份信息（系统底座）
    # ==========================================
    agent_id: str = Field(
        ...,
        description="Agent 的唯一字符串标识，作为主键或索引。例如: 'psychology_expert'",
    )
    name: str = Field(
        ...,
        description="Agent 的人类可读名称，用于日志、前端展示以及 Coordinator 的 Prompt 注入。例如: '心理学人设专家'",
    )
    version: str = Field(
        default="1.0.0",
        description="Prompt 或配置的版本号，便于迭代和 A/B 测试",
    )

    # ==========================================
    # 2. 调度与认知信息（给 Coordinator 看的"简历"）
    # ==========================================
    description: str = Field(
        ...,
        description=(
            "极其重要！Agent 的能力画像描述。Coordinator 将依靠这段描述来判断是否雇佣该 Agent。"
            "例如: '擅长挖掘角色的深层动机、内在矛盾、阴暗面以及童年阴影，能让人物立柱。'"
        ),
    )
    applicable_stages: list[str] = Field(
        ...,
        description="该 Agent 适用的工作流阶段。例如: ['Stage_2_CharacterDesign']。过滤无关 Agent，防止召回噪音。",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="标签分类，如 ['creative', 'dialogue', 'scifi']，便于在人才库庞大时进行快速检索",
    )

    # ==========================================
    # 3. 运行控制与 LLM 配置（物理执行层）
    # ==========================================
    model_name: str = Field(
        default="gpt-4o",
        description="该 Agent 绑定的模型底座。长文本润色可用 Claude 3.5, 结构化输出可用 GPT-4o",
    )
    temperature: float = Field(
        default=0.7,
        description="生成温度，控制输出的随机性。创意任务可调高，结构化任务应调低",
    )
    max_tokens: int | None = Field(
        default=None,
        description="最大输出 token 数，未配置时由模型默认值决定",
    )

    # ==========================================
    # 4. 输出约束（数据契约）
    # ==========================================
    output_schema_name: str | None = Field(
        default=None,
        description="该 Agent 强制输出的 Pydantic Schema 名称。用于动态加载验证器，确保 Worker 返回的数据 100% 符合预期结构。",
    )

    # ==========================================
    # 5. 业务与财务统计（扩展槽）
    # ==========================================
    metadata_ext: dict[str, Any] = Field(
        default_factory=dict,
        description="留出的扩展槽，可以存放该 Agent 的 Token 消耗配额、预计耗时、作者信息等",
    )
