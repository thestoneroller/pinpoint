import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const Search = () => import('../views/Search.vue')
const NotFound = () => import('../views/NotFound.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home },
    {
      path: '/search/:endpoint',
      name: 'search',
      component: Search,
      props: true,
    },
    { path: '/:pathMatch(.*)*', component: NotFound },
  ],
})

export default router
