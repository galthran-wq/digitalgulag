export interface ProductivityPoint {
  interval_start: string
  focus_score: number | null
  depth: string | null
  category: string | null
  color: string | null
  is_work: boolean
  productivity_score: number | null
}

export interface ProductivityCurveResponse {
  date: string
  points: ProductivityPoint[]
  day_score: number | null
  work_minutes: number
}
