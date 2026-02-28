<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, NAlert, NText } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (e) {
    if (e instanceof ApiError) {
      error.value = e.message
    } else {
      error.value = 'An unexpected error occurred'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div style="text-align: center; margin-bottom: 32px">
      <div style="font-size: 36px; font-weight: 700; color: #3B82F6; margin-bottom: 8px">TimeOracle</div>
      <NText depth="3" style="font-size: 14px">AI-powered time tracking</NText>
    </div>
    <NCard style="max-width: 400px; width: 100%; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12)">
      <NForm @submit.prevent="handleSubmit">
        <NAlert v-if="error" type="error" :title="error" style="margin-bottom: 16px" closable />
        <NFormItem label="Email">
          <NInput v-model:value="email" type="text" placeholder="you@example.com" size="large" />
        </NFormItem>
        <NFormItem label="Password">
          <NInput
            v-model:value="password"
            type="password"
            show-password-on="click"
            placeholder="Password"
            size="large"
          />
        </NFormItem>
        <NButton
          type="primary"
          attr-type="submit"
          :loading="loading"
          :disabled="!email || !password"
          block
          size="large"
          style="margin-top: 8px"
        >
          Sign In
        </NButton>
      </NForm>
    </NCard>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
}
</style>
