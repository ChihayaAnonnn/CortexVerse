"""世界构建 Agent（World Builder）— L1 层。

负责根据题材标签和创作意图，通过 LLM 生成完整的 WorldAsset。
"""

import instructor
import litellm
from loguru import logger
from pydantic import BaseModel, Field

from cortexverse.domain.world_asset import WorldAsset


class WorldBuilderInput(BaseModel):
    """世界构建 Agent 输入。"""

    genre_tags: list[str] = Field(description="题材标签组合。例如：['赛博朋克', '废土末日']")
    creative_intent: str = Field(description="创作意图描述。例如：'一个资源匮乏的末世，人类为净水而战'")
    num_factions: int = Field(default=3, ge=2, le=6, description="生成的组织/派系数量")
    num_characters: int = Field(default=3, ge=1, le=8, description="生成的核心角色数量")
    num_resources: int = Field(default=3, ge=2, le=6, description="生成的稀缺资源数量")
    num_locations: int = Field(default=4, ge=2, le=8, description="生成的物理区域节点数量")


async def run_world_builder(input_data: WorldBuilderInput) -> WorldAsset:
    """执行世界构建，生成完整的 WorldAsset。

    通过 instructor 调用 LLM，强制输出符合 WorldAsset schema 的结构化 JSON，
    并通过 Pydantic 的关系校验确保实体间引用完整性。

    Args:
        input_data: 世界构建输入参数。

    Returns:
        经过关系校验的 WorldAsset 实例。
    """
    logger.info("开始世界构建 genre_tags={}", input_data.genre_tags)

    # 构造 LLM prompt
    prompt = _build_prompt(input_data)

    # 使用 instructor 调用 LLM，强制输出 WorldAsset schema
    client = instructor.from_litellm(litellm.acompletion)

    world_asset = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=WorldAsset,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个专业世界观架构师。根据用户的题材标签和创作意图，"
                    "生成完整、自洽、可商业化的世界观资产。"
                    "所有实体 ID 必须遵循命名规范，所有关系引用必须完整且合法。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_retries=3,
    )

    logger.info(
        "世界构建完成 world_id={} factions={} characters={} resources={}",
        world_asset.world_id,
        len(world_asset.micro_factions),
        len(world_asset.micro_characters),
        len(world_asset.micro_resources),
    )

    return world_asset


def _build_prompt(input_data: WorldBuilderInput) -> str:
    """构造 LLM 提示词。"""
    return f"""请根据以下要求生成一个完整的世界观资产：

## 题材标签
{', '.join(input_data.genre_tags)}

## 创作意图
{input_data.creative_intent}

## 数量要求
- 组织/派系：{input_data.num_factions} 个
- 核心角色：{input_data.num_characters} 个
- 稀缺资源：{input_data.num_resources} 个
- 物理区域：{input_data.num_locations} 个

## 要求
1. 宏观层：构建有深度的哲学内核、前史厚度和成长哲学
2. 微观层：生成具有强关联性的实体，确保所有 ID 引用合法
3. 冲突设计：至少包含 {input_data.num_factions - 1} 个冲突节点，围绕稀缺资源展开
4. 视觉提示词：所有 location 的 visual_sd_prompt 必须是可直接用于 ComfyUI 的英文 tag
"""
