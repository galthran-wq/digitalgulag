<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ProductivityCurve from '@/components/ProductivityCurve.vue'
import CategoryBreakdownChart from '@/components/CategoryBreakdownChart.vue'
import type { ProductivityPoint } from '@/types/productivityCurve'
import type { TimelineEntry } from '@/types/timeline'

const route = useRoute()
const router = useRouter()

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

const pages: Page[] = [
  {
    key: 'idea',
    title: 'The Idea',
    sections: [
      { id: 'idea-problem', label: 'The Problem' },
      { id: 'idea-solution', label: 'The Solution' },
      { id: 'idea-philosophy', label: 'The Philosophy' },
    ],
  },
  {
    key: 'curve',
    title: 'Productivity Curve',
    sections: [
      { id: 'curve-overview', label: 'Overview' },
      { id: 'curve-demo', label: 'See It' },
    ],
  },
  {
    key: 'scoring',
    title: 'Scoring',
    sections: [
      { id: 'scoring-focus', label: 'Focus' },
      { id: 'scoring-depth', label: 'Depth' },
      { id: 'scoring-formula', label: 'The Formula' },
    ],
  },
  {
    key: 'categories',
    title: 'What Counts as Work',
    sections: [
      { id: 'cat-question', label: 'The Question' },
      { id: 'cat-distinction', label: 'Two Different Things' },
      { id: 'cat-yours', label: 'You Define It' },
      { id: 'cat-rules', label: 'Classification Rules' },
      { id: 'cat-flag', label: 'Work vs. Not Work' },
      { id: 'cat-chart', label: 'The Breakdown' },
    ],
  },
  {
    key: 'dashboard',
    title: 'The Dashboard',
    sections: [
      { id: 'dash-numbers', label: 'The Numbers' },
      { id: 'dash-time', label: 'Time Scales' },
      { id: 'dash-aggregation', label: 'How We Aggregate' },
      { id: 'dash-heatmap', label: 'Heatmap' },
      { id: 'dash-narrative', label: 'Narrative' },
    ],
  },
  {
    key: 'timeline',
    title: 'The Timeline',
    sections: [
      { id: 'tl-raw', label: 'What We See' },
      { id: 'tl-ai', label: 'What You See' },
      { id: 'tl-loop', label: 'The Loop' },
    ],
  },
  {
    key: 'agent',
    title: 'The Agent',
    sections: [
      { id: 'agent-what', label: 'What It Does' },
      { id: 'agent-talk', label: 'Talk To It' },
      { id: 'agent-memory', label: 'Memory' },
    ],
  },
  {
    key: 'integrations',
    title: 'Integrations',
    sections: [
      { id: 'int-why', label: 'Why More Data' },
      { id: 'int-current', label: 'Available Now' },
      { id: 'int-planned', label: 'Planned' },
    ],
  },
  {
    key: 'security',
    title: 'Security',
    sections: [
      { id: 'sec-concern', label: 'The Concern' },
      { id: 'sec-collect', label: 'What We Collect' },
      { id: 'sec-llm', label: 'The LLM Question' },
      { id: 'sec-open', label: 'Open Source' },
    ],
  },
  {
    key: 'conclusion',
    title: 'Conclusion',
    sections: [
      { id: 'end-summary', label: 'The Point' },
      { id: 'end-references', label: 'References' },
    ],
  },
]

const activePage = ref(pages[0].key)
const activeSection = ref('')
const contentRef = ref<HTMLElement | null>(null)

const currentPage = computed(() => pages.find((p) => p.key === activePage.value) ?? pages[0])

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

