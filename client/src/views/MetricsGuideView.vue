<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import ProductivityCurve from '@/components/ProductivityCurve.vue'
import CategoryBreakdownChart from '@/components/CategoryBreakdownChart.vue'
import type { ProductivityPoint } from '@/types/productivityCurve'
import type { TimelineEntry } from '@/types/timeline'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const BASE_DATE = '2026-01-15'
const T = (h: number, m: number) => `${BASE_DATE}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`

function makePoint(h: number, m: number, focus: number, depth: string, category: string, color: string, isWork: boolean): ProductivityPoint {
  const weights: Record<string, number> = { deep: 1.0, shallow: 0.6, reactive: 0.3 }
  return {
    interval_start: T(h, m),
    focus_score: focus,
    depth,
    category,
    color,
    is_work: isWork,
    productivity_score: Math.round(focus * (weights[depth] ?? 1) * 100),
  }
}

const demoPoints: ProductivityPoint[] = [
  makePoint(9, 0, 0.75, 'deep', 'Work', '#3B82F6', true),
  makePoint(9, 10, 0.85, 'deep', 'Work', '#3B82F6', true),
  makePoint(9, 20, 0.92, 'deep', 'Work', '#3B82F6', true),
  makePoint(9, 30, 0.95, 'deep', 'Work', '#3B82F6', true),
  makePoint(9, 40, 0.88, 'deep', 'Work', '#3B82F6', true),
  makePoint(9, 50, 0.90, 'deep', 'Work', '#3B82F6', true),
  makePoint(10, 0, 0.70, 'shallow', 'Admin', '#6B7280', true),
  makePoint(10, 10, 0.65, 'shallow', 'Admin', '#6B7280', true),
  makePoint(10, 20, 0.50, 'reactive', 'Communication', '#8B5CF6', true),
  makePoint(10, 30, 0.45, 'reactive', 'Communication', '#8B5CF6', true),
  makePoint(10, 40, 0.60, 'deep', 'Work', '#3B82F6', true),
  makePoint(10, 50, 0.72, 'deep', 'Work', '#3B82F6', true),
  makePoint(11, 0, 0.80, 'deep', 'Work', '#3B82F6', true),
  makePoint(11, 10, 0.88, 'deep', 'Work', '#3B82F6', true),
  makePoint(11, 20, 0.91, 'deep', 'Work', '#3B82F6', true),
  makePoint(11, 30, 0.40, 'shallow', 'Research', '#F59E0B', true),
  makePoint(11, 40, 0.35, 'reactive', 'Entertainment', '#EF4444', false),
  makePoint(11, 50, 0.25, 'reactive', 'Entertainment', '#EF4444', false),
]

const demoEntries: TimelineEntry[] = [
  { id: '1', user_id: '', date: BASE_DATE, start_time: T(9, 0), end_time: T(10, 0), label: 'Coding in VS Code', description: 'Implementing new feature with deep focus', category: 'Work', color: '#3B82F6', source: 'demo', source_summary: null, confidence: null, edited_by_user: false, created_at: '', updated_at: '' },
  { id: '2', user_id: '', date: BASE_DATE, start_time: T(10, 0), end_time: T(10, 20), label: 'Email & admin tasks', description: 'Triaging inbox and scheduling', category: 'Admin', color: '#6B7280', source: 'demo', source_summary: null, confidence: null, edited_by_user: false, created_at: '', updated_at: '' },
  { id: '3', user_id: '', date: BASE_DATE, start_time: T(10, 20), end_time: T(10, 40), label: 'Team chat', description: 'Responding to Slack messages', category: 'Communication', color: '#8B5CF6', source: 'demo', source_summary: null, confidence: null, edited_by_user: false, created_at: '', updated_at: '' },
  { id: '4', user_id: '', date: BASE_DATE, start_time: T(10, 40), end_time: T(11, 20), label: 'Back to coding', description: 'Resumed feature work, ramping back up', category: 'Work', color: '#3B82F6', source: 'demo', source_summary: null, confidence: null, edited_by_user: false, created_at: '', updated_at: '' },
  { id: '5', user_id: '', date: BASE_DATE, start_time: T(11, 20), end_time: T(11, 30), label: 'Quick research', description: 'Looking up API docs', category: 'Research', color: '#F59E0B', source: 'demo', source_summary: null, confidence: null, edited_by_user: false, created_at: '', updated_at: '' },
  { id: '6', user_id: '', date: BASE_DATE, start_time: T(11, 30), end_time: T(12, 0), label: 'YouTube & Reddit', description: 'Distracted browsing', category: 'Entertainment', color: '#EF4444', source: 'demo', source_summary: null, confidence: null, edited_by_user: false, created_at: '', updated_at: '' },
]

const demoCategories = [
  { category: 'Work', minutes: 180, avgScore: 72, color: '#3B82F6' },
  { category: 'Communication', minutes: 60, avgScore: 45, color: '#8B5CF6' },
  { category: 'Research', minutes: 40, avgScore: 68, color: '#F59E0B' },
  { category: 'Entertainment', minutes: 30, avgScore: 22, color: '#EF4444' },
]

interface Section { id: string; label: string }
interface Page { key: string; title: string; sections: Section[] }

