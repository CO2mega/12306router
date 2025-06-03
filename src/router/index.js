import { createRouter, createWebHistory } from "vue-router";
import HomepageView from "../views/homepageView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "layout",
      component: () => import("../layouts/MainLayout.vue"),
      children: [
        {
          path: "",
          name: "homepage",
          component: HomepageView,
        },
        {
          path: "login", 
          name: "login",
          component: () => import("../views/login.vue"),
        },
        {
          path: "register",
          name: "register",
          component: () => import("../views/signup.vue"),
        },
        {
          path: "ticket",
          name: "ticket",
          component: () => import("../views/ticketView.vue")
        },
        {
          path: "user-profile",
          name: "userProfile",
          component: () => import("../views/user-profile.vue")
        },
        {
          path: "query",
          name: "query",
          component: () => import("../views/queryView.vue")
        },
        {
          path:"change-ticket",
          name: "changeTicket", 
          component: () => import("../views/changeTicketView.vue")
        }
      ]
    }
  ],
});

export default router;
