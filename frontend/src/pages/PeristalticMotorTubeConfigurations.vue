<template>
	<div class="h-full flex flex-col min-h-0">
	  <div class="page-header flex-shrink-0">
		  <h1 class="page-title"><span class="text-muted-color">Peristaltic Tube Configurations</span></h1>
		</div>
	<div class="flex w-full flex-1 min-h-0">
		<Card style="height: 81.5vh;" class="w-full calibration-card">
			<template #title> Peristaltic Motor Tube Configurations</template>
			<template #content>
				<div class="mb-2 ml-4">
				<span class="text-md border-round-lg p-2 bg-gray-100 text-gray-500 ">The preset tube configuration ml/rotation is calculated by formula: ( 51/4 * π² * diameter² ) / 1000</span>
			</div>
			<div class="flex justify-end">
				<Button label="Add" icon="pi pi-plus" @click="showAddDialog = true" />
			</div>
			<DataTable editMode="row"  v-model:editingRows="editingRows" @row-edit-save="onRowEditSave" :value="tubeConfigurations">
				<Column field="name" header="Name" />
				<Column field="diameter" header="Diameter">
					<template #body="slotProps">
						{{ slotProps.data.diameter > 0 ? slotProps.data.diameter.toFixed(2) : ' - ' }}
					</template>
				</Column>
				<Column field="flow_rate" header="mL/rotation">
					<template #body="slotProps">
						{{ slotProps.data.flow_rate.toFixed(3) }}
					</template>
					<template #editor="{ data, field }">
						<template v-if="field === 'flow_rate'">
							<InputNumber
							style="width: 70px; height: 25px; padding: 0px; margin: 0px;"
							v-model="data[field]"
							:minFractionDigits="0" :maxFractionDigits="3"
							:min="0"
							:step="0.001"
							autofocus
							fluid
							/>
						</template>
					</template>
				</Column>
				<Column field="preset" header="Preset" >
					<template #body="slotProps">
						<Tag :value="slotProps.data.preset ? 'Preset' : 'Custom'" :severity="slotProps.data.preset ? 'success' : 'warn'" />
					</template>
			    </Column>
				<Column :rowEditor="true" style="width: 10%; min-width: 8rem" bodyStyle="text-align:center"></Column>
			</DataTable>
			</template>
		</Card>
	</div>
	</div>
	<Dialog modal v-model:visible="showAddDialog" header="Add Tube Configuration" :style="{ width: '30rem' }">
		<div class="flex flex-col my-2 gap-2">
			<FloatLabel class="w-full" variant="on" >
				<Select class="w-full" v-model="newTubeConfiguration.preset" :options="presetOptions" optionLabel="label" optionValue="value" />
				<label>Preset</label>
			</FloatLabel>
		</div>
		<div v-if="newTubeConfiguration.preset">
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputText class="w-full" v-model="newTubeConfiguration.name" />
					<label >Name</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber :min="0" :max="10" :step="0.01" :minFractionDigits="0" :maxFractionDigits="2" class="w-full" v-model="newTubeConfiguration.diameter" />
					<label>Diameter</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber :min="0" :max="1000" :step="0.001" :minFractionDigits="0" :maxFractionDigits="2" class="w-full" v-model="newTubeConfiguration.flow_rate" />
					<label>Flow Rate</label>
				</FloatLabel>
			</div>
		</div>
		<div v-else>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber class="w-full" v-model="newPeristalticCalibration.duration" />
					<label>Duration</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber class="w-full" v-model="newPeristalticCalibration.low_rpm" />
					<label>Low RPM</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber class="w-full" v-model="newPeristalticCalibration.high_rpm" />
					<label>High RPM</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber :minFractionDigits="0" :maxFractionDigits="2" class="w-full" v-model="newPeristalticCalibration.low_rpm_volume" />
					<label>Low RPM Volume</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputNumber :minFractionDigits="0" :maxFractionDigits="2" class="w-full" v-model="newPeristalticCalibration.high_rpm_volume" />
					<label>High RPM Volume</label>
				</FloatLabel>
			</div>
			<div class="flex flex-col mb-2 gap-2">
				<FloatLabel class="w-full" variant="on" >
					<InputText class="w-full" v-model="newPeristalticCalibration.name" />
					<label>Filename</label>
				</FloatLabel>
			</div>
		</div>
		<template #footer>
		<Button
		  label="Cancel"
		  severity="secondary"
		  outlined
		  @click="showAddDialog = false"
		/>
		<Button
		  label="Add"
		  severity="primary"
		  @click="addTubeConfiguration()"
		/>
	  </template>
	</Dialog>
	<Toast></Toast>