const pages = computed<Page[]>(() => [
  {
    key: 'idea',
    title: t('guide.pages.idea'),
    sections: [
      { id: 'idea-problem', label: t('guide.sections.ideaProblem') },
      { id: 'idea-solution', label: t('guide.sections.ideaSolution') },
      { id: 'idea-philosophy', label: t('guide.sections.ideaPhilosophy') },
    ],
  },
  {
    key: 'curve',
    title: t('guide.pages.curve'),
    sections: [
      { id: 'curve-overview', label: t('guide.sections.curveOverview') },
      { id: 'curve-demo', label: t('guide.sections.curveSeeIt') },
    ],
  },
  {
    key: 'scoring',
    title: t('guide.pages.scoring'),
    sections: [
      { id: 'scoring-focus', label: t('guide.sections.scoringFocus') },
      { id: 'scoring-depth', label: t('guide.sections.scoringDepth') },
      { id: 'scoring-formula', label: t('guide.sections.scoringFormula') },
    ],
  },
  {
    key: 'categories',
    title: t('guide.pages.categories'),
    sections: [
      { id: 'cat-question', label: t('guide.sections.catQuestion') },
      { id: 'cat-distinction', label: t('guide.sections.catDistinction') },
      { id: 'cat-yours', label: t('guide.sections.catYours') },
      { id: 'cat-rules', label: t('guide.sections.catRules') },
      { id: 'cat-flag', label: t('guide.sections.catFlag') },
      { id: 'cat-chart', label: t('guide.sections.catChart') },
    ],
  },
  {
    key: 'dashboard',
    title: t('guide.pages.dashboard'),
    sections: [
      { id: 'dash-numbers', label: t('guide.sections.dashNumbers') },
      { id: 'dash-time', label: t('guide.sections.dashTime') },
      { id: 'dash-aggregation', label: t('guide.sections.dashAggregation') },
      { id: 'dash-heatmap', label: t('guide.sections.dashHeatmap') },
      { id: 'dash-narrative', label: t('guide.sections.dashNarrative') },
    ],
  },
  {
    key: 'timeline',
    title: t('guide.pages.timeline'),
    sections: [
      { id: 'tl-raw', label: t('guide.sections.tlRaw') },
      { id: 'tl-ai', label: t('guide.sections.tlAi') },
      { id: 'tl-loop', label: t('guide.sections.tlLoop') },
    ],
  },
  {
    key: 'agent',
    title: t('guide.pages.agent'),
    sections: [
      { id: 'agent-what', label: t('guide.sections.agentWhat') },
      { id: 'agent-talk', label: t('guide.sections.agentTalk') },
      { id: 'agent-memory', label: t('guide.sections.agentMemory') },
    ],
  },
  {
    key: 'integrations',
    title: t('guide.pages.integrations'),
    sections: [
      { id: 'int-why', label: t('guide.sections.intWhy') },
      { id: 'int-current', label: t('guide.sections.intCurrent') },
      { id: 'int-planned', label: t('guide.sections.intPlanned') },
    ],
  },
  {
    key: 'security',
    title: t('guide.pages.security'),
    sections: [
      { id: 'sec-concern', label: t('guide.sections.secConcern') },
      { id: 'sec-collect', label: t('guide.sections.secCollect') },
      { id: 'sec-llm', label: t('guide.sections.secLlm') },
      { id: 'sec-open', label: t('guide.sections.secOpen') },
    ],
  },
  {
    key: 'conclusion',
    title: t('guide.pages.conclusion'),
    sections: [
      { id: 'end-summary', label: t('guide.sections.endSummary') },
      { id: 'end-references', label: t('guide.sections.endReferences') },
    ],
  },
])

const activePage = ref(pages.value[0].key)
const activeSection = ref('')
const contentRef = ref<HTMLElement | null>(null)

const currentPage = computed(() => pages.value.find((p) => p.key === activePage.value) ?? pages.value[0])

function selectPage(key: string) {
  activePage.value = key
  activeSection.value = ''
  router.replace({ name: 'guide', params: { page: key } })
  nextTick(() => {
    if (contentRef.value) contentRef.value.scrollTop = 0
  })
}

function scrollToSection(id: string) {
  const el = document.getElementById(id)
  if (el && contentRef.value) {
    const offset = el.offsetTop - contentRef.value.offsetTop
    contentRef.value.scrollTo({ top: offset - 16, behavior: 'smooth' })
  }
}

function onContentScroll() {
  if (!contentRef.value) return
  const scrollTop = contentRef.value.scrollTop + 60
  const secs = currentPage.value.sections
  for (let i = secs.length - 1; i >= 0; i--) {
    const el = document.getElementById(secs[i].id)
    if (el) {
      const offset = el.offsetTop - contentRef.value.offsetTop
      if (offset <= scrollTop) {
        activeSection.value = secs[i].id
        return
      }
    }
  }
  activeSection.value = secs[0]?.id ?? ''
}

function onContentClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.tagName === 'A' && target.dataset.page) {
    e.preventDefault()
    selectPage(target.dataset.page)
  }
}

