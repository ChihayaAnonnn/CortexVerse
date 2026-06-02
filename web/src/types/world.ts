// 世界观类型定义 — 对应后端 Pydantic 模型

// ====== 宏观层 ======

export interface MacroPhilosophy {
  theme_statement: string
  narrative_tone: string
  world_drive_force: string
}

export interface MacroHistory {
  epoch_name: string
  pre_history_legacy: string
}

export interface MacroGrowthOverview {
  ladder_philosophy: string
  desire_anchor: string
}

// ====== 微观层 ======

export interface MicroFaction {
  faction_id: string
  name: string
  core_belief: string
  controlled_resource_ids: string[]
}

export interface MicroCharacter {
  character_id: string
  name: string
  affiliation_faction_id: string
  current_tier_rank: number
}

export interface MicroResource {
  resource_id: string
  name: string
  scarcity_scale: number
  monopolizer_faction_id: string
}

export interface MicroConflictNode {
  conflict_id: string
  faction_a_id: string
  faction_b_id: string
  contested_resource_id: string
  climax_trigger: string
}

export interface MicroPowerTier {
  rank: number
  title: string
  hard_cost: string
}

export interface MicroLocationNode {
  location_id: string
  name: string
  danger_coefficient: number
  visual_sd_prompt: string
}

// ====== 聚合根 ======

export interface WorldAsset {
  world_id: string
  name: string
  genre_tags: string[]
  macro_philosophy: MacroPhilosophy
  macro_history: MacroHistory
  macro_growth: MacroGrowthOverview
  micro_factions: MicroFaction[]
  micro_characters: MicroCharacter[]
  micro_resources: MicroResource[]
  micro_conflicts: MicroConflictNode[]
  micro_hierarchy: MicroPowerTier[]
  micro_locations: MicroLocationNode[]
}

// ====== API 请求/响应 ======

export interface WorldGenerateRequest {
  world_name: string
  genre_tags: string[]
  theme_input: string
}

export interface WorldGenerateResponse {
  world_id: string
  status: 'completed' | 'failed'
  world_asset: WorldAsset | null
  error: string | null
}

// ====== 构建阶段 ======

export type BuildPhase =
  | 'idle'
  | 'macro_architect'
  | 'geography_subagent'
  | 'economy_subagent'
  | 'conflict_subagent'
  | 'completed'
  | 'failed'

export interface PhaseInfo {
  key: BuildPhase
  label: string
  description: string
  icon: string
}

export const BUILD_PHASES: PhaseInfo[] = [
  { key: 'macro_architect', label: '宏观架构', description: '构建世界哲学内核与历史厚度', icon: '🌌' },
  { key: 'geography_subagent', label: '地理精算', description: '切分物理区域节点与视觉标签', icon: '🗺️' },
  { key: 'economy_subagent', label: '经济社会', description: '设计阶层、资源、势力与角色', icon: '⚔️' },
  { key: 'conflict_subagent', label: '冲突编排', description: '编排核心矛盾与导火索事件', icon: '🔥' },
]
