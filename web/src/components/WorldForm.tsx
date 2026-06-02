// 世界构建表单组件

import { useState } from 'react'
import type { WorldGenerateRequest } from '../types/world'

interface WorldFormProps {
  onSubmit: (request: WorldGenerateRequest) => void
  isLoading: boolean
}

const PRESET_TAGS = [
  '赛博朋克', '废土', '修仙', '玄幻', '末日', '科幻', '都市', '历史',
  '悬疑', '恐怖', '武侠', '仙侠', '奇幻', '蒸汽朋克', '架空',
]

export function WorldForm({ onSubmit, isLoading }: WorldFormProps) {
  const [worldName, setWorldName] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [customTag, setCustomTag] = useState('')
  const [themeInput, setThemeInput] = useState('')

  const allTags = [...selectedTags, ...(customTag ? [customTag] : [])]

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!worldName.trim() || allTags.length === 0 || !themeInput.trim()) return

    onSubmit({
      world_name: worldName.trim(),
      genre_tags: allTags,
      theme_input: themeInput.trim(),
    })
  }

  const isValid = worldName.trim() && allTags.length > 0 && themeInput.trim()

  return (
    <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
      {/* 标题 */}
      <div className="text-center mb-6">
        <h2 className="font-orbitron text-xl neon-green mb-2">WORLD BUILDER</h2>
        <p className="text-sm" style={{ color: 'var(--cyber-text-dim)' }}>
          定义你的世界观参数
        </p>
      </div>

      {/* 世界名称 */}
      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--cyber-text-dim)' }}>
          世界名称
        </label>
        <input
          type="text"
          value={worldName}
          onChange={(e) => setWorldName(e.target.value)}
          placeholder="例如：霓虹深渊、九天仙域"
          className="w-full px-4 py-3 rounded-lg text-sm"
          style={{
            background: 'var(--cyber-bg)',
            border: '1px solid var(--cyber-border)',
            color: 'var(--cyber-text)',
            outline: 'none',
          }}
          maxLength={100}
        />
      </div>

      {/* 题材标签 */}
      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--cyber-text-dim)' }}>
          题材标签 <span className="text-xs">（点击选择，至少 1 个）</span>
        </label>
        <div className="flex flex-wrap gap-2 mb-3">
          {PRESET_TAGS.map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => toggleTag(tag)}
              className="px-3 py-1.5 rounded-full text-xs transition-all"
              style={{
                background: selectedTags.includes(tag) ? 'var(--cyber-green)' : 'var(--cyber-bg)',
                color: selectedTags.includes(tag) ? '#000' : 'var(--cyber-text-dim)',
                border: `1px solid ${selectedTags.includes(tag) ? 'var(--cyber-green)' : 'var(--cyber-border)'}`,
              }}
            >
              {tag}
            </button>
          ))}
        </div>
        <input
          type="text"
          value={customTag}
          onChange={(e) => setCustomTag(e.target.value)}
          placeholder="自定义标签（回车确认）"
          className="w-full px-4 py-2 rounded-lg text-sm"
          style={{
            background: 'var(--cyber-bg)',
            border: '1px solid var(--cyber-border)',
            color: 'var(--cyber-text)',
            outline: 'none',
          }}
        />
      </div>

      {/* 主题倾向 */}
      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--cyber-text-dim)' }}>
          核心主题倾向
        </label>
        <textarea
          value={themeInput}
          onChange={(e) => setThemeInput(e.target.value)}
          placeholder="描述你想要的世界核心矛盾与叙事基调，例如：底层逆袭、打破阶级固化、凡人对抗宿命"
          rows={3}
          className="w-full px-4 py-3 rounded-lg text-sm resize-none"
          style={{
            background: 'var(--cyber-bg)',
            border: '1px solid var(--cyber-border)',
            color: 'var(--cyber-text)',
            outline: 'none',
          }}
          maxLength={500}
        />
      </div>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={!isValid || isLoading}
        className="w-full py-3 rounded-lg font-orbitron text-sm font-semibold transition-all"
        style={{
          background: isValid && !isLoading ? 'var(--cyber-green)' : 'var(--cyber-border)',
          color: isValid && !isLoading ? '#000' : 'var(--cyber-text-dim)',
          cursor: isValid && !isLoading ? 'pointer' : 'not-allowed',
          boxShadow: isValid && !isLoading ? '0 0 20px rgba(0, 255, 136, 0.3)' : 'none',
        }}
      >
        {isLoading ? '构建中...' : '开始构建'}
      </button>
    </form>
  )
}
