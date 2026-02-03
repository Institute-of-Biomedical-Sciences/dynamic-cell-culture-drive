<template>
  <div class="h-full">
    <div class="page-header">
      <h1 class="page-title"><span class="text-muted-color">Measurements History</span></h1>
    </div>

    <div class="grid grid-cols-3 control-grid">
      <!-- Entry selection + chart -->
      <Card class="col-span-3">
        <template #content>
          <div class="form-group mb-4">
            <label for="entrySelect" class="form-label">Entry</label>
            <Select v-model="selectedEntry" :options="entries" optionLabel="name" placeholder="Select a measurement entry" class="w-full md:w-56" >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex align-items-center">
                  <span>{{ slotProps.value.type === 0 ? 'tilt' : slotProps.value.type === 1 ? 'rotate' : 'peristaltic' }}_{{ slotProps.value.scenario_name }}_{{ formatTimestamp(slotProps.value.measurement_timestamp) }}</span>
                </div>
                <span v-else class="text-muted">Select measurement entry</span>
              </template>
              <template #option="slotProps">
                <div class="flex align-items-center">
                  <span>{{ slotProps.option.type === 0 ? 'tilt' : slotProps.option.type === 1 ? 'rotate' : 'peristaltic' }}_{{ slotProps.option.scenario_name }}_{{ formatTimestamp(slotProps.option.measurement_timestamp) }} </span>
                </div>
              </template>
            </Select>
          </div>

          <div v-if="measurementsError" class="alert alert-danger mb-4">
            {{ measurementsError }}
          </div>
          <div v-if="selectedEntry && seriesData.length > 0">
            <apexchart
              :key="selectedEntry?.id"
              type="line"
              :options="chartOptions"
              :series="series"
              height="675px"
            />
          </div>
          <div v-else-if="selectedEntry">
            <p class="text-muted">No measurements found for this entry.</p>
          </div>
          <div v-else>
            <p class="text-muted">Select an entry to view its measurements.</p>
          </div>
        </template>
      </Card>
    </div>
  </div>
    <!-- Filename Modal -->
    <Dialog
    v-model:visible="showFilenameModal"
    modal
    header="Set Filename"
    :style="{ width: '25rem' }"
  >
  <FilenameModal
    :type="selectedEntry?.type ?? 0"
    :scenarioName="selectedEntry?.scenario_name ?? ''"
    :endTimestamp="formatTimestamp(selectedEntry?.measurement_timestamp ?? '')"
    :visible="showFilenameModal"
    :prefix="filenamePrefix"
    @update:visible="val => (showFilenameModal = val)"
    @confirm="({ prefix, filename }) => { filenamePrefix = prefix; downloadCsv(filename) }"
  />
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { EntryResponse, peristalticMotorApi, rotaryMotorApi, tiltMotorApi } from "../api";
import Card from 'primevue/card';
import Dialog from 'primevue/dialog';
import FilenameModal from "../components/FilenameModal.vue";
import Select from 'primevue/select';

const entries = ref<any[]>([]);
const selectedEntry = ref<EntryResponse | null>(null);
const measurementsError = ref<string | null>(null);
const showFilenameModal = ref(false);
const filenamePrefix = ref('');
const maxDataPoints = 1000;

const seriesData = ref([] as Array<{ x: number; y: number }>);

const series = computed(() => [
  {
    name: selectedEntry.value?.type === 0 ? "Angle" : selectedEntry.value?.type === 1 ? "RPM" : "RPM",
    data: seriesData.value,
  },
]);

