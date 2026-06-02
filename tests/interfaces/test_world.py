"""世界构建 API 测试。"""

from unittest.mock import AsyncMock, patch

import pytest

from cortexverse.domain.macro import MacroGrowthOverview, MacroHistory, MacroPhilosophy, MacroState
from cortexverse.domain.micro import (
    ConflictState,
    EconomyState,
    GeographyState,
    MicroCharacter,
    MicroConflictNode,
    MicroFaction,
    MicroLocationNode,
    MicroPowerTier,
    MicroResource,
)


def _build_mock_macro_state() -> MacroState:
    """构建测试用 MacroState。"""
    return MacroState(
        macro_philosophy=MacroPhilosophy(
            theme_statement="凡人对宿命的反抗",
            narrative_tone="黑冷, 荒诞",
            world_drive_force="对自由的渴望",
        ),
        macro_history=MacroHistory(
            epoch_name="大崩塌后的第七纪元",
            pre_history_legacy="神明陨落后留下的辐射改变了全球生态",
        ),
        macro_growth=MacroGrowthOverview(
            ladder_philosophy="吞噬异种脊髓液可获跃升，但有概率成为畸变体",
            desire_anchor="上城区的永久居住权",
        ),
    )


def _build_mock_geography_state() -> GeographyState:
    """构建测试用 GeographyState。"""
    return GeographyState(micro_locations=[
        MicroLocationNode(
            location_id="loc_slum_01",
            name="机械垃圾镇",
            danger_coefficient=0.7,
            visual_sd_prompt="dark metallic, rusty scaffolding",
        ),
        MicroLocationNode(
            location_id="loc_core_01",
            name="上城区",
            danger_coefficient=0.1,
            visual_sd_prompt="clean white towers, neon lights",
        ),
        MicroLocationNode(
            location_id="loc_abyss_01",
            name="深渊采矿场",
            danger_coefficient=0.9,
            visual_sd_prompt="dark cave, glowing toxic fluid",
        ),
    ])


def _build_mock_economy_state() -> EconomyState:
    """构建测试用 EconomyState。"""
    return EconomyState(
        micro_hierarchy=[
            MicroPowerTier(rank=1, title="下城区贱民", hard_cost="无"),
            MicroPowerTier(rank=2, title="上城区公民", hard_cost="缴纳100万信用点"),
        ],
        micro_resources=[
            MicroResource(
                resource_id="res_pure_water",
                name="高纯度抗辐射水",
                scarcity_scale=9,
                monopolizer_faction_id="fac_neon_corp",
            ),
        ],
        micro_factions=[
            MicroFaction(
                faction_id="fac_neon_corp",
                name="霓虹科技集团",
                core_belief="技术至上",
                controlled_resource_ids=["res_pure_water"],
            ),
            MicroFaction(
                faction_id="fac_rebel",
                name="叛军",
                core_belief="推翻垄断",
                controlled_resource_ids=[],
            ),
        ],
        micro_characters=[
            MicroCharacter(
                character_id="char_kyle_01",
                name="凯尔",
                affiliation_faction_id="fac_neon_corp",
                current_tier_rank=1,
            ),
        ],
    )


def _build_mock_conflict_state() -> ConflictState:
    """构建测试用 ConflictState。"""
    return ConflictState(micro_conflicts=[
        MicroConflictNode(
            conflict_id="conf_water_war",
            faction_a_id="fac_rebel",
            faction_b_id="fac_neon_corp",
            contested_resource_id="res_pure_water",
            climax_trigger="叛军引爆了伪造的以太核心，趁乱劫走了抗辐射水",
        ),
    ])


class TestWorldGenerateAPI:
    """世界构建 API 端点测试。"""

    def test_generate_world_success(self, client) -> None:
        """成功构建世界。"""
        mock_macro = _build_mock_macro_state()
        mock_geo = _build_mock_geography_state()
        mock_econ = _build_mock_economy_state()
        mock_conflict = _build_mock_conflict_state()

        from cortexverse.domain.world_asset import WorldAsset

        mock_world = WorldAsset(
            world_id="world_test1234",
            name="赛博废土",
            genre_tags=["赛博朋克", "废土"],
            macro_philosophy=mock_macro.macro_philosophy,
            macro_history=mock_macro.macro_history,
            macro_growth=mock_macro.macro_growth,
            micro_locations=mock_geo.micro_locations,
            micro_hierarchy=mock_econ.micro_hierarchy,
            micro_resources=mock_econ.micro_resources,
            micro_factions=mock_econ.micro_factions,
            micro_characters=mock_econ.micro_characters,
            micro_conflicts=mock_conflict.micro_conflicts,
        )

        with patch(
            "cortexverse.interfaces.api.world.run_world_generation",
            new_callable=AsyncMock,
            return_value=mock_world,
        ):
            response = client.post(
                "/api/world/generate",
                json={
                    "world_name": "赛博废土",
                    "genre_tags": ["赛博朋克", "废土"],
                    "theme_input": "底层逆袭",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["world_id"] == "world_test1234"
        assert data["error"] is None

    def test_generate_world_failure(self, client) -> None:
        """构建世界失败时返回错误信息。"""
        with patch(
            "cortexverse.interfaces.api.world.run_world_generation",
            side_effect=RuntimeError("LLM 调用超时"),
        ):
            response = client.post(
                "/api/world/generate",
                json={
                    "world_name": "赛博废土",
                    "genre_tags": ["赛博朋克"],
                    "theme_input": "底层逆袭",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "LLM 调用超时" in data["error"]

    def test_generate_world_validation_error(self, client) -> None:
        """请求参数校验失败。"""
        response = client.post(
            "/api/world/generate",
            json={
                "world_name": "",
                "genre_tags": [],
                "theme_input": "",
            },
        )
        assert response.status_code == 422