onMounted(() => {
  const pageParam = route.params.page as string
  if (pageParam && pages.value.some((p) => p.key === pageParam)) {
    activePage.value = pageParam
  }
})

watch(activePage, () => {
  nextTick(() => {
    activeSection.value = currentPage.value.sections[0]?.id ?? ''
  })
}, { immediate: true })
</script>

<template>
  <div class="docs-layout">
    <nav class="docs-pages">
      <div class="docs-pages-title">{{ t('guide.docTitle') }}</div>
      <a
        v-for="p in pages"
        :key="p.key"
        class="docs-page-link"
        :class="{ active: activePage === p.key }"
        @click.prevent="selectPage(p.key)"
      >{{ p.title }}</a>
    </nav>

    <div ref="contentRef" class="docs-content" @scroll="onContentScroll" @click="onContentClick">

      <template v-if="activePage === 'idea'">
        <div class="hero">
          <h1>{{ t('guide.idea.heroTitle') }}</h1>
          <p class="tagline">{{ t('guide.idea.tagline') }}</p>
        </div>

        <h2 id="idea-problem" class="idea-section">{{ t('guide.idea.problemTitle') }}</h2>
        <div class="question-cascade">
          <p>{{ t('guide.idea.problemQ1') }}</p>
          <p v-html="t('guide.idea.problemQ2')"></p>
          <p v-html="t('guide.idea.problemQ3')"></p>
          <p class="question-standalone" v-html="t('guide.idea.problemQ4')"></p>
          <p>{{ t('guide.idea.problemQ5') }}</p>
          <p v-html="t('guide.idea.problemQ6')"></p>
        </div>
        <p class="accent-line">{{ t('guide.idea.accentSolve') }}</p>

        <h2 id="idea-solution" class="idea-section">{{ t('guide.idea.solutionTitle') }}</h2>
        <p>{{ t('guide.idea.solutionP1') }}</p>
        <p v-html="t('guide.idea.solutionP2')"></p>
        <p v-html="t('guide.idea.solutionP3')"></p>

        <h2 id="idea-philosophy" class="idea-section">{{ t('guide.idea.philosophyTitle') }}</h2>
        <p class="manifesto-line">{{ t('guide.idea.philosophyManifesto') }}</p>
        <p v-html="t('guide.idea.philosophyP1')"></p>
        <p>{{ t('guide.idea.philosophyP2') }}</p>
        <div class="score-hero">
          <span class="score-number">{{ t('guide.idea.scoreNumber') }}</span>
          <span class="score-caption">{{ t('guide.idea.scoreCaption') }}</span>
        </div>
        <p>{{ t('guide.idea.philosophyP3') }}</p>
        <p class="accent-line">{{ t('guide.idea.accentImpossible') }}</p>
        <p>{{ t('guide.idea.philosophyP4') }}</p>
        <p class="manifesto-line closing">{{ t('guide.idea.philosophyClosing') }}</p>
      </template>

      <template v-if="activePage === 'curve'">
        <h1>{{ t('guide.curve.title') }}</h1>
        <h2 id="curve-overview">{{ t('guide.curve.overviewTitle') }}</h2>
        <p>{{ t('guide.curve.overviewP1') }}</p>
        <p v-html="t('guide.curve.overviewP2')"></p>
        <p>{{ t('guide.curve.overviewP3') }}</p>
        <p v-html="t('guide.curve.overviewP4')"></p>

        <h2 id="curve-demo">{{ t('guide.curve.seeItTitle') }}</h2>
        <p>{{ t('guide.curve.seeItP1') }}</p>
        <div class="demo-chart">
          <ProductivityCurve key="demo-curve" :points="demoPoints" :entries="demoEntries" />
        </div>
      </template>

      <template v-if="activePage === 'scoring'">
        <h1>{{ t('guide.scoring.title') }}</h1>
        <h2 id="scoring-focus">{{ t('guide.scoring.focusTitle') }}</h2>
        <p v-html="t('guide.scoring.focusP1')"></p>
        <p>{{ t('guide.scoring.focusP2') }}</p>
        <p>{{ t('guide.scoring.focusP3') }}</p>
        <table class="info-table">
          <thead><tr><th v-for="h in (t('guide.scoring.focusTableHeader') as unknown as string[])" :key="h">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="(row, i) in (t('guide.scoring.focusTableRows') as unknown as string[][])" :key="i">
              <td :class="{ 'score-high': i < 2, 'score-mid': i === 2, 'score-low': i > 2 }" v-if="row.length > 0">{{ row[0] }}</td>
              <td v-for="(cell, j) in row.slice(1)" :key="j">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
        <p class="note">{{ t('guide.scoring.focusNote') }}</p>

        <h2 id="scoring-depth">{{ t('guide.scoring.depthTitle') }}</h2>
        <p v-html="t('guide.scoring.depthP1')"></p>
        <p>{{ t('guide.scoring.depthP2') }}</p>
        <div class="depth-cards">
          <div class="depth-card deep">
            <div class="depth-label">{{ t('guide.scoring.depthDeepLabel') }}</div>
            <div class="depth-weight">{{ t('guide.scoring.depthDeepWeight') }}</div>
            <p>{{ t('guide.scoring.depthDeepDesc') }}</p>
          </div>
          <div class="depth-card shallow">
            <div class="depth-label">{{ t('guide.scoring.depthShallowLabel') }}</div>
            <div class="depth-weight">{{ t('guide.scoring.depthShallowWeight') }}</div>
            <p>{{ t('guide.scoring.depthShallowDesc') }}</p>
          </div>
          <div class="depth-card reactive">
            <div class="depth-label">{{ t('guide.scoring.depthReactiveLabel') }}</div>
            <div class="depth-weight">{{ t('guide.scoring.depthReactiveWeight') }}</div>
            <p>{{ t('guide.scoring.depthReactiveDesc') }}</p>
          </div>
        </div>

        <h2 id="scoring-formula">{{ t('guide.scoring.formulaTitle') }}</h2>
        <p class="formula">{{ t('guide.scoring.formula') }}</p>
        <p>{{ t('guide.scoring.formulaP1') }}</p>
        <p>{{ t('guide.scoring.formulaP2') }}</p>
        <table class="info-table">
          <thead><tr><th v-for="h in (t('guide.scoring.formulaTableHeader') as unknown as string[])" :key="h">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="(row, i) in (t('guide.scoring.formulaTableRows') as unknown as string[][])" :key="i">
              <td v-for="(cell, j) in row" :key="j" :class="{ 'score-high': j === row.length - 1 && Number(cell) >= 70, 'score-mid': j === row.length - 1 && Number(cell) >= 50 && Number(cell) < 70, 'score-low': j === row.length - 1 && Number(cell) < 50 }">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
        <p>{{ t('guide.scoring.formulaP3') }}</p>
      </template>

      <template v-if="activePage === 'categories'">
        <h1>{{ t('guide.categories.title') }}</h1>
        <h2 id="cat-question">{{ t('guide.categories.questionTitle') }}</h2>
        <p v-html="t('guide.categories.questionP1')"></p>
        <p>{{ t('guide.categories.questionP2') }}</p>
        <p class="accent-line">{{ t('guide.categories.questionAccent') }}</p>

        <h2 id="cat-distinction">{{ t('guide.categories.distinctionTitle') }}</h2>
        <p v-html="t('guide.categories.distinctionP1')"></p>
        <p v-html="t('guide.categories.distinctionP2')"></p>
        <p>{{ t('guide.categories.distinctionP3') }}</p>
        <p v-html="t('guide.categories.distinctionP4')"></p>
        <p>{{ t('guide.categories.distinctionP5') }}</p>

        <h2 id="cat-yours">{{ t('guide.categories.yoursTitle') }}</h2>
        <p v-html="t('guide.categories.yoursP1')"></p>
        <div class="example-categories">
          <div v-for="cat in (t('guide.categories.defaultCategories') as unknown as any[])" :key="cat.name" class="example-cat">
            <span class="cat-dot" :style="{ background: cat.color }"></span>
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-flag" :class="cat.flag === 'work' ? 'work' : 'not-work'">{{ cat.flag }}</span>
          </div>
        </div>
        <p>{{ t('guide.categories.yoursP2') }}</p>
        <div class="example-categories custom">
          <div v-for="cat in (t('guide.categories.customCategories') as unknown as any[])" :key="cat.name" class="example-cat">
            <span class="cat-dot" :style="{ background: cat.color }"></span>
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-flag" :class="cat.flag === 'work' ? 'work' : 'not-work'">{{ cat.flag }}</span>
          </div>
        </div>

        <h2 id="cat-rules">{{ t('guide.categories.rulesTitle') }}</h2>
        <p v-html="t('guide.categories.rulesP1')"></p>
        <div class="example-rules">
          <div v-for="(rule, i) in (t('guide.categories.exampleRules') as unknown as string[])" :key="i" class="example-rule">{{ rule }}</div>
        </div>
        <p v-html="t('guide.categories.rulesP2')"></p>

        <h2 id="cat-flag">{{ t('guide.categories.flagTitle') }}</h2>
        <p>{{ t('guide.categories.flagP1') }}</p>
        <ul>
          <li v-html="t('guide.categories.flagProductivity')"></li>
          <li v-html="t('guide.categories.flagPerformance')"></li>
        </ul>
        <p>{{ t('guide.categories.flagP2') }}</p>

        <h2 id="cat-chart">{{ t('guide.categories.chartTitle') }}</h2>
        <p>{{ t('guide.categories.chartP1') }}</p>
        <div class="demo-categories">
          <CategoryBreakdownChart :items="demoCategories" />
        </div>
      </template>

      <template v-if="activePage === 'dashboard'">
        <h1>{{ t('guide.dashboard.title') }}</h1>
        <h2 id="dash-numbers">{{ t('guide.dashboard.numbersTitle') }}</h2>
        <p>{{ t('guide.dashboard.numbersP1') }}</p>
        <div class="metrics-explainer">
          <div class="metric-explain">
            <div class="metric-ex-value">{{ (t('guide.dashboard.metricActive') as unknown as any).value }}</div>
            <div class="metric-ex-label">{{ (t('guide.dashboard.metricActive') as unknown as any).label }}</div>
            <div class="metric-ex-desc">{{ (t('guide.dashboard.metricActive') as unknown as any).desc }}</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">{{ (t('guide.dashboard.metricWorkTime') as unknown as any).value }}</div>
            <div class="metric-ex-label">{{ (t('guide.dashboard.metricWorkTime') as unknown as any).label }}</div>
            <div class="metric-ex-desc" v-html="(t('guide.dashboard.metricWorkTime') as unknown as any).desc"></div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">{{ (t('guide.dashboard.metricDeepWork') as unknown as any).value }}</div>
            <div class="metric-ex-label">{{ (t('guide.dashboard.metricDeepWork') as unknown as any).label }}</div>
            <div class="metric-ex-desc" v-html="(t('guide.dashboard.metricDeepWork') as unknown as any).desc"></div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">{{ (t('guide.dashboard.metricFocus') as unknown as any).value }}</div>
            <div class="metric-ex-label">{{ (t('guide.dashboard.metricFocus') as unknown as any).label }}</div>
            <div class="metric-ex-desc">{{ (t('guide.dashboard.metricFocus') as unknown as any).desc }}</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">{{ (t('guide.dashboard.metricBestStreak') as unknown as any).value }}</div>
            <div class="metric-ex-label">{{ (t('guide.dashboard.metricBestStreak') as unknown as any).label }}</div>
            <div class="metric-ex-desc">{{ (t('guide.dashboard.metricBestStreak') as unknown as any).desc }}</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">{{ (t('guide.dashboard.metricSwitches') as unknown as any).value }}</div>
            <div class="metric-ex-label">{{ (t('guide.dashboard.metricSwitches') as unknown as any).label }}</div>
            <div class="metric-ex-desc">{{ (t('guide.dashboard.metricSwitches') as unknown as any).desc }}</div>
          </div>
        </div>
        <p v-html="t('guide.dashboard.numbersP2')"></p>

        <h2 id="dash-time">{{ t('guide.dashboard.timeTitle') }}</h2>
        <p>{{ t('guide.dashboard.timeP1') }}</p>
        <p v-html="t('guide.dashboard.timeP2')"></p>
        <p>{{ t('guide.dashboard.timeP3') }}</p>

        <h2 id="dash-aggregation">{{ t('guide.dashboard.aggregationTitle') }}</h2>
        <p>{{ t('guide.dashboard.aggregationP1') }}</p>
        <table class="info-table">
          <thead><tr><th v-for="h in (t('guide.dashboard.aggregationTableHeader') as unknown as string[])" :key="h">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="(row, i) in (t('guide.dashboard.aggregationTableRows') as unknown as string[][])" :key="i">
              <td v-for="(cell, j) in row" :key="j" v-html="cell"></td>
            </tr>
          </tbody>
        </table>

        <h2 id="dash-heatmap">{{ t('guide.dashboard.heatmapTitle') }}</h2>
        <p v-html="t('guide.dashboard.heatmapP1')"></p>
        <p>{{ t('guide.dashboard.heatmapP2') }}</p>

        <h2 id="dash-narrative">{{ t('guide.dashboard.narrativeTitle') }}</h2>
        <p v-html="t('guide.dashboard.narrativeP1')"></p>
        <p>{{ t('guide.dashboard.narrativeP2') }}</p>
      </template>

      <template v-if="activePage === 'timeline'">
        <h1>{{ t('guide.timeline.title') }}</h1>
        <h2 id="tl-raw">{{ t('guide.timeline.rawTitle') }}</h2>
        <p>{{ t('guide.timeline.rawP1') }}</p>
        <p>{{ t('guide.timeline.rawP2') }}</p>
        <div class="event-log">
          <div v-for="(ev, i) in (t('guide.timeline.eventLog') as unknown as any[])" :key="i" class="event-line" :class="{ dim: ev.dim }">
            <span class="ev-time">{{ ev.time }}</span><span class="ev-app">{{ ev.app }}</span><span class="ev-detail">{{ ev.detail }}</span>
          </div>
          <div class="event-line dim"><span class="ev-time">…</span><span class="ev-app"></span><span class="ev-detail"></span></div>
        </div>
        <p v-html="t('guide.timeline.rawP3')"></p>

        <h2 id="tl-ai">{{ t('guide.timeline.aiTitle') }}</h2>
        <p>{{ t('guide.timeline.aiP1') }}</p>
        <div class="timeline-demo">
          <div v-for="(entry, i) in (t('guide.timeline.timelineEntries') as unknown as any[])" :key="i" class="tl-entry" :style="{ borderLeftColor: entry.color }">
            <span class="tl-time">{{ entry.time }}</span>
            <span class="tl-label">{{ entry.label }}</span>
          </div>
        </div>
        <p>{{ t('guide.timeline.aiP2') }}</p>
        <p v-html="t('guide.timeline.aiP3')"></p>
        <p v-html="t('guide.timeline.aiP4')"></p>

        <h2 id="tl-loop">{{ t('guide.timeline.loopTitle') }}</h2>
        <p>{{ t('guide.timeline.loopP1') }}</p>
        <p>{{ t('guide.timeline.loopP2') }}</p>
        <p v-html="t('guide.timeline.loopP3')"></p>
      </template>

      <template v-if="activePage === 'agent'">
        <h1>{{ t('guide.agent.title') }}</h1>
        <h2 id="agent-what">{{ t('guide.agent.whatTitle') }}</h2>
        <p v-html="t('guide.agent.whatP1')"></p>
        <p>{{ t('guide.agent.whatP2') }}</p>
        <p class="accent-line">{{ t('guide.agent.whatAccent') }}</p>

        <h2 id="agent-talk">{{ t('guide.agent.talkTitle') }}</h2>
        <p v-html="t('guide.agent.talkP1')"></p>
        <div class="chat-examples">
          <div v-for="(msg, i) in (t('guide.agent.chatExamples') as unknown as any[])" :key="i" class="chat-bubble" :class="msg.role">{{ msg.text }}</div>
        </div>
        <p>{{ t('guide.agent.talkP2') }}</p>

        <h2 id="agent-memory">{{ t('guide.agent.memoryTitle') }}</h2>
        <p>{{ t('guide.agent.memoryP1') }}</p>
        <div class="chat-examples">
          <div v-for="(msg, i) in (t('guide.agent.memoryExamples') as unknown as any[])" :key="i" class="chat-bubble" :class="msg.role">{{ msg.text }}</div>
        </div>
        <p>{{ t('guide.agent.memoryP2') }}</p>
      </template>

      <template v-if="activePage === 'integrations'">
        <h1>{{ t('guide.integrations.title') }}</h1>
        <h2 id="int-why">{{ t('guide.integrations.whyTitle') }}</h2>
        <p>{{ t('guide.integrations.whyP1') }}</p>
        <p>{{ t('guide.integrations.whyP2') }}</p>
        <p v-html="t('guide.integrations.whyP3')"></p>

        <h2 id="int-current">{{ t('guide.integrations.currentTitle') }}</h2>
        <div class="integration-list">
          <div class="integration-card">
            <div class="int-header">
              <span class="int-name">{{ (t('guide.integrations.telegram') as unknown as any).name }}</span>
              <span class="int-badge live">{{ (t('guide.integrations.telegram') as unknown as any).badge }}</span>
            </div>
            <p>{{ (t('guide.integrations.telegram') as unknown as any).desc }}</p>
          </div>
        </div>

        <h2 id="int-planned">{{ t('guide.integrations.plannedTitle') }}</h2>
        <p>{{ t('guide.integrations.plannedP1') }}</p>
        <div class="integration-list">
          <div v-for="int in (t('guide.integrations.plannedIntegrations') as unknown as any[])" :key="int.name" class="integration-card planned">
            <div class="int-header">
              <span class="int-name">{{ int.name }}</span>
              <span class="int-badge planned">{{ t('guide.integrations.plannedTitle').toLowerCase() }}</span>
            </div>
            <p>{{ int.desc }}</p>
          </div>
        </div>
      </template>

      <template v-if="activePage === 'security'">
        <h1>{{ t('guide.security.title') }}</h1>
        <h2 id="sec-concern">{{ t('guide.security.concernTitle') }}</h2>
        <p>{{ t('guide.security.concernP1') }}</p>
        <p>{{ t('guide.security.concernP2') }}</p>

        <h2 id="sec-collect">{{ t('guide.security.collectTitle') }}</h2>
        <p>{{ t('guide.security.collectP1') }}</p>
        <ul>
          <li v-for="(item, i) in (t('guide.security.collectItems') as unknown as string[])" :key="i" v-html="item"></li>
        </ul>
        <p>{{ t('guide.security.collectP2') }}</p>

        <h2 id="sec-llm">{{ t('guide.security.llmTitle') }}</h2>
        <p v-html="t('guide.security.llmP1')"></p>
        <p>{{ t('guide.security.llmP2') }}</p>
        <p>{{ t('guide.security.llmP3') }}</p>

        <h2 id="sec-open">{{ t('guide.security.openTitle') }}</h2>
        <p>{{ t('guide.security.openP1') }}</p>
        <p class="github-cta">
          <a :href="t('guide.security.githubUrl') as unknown as string" target="_blank" rel="noopener" class="github-link">
            <svg viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            {{ t('guide.security.githubRepo') }}
          </a>
        </p>
        <p>{{ t('guide.security.openP2') }}</p>
        <p>{{ t('guide.security.openP3') }}</p>
        <p>{{ t('guide.security.openP4') }}</p>
      </template>

      <template v-if="activePage === 'conclusion'">
        <h1>{{ t('guide.conclusion.title') }}</h1>
        <h2 id="end-summary">{{ t('guide.conclusion.summaryTitle') }}</h2>
        <p>{{ t('guide.conclusion.summaryP1') }}</p>
        <p v-html="t('guide.conclusion.summaryP2')"></p>
        <p v-html="t('guide.conclusion.summaryP3')"></p>
        <p>{{ t('guide.conclusion.summaryP4') }}</p>
        <p class="manifesto-line closing" style="margin-top: 32px">{{ t('guide.conclusion.summaryClosing') }}</p>

        <h2 id="end-references">{{ t('guide.conclusion.referencesTitle') }}</h2>
        <p>{{ t('guide.conclusion.referencesIntro') }}</p>
        <div class="references">
          <p v-for="(ref, i) in (t('guide.conclusion.references') as unknown as any[])" :key="i">
            {{ ref.authors }} <em>{{ ref.title }}</em> {{ ref.detail }}
          </p>
        </div>
      </template>

    </div>

    <nav class="docs-toc">
      <div class="docs-toc-title">{{ t('guide.onThisPage') }}</div>
      <a
        v-for="s in currentPage.sections"
        :key="s.id"
        class="docs-toc-link"
        :class="{ active: activeSection === s.id }"
        @click.prevent="scrollToSection(s.id)"
      >{{ s.label }}</a>
    </nav>
  </div>
