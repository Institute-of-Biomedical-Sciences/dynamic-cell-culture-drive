<template>
	<div class="h-full">
	  <div class="page-header">
		  <h1 class="page-title"><span class="text-muted-color">Peristaltic Motor Calibration</span></h1>
		</div>
	<div class="flex w-full h-full">
		<Card style="height: 81.5vh;" class="w-full calibration-card">
			<template #title> Peristaltic Motor Calibration</template>
			<template #content>
						<div class="flex flex-col h-full stepper-wrapper">
							<Stepper value="1" class="stepper-container">
							<StepList>
								<Step value="1">Calibration Overview</Step>
								<Step value="2">Duration Selection</Step>
								<Step value="3">Low RPM</Step>
								<Step value="4">High RPM</Step>
								<Step value="5">File Selection</Step>
							</StepList>
							<StepPanels class=" step-panels-container">
								<StepPanel v-slot="{ activateCallback }" value="1" class="step-panel">
									<div class="flex flex-col h-100 step-panel-content">
										<Accordion value="0" class="flex-1 overflow-auto">
											<AccordionPanel value="0">
												<AccordionHeader>Step I</AccordionHeader>
												<AccordionContent>
													<p class="m-0">
														Choose the duration of the rotation movement for calibration. Unit can be selected from the dropdown menu (seconds or minutes). <br>
														Used for calculating the slope relation between rpm and flow rate.
													</p>
												</AccordionContent>
											</AccordionPanel>
											<AccordionPanel value="1">
												<AccordionHeader>Step II</AccordionHeader>
												<AccordionContent>
													<p class="m-0">
														Choose the Low RPM for the calibration movement. <br>
														After the movement is finished, measure the volume of the fluid that has passed through the tube (in mL).
													</p>
												</AccordionContent>
											</AccordionPanel>
											<AccordionPanel value="2">
												<AccordionHeader>Step III</AccordionHeader>
												<AccordionContent>
													<p class="m-0">
														Choose the High RPM for the calibration movement. <br>
														After the movement is finished, measure the volume of the fluid that has passed through the tube (in mL).
													</p>
												</AccordionContent>
											</AccordionPanel>
											<AccordionPanel value="3">
												<AccordionHeader>Step IV</AccordionHeader>
												<AccordionContent>
													<p class="m-0">
														Choose the file name for the calibration. This will be used to save the calibration data. <br>
														After clicking on the "Finish Calibration" button, the calibration data will be saved to a file.
													</p>
												</AccordionContent>
											</AccordionPanel>
										</Accordion>
									</div>
									<div class=" mt-7 pt-2 flex justify-end step-panel-footer">
										<Button label="Start" icon="pi pi-arrow-right" iconPos="right" @click="activateCallback('2'); durationProgress = 0" />
									</div>
								</StepPanel>
								<StepPanel v-slot="{ activateCallback }" value="2">
									<div class="mt-3 grid h-100">
										<div class="col-10">
											<FloatLabel class="w-full mb-1" variant="on">
												<InputNumber class="w-full" :min="0" :max="100" :step="1" v-model="peristalticMotorCalibration.duration" />
												<label for="on_label">Calibration Duration</label>
											</FloatLabel>
										</div>
										<div class="col-2">
											<FloatLabel class="w-full mb-1" variant="on">
											<Select class="w-full" :options="durationOptions" optionLabel="label" optionValue="value" v-model="selectedTimeUnit" />
											<label for="on_label">Unit</label>
											</FloatLabel>
										</div>
										<div class="col-12">
											<FloatLabel class="w-full mb-1" variant="on">
												<Select class="w-full" :options="directionOptions" optionLabel="label" optionValue="value" v-model="peristalticMotorCalibration.direction" />
												<label for="on_label">Direction Selection</label>
											</FloatLabel>
										</div>
										<div class="col-12">
											<FloatLabel class="w-full mb-1" variant="on">
												<InputNumber class="w-full" :minFractionDigits="0" :maxFractionDigits="3" :step="0.01" v-model="peristalticMotorCalibration.diameter" />
												<label for="on_label">Tube Diameter</label>
											</FloatLabel>
										</div>
										<div style="height: 300px;"></div>

									</div>
									<div class="flex mt-2 pt-6 justify-between">
										<Button label="Back" severity="secondary" icon="pi pi-arrow-left" @click="activateCallback('1'); durationProgress = 0" />
										<Button :disabled="peristalticMotorCalibration.duration === null || peristalticMotorCalibration.duration < 0" label="Next" icon="pi pi-arrow-right" iconPos="right" @click="setCalibrationDuration(); activateCallback('3'); durationProgress = 0" />
									</div>
								</StepPanel>
								<StepPanel v-slot="{ activateCallback }" value="3">
									<div class="mt-4 flex flex-col h-100">
										<FloatLabel class="w-full" variant="on">
											<InputNumber class="w-full" :min="0" :max="100" :step="1" v-model="peristalticMotorCalibration.low_rpm" />
											<label for="on_label">Low RPM</label>
										</FloatLabel>
										<div class="flex w-full justify-end">
											<Button class="mt-8 mr-2" label="Start" severity="primary" icon="pi pi-play-circle" @click="startRPMCalibration(peristalticMotorCalibration.low_rpm, peristalticMotorCalibration.duration, peristalticMotorCalibration.direction)" />
											<Button class="mt-8"  label="Stop" severity="secondary" icon="pi pi-stop-circle" @click="stopRPMCalibration()" />
										</div>
										<FloatLabel class="w-full mt-5" variant="on">
											<InputNumber :disabled="durationProgress < 100" class="w-full" :min="0" :max="100" :minFractionDigits="0" :maxFractionDigits="2" :step="0.1" v-model="peristalticMotorCalibration.low_rpm_volume" />
											<label for="on_label">Low RPM Volume (ml)</label>
										</FloatLabel>
										<div v-if="durationProgress < 100 && durationProgress > 0" class="mt-2 flex justify-center">
											<ProgressSpinner style="width: 50px; height: 50px" strokeWidth="8" fill="transparent"
												:animationDuration="durationProgress + 's'" aria-label="Custom ProgressSpinner" />
												<p class="mt-2 text-sm text-gray-500">Progress: {{ durationProgress }}%</p>
										</div>
									</div>
									<div class="flex pt-6 justify-between">
										<Button label="Back" severity="secondary" icon="pi pi-arrow-left" @click="activateCallback('2'); durationProgress = 0" />
										<Button :disabled="durationProgress < 100 || peristalticMotorCalibration.low_rpm_volume === null || peristalticMotorCalibration.low_rpm_volume < 0" label="Next" icon="pi pi-arrow-right" iconPos="right" @click="activateCallback('4'); durationProgress = 0" />
									</div>
								</StepPanel>
								<StepPanel v-slot="{ activateCallback }" value="4">
									<div class="mt-4 flex flex-col h-100">
										<FloatLabel class="w-full" variant="on">
											<InputNumber class="w-full" :min="0" :max="100" :step="1" v-model="peristalticMotorCalibration.high_rpm" />
											<label for="on_label">High RPM</label>
										</FloatLabel>
										<div class="flex w-full justify-end">
											<Button class="mt-8 mr-2" label="Start" severity="primary" icon="pi pi-play-circle" @click="startRPMCalibration(peristalticMotorCalibration.high_rpm, peristalticMotorCalibration.duration, peristalticMotorCalibration.direction)" />
											<Button class="mt-8" label="Stop" severity="secondary" icon="pi pi-stop-circle" @click="stopRPMCalibration()" />
										</div>
										<FloatLabel class="w-full mt-5" variant="on">
											<InputNumber :disabled="durationProgress < 100" class="w-full" :min="0" :max="100" :minFractionDigits="0" :maxFractionDigits="2" :step="0.1" v-model="peristalticMotorCalibration.high_rpm_volume" />
											<label for="on_label">High RPM Volume (ml)</label>
										</FloatLabel>
										<div v-if="durationProgress < 100 && durationProgress > 0" class="mt-2 flex justify-center">
											<ProgressSpinner style="width: 50px; height: 50px" strokeWidth="8" fill="transparent"
												:animationDuration="durationProgress + 's'" aria-label="Custom ProgressSpinner" />
												<p class="mt-2 text-sm text-gray-500">Progress: {{ durationProgress }}%</p>
										</div>
									</div>
									<div class="flex pt-6 justify-between">
										<Button label="Back" severity="secondary" icon="pi pi-arrow-left" @click="activateCallback('3'); durationProgress = 0" />
										<Button :disabled="durationProgress < 100 || peristalticMotorCalibration.high_rpm_volume === null || peristalticMotorCalibration.high_rpm_volume < 0" label="Next" icon="pi pi-arrow-right" iconPos="right" @click="activateCallback('5'); durationProgress = 0; computeSlope()" />
									</div>
								</StepPanel>
								<StepPanel v-slot="{ activateCallback }" value="5">
									<div class="mt-4 flex flex-col h-100">
										<FloatLabel class="w-full" variant="on">
											<InputText class="w-full" v-model="peristalticMotorCalibration.name" />
											<label for="on_label">File Name</label>
										</FloatLabel>
										<div class="mt-4">
											<apexchart
											type="line"
											:options="chartOptions"
											:series="series"
											:height="300"
											/>
										</div>
									</div>
									<div class="flex pt-6 justify-between">
										<Button label="Back" severity="secondary" icon="pi pi-arrow-left" @click="activateCallback('4'); durationProgress = 0" />
										<Button label="Finish Calibration" icon="pi pi-arrow-right" iconPos="right" @click="downloadCalibrationFile()" />
									</div>
								</StepPanel>
							</StepPanels>
						</Stepper>
						</div>
			</template>
		</Card>
	</div>
	</div>
	<Toast />
