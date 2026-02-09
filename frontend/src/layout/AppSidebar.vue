<script setup>
import AppMenu from './AppMenu.vue';
import { Card, Button } from 'primevue';
import { computed, onMounted, onBeforeUnmount, ref } from 'vue';

const showNewReleaseWarning = ref(false);
let statusInterval;

onBeforeUnmount(() => {
  if (statusInterval) {
    clearInterval(statusInterval);
  }
});

const openReleasePage = () => {
  window.open('https://github.com/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/releases/latest', '_blank');
};

const url = `https://api.github.com/repos/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/releases/latest`;
async function checkLatestRelease() {
  const res = await fetch(url, {
    headers: {
      "Accept": "application/vnd.github+json",
    },
  });

  if (!res.ok) {
    throw new Error(`GitHub API error: ${res.status}`);
  }

  const release = await res.json();

  showNewReleaseWarning.value = release.tag_name !== localStorage.getItem('latest_release');
  localStorage.setItem('latest_release', release.tag_name);
}

onMounted(() => {
  checkLatestRelease();
  statusInterval = window.setInterval(() => {
    checkLatestRelease();
  }, 1.08e+7);
})
</script>

<template>
    <Card class="layout-sidebar">
      <template #content>
        <div class="sidebar-content">
          <app-menu></app-menu>
          <div class="sidebar-warning" style="display: flex; justify-content: flex-end;">
            <Button v-if="showNewReleaseWarning"
            icon="pi pi-exclamation-triangle"
            label="Update available"
            severity="warn"
            size="small"
            @click="openReleasePage"
          />
          </div>
        </div>
      </template>
    </Card>
</template>

<style lang="scss" scoped>
.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-warning {
  margin-top: 2rem;
}
</style>
