const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('pages/IndexPage.vue') },
      {
        path: 'programacao',
        name: 'programacao',
        component: () => import('pages/ProgramacaoPage.vue'),
      },
      { path: 'mapa', name: 'mapa', component: () => import('pages/MapaPage.vue') },
      {
        path: 'favoritos',
        name: 'favoritos',
        component: () => import('pages/FavoritosPage.vue'),
      },
      {
        path: 'cadastro',
        name: 'cadastro',
        component: () => import('pages/CadastroProdutorPage.vue'),
      },
      {
        path: 'moderacao',
        name: 'moderacao',
        component: () => import('pages/ModeracaoPage.vue'),
      },
      { path: 'scraper', name: 'scraper', component: () => import('pages/ScraperPage.vue') },
      {
        path: 'evento/:slug',
        name: 'event-detail',
        component: () => import('pages/EventDetailPage.vue'),
      },
    ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
