<template>
  <div class="h-full flex flex-col">
    <div class="page-header">
      <h1 class="page-title"><span class="text-muted-color">Rotary Motor Control</span></h1>
    </div>

    <!-- Main content: two stacked cards filling available height -->

    <div class="grid">
      <!-- Top card: speed & duration -->

	  <div class="col-5">
  <Card class="run-config-card">
    <template #title> Run Configuration</template>
    <template #content>
      <div class="run-config-content">
        <div class="form-group flex flex-col gap-1">
          <FloatLabel class="w-full" variant="on">
            <InputText class="w-full" id="scenarioName" v-model="runConfiguration.name" />
            <label for="on_label">Scenario Name</label>
          </FloatLabel>
          <div v-for="i in runConfiguration.movements.length" :key="i">
            <Fieldset>
              <template #legend>
                <div class="flex justify-end items-center w-full">
                  <div class="mr-2">
                    <Button icon="pi pi-times-circle" size="small" severity="danger" rounded @click="removeMovementGroup(i)" />
                  </div>
                  <span>Movement Group {{ i }}</span>
                </div>
              </template>
              <div v-if="runConfiguration.movements.length > 0" class="grid">
				<div class="col">
					<FloatLabel variant="on" >
					<InputNumber class="w-full"
						:min="0"
						:max="10"
						:step="0.1"
						v-model="runConfiguration.movements[i-1].rpm" />
					<label>Speed (RPM)</label>
					</FloatLabel>
				</div>

				<div class="col">
					<FloatLabel variant="on" >
					<InputNumber class="w-full"
						v-model="runConfiguration.movements[i-1].duration" />
					<label>Duration (s)</label>
					</FloatLabel>
				</div>

				<div class="col">
					<FloatLabel variant="on" >
					<Select class="w-full"
						v-model="runConfiguration.movements[i-1].direction"
						:options="directionOptions"
						optionLabel="label"
						optionValue="value" />
					<label>Direction</label>
					</FloatLabel>
				</div>
              </div>
            </Fieldset>
          </div>
          <div class="mt-2 flex justify-center">
            <Button icon="pi pi-plus-circle" size="small" severity="primary" rounded @click="addMovementGroup" />
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="run-config-footer">
        <div class="flex justify-end">
          <Button v-if="runConfiguration && !isRotating && !rotatePaused" severity="secondary" class="ml-2 btn" @click="handleExportScenario">Export</Button>
          <Button v-if="!isRotating && !rotatePaused && scenarios.find(el => el.id === runConfiguration.scenario_id && el.name === runConfiguration.name)" severity="secondary" class="ml-2 btn" @click="handleUpdateScenario">Update Rotation Scenario</Button>
          <Button v-if="!isRotating && !rotatePaused && !scenarios.find(el => el.id === runConfiguration.scenario_id && el.name === runConfiguration.name)" severity="info" class="ml-2 btn" @click="handleSaveScenario">Save Rotation Scenario</Button>
          <Button v-if="!isRotating && !rotatePaused" class="ml-2 btn" @click="rotateMotor">Rotate Motor</Button>
          <div v-if="isRotating">
            <Button v-if="!rotatePaused" class="btn mr-2" severity="info" @click="pauseRotating">Pause Rotating</Button>
            <Button v-if="rotatePaused" class="btn mr-2" severity="secondary" @click="resumeRotating">Resume Rotating</Button>
            <Button class="btn" severity="danger" @click="stopRotating">Stop Motor</Button>
          </div>
        </div>
      </div>
    </template>
  </Card>
