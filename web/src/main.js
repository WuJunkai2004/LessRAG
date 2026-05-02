import { createApp } from "vue";
import App from "./App.vue";

import router from "./router";

import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";
import "./assets/main.css";
import "primeflex/primeflex.css";
import "primeicons/primeicons.css";

import ConfirmationService from "primevue/confirmationservice";
import ToastService from "primevue/toastservice";

import { definePreset } from "@primeuix/themes";
const Fuchsia = definePreset(Aura, {
  semantic: {
    primary: {
      50: "{fuchsia.50}",
      100: "{fuchsia.100}",
      200: "{fuchsia.200}",
      300: "{fuchsia.300}",
      400: "{fuchsia.400}",
      500: "{fuchsia.500}",
      600: "{fuchsia.600}",
      700: "{fuchsia.700}",
      800: "{fuchsia.800}",
      900: "{fuchsia.900}",
      950: "{fuchsia.950}",
    },
  },
});

const app = createApp(App);

app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Fuchsia,
  },
});
app.use(ConfirmationService);
app.use(ToastService);

app.mount("#app");
