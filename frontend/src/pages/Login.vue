<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">Dynamic Cell Culture Drive Control</h1>
          <p class="login-subtitle">Sign in to access the control panel</p>
        </div>

        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="form-control"
              required
              autocomplete="username"
              :disabled="loading"
              placeholder="Enter your username"
            />
          </div>
          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              class="form-control"
              required
              autocomplete="current-password"
              :disabled="loading"
              placeholder="Enter your password"
            />
          </div>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="login-divider">
          <span>or</span>
        </div>

        <button
          class="btn btn-outline quick-login-btn"
          @click="quickLogin"
          :disabled="loading"
        >
          🔑 Quick Login as Admin
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '../api'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = 'Please enter both username and password'
    return
  }

  try {
    loading.value = true
    error.value = ''
    await authApi.login(username.value, password.value)
    // Force router to re-evaluate auth state
    const redirect = (route.query.redirect as string) || '/'
    await router.push(redirect)
    // Trigger a small delay to ensure state updates
    await router.isReady()
  } catch (err: any) {
    error.value =
      err.response?.data?.detail ||
      err.message ||
      'Invalid username or password'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

const quickLogin = async () => {
  username.value = 'admin'
  password.value = 'admin'
  await handleLogin()
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e4f7e7 0%, #FFFFFF 100%);
  padding: 2rem;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 2.5rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.login-form {
  margin-bottom: 1.5rem;
}

.login-form .btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.login-divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.login-divider::before,
.login-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border-color);
}

.login-divider span {
  padding: 0 1rem;
}

.quick-login-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.9375rem;
}

.alert {
  margin-bottom: 1.5rem;
}
</style>
