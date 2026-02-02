<script setup>
import AppMenu from './AppMenu.vue';
import { Card } from 'primevue';
</script>

<template>
    <Card class="layout-sidebar">
        <template #content>
            <app-menu></app-menu>
        </template>
    </Card>
</template>

<style lang="scss" scoped></style>
