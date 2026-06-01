"""宏观上下文层（MACRO）— 世界的叙事风味、前史厚度与灵魂基调。"""

from pydantic import BaseModel, Field


class MacroPhilosophy(BaseModel):
    """世界的宏观哲学与精神内核。控制故事的基调与集体潜意识。"""

    theme_statement: str = Field(
        description="定义世界的核心精神内核与主要矛盾。例如：'凡人对宿命的悲壮反抗' 或 '金钱对人性的绝对异化'。"
    )
    narrative_tone: str = Field(
        description="文本风格语调提示词（以逗号分隔）。直接作为下游 LLM 的语气控制器。例如：'黑冷, 荒诞讽刺, 古典厚重'。"
    )
    world_drive_force: str = Field(
        description="促使这个世界自运转、引发底层群体行为冲突的终极欲望或集体潜意识。例如：'对长生的极度渴望'。"
    )


class MacroHistory(BaseModel):
    """世界的前史厚度。为当下的遗迹、奇观、核心冲突提供合法性解释。"""

    epoch_name: str = Field(
        description="当前故事发生时代的宏观尊称。例如：'大崩塌后的第七纪元'、'黄金帝国末期'。"
    )
    pre_history_legacy: str = Field(
        description="一句话高度概括前史对现在世界留下的最大物理或精神遗产。例如：'神明陨落后留下的辐射改变了全球生态'。"
    )


class MacroGrowthOverview(BaseModel):
    """世界的成长哲学。为角色跨越阶层提供宏观逻辑。"""

    ladder_philosophy: str = Field(
        description="阶级或力量晋升的底层宏观代价。例如：'通过融合机械义肢获取力量，但会随着义体化程度提高而逐渐丧失人性'。"
    )
    desire_anchor: str = Field(
        description="整个世界里几乎所有人都在追逐的梦幻泡影或终极特权。例如：'上城区的永久居住权'、'飞升仙界的通票'。"
    )