</template>

<style scoped>
.docs-layout {
  display: flex;
  gap: 0;
  height: 100%;
}

.docs-pages {
  width: 190px;
  flex-shrink: 0;
  padding: 8px 16px 24px 0;
  border-right: 1px solid rgba(150, 150, 150, 0.1);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.docs-pages-title {
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.4;
  margin-bottom: 10px;
}

.docs-page-link {
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 5px;
  cursor: pointer;
  opacity: 0.55;
  transition: opacity 0.15s, background 0.15s;
  text-decoration: none;
  color: inherit;
}

.docs-page-link:hover {
  opacity: 0.85;
  background: rgba(150, 150, 150, 0.08);
}

.docs-page-link.active {
  opacity: 1;
  background: rgba(150, 150, 150, 0.1);
  font-weight: 600;
}

.docs-content {
  flex: 1;
  min-width: 0;
  padding: 0 40px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.7;
}

.docs-content h1 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 20px;
}

.docs-content h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 32px 0 10px;
  padding-top: 8px;
}

.docs-content h2:first-of-type {
  margin-top: 0;
}

.docs-content h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 20px 0 8px;
}

.docs-content p {
  margin: 0 0 12px;
}

.docs-content ul {
  margin: 0 0 12px;
  padding-left: 20px;
}

