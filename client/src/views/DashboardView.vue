<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import {
  NSpace,
  NButton,
  NList,
  NListItem,
  NText,
  NCard,
  NSpin,
  NEmpty,
  NGrid,
  NGridItem,
  NStatistic,
  NBadge,
} from 'naive-ui'
import { useRouter } from 'vue-router'
import { format } from 'date-fns'
import { formatDistanceToNow } from 'date-fns'
import { useActivityStore } from '@/stores/activity'
import { listEntries } from '@/api/timeline'
import { listSessions } from '@/api/activity'
import { useDayAnalytics } from '@/composables/useDayAnalytics'
import { SESSION_PALETTE } from '@/constants/palette'
import type { TimelineEntry } from '@/types/timeline'
import type { ActivitySession } from '@/types/activity'

const router = useRouter()
const activityStore = useActivityStore()
const todayEntries = ref<TimelineEntry[]>([])
const todaySessions = ref<ActivitySession[]>([])
const loading = ref(true)
const showAllEntries = ref(false)
const showAllSessions = ref(false)

const {
  totalActiveMinutes,
  sessionCount,
  topApp,
  appBreakdown,
  categoryBreakdown,
  formatMinutes,
} = useDayAnalytics(todaySessions, todayEntries)

const isActive = computed(() => {
  if (!activityStore.status?.last_event_at) return false
  return Date.now() - new Date(activityStore.status.last_event_at).getTime() < 5 * 60 * 1000
})

const lastEventText = computed(() => {
  if (!activityStore.status?.last_event_at) return 'No events yet'
  return formatDistanceToNow(new Date(activityStore.status.last_event_at), { addSuffix: true })
})

const maxAppMinutes = computed(() => appBreakdown.value[0]?.minutes ?? 1)
const maxCategoryMinutes = computed(() => categoryBreakdown.value[0]?.minutes ?? 1)

const displayedEntries = computed(() =>
  showAllEntries.value ? todayEntries.value : todayEntries.value.slice(0, 5)
)
const displayedSessions = computed(() =>
  showAllSessions.value ? todaySessions.value : todaySessions.value.slice(0, 5)
)

function appColor(app: string): string {
  const apps = [...new Set(todaySessions.value.map((s) => s.app_name))]
  const idx = apps.indexOf(app)
  return SESSION_PALETTE[(idx >= 0 ? idx : 0) % SESSION_PALETTE.length].main
}

onMounted(async () => {
  const today = format(new Date(), 'yyyy-MM-dd')
  await Promise.all([
    activityStore.fetchStatus(),
    listEntries({ date: today }).then((res) => {
      todayEntries.value = res.entries
    }),
    listSessions({ date: today, limit: 200 }).then((res) => {
      todaySessions.value = res.sessions
    }),
  ])
  loading.value = false
})
</script>

