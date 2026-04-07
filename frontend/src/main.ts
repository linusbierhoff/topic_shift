import { createApp } from "vue";
import "./style.css";
/* import the core styles */
import "@vue-flow/core/dist/style.css";

/* import the default theme, this is optional but generally recommended */
import "@vue-flow/core/dist/theme-default.css";

import "@vue-flow/controls/dist/style.css";

import App from "./App.vue";
import router from "./router";

createApp(App).use(router).mount("#app");
