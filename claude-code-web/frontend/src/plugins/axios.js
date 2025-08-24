import axios from 'axios'
import store from '../store'
import router from '../router'

// Configuration de base
const apiClient = axios.create({
  baseURL: 'https://claude-api.colaig.fr',
  timeout: 10000,
})

// Intercepteur de requête pour ajouter automatiquement le token
apiClient.interceptors.request.use(
  (config) => {
    const token = store.getters.getToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur de réponse pour gérer les erreurs d'authentification
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token invalide ou expiré
      console.warn('Token invalide ou expiré, déconnexion automatique')
      store.dispatch('logout')
      router.push('/')
    }
    return Promise.reject(error)
  }
)

export default apiClient