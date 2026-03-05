<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import LogoIcon from '@/components/LogoIcon.vue'
import ProductivityCurve from '@/components/ProductivityCurve.vue'
import type { ProductivityPoint } from '@/types/productivityCurve'
import type { TimelineEntry } from '@/types/timeline'

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

const features = [
  { title: 'Productivity Curve', desc: 'Your score plotted over time. Every 10 minutes, a number. The shape of your day — visible, measurable, undeniable.', page: 'curve' },
  { title: 'AI Timeline', desc: 'Raw window switches become a human-readable story. What you did, when, and how well. Updated every hour.', page: 'timeline' },
  { title: 'Categories & Rules', desc: 'You define what counts as work. Custom categories, plain-English classification rules. Your workflow, your rules.', page: 'categories' },
  { title: 'Agent Chat', desc: 'Something wrong? Tell the agent. It reads your data, fixes mistakes, answers questions, and remembers for next time.', page: 'agent' },
  { title: 'Integrations', desc: 'GitHub, health data, calendar, screen time. The more we know, the better we explain why some days work and others don\'t.', page: 'integrations' },
  { title: 'Open Source', desc: 'Every line of code is public. Deploy it yourself. Use your own LLM. Full sovereignty, zero trust required.', page: 'security' },
]
</script>

<template>
  <div class="landing">

    <section class="hero">
      <LogoIcon :size="140" />
      <h1 class="hero-title">DIGITAL GULAG</h1>
      <p class="hero-tagline">The ultimate productivity monitoring system.</p>
      <p class="hero-hook">
        Have you ever spent an entire day at your computer and had no idea where the time went?
      </p>
      <div class="hero-cta">
        <NButton type="primary" size="large" @click="router.push({ name: 'login' })">Get Started</NButton>
        <NButton size="large" secondary @click="router.push({ name: 'guide', params: { page: 'idea' } })">How It Works</NButton>
      </div>
    </section>

    <section class="section problem">
      <p>You don't know where your time goes. You can't explain why some days work and others don't.</p>
      <p>You've tried to find patterns. You've tried to force yourself. You've watched the hours disappear into Slack, Reddit, YouTube — knowing you should be working.</p>
      <p class="problem-punchline">We measure every aspect of your performance. Comprehensively, continuously, with zero manual input.</p>
    </section>

    <section class="section steps">
      <h2 class="section-title">How It Works</h2>
      <div class="steps-grid">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-title">Monitor</div>
          <p>A daemon on your machine captures window titles, idle state, and URLs. No keystrokes, no screenshots, no clipboard. Just enough to know what you're doing.</p>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-title">Analyze</div>
          <p>Every 10 minutes, AI scores your focus and cognitive depth. It builds a timeline of your day in plain language. Not what apps you opened — what you actually did.</p>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-title">Improve</div>
          <p>The dashboard shows the truth. The curve exposes your patterns. The agent helps you understand them. What you do with that information is up to you.</p>
        </div>
      </div>
    </section>

    <section class="section curve-section">
      <h2 class="section-title">This Is What a Morning Looks Like</h2>
      <p class="curve-subtitle">Deep focus building up. A dip into admin and chat. The recovery grind. Then distraction. Hover to explore.</p>
      <div class="curve-demo">
        <ProductivityCurve :points="demoPoints" :entries="demoEntries" />
      </div>
    </section>

    <section class="section features">
      <h2 class="section-title">Everything You Need</h2>
      <div class="features-grid">
        <a
          v-for="f in features"
          :key="f.page"
          class="feature-card"
          @click.prevent="router.push({ name: 'guide', params: { page: f.page } })"
        >
          <div class="feature-title">{{ f.title }}</div>
          <p>{{ f.desc }}</p>
        </a>
      </div>
    </section>

    <section class="section cta-footer">
      <p class="cta-line">Now close this page and go do something worth measuring.</p>
      <div class="cta-buttons">
        <NButton type="primary" size="large" @click="router.push({ name: 'login' })">Get Started</NButton>
      </div>
      <a href="https://github.com/galthran-wq/digitalgulag" target="_blank" rel="noopener" class="footer-github">
        <svg viewBox="0 0 16 16" width="18" height="18" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
        galthran-wq/digitalgulag
      </a>
    </section>

  </div>
</template>

<style scoped>
.landing {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
}

.hero {
  text-align: center;
  padding: 80px 0 60px;
}

.hero-title {
  font-size: 52px;
  font-weight: 800;
  letter-spacing: 8px;
  margin: 24px 0 0;
}

.hero-tagline {
  font-size: 14px;
  opacity: 0.4;
  letter-spacing: 1px;
  margin: 10px 0 0;
}

.hero-hook {
  font-size: 17px;
  opacity: 0.6;
  margin: 32px auto 0;
  max-width: 520px;
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 36px;
}

.section {
  padding: 48px 0;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 32px;
}

.problem {
  text-align: center;
  border-top: 1px solid rgba(150, 150, 150, 0.1);
}

.problem p {
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.6;
  max-width: 600px;
  margin: 0 auto 16px;
}

.problem-punchline {
  font-size: 17px !important;
  font-weight: 600;
  opacity: 1 !important;
  margin-top: 24px !important;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.step {
  text-align: center;
  padding: 24px 16px;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--to-brand);
  color: var(--to-surface);
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.step-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

.step p {
  font-size: 13px;
  line-height: 1.6;
  opacity: 0.6;
}

.curve-section {
  border-top: 1px solid rgba(150, 150, 150, 0.1);
}

.curve-subtitle {
  text-align: center;
  font-size: 14px;
  opacity: 0.5;
  margin: -20px auto 24px;
  max-width: 500px;
}

.curve-demo {
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.feature-card {
  padding: 20px;
  border-radius: 10px;
  background: rgba(150, 150, 150, 0.04);
  border: 1px solid rgba(150, 150, 150, 0.08);
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s, border-color 0.15s;
}

.feature-card:hover {
  background: rgba(150, 150, 150, 0.08);
  border-color: rgba(150, 150, 150, 0.15);
}

.feature-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 6px;
}

.feature-card p {
  font-size: 13px;
  line-height: 1.5;
  opacity: 0.55;
  margin: 0;
}

.cta-footer {
  text-align: center;
  padding: 48px 0 64px;
  border-top: 1px solid rgba(150, 150, 150, 0.1);
}

.cta-line {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 24px;
  opacity: 0.7;
}

.cta-buttons {
  margin-bottom: 24px;
}

.footer-github {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  opacity: 0.35;
  color: inherit;
  text-decoration: none;
  transition: opacity 0.15s;
}

.footer-github:hover {
  opacity: 0.7;
}

@media (max-width: 700px) {
  .hero-title { font-size: 36px; letter-spacing: 4px; }
  .steps-grid { grid-template-columns: 1fr; }
  .features-grid { grid-template-columns: 1fr; }
}
</style>
