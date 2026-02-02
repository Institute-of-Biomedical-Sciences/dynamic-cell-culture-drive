<template>
	<Dialog
	  v-model:visible="visibleProxy"
	  modal
	  header="Set Filename"
	  :style="{ width: '27rem' }"
	>
	  <div class="flex flex-column gap-3">
		<div>
		  <label for="prefix" class="block text-sm font-medium mb-2">Filename Prefix</label>
		  <InputText
			id="prefix"
			v-model="localPrefix"
			placeholder="Enter prefix"
			class="w-full"
		  />
		</div>
		<div>
		  <label class="block text-sm font-medium mb-2">Generated Filename</label>
		  <div class="p-2 border-round bg-surface-100 text-sm">
			{{ generatedFilename }}
		  </div>
		</div>
	  </div>

	  <template #footer>
		<Button
		  label="Cancel"
		  severity="secondary"
		  outlined
		  @click="visibleProxy = false"
		/>
		<Button
		  label="Download"
		  @click="onConfirm"
		/>
	  </template>
	</Dialog>
  </template>

  <script setup lang="ts">
  import { computed, ref, watch } from 'vue'
  import Dialog from 'primevue/dialog'
  import InputText from 'primevue/inputtext'
  import Button from 'primevue/button'

  const props = defineProps<{
	visible: boolean
	scenarioName?: string
	type: number
	endTimestamp?: string
  }>()

  const emit = defineEmits<{
	(e: 'update:visible', value: boolean): void
	(e: 'confirm', payload: { prefix: string; filename: string }): void
  }>()

  // v-model:visible bridge
  const visibleProxy = computed({
	get: () => props.visible,
	set: (val: boolean) => emit('update:visible', val),
  })

  const localPrefix = ref('')

  // Generate filename: prefix_scenarioName_endTimestamp.csv
  const generatedFilename = computed(() => {
	const prefix = localPrefix.value || `${props.type === 0 ? 'tilt' : props.type === 1 ? 'rotate' : props.type === 2 ? 'peristaltic' : 'movements'}`
	return `${prefix}_${props.scenarioName}_${props.endTimestamp}.csv`
  })

  const onConfirm = () => {
	emit('confirm', {
	  prefix: localPrefix.value,
	  filename: generatedFilename.value,
	})
	visibleProxy.value = false
  }
  </script>
