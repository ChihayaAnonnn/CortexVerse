// CortexVerse — 世界构建可视化

import { useState, useCallback } from 'react'
import { WorldForm } from './components/WorldForm'
import { LoadingPhases } from './components/LoadingPhases'
import { WorldResult } from './components/WorldResult'
import { generateWorld } from './api/world'
import type { BuildPhase, WorldAsset, WorldGenerateRequest } from './types/world'

function App() {
  const [phase, setPhase] = useState<BuildPhase>('idle')
  const [worldAsset, setWorldAsset] = useState<WorldAsset | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = useCallback(async (request: WorldGenerateRequest) => {
    setPhase('macro_architect')
    setWorldAsset(null)
    setError(null)

    // 模拟阶段推进（实际只有一个 API 调用，用定时器模拟进度）
    const phaseTimers = [
      setTimeout(() => setPhase('geography_subagent'), 3000),
      setTimeout(() => setPhase('economy_subagent'), 6000),
      setTimeout(() => setPhase('conflict_subagent'), 9000),
    ]

    try {
      const response = await generateWorld(request)

      // 清除定时器
      phaseTimers.forEach(clearTimeout)

      if (response.status === 'completed' && response.world_asset) {
        setPhase('completed')
        setWorldAsset(response.world_asset)
      } else {
        setPhase('failed')
        setError(response.error || '构建失败')
      }
    } catch (err) {
      phaseTimers.forEach(clearTimeout)
      setPhase('failed')
      setError(err instanceof Error ? err.message : '网络请求失败')
    }
  }, [])

  const handleReset = useCallback(() => {
    setPhase('idle')
    setWorldAsset(null)
    setError(null)
  }, [])

  const isLoading = phase !== 'idle' && phase !== 'completed' && phase !== 'failed'

  return (
    <div className="min-h-screen" style={{ background: 'var(--cyber-bg)' }}>
      {/* 头部 */}
      <header className="py-8 text-center">
        <h1 className="font-orbitron text-4xl neon-green mb-2">CORTEXVERSE</h1>
        <p className="text-sm" style={{ color: 'var(--cyber-text-dim)' }}>
          系统驱动的虚拟内容生产线
        </p>
      </header>

      {/* 主内容区 */}
      <main className="max-w-6xl mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧：输入 */}
          <div>
            {phase === 'idle' || phase === 'completed' || phase === 'failed' ? (
              <WorldForm onSubmit={handleGenerate} isLoading={isLoading} />
            ) : (
              <LoadingPhases currentPhase={phase} />
            )}

            {/* 错误信息 */}
            {error && (
              <div
                className="mt-4 p-4 rounded-lg"
                style={{ background: 'rgba(255, 107, 53, 0.1)', border: '1px solid var(--cyber-orange)' }}
              >
                <p className="text-sm" style={{ color: 'var(--cyber-orange)' }}>
                  构建失败：{error}
                </p>
                <button
                  onClick={handleReset}
                  className="mt-2 text-xs underline"
                  style={{ color: 'var(--cyber-text-dim)' }}
                >
                  重试
                </button>
              </div>
            )}

            {/* 完成后重置按钮 */}
            {phase === 'completed' && worldAsset && (
              <button
                onClick={handleReset}
                className="mt-4 w-full py-2 rounded-lg text-sm transition-all"
                style={{
                  background: 'transparent',
                  border: '1px solid var(--cyber-border)',
                  color: 'var(--cyber-text-dim)',
                }}
              >
                构建新的世界观
              </button>
            )}
          </div>

          {/* 右侧：结果 */}
          <div>
            {worldAsset ? (
              <WorldResult worldAsset={worldAsset} />
            ) : (
              <div className="glass-card p-12 text-center">
                <div className="text-6xl mb-4">🌌</div>
                <p className="text-sm" style={{ color: 'var(--cyber-text-dim)' }}>
                  {isLoading ? '正在构建世界观...' : '填写参数并开始构建'}
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* 底部 */}
      <footer className="py-6 text-center">
        <p className="text-xs" style={{ color: 'var(--cyber-text-dim)' }}>
          CortexVerse v0.1.0 · Powered by DeepSeek + Instructor
        </p>
      </footer>
    </div>
  )
}

export default App
