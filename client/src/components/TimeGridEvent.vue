<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  calendarEvent: any
  isDark: boolean
}>()

const eventColor = computed(() => props.calendarEvent._color || '#3B82F6')
const title = computed(() => props.calendarEvent._label || props.calendarEvent.title || '')
const category = computed(() => props.calendarEvent._category || '')
const description = computed(() => props.calendarEvent.description || '')
</script>

<template>
  <div class="tge-card" :class="{ 'is-dark': isDark }" :style="{ borderLeftColor: eventColor }">
    <div class="tge-text">
      <div class="tge-title">{{ title }}</div>
      <div v-if="category" class="tge-category">{{ category }}</div>
      <div v-if="description" class="tge-description">{{ description }}</div>
    </div>
  </div>
</template>
