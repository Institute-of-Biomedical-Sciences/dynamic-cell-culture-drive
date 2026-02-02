import { createRouter, createWebHistory } from 'vue-router'
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
        {
          path: '/',
          name: 'Dashboard',
          component: () => import('@/pages/Dashboard.vue'),
        },
        {
          path: '/tilt-motor',
          name: 'TiltMotor',
          component: () => import('@/pages/TiltMotor.vue'),
        },
        {
          path: '/rotary-motor',
          name: 'RotaryMotor',
          component: () => import('@/pages/RotaryMotor.vue'),
        },
        {
          path: '/peristaltic-motor-calibration',
          name: 'PeristalticMotorCalibration',
          component: () => import('@/pages/PeristalticMotorCalibration.vue'),
        },
        {
          path: '/peristaltic-motor-tube-configurations',
          name: 'PeristalticMotorTubeConfigurations',
          component: () => import('@/pages/PeristalticMotorTubeConfigurations.vue'),
        },
        {
          path: '/peristaltic-motor',
          name: 'PeristalticMotor',
          component: () => import('@/pages/PeristalticMotor.vue'),
        },
        {
          path: '/measurements-history',
          name: 'MeasurementsHistory',
          component: () => import('@/pages/MeasurementsHistory.vue'),
        },
      ],
    },
  ],
})

// Auth guard - redirect to login if not authenticated
router.beforeEach((to, from, next) => {
  const isAuthenticated = authApi.isAuthenticated()

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login with return path
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  } else if (to.path === '/login' && isAuthenticated) {
    // If already logged in, redirect to dashboard
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
