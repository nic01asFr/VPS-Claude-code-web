import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Terminal from '../views/Terminal.vue'
import Projects from '../views/Projects.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/terminal',
    name: 'Terminal',
    component: Terminal,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next({ name: 'Login' })
    } else {
      // Valider le token avec le serveur
      const isTokenValid = await store.dispatch('validateToken')
      if (isTokenValid) {
        next()
      } else {
        next({ name: 'Login' })
      }
    }
  } else {
    next()
  }
})

export default router 