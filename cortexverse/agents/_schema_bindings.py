"""集中注册所有 Agent 的输出 Schema（导入即生效）。"""

from cortexverse.domain.world.macro import MacroState
from cortexverse.domain.world.micro import ConflictState, EconomyState, GeographyState
from cortexverse.agents.factory.registry import register_schema

register_schema("macro_architect")(MacroState)
register_schema("geography_subagent")(GeographyState)
register_schema("economy_subagent")(EconomyState)
register_schema("conflict_subagent")(ConflictState)
