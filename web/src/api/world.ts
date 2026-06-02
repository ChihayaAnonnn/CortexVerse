// 世界构建 API 调用封装

import type { WorldGenerateRequest, WorldGenerateResponse } from '../types/world'

const API_BASE = '/api'

/**
 * 触发世界构建流水线（同步版本）
 * @param request 世界构建请求参数
 * @returns 世界构建响应
 */
export async function generateWorld(request: WorldGenerateRequest): Promise<WorldGenerateResponse> {
  const response = await fetch(`${API_BASE}/world/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

/**
 * SSE 事件类型
 */
export interface SSEEvent {
  event: string
  data: Record<string, unknown>
}

/**
 * 触发世界构建流水线（SSE 流式版本）
 * @param request 世界构建请求参数
 * @param onEvent 事件回调
 */
export async function generateWorldStream(
  request: WorldGenerateRequest,
  onEvent: (event: SSEEvent) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE}/world/generate/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('无法读取响应流')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 解析 SSE 事件
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      let currentEvent = ''
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          const dataStr = line.slice(6)
          try {
            const data = JSON.parse(dataStr)
            onEvent({ event: currentEvent, data })
          } catch {
            // 忽略解析错误
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