.docs-content li {
  margin-bottom: 4px;
}

.docs-toc {
  width: 160px;
  flex-shrink: 0;
  padding: 8px 0 24px 16px;
  border-left: 1px solid rgba(150, 150, 150, 0.1);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.docs-toc-title {
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.4;
  margin-bottom: 8px;
}

.docs-toc-link {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.45;
  transition: opacity 0.15s, background 0.15s;
  text-decoration: none;
  color: inherit;
}

.docs-toc-link:hover {
  opacity: 0.8;
  background: rgba(150, 150, 150, 0.08);
}

.docs-toc-link.active {
  opacity: 1;
  background: rgba(150, 150, 150, 0.1);
  font-weight: 600;
}

.hero {
  text-align: center;
  padding: 24px 0 16px;
  margin-bottom: 8px;
}

.hero h1 {
  font-size: 40px;
  font-weight: 800;
  letter-spacing: 8px;
  margin: 0;
}

.hero .tagline {
  font-size: 14px;
  opacity: 0.4;
  margin: 8px 0 0;
  letter-spacing: 1px;
}

.idea-section {
  margin-top: 48px !important;
}

.question-cascade {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-cascade p {
  font-size: 15px;
  line-height: 1.8;
  margin: 0;
}

.question-cascade p:nth-child(1) { opacity: 0.5; }
.question-cascade p:nth-child(2) { opacity: 0.6; }
.question-cascade p:nth-child(3) { opacity: 0.7; }
.question-cascade p:nth-child(4) { opacity: 0.85; }
.question-cascade p:nth-child(5) { opacity: 0.9; }
.question-cascade p:nth-child(6) { opacity: 1; }

.question-standalone {
  margin-top: 8px !important;
  font-size: 16px !important;
  font-weight: 600;
}

.accent-line {
  font-size: 19px;
  font-weight: 700;
  text-align: center;
  padding: 28px 0;
  letter-spacing: 0.3px;
  position: relative;
}

.accent-line::before {
  content: '';
  display: block;
  width: 40px;
  height: 2px;
  background: rgba(255, 255, 255, 0.25);
  margin: 0 auto 20px;
}

.score-hero {
  text-align: center;
  padding: 32px 0;
}

.score-hero .score-number {
  display: block;
  font-size: 56px;
  font-weight: 800;
  color: #22C55E;
  line-height: 1;
  text-shadow: 0 0 40px rgba(34, 197, 94, 0.3), 0 0 80px rgba(34, 197, 94, 0.1);
}

.score-hero .score-caption {
  display: block;
  font-size: 13px;
  opacity: 0.4;
  margin-top: 10px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.manifesto-line {
  font-size: 16px;
  font-weight: 600;
  border-left: 3px solid #EF4444;
  padding-left: 16px;
  margin: 20px 0;
}

.manifesto-line.closing {
  border-left-color: rgba(255, 255, 255, 0.2);
  opacity: 0.7;
  margin-top: 24px;
}

.page-link {
  color: var(--to-brand, #3B82F6);
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
  transition: opacity 0.15s;
}

.page-link:hover {
  opacity: 0.7;
}

.note {
  font-size: 13px;
  opacity: 0.6;
  font-style: italic;
}

.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin: 12px 0;
}

.info-table th {
  text-align: left;
  font-weight: 600;
  padding: 6px 10px;
  border-bottom: 1px solid rgba(150, 150, 150, 0.15);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.5;
}

.info-table td {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(150, 150, 150, 0.06);
}

.score-high { color: #22C55E; font-weight: 700; }
.score-mid { color: #EAB308; font-weight: 700; }
.score-low { color: #EF4444; font-weight: 700; }

.depth-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 12px 0;
}

.depth-card {
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
}

.depth-card p { margin: 6px 0 4px; }
.depth-card.deep { background: rgba(59, 130, 246, 0.1); border-left: 3px solid #3B82F6; }
.depth-card.shallow { background: rgba(234, 179, 8, 0.1); border-left: 3px solid #EAB308; }
.depth-card.reactive { background: rgba(239, 68, 68, 0.1); border-left: 3px solid #EF4444; }
.depth-label { font-weight: 700; font-size: 14px; }
.depth-weight { font-size: 12px; opacity: 0.5; font-weight: 600; }

.formula {
  font-family: monospace;
  font-size: 16px;
  font-weight: 600;
  padding: 12px 16px;
  background: rgba(150, 150, 150, 0.06);
  border-radius: 6px;
  text-align: center;
  margin-bottom: 12px;
}

.demo-chart { margin: 16px 0 24px; }

.demo-categories {
  max-width: 350px;
  margin: 16px auto 24px;
}

.metrics-explainer {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.metric-explain {
  text-align: center;
  padding: 12px 8px;
  border-radius: 8px;
  background: rgba(150, 150, 150, 0.04);
}

.metric-ex-value { font-size: 22px; font-weight: 700; color: var(--to-brand); }
.metric-ex-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.5; margin: 4px 0; font-weight: 600; }
.metric-ex-desc { font-size: 12px; line-height: 1.4; opacity: 0.6; }

.event-log {
  background: #1a1a2e;
  border-radius: 8px;
  padding: 14px 16px;
  margin: 12px 0 16px;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.9;
  overflow-x: auto;
}

.event-line {
  display: flex;
  gap: 12px;
  white-space: nowrap;
}

.event-line.dim {
  opacity: 0.35;
}

.ev-time {
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
  width: 62px;
}

.ev-app {
  color: #22C55E;
  flex-shrink: 0;
  width: 70px;
}

.ev-detail {
  color: rgba(255, 255, 255, 0.55);
}

.timeline-demo {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 12px 0 16px;
}

.tl-entry {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 8px 14px;
  border-left: 3px solid;
  background: rgba(150, 150, 150, 0.04);
  border-radius: 0 6px 6px 0;
}

.tl-time {
  font-size: 12px;
  font-family: monospace;
  opacity: 0.4;
  flex-shrink: 0;
}

.tl-label {
  font-size: 13px;
  font-weight: 500;
}

.chat-examples {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
}

.chat-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  max-width: 85%;
}

.chat-bubble.user {
  background: rgba(59, 130, 246, 0.12);
  align-self: flex-end;
  font-style: italic;
}

.chat-bubble.agent {
  background: rgba(150, 150, 150, 0.08);
  align-self: flex-start;
  opacity: 0.7;
  font-size: 12px;
}

.integration-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 16px 0;
}

.integration-card {
  padding: 14px 16px;
  border-radius: 8px;
  background: rgba(150, 150, 150, 0.04);
  border: 1px solid rgba(150, 150, 150, 0.08);
}

.integration-card.planned {
  opacity: 0.6;
}

.integration-card p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.5;
}

.int-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.int-name {
  font-weight: 700;
  font-size: 14px;
}

.int-badge {
  font-size: 10px;
  padding: 2px 7px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
}

.int-badge.live {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.int-badge.planned {
  background: rgba(150, 150, 150, 0.12);
  color: inherit;
  opacity: 0.5;
}

.github-cta {
  text-align: center;
  margin: 20px 0;
}

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  background: rgba(150, 150, 150, 0.08);
  border: 1px solid rgba(150, 150, 150, 0.12);
  color: inherit;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.15s;
}

.github-link:hover {
  background: rgba(150, 150, 150, 0.15);
}

.example-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0;
}

.example-categories.custom {
  margin-top: 12px;
}

.example-cat {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(150, 150, 150, 0.06);
  font-size: 13px;
}

.cat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cat-name {
  font-weight: 600;
}

.cat-flag {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.cat-flag.work {
  background: rgba(34, 197, 94, 0.12);
  color: #22C55E;
}

.cat-flag.not-work {
  background: rgba(239, 68, 68, 0.12);
  color: #EF4444;
}

.example-rules {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 16px 0;
}

.example-rule {
  font-size: 13px;
  font-style: italic;
  padding: 8px 14px;
  border-left: 2px solid rgba(150, 150, 150, 0.15);
  opacity: 0.7;
}

.references p {
  font-size: 12px;
  opacity: 0.6;
  margin-bottom: 6px;
}

@media (max-width: 900px) {
  .docs-toc { display: none; }
}

@media (max-width: 640px) {
  .docs-pages { display: none; }
  .depth-cards { grid-template-columns: 1fr; }
  .metrics-explainer { grid-template-columns: repeat(2, 1fr); }
}
</style>
