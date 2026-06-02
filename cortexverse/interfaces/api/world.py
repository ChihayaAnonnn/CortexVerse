"""世界构建 API 路由。"""

import uuid

from fastapi import APIRouter
from loguru import logger

from cortexverse.interfaces.api.schemas import WorldGenerateRequest, WorldGenerateResponse
from cortexverse.workflows.world_gen import run_world_generation

router = APIRouter()


@router.post("/generate", response_model=WorldGenerateResponse)
async def generate_world(request: WorldGenerateRequest) -> WorldGenerateResponse:
    """触发世界构建流水线。

    四阶段：宏观架构 → 地理精算 → 经济社会 → 冲突编排。
    """
    world_id = f"world_{uuid.uuid4().hex[:8]}"
    logger.info("收到世界构建请求 world_id={} world_name={}", world_id, request.world_name)

    try:
        world_asset = await run_world_generation(
            world_name=request.world_name,
            genre_tags=request.genre_tags,
            theme_input=request.theme_input,
        )
        return WorldGenerateResponse(
            world_id=world_asset.world_id,
            status="completed",
            world_asset=world_asset,
        )
    except Exception as exc:
        logger.error("世界构建失败 world_id={} error={}", world_id, str(exc))
        return WorldGenerateResponse(
            world_id=world_id,
            status="failed",
            error=str(exc),
        )
