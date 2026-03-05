import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import LandingView from '@/views/LandingView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ActivityView from '@/views/ActivityView.vue'
import TimelineView from '@/views/TimelineView.vue'
import SettingsView from '@/views/SettingsView.vue'
import MetricsGuideView from '@/views/MetricsGuideView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/landing', name: 'landing', component: LandingView, meta: { public: true } },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/activity', name: 'activity', component: ActivityView },
    { path: '/timeline', name: 'timeline', component: TimelineView },
    { path: '/settings', name: 'settings', component: SettingsView },
    { path: '/guide/:page?', name: 'guide', component: MetricsGuideView, meta: { public: true } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'landing' }
  }
  if ((to.name === 'login' || to.name === 'landing') && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