onMounted(() => {
  const pageParam = route.params.page as string
  if (pageParam && pages.some((p) => p.key === pageParam)) {
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
      <div class="docs-pages-title">Documentation</div>
      <a
        v-for="p in pages"
        :key="p.key"
        class="docs-page-link"
        :class="{ active: activePage === p.key }"
        @click.prevent="selectPage(p.key)"
      >{{ p.title }}</a>
    </nav>

    <div ref="contentRef" class="docs-content" @scroll="onContentScroll">

      <template v-if="activePage === 'idea'">
        <div class="hero">
          <h1>DIGITAL GULAG</h1>
          <p class="tagline">The ultimate productivity monitoring system.</p>
        </div>

        <h2 id="idea-problem" class="idea-section">The Problem</h2>
        <div class="question-cascade">
          <p>
            Have you ever spent an entire day at your computer and had no idea where the time went?
          </p>
          <p>
            Have you noticed you're suddenly out of time — somehow floating through hours without
            anything to show for it? Have you found yourself unable to answer a simple question:
            <strong>what did I actually do today?</strong> What did I do last week? Last month?
          </p>
          <p>
            Have you had days where you were completely off? Unproductive in a way you can feel
            but can't explain? Have you caught yourself <em>trying</em> to find reasons — searching
            for correlations, patterns, anything that would explain why some days work and others don't?
          </p>
          <p class="question-standalone">
            Have you ever wished for someone to just <strong>make</strong> you work?
          </p>
          <p>
            Have you been in that position where you know exactly what you should be doing — but
            you're not doing it? Maybe because it's hard. Maybe because you're lazy. Maybe because
            you're tired. Maybe you don't even know why.
          </p>
          <p>
            Have you found yourself distracted by things that are completely, utterly unimportant?
            Watching TikToks. Scrolling Reddit. Clicking through YouTube rabbit holes. All while
            knowing — <em>knowing</em> — you should be working.
          </p>
        </div>
        <p class="accent-line">
          That is precisely what we are here to solve.
        </p>

        <h2 id="idea-solution" class="idea-section">The Solution</h2>
        <p>
          Digital Gulag measures every aspect of your computer activity — comprehensively,
          continuously, and with zero manual input. A daemon captures what you're doing. AI
          analyzes how well you're doing it. The dashboard shows you the truth.
        </p>
        <p>
          We use state-of-the-art technology and research to assess not just <em>what</em> you
          did, but <em>how effectively</em> you did it. Two people can spend 8 hours in VS Code.
          One produced exceptional work. The other alt-tabbed to Discord every 3 minutes. Traditional
          time trackers call that the same day. We don't.
        </p>
        <p>
          Every 10 minutes, we compute a
          <a class="page-link" @click.prevent="selectPage('scoring')">productivity score</a>
          that captures both your focus quality and the cognitive depth of your work. These scores
          form a
          <a class="page-link" @click.prevent="selectPage('curve')">productivity curve</a>
          — a real-time portrait of your output. Two headline numbers sit at the top:
          <strong>Productivity</strong> (your overall output quality) and
          <strong>Performance</strong> (how well you perform during
          <a class="page-link" @click.prevent="selectPage('categories')">work-flagged</a> activity).
        </p>

        <h2 id="idea-philosophy" class="idea-section">The Philosophy</h2>
        <p class="manifesto-line">
          Our goal is to make you a better person. And by "better" we mean one thing:
          working as hard as possible, for as long as possible.
        </p>
        <p>
          That's where the name comes from. <strong>Digital Gulag</strong> is not a cozy
          productivity companion. It's a monitoring system designed to improve your direct
          performance metric. Your goal, when it comes to us, is to become an ultimate machine.
          An absolute icon of impact.
        </p>
        <p>
          The highest productivity score is:
        </p>
        <div class="score-hero">
          <span class="score-number">100</span>
          <span class="score-caption">16 hours. Zero breaks. Zero distractions.</span>
        </div>
        <p>
          Deep, focused, relentless output from the moment you wake up until you
          physically cannot continue.
        </p>
        <p class="accent-line">
          This metric is, by design, impossible to achieve.
        </p>
        <p>
          We help you get as close as you possibly can.
        </p>
        <p class="manifesto-line closing">
          That is the core principle of the Digital Gulag philosophy.
        </p>
      </template>

      <template v-if="activePage === 'curve'">
        <h1>The Curve</h1>
        <h2 id="curve-overview">Overview</h2>
        <p>
          You think you know how your day went. You don't.
        </p>
        <p>
          The productivity curve is a mirror. It takes every 10 minutes of your computer
          activity and assigns it a <strong>productivity score</strong> from 0 to 100. Then
          it plots them, one after another, across your entire day. What you get is the actual
          shape of your output — not what you remember, not what you felt, but what happened.
        </p>
        <p>
          The ramp-up in the morning when you finally lock in. The crater where you opened
          Slack "for a second." The slow, painful climb back. The scatter at the end when
          you're running on fumes but pretending you're still working. It's all there.
        </p>
        <p>
          Every point is colored by its
          <a class="page-link" @click.prevent="selectPage('categories')">category</a>.
          Every point carries a
          <a class="page-link" @click.prevent="selectPage('scoring')">score</a>
          built from two dimensions: how <strong>focused</strong> you were and how
          <strong>deep</strong> the work was. Hover over any point and the truth is right there —
          what you were doing, how well you were doing it, and what it cost you.
        </p>

        <h2 id="curve-demo">See It</h2>
        <p>
          Three hours of a morning. Deep focus building up, a dip into admin and chat,
          the recovery grind back into real work, then the collapse into distraction.
          This is what a day actually looks like.
        </p>
        <div class="demo-chart">
          <ProductivityCurve key="demo-curve" :points="demoPoints" :entries="demoEntries" />
        </div>
      </template>

      <template v-if="activePage === 'scoring'">
        <h1>Scoring</h1>
        <h2 id="scoring-focus">Focus</h2>
        <p>
          Every 10 minutes, we ask one question: <strong>how concentrated were you?</strong>
        </p>
        <p>
          Not what app you had open. Not how many lines you typed. We look at the pattern —
          your switches, your window changes, your activity rhythm — and we produce a single
          number from 0 to 100. That number is your focus score.
        </p>
        <p>
          A developer who spends 10 minutes in VS Code without touching anything else gets
          a 95. The same developer who checks Discord twice and glances at Reddit gets a 55.
          Same app. Same time. Completely different output. We know the difference.
        </p>
        <table class="info-table">
          <thead><tr><th>Score</th><th>What it means</th><th>What it looks like</th></tr></thead>
          <tbody>
            <tr><td class="score-high">90–100</td><td>Locked in. Near-zero switching.</td><td>10 min in one app, no distractions</td></tr>
            <tr><td class="score-high">70–90</td><td>Focused. Brief relevant switches.</td><td>Coding with a quick doc lookup</td></tr>
            <tr><td class="score-mid">50–70</td><td>Fragmented. You're splitting attention.</td><td>Working but checking chat mid-flow</td></tr>
            <tr><td class="score-low">30–50</td><td>Scattered. More switching than working.</td><td>30–40% of time on unrelated apps</td></tr>
            <tr><td class="score-low">0–30</td><td>Chaos. You're not really here.</td><td>Bouncing between 4–5 apps nonstop</td></tr>
          </tbody>
        </table>
        <p class="note">
          Switching between related tools in the same task — IDE, terminal, docs, back to IDE —
          is normal workflow. That scores 80+. Only unrelated switches hurt you.
        </p>

        <h2 id="scoring-depth">Depth</h2>
        <p>
          Focus tells us how hard you were concentrating. Depth tells us what that concentration
          was <em>worth</em>.
        </p>
        <p>
          You can be 100% focused on organizing your inbox. You can be 100% focused on
          architecting a distributed system. These are not the same thing. Depth captures that.
        </p>
        <div class="depth-cards">
          <div class="depth-card deep">
            <div class="depth-label">Deep</div>
            <div class="depth-weight">1.0×</div>
            <p>The work that matters. Code, design, analysis, debugging. Complex problems that
            require your actual expertise. If someone interrupted you here, it would cost you.</p>
          </div>
          <div class="depth-card shallow">
            <div class="depth-label">Shallow</div>
            <div class="depth-weight">0.6×</div>
            <p>Necessary but replaceable. Email triage, file management, scheduling, admin.
            You could do this half-asleep — and often do.</p>
          </div>
          <div class="depth-card reactive">
            <div class="depth-label">Reactive</div>
            <div class="depth-weight">0.3×</div>
            <p>You're not driving. Chat responses, notifications, support pings.
            Someone else's agenda is controlling your time.</p>
          </div>
        </div>

        <h2 id="scoring-formula">The Formula</h2>
        <p class="formula">Productivity = Focus × Depth × 100</p>
        <p>
          Multiplicative. Not additive. Because that's how reality works.
        </p>
        <p>
          You can be laser-focused on email triage — the task has a ceiling. You can attempt
          deep architecture work while alt-tabbing to Twitter — the focus isn't there to sustain it.
          Both dimensions have to be present. The product captures this naturally.
        </p>
        <table class="info-table">
          <thead><tr><th>Scenario</th><th>Focus</th><th>Depth</th><th>Score</th></tr></thead>
          <tbody>
            <tr><td>Deep work, fully locked in</td><td>1.0</td><td>deep (1.0×)</td><td class="score-high">100</td></tr>
            <tr><td>Deep work, moderate focus</td><td>0.7</td><td>deep (1.0×)</td><td class="score-high">70</td></tr>
            <tr><td>Shallow work, fully focused</td><td>1.0</td><td>shallow (0.6×)</td><td class="score-mid">60</td></tr>
            <tr><td>Reactive, high engagement</td><td>1.0</td><td>reactive (0.3×)</td><td class="score-low">30</td></tr>
          </tbody>
        </table>
        <p>
          That last row is the uncomfortable one. You can be fully engaged in Slack all day,
          responding instantly, feeling productive. Your score is 30. Because you weren't
          producing — you were reacting.
        </p>
      </template>

      <template v-if="activePage === 'categories'">
        <h1>What Counts as Work</h1>
        <h2 id="cat-question">The Question</h2>
        <p>
          So how do we decide — without your input — what counts as "work" for <em>you</em>?
        </p>
        <p>
          Maybe watching TikTok is your job. In which case, you have our sincere condolences.
          Maybe browsing Reddit is research. Maybe that 3-hour YouTube session was actually
          scripting your next video. We don't know your life. We don't pretend to.
        </p>
        <p class="accent-line">
          We don't define work for you. You do.
        </p>

        <h2 id="cat-distinction">Two Different Things</h2>
        <p>
          Before we go further — understand this. <em>What</em> you're doing and <em>how
          well</em> you're doing it are two completely separate things.
        </p>
        <p>
          A category is a label. "Work." "Research." "Entertainment." It tells you where
          your time went. It does not tell you whether that time was worth anything. You can
          spend 4 hours in "Work" and produce nothing. You can spend 30 minutes in "Research"
          and come out with the insight that saves your project. The label is the same. The
          <a class="page-link" @click.prevent="selectPage('scoring')">productivity score</a>
          is not.
        </p>
        <p>
          They are correlated, obviously. Time in "Entertainment" tends to score low. Time in
          "Work" tends to score higher. But it's not automatic — and that's the point. The
          score measures quality. The category measures intent.
        </p>
        <p>
          On the <a class="page-link" @click.prevent="selectPage('curve')">curve</a>, you'll
          see this directly. Each segment is colored by its category. The height is the score.
          Same color, different heights — that's the difference between focused deep work and
          distracted shallow work, both filed under "Work." The color tells you what you were
          doing. The height tells you the truth.
        </p>
        <p>
          Categories also give you the numbers that matter for planning: "I spent 20 hours on
          my side project this week." "Communication ate 8 hours." "I only got 12 hours of
          actual deep work done this month." These are the answers you couldn't get before.
        </p>

        <h2 id="cat-yours">You Define It</h2>
        <p>
          In Settings, you create <strong>categories</strong> — labels that describe how you
          spend your time. Each gets a color and a single toggle: <strong>work</strong> or
          <strong>not work</strong>. That's it. You can make them as broad or as specific as
          you want.
        </p>
        <div class="example-categories">
          <div class="example-cat">
            <span class="cat-dot" style="background: #3B82F6"></span>
            <span class="cat-name">Work</span>
            <span class="cat-flag work">work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #8B5CF6"></span>
            <span class="cat-name">Communication</span>
            <span class="cat-flag work">work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #F59E0B"></span>
            <span class="cat-name">Research</span>
            <span class="cat-flag work">work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #6B7280"></span>
            <span class="cat-name">Admin</span>
            <span class="cat-flag work">work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #EF4444"></span>
            <span class="cat-name">Entertainment</span>
            <span class="cat-flag not-work">not work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #EC4899"></span>
            <span class="cat-name">Personal</span>
            <span class="cat-flag not-work">not work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #10B981"></span>
            <span class="cat-name">Health</span>
            <span class="cat-flag not-work">not work</span>
          </div>
        </div>
        <p>
          Those are the defaults. But you're not limited to them. Add project-specific categories.
          Make it yours.
        </p>
        <div class="example-categories custom">
          <div class="example-cat">
            <span class="cat-dot" style="background: #3B82F6"></span>
            <span class="cat-name">Digital Gulag Project</span>
            <span class="cat-flag work">work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #F59E0B"></span>
            <span class="cat-name">YouTube Channel</span>
            <span class="cat-flag work">work</span>
          </div>
          <div class="example-cat">
            <span class="cat-dot" style="background: #8B5CF6"></span>
            <span class="cat-name">Client Freelance</span>
            <span class="cat-flag work">work</span>
          </div>
        </div>

        <h2 id="cat-rules">Classification Rules</h2>
        <p>
          AI classifies your activity into categories automatically. It looks at the app,
          the window title, the URL, and the context of what you're doing. Most of the time
          it gets it right. When it doesn't — or when your situation is unusual — you write
          <strong>classification rules</strong>. Plain English instructions that override the
          AI's default judgment.
        </p>
        <div class="example-rules">
          <div class="example-rule">"When I'm in Google Docs writing a YouTube script, that's YouTube Channel, deep work"</div>
          <div class="example-rule">"Reddit in the r/rust subreddit is Research, not Entertainment"</div>
          <div class="example-rule">"Figma is always Digital Gulag Project"</div>
          <div class="example-rule">"Discord in the #client-project channel is Client Freelance, not Communication"</div>
        </div>
        <p>
          We judge whether what you did was
          <a class="page-link" @click.prevent="selectPage('scoring')">deep, shallow, or reactive</a>.
          But if we're systematically wrong about something — your workflow is unusual, your tools
          don't fit the pattern — you override that too. The rules take priority over everything.
        </p>

        <h2 id="cat-flag">Work vs. Not Work</h2>
        <p>
          That single toggle on each category — work or not work — creates two numbers that
          define your day:
        </p>
        <ul>
          <li><strong>Productivity</strong> — your average score across <em>everything</em>.
          Every minute at your computer, work or not. This is the honest number.</li>
          <li><strong>Performance</strong> — your average score across <em>work only</em>.
          How good you are when you're actually trying. This is the number you hide behind.</li>
        </ul>
        <p>
          A high Performance with low Productivity means you work well — you just don't
          work enough. A high Productivity with low Performance means you're always busy
          but never doing anything hard. Neither is where you want to be.
        </p>

        <h2 id="cat-chart">The Breakdown</h2>
        <p>
          Each slice is a category. The radius is your average score in it. Big slice,
          high score — that's where you're effective. Small slice, low score — that's
          where your time goes to die.
        </p>
        <div class="demo-categories">
          <CategoryBreakdownChart :items="demoCategories" />
        </div>
      </template>

      <template v-if="activePage === 'dashboard'">
        <h1>The Dashboard</h1>
        <h2 id="dash-numbers">The Numbers</h2>
        <p>
          Six numbers. That's what your day reduces to. Not because your day is simple —
          because these six are the ones that actually matter.
        </p>
        <div class="metrics-explainer">
          <div class="metric-explain">
            <div class="metric-ex-value">5h 20m</div>
            <div class="metric-ex-label">Active</div>
            <div class="metric-ex-desc">Total time at your computer with detected activity.
            Not time logged in. Not time the screen was on. Time you were actually doing something.</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">3h 45m</div>
            <div class="metric-ex-label">Work Time</div>
            <div class="metric-ex-desc">Time in
            <a class="page-link" @click.prevent="selectPage('categories')">work-flagged</a>
            categories. The gap between Active and Work Time is how much of your day went to
            non-work. You already know where.</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">2h 10m</div>
            <div class="metric-ex-label">Deep Work</div>
            <div class="metric-ex-desc">Time classified as
            <a class="page-link" @click.prevent="selectPage('scoring')">deep</a> — complex,
            cognitively demanding focus. The most valuable hours of your day. Everything else is overhead.</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">72%</div>
            <div class="metric-ex-label">Focus</div>
            <div class="metric-ex-desc">Average concentration quality across all activity.
            How present you were when you were present.</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">48m</div>
            <div class="metric-ex-label">Best Streak</div>
            <div class="metric-ex-desc">Longest unbroken stretch of focused work — focus
            staying above 70% without dropping. Your personal record for the day.</div>
          </div>
          <div class="metric-explain">
            <div class="metric-ex-value">8</div>
            <div class="metric-ex-label">Switches</div>
            <div class="metric-ex-desc">How many times you transitioned between depth levels.
            Deep to shallow. Shallow to reactive. Each switch is a context loss. Fewer is better.</div>
          </div>
        </div>
        <p>
          Every metric shows a <strong>delta</strong> — how you compare to the previous period.
          Green means improvement. Red means decline. For switches, the colors are inverted:
          fewer is better.
        </p>

        <h2 id="dash-time">Time Scales</h2>
        <p>
          A day is useful. A week tells you more. A month tells you the truth.
        </p>
        <p>
          The dashboard has three views: <strong>day</strong>, <strong>week</strong>, and
          <strong>month</strong>. The day view shows every 10-minute interval on the
          <a class="page-link" @click.prevent="selectPage('curve')">curve</a> — the raw,
          unfiltered shape of your output. You see every spike, every dip, every moment you
          checked out.
        </p>
        <p>
          Week and month views aggregate those 10-minute points into larger buckets — 1 hour,
          3 hours, 6 hours, or full days. You choose the granularity. Each bucket shows the
          average score of all points within it. The curve smooths out, and patterns emerge
          that you can't see at the daily level. Which days consistently underperform. Which
          time blocks are your most productive. Whether your Fridays are actually worth anything.
        </p>

        <h2 id="dash-aggregation">How We Aggregate</h2>
        <p>
          Not all numbers add up the same way. If you worked 4 hours Monday and 8 hours
          Tuesday, your week's work time is 12 hours — obvious. But your average focus
          isn't the average of all individual 10-minute intervals across both days. It's the
          average of Monday's focus and Tuesday's focus. Each day weighs equally, regardless
          of length. Otherwise a 12-hour grind would drown out a sharp 4-hour morning.
        </p>
        <table class="info-table">
          <thead><tr><th>Type</th><th>How it aggregates</th><th>Metrics</th></tr></thead>
          <tbody>
            <tr><td>Time</td><td><strong>Sum</strong> across days</td><td>Active, Work Time, Deep Work</td></tr>
            <tr><td>Quality</td><td><strong>Average</strong> per day, then average of days</td><td>Focus, Productivity, Performance</td></tr>
            <tr><td>Count</td><td><strong>Sum</strong> across days</td><td>Switches</td></tr>
            <tr><td>Peak</td><td><strong>Maximum</strong> across days</td><td>Best Streak</td></tr>
          </tbody>
        </table>

        <h2 id="dash-heatmap">Heatmap</h2>
        <p>
          In week and month views, a color grid appears next to the curve. It answers the
          question you keep asking yourself: <em>when</em> am I actually productive?
        </p>
        <p>
          Week view splits each day into four 6-hour blocks. Month view shows a calendar grid.
          Green means you were productive. Red means you weren't. Gray means you weren't there.
          After a few weeks, the pattern is obvious. You'll see which time blocks consistently
          light up — and which ones you've been lying to yourself about.
        </p>

        <h2 id="dash-narrative">Narrative</h2>
        <p>
          At the top of your dashboard, AI writes a summary of your day. Not a list of apps.
          Not a time breakdown. A <em>narrative</em> — what happened, how it went, what the
          patterns mean.
        </p>
        <p>
          During the day, it reacts to your current state. After the day ends, it reflects.
          Updated every hour alongside your timeline. It's the voice that says what the
          numbers already show but you might not want to read.
        </p>
      </template>

      <template v-if="activePage === 'timeline'">
        <h1>The Timeline</h1>
        <h2 id="tl-raw">What We See</h2>
        <p>
          A daemon runs on your machine. It watches everything. Every window you open, every
          app you switch to, every URL you visit, every idle gap where you walked away. It
          captures this as raw activity events — hundreds of them per hour — and ships them
          to the server.
        </p>
        <p>This is what the raw data looks like:</p>
        <div class="event-log">
          <div class="event-line"><span class="ev-time">09:01:14</span><span class="ev-app">VS Code</span><span class="ev-detail">main.rs — digitalgulag/server/src</span></div>
          <div class="event-line"><span class="ev-time">09:03:47</span><span class="ev-app">Chrome</span><span class="ev-detail">Stack Overflow — "rust async trait bounds"</span></div>
          <div class="event-line"><span class="ev-time">09:04:02</span><span class="ev-app">Slack</span><span class="ev-detail">#general — new message</span></div>
          <div class="event-line"><span class="ev-time">09:04:18</span><span class="ev-app">VS Code</span><span class="ev-detail">main.rs — digitalgulag/server/src</span></div>
          <div class="event-line"><span class="ev-time">09:06:33</span><span class="ev-app">Terminal</span><span class="ev-detail">cargo test — 3 passed</span></div>
          <div class="event-line"><span class="ev-time">09:07:01</span><span class="ev-app">VS Code</span><span class="ev-detail">auth.rs — digitalgulag/server/src</span></div>
          <div class="event-line"><span class="ev-time">09:09:44</span><span class="ev-app">Chrome</span><span class="ev-detail">docs.rs — reqwest::Client</span></div>
          <div class="event-line dim"><span class="ev-time">09:10:12</span><span class="ev-app">VS Code</span><span class="ev-detail">auth.rs — digitalgulag/server/src</span></div>
          <div class="event-line dim"><span class="ev-time">09:12:58</span><span class="ev-app">Chrome</span><span class="ev-detail">Reddit — r/rust frontpage</span></div>
          <div class="event-line dim"><span class="ev-time">09:13:06</span><span class="ev-app">Chrome</span><span class="ev-detail">Reddit — "Is Axum better than Actix?"</span></div>
          <div class="event-line dim"><span class="ev-time">…</span><span class="ev-app"></span><span class="ev-detail"></span></div>
        </div>
        <p>
          Dozens of window switches. App names. Timestamps. None of it is human-readable.
          None of it tells you what you actually <em>did</em>.
        </p>

        <h2 id="tl-ai">What You See</h2>
        <p>
          AI takes that stream of raw events and turns it into a timeline:
        </p>
        <div class="timeline-demo">
          <div class="tl-entry" style="border-left-color: #3B82F6">
            <span class="tl-time">09:00 – 10:15</span>
            <span class="tl-label">Coding auth module in VS Code</span>
          </div>
          <div class="tl-entry" style="border-left-color: #8B5CF6">
            <span class="tl-time">10:15 – 10:35</span>
            <span class="tl-label">Slack and email triage</span>
          </div>
          <div class="tl-entry" style="border-left-color: #3B82F6">
            <span class="tl-time">10:35 – 11:40</span>
            <span class="tl-label">Back to coding, implementing API endpoints</span>
          </div>
          <div class="tl-entry" style="border-left-color: #EF4444">
            <span class="tl-time">11:40 – 12:00</span>
            <span class="tl-label">Reddit and YouTube</span>
          </div>
        </div>
        <p>
          Not a list of window switches. A story.
        </p>
        <p>
          Each entry gets a
          <a class="page-link" @click.prevent="selectPage('categories')">category</a>,
          a color, a description, and the
          <a class="page-link" @click.prevent="selectPage('scoring')">productivity score</a>
          for that block. The AI decides where one activity ends and another begins. It
          merges the noise — the quick doc lookups, the terminal switches, the brief tab
          changes — into coherent sessions that reflect what you were actually working on.
        </p>
        <p>
          If it gets something wrong, you edit it. The correction is instant and the AI
          learns from your
          <a class="page-link" @click.prevent="selectPage('categories')">classification rules</a>.
        </p>

        <h2 id="tl-loop">The Loop</h2>
        <p>
          The timeline updates every hour. New raw events come in, AI processes them, new
          entries appear. During the day you're watching your story write itself in near
          real-time.
        </p>
        <p>
          At the end of the day, the full picture is there. Every hour accounted for. Every
          distraction visible. Every deep work session measured. You open the dashboard the
          next morning and the answer to "what did I do yesterday?" is already written.
        </p>
        <p>
          That's the point. You asked a question on the
          <a class="page-link" @click.prevent="selectPage('idea')">first page</a> —
          what did I actually do today? The timeline is the answer.
        </p>
      </template>

      <template v-if="activePage === 'agent'">
        <h1>The Agent</h1>
        <h2 id="agent-what">What It Does</h2>
        <p>
          Everything you see on the dashboard — the
          <a class="page-link" @click.prevent="selectPage('timeline')">timeline</a>, the
          <a class="page-link" @click.prevent="selectPage('curve')">curve</a>, the
          <a class="page-link" @click.prevent="selectPage('dashboard')">narrative</a> — is
          produced by an AI agent. It reads your raw activity, understands what you were
          doing, scores how well you were doing it, and writes the story of your day.
        </p>
        <p>
          It runs automatically every hour. You don't need to do anything. But if something
          is wrong — a miscategorized entry, a timeline gap, a score that doesn't feel right —
          you don't file a bug report. You don't dig through settings.
        </p>
        <p class="accent-line">
          You talk to it.
        </p>

        <h2 id="agent-talk">Talk To It</h2>
        <p>
          The chat panel on the right side of your dashboard is a direct line to the agent.
          It has full access to your data — your activity events, your timeline, your scores,
          your
          <a class="page-link" @click.prevent="selectPage('categories')">categories and
          classification rules</a>. It can read everything and change everything.
        </p>
        <div class="chat-examples">
          <div class="chat-bubble user">"That block from 2-3pm was actually deep work on the API, not admin"</div>
          <div class="chat-bubble agent">Updates the timeline entry, recalculates the productivity score for that interval.</div>
          <div class="chat-bubble user">"Why was my performance so low on Thursday?"</div>
          <div class="chat-bubble agent">Analyzes your Thursday data, identifies the 2-hour Slack spiral after lunch, explains the impact on your score.</div>
          <div class="chat-bubble user">"Reprocess today, I updated my classification rules"</div>
          <div class="chat-bubble agent">Re-reads your raw events with the new rules, regenerates the timeline and curve.</div>
        </div>
        <p>
          Whatever is wrong, whatever needs to change — ask it and it will do it.
          No menus. No forms. Just tell it what you need.
        </p>

        <h2 id="agent-memory">Memory</h2>
        <p>
          The agent remembers. Not just within a conversation — across sessions. It builds
          up context about your work patterns, your projects, your preferences. Tell it
          something once and it carries that forward.
        </p>
        <div class="chat-examples">
          <div class="chat-bubble user">"When I'm in Figma it's always the Digital Gulag project"</div>
          <div class="chat-bubble agent">Saves this as a memory. From now on, Figma activity is automatically categorized correctly — no classification rule needed.</div>
        </div>
        <p>
          The more you interact with it, the less you need to. It learns your world and
          stops making mistakes you've already corrected.
        </p>
      </template>

      <template v-if="activePage === 'integrations'">
        <h1>Integrations</h1>
        <h2 id="int-why">Why More Data</h2>
        <p>
          We monitor your computer. That's a start. But your life doesn't happen entirely
          inside a browser and an IDE.
        </p>
        <p>
          You slept 4 hours last night and your focus score tanked — was it the work or
          the sleep? You pushed 47 commits this week but your deep work time shows only
          12 hours — where's the gap? You had a great Thursday but you can't figure out
          what was different.
        </p>
        <p>
          The more data we have about your life, the better we can explain your performance.
          Not just <em>what</em> happened, but <em>why</em>. Integrations feed external
          data into the system so the agent can connect the dots you can't see.
        </p>

        <h2 id="int-current">Available Now</h2>
        <div class="integration-list">
          <div class="integration-card">
            <div class="int-header">
              <span class="int-name">Telegram</span>
              <span class="int-badge live">live</span>
            </div>
            <p>Push notifications. Daily summaries delivered to your chat.
            Reminders when you've been unproductive for too long. The agent can
            reach you even when you're not looking at the dashboard.</p>
          </div>
        </div>

        <h2 id="int-planned">Planned</h2>
        <p>
          These are coming. The goal is the same for all of them — more signal, better
          explanations, sharper insights.
        </p>
        <div class="integration-list">
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">GitHub</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>Commits, PRs, reviews. Map your code output directly to your deep work
            sessions. See whether 4 hours of "coding" actually produced anything.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">Oura / Health</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>Sleep, readiness, heart rate. Correlate your physical state with your
            cognitive output. Find out if your bad Tuesdays are actually bad Mondays.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">AI Coding Tools</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>Claude Code, Cursor, Copilot. Track AI-assisted vs. solo work.
            Measure whether your tools are actually making you faster or just
            making you feel faster.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">Calendar</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>Google Calendar, Outlook. See meetings as timeline blocks. Measure
            the real cost of a 30-minute meeting — including the 20 minutes of
            recovery focus you lost after.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">Spotify / Music</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>What were you listening to during your best deep work sessions?
            Does lo-fi actually help or is that a placebo? Does silence beat
            everything? The data will show it — and you might not like the answer.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">Phone Screen Time</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>iOS and Android screen time data. The biggest blind spot in computer
            monitoring. You "stepped away for a break" but actually scrolled TikTok
            for 25 minutes. Phone pickups during work hours are the silent killer
            no one wants to measure.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">Linear / Jira / Notion</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>Map tasks and tickets to time blocks. Instead of "6 hours of Work"
            you get "6 hours on PROJ-142." Track time per project, per epic, per sprint.
            The granularity your manager wishes they had — except this time it's for you.</p>
          </div>
          <div class="integration-card planned">
            <div class="int-header">
              <span class="int-name">Location</span>
              <span class="int-badge planned">planned</span>
            </div>
            <p>Coffee shop vs. home vs. office. You tell yourself you work better
            at the café. Maybe you do. Maybe you spend 40% of the time people-watching.
            Location data lets the agent correlate environment with output — and settle
            the argument with numbers.</p>
          </div>
        </div>
      </template>

      <template v-if="activePage === 'security'">
        <h1>Security</h1>
        <h2 id="sec-concern">The Concern</h2>
        <p>
          A daemon on your machine watching every window you open and every URL you visit,
          shipping it to a server, feeding it to an LLM. You'd be insane not to ask questions.
        </p>
        <p>
          So let's answer them.
        </p>

        <h2 id="sec-collect">What We Collect</h2>
        <p>
          The daemon captures three things:
        </p>
        <ul>
          <li><strong>Window titles</strong> — the title bar of whatever app is in focus.
          "main.rs — VS Code", "Inbox — Gmail", "r/rust — Chrome".</li>
          <li><strong>Idle / non-idle state</strong> — whether you're at your computer or not.
          No keylogging, no mouse tracking, no screenshots. Just: present or absent.</li>
          <li><strong>URLs</strong> — the address of the active browser tab. This is on by
          default because it dramatically improves classification accuracy. You can disable
          it in the daemon config if you don't want it.</li>
        </ul>
        <p>
          That's it. No keystrokes. No screen recording. No clipboard. No file contents.
          No camera. No microphone. We capture the minimum needed to understand what you're
          doing — not what you're typing or saying.
        </p>

        <h2 id="sec-llm">The LLM Question</h2>
        <p>
          Yes, your window titles and URLs are sent to an LLM for analysis. That's how the
          <a class="page-link" @click.prevent="selectPage('agent')">agent</a> understands
          your activity — it reads the same metadata you'd see in a task manager.
        </p>
        <p>
          Should you care? Depends on your threat model. If your window titles contain
          classified information, this tool is not for you. For most people — developers,
          designers, writers, students — your window titles are "VS Code", "Figma",
          "Google Docs", and "YouTube." Not exactly state secrets.
        </p>
        <p>
          If it still bothers you, there's a simple solution:
        </p>

        <h2 id="sec-open">Open Source</h2>
        <p>
          The entire project is open source. Every line of code — the daemon, the server,
          the AI agent, the frontend. Nothing is hidden. Nothing is obfuscated.
        </p>
        <p class="github-cta">
          <a href="https://github.com/galthran-wq/digitalgulag" target="_blank" rel="noopener" class="github-link">
            <svg viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            galthran-wq/digitalgulag
          </a>
        </p>
        <p>
          You can read exactly what the daemon collects, exactly what gets sent to the LLM,
          exactly what's stored in the database. If you don't trust us — good. Read the code.
        </p>
        <p>
          And if security is truly your main concern: deploy it yourself. The entire stack
          runs on any server you control. Your data never leaves your machine. Use your own
          LLM API key. Point the daemon at your own server. Full sovereignty, zero trust
          required.
        </p>
        <p>
          And while you're there — if this project is useful to you, leave a star. It's
          built by one person who could be doing literally anything else with their time.
          A star costs you nothing and means more than you think.
        </p>
      </template>

      <template v-if="activePage === 'conclusion'">
        <h1>Conclusion</h1>
        <h2 id="end-summary">The Point</h2>
        <p>
          You already know you could be doing better. You don't need an app to tell you that.
        </p>
        <p>
          What you need is to see <em>exactly</em> where the time goes. Not a vague feeling
          that the day slipped away — a precise, minute-by-minute accounting of what happened.
          The
          <a class="page-link" @click.prevent="selectPage('timeline')">timeline</a>
          gives you that. The
          <a class="page-link" @click.prevent="selectPage('curve')">curve</a>
          shows you how well you spent it. The
          <a class="page-link" @click.prevent="selectPage('scoring')">score</a>
          puts a number on it so you can't lie to yourself.
        </p>
        <p>
          Every context switch costs you up to 23 minutes of degraded focus. Brief
          interruptions consume up to 40% of your productive time. Four focused hours
          beat eight scattered ones — but the scattered day <em>looks</em> busier by
          every traditional metric. That's the gap we exist to close.
        </p>
        <p>
          This is not a gentle tool. It doesn't congratulate you for showing up. It
          measures what you actually produced, compares it to what you could have produced,
          and shows you the difference. What you do with that information is up to you.
        </p>
        <p class="manifesto-line closing" style="margin-top: 32px">
          Now close this page and go do something worth measuring.
        </p>

        <h2 id="end-references">References</h2>
        <p>
          The scoring model, the depth framework, the attention residue costs — none of
          it was invented. It's built on research.
        </p>
        <div class="references">
          <p>Mark, Gudith, Klocke (2008). <em>"The Cost of Interrupted Work: More Speed and Stress."</em>
          CHI 2008, UCI. The 23-minute refocus finding.</p>
          <p>Cal Newport (2016). <em>"Deep Work: Rules for Focused Success in a Distracted World."</em>
          The deep vs. shallow framework our depth classification is built on.</p>
          <p>Ophir, Nass, Wagner (2009). <em>"Cognitive control in media multitaskers."</em>
          Stanford. Heavy multitaskers are worse at filtering — the cost compounds.</p>
          <p>Csikszentmihalyi (1990). <em>"Flow: The Psychology of Optimal Experience."</em>
          The foundational work on optimal concentration states.</p>
          <p>Ashinoff, Abu-Akel (2021). <em>"Hyperfocus: the forgotten frontier of attention."</em>
          Intense absorbed concentration as a feature, not a bug.</p>
          <p>Todoist Research. <em>"The Real Cost of Context Switching."</em>
          40% productive time loss from brief interruptions.</p>
        </div>
      </template>

    </div>

    <nav class="docs-toc">
      <div class="docs-toc-title">On this page</div>
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