</div>
	<div class="col-7">
		<Card>
      <template #title> <span class="text-muted-color">Real-time Rotary Movements</span> <span class="ml-4 text-sm ">Movement: {{ currentMovement }}</span></template>
        <template #content>
          <MovementsChart
            :key="runId"
            :isMoving="isRotating"
            :scenario_name="runConfiguration.name"
            :runId="runId"
            :maxVal="movementsMaxRPM"
            :minVal="-movementsMaxRPM"
			      :chartHeight="460"
			      :type="1"
          />
        </template>
      </Card>

	</div>
      <!-- Bottom card: MovementsChart fills remaining space -->
	<div class="col-12">
		<Card>
        <template #title> Move Scenarios </template>
        <template #content>
          <div v-if="scenariosError" class="alert alert-danger">
            {{ scenariosError }}
          </div>
          <div  v-else>
			      <div class="flex justify-end m-1">
					<FileUpload @select="handleFileSelect" mode="basic" name="importScenario" customUpload auto chooseLabel="Import" />
				    </div>
            <div class="overflow-auto table-responsive">

			<DataTable
			v-if="scenarios.length > 0"
			:value="scenarios"
			v-model:expandedRows="expandedRows"
			tableStyle="min-width: 55rem"
			>
			<!-- Fix: Remove "expander" prop and custom template -->
      <Column expander style="width: 3rem">
        <template #body="slotProps">
          <Button
            v-if="slotProps.data.movements && slotProps.data.movements.length > 1"
            icon="pi pi-chevron-right"
            text
            rounded
            @click="toggleRow(slotProps.data)"
            :class="{ 'rotate-45': isRowExpanded(slotProps.data) }"
          />
        </template>
      </Column>


			<Column field="imported" header="DB" style="width: 4%">
				<template #body="slotProps">
				<i class="pi pi-database" v-if="!slotProps.data.imported"></i>
				</template>
			</Column>

			<Column field="name" header="Name" />

			<Column header="Speed (RPM)">
				<template #body="slotProps">
				{{ slotProps.data.movements?.[0]?.rpm ?? '-' }}
				</template>
			</Column>

			<Column header="Duration (s)">
				<template #body="slotProps">
				{{ slotProps.data.movements?.[0]?.duration ?? '-' }}
				</template>
			</Column>

			<Column header="Direction">
				<template #body="slotProps">
				{{ directionOptions.find(option => option.value === slotProps.data.movements?.[0]?.direction)?.label ?? '-' }}
				</template>
			</Column>

      <Column class="" field="actions" style="width: 15%" header="Actions"> <template #body="slotProps">
                    <Button icon="pi pi-pencil" style="width: 60px" severity="primary" class="ml-1 btn" @click="loadScenario(slotProps.data)"> Load </Button>
                    <Button icon="pi pi-trash" style="width: 60px" class="ml-2 btn" severity="danger" @click="deleteScenarioModalActive = true; removeId = slotProps.data.id"> Delete </Button>
                  </template> </Column>

			<template #expansion="slotProps">
				<div v-if="slotProps.data.movements && slotProps.data.movements.length > 1" class="p-3 ml-6">
				<h4 class="mb-2">Movements</h4>
				<DataTable :value="slotProps.data.movements" size="small">
					<Column field="rpm" header="Speed (RPM)" />
					<Column field="duration" header="Duration (s)" />
					<Column field="direction" header="Direction">
            <template #body="slotProps">
              {{ directionOptions.find(option => option.value === slotProps.data.direction)?.label ?? '-' }}
            </template>
          </Column>
				</DataTable>
				</div>
			</template>
			</DataTable>
            </div>
          </div>
        </template>
      </Card>
	</div>
    </div>
