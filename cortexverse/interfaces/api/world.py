"""世界构建 API 路由。"""

import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

from cortexverse.interfaces.api.schemas import WorldGenerateRequest, WorldGenerateResponse
from cortexverse.workflows.world_gen import run_world_generation

router = APIRouter()


@router.post("/generate", response_model=WorldGenerateResponse)
async def generate_world(request: WorldGenerateRequest) -> WorldGenerateResponse:
    """触发世界构建流水线（同步版本）。

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


def _sse_event(event: str, data: dict) -> str:
    """格式化 SSE 事件。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/generate/stream")
async def generate_world_stream(request: WorldGenerateRequest):
    """触发世界构建流水线（SSE 流式版本）。

    事件类型：
    - phase_start: 阶段开始 {phase, step}
    - phase_complete: 阶段完成 {phase, step, result}
    - world_complete: 全部完成 {world_asset}
    - world_failed: 构建失败 {error}
    """
    world_id = f"world_{uuid.uuid4().hex[:8]}"

    async def event_generator():
        # 用于收集进度事件
        events: list[str] = []

        def on_progress(phase: str, step: int, result: BaseModel | None):
            if result is None:
                # 阶段开始
                events.append(_sse_event("phase_start", {"phase": phase, "step": step}))
            else:
                # 阶段完成
                events.append(_sse_event("phase_complete", {
                    "phase": phase,
                    "step": step,
                    "result": result.model_dump(),
                }))

        try:
            # 发送初始事件
            yield _sse_event("start", {"world_id": world_id, "world_name": request.world_name})

            # 执行构建（通过回调收集事件）
            # 由于回调是同步的，我们需要用列表收集然后在异步生成器中逐个 yield
            # 这里改用另一种方式：直接在生成器中执行

            from cortexverse.agents import _schema_bindings  # noqa: F401
            from cortexverse.domain.world.macro import MacroState
            from cortexverse.domain.world.micro import ConflictState, EconomyState, GeographyState
            from cortexverse.domain.world.world_asset import WorldAsset
            from cortexverse.agents.factory.factory import AgentFactory
            from cortexverse.workflows.world_gen import MAX_REFINE, _run_with_refine, _validate_conflict_refs

            factory = AgentFactory.from_config()

            # 阶段 1
            yield _sse_event("phase_start", {"phase": "macro_architect", "step": 1})
            macro_state: MacroState = await _run_with_refine(
                "macro_architect", "generate",
                {"world_name": request.world_name, "theme_input": request.theme_input,
                 "genre_tags": ", ".join(request.genre_tags)},
                factory,
            )
            yield _sse_event("phase_complete", {
                "phase": "macro_architect", "step": 1,
                "result": macro_state.model_dump(),
            })

            # 阶段 2
            yield _sse_event("phase_start", {"phase": "geography_subagent", "step": 2})
            geography_state: GeographyState = await _run_with_refine(
                "geography_subagent", "generate",
                {"macro_context": macro_state.model_dump_json()},
                factory,
            )
            yield _sse_event("phase_complete", {
                "phase": "geography_subagent", "step": 2,
                "result": geography_state.model_dump(),
            })

            # 阶段 3
            yield _sse_event("phase_start", {"phase": "economy_subagent", "step": 3})
            economy_state: EconomyState = await _run_with_refine(
                "economy_subagent", "generate",
                {
                    "macro_context": macro_state.model_dump_json(),
                    "geography_context": geography_state.model_dump_json(),
                },
                factory,
            )
            yield _sse_event("phase_complete", {
                "phase": "economy_subagent", "step": 3,
                "result": economy_state.model_dump(),
            })

            # 阶段 4
            yield _sse_event("phase_start", {"phase": "conflict_subagent", "step": 4})

            def conflict_validator(state: ConflictState) -> list[str]:
                return _validate_conflict_refs(state, economy_state)

            conflict_state: ConflictState = await _run_with_refine(
                "conflict_subagent", "generate",
                {
                    "macro_context": macro_state.model_dump_json(),
                    "geography_context": geography_state.model_dump_json(),
                    "economy_context": economy_state.model_dump_json(),
                },
                factory,
                validator=conflict_validator,
            )
            yield _sse_event("phase_complete", {
                "phase": "conflict_subagent", "step": 4,
                "result": conflict_state.model_dump(),
            })

            # 组装 WorldAsset
            world_asset = WorldAsset(
                world_id=world_id,
                name=request.world_name,
                genre_tags=request.genre_tags,
                macro_philosophy=macro_state.macro_philosophy,
                macro_history=macro_state.macro_history,
                macro_growth=macro_state.macro_growth,
                micro_locations=geography_state.micro_locations,
                micro_hierarchy=economy_state.micro_hierarchy,
                micro_resources=economy_state.micro_resources,
                micro_factions=economy_state.micro_factions,
                micro_characters=economy_state.micro_characters,
                micro_conflicts=conflict_state.micro_conflicts,
            )

            yield _sse_event("world_complete", {"world_asset": world_asset.model_dump()})

        except Exception as exc:
            logger.error("世界构建失败 world_id={} error={}", world_id, str(exc))
            yield _sse_event("world_failed", {"error": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
