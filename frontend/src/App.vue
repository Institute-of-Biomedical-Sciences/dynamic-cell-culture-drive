<template>
  <div id="app">
    <router-view />

    <!-- Navigation Confirmation Dialog -->
    <Dialog
      v-model:visible="showNavigationDialog"
      modal
      header="You are about to switch motor control."
      :style="{ width: '30rem' }"
    >
      <p>Please confirm that the correct motor is connected before continuing.</p>
      <template #footer>
        <Button label="Cancel" severity="secondary" icon="pi pi-times" @click="cancelNavigation" text />
        <Button label="Confirm" icon="pi pi-check" @click="confirmNavigation" autofocus />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const router = useRouter()
const showNavigationDialog = ref(false)
let pendingNavigation: (() => void) | null = null

onMounted(() => {
  router.beforeEach((to, from, next) => {
    // Skip confirmation for initial load or if route has skipConfirm meta
    if (from.name === null || to.meta.skipConfirm) {
      next()
      return
    }

    // Skip if navigating to the same route
    if (to.path === from.path) {
      next()
      return
    }
    // Store the navigation function and show dialog
    pendingNavigation = () => next()
    if (to.name === 'TiltMotor' || to.name === 'RotaryMotor' || to.name === 'PeristalticMotor') {
      showNavigationDialog.value = true
    } else {
      next()
    }
  })
})

const confirmNavigation = () => {
  showNavigationDialog.value = false
  if (pendingNavigation) {
    pendingNavigation()
    pendingNavigation = null
  }
}

const cancelNavigation = () => {
  showNavigationDialog.value = false
  pendingNavigation = null
}
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