</template>
<script setup lang="ts">
	import { ref, onBeforeUnmount, computed } from 'vue';
	import { peristalticMotorApi } from '../api';
	import Card from 'primevue/card';
	import Stepper from 'primevue/stepper';
	import StepList from 'primevue/steplist';
	import Step from 'primevue/step';
	import StepPanel from 'primevue/steppanel';
	import StepPanels from 'primevue/steppanels';
	import Button from 'primevue/button';
	import Accordion from 'primevue/accordion';
	import AccordionPanel from 'primevue/accordionpanel';
	import AccordionHeader from 'primevue/accordionheader';
	import AccordionContent from 'primevue/accordioncontent';
	import FloatLabel from 'primevue/floatlabel';
	import InputNumber from 'primevue/inputnumber';
	import InputText from 'primevue/inputtext';
	import Select from 'primevue/select';
	import ProgressSpinner from 'primevue/progressspinner';
	import Toast from 'primevue/toast';
	import { useToast } from 'primevue/usetoast';
	const toast = useToast();
	import { useRouter } from 'vue-router';
	const router = useRouter();
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
	const peristalticMotorCalibration = ref({
		low_rpm: null,
		high_rpm: null,
		low_rpm_volume: null,
		high_rpm_volume: null,
		duration: null,
		name: null,
		direction: null,
		diameter: null,
	});

	const directionOptions = ref([
		{ label: 'Clockwise', value: 'cw' },
		{ label: 'Counterclockwise', value: 'ccw' },
	]);
	const durationOptions = ref([
		{ label: 'Seconds', value: 's' },
		{ label: 'Minutes', value: 'm' },
	]);
	const selectedTimeUnit = ref('s');
	const durationProgress = ref(0);
	let progressTimer: number | null = null;
	let startTime: number = 0;
	let totalDuration: number = 0;
	const slopeFromBackend = ref<number | null>(null)
	const computeSlope = async () => {
		try {
			const response = await peristalticMotorApi.computeSlope({duration: peristalticMotorCalibration.value.duration, low_rpm: peristalticMotorCalibration.value.low_rpm, high_rpm: peristalticMotorCalibration.value.high_rpm, low_rpm_volume: peristalticMotorCalibration.value.low_rpm_volume, high_rpm_volume: peristalticMotorCalibration.value.high_rpm_volume});
			slopeFromBackend.value = response.slope;
		} catch (error) {
			console.error('Error computing slope:', error);
		}
	}

	const setCalibrationDuration = () => {
		if (selectedTimeUnit.value === 'm') {
			peristalticMotorCalibration.value.duration = peristalticMotorCalibration.value.duration * 60;
		}
	};
	const startRPMCalibration = async (rpm: number, duration: number, direction: string) => {
		try {
			// Reset progress
			durationProgress.value = 0;

			// Store start time and total duration
			startTime = Date.now();
			totalDuration = duration * 1000; // Convert seconds to milliseconds
						// Start the progress timer
			startProgressTimer();
			// Start the API call
			await peristalticMotorApi.startRPMCalibration({duration, rpm, direction});


		} catch (error) {
			console.error('Error starting RPM calibration:', error);
			stopProgressTimer();
		}
	};

	const stopRPMCalibration = async () => {
		try {
			stopProgressTimer();
			durationProgress.value = 0;
			startTime = 0;
			totalDuration = 0;
			await peristalticMotorApi.stopRPMCalibration();
		} catch (error) {
			console.error('Error stopping RPM calibration:', error);
		}
	}

	const startProgressTimer = () => {
		// Clear any existing timer
		stopProgressTimer();

		// Update progress every 100ms for smooth animation
		progressTimer = window.setInterval(() => {
			const elapsed = Date.now() - startTime;
			const progress = Math.min((elapsed / totalDuration) * 100, 100);

			durationProgress.value = Math.round(progress);

			// Stop timer when progress reaches 100%
			if (progress >= 100) {
				stopProgressTimer();
				durationProgress.value = 100;
			}
		}, 20); // Update every 100ms
	};

	const stopProgressTimer = () => {
		if (progressTimer !== null) {
			clearInterval(progressTimer);
			progressTimer = null;
		}
	};

