<script setup>
import { ref } from "vue";

import AppMenuItem from "./AppMenuItem.vue";

const model = ref([
  {
    label: "Home",
    items: [{ label: "Dashboard", icon: "pi pi-fw pi-home", to: "/" }],
  },
  {
    label: "Tilt Motor",
    items: [
      { label: "Control", icon: "pi pi-fw pi-play-circle", to: "/tilt-motor" },
    ],
  },
  {
    label: "Rotary Motor",
    items: [
      {
        label: "Control",
        icon: "pi pi-fw pi-play-circle",
        to: "/rotary-motor",
      },
    ],
  },
  {
    label: "Peristaltic Motor",
    items: [
      {
        label: "Calibration",
        icon: "pi pi-fw pi-cog",
        to: "/peristaltic-motor-calibration",
      },
      {
        label: "Tube Configurations",
        icon: "pi pi-fw pi-wrench",
        to: "/peristaltic-motor-tube-configurations",
      },
      {
        label: "Control",
        icon: "pi pi-fw pi-play-circle",
        to: "/peristaltic-motor",
      },
    ],
  },
  {
    label: "History",
    items: [
      {
        label: "Measurements History",
        icon: "pi pi-fw pi-history",
        to: "/measurements-history",
      },
    ],
  },
  {
    label: "Documentation",
    items: [
      {
        label: "Assembly",
        icon: "pi pi-fw pi-book",
        url: "https://github.com/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/blob/main/docs/assembly/README.md",
        target: "_blank",
      },
      {
        label: "Setup",
        icon: "pi pi-fw pi-book",
        url: "https://github.com/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/blob/main/docs/setup/README.md",
        target: "_blank",
      },
      {
        label: "Installation",
        icon: "pi pi-fw pi-book",
        url: "https://github.com/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/blob/main/docs/INSTALLATION.md",
        target: "_blank",
      },
      {
        label: "User Guide",
        icon: "pi pi-fw pi-book",
        url: "https://github.com/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/blob/main/docs/user_guide/README.md",
        target: "_blank",
      },
    ],
  },
]);
</script>

<template>
  <ul class="layout-menu">
    <template v-for="(item, i) in model" :key="item">
      <app-menu-item
        v-if="!item.separator"
        :item="item"
        :index="i"
      ></app-menu-item>
      <li v-if="item.separator" class="menu-separator"></li>
    </template>
  </ul>
</template>

<style lang="scss" scoped></style>
