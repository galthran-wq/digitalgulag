<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import uPlot from 'uplot'
import 'uplot/dist/uPlot.min.css'
import type { ProductivityPoint } from '@/types/productivityCurve'

const props = defineProps<{
  points: ProductivityPoint[]
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: uPlot | null = null

function buildChart() {
  if (!chartEl.value || !props.points.length) return
  if (chart) {
    chart.destroy()
    chart = null
  }

  const timestamps: number[] = []
  const scores: (number | null)[] = []
  const pointColors: (string | null)[] = []
  const isWork: boolean[] = []

  for (const p of props.points) {
    timestamps.push(new Date(p.interval_start).getTime() / 1000)
    scores.push(p.productivity_score)
    pointColors.push(p.color)
    isWork.push(p.is_work)
  }

  const width = chartEl.value.clientWidth
  const height = 220

  const opts: uPlot.Options = {
    width,
    height,
    cursor: {
      show: true,
      points: { show: true, size: 8, fill: '#0d7377' },
    },
    scales: {
      x: { time: true },
      y: { min: 0, max: 100 },
    },
    axes: [
      {
        stroke: 'rgba(150,150,150,0.6)',
        grid: { stroke: 'rgba(150,150,150,0.1)' },
        ticks: { stroke: 'rgba(150,150,150,0.2)' },
      },
      {
        stroke: 'rgba(150,150,150,0.6)',
        grid: { stroke: 'rgba(150,150,150,0.1)' },
        ticks: { stroke: 'rgba(150,150,150,0.2)' },
        values: (_: uPlot, vals: number[]) => vals.map((v) => String(Math.round(v))),
      },
    ],
    series: [
      {},
      {
        label: 'Productivity',
        stroke: '#0d7377',
        width: 2,
        fill: (self: uPlot, seriesIdx: number) => {
          const ctx = self.ctx
          if (!ctx) return 'rgba(13,115,119,0.15)'

          const plotTop = self.bbox.top / devicePixelRatio
          const plotBot = (self.bbox.top + self.bbox.height) / devicePixelRatio

          const grad = ctx.createLinearGradient(0, plotTop, 0, plotBot)
          grad.addColorStop(0, 'rgba(13,115,119,0.3)')
          grad.addColorStop(1, 'rgba(13,115,119,0.02)')
          return grad
        },
        points: {
          show: false,
        },
      },
    ],
    plugins: [
      {
        hooks: {
          drawSeries: [
            (u: uPlot, seriesIdx: number) => {
              if (seriesIdx !== 1) return
              const ctx = u.ctx
              if (!ctx) return

              const xData = u.data[0]
              const yData = u.data[1]
              if (!xData || !yData) return

              for (let i = 0; i < xData.length; i++) {
                const score = yData[i]
                if (score == null) continue

                const cx = Math.round(u.valToPos(xData[i], 'x', true))
                const cy = Math.round(u.valToPos(score as number, 'y', true))
                const color = pointColors[i]
                if (!color) continue

                const alpha = isWork[i] ? 0.9 : 0.4
                ctx.beginPath()
                ctx.arc(cx, cy, 4 * devicePixelRatio, 0, Math.PI * 2)
                ctx.fillStyle = color.replace(/^#([0-9a-f]{6})$/i, (_, hex) => {
                  const r = parseInt(hex.slice(0, 2), 16)
                  const g = parseInt(hex.slice(2, 4), 16)
                  const b = parseInt(hex.slice(4, 6), 16)
                  return `rgba(${r},${g},${b},${alpha})`
                })
                ctx.fill()
              }
            },
          ],
        },
      },
    ],
  }

  const data: uPlot.AlignedData = [
    new Float64Array(timestamps),
    scores.map((s) => (s == null ? null : s)) as any,
  ]

  chart = new uPlot(opts, data, chartEl.value)
}

function handleResize() {
  if (chart && chartEl.value) {
    chart.setSize({ width: chartEl.value.clientWidth, height: 220 })
  }
}

watch(
  () => props.points,
  () => nextTick(buildChart),
  { deep: true },
)

onMounted(() => {
  nextTick(buildChart)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.destroy()
    chart = null
  }
})
</script>

<template>
  <div ref="chartEl" class="productivity-curve" />
</template>

<style scoped>
.productivity-curve {
  width: 100%;
  min-height: 220px;
}
</style>