<div>      <Dialog v-model:visible="deleteScenarioModalActive" modal header="Delete Scenario" :style="{ width: '25vw' }">
			<span class="text-surface-500 block mb-8">Are you sure you want to delete this scenario?</span>
        <div class="flex justify-end gap-2">
          <Button label="Cancel" severity="secondary" outlined @click="deleteScenarioModalActive = false;" />
          <Button label="Delete" severity="danger" @click="removeScenario(removeId.toString()); deleteScenarioModalActive = false; removeId = 0" />
        </div>
      </Dialog></div>
	  <div
	v-if="deleteScenarioModalActive"
	class="modal-overlay"
	@click.self="deleteScenarioModalActive = false"
  >
  </div>
  <Toast></Toast>
	</div>
  </template>

  <script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, computed } from "vue";
  import { rotaryMotorApi, type MotorStatus, type RotationScenario, RotationConfiguration } from "../api";
  import MovementsChart from "../components/MovementsChart.vue";
  import Button from 'primevue/button';
  import Card from 'primevue/card';
  import FloatLabel from 'primevue/floatlabel';
  import InputNumber from 'primevue/inputnumber';
  import InputText from 'primevue/inputtext';
  import Dialog from 'primevue/dialog';
  import Select from 'primevue/select';
  import DataTable from 'primevue/datatable';
  import Column from 'primevue/column';
  import FileUpload from 'primevue/fileupload';
  import Fieldset from 'primevue/fieldset';

  import Toast from 'primevue/toast';
  import { useToast } from 'primevue/usetoast';
  const toast = useToast();
  const showSuccess = (message: string) => {
    toast.add({
    severity: 'success', // 'success', 'info', 'warn', 'error'
    summary: 'Success',
    detail: message,
    life: 3000 // milliseconds (optional)
    });
  }
  const showError = (message: string) => {
    toast.add({
    severity: 'error', // 'success', 'info', 'warn', 'error'
    summary: 'Error',
    detail: message,
    life: 3000 // milliseconds (optional)
    });
  }

  const status = ref<MotorStatus | null>(null);
  const isRotating = ref(false);
  const rotatePaused = ref(false);
  const currentMovement = ref(0);
  const runId = ref(0);
  let statusInterval: number | null = null;

  const directionOptions = ref([
	{ label: 'Clockwise', value: "cw" },
	{ label: 'Counter clockwise', value: "ccw" },
  ]);
  const runConfiguration = ref<RotationConfiguration>({
	name: "",
	scenario_id: null,
	movements: [
		{
			duration: null,
			direction: null,
			rpm: null,
		},
	],
  });

  const scenarios = ref<RotationScenario[]>([]);
  const expandedRows = ref([]);

  const toggleRow = (rowData) => {
    const index = expandedRows.value.findIndex(r => r === rowData);
    if (index !== -1) {
      expandedRows.value.splice(index, 1);
    } else {
      expandedRows.value.push(rowData);
    }
  };


  const isRowExpanded = (rowData) => {
    return expandedRows.value.some(r => r.id === rowData.id);
  };

  const scenariosError = ref<string | null>(null);
  const deleteScenarioModalActive = ref(false);
  const removeId = ref(0);


  const timeElapsed = ref(0.0);


  // WebSocket
  const socket = ref<WebSocket | null>(null);
  const setupWebSocket = () => {
	if (socket.value) {
	  socket.value.close();
	  socket.value = null;
	}
	socket.value = new WebSocket("ws://" + window.location.hostname + ":8000/ws/motor");
	socket.value.onopen = () => {
	};
	socket.value.onmessage = (event: MessageEvent) => {
		const msg = JSON.parse(event.data);
	  if (msg.type === "rotate") {
		if (msg.data.rotate_stopped) {
		  isRotating.value = false;
		  rotatePaused.value = false;
		}
	  }
	  if (msg.type === "rotate_movement") {
		currentMovement.value = msg.data.movement;
	  }
	};
  };
  const handleFileSelect = (event: any) => {
  // PrimeVue FileUpload passes files in event.files
  const files = event?.files || [];
  const file = files[0];

  if (!file) {
    return;
  }

  // Check if it's a JSON file
  const isJsonFile = file.type === 'application/json' ||
                     file.name?.toLowerCase().endsWith('.json');

  if (!isJsonFile) {
    console.error('Invalid file type. Please select a JSON file.');
    return;
  }

  const reader = new FileReader();

  reader.onload = (e: ProgressEvent<FileReader>) => {
    try {
      const content = e.target?.result as string;

      if (!content) {
        console.error('File content is empty');
        return;
      }

      const data = JSON.parse(content);

      // Validation function
      const validateRotationScenario = (obj: any): boolean => {
        // Check if it's an object
        if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
          showError('Invalid format: Root must be an object');
          return false;
        }

        // Check for "name" field - must be a string
        if (!('name' in obj) || typeof obj.name !== 'string') {
          showError('Invalid format: "name" field is required and must be a string');
          return false;
        }

        // Check for "movements" field - must be an array
        if (!('movements' in obj) || !Array.isArray(obj.movements)) {
          showError('Invalid format: "movements" field is required and must be an array');
          return false;
        }

        // Validate each movement in the array
        for (let i = 0; i < obj.movements.length; i++) {
          const movement = obj.movements[i];

          if (!movement || typeof movement !== 'object' || Array.isArray(movement)) {
            showError(`Invalid format: Movement at index ${i} must be an object`);
            return false;
          }

          // Check for required fields
          if (!('duration' in movement) || typeof movement.duration !== 'number') {
            showError(`Invalid format: Movement at index ${i} must have "duration" as a number`);
            return false;
          }

          if (!('direction' in movement) || typeof movement.direction !== 'string') {
            showError(`Invalid format: Movement at index ${i} must have "direction" as a string`);
            return false;
          }

          if (!('rpm' in movement) || typeof movement.rpm !== 'number') {
            showError(`Invalid format: Movement at index ${i} must have "rpm" as a number`);
            return false;
          }
        }
        return true;
      };

      // Validate the data
      if (!validateRotationScenario(data)) {
        showError('JSON file does not match the required format');
        // You can also show a user-friendly error message here
        // For example, using a toast notification or setting an error state
        return;
      }

      // If validation passes, add to scenarios
      scenarios.value.push({
        name: data.name,
        movements: data.movements,
        imported: true,
      });
      showSuccess("Scenario imported successfully.");

    } catch (error) {
      if (error instanceof SyntaxError) {
        showError('Invalid JSON syntax');
      }
    }
  };


  reader.onabort = () => {
    showError('File reading was aborted');
  };

  try {
    reader.readAsText(file);
  } catch (error) {
  }
};

  const fetchStatus = async () => {
	try {
	  status.value = await rotaryMotorApi.getStatus();
    if (status.value?.is_moving) {
      isRotating.value = true;
    } else isRotating.value = false;
	} catch (err: any) {
	}
  };

  const movementsMaxRPM = computed(() => {
    return runConfiguration.value.movements.reduce((max, movement) => {
      return Math.max(max, movement.rpm ?? 3);
    }, 0);
  });

  const rotateMotor = async () => {
	try {
	  runId.value++;
	  const entry_name = `entry_${new Date().toISOString().replace(/[-:.]/g, "").slice(0,15)}`;
	timeElapsed.value = performance.now();
	  const response = await rotaryMotorApi.rotateMotor(entry_name, {...runConfiguration.value});
	  isRotating.value = response.success
	} catch (err: any) {
      showError("Error with starting rotating.")
	} finally {
    showSuccess("Motor started rotating successfully.")
	}
  };

  const resumeRotating = async () => {
	try {
	  const response = await rotaryMotorApi.resumeRotate(currentMovement.value);
	  rotatePaused.value = false;
	} catch (err: any) {
      showError("Error with resuming rotating.")
	} finally {
    showSuccess("Motor resumed rotating successfully.")
	}
  };

  const pauseRotating = async () => {
	try {
	  const response = await rotaryMotorApi.pauseRotate();
	  rotatePaused.value = true;
	} catch (err: any) {
      showError("Error with pausing rotating.")
	} finally {
    showSuccess("Motor paused successfully.")
	}
  };

  const stopRotating = async () => {
	try {
	  await rotaryMotorApi.stopRotate();
	  timeElapsed.value = performance.now() - timeElapsed.value;
	  rotatePaused.value = false;
	} catch (err: any) {
      showError("Error with stopping rotating.")
	} finally {
    showSuccess("Motor stopped successfully.")
	}
  };
  const fetchScenarios = async () => {
	try {
	  scenariosError.value = null;
	  scenarios.value = await rotaryMotorApi.getRotationScenarios();
	} catch (err: any) {
	  scenariosError.value =
		err.response?.data?.detail || err.message || "Failed to fetch scenarios";
	  console.error("Error fetching scenarios:", err);
	} finally {
	}
  };

  const loadScenario = (scenario: RotationScenario) => {
  runConfiguration.value = {
    scenario_id: scenario.id || null,
    ...scenario,
  }
};

  const removeScenario = async (scenarioId: string) => {
	try {
	  const response = await rotaryMotorApi.removeRotationScenario(scenarioId);
	  if (response.success) {
		fetchScenarios();
	  }
	} catch (err: any) {
      showError("Error with deleting scenario.")
	} finally {
      showSuccess("Scenario deleted successfully.")
	}
  };

  const handleUpdateScenario = async () => {
    try {
      const response = await rotaryMotorApi.updateRotationScenario(runConfiguration.value.scenario_id, { ...runConfiguration.value});
    } catch (err: any) {
      showError("Error with updating scenario.")
    } finally {
      showSuccess("Scenario updated successfully.")
      fetchScenarios();
    }
  };
  const handleSaveScenario = async () => {
  try {

    const response = await rotaryMotorApi.saveRotationScenario({
      id: null,
      name: runConfiguration.value.name,
      movements: runConfiguration.value.movements,
    })
    if (response.success) {
      await fetchScenarios()
      // optionally: find the new scenario by response.rotation_scenario_id and call loadScenario on it
    }
  } catch (err: any) {
    showError("Error with saving scenario.")
  } finally {
    showSuccess("Scenario saved successfully.")
  }
}

  const addMovementGroup = () => {
	runConfiguration.value.movements.push({
	  duration: null,
	  direction: null,
	  rpm: null,
	});
  };

  const removeMovementGroup = (groupId: number) => {

	runConfiguration.value.movements.splice(groupId - 1, 1);
  };

  const handleExportScenario = () => {
  try{
    const scenario = {
      name: runConfiguration.value.name,
      movements: runConfiguration.value.movements,
    };
    const json = JSON.stringify(scenario, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${scenario.name}.json`;
    a.click();
    URL.revokeObjectURL(url);

  } catch (err: any) {
    showError("Error with exporting scenario.")
  } finally {
    showSuccess("Scenario exported successfully.");
  }
}
  onMounted(() => {
	setupWebSocket();
	fetchStatus();
	fetchScenarios();
	statusInterval = window.setInterval(() => {
	  fetchStatus();
	}, 2000);
  });

  onBeforeUnmount(() => {
	if (statusInterval) {
	  clearInterval(statusInterval);
	}
	if (socket.value) {
	  socket.value.close();
	  socket.value = null;
	}
  });


  </script>

  <style scoped>

	/* Run Configuration Card - Fixed height matching graph card */
.run-config-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.run-config-card :deep(.p-card-title) {
	margin: 1rem;
}
/* Card content wrapper - takes available space and scrolls */
.run-config-card :deep(.p-card-body) {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0; /* Important for flexbox scrolling */
  padding: 0;
}

.run-config-card :deep(.p-card-content) {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding: 1.25rem;
}

.run-config-content {
  height: 100%;
}

/* Footer - always at bottom, never moves */
.run-config-card :deep(.p-card-footer) {
  flex-shrink: 0;
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
  margin-top: auto;
}

.run-config-footer {
  width: 100%;
}

/* Match the graph card height (500px chart + card padding/header/footer) */
.run-config-card {
  height: calc(500px + 4rem); /* Adjust based on your card header/footer heights */
}

/* Or if you want it to match exactly, use the same height as the graph card */
.col-5 .run-config-card,
.col-7 .p-card {
  height: calc(500px + 4rem);
}

  .h-full {
	height: 100%;
	display: flex;
	flex-direction: column;
  }

  .page-header {
	flex-shrink: 0;
  }

  .page-title {
	font-size: 2rem;
	font-weight: 700;
	color: var(--text-primary);
  }



  .alert {
	position: relative;
	padding-right: 2rem;
  }

  .alert-close {
	position: absolute;
	top: 0.5rem;
	right: 0.5rem;
	background: none;
	border: none;
	font-size: 1.5rem;
	line-height: 1;
	cursor: pointer;
	color: inherit;
	opacity: 0.7;
  }

  .alert-close:hover {
	opacity: 1;
  }

  .table-empty {
	text-align: center;
	color: var(--text-secondary);
	padding: 2rem !important;
  }

  .modal-close {
	background: none;
	border: none;
	font-size: 1.5rem;
	line-height: 1;
	cursor: pointer;
	color: var(--text-secondary);
	padding: 0;
	width: 2rem;
	height: 2rem;
	display: flex;
	align-items: center;
	justify-content: center;
  }

  .modal-close:hover {
	color: var(--text-primary);
  }
  </style>
