"""ORM 模型 — 领域模型的数据库持久化映射层。

采用"领域模型 + ORM 模型"双轨制：
- 领域模型（domain/）：纯 Pydantic，负责 LLM 输出解析与业务校验
- ORM 模型（本文件）：SQLAlchemy 2.0 Mapped，负责 PostgreSQL 持久化
- 双向转换：每个 Row 类提供 to_domain() / from_domain() 方法

宏观值对象采用 1:1 子表 + JSONB 冗余双存储：
- 子表用于结构化精确查询
- JSONB 列用于快速整体读取，避免 JOIN
"""

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from cortexverse.domain.world.macro import MacroGrowthOverview, MacroHistory, MacroPhilosophy
from cortexverse.domain.world.micro import (
    MicroCharacter,
    MicroConflictNode,
    MicroFaction,
    MicroLocationNode,
    MicroPowerTier,
    MicroResource,
)
from cortexverse.domain.world.world_asset import WorldAsset


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类。"""
    pass


# ====== 宏观 1:1 子表 ======


class MacroPhilosophyRow(Base):
    """MacroPhilosophy 的 ORM 映射 — 1:1 子表。"""

    __tablename__ = "macro_philosophy"

    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        primary_key=True,
        comment="所属世界观 ID，主键兼外键",
    )
    theme_statement: Mapped[str] = mapped_column(Text, comment="世界核心精神内核")
    narrative_tone: Mapped[str] = mapped_column(Text, comment="文本风格语调提示词")
    world_drive_force: Mapped[str] = mapped_column(Text, comment="世界自运转的终极欲望")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="macro_philosophy_rel")

    def to_domain(self) -> MacroPhilosophy:
        """ORM → 领域模型。"""
        return MacroPhilosophy(
            theme_statement=self.theme_statement,
            narrative_tone=self.narrative_tone,
            world_drive_force=self.world_drive_force,
        )

    @classmethod
    def from_domain(cls, domain: MacroPhilosophy, world_id: str) -> "MacroPhilosophyRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            theme_statement=domain.theme_statement,
            narrative_tone=domain.narrative_tone,
            world_drive_force=domain.world_drive_force,
        )


class MacroHistoryRow(Base):
    """MacroHistory 的 ORM 映射 — 1:1 子表。"""

    __tablename__ = "macro_history"

    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        primary_key=True,
        comment="所属世界观 ID，主键兼外键",
    )
    epoch_name: Mapped[str] = mapped_column(String(256), comment="当前时代宏观尊称")
    pre_history_legacy: Mapped[str] = mapped_column(Text, comment="前史对现在的一句话遗产")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="macro_history_rel")

    def to_domain(self) -> MacroHistory:
        """ORM → 领域模型。"""
        return MacroHistory(
            epoch_name=self.epoch_name,
            pre_history_legacy=self.pre_history_legacy,
        )

    @classmethod
    def from_domain(cls, domain: MacroHistory, world_id: str) -> "MacroHistoryRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            epoch_name=domain.epoch_name,
            pre_history_legacy=domain.pre_history_legacy,
        )


class MacroGrowthRow(Base):
    """MacroGrowthOverview 的 ORM 映射 — 1:1 子表。"""

    __tablename__ = "macro_growth"

    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        primary_key=True,
        comment="所属世界观 ID，主键兼外键",
    )
    ladder_philosophy: Mapped[str] = mapped_column(Text, comment="阶级晋升的宏观代价")
    desire_anchor: Mapped[str] = mapped_column(Text, comment="世界追逐的梦幻泡影")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="macro_growth_rel")

    def to_domain(self) -> MacroGrowthOverview:
        """ORM → 领域模型。"""
        return MacroGrowthOverview(
            ladder_philosophy=self.ladder_philosophy,
            desire_anchor=self.desire_anchor,
        )

    @classmethod
    def from_domain(cls, domain: MacroGrowthOverview, world_id: str) -> "MacroGrowthRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            ladder_philosophy=domain.ladder_philosophy,
            desire_anchor=domain.desire_anchor,
        )


# ====== 微观独立表 ======


class MicroFactionRow(Base):
    """MicroFaction 的 ORM 映射。"""

    __tablename__ = "micro_factions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        comment="所属世界观 ID",
    )
    faction_id: Mapped[str] = mapped_column(String(64), comment="业务唯一 ID")
    name: Mapped[str] = mapped_column(String(256), comment="组织名称")
    core_belief: Mapped[str] = mapped_column(Text, comment="终极行动纲领")
    controlled_resource_ids: Mapped[list] = mapped_column(
        JSONB, default=list, comment="控制的资源 ID 列表",
    )

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="factions")

    def to_domain(self) -> MicroFaction:
        """ORM → 领域模型。"""
        return MicroFaction(
            faction_id=self.faction_id,
            name=self.name,
            core_belief=self.core_belief,
            controlled_resource_ids=self.controlled_resource_ids or [],
        )

    @classmethod
    def from_domain(cls, domain: MicroFaction, world_id: str) -> "MicroFactionRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            faction_id=domain.faction_id,
            name=domain.name,
            core_belief=domain.core_belief,
            controlled_resource_ids=domain.controlled_resource_ids,
        )


class MicroCharacterRow(Base):
    """MicroCharacter 的 ORM 映射。"""

    __tablename__ = "micro_characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        comment="所属世界观 ID",
    )
    character_id: Mapped[str] = mapped_column(String(64), comment="业务唯一 ID")
    name: Mapped[str] = mapped_column(String(256), comment="角色姓名")
    affiliation_faction_id: Mapped[str] = mapped_column(String(64), comment="归属势力 ID")
    current_tier_rank: Mapped[int] = mapped_column(Integer, comment="初始阶层等级")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="characters")

    def to_domain(self) -> MicroCharacter:
        """ORM → 领域模型。"""
        return MicroCharacter(
            character_id=self.character_id,
            name=self.name,
            affiliation_faction_id=self.affiliation_faction_id,
            current_tier_rank=self.current_tier_rank,
        )

    @classmethod
    def from_domain(cls, domain: MicroCharacter, world_id: str) -> "MicroCharacterRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            character_id=domain.character_id,
            name=domain.name,
            affiliation_faction_id=domain.affiliation_faction_id,
            current_tier_rank=domain.current_tier_rank,
        )


class MicroResourceRow(Base):
    """MicroResource 的 ORM 映射。"""

    __tablename__ = "micro_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        comment="所属世界观 ID",
    )
    resource_id: Mapped[str] = mapped_column(String(64), comment="业务唯一 ID")
    name: Mapped[str] = mapped_column(String(256), comment="资源名称")
    scarcity_scale: Mapped[int] = mapped_column(Integer, comment="稀缺指数 (1-10)")
    monopolizer_faction_id: Mapped[str] = mapped_column(String(64), comment="垄断组织 ID")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="resources")

    def to_domain(self) -> MicroResource:
        """ORM → 领域模型。"""
        return MicroResource(
            resource_id=self.resource_id,
            name=self.name,
            scarcity_scale=self.scarcity_scale,
            monopolizer_faction_id=self.monopolizer_faction_id,
        )

    @classmethod
    def from_domain(cls, domain: MicroResource, world_id: str) -> "MicroResourceRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            resource_id=domain.resource_id,
            name=domain.name,
            scarcity_scale=domain.scarcity_scale,
            monopolizer_faction_id=domain.monopolizer_faction_id,
        )


class MicroConflictRow(Base):
    """MicroConflictNode 的 ORM 映射。"""

    __tablename__ = "micro_conflicts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        comment="所属世界观 ID",
    )
    conflict_id: Mapped[str] = mapped_column(String(64), comment="业务唯一 ID")
    faction_a_id: Mapped[str] = mapped_column(String(64), comment="势力 A ID")
    faction_b_id: Mapped[str] = mapped_column(String(64), comment="势力 B ID")
    contested_resource_id: Mapped[str] = mapped_column(String(64), comment="争夺的资源 ID")
    climax_trigger: Mapped[str] = mapped_column(Text, comment="爆发导火索事件")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="conflicts")

    def to_domain(self) -> MicroConflictNode:
        """ORM → 领域模型。"""
        return MicroConflictNode(
            conflict_id=self.conflict_id,
            faction_a_id=self.faction_a_id,
            faction_b_id=self.faction_b_id,
            contested_resource_id=self.contested_resource_id,
            climax_trigger=self.climax_trigger,
        )

    @classmethod
    def from_domain(cls, domain: MicroConflictNode, world_id: str) -> "MicroConflictRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            conflict_id=domain.conflict_id,
            faction_a_id=domain.faction_a_id,
            faction_b_id=domain.faction_b_id,
            contested_resource_id=domain.contested_resource_id,
            climax_trigger=domain.climax_trigger,
        )


class MicroPowerTierRow(Base):
    """MicroPowerTier 的 ORM 映射 — 复合主键 (world_id, rank)。"""

    __tablename__ = "micro_power_tiers"

    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        primary_key=True,
        comment="所属世界观 ID，复合主键",
    )
    rank: Mapped[int] = mapped_column(Integer, primary_key=True, comment="阶层等级，复合主键")
    title: Mapped[str] = mapped_column(String(256), comment="阶层尊称")
    hard_cost: Mapped[str] = mapped_column(Text, comment="晋升硬性代价")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="power_tiers")

    def to_domain(self) -> MicroPowerTier:
        """ORM → 领域模型。"""
        return MicroPowerTier(
            rank=self.rank,
            title=self.title,
            hard_cost=self.hard_cost,
        )

    @classmethod
    def from_domain(cls, domain: MicroPowerTier, world_id: str) -> "MicroPowerTierRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            rank=domain.rank,
            title=domain.title,
            hard_cost=domain.hard_cost,
        )


class MicroLocationRow(Base):
    """MicroLocationNode 的 ORM 映射。"""

    __tablename__ = "micro_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    world_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("world_assets.world_id", ondelete="CASCADE"),
        comment="所属世界观 ID",
    )
    location_id: Mapped[str] = mapped_column(String(64), comment="业务唯一 ID")
    name: Mapped[str] = mapped_column(String(256), comment="区域名称")
    danger_coefficient: Mapped[float] = mapped_column(Float, comment="危险系数 (0.0-1.0)")
    visual_sd_prompt: Mapped[str] = mapped_column(Text, comment="视觉 Tag")

    # 反向关系
    world: Mapped["WorldAssetRow"] = relationship(back_populates="locations")

    def to_domain(self) -> MicroLocationNode:
        """ORM → 领域模型。"""
        return MicroLocationNode(
            location_id=self.location_id,
            name=self.name,
            danger_coefficient=self.danger_coefficient,
            visual_sd_prompt=self.visual_sd_prompt,
        )

    @classmethod
    def from_domain(cls, domain: MicroLocationNode, world_id: str) -> "MicroLocationRow":
        """领域模型 → ORM。"""
        return cls(
            world_id=world_id,
            location_id=domain.location_id,
            name=domain.name,
            danger_coefficient=domain.danger_coefficient,
            visual_sd_prompt=domain.visual_sd_prompt,
        )


# ====== 聚合根 ======


class WorldAssetRow(Base):
    """WorldAsset 聚合根的 ORM 映射。

    包含宏观 JSONB 冗余列（快读）+ 1:1 子表关系（结构化查询）+ 微观实体关系。
    """

    __tablename__ = "world_assets"

    world_id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="世界观全局唯一 ID")
    name: Mapped[str] = mapped_column(String(256), comment="世界观名称")
    genre_tags: Mapped[list] = mapped_column(JSONB, default=list, comment="题材标签数组")

    # 宏观 JSONB 冗余列 — 用于快速整体读取，避免 JOIN
    macro_philosophy: Mapped[dict] = mapped_column(JSONB, comment="MacroPhilosophy JSON 冗余")
    macro_history: Mapped[dict] = mapped_column(JSONB, comment="MacroHistory JSON 冗余")
    macro_growth: Mapped[dict] = mapped_column(JSONB, comment="MacroGrowthOverview JSON 冗余")

    # 宏观 1:1 子表关系
    macro_philosophy_rel: Mapped["MacroPhilosophyRow"] = relationship(
        back_populates="world", cascade="all, delete-orphan", uselist=False,
    )
    macro_history_rel: Mapped["MacroHistoryRow"] = relationship(
        back_populates="world", cascade="all, delete-orphan", uselist=False,
    )
    macro_growth_rel: Mapped["MacroGrowthRow"] = relationship(
        back_populates="world", cascade="all, delete-orphan", uselist=False,
    )

    # 微观实体关系
    factions: Mapped[list["MicroFactionRow"]] = relationship(
        back_populates="world", cascade="all, delete-orphan",
    )
    characters: Mapped[list["MicroCharacterRow"]] = relationship(
        back_populates="world", cascade="all, delete-orphan",
    )
    resources: Mapped[list["MicroResourceRow"]] = relationship(
        back_populates="world", cascade="all, delete-orphan",
    )
    conflicts: Mapped[list["MicroConflictRow"]] = relationship(
        back_populates="world", cascade="all, delete-orphan",
    )
    power_tiers: Mapped[list["MicroPowerTierRow"]] = relationship(
        back_populates="world", cascade="all, delete-orphan",
    )
    locations: Mapped[list["MicroLocationRow"]] = relationship(
        back_populates="world", cascade="all, delete-orphan",
    )

    def to_domain(self) -> WorldAsset:
        """聚合根 ORM → 领域模型。

        优先使用 1:1 子表数据（结构化），JSONB 列作为兜底。
        """
        # 宏观：优先从子表加载，若子表为空则从 JSONB 列解析
        if self.macro_philosophy_rel:
            philosophy = self.macro_philosophy_rel.to_domain()
        else:
            philosophy = MacroPhilosophy(**self.macro_philosophy)

        if self.macro_history_rel:
            history = self.macro_history_rel.to_domain()
        else:
            history = MacroHistory(**self.macro_history)

        if self.macro_growth_rel:
            growth = self.macro_growth_rel.to_domain()
        else:
            growth = MacroGrowthOverview(**self.macro_growth)

        return WorldAsset(
            world_id=self.world_id,
            name=self.name,
            genre_tags=self.genre_tags or [],
            macro_philosophy=philosophy,
            macro_history=history,
            macro_growth=growth,
            micro_factions=[f.to_domain() for f in self.factions],
            micro_characters=[c.to_domain() for c in self.characters],
            micro_resources=[r.to_domain() for r in self.resources],
            micro_conflicts=[c.to_domain() for c in self.conflicts],
            micro_hierarchy=[t.to_domain() for t in self.power_tiers],
            micro_locations=[l.to_domain() for l in self.locations],
        )

    @classmethod
    def from_domain(cls, domain: WorldAsset) -> "WorldAssetRow":
        """领域模型 → 聚合根 ORM。

        同时写入 JSONB 冗余列和 1:1 子表。
        """
        world_id = domain.world_id
        return cls(
            world_id=world_id,
            name=domain.name,
            genre_tags=domain.genre_tags,
            # JSONB 冗余列
            macro_philosophy=domain.macro_philosophy.model_dump(),
            macro_history=domain.macro_history.model_dump(),
            macro_growth=domain.macro_growth.model_dump(),
            # 1:1 子表
            macro_philosophy_rel=MacroPhilosophyRow.from_domain(domain.macro_philosophy, world_id),
            macro_history_rel=MacroHistoryRow.from_domain(domain.macro_history, world_id),
            macro_growth_rel=MacroGrowthRow.from_domain(domain.macro_growth, world_id),
            # 微观实体
            factions=[MicroFactionRow.from_domain(f, world_id) for f in domain.micro_factions],
            characters=[MicroCharacterRow.from_domain(c, world_id) for c in domain.micro_characters],
            resources=[MicroResourceRow.from_domain(r, world_id) for r in domain.micro_resources],
            conflicts=[MicroConflictRow.from_domain(c, world_id) for c in domain.micro_conflicts],
            power_tiers=[MicroPowerTierRow.from_domain(t, world_id) for t in domain.micro_hierarchy],
            locations=[MicroLocationRow.from_domain(l, world_id) for l in domain.micro_locations],
        )
