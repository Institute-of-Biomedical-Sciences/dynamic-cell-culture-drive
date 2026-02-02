import "./styles/main.css";
import "./index.css";
// PrimeVue CSS must be imported before app creation
import "primeicons/primeicons.css"; //icons
import "primeflex/primeflex.css";
import "@/assets/tailwind.css";
import "@/assets/styles.scss";

import Aura from "@primeuix/themes/aura";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import {createApp} from "vue";
import VueApexCharts from "vue3-apexcharts";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(router);
app.use(VueApexCharts);
app.use(ToastService);
app.use(PrimeVue, {
  theme : {
    preset : Aura,
    options : {
      darkModeSelector : ".app-dark",
    },
  },
});
app.mount("#app");
