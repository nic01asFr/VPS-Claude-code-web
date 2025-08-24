import { createStore } from 'vuex'

export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    userId: localStorage.getItem('userId') || '',
    username: localStorage.getItem('username') || '',
    sessionId: localStorage.getItem('sessionId') || '',
  },
  getters: {
    isAuthenticated: state => !!state.token,
    getToken: state => state.token,
    getUserId: state => state.userId,
    getUsername: state => state.username,
    getSessionId: state => state.sessionId
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    setUserId(state, userId) {
      state.userId = userId
      localStorage.setItem('userId', userId)
    },
    setUsername(state, username) {
      state.username = username
      localStorage.setItem('username', username)
    },
    setSessionId(state, sessionId) {
      state.sessionId = sessionId
      localStorage.setItem('sessionId', sessionId)
    },
    logout(state) {
      state.token = ''
      state.userId = ''
      state.username = ''
      state.sessionId = ''
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('username')
      localStorage.removeItem('sessionId')
    }
  },
  actions: {
    login({ commit }, { token, userId, username }) {
      commit('setToken', token)
      commit('setUserId', userId)
      commit('setUsername', username)
    },
    setSession({ commit }, sessionId) {
      commit('setSessionId', sessionId)
    },
    logout({ commit }) {
      commit('logout')
    },
    async validateToken({ commit, state }) {
      if (!state.token) {
        return false
      }
      
      try {
        const response = await fetch('/api/projects', {
          headers: {
            'Authorization': `Bearer ${state.token}`
          }
        })
        
        if (response.ok) {
          return true
        } else {
          // Token invalide, déconnecter l'utilisateur
          commit('logout')
          return false
        }
      } catch (error) {
        console.error('Erreur lors de la validation du token:', error)
        commit('logout')
        return false
      }
    }
  }
}) 