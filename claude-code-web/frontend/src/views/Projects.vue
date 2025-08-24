<template>
  <div class="projects-container">
    <div class="header">
      <h1>Claude Code Web - Gestion des Projets</h1>
      <div class="user-info">
        <span>{{ username }}</span>
        <button @click="logout" class="logout-btn">Déconnexion</button>
      </div>
    </div>

    <div class="main-content">
      <!-- Section Nouveau Projet -->
      <div class="new-project-section">
        <h2>🆕 Nouveau Projet</h2>
        <p class="section-description">Créez un nouveau projet avec un template optimisé et une structure Docker/Traefik complète.</p>
        <div class="project-form">
          <input 
            v-model="newProject.name" 
            placeholder="Nom du projet" 
            class="project-input"
          />
          <select v-model="newProject.template" class="template-select">
            <option value="">Sélectionner un template</option>
            <option value="react-node-postgres">🚀 React + Node.js + PostgreSQL - Applications web complexes</option>
            <option value="vue-flask-postgres">⚡ Vue.js + Flask + PostgreSQL - Développement Python rapide</option>
            <option value="static-site">📄 Site Statique - Sites de contenu avec Nginx</option>
            <option value="api-backend">🔌 API Backend - Services backend Node.js/Express</option>
          </select>
          <textarea 
            v-model="newProject.description" 
            placeholder="Décrivez votre projet (objectifs, fonctionnalités principales, public cible...)"
            class="project-description"
          ></textarea>
          <button @click="createProject" :disabled="!canCreateProject" class="create-btn">
            Créer le Projet
          </button>
        </div>
      </div>

      <!-- Liste des Projets Existants -->
      <div class="projects-section">
        <h2>📁 Projets Existants</h2>
        <p class="section-description">Gérez vos projets existants avec des terminaux Claude Code dédiés et des URLs de production.</p>
        <div class="projects-grid">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="project-card"
            @click="selectProject(project)"
          >
            <div class="project-header">
              <h3>{{ project.name }}</h3>
              <div class="project-status" :class="project.status">
                {{ project.status }}
              </div>
            </div>
            <p class="project-description">{{ project.description }}</p>
            <div class="project-meta">
              <span class="template">{{ project.template }}</span>
              <span class="created">{{ formatDate(project.created_at) }}</span>
            </div>
            <div class="project-actions">
              <button @click.stop="openTerminal(project)" class="terminal-btn">
                Terminal
              </button>
              <button @click.stop="viewProject(project)" class="view-btn">
                Voir
              </button>
              <button @click.stop="deleteProject(project)" class="delete-btn">
                Supprimer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Terminal pour Projet Spécifique -->
    <div v-if="selectedProject" class="terminal-modal" @click="closeTerminal">
      <div class="terminal-content" @click.stop>
        <div class="terminal-header">
          <h3>{{ selectedProject.name }} - Terminal</h3>
          <button @click="closeTerminal" class="close-btn">×</button>
        </div>
        <ProjectTerminal 
          :project="selectedProject" 
          :token="token"
          @close="closeTerminal"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ProjectTerminal from '../components/ProjectTerminal.vue'
import apiClient from '../plugins/axios.js'
import { useStore } from 'vuex'
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Projects',
  components: {
    ProjectTerminal
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const projects = ref([])
    const selectedProject = ref(null)
    const newProject = ref({
      name: '',
      template: '',
      description: ''
    })

    const username = computed(() => store.state.user && store.state.user.username ? store.state.user.username : 'Utilisateur')
    const token = computed(() => store.state.token)

    const canCreateProject = computed(() => {
      return newProject.value.name && 
             newProject.value.template && 
             newProject.value.description
    })

    const logout = () => {
      store.dispatch('logout')
      router.push('/')
    }

    const loadProjects = async () => {
      try {
        const response = await apiClient.get('/api/projects')
        projects.value = response.data
      } catch (error) {
        console.error('Erreur lors du chargement des projets:', error)
      }
    }

    const createProject = async () => {
      try {
        const response = await apiClient.post('/api/projects', newProject.value)
        const project = response.data
        projects.value.push(project)
        
        // Reset form
        newProject.value = {
          name: '',
          template: '',
          description: ''
        }
      } catch (error) {
        console.error('Erreur lors de la création du projet:', error)
      }
    }

    const selectProject = (project) => {
      selectedProject.value = project
    }

    const openTerminal = (project) => {
      selectedProject.value = project
    }

    const closeTerminal = () => {
      selectedProject.value = null
    }

    const viewProject = (project) => {
      // Ouvrir la page du projet dans un nouvel onglet
      let url = null
      if (project.urls && project.urls.production) {
        url = project.urls.production
      } else if (project.urls && project.urls.staging) {
        url = project.urls.staging
      }
      if (url) {
        window.open(url, '_blank')
      }
    }

    const deleteProject = async (project) => {
      if (!confirm(`Êtes-vous sûr de vouloir supprimer le projet "${project.name}" ?`)) {
        return
      }

      try {
        await apiClient.delete(`/api/projects/${project.id}`)
        projects.value = projects.value.filter(p => p.id !== project.id)
      } catch (error) {
        console.error('Erreur lors de la suppression du projet:', error)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('fr-FR')
    }

    onMounted(() => {
      loadProjects()
    })

    return {
      projects,
      selectedProject,
      newProject,
      username,
      token,
      canCreateProject,
      logout,
      createProject,
      selectProject,
      openTerminal,
      closeTerminal,
      viewProject,
      deleteProject,
      formatDate
    }
  }
}
</script>

<style scoped>
.projects-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-family: 'Monaco', 'Consolas', monospace;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  background: #ff6b6b;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.new-project-section {
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.section-description {
  opacity: 0.8;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.project-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 500px;
}

.project-input, .template-select, .project-description {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.project-input::placeholder, .project-description::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.template-select option {
  background: #333;
  color: white;
}

.project-description {
  min-height: 80px;
  resize: vertical;
}

.create-btn {
  background: #4ecdc4;
  border: none;
  padding: 0.75rem;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-weight: bold;
}

.create-btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.projects-section h2 {
  margin-bottom: 1rem;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.project-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.project-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.project-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.project-status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.project-status.active {
  background: #4ecdc4;
}

.project-status.developing {
  background: #ffa726;
}

.project-status.inactive {
  background: #666;
}

.project-description {
  margin-bottom: 1rem;
  opacity: 0.8;
  line-height: 1.4;
}

.project-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  opacity: 0.7;
}

.project-actions {
  display: flex;
  gap: 0.5rem;
}

.terminal-btn {
  background: #4ecdc4;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.view-btn {
  background: #667eea;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.delete-btn {
  background: #ff6b6b;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.terminal-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.terminal-content {
  background: #1a1a1a;
  border-radius: 8px;
  width: 90%;
  height: 80%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #333;
}

.terminal-header h3 {
  margin: 0;
  color: white;
}

.close-btn {
  background: #ff6b6b;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
}
</style>