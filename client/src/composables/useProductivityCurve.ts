import { ref, computed, type Ref } from 'vue'
import { getProductivityCurve } from '@/api/productivityCurve'
import type { ProductivityCurveResponse, ProductivityPoint } from '@/types/productivityCurve'

export function useProductivityCurve(date: Ref<string>) {
  const curve = ref<ProductivityCurveResponse | null>(null)
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try {
      curve.value = await getProductivityCurve(date.value)
    } catch {
      curve.value = null
    } finally {
      loading.value = false
    }
  }

  const points = computed(() => curve.value?.points ?? [])
  const dayScore = computed(() => curve.value?.day_score ?? null)
  const workMinutes = computed(() => curve.value?.work_minutes ?? 0)

  const chartData = computed(() => {
    if (!points.value.length) return null

    const timestamps: number[] = []
    const scores: (number | null)[] = []
    const colors: (string | null)[] = []

    for (const p of points.value) {
      timestamps.push(new Date(p.interval_start).getTime() / 1000)
      scores.push(p.productivity_score)
      colors.push(p.color)
    }

    return { timestamps, scores, colors }
  })

  return { curve, loading, points, dayScore, workMinutes, chartData, fetch }
}
