import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/homeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
      children: [
        {
          path: "",
          name: "homepage",
          component: () => import("../views/homepageView.vue"),
        },
        {
          path: "ticket",
          name: "ticket",
          component: () => import("../views/ticketView.vue"),
        },
      ],
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/login.vue"),
    },
  ],
});

export default router;
