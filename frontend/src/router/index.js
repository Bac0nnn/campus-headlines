import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'portal-login',
    component: () => import('@/views/portal/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'portal-register',
    component: () => import('@/views/portal/Register.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/PortalLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/portal/Home.vue') },
      { path: 'article/:id', name: 'article', component: () => import('@/views/portal/ArticleDetail.vue') },
      { path: 'video', name: 'video', component: () => import('@/views/portal/Video.vue') },
      { path: 'discover', name: 'discover', component: () => import('@/views/portal/Discover.vue') },
      { path: 'profile', name: 'profile', component: () => import('@/views/portal/Profile.vue') }
    ]
  },
  {
    path: '/media/login',
    name: 'media-login',
    component: () => import('@/views/media/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/media',
    component: () => import('@/layouts/MediaLayout.vue'),
    children: [
      { path: '', redirect: '/media/publish' },
      { path: 'publish', name: 'media-publish', component: () => import('@/views/media/Publish.vue') },
      { path: 'content', name: 'media-content', component: () => import('@/views/media/ContentList.vue') },
      { path: 'material', name: 'media-material', component: () => import('@/views/media/Material.vue') },
      { path: 'audit', name: 'media-audit', component: () => import('@/views/media/Audit.vue') },
      { path: 'profile', name: 'media-profile', component: () => import('@/views/media/MediaProfile.vue') }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  if (to.path.startsWith('/media') && to.path !== '/media/login') {
    if (!localStorage.getItem('campus_media_token')) {
      return { path: '/media/login', query: { redirect: to.fullPath } }
    }
    try {
      const profile = JSON.parse(localStorage.getItem('campus_media_profile') || 'null')
      if (to.path === '/media/audit' && (!profile || profile.accountRole !== 1)) {
        return '/media/publish'
      }
      const reviewerPages = ['/media/audit', '/media/profile']
      if (profile && profile.accountRole === 1 && !reviewerPages.includes(to.path)) {
        return '/media/audit'
      }
    } catch (e) {
      return '/media/login'
    }
  }
  return true
})

export default router
