// 世界构建 API 调用封装

import type { WorldGenerateRequest, WorldGenerateResponse } from '../types/world'

const API_BASE = '/api'

/**
 * 触发世界构建流水线
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
