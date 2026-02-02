<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useLayout } from '@/layout/composables/layout';
import { authApi, generalApi } from '@/api';
import Menu from 'primevue/menu';
import ProgressBar from 'primevue/progressbar';
import Tag from 'primevue/tag';

const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();
const router = useRouter();
const menu = ref();
const generalStatus = ref(null);

setInterval(async () => {
    generalStatus.value = await generalApi.getGeneralStatus();
}, 1000);

const toggle = (event) => {
    menu.value.toggle(event);
};

const items = ref([
    {
        label: 'Logout',
        icon: 'pi pi-sign-out',
        command: () => {
            authApi.logout();
            router.push({ name: 'Login' });
        }
    }
]);
</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
            <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
                <i class="pi pi-bars"></i>
            </button>
            <router-link to="/" class="layout-topbar-logo">
                <!-- ... existing logo SVG ... -->
                <svg viewBox="0 0 54 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- ... existing SVG paths ... -->
                </svg>
                <span class="text-primary-color font-bold text-2xl">New Harvest</span>
            </router-link>
        </div>
        <div class="justify-end flex flex-row gap-2 w-full">
            <!-- Put the progress bar and the text in a flex row -->
                <!-- progress and span side by side. also take up 100% of the width -->
                 <div class="flex flex-row gap-2 w-2">
                    <div class="w-full flex flex-row gap-2" v-if="generalStatus?.tilt?.is_moving">
                    <ProgressBar mode="indeterminate" style="margin-top: 8px; width: 30%; height: 8px" />
                    <Tag rounded value="Tilt Motor is moving" />
                    </div>
                    <div class="w-full flex flex-row gap-2" v-if="generalStatus?.rotary?.is_moving">
                    <ProgressBar mode="indeterminate" style="margin-top: 8px; width: 30%; height: 8px" />
                    <Tag rounded value="Rotary Motor is moving" />
                    </div>
                    <div class="w-full flex flex-row gap-2" v-if="generalStatus?.peristaltic?.is_moving">
                    <ProgressBar mode="indeterminate" style="margin-top: 8px; width: 30%; height: 8px" />
                    <Tag rounded value="Peristaltic Motor is moving" />
                    </div>
                    <div style="margin-left: 34%;" class=" w-full flex flex-row gap-2" v-if="!generalStatus?.tilt?.is_moving && !generalStatus?.rotary?.is_moving && !generalStatus?.peristaltic?.is_moving">
                    <Tag rounded severity="info" value="All motors are idle" />
                    </div>
                </div>
        </div>
        <div class="layout-topbar-actions">
            <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content">
                    <button
                        type="button"
                        class="layout-topbar-action"
                        @click="toggle"
                        aria-haspopup="true"
                        aria-controls="overlay_menu"
                    >
                        <i class="pi pi-user"></i>
                        <span>Profile</span>
                    </button>
                    <Menu
                        ref="menu"
                        id="overlay_menu"
                        :model="items"
                        popup
                    />
                </div>
            </div>
        </div>
    </div>
</template>
