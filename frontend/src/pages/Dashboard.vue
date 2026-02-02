<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title"><span class="text-muted-color">Dashboard</span></h1>
    </div>

    <div class="dashboard-grid">
      <Card class="card">
        <template #content>
          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>
          <div v-else class="status-content">
            <div class="status-item">
              <strong>Status:</strong>
              <span :class="`badge badge-${statusBadgeVariant}`">
                {{ status?.status?.toUpperCase() || "Unknown" }}
              </span>
            </div>
            <div class="status-item">
              <strong>Position:</strong>
              <span>{{ status?.position ?? "N/A" }}°</span>
            </div>
            <div class="status-item">
              <strong>Moving:</strong>
              <span
                :class="`badge badge-${
                  status?.is_moving ? 'warning' : 'success'
                }`"
              >
                {{ status?.is_moving ? "Yes" : "No" }}
              </span>
            </div>
            <div class="status-item">
              <strong>Initialized:</strong>
              <span
                :class="`badge badge-${
                  status?.initialized ? 'success' : 'danger'
                }`"
              >
                {{ status?.initialized ? "Yes" : "No" }}
              </span>
            </div>
          </div>
        </template>
        <template #footer>
          <div class=" flex justify-end mt-5">
          <Button class="btn mt-2 flex justify-end" @click="goToTiltMotor">Go to Tilt Motor Control</Button>
					</div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { tiltMotorApi, type MotorStatus } from "../api";
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import Card from 'primevue/card';
const router = useRouter();
const status = ref<MotorStatus | null>(null);
const error = ref<string | null>(null);
let interval: number | null = null;

const statusBadgeVariant = computed(() => {
  if (!status.value) return "secondary";
  switch (status.value.status) {
    case "idle":
      return "success";
    case "moving":
      return "warning";
    case "error":
      return "danger";
    default:
      return "secondary";
  }
});

const goToTiltMotor = () => {
  router.push({ name: 'TiltMotor' });
}

const fetchStatus = async () => {
  try {
    error.value = null;
    status.value = await tiltMotorApi.getStatus();
  } catch (err: any) {
    error.value =
      err.response?.data?.detail || err.message || "Failed to fetch status";
    console.error("Error fetching status:", err);
  } finally {
  }
};

onMounted(() => {
  fetchStatus();
  interval = window.setInterval(() => {
    fetchStatus();
  }, 2000);
});

onBeforeUnmount(() => {
  if (interval) {
    clearInterval(interval);
  }
});
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
}

.status-item:last-child {
  border-bottom: none;
}

.status-item strong {
  color: var(--text-secondary);
  font-weight: 500;
}
</style>
