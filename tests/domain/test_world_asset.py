"""WorldAsset 关系校验测试。"""

import pytest

from cortexverse.domain import (
    MacroGrowthOverview,
    MacroHistory,
    MacroPhilosophy,
    MicroCharacter,
    MicroConflictNode,
    MicroFaction,
    MicroLocationNode,
    MicroPowerTier,
    MicroResource,
    WorldAsset,
)


def _build_valid_world_asset() -> WorldAsset:
    """构建一个合法的 WorldAsset 实例。"""
    return WorldAsset(
        world_id="world_test_001",
        name="测试世界观",
        genre_tags=["赛博朋克", "废土末日"],
        macro_philosophy=MacroPhilosophy(
            theme_statement="凡人对宿命的反抗",
            narrative_tone="黑冷, 荒诞讽刺",
            world_drive_force="对净水的极度渴望",
        ),
        macro_history=MacroHistory(
            epoch_name="大崩塌后的第七纪元",
            pre_history_legacy="核战后地表水源枯竭",
        ),
        macro_growth=MacroGrowthOverview(
            ladder_philosophy="通过义体改造获取力量，但逐渐丧失人性",
            desire_anchor="上城区的永久居住权",
        ),
        micro_factions=[
            MicroFaction(
                faction_id="fac_aqua_corp",
                name="水务集团",
                core_belief="垄断净水，控制人口",
                controlled_resource_ids=["res_pure_water"],
            ),
            MicroFaction(
                faction_id="fac_rebel",
                name="反抗军",
                core_belief="水资源应当公有",
                controlled_resource_ids=[],
            ),
        ],
        micro_characters=[
            MicroCharacter(
                character_id="char_protagonist",
                name="凯",
                affiliation_faction_id="fac_rebel",
                current_tier_rank=1,
            ),
        ],
        micro_resources=[
            MicroResource(
                resource_id="res_pure_water",
                name="高纯度净水",
                scarcity_scale=9,
                monopolizer_faction_id="fac_aqua_corp",
            ),
        ],
        micro_conflicts=[
            MicroConflictNode(
                conflict_id="conf_water_war",
                faction_a_id="fac_rebel",
                faction_b_id="fac_aqua_corp",
                contested_resource_id="res_pure_water",
                climax_trigger="反抗军突袭水务集团的净水工厂",
            ),
        ],
        micro_hierarchy=[
            MicroPowerTier(rank=1, title="下城区贱民", hard_cost="无"),
            MicroPowerTier(rank=2, title="中城区市民", hard_cost="缴纳 100 升净水"),
        ],
        micro_locations=[
            MicroLocationNode(
                location_id="loc_slum",
                name="下城区废墟",
                danger_coefficient=0.8,
                visual_sd_prompt="rusty metallic dust, dark neon cyber, dense oppressive grey fog",
            ),
        ],
    )


def test_valid_world_asset_passes_validation() -> None:
    """合法的 WorldAsset 应通过关系校验。"""
    asset = _build_valid_world_asset()
    assert asset.world_id == "world_test_001"
    assert len(asset.micro_factions) == 2
    assert len(asset.micro_conflicts) == 1


def test_invalid_faction_a_id_raises_error() -> None:
    """冲突节点引用不存在的 faction_a_id 时应抛出 ValueError。"""
    with pytest.raises(ValueError, match="faction_a_id"):
        WorldAsset(
            world_id="world_invalid",
            name="无效世界观",
            genre_tags=["测试"],
            macro_philosophy=MacroPhilosophy(
                theme_statement="测试", narrative_tone="测试", world_drive_force="测试"
            ),
            macro_history=MacroHistory(epoch_name="测试", pre_history_legacy="测试"),
            macro_growth=MacroGrowthOverview(ladder_philosophy="测试", desire_anchor="测试"),
            micro_factions=[
                MicroFaction(faction_id="fac_a", name="A", core_belief="测试"),
            ],
            micro_conflicts=[
                MicroConflictNode(
                    conflict_id="conf_bad",
                    faction_a_id="fac_nonexistent",
                    faction_b_id="fac_a",
                    contested_resource_id="res_x",
                    climax_trigger="测试",
                ),
            ],
            micro_resources=[
                MicroResource(resource_id="res_x", name="X", scarcity_scale=5, monopolizer_faction_id="public"),
            ],
        )


def test_invalid_character_faction_raises_error() -> None:
    """角色引用不存在的 faction_id 时应抛出 ValueError。"""
    with pytest.raises(ValueError, match="关系校验失败.*fac_nonexistent"):
        WorldAsset(
            world_id="world_invalid",
            name="无效世界观",
            genre_tags=["测试"],
            macro_philosophy=MacroPhilosophy(
                theme_statement="测试", narrative_tone="测试", world_drive_force="测试"
            ),
            macro_history=MacroHistory(epoch_name="测试", pre_history_legacy="测试"),
            macro_growth=MacroGrowthOverview(ladder_philosophy="测试", desire_anchor="测试"),
            micro_factions=[
                MicroFaction(faction_id="fac_a", name="A", core_belief="测试"),
            ],
            micro_characters=[
                MicroCharacter(
                    character_id="char_bad",
                    name="无效角色",
                    affiliation_faction_id="fac_nonexistent",
                    current_tier_rank=1,
                ),
            ],
            micro_hierarchy=[
                MicroPowerTier(rank=1, title="底层", hard_cost="无"),
            ],
        )


def test_invalid_resource_in_faction_raises_error() -> None:
    """组织引用不存在的资源 ID 时应抛出 ValueError。"""
    with pytest.raises(ValueError, match="关系校验失败.*res_nonexistent"):
        WorldAsset(
            world_id="world_invalid",
            name="无效世界观",
            genre_tags=["测试"],
            macro_philosophy=MacroPhilosophy(
                theme_statement="测试", narrative_tone="测试", world_drive_force="测试"
            ),
            macro_history=MacroHistory(epoch_name="测试", pre_history_legacy="测试"),
            macro_growth=MacroGrowthOverview(ladder_philosophy="测试", desire_anchor="测试"),
            micro_factions=[
                MicroFaction(
                    faction_id="fac_a",
                    name="A",
                    core_belief="测试",
                    controlled_resource_ids=["res_nonexistent"],
                ),
            ],
            micro_resources=[
                MicroResource(resource_id="res_real", name="真实资源", scarcity_scale=5, monopolizer_faction_id="public"),
            ],
        )
