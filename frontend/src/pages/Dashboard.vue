<template>
  <div class="dashboard flex flex-col h-full ">
    <div class="page-header">
      <h1 class="page-title"><span class="text-muted-color">Modules Information</span></h1>
    </div>

    <div class="grid h-full flex-grow align-items-stretch">
      <div class="h-full col-4">
        <Card class="flex flex-col w-full h-full">
          <template #title>Tilt Motor</template>
          <template #content>
            <div class="flex flex-col gap-3 text-sm">
              <p class="text-color-secondary mt-0 mb-0">
                The Tilt Motor module provides precise control over a platform capable of tilting within a configurable range of -20° to +20°. Users can define a wide variety of motion parameters to suit specific applications.
              </p>

              <div class="font-semibold text-sm">Parameters</div>
              <ul class="list-none p-0 m-0 text-color-secondary space-y-1">
                <li><span class="font-semibold text-color">Tilt range:</span> Set minimum and maximum tilt angles.</li>
                <li><span class="font-semibold text-color">Movement duration:</span> Time for a single tilt movement.</li>
                <li><span class="font-semibold text-color">Repetition timing:</span> How long the motion sequence repeats (seconds).</li>
                <li><span class="font-semibold text-color">Standstill durations:</span> Pause at left, horizontal, and right.</li>
                <li><span class="font-semibold text-color">End position:</span> Final position after the sequence (left, horizontal, or right).</li>
                <li><span class="font-semibold text-color">Microstepping:</span> 1/4 to 1/256 step for motor precision.</li>
                <li><span class="font-semibold text-color">Homing:</span> Reset platform to reference 0°.</li>
              </ul>

              <p class="text-color-secondary mt-0 mb-0">
                Movements are shown in real time in the chart; scenarios can be saved in the database or exported/imported as JSON. CSV export is available for analysis.
              </p>

              <div class="font-semibold text-sm">Import/Export JSON format</div>
              <pre class="app-code mt-0 mb-0 overflow-x-auto" style="max-height: 12rem;"><code>{
            "name": "desired_name",
            "min_tilt": -20,
            "max_tilt": 20,
            "repetitions": 10,
            "move_duration": 2,
            "standstill_duration_left": 1,
            "standstill_duration_horizontal": 0.5,
            "standstill_duration_right": 1,
            "end_position": 1, // 0: right, 1: horizontal, 2: left
            "microstepping": 2 // 1/2² = 1 / 4 step
          }</code></pre>
          <div class="flex flex-col items-center">
            <img src="@/assets/images/tilt-motor.gif" alt="Tilt Motor" style="width:40%; height:auto; object-fit:contain;"/>
            <p class="text-color-secondary text-xs mb-0">Tilt motion cycle illustration</p>
          </div>
            </div>
</template>
        </Card>
      </div>
      <div class="h-full col-4">
        <Card class="flex flex-col w-full h-full">
          <template #title>Rotary Motor</template>
          <template #content>
  <div class="flex flex-col gap-3 text-sm">
    <p class="text-color-secondary mt-0 mb-0">
      The Rotary Motor module controls continuous or timed rotation at a set speed (RPM). Scenarios are built from one or more movement groups, each with its own speed, duration, and direction, for flexible rotation profiles.
    </p>

    <div class="font-semibold text-sm">Parameters</div>
    <ul class="list-none p-0 m-0 text-color-secondary space-y-1">
      <li><span class="font-semibold text-color">Scenario name:</span> Name used when saving the scenario.</li>
      <li><span class="font-semibold text-color">Speed (RPM):</span> Rotations per minute for the movement.</li>
      <li><span class="font-semibold text-color">Duration (s):</span> Length of the movement in seconds (0 = no limit).</li>
      <li><span class="font-semibold text-color">Direction:</span> Clockwise (cw) or counter-clockwise (ccw).</li>
      <li><span class="font-semibold text-color">Movement groups:</span> Add or remove segments to chain multiple speed/duration/direction steps.</li>
    </ul>

    <p class="text-color-secondary mt-0 mb-0">
      Real-time RPM is shown in the chart; scenarios can be saved in the database or exported/imported as JSON. CSV export is available for analysis.
    </p>
    <div style="margin-top: 17px;" class="font-semibold text-sm">Import/Export JSON format</div>
    <pre class="app-code mt-0 mb-0 overflow-x-auto" style="max-height: 12rem;"><code>{
  "name": "Rotary format",
  "movements": [
    {
      "duration": 15,
      "direction": "cw",
      "rpm": 5
    },
    {
      "duration": 10,
      "direction": "ccw",
      "rpm": 5
    },
    {
      "duration": 3,
      "direction": "cw", // cw: clockwise, ccw: counter-clockwise
      "rpm": 1
    }
  ]
}</code></pre>
<div class="flex flex-col items-center">
  <img src="@/assets/images/rotary-motor.gif" alt="Rotary Motor" style="width:40%; height:auto; object-fit:contain;"/>
  <p class="text-color-secondary text-xs mb-0">Rotary motion cycle illustration</p>
</div>
  </div>
</template>
        </Card>
      </div>
      <div class="h-full col-4">
        <Card class="flex flex-col w-full h-full">
          <template #title>Peristaltic Motor</template>
          <template #content>
  <div class="flex flex-col gap-3 text-sm">
    <p class="text-color-secondary mt-0 mb-0">
      The Peristaltic Motor module controls fluid flow via pump rotation. Speed is set in flow (mL/min) using a calibration that maps RPM to flow rate. Scenarios are built from movement groups with flow, duration, and direction.
    </p>

    <div class="font-semibold text-sm">Parameters</div>
    <ul class="list-none p-0 m-0 text-color-secondary space-y-1">
      <li><span class="font-semibold text-color">Scenario name:</span> Name used when saving the scenario.</li>
      <li><span class="font-semibold text-color">Calibration:</span> Tube Configurations or Peristaltic Calibration for RPM–flow mapping.</li>
      <li><span class="font-semibold text-color">Flow (mL/min):</span> Target flow rate for the movement.</li>
      <li><span class="font-semibold text-color">Duration (s):</span> Length of the movement in seconds (0 = no limit).</li>
      <li><span class="font-semibold text-color">Direction:</span> Clockwise (cw) or counter-clockwise (ccw).</li>
      <li><span class="font-semibold text-color">Movement groups:</span> Add or remove segments to chain multiple flow/duration/direction steps.</li>
    </ul>

    <p class="text-color-secondary mt-0 mb-0">
      Real-time movement is shown in the chart;
       scenarios can be saved in the database or exported/imported as JSON.
        CSV export is available.
    </p>

    <div class="font-semibold text-sm">Import/Export JSON format</div>
    <pre class="app-code mt-0 mb-0 overflow-x-auto" style="max-height: 12rem;"><code>{
  "name": "Peristaltic format",
  "movements": [
    {
      "duration": 15,
      "direction": "cw",
      "rpm": 5
    },
    {
      "duration": 10,
      "direction": "ccw",
      "rpm": 5
    }
  ],
  "calibration": {
    "id": 1,
    "name": "calibration",
    "diameter": 1.42,
    "flow_rate": 0.25,
    "preset": true
  }
}</code></pre>
<div class="flex flex-col items-center">
    <img src="@/assets/images/peristaltic-motor.gif" alt="Peristaltic Motor" style="width:40%; height:auto; object-fit:contain;"/>
    <p class="text-color-secondary text-xs mb-0">Peristaltic motion cycle illustration</p>
  </div>
  </div>
</template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
</script>

<style scoped>
</style>