</template>

<script setup lang="ts">
import { type TubeConfiguration, type PeristalticCalibration, type ApiResponse } from '../api';
import InputNumber from 'primevue/inputnumber';
import { ref, onMounted } from 'vue';
import { peristalticMotorApi } from '../api';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import FloatLabel from 'primevue/floatlabel';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';

const tubeConfigurations = ref<TubeConfiguration[]>([]);
const calibrations = ref<PeristalticCalibration[]>([]);

// add new config variables
const showAddDialog = ref(false);
const presetOptions = ref([
	{ label: 'Preset', value: true },
	{ label: 'Custom', value: false },
]);
const newTubeConfiguration = ref<TubeConfiguration>({
	id: null,
	name: '',
	diameter: 0.0,
	flow_rate: 0.0,
	preset: false,
});
const newPeristalticCalibration = ref<PeristalticCalibration>({
	id: null,
	duration: 0,
	low_rpm: 0,
	high_rpm: 0,
	low_rpm_volume: 0,
	high_rpm_volume: 0,
	name: '',
});

// table editing variables
const editingRows = ref([]);
const onRowEditSave = async (event: any) => {
    let { newData, index } = event;
    try {
        let response: ApiResponse;
        if (newData.preset) {
            response = await peristalticMotorApi.updateTubeConfiguration(newData);
        } else {
			let calibrationData = calibrations.value.find(calibration => calibration.name === newData.name);
			if (calibrationData) {
				response = await peristalticMotorApi.updatePeristalticCalibration({...calibrationData, slope: newData.flow_rate});
			}
        }
        if (response.success) {
            fetchTubeConfigurations();
            showSuccess('Tube configuration updated successfully');
        }
    } catch (error) {
        showError(`Error updating tube configuration: ${error}`);
    }
};

// toast functions

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

// functions
const fetchTubeConfigurations = async () => {
	try {
		const response = await peristalticMotorApi.getTubeConfigurations();
		tubeConfigurations.value = response.tube_configurations;
		calibrations.value = await peristalticMotorApi.getPeristalticCalibrations();
		for (const calibration of calibrations.value) {
			tubeConfigurations.value.push({
				id: calibration.id,
				name: calibration.name,
				diameter: 0,
				flow_rate: calibration.slope,
				preset: false,
			});
		}
	} catch (error) {
		console.error('Error fetching tube configurations:', error);
	}
};

const addTubeConfiguration = async () => {
	try {
		let response: ApiResponse;
		if (newTubeConfiguration.value.preset) {
			response = await peristalticMotorApi.saveTubeConfiguration(newTubeConfiguration.value);
		} else {
			response = await peristalticMotorApi.savePeristalticCalibration({...newPeristalticCalibration.value});
		}
		if (response.success) {
			fetchTubeConfigurations();
			showSuccess('Tube configuration added successfully');
		}
	} catch (error) {
		showError(`Error adding tube configuration: ${error}`);
	} finally {
		showAddDialog.value = false;
	}
};
onMounted(async () => {
	await fetchTubeConfigurations();
});


</script>
<style scoped>
	.h-full {
		height: 100%;
		display: flex;
		flex-direction: column;
		min-height: 0;
	}

	.page-header {
		flex-shrink: 0;
	}


	.calibration-card :deep(.p-card-body) {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 0;
		overflow: hidden;
	}

	.calibration-card :deep(.p-card-content) {
		flex: 1;
		overflow: auto;
		min-height: 0;
	}
</style>
