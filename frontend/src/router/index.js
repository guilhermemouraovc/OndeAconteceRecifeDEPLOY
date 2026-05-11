import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/cadastro',
      name: 'cadastro',
      component: () => import('@/views/CadastroProdutorView.vue'),
    },
  ],
})

export default router
