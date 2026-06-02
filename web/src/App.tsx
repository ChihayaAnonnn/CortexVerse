// CortexVerse — 世界构建可视化

import { useState, useCallback } from 'react'
import { WorldForm } from './components/WorldForm'
import { LoadingPhases } from './components/LoadingPhases'
import { WorldResult } from './components/WorldResult'
import { generateWorldStream } from './api/world'
import type {
  BuildPhase,
  WorldAsset,
  WorldGenerateRequest,
  PhaseResult,
  SSEPhaseComplete,
  SSEWorldComplete,
  SSEWorldFailed,
} from './types/world'

function App() {
  const [phase, setPhase] = useState<BuildPhase>('idle')
  const [worldAsset, setWorldAsset] = useState<WorldAsset | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [phaseResults, setPhaseResults] = useState<Record<number, PhaseResult>>({})

  const handleGenerate = useCallback(async (request: WorldGenerateRequest) => {
    setPhase('macro_architect')
    setWorldAsset(null)
    setError(null)
    setPhaseResults({})

    try {
      await generateWorldStream(request, (event) => {
        switch (event.event) {
          case 'phase_start': {
            const { phase: phaseName } = event.data as { phase: string }
            setPhase(phaseName as BuildPhase)
            break
          }
          case 'phase_complete': {
            const data = event.data as unknown as SSEPhaseComplete
            setPhaseResults((prev) => ({
              ...prev,
              [data.step]: { phase: data.phase as BuildPhase, step: data.step, result: data.result },
            }))
            break
          }
          case 'world_complete': {
            const data = event.data as unknown as SSEWorldComplete
            setPhase('completed')
            setWorldAsset(data.world_asset)
            break
          }
          case 'world_failed': {
            const data = event.data as unknown as SSEWorldFailed
            setPhase('failed')
            setError(data.error)
            break
          }
        }
      })
    } catch (err) {
      setPhase('failed')
      setError(err instanceof Error ? err.message : '网络请求失败')
    }
  }, [])

  const handleReset = useCallback(() => {
    setPhase('idle')
    setWorldAsset(null)
    setError(null)
    setPhaseResults({})
  }, [])

  const isLoading = phase !== 'idle' && phase !== 'completed' && phase !== 'failed'

  // 获取当前阶段的步骤数
  const getCurrentStep = () => {
    const steps = Object.keys(phaseResults).map(Number)
    return steps.length > 0 ? Math.max(...steps) : 0
  }

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
              <LoadingPhases currentPhase={phase} currentStep={getCurrentStep()} />
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
            ) : isLoading && Object.keys(phaseResults).length > 0 ? (
              <PhaseResultsPreview phaseResults={phaseResults} />
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

// 阶段结果预览组件
function PhaseResultsPreview({ phaseResults }: { phaseResults: Record<number, PhaseResult> }) {
  const sortedResults = Object.entries(phaseResults)
    .map(([step, result]) => ({ stepNum: Number(step), ...result }))
    .sort((a, b) => a.stepNum - b.stepNum)

  const phaseLabels: Record<string, string> = {
    macro_architect: '宏观架构',
    geography_subagent: '地理精算',
    economy_subagent: '经济社会',
    conflict_subagent: '冲突编排',
  }

  const phaseIcons: Record<string, string> = {
    macro_architect: '🌌',
    geography_subagent: '🗺️',
    economy_subagent: '⚔️',
    conflict_subagent: '🔥',
  }

  return (
    <div className="space-y-4">
      <h3 className="font-orbitron text-lg neon-orange text-center">已完成的阶段</h3>
      {sortedResults.map(({ stepNum, phase, result }) => (
        <div key={stepNum} className="glass-card p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">{phaseIcons[phase] || '✨'}</span>
            <span className="font-orbitron text-sm" style={{ color: 'var(--cyber-green)' }}>
              阶段 {stepNum}：{phaseLabels[phase] || phase}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--cyber-green)', color: '#000' }}>
              完成
            </span>
          </div>
          <div className="text-xs p-3 rounded-lg overflow-auto max-h-40" style={{ background: 'var(--cyber-bg)', color: 'var(--cyber-text-dim)' }}>
            <pre className="whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
          </div>
        </div>
      ))}
    </div>
  )
}

export default App
