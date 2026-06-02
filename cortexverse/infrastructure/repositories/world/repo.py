"""WorldAsset 仓储 — 聚合根的持久化与查询。"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cortexverse.domain.world.world_asset import WorldAsset
from cortexverse.infrastructure.repositories.world.models import WorldAssetRow


class WorldAssetRepository:
    """WorldAsset 聚合根仓储。

    封装 WorldAsset 的 CRUD 操作，内部处理 ORM ↔ 领域模型的转换。
    采用"删除-重建"策略处理 upsert，保证聚合内部一致性。
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, world: WorldAsset) -> None:
        """持久化整个聚合（Upsert）。

        若 world_id 已存在则先删除旧数据（级联删除子表），再写入新数据。
        宏观数据同时写入 1:1 子表和 JSONB 冗余列。

        Args:
            world: 领域模型实例。
        """
        # 检查是否已存在，存在则先删除
        existing = await self._session.get(WorldAssetRow, world.world_id)
        if existing:
            await self._session.delete(existing)
            await self._session.flush()
            logger.debug("已删除旧聚合 world_id={}", world.world_id)

        row = WorldAssetRow.from_domain(world)
        self._session.add(row)
        await self._session.commit()
        logger.info("聚合持久化完成 world_id={}", world.world_id)

    async def get_by_id(self, world_id: str) -> WorldAsset | None:
        """按 ID 加载聚合并转为领域模型。

        使用 selectinload 预加载所有子关系，避免 N+1 查询。
        宏观数据优先从 1:1 子表加载。

        Args:
            world_id: 世界观全局唯一 ID。

        Returns:
            领域模型实例，不存在则返回 None。
        """
        stmt = (
            select(WorldAssetRow)
            .where(WorldAssetRow.world_id == world_id)
            .options(
                selectinload(WorldAssetRow.macro_philosophy_rel),
                selectinload(WorldAssetRow.macro_history_rel),
                selectinload(WorldAssetRow.macro_growth_rel),
                selectinload(WorldAssetRow.factions),
                selectinload(WorldAssetRow.characters),
                selectinload(WorldAssetRow.resources),
                selectinload(WorldAssetRow.conflicts),
                selectinload(WorldAssetRow.power_tiers),
                selectinload(WorldAssetRow.locations),
            )
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            return None

        return row.to_domain()

    async def list_all(self) -> list[WorldAsset]:
        """列出所有聚合并转为领域模型列表。

        Returns:
            所有 WorldAsset 领域模型列表。
        """
        stmt = select(WorldAssetRow).options(
            selectinload(WorldAssetRow.macro_philosophy_rel),
            selectinload(WorldAssetRow.macro_history_rel),
            selectinload(WorldAssetRow.macro_growth_rel),
            selectinload(WorldAssetRow.factions),
            selectinload(WorldAssetRow.characters),
            selectinload(WorldAssetRow.resources),
            selectinload(WorldAssetRow.conflicts),
            selectinload(WorldAssetRow.power_tiers),
            selectinload(WorldAssetRow.locations),
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        return [row.to_domain() for row in rows]

    async def delete(self, world_id: str) -> bool:
        """级联删除整个聚合。

        通过 ORM cascade 自动清理所有子表数据。

        Args:
            world_id: 世界观全局唯一 ID。

        Returns:
            是否成功删除（False 表示不存在）。
        """
        row = await self._session.get(WorldAssetRow, world_id)
        if row is None:
            return False

        await self._session.delete(row)
        await self._session.commit()
        logger.info("聚合已删除 world_id={}", world_id)
        return True
