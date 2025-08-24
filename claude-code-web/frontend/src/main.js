import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)

// Initialiser l'application
app.use(store).use(router)

// Valider le token au démarrage si l'utilisateur semble être connecté
if (store.getters.isAuthenticated) {
  store.dispatch('validateToken').then(isValid => {
    if (!isValid) {
      // Rediriger vers la page de connexion si le token n'est pas valide
      router.push('/')
    }
  })
}

app.mount('#app') 