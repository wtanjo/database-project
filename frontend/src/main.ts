import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "./style.css";
import App from "./App.vue";
import AppLayout from "./components/AppLayout.vue";
import DashboardView from "./views/DashboardView.vue";
import TasksView from "./views/TasksView.vue";
import ContentsView from "./views/ContentsView.vue";
import ImagesView from "./views/ImagesView.vue";
import WebsitesView from "./views/WebsitesView.vue";
import WebpagesView from "./views/WebpagesView.vue";
import SettingsView from "./views/SettingsView.vue";

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{
			path: "/",
			component: AppLayout,
			children: [
				{ path: "", component: DashboardView },
				{ path: "tasks", component: TasksView },
				{ path: "contents", component: ContentsView },
				{ path: "images", component: ImagesView },
				{ path: "websites", component: WebsitesView },
				{ path: "webpages", component: WebpagesView },
				{ path: "settings", component: SettingsView },
			],
		},
	],
});

const app = createApp(App);

app.use(ElementPlus).use(router).mount("#app");
