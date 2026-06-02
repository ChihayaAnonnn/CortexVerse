// 四阶段加载动画组件

import { BUILD_PHASES, type BuildPhase } from '../types/world'

interface LoadingPhasesProps {
  currentPhase: BuildPhase
  currentStep?: number
}

export function LoadingPhases({ currentPhase, currentStep = 0 }: LoadingPhasesProps) {
  const currentIndex = BUILD_PHASES.findIndex((p) => p.key === currentPhase)

  return (
    <div className="glass-card p-6">
      <h3 className="font-orbitron text-lg neon-orange mb-6 text-center">
        构建进度
      </h3>

      <div className="space-y-4">
        {BUILD_PHASES.map((phase, index) => {
          const stepNumber = index + 1
          const isActive = index === currentIndex
          const isCompleted = stepNumber <= currentStep

          return (
            <div
              key={phase.key}
              className="flex items-center gap-4 p-4 rounded-lg transition-all"
              style={{
                background: isActive
                  ? 'rgba(0, 255, 136, 0.05)'
                  : 'transparent',
                border: `1px solid ${isActive ? 'var(--cyber-green)' : 'var(--cyber-border)'}`,
                opacity: isCompleted ? 0.6 : 1,
              }}
            >
              {/* 状态指示器 */}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 ${isActive ? 'phase-active' : ''}`}
                style={{
                  background: isCompleted
                    ? 'var(--cyber-green)'
                    : isActive
                      ? 'transparent'
                      : 'var(--cyber-bg)',
                  border: isActive ? '2px solid var(--cyber-green)' : 'none',
                }}
              >
                {isCompleted ? '✓' : phase.icon}
              </div>

              {/* 阶段信息 */}
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className="font-orbitron text-sm"
                    style={{
                      color: isActive
                        ? 'var(--cyber-green)'
                        : isCompleted
                          ? 'var(--cyber-text-dim)'
                          : 'var(--cyber-text)',
                    }}
                  >
                    {phase.label}
                  </span>
                  {isActive && (
                    <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--cyber-green)', color: '#000' }}>
                      进行中
                    </span>
                  )}
                  {isCompleted && (
                    <span className="text-xs" style={{ color: 'var(--cyber-text-dim)' }}>
                      完成
                    </span>
                  )}
                </div>
                <p className="text-xs mt-1" style={{ color: 'var(--cyber-text-dim)' }}>
                  {phase.description}
                </p>
              </div>

              {/* 进度条 */}
              {isActive && (
                <div className="w-16 h-1 rounded-full overflow-hidden" style={{ background: 'var(--cyber-border)' }}>
                  <div
                    className="h-full rounded-full"
                    style={{
                      background: 'var(--cyber-green)',
                      animation: 'loading-bar 2s ease-in-out infinite',
                    }}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* 提示文字 */}
      <p className="text-center text-xs mt-6" style={{ color: 'var(--cyber-text-dim)' }}>
        正在调用 LLM 生成世界观资产，请耐心等待...
      </p>

      <style>{`
        @keyframes loading-bar {
          0% { width: 0%; }
          50% { width: 100%; }
          100% { width: 0%; }
        }
      `}</style>
    </div>
  )
}
