import { get } from './client'
import type { ProductivityCurveResponse } from '@/types/productivityCurve'

export function getProductivityCurve(date: string): Promise<ProductivityCurveResponse> {
  return get<ProductivityCurveResponse>(`/api/productivity-curve/${date}`)
}

export function getProductivityCurveRange(
  start: string,
  end: string,
): Promise<ProductivityCurveResponse[]> {
  return get<ProductivityCurveResponse[]>('/api/productivity-curve', { start, end })
}
