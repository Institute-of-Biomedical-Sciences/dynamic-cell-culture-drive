import { ref } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized } from 'vue-router'
import AppLayout from '@/layout/AppLayout.vue'
import { authApi } from '@/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/pages/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '/', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
        { path: '/tilt-motor', name: 'TiltMotor', component: () => import('@/pages/TiltMotor.vue') },
        { path: '/rotary-motor', name: 'RotaryMotor', component: () => import('@/pages/RotaryMotor.vue') },
        { path: '/peristaltic-motor-calibration', name: 'PeristalticMotorCalibration', component: () => import('@/pages/PeristalticMotorCalibration.vue') },
        { path: '/peristaltic-motor-tube-configurations', name: 'PeristalticMotorTubeConfigurations', component: () => import('@/pages/PeristalticMotorTubeConfigurations.vue') },
        { path: '/peristaltic-motor', name: 'PeristalticMotor', component: () => import('@/pages/PeristalticMotor.vue') },
        { path: '/measurements-history', name: 'MeasurementsHistory', component: () => import('@/pages/MeasurementsHistory.vue') },
      ],
    },
  ],
})

// Navigating to any motor page shows the confirmation dialog (in App.vue).
// Only PeristalticMotorCalibration → PeristalticMotor (Finish Calibration) passes without dialog.
const MOTOR_ROUTE_NAMES = ['TiltMotor', 'RotaryMotor', 'PeristalticMotor']

let skipMotorConfirm = false
export const navigationConfirmPending = ref<{ to: RouteLocationNormalized } | null>(null)

export function confirmMotorNavigation() {
  const pending = navigationConfirmPending.value
  if (pending) {
    skipMotorConfirm = true
    navigationConfirmPending.value = null
    router.push(pending.to)
  }
}

export function cancelMotorNavigation() {
  navigationConfirmPending.value = null
}

router.beforeEach((to, from, next) => {
  const isAuthenticated = authApi.isAuthenticated()

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  if (to.path === '/login' && isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  if (skipMotorConfirm) {
    skipMotorConfirm = false
    next()
    return
  }
  if (from.name === 'PeristalticMotorCalibration' && to.name === 'PeristalticMotor') {
    next()
    return
  }
  if (from.name && MOTOR_ROUTE_NAMES.includes(to.name as string)) {
    navigationConfirmPending.value = { to }
    next(false)
    return
  }

  next()
})

export default router
