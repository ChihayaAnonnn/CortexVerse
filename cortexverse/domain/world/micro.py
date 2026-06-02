"""微观原子数据层（MICRO）— 为下游状态机和多模态引擎提供可计算的硬指标。"""

from pydantic import BaseModel, Field, model_validator


class MicroFaction(BaseModel):
    """微观组织/派系实体。世界政治版图的割据力量。"""

    faction_id: str = Field(description="组织唯一标识符，格式规范如：'fac_neon_corp'")
    name: str = Field(description="组织的完整名称，例如：'霓虹科技集团'。")
    core_belief: str = Field(description="该组织的终极行动纲领或利益诉求，指导其对冲突事件的决策响应。")
    controlled_resource_ids: list[str] = Field(
        default=[],
        description="该组织当前垄断或实质性控制的资源 ID 列表。元素必须能在 micro_resources 中找到。",
    )


class MicroCharacter(BaseModel):
    """微观核心初始角色。作为引子或世界观具象载体。"""

    character_id: str = Field(description="角色唯一标识符，格式规范如：'char_protagonist_01'")
    name: str = Field(description="角色姓名。")
    affiliation_faction_id: str = Field(description="角色初始归属势力的 ID。必须对应一个合法的 faction_id。")
    current_tier_rank: int = Field(
        description="角色初始在世界力量/阶级系统中所处的绝对数值层级。对应 MicroPowerTier 中的 rank。"
    )


class MicroResource(BaseModel):
    """微观经济原子资产。引发剧情冲突的核心资源。"""

    resource_id: str = Field(description="资源唯一标识符，格式规范如：'res_pure_water'")
    name: str = Field(description="资源名称，如 '高纯度基因抑制剂'、'太乙精铁'。")
    scarcity_scale: int = Field(
        ge=1,
        le=10,
        description="资源稀缺指数（1-10）。数值在 8 以上的稀缺资源在状态机推演中极易催生背叛、血腥冲突事件。",
    )
    monopolizer_faction_id: str = Field(
        description="当前垄断该资源的组织 ID。若无组织垄断，填 'public'。"
    )


class MicroConflictNode(BaseModel):
    """微观冲突焦点。状态机提取剧情、编排爽点事件的直接原料。"""

    conflict_id: str = Field(description="冲突唯一标识符，格式规范如：'conf_black_market_war'")
    faction_a_id: str = Field(description="发起冲突或利益受损的势力 A 的 ID。")
    faction_b_id: str = Field(description="被对抗或利益既得的势力 B 的 ID。")
    contested_resource_id: str = Field(description="双方进行核心争夺的微观资源 ID。")
    climax_trigger: str = Field(
        description="触发这次大冲突爆发的具象导火索事件。例如：'三年一度的地下黑市拍卖会遭遇突袭'。"
    )


class MicroPowerTier(BaseModel):
    """微观战力与社会阶层精算表。控制爽点、变现节奏与升级惩罚。"""

    rank: int = Field(description="社会或战力的绝对数值层级。1 为最底层，数值越高特权越大。")
    title: str = Field(description="该阶层的尊称。例如：'下城区贱民'、'外门杂役'、'序列9-收尸人'。")
    hard_cost: str = Field(
        description="角色在代码逻辑中晋升至此层层级所需的绝对硬性代价。例如：'消耗纯净水*100升、脑容量永久损耗15%'。"
    )


class MicroLocationNode(BaseModel):
    """微观物理区域节点。控制剧情发生地、致死率与图像生成提示词。"""

    location_id: str = Field(description="物理节点唯一标识符，格式规范如：'loc_slum_04'")
    name: str = Field(description="区域具象名称。例如：'4号机械垃圾镇'、'无尽剑海'。")
    danger_coefficient: float = Field(
        ge=0.0,
        le=1.0,
        description="区域危险系数（0.0 至 1.0）。在状态机循环中作为计算事件突发致死率或遭遇战概率的直接权重系数。",
    )
    visual_sd_prompt: str = Field(
        description="高度原子化的纯英文视觉 Tag。后续无缝透传给 ComfyUI 渲染。不得出现长句叙述。"
        "例如：'rusty metallic dust, dark neon cyber, dense oppressive grey fog'。",
    )


# ====== 【针对 Geography Agent 的专用响应容器】 ======
class GeographyState(BaseModel):
    """地理精算师 Agent 的直接输出 Schema"""
    micro_locations: list[MicroLocationNode] = Field(
        min_items=3, max_items=8, description="根据宏观背景切分的具象物理区域节点列表"
    )

# ====== 【针对 Economy Agent 的专用响应容器】 ======
class EconomyState(BaseModel):
    """阶级与社会精算师 Agent 的直接输出 Schema"""
    micro_hierarchy: list[MicroPowerTier] = Field(description="战力与社会阶层精算大表，必须包含从底层到高层的完整梯度")
    micro_resources: list[MicroResource] = Field(description="引发地缘冲突的核心经济原子资产")
    micro_factions: list[MicroFaction] = Field(description="割据世界的政治、宗门或财阀派系")
    micro_characters: list[MicroCharacter] = Field(description="作为世界观具象载体的初始核心角色")

    @model_validator(mode='after')
    def validate_internal_economy(self):
        """局部内聚校验：在社会学阶段就熔断错乱的外键"""
        faction_ids = {f.faction_id for f in self.micro_factions}
        resource_ids = {r.resource_id for r in self.micro_resources}
        rank_levels = {p.rank for p in self.micro_hierarchy}

        for char in self.micro_characters:
            if char.affiliation_faction_id not in faction_ids:
                raise ValueError(f"角色 {char.character_id} 归属了不存在的势力 {char.affiliation_faction_id}")
            if char.current_tier_rank not in rank_levels:
                raise ValueError(f"角色 {char.character_id} 的级别在阶层表中未定义")
        return self

# ====== 【针对 Conflict Agent 的专用响应容器】 ======
class ConflictState(BaseModel):
    """冲突编排师 Agent 的直接输出 Schema"""
    micro_conflicts: list[MicroConflictNode] = Field(description="核心地缘政治与利益对立冲突节点网络")