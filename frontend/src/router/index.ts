import { createRouter, createWebHistory } from 'vue-router'
import { useSetupStore } from '@/stores/setup'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/setup',
      name: 'setup',
      component: () => import('@/views/SetupView.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresSetup: true },
    },
    {
      path: '/agent/:id',
      name: 'agent',
      component: () => import('@/views/AgentView.vue'),
      meta: { requiresSetup: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const setupStore = useSetupStore()

  if (!setupStore.loaded) {
    await setupStore.load()
  }

  if (to.meta.requiresSetup && !setupStore.isSetup) {
    return { name: 'setup' }
  }

  if (to.name === 'setup' && setupStore.isSetup) {
    return { name: 'home' }
  }
})

export default router
