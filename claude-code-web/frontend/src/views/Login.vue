<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Claude Code Web</h1>
      <div class="form-group">
        <label for="username">Nom d'utilisateur</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          placeholder="Nom d'utilisateur"
          @keyup.enter="login"
        >
      </div>
      <div class="form-group">
        <label for="password">Mot de passe</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="Mot de passe"
          @keyup.enter="login"
        >
      </div>
      <button @click="login" :disabled="isLoading">
        {{ isLoading ? 'Connexion...' : 'Se connecter' }}
      </button>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import apiClient from '../plugins/axios.js'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      isLoading: false
    }
  },
  methods: {
    async login() {
      if (!this.username || !this.password) {
        this.error = 'Veuillez remplir tous les champs'
        return
      }
      
      this.isLoading = true
      this.error = ''
      
      try {
        const response = await apiClient.post('/api/auth', {
          username: this.username,
          password: this.password
        })
        
        const { token, user_id, username } = response.data
        this.$store.dispatch('login', { token, userId: user_id, username })
        
        // Créer une nouvelle session
        await this.createSession()
        
        console.log("Redirection vers /projects");
        
        // Rediriger vers la page des projets
        this.$router.push('/projects')
        
        // Forcer la navigation si la redirection ne fonctionne pas
        setTimeout(() => {
          if (this.$router.currentRoute.value.path !== '/projects') {
            window.location.href = '/projects';
          }
        }, 1000);
      } catch (error) {
        console.error('Erreur de connexion:', error)
        this.error = 'Identifiants invalides'
      } finally {
        this.isLoading = false
      }
    },
    async createSession() {
      try {
        const response = await apiClient.post('/api/session/new')
        
        const { session_id } = response.data
        this.$store.dispatch('setSession', session_id)
      } catch (error) {
        console.error('Erreur lors de la création de la session:', error)
        throw error
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #3aa876;
}

button:disabled {
  background-color: #a8d5c3;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 15px;
  text-align: center;
}
</style> 