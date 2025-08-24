<template>
  <div class="project-terminal">
    <div class="terminal-info">
      <div class="project-info">
        <span class="project-name">{{ project.name }}</span>
        <span class="template-badge">{{ project.template }}</span>
      </div>
      <div class="connection-status" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
        {{ isConnected ? 'Connecté' : 'Déconnecté' }}
      </div>
    </div>
    
    <div class="terminal-output" ref="terminalOutput" v-html="formattedOutput"></div>
    
    <div class="input-container">
      <textarea 
        v-model="userInput" 
        @keydown.ctrl.enter="sendMessage"
        @keydown="handleKeyDown"
        placeholder="Entrez votre commande pour ce projet (Ctrl+Enter pour envoyer)"
        ref="inputArea"
        autofocus
      ></textarea>
      <button @click="sendMessage" :disabled="!isConnected && !(socket && socket.connected)">Envoyer</button>
    </div>
  </div>
</template>

<script>
import { io } from 'socket.io-client'

export default {
  name: 'ProjectTerminal',
  props: {
    project: {
      type: Object,
      required: true
    },
    token: {
      type: String,
      required: true
    }
  },
  emits: ['close'],
  data() {
    return {
      socket: null,
      userInput: '',
      terminalOutput: '',
      isConnected: false,
      reconnecting: false,
      sessionId: null
    }
  },
  computed: {
    formattedOutput() {
      return this.terminalOutput
        .replace(/\n/g, '<br>')
        .replace(/\s{2}/g, '&nbsp;&nbsp;')
        .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;');
    }
  },
  mounted() {
    this.connectToProject();
    this.$nextTick(() => {
      if (this.$refs.inputArea) {
        this.$refs.inputArea.focus();
      }
    });
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect();
    }
  },
  methods: {
    async connectToProject() {
      try {
        // Créer ou récupérer une session pour ce projet
        const response = await fetch(`/api/projects/${this.project.id}/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
          }
        });

        if (!response.ok) {
          throw new Error('Erreur lors de la création de la session projet');
        }

        const sessionData = await response.json();
        this.sessionId = sessionData.session_id;

        // Maintenant connecter le WebSocket
        this.connectSocket();
      } catch (error) {
        console.error('Erreur lors de la connexion au projet:', error);
        this.terminalOutput = `Erreur de connexion au projet ${this.project.name}: ${error.message}\n`;
      }
    },

    connectSocket() {
      if (this.socket) {
        this.socket.disconnect();
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}`;

      this.socket = io(wsUrl, {
        path: '/socket.io/',
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });

      this.socket.on('connect', () => {
        console.log('WebSocket connecté pour le projet:', this.project.name);
        this.isConnected = true;
        this.reconnecting = false;

        // Rejoindre la session du projet
        this.socket.emit('join_project', {
          session_id: this.sessionId,
          project_id: this.project.id,
          token: this.token
        });
      });

      this.socket.on('disconnect', () => {
        console.log('WebSocket déconnecté pour le projet:', this.project.name);
        this.isConnected = false;
      });

      this.socket.on('joined', (data) => {
        console.log('Rejoint la session du projet:', data);
        this.terminalOutput = data.initial_output || `Terminal du projet ${this.project.name}\n\nProjet: ${this.project.name}\nTemplate: ${this.project.template}\nRépertoire: /root/docker/apps/${this.project.name}/\n\nPrêt à recevoir vos commandes...\n`;
        this.scrollToBottom();
      });

      this.socket.on('output', (data) => {
        console.log('Nouvelle sortie reçue:', data);
        this.terminalOutput = data.output;
        this.scrollToBottom();
      });

      this.socket.on('error', (data) => {
        console.error('Erreur WebSocket:', data);
        this.terminalOutput += `\nErreur: ${data.message}\n`;
        this.scrollToBottom();
      });

      this.socket.on('connect_error', (error) => {
        console.error('Erreur de connexion WebSocket:', error);
        this.isConnected = false;
      });
    },

    sendMessage() {
      console.log('sendMessage appelé - userInput:', this.userInput.trim());
      console.log('sendMessage appelé - isConnected:', this.isConnected);
      console.log('sendMessage appelé - sessionId:', this.sessionId);
      
      if (!this.userInput.trim() || (!this.isConnected && !(this.socket && this.socket.connected)) || !this.sessionId) {
        console.log('Envoi bloqué par les conditions');
        return;
      }

      console.log('Envoi de message pour le projet:', this.project.name, this.userInput);
      console.log('Socket connecté ?', this.socket.connected);
      console.log('Session ID:', this.sessionId);
      console.log('Project ID:', this.project.id);

      this.socket.emit('project_message', {
        session_id: this.sessionId,
        project_id: this.project.id,
        message: this.userInput,
        token: this.token
      });
      
      console.log('Événement project_message émis');

      this.userInput = '';
    },

    handleKeyDown(event) {
      // Gérer Ctrl+Enter pour envoyer
      if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault();
        this.sendMessage();
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.terminalOutput) {
          this.$refs.terminalOutput.scrollTop = this.$refs.terminalOutput.scrollHeight;
        }
      });
    }
  }
}
</script>

<style scoped>
.project-terminal {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a1a;
  color: #00ff00;
  font-family: 'Monaco', 'Consolas', monospace;
}

.terminal-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid #333;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.project-name {
  font-weight: bold;
  color: #4ecdc4;
}

.template-badge {
  background: #667eea;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  color: white;
}

.connection-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.connection-status.connected {
  background: #4caf50;
  color: white;
}

.connection-status.disconnected {
  background: #f44336;
  color: white;
}

.terminal-output {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: #000;
  color: #00ff00;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.4;
}

.input-container {
  display: flex;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid #333;
}

.input-container textarea {
  flex: 1;
  background: #222;
  border: 1px solid #555;
  color: #00ff00;
  padding: 0.75rem;
  border-radius: 4px;
  resize: none;
  min-height: 60px;
  font-family: inherit;
}

.input-container textarea:focus {
  outline: none;
  border-color: #4ecdc4;
}

.input-container textarea::placeholder {
  color: #666;
}

.input-container button {
  margin-left: 1rem;
  background: #4ecdc4;
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.input-container button:hover {
  background: #45b7b8;
}

.input-container button:disabled {
  background: #666;
  cursor: not-allowed;
}

/* Scrollbar personnalisée */
.terminal-output::-webkit-scrollbar {
  width: 8px;
}

.terminal-output::-webkit-scrollbar-track {
  background: #333;
}

.terminal-output::-webkit-scrollbar-thumb {
  background: #666;
  border-radius: 4px;
}

.terminal-output::-webkit-scrollbar-thumb:hover {
  background: #888;
}
</style>