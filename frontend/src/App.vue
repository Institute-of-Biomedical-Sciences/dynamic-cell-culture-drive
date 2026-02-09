<template>
  <div id="app">
    <router-view />

    <!-- Shown when router sets navigationConfirmPending (navigating to a motor page). -->
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
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { navigationConfirmPending, confirmMotorNavigation, cancelMotorNavigation } from '@/router'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const showNavigationDialog = ref(false)
let statusInterval: number | null = null;

watch(
  navigationConfirmPending,
  (pending) => {
    showNavigationDialog.value = !!pending
  },
  { immediate: true }
)

const confirmNavigation = () => {
  showNavigationDialog.value = false
  confirmMotorNavigation()
}

const cancelNavigation = () => {
  showNavigationDialog.value = false
  cancelMotorNavigation()
}

onBeforeUnmount(() => {
  if (statusInterval) {
    clearInterval(statusInterval);
  }
})
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
