<template>
  <div class="terminal-container">
    <div class="header">
      <h1>Claude Code Web</h1>
      <div class="status-indicator" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
        {{ isConnected ? 'Connecté' : 'Déconnecté' }}
      </div>
      <button @click="logout" class="logout-btn">Déconnexion</button>
    </div>
    
    <div class="terminal-window">
      <div class="terminal-output" ref="terminalOutput" v-html="formattedOutput"></div>
      
      <div class="input-container">
        <textarea 
          v-model="userInput" 
          @keydown.ctrl.enter="sendMessage"
          @keydown="handleKeyDown"
          placeholder="Entrez votre requête (Ctrl+Enter pour envoyer, ↑↓ pour naviguer dans les choix)"
          ref="inputArea"
          autofocus
        ></textarea>
        <button @click="sendMessage" :disabled="!isConnected">Envoyer</button>
      </div>
    </div>
  </div>
</template>

<script>
import { io } from 'socket.io-client'

export default {
  name: 'Terminal',
  data() {
    return {
      socket: null,
      userInput: '',
      terminalOutput: '',
      isConnected: false,
      reconnecting: false,
      reconnectAttempts: 0,
      maxReconnectAttempts: 5,
      choices: [],
      selectedChoiceIndex: -1,
      isChoiceMode: false
    }
  },
  computed: {
    formattedOutput() {
      // Amélioration du formatage pour une meilleure lisibilité
      return this.terminalOutput
        .replace(/\n/g, '<br>')
        .replace(/\s{2}/g, '&nbsp;&nbsp;')
        .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;');
    }
  },
  mounted() {
    console.log('Terminal component mounted');
    this.connectSocket();
    // Focus automatique sur le champ de saisie
    this.$nextTick(() => {
      if (this.$refs.inputArea) {
        this.$refs.inputArea.focus();
      }
    });
    
    // Vérifier périodiquement la connexion
    this.connectionChecker = setInterval(this.checkConnection, 10000);
    
    // Ajouter des gestionnaires d'événements pour la visibilité de la page
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect();
    }
    
    clearInterval(this.connectionChecker);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  },
  methods: {
    handleVisibilityChange() {
      if (document.visibilityState === 'visible') {
        // Si la page devient visible et que la connexion est perdue, tenter de reconnecter
        if (!this.isConnected && !this.reconnecting) {
          console.log('Page visible, tentative de reconnexion...');
          this.connectSocket();
        }
      }
    },
    checkConnection() {
      if (this.socket && !this.socket.connected && !this.reconnecting) {
        console.log('Détection de déconnexion via vérification périodique');
        this.connectSocket();
      }
    },
    connectSocket() {
      if (this.reconnecting) return;
      
      this.reconnecting = true;
      console.log("Tentative de connexion Socket.IO à l'API actuelle");
      
      if (this.socket) {
        this.socket.disconnect();
      }
      
      // Configuration Socket.IO compatible avec CORS et credentials
      this.socket = io(window.location.origin, {
        path: '/socket.io/',
        transports: ['polling', 'websocket'],
        reconnectionAttempts: 10,
        reconnectionDelay: 2000,
        timeout: 30000,
        withCredentials: true,
        forceNew: true,
        autoConnect: true
      });
      
      this.socket.on('connect', () => {
        console.log('Socket.IO connecté avec succès!');
        this.isConnected = true;
        this.reconnecting = false;
        this.reconnectAttempts = 0;
        const sessionId = this.$store.getters.getSessionId;
        const token = this.$store.getters.getToken;
        
        if (sessionId && token) {
          console.log(`Tentative de rejoindre la session ${sessionId}`);
          this.socket.emit('join', { session_id: sessionId, token });
          this.terminalOutput = 'Connexion au terminal en cours...';
        }
      });
      
      this.socket.on('connect_error', (error) => {
        console.error('Erreur de connexion Socket.IO:', error);
        this.isConnected = false;
        this.terminalOutput = `Erreur de connexion au serveur: ${error.message}\nTentative de reconnexion...`;
        this.scrollToBottom();
        
        // Tentative de reconnexion après un délai
        this.reconnectAttempts++;
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnecting = false;
            this.connectSocket();
          }, 3000);
        } else {
          this.reconnecting = false;
          this.terminalOutput += "\n\nImpossible de se connecter au serveur après plusieurs tentatives. Veuillez actualiser la page.";
        }
      });
      
      this.socket.on('joined', (data) => {
        console.log('Reçu événement joined avec données:', data);
        if (data.initial_output) {
          this.terminalOutput = data.initial_output;
        } else {
          this.terminalOutput = 'En attente de la sortie du terminal...';
        }
        this.scrollToBottom();
      });
      
      this.socket.on('tmux_output', (data) => {
        console.log('Reçu événement tmux_output avec données de longueur:', data.output ? data.output.length : 0);
        if (data.output && data.output.trim()) {
          this.terminalOutput = data.output;
          this.scrollToBottom();
        }
      });
      
      this.socket.on('error', (error) => {
        console.error('Erreur Socket.IO:', error);
        this.terminalOutput += '\n\nErreur de communication avec le serveur: ' + error.message;
        this.scrollToBottom();
      });
      
      this.socket.on('disconnect', () => {
        console.log('Déconnecté du serveur Socket.IO');
        this.isConnected = false;
        this.terminalOutput += '\n\nDéconnecté du serveur. Tentative de reconnexion...';
        this.scrollToBottom();
        
        // Tentative automatique de reconnexion après déconnexion
        setTimeout(() => {
          this.reconnecting = false;
          this.connectSocket();
        }, 2000);
      });
    },
    sendMessage() {
      if (!this.userInput.trim() || !this.isConnected) return;
      
      // Ajouter la commande à la sortie du terminal pour montrer ce que l'utilisateur a tapé
      this.terminalOutput += `\n\n> ${this.userInput}\n`;
      this.scrollToBottom();
      
      this.socket.emit('message', {
        session_id: this.$store.getters.getSessionId,
        message: this.userInput,
        token: this.$store.getters.getToken
      });
      
      this.userInput = '';
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.terminalOutput;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
    logout() {
      if (this.socket) {
        this.socket.disconnect();
      }
      this.$store.dispatch('logout');
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.terminal-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #2c3e50;
  color: white;
  z-index: 10;
}

.status-indicator {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.status-indicator.connected {
  background-color: #2ecc71;
  color: white;
}

.status-indicator.disconnected {
  background-color: #e74c3c;
  color: white;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.logout-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.terminal-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin: 0;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  height: calc(100% - 60px);
}

.terminal-output {
  flex: 1;
  background-color: #282c34;
  color: #abb2bf;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.4;
  overflow-y: auto;
  white-space: pre-wrap;
  min-height: 300px;
  height: calc(100% - 80px);
}

.input-container {
  display: flex;
  background-color: #21252b;
  padding: 10px;
  height: 80px;
}

textarea {
  flex: 1;
  height: 60px;
  background-color: #1e2127;
  color: #abb2bf;
  border: 1px solid #3e4451;
  padding: 10px;
  font-family: 'Courier New', monospace;
  resize: none;
  font-size: 14px;
}

button {
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0 15px;
  margin-left: 10px;
  cursor: pointer;
  font-weight: bold;
}

button:disabled {
  background-color: #6e9a84;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Styles pour mettre en évidence les commandes tapées */
.terminal-output >>> b {
  color: #61afef;
  font-weight: bold;
}

/* Animation pour indiquer que le terminal est actif */
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.terminal-output::after {
  content: "_";
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: #61afef;
}
</style> 