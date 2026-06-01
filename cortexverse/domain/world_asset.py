"""世界观资产聚合模型（WorldAsset）— 双层商业世界观资产终极聚合。"""

from pydantic import BaseModel, Field, model_validator

from cortexverse.domain.macro import MacroGrowthOverview, MacroHistory, MacroPhilosophy
from cortexverse.domain.micro import (
    MicroCharacter,
    MicroConflictNode,
    MicroFaction,
    MicroLocationNode,
    MicroPowerTier,
    MicroResource,
)


class WorldAsset(BaseModel):
    """CortexVerse 创世资产终极聚合模型。

    包含完整的宏观上下文控制台与微观原子关系型数据库。
    """

    world_id: str = Field(description="世界观全局唯一识别码")
    name: str = Field(description="世界观名称/项目代号")
    genre_tags: list[str] = Field(description="题材标签组合。例如：['赛博朋克', '社会派推理', '底层逆袭']")

    # 宏观控制台 (The Lore Context)
    macro_philosophy: MacroPhilosophy
    macro_history: MacroHistory
    macro_growth: MacroGrowthOverview

    # 微观关系型数据表 (The Micro Database)
    micro_factions: list[MicroFaction] = Field(default=[])
    micro_characters: list[MicroCharacter] = Field(default=[])
    micro_resources: list[MicroResource] = Field(default=[])
    micro_conflicts: list[MicroConflictNode] = Field(default=[])
    micro_hierarchy: list[MicroPowerTier] = Field(default=[], description="世界的阶层晋升精算大表")
    micro_locations: list[MicroLocationNode] = Field(default=[], description="物理世界地图节点大表")

    @model_validator(mode="after")
    def validate_relational_integrity(self) -> "WorldAsset":
        """企业级图关系断言：硬性校验微观层实体间的链接完整性，强行熔断大模型幻觉。"""
        # 提取所有合法的实体 ID 集合
        faction_ids = {f.faction_id for f in self.micro_factions}
        resource_ids = {r.resource_id for r in self.micro_resources}
        rank_levels = {p.rank for p in self.micro_hierarchy}

        # 校验冲突节点关系 (Faction A, Faction B, Resource)
        for conflict in self.micro_conflicts:
            if conflict.faction_a_id not in faction_ids:
                raise ValueError(
                    f"[关系校验失败] 冲突节点 '{conflict.conflict_id}' 中的 "
                    f"faction_a_id ({conflict.faction_a_id}) 在 micro_factions 中不存在。"
                )
            if conflict.faction_b_id not in faction_ids:
                raise ValueError(
                    f"[关系校验失败] 冲突节点 '{conflict.conflict_id}' 中的 "
                    f"faction_b_id ({conflict.faction_b_id}) 在 micro_factions 中不存在。"
                )
            if conflict.contested_resource_id not in resource_ids:
                raise ValueError(
                    f"[关系校验失败] 冲突节点 '{conflict.conflict_id}' 中的 "
                    f"contested_resource_id ({conflict.contested_resource_id}) 在 micro_resources 中不存在。"
                )

        # 校验角色组织归属与战力等级合法性
        for character in self.micro_characters:
            if character.affiliation_faction_id not in faction_ids:
                raise ValueError(
                    f"[关系校验失败] 角色 '{character.character_id}' 归属的势力 "
                    f"({character.affiliation_faction_id}) 在 micro_factions 中不存在。"
                )
            if rank_levels and character.current_tier_rank not in rank_levels:
                raise ValueError(
                    f"[关系校验失败] 角色 '{character.character_id}' 的初始 Rank "
                    f"({character.current_tier_rank}) 无法在 micro_hierarchy 阶层表中匹配。"
                )

        # 校验势力控制的资源合法性
        for faction in self.micro_factions:
            for res_id in faction.controlled_resource_ids:
                if res_id not in resource_ids:
                    raise ValueError(
                        f"[关系校验失败] 组织 '{faction.faction_id}' 声明控制的资源 "
                        f"({res_id}) 在 micro_resources 中不存在。"
                    )

        return self
