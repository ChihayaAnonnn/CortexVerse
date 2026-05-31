"""剧集生成主循环（Game Loop）。

编排各 Agent 节点，驱动单集内容从世界观构建到脚本输出的完整流程。
"""

from dataclasses import dataclass
from enum import Enum

from loguru import logger


class EpisodePhase(str, Enum):
    """剧集生成阶段。"""

    WORLD_BUILD = "world_build"
    CHARACTER_UPDATE = "character_update"
    NARRATIVE_PLAN = "narrative_plan"
    SCRIPT_TRANSLATE = "script_translate"
    MEDIA_RENDER = "media_render"
    COMPLETE = "complete"


@dataclass
class EpisodeState:
    """单集生成状态。"""

    episode_id: str
    phase: EpisodePhase = EpisodePhase.WORLD_BUILD
    world_state: dict | None = None
    characters: list[dict] | None = None
    narrative: dict | None = None
    script: dict | None = None
    media_assets: list[dict] | None = None


async def run_episode_loop(episode_id: str) -> EpisodeState:
    """执行单集生成的完整 Game Loop。

    按阶段依次调用各 Agent 节点：
    1. 世界观构建（World Builder）
    2. 角色状态更新（Character Engine）
    3. 叙事规划（Narrative Planner）
    4. 脚本翻译（Script Translator）
    5. 媒体渲染（Media Adapter）

    Args:
        episode_id: 剧集唯一标识。

    Returns:
        包含完整生成结果的 EpisodeState。
    """
    state = EpisodeState(episode_id=episode_id)

    logger.info("开始剧集生成 episode_id={}", episode_id)

    while state.phase != EpisodePhase.COMPLETE:
        logger.info("进入阶段 phase={}", state.phase.value)

        match state.phase:
            case EpisodePhase.WORLD_BUILD:
                # TODO: 调用 world_builder agent
                state.phase = EpisodePhase.CHARACTER_UPDATE
            case EpisodePhase.CHARACTER_UPDATE:
                # TODO: 调用 character_engine agent
                state.phase = EpisodePhase.NARRATIVE_PLAN
            case EpisodePhase.NARRATIVE_PLAN:
                # TODO: 调用 narrative_planner agent
                state.phase = EpisodePhase.SCRIPT_TRANSLATE
            case EpisodePhase.SCRIPT_TRANSLATE:
                # TODO: 调用 script_translator agent
                state.phase = EpisodePhase.MEDIA_RENDER
            case EpisodePhase.MEDIA_RENDER:
                # TODO: 调用 infrastructure/media_adapters
                state.phase = EpisodePhase.COMPLETE

    logger.info("剧集生成完成 episode_id={}", episode_id)
    return state