const chartOptions = computed(() => {
	const low = peristalticMotorCalibration.value.low_rpm;
	const high = peristalticMotorCalibration.value.high_rpm;

	// Calculate x-axis range (extend a bit beyond the points)
	//const minX = low ? Math.max(0, low - (high - low) * 0.2) : 0;
	const maxX = high ? high + (high - low) * 0.2 : 100;

	return {
  chart: {
    type: 'line',
    toolbar: {
      show: false
    }
  },
  xaxis: {
    type: 'numeric',
    title: {
      text: 'RPM'
    },
    min: 0,
    max: maxX
  },
  yaxis: {
    title: {
      text: 'Volume (ml)'
    },
    labels: {
      formatter: (val: number) => {
        if (val === undefined || val === null || isNaN(val)) {
          return '0';
        }
        return val.toFixed(0);
      },
    },
  },
  legend: {
    show: true,
    position: 'top'
  },
  markers: {
    size: [8, 4, 0] // Show markers for first two series (data points), not for line
  },
  stroke: {
    curve: 'smooth'
  }
};
});

const series = computed(() => {
	const low = peristalticMotorCalibration.value.low_rpm;
	const high = peristalticMotorCalibration.value.high_rpm;
	const lowVol = peristalticMotorCalibration.value.low_rpm_volume;
	const highVol = peristalticMotorCalibration.value.high_rpm_volume;
	const currentSlope = slopeFromBackend.value || 0;

	// Two calibration data points
	const dataPoints = [];
	dataPoints.push([0, 0]);
	if (low !== null && lowVol !== null) {
		dataPoints.push([low, lowVol]);
	}
	if (high !== null && highVol !== null) {
		dataPoints.push([high, highVol]);
	}

	// Linear function y = slope * x
	// Generate points for the line (from point 0, 0 to maxX, maxY)
	const linePoints = [];
	if (currentSlope !== 0 && (low !== null || high !== null)) {
		const minX = 0;
		const maxX = high !== null && low !== null ? high + (high - low) * 0.2 : 100;
		const maxY = currentSlope * maxX;

		// Generate 50 points for smooth line
		for (let x = minX; x <= maxX; x += (maxX - minX) / 50) {
			linePoints.push([x, Math.min(currentSlope * x, maxY)]);
		}
	}

	return [
		{
			name: 'Calibration Points',
			type: 'scatter',
			data: dataPoints
		},
		{
			name: `Slope y = ${currentSlope.toFixed(4)}x`,
			type: 'line',
			data: linePoints
		}
	];
});

	const downloadCalibrationFile = async () => {
		//download a json file with the peristalticmotorcalibration object (without the field name)
		try{
			const response = await peristalticMotorApi.savePeristalticCalibration({...peristalticMotorCalibration.value, name: peristalticMotorCalibration.value.name});
			const calibrationData = {
				low_rpm: peristalticMotorCalibration.value.low_rpm,
				high_rpm: peristalticMotorCalibration.value.high_rpm,
				low_rpm_volume: peristalticMotorCalibration.value.low_rpm_volume,
				high_rpm_volume: peristalticMotorCalibration.value.high_rpm_volume,
				duration: peristalticMotorCalibration.value.duration,
				diameter: peristalticMotorCalibration.value.diameter,
			};
			const calibrationJson = JSON.stringify(calibrationData);
			const calibrationBlob = new Blob([calibrationJson], { type: 'application/json' });
			const calibrationUrl = URL.createObjectURL(calibrationBlob);
			const calibrationLink = document.createElement('a');
			calibrationLink.href = calibrationUrl;
			calibrationLink.download = `${peristalticMotorCalibration.value.name}.json`;
			calibrationLink.click();
			URL.revokeObjectURL(calibrationUrl);

			showSuccess('Calibration file downloaded successfully');
			router.push('/peristaltic-motor');
		} catch (error) {
			console.error('Error downloading calibration file:', error);
			showError('Error downloading calibration file. Filename is required.');
		}
	}

	// Cleanup on component unmount
	onBeforeUnmount(() => {
		stopProgressTimer();
	});
	</script>
<style scoped>

</style>
