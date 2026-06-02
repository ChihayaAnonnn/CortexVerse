"""API 路由模块。"""

from fastapi import APIRouter

from cortexverse.interfaces.api.world import router as world_router

router = APIRouter()

router.include_router(world_router, prefix="/world", tags=["world"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查端点。"""
    return {"status": "ok"}
