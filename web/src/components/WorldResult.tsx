// 世界构建结果展示组件

import type { WorldAsset } from '../types/world'

interface WorldResultProps {
  worldAsset: WorldAsset
}

export function WorldResult({ worldAsset }: WorldResultProps) {
  const { macro_philosophy, macro_history, macro_growth, micro_factions, micro_resources, micro_characters, micro_conflicts, micro_hierarchy, micro_locations } = worldAsset

  return (
    <div className="space-y-6">
      {/* 头部信息 */}
      <div className="glass-card p-6 text-center">
        <h2 className="font-orbitron text-2xl neon-green mb-2">{worldAsset.name}</h2>
        <div className="flex items-center justify-center gap-2 flex-wrap">
          {worldAsset.genre_tags.map((tag) => (
            <span
              key={tag}
              className="px-3 py-1 rounded-full text-xs"
              style={{ background: 'var(--cyber-green)', color: '#000' }}
            >
              {tag}
            </span>
          ))}
        </div>
        <p className="text-xs mt-3" style={{ color: 'var(--cyber-text-dim)' }}>
          ID: {worldAsset.world_id}
        </p>
      </div>

      {/* 宏观哲学 */}
      <div className="glass-card p-6">
        <h3 className="font-orbitron text-sm neon-orange mb-4">宏观哲学</h3>
        <div className="space-y-3">
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>核心主题</span>
            <p className="text-sm mt-1">{macro_philosophy.theme_statement}</p>
          </div>
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>叙事基调</span>
            <p className="text-sm mt-1">{macro_philosophy.narrative_tone}</p>
          </div>
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>世界驱动力</span>
            <p className="text-sm mt-1">{macro_philosophy.world_drive_force}</p>
          </div>
        </div>
      </div>

      {/* 宏观历史 */}
      <div className="glass-card p-6">
        <h3 className="font-orbitron text-sm neon-orange mb-4">宏观历史</h3>
        <div className="space-y-3">
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>时代名称</span>
            <p className="text-sm mt-1">{macro_history.epoch_name}</p>
          </div>
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>前史遗产</span>
            <p className="text-sm mt-1">{macro_history.pre_history_legacy}</p>
          </div>
        </div>
      </div>

      {/* 成长逻辑 */}
      <div className="glass-card p-6">
        <h3 className="font-orbitron text-sm neon-orange mb-4">成长逻辑</h3>
        <div className="space-y-3">
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>阶级晋升代价</span>
            <p className="text-sm mt-1">{macro_growth.ladder_philosophy}</p>
          </div>
          <div>
            <span className="text-xs font-medium" style={{ color: 'var(--cyber-text-dim)' }}>欲望锚点</span>
            <p className="text-sm mt-1">{macro_growth.desire_anchor}</p>
          </div>
        </div>
      </div>

      {/* 地理节点 */}
      {micro_locations.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-orbitron text-sm neon-orange mb-4">
            地理节点 <span className="text-xs font-normal" style={{ color: 'var(--cyber-text-dim)' }}>({micro_locations.length})</span>
          </h3>
          <div className="grid gap-3">
            {micro_locations.map((loc) => (
              <div
                key={loc.location_id}
                className="p-3 rounded-lg"
                style={{ background: 'var(--cyber-bg)', border: '1px solid var(--cyber-border)' }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{loc.name}</span>
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      background: loc.danger_coefficient > 0.7 ? 'var(--cyber-orange)' : 'var(--cyber-blue)',
                      color: '#000',
                    }}
                  >
                    危险系数 {loc.danger_coefficient}
                  </span>
                </div>
                <p className="text-xs" style={{ color: 'var(--cyber-text-dim)' }}>
                  {loc.location_id}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 阶层体系 */}
      {micro_hierarchy.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-orbitron text-sm neon-orange mb-4">
            阶层体系 <span className="text-xs font-normal" style={{ color: 'var(--cyber-text-dim)' }}>({micro_hierarchy.length})</span>
          </h3>
          <div className="space-y-2">
            {micro_hierarchy.map((tier) => (
              <div
                key={tier.rank}
                className="flex items-center gap-3 p-3 rounded-lg"
                style={{ background: 'var(--cyber-bg)', border: '1px solid var(--cyber-border)' }}
              >
                <span
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-orbitron"
                  style={{ background: 'var(--cyber-purple)', color: '#fff' }}
                >
                  {tier.rank}
                </span>
                <div className="flex-1">
                  <span className="text-sm font-medium">{tier.title}</span>
                  <p className="text-xs" style={{ color: 'var(--cyber-text-dim)' }}>
                    晋升代价：{tier.hard_cost}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 资源 */}
      {micro_resources.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-orbitron text-sm neon-orange mb-4">
            稀缺资源 <span className="text-xs font-normal" style={{ color: 'var(--cyber-text-dim)' }}>({micro_resources.length})</span>
          </h3>
          <div className="grid gap-3">
            {micro_resources.map((res) => (
              <div
                key={res.resource_id}
                className="p-3 rounded-lg"
                style={{ background: 'var(--cyber-bg)', border: '1px solid var(--cyber-border)' }}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">{res.name}</span>
                  <span className="text-xs" style={{ color: 'var(--cyber-orange)' }}>
                    稀缺度 {res.scarcity_scale}/10
                  </span>
                </div>
                <p className="text-xs" style={{ color: 'var(--cyber-text-dim)' }}>
                  {res.resource_id} · 垄断者：{res.monopolizer_faction_id}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 势力 */}
      {micro_factions.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-orbitron text-sm neon-orange mb-4">
            割据势力 <span className="text-xs font-normal" style={{ color: 'var(--cyber-text-dim)' }}>({micro_factions.length})</span>
          </h3>
          <div className="grid gap-3">
            {micro_factions.map((faction) => (
              <div
                key={faction.faction_id}
                className="p-3 rounded-lg"
                style={{ background: 'var(--cyber-bg)', border: '1px solid var(--cyber-border)' }}
              >
                <span className="text-sm font-medium">{faction.name}</span>
                <p className="text-xs mt-1" style={{ color: 'var(--cyber-text-dim)' }}>
                  {faction.core_belief}
                </p>
                {faction.controlled_resource_ids.length > 0 && (
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {faction.controlled_resource_ids.map((resId) => (
                      <span
                        key={resId}
                        className="text-xs px-2 py-0.5 rounded"
                        style={{ background: 'var(--cyber-border)', color: 'var(--cyber-text-dim)' }}
                      >
                        {resId}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 角色 */}
      {micro_characters.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-orbitron text-sm neon-orange mb-4">
            核心角色 <span className="text-xs font-normal" style={{ color: 'var(--cyber-text-dim)' }}>({micro_characters.length})</span>
          </h3>
          <div className="grid gap-3">
            {micro_characters.map((char) => (
              <div
                key={char.character_id}
                className="p-3 rounded-lg"
                style={{ background: 'var(--cyber-bg)', border: '1px solid var(--cyber-border)' }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{char.name}</span>
                  <span className="text-xs" style={{ color: 'var(--cyber-blue)' }}>
                    阶层 {char.current_tier_rank}
                  </span>
                </div>
                <p className="text-xs mt-1" style={{ color: 'var(--cyber-text-dim)' }}>
                  {char.character_id} · 归属：{char.affiliation_faction_id}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 冲突 */}
      {micro_conflicts.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-orbitron text-sm neon-orange mb-4">
            冲突节点 <span className="text-xs font-normal" style={{ color: 'var(--cyber-text-dim)' }}>({micro_conflicts.length})</span>
          </h3>
          <div className="grid gap-3">
            {micro_conflicts.map((conflict) => (
              <div
                key={conflict.conflict_id}
                className="p-3 rounded-lg"
                style={{ background: 'var(--cyber-bg)', border: '1px solid var(--cyber-orange)' }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs px-2 py-0.5 rounded" style={{ background: 'var(--cyber-orange)', color: '#000' }}>
                    {conflict.faction_a_id}
                  </span>
                  <span className="text-xs" style={{ color: 'var(--cyber-text-dim)' }}>VS</span>
                  <span className="text-xs px-2 py-0.5 rounded" style={{ background: 'var(--cyber-orange)', color: '#000' }}>
                    {conflict.faction_b_id}
                  </span>
                </div>
                <p className="text-sm">{conflict.climax_trigger}</p>
                <p className="text-xs mt-2" style={{ color: 'var(--cyber-text-dim)' }}>
                  争夺资源：{conflict.contested_resource_id}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