const chartOptions = computed(() => {
  const type = selectedEntry.value?.type ?? 0;
  const minVal = type === 0 ? -20 : type === 1 ? -12 : -100;
  const maxVal = type === 0 ? 20 : type === 1 ? 12 : 100;

  return {
    chart: {
      type: "line",
      height: 350,
      animations: {
        enabled: false,
      },
      toolbar: {
        show: true,
        tools: {
          download: false,
          customIcons: [
            {
              icon: '<span style="margin-left: 4px; padding: 2px 4px 2px 4px; font-size: 12px; border: 1px solid #6e8192; border-radius: 8px;">CSV</span>',
              title: 'Download CSV',
              index: 5,
              class: 'custom-csv-download',
              appendTo: 'right',
              click: () => {
                showFilenameModal.value = true;
              },
            },
          ],
        },
      },
      zoom: {
        enabled: true,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "smooth",
      width: 2,
    },
    title: {
      text: type === 0 ? "Tilt Angle History" : type === 1 ? "Rotary Speed History" : type === 2 ? "Peristaltic Speed History" : "Movements History",
      align: "left",
    },
    xaxis: {
      type: "numeric",
      title: {
        text: "Time (from start)",
      },
    },
    yaxis: {
      title: {
        text: type === 0 ? "Angle" : "Speed (RPM)",
      },
      min: minVal,
      max: maxVal,
      labels: {
        formatter: (val: number) => {
          if (val === undefined || val === null || isNaN(val)) {
            return '0';
          }
          return val.toFixed(0);
        },
      },
    },
    tooltip: {
      y: {
        formatter: (val: number) => val.toFixed(0),
      },
    },
    legend: {
      show: true,
      position: "top",
    },
    grid: {
      borderColor: "#e7e7e7",
      row: {
        colors: ["#f3f3f3", "transparent"],
        opacity: 0.5,
      },
    },
  };
});

const downloadCsv = (customFilename?: string) => {
  const points = seriesData.value;

  const header = 'Timestamp (ms),' + (selectedEntry.value?.type === 0 ? "Angle (deg)" : selectedEntry.value?.type === 1 ? "RPM" : "RPM") + '\n';
  const rows = points
    .map((p) => {
      return `${p.x * 1000},${p.y}`;
    })
    .join('\n');

  const csv = header + rows;
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = customFilename || (selectedEntry.value?.type === 0 ? "tilt.csv" : selectedEntry.value?.type === 1 ? "rotate.csv" : "peristaltic.csv");
  a.click();
  URL.revokeObjectURL(url);
};

const formatTimestamp = (ts: string) => {
  const d = new Date(ts);
  return d.toISOString();
};

const fetchEntries = async () => {
  try {
    measurementsError.value = null;
    const tilt = await tiltMotorApi.getEntries();
    const rotary = await rotaryMotorApi.getEntries();
    const peristaltic = await peristalticMotorApi.getEntries();
    // combine the two arrays with field tilt_scenario_id and rotary_scenario_id formatt as scenario_id
    // add a field type with value 0 in case of tilt and 1 in case of rotary
    entries.value = [...tilt, ...rotary, ...peristaltic].map((e: any) => ({
      id: e.id,
      scenario_id: e.scenario_id,
      scenario_name: e.scenario_name as string | null,
      type: e.type,
      name: e.name as string,
      measurement_timestamp: e.measurement_timestamp as string,
    })) as any[];
    entries.value.sort((a, b) => new Date(b.measurement_timestamp).getTime() - new Date(a.measurement_timestamp).getTime());
  } catch (err: any) {
    measurementsError.value =
      err.response?.data?.detail ||
      err.message ||
      "Failed to fetch entries";
    console.error("Error fetching entries:", err);
  }
};

const fetchMeasurements = async (entry: any) => {
  if (!entry) {
    seriesData.value = [];
    return;
  }

  try {
    measurementsError.value = null;
    let measurements: any[] = [];
    if (entry.type === 0) {
      measurements = await tiltMotorApi.getMeasurements(entry.id, entry.scenario_id, maxDataPoints);
    } else if (entry.type === 1) {
      measurements = await rotaryMotorApi.getMeasurements(entry.id, entry.scenario_id, maxDataPoints);
    } else if (entry.type === 2) {
      measurements = await peristalticMotorApi.getMeasurements(entry.id, entry.scenario_id, maxDataPoints);
    }

    seriesData.value = measurements.map((m) => ({
      x: m.time,
      y: entry.type === 0 ? m.angle : entry.type === 1 ? m.speed : m.speed,
    }));
  } catch (err: any) {
    measurementsError.value =
      err.response?.data?.detail ||
      err.message ||
      "Failed to fetch measurements";
    console.error("Error fetching measurements:", err);
    seriesData.value = [];
  }
};

watch(
  () => selectedEntry.value,
  (newEntry) => {
    if (newEntry) {
      fetchMeasurements(newEntry);
    } else {
      seriesData.value = [];
    }
  }
);

onMounted(() => {
  fetchEntries();
});

</script>

<style scoped>
  .page-header {
    margin-bottom: 2rem;
  }

  .page-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
  }

  .control-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
</style>