<template>
  <NSpin :show="loading">
    <NSpace vertical :size="20">
      <NSpace align="center" :size="16">
        <NBadge :dot="true" :type="isActive ? 'success' : 'error'" />
        <NText>Daemon {{ isActive ? 'active' : 'inactive' }}</NText>
        <NText depth="3" style="font-size: 13px">{{ lastEventText }}</NText>
        <NText depth="3" style="font-size: 13px">·</NText>
        <NText depth="3" style="font-size: 13px">{{ activityStore.status?.events_today ?? 0 }} events today</NText>
      </NSpace>

      <NGrid :cols="3" :x-gap="16" :y-gap="16">
        <NGridItem>
          <NCard size="small">
            <NStatistic label="Active Time">
              <template #default>
                <span style="font-size: 28px; font-weight: 700">{{ formatMinutes(totalActiveMinutes) }}</span>
              </template>
            </NStatistic>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard size="small">
            <NStatistic label="Sessions" :value="sessionCount" />
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard size="small">
            <NStatistic label="Top App">
              <template #default>
                <span style="font-size: 20px; font-weight: 600">{{ topApp ?? '—' }}</span>
              </template>
            </NStatistic>
          </NCard>
        </NGridItem>
      </NGrid>

      <NGrid :cols="2" :x-gap="16" :y-gap="16">
        <NGridItem>
          <NCard title="Time by App" size="small">
            <NEmpty v-if="!appBreakdown.length" description="No activity" />
            <div v-else>
              <div
                v-for="item in appBreakdown"
                :key="item.app"
                style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px"
              >
                <NText
                  style="width: 100px; text-align: right; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-shrink: 0"
                  :title="item.app"
                >
                  {{ item.app }}
                </NText>
                <div style="flex: 1; height: 20px; background: var(--n-color-modal); border-radius: 3px; overflow: hidden">
                  <div
                    :style="{
                      width: (item.minutes / maxAppMinutes * 100) + '%',
                      height: '100%',
                      background: appColor(item.app),
                      borderRadius: '3px',
                      transition: 'width 0.3s ease',
                    }"
                  />
                </div>
                <NText depth="3" style="width: 50px; font-size: 12px; flex-shrink: 0">
                  {{ formatMinutes(item.minutes) }}
                </NText>
              </div>
            </div>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard title="Time by Category" size="small">
            <template #header-extra>
              <NButton text type="primary" size="small" @click="router.push({ name: 'timeline' })">
                View Calendar
              </NButton>
            </template>
            <NEmpty v-if="!categoryBreakdown.length" description="No timeline entries" />
            <div v-else>
              <div
                v-for="item in categoryBreakdown"
                :key="item.category"
                style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px"
              >
                <NText
                  style="width: 100px; text-align: right; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-shrink: 0"
                  :title="item.category"
                >
                  {{ item.category }}
                </NText>
                <div style="flex: 1; height: 20px; background: var(--n-color-modal); border-radius: 3px; overflow: hidden">
                  <div
                    :style="{
                      width: (item.minutes / maxCategoryMinutes * 100) + '%',
                      height: '100%',
                      background: '#3B82F6',
                      borderRadius: '3px',
                      transition: 'width 0.3s ease',
                    }"
                  />
                </div>
                <NText depth="3" style="width: 50px; font-size: 12px; flex-shrink: 0">
                  {{ formatMinutes(item.minutes) }}
                </NText>
              </div>
            </div>
          </NCard>
        </NGridItem>
      </NGrid>

      <NGrid :cols="2" :x-gap="16" :y-gap="16">
        <NGridItem>
          <NCard title="Today's Timeline" size="small">
            <NEmpty v-if="!todayEntries.length" description="No timeline entries today" />
            <template v-else>
              <NList :show-divider="false" style="margin: -4px 0">
                <NListItem v-for="entry in displayedEntries" :key="entry.id" style="padding: 6px 0">
                  <NSpace align="center" :size="8">
                    <div
                      v-if="entry.color"
                      :style="{
                        width: '10px',
                        height: '10px',
                        borderRadius: '2px',
                        backgroundColor: entry.color,
                        flexShrink: 0,
                      }"
                    />
                    <NText strong style="font-size: 13px">{{ entry.label }}</NText>
                    <NText depth="3" style="font-size: 12px">
                      {{ format(new Date(entry.start_time), 'HH:mm') }}–{{ format(new Date(entry.end_time), 'HH:mm') }}
                    </NText>
                    <NText v-if="entry.category" depth="3" style="font-size: 12px">· {{ entry.category }}</NText>
                  </NSpace>
                </NListItem>
              </NList>
              <NButton
                v-if="todayEntries.length > 5"
                text
                type="primary"
                size="small"
                style="margin-top: 4px"
                @click="showAllEntries = !showAllEntries"
              >
                {{ showAllEntries ? 'Show less' : `Show all (${todayEntries.length})` }}
              </NButton>
            </template>
          </NCard>
        </NGridItem>
        <NGridItem>
          <NCard title="Today's Activity" size="small">
            <NEmpty v-if="!todaySessions.length" description="No activity recorded today" />
            <template v-else>
              <NList :show-divider="false" style="margin: -4px 0">
                <NListItem v-for="session in displayedSessions" :key="session.id" style="padding: 6px 0">
                  <NSpace align="center" :size="8">
                    <div
                      :style="{
                        width: '10px',
                        height: '10px',
                        borderRadius: '2px',
                        backgroundColor: appColor(session.app_name),
                        flexShrink: 0,
                      }"
                    />
                    <NText strong style="font-size: 13px">{{ session.app_name }}</NText>
                    <NText depth="3" style="font-size: 12px">
                      {{ format(new Date(session.start_time), 'HH:mm') }}–{{ format(new Date(session.end_time), 'HH:mm') }}
                    </NText>
                  </NSpace>
                </NListItem>
              </NList>
              <NButton
                v-if="todaySessions.length > 5"
                text
                type="primary"
                size="small"
                style="margin-top: 4px"
                @click="showAllSessions = !showAllSessions"
              >
                {{ showAllSessions ? 'Show less' : `Show all (${todaySessions.length})` }}
              </NButton>
            </template>
          </NCard>
        </NGridItem>
      </NGrid>
    </NSpace>
  </NSpin>
</template>
