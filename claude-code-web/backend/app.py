from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
import os
import subprocess
import time
import json
import jwt
import uuid
import docker
import requests
from datetime import datetime, timedelta
import threading
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/claude-web.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend/dist')
# Configuration CORS avec origines spécifiques (pas de wildcard)
allowed_origins = ['https://claude.colaig.fr', 'http://localhost:8080', 'http://localhost:5002']
CORS(app, 
     resources={r"/*": {"origins": allowed_origins}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Access-Control-Allow-Origin"],
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])

# Configuration de Socket.IO avec des origines spécifiques
socketio = SocketIO(
    app, 
    cors_allowed_origins=allowed_origins,
    async_mode='threading',
    path='/socket.io/',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    always_connect=True
)

# Configuration
SECRET_KEY = os.environ.get('AUTH_SECRET', 'claude-web-secret-key')
SESSIONS_DIR = '/root/docker/claude-code-web/tmux-sessions'
DOCKER_PATH = '/root/docker'
CLAUDE_CODE_PATH = '/root/docker/claude-code'
N8N_API_URL = os.environ.get('N8N_API_URL', 'https://n8n.colaig.fr')
N8N_API_KEY = os.environ.get('N8N_API_KEY', '')

# Client Docker
try:
    docker_client = docker.from_env()
    logger.info("Docker client initialisé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation du client Docker: {str(e)}")
    docker_client = None

# Stockage des sessions actives
active_sessions = {}
output_threads = {}

# Stockage des projets et sessions par projet
project_sessions = {}
project_data = {}

# Au démarrage, nettoyer toutes les anciennes sessions tmux
def cleanup_old_sessions():
    """Nettoie les anciennes sessions tmux au démarrage"""
    logger.info("Nettoyage des anciennes sessions tmux...")
    try:
        # Liste toutes les sessions tmux
        result = subprocess.run("tmux list-sessions -F '#{session_name}'", 
                              shell=True, capture_output=True, text=True)
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('claude_'):
                # Nettoyage des sessions utilisateur
                session_name = line.strip()
                logger.info(f"Nettoyage de l'ancienne session: {session_name}")
                subprocess.run(f"tmux kill-session -t {session_name}", shell=True)
        
        # Tuer aussi la session principale si elle existe
        subprocess.run("tmux kill-session -t claude-code-session 2>/dev/null || true", shell=True)
        logger.info("Nettoyage des sessions terminé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des anciennes sessions: {str(e)}")

# Exécuter le nettoyage au démarrage
cleanup_old_sessions()

def generate_token(user_id, username):
    """Génère un token JWT"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Vérifie un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except Exception as e:
        logger.error(f"Erreur de vérification du token: {str(e)}")
        return None

def create_tmux_session(session_id):
    """Crée une nouvelle session tmux pour Claude Code"""
    os.makedirs(f"{SESSIONS_DIR}/{session_id}", exist_ok=True)
    
    logger.info("Vérification de la session principale Claude Code")
    
    # Arrêter les sessions existantes pour tout nettoyer
    subprocess.run("tmux kill-session -t claude-code-session 2>/dev/null || true", shell=True)
    subprocess.run(f"tmux kill-session -t claude_{session_id} 2>/dev/null || true", shell=True)
    
    logger.info("Création d'une nouvelle session Claude Code principale")
    
    # S'assurer que les sockets tmux ont les bonnes permissions
    subprocess.run("mkdir -p /tmp/tmux-0", shell=True)
    subprocess.run("chmod -R 777 /tmp/tmux-0", shell=True)
    
    # Exporter la variable TMUX pour éviter des conflits de sessions
    os.environ.pop('TMUX', None)
    
    # Créer une session tmux pour Claude Code avec un contenu initial visible
    subprocess.run("cd /root && TMUX= tmux -S /tmp/tmux-0/default new-session -d -s claude-code-session", shell=True)
    
    # S'assurer que les permissions du socket sont correctes
    subprocess.run("chmod 777 /tmp/tmux-0/default", shell=True)
    
    # Configurer l'environnement et afficher un message de bienvenue
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'clear' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\\033[1;32mBienvenue dans Claude Code Web!\\033[0m\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\\033[1;36mTerminal interactif pour Claude Code\\033[0m\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"-------------------------------------\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'export PATH=/root/.npm-global/bin:$PATH' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'cd /root/docker' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'ls -la' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\\033[1;33mPrêt à utiliser Claude Code...\\033[0m\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\\033[0;37mTapez votre question ou commande ci-dessous:\\033[0m\"' C-m", shell=True)
    
    # Attendre un peu pour que les commandes s'exécutent
    time.sleep(3)
    
    # Créer une session utilisateur attachée à la session principale
    logger.info(f"Création d'une nouvelle session utilisateur claude_{session_id}")
    subprocess.run(f"TMUX= tmux -S /tmp/tmux-0/default new-session -d -s claude_{session_id} -t claude-code-session", shell=True)
    
    # Lancer Claude après avoir créé les sessions clones
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session 'echo \"\"' C-m", shell=True)
    subprocess.run("tmux -S /tmp/tmux-0/default send-keys -t claude-code-session '/root/.npm-global/bin/claude' C-m", shell=True)
    
    # Synchroniser l'écran
    time.sleep(2)
    subprocess.run(f"tmux -S /tmp/tmux-0/default send-keys -t claude_{session_id} ' ' C-h", shell=True)
    
    # Ajuster la taille du tampon d'historique pour capturer plus de contenu
    subprocess.run("tmux -S /tmp/tmux-0/default set-option -g history-limit 5000", shell=True)
    
    logger.info(f"Session tmux claude_{session_id} créée et prête")
    
    # Capturer la sortie actuelle pour vérification
    output = get_tmux_output(session_id)
    logger.info(f"Contenu initial de la session: {len(output)} caractères")
    
    return session_id

def get_tmux_output(session_id):
    """Récupère la sortie de la session tmux"""
    try:
        # Essayer d'abord la session principale (source de vérité)
        cmd_main = f"tmux -S /tmp/tmux-0/default capture-pane -p -S -1000 -t claude-code-session"
        result_main = subprocess.run(cmd_main, shell=True, capture_output=True, text=True)
        main_output = result_main.stdout
        
        # Puis la session utilisateur comme backup
        cmd = f"tmux -S /tmp/tmux-0/default capture-pane -p -S -1000 -t claude_{session_id}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        user_output = result.stdout
        
        # Comparer et choisir le meilleur résultat
        if len(main_output.strip()) > len(user_output.strip()):
            logger.info(f"Utilisation de la sortie principale: {len(main_output)} caractères")
            final_output = main_output
        else:
            logger.info(f"Utilisation de la sortie utilisateur: {len(user_output)} caractères")
            final_output = user_output
        
        # Si toujours pas de contenu, créer un message par défaut
        if len(final_output.strip()) < 10:
            logger.warning("Sortie trop courte, ajout d'un message par défaut")
            final_output = "Bienvenue dans Claude Code Web\n\n" + \
                          "Terminal interactif pour Claude Code\n" + \
                          "--------------------------------------\n\n" + \
                          "Prêt à recevoir vos commandes...\n" + \
                          "Tapez votre message et appuyez sur Ctrl+Enter pour l'envoyer."
        
        # Nettoyer la sortie
        final_output = final_output.rstrip()
        
        return final_output
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sortie tmux: {str(e)}")
        # Retourner un message d'erreur formaté en cas d'échec
        return f"Erreur de connexion au terminal.\nDétails: {str(e)}\n\nRéessayez ou rechargez la page."

def send_to_tmux(session_id, command):
    """Envoie une commande à la session tmux"""
    # Échapper les caractères spéciaux dans la commande
    escaped_command = command.replace("'", "'\\''")
    
    # Envoyer directement la commande à la session principale pour être sûr
    logger.info(f"Envoi de la commande à la session principale: {escaped_command}")
    cmd_main = f"tmux -S /tmp/tmux-0/default send-keys -t claude-code-session '{escaped_command}' C-m"
    subprocess.run(cmd_main, shell=True)
    
    # Envoyer également à la session utilisateur
    logger.info(f"Envoi de la commande à la session utilisateur: {escaped_command}")
    cmd = f"tmux -S /tmp/tmux-0/default send-keys -t claude_{session_id} '{escaped_command}' C-m"
    subprocess.run(cmd, shell=True)
    
    # Synchroniser les deux sessions
    subprocess.run(f"tmux -S /tmp/tmux-0/default refresh-client -t claude_{session_id} 2>/dev/null || true", shell=True)
    subprocess.run(f"tmux -S /tmp/tmux-0/default refresh-client -t claude-code-session 2>/dev/null || true", shell=True)
    
    # Attendre un peu pour que la commande s'exécute et que Claude Code réponde
    time.sleep(2)
    
    # Capturer la sortie de la session principale Claude Code
    output_main = subprocess.run(f"tmux -S /tmp/tmux-0/default capture-pane -p -S -1000 -t claude-code-session", 
                            shell=True, capture_output=True, text=True).stdout
    
    # Capturer aussi la sortie de la session utilisateur
    output_user = get_tmux_output(session_id)
    
    # Choisir l'output le plus complet
    output = output_main if len(output_main) > len(output_user) else output_user
    
    logger.info(f"Commande envoyée: {command}, Réponse reçue de longueur {len(output)}")
    
    return output

def monitor_tmux_output(session_id, client_id):
    """Surveille la sortie d'une session tmux et envoie les mises à jour via WebSocket"""
    last_output = ""
    logger.info(f"Démarrage de la surveillance pour la session {session_id}, client {client_id}")
    
    # Forcer une première mise à jour immédiate
    try:
        # Capturer la sortie initiale et l'envoyer immédiatement
        main_output = subprocess.run(f"tmux -S /tmp/tmux-0/default capture-pane -p -S -1000 -t claude-code-session", 
                                  shell=True, capture_output=True, text=True).stdout
        
        user_output = get_tmux_output(session_id)
        current_output = main_output if len(main_output) > len(user_output) else user_output
        
        socketio.emit('tmux_output', {
            'session_id': session_id,
            'output': current_output
        }, to=client_id)
        
        last_output = current_output
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la sortie initiale pour {session_id}: {str(e)}")
    
    while session_id in active_sessions:
        try:
            # Vérifier d'abord la session principale avec plus de lignes d'historique
            main_output = subprocess.run(f"tmux -S /tmp/tmux-0/default capture-pane -p -S -1000 -t claude-code-session", 
                                      shell=True, capture_output=True, text=True).stdout
            
            # Puis capturer la sortie de la session utilisateur
            user_output = get_tmux_output(session_id)
            
            # Choisir l'output le plus complet
            current_output = main_output if len(main_output) > len(user_output) else user_output
            
            # Comparer et envoyer si différent
            if current_output != last_output:
                logger.info(f"Nouvelle sortie détectée pour la session {session_id}, envoi au client {client_id}")
                socketio.emit('tmux_output', {
                    'session_id': session_id,
                    'output': current_output
                }, to=client_id)
                
                last_output = current_output
                
                # Synchroniser les sessions entre elles
                subprocess.run(f"tmux -S /tmp/tmux-0/default refresh-client -t claude_{session_id} 2>/dev/null || true", shell=True)
                subprocess.run(f"tmux -S /tmp/tmux-0/default refresh-client -t claude-code-session 2>/dev/null || true", shell=True)
            
            # Attendre un court moment avant de vérifier à nouveau
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"Erreur lors de la surveillance de la session {session_id}: {str(e)}")
            time.sleep(1)  # Attendre un peu plus longtemps en cas d'erreur
    
    logger.info(f"Arrêt de la surveillance pour la session {session_id}, client {client_id}")

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Si c'est une route API, ne pas intercepter
    if path.startswith('api/'):
        return jsonify({"error": "API route not found"}), 404
    
    # Vérifier si le fichier existe dans static_folder
    static_file = os.path.join(app.static_folder, path)
    if os.path.isfile(static_file):
        return send_from_directory(app.static_folder, path)
    
    # Pour toutes les autres routes (routes SPA), servir index.html
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authentifie un utilisateur"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Vérification simplifiée - à remplacer par une vérification réelle
    valid_users = {
        'admin': 'claude_admin',
        'colaig': 'colaigialoc'
    }
    
    if username in valid_users and password == valid_users[username]:
        user_id = str(uuid.uuid4())
        token = generate_token(user_id, username)
        logger.info(f"Utilisateur {username} authentifié avec succès")
        return jsonify({"token": token, "user_id": user_id, "username": username})
    
    logger.warning(f"Tentative d'authentification échouée pour {username}")
    return jsonify({"error": "Identifiants invalides"}), 401

@app.route('/api/session/new', methods=['POST'])
def new_session():
    """Crée une nouvelle session tmux"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    user_id = payload['user_id']
    username = payload['username']
    
    session_id = str(uuid.uuid4())
    create_tmux_session(session_id)
    active_sessions[session_id] = user_id
    
    logger.info(f"Nouvelle session {session_id} créée pour {username}")
    return jsonify({"session_id": session_id})

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """Liste les sessions tmux actives"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    # Récupérer toutes les sessions tmux
    result = subprocess.run("tmux list-sessions -F '#{session_name}'", 
                          shell=True, capture_output=True, text=True)
    
    sessions = []
    for line in result.stdout.strip().split('\n'):
        if line.startswith('claude_') and line != '':
            session_id = line.replace('claude_', '')
            sessions.append({
                "id": session_id,
                "created_at": datetime.now().isoformat()
            })
    
    return jsonify(sessions)

@app.route('/api/docker/apps', methods=['GET'])
def list_docker_apps():
    """Liste les applications Docker"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    try:
        if docker_client:
            containers = docker_client.containers.list()
            return jsonify([{
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "none"
            } for container in containers])
        else:
            return jsonify({"error": "Client Docker non disponible"}), 500
    except Exception as e:
        logger.error(f"Erreur lors de la liste des applications Docker: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/n8n/workflows', methods=['GET'])
def list_n8n_workflows():
    """Liste les workflows n8n"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    try:
        headers = {'X-N8N-API-KEY': N8N_API_KEY}
        response = requests.get(f"{N8N_API_URL}/api/v1/workflows", headers=headers)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Erreur lors de la liste des workflows n8n: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# ROUTES GESTION DES PROJETS
# ================================

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """Liste tous les projets disponibles"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    try:
        projects = []
        apps_dir = f"{DOCKER_PATH}/apps"
        
        # Scanner le dossier apps pour trouver les projets
        if os.path.exists(apps_dir):
            for project_name in os.listdir(apps_dir):
                project_path = os.path.join(apps_dir, project_name)
                if os.path.isdir(project_path):
                    # Lire les métadonnées du projet
                    project_info = get_project_info(project_name, project_path)
                    projects.append(project_info)
        
        return jsonify(projects)
    except Exception as e:
        logger.error(f"Erreur lors de la liste des projets: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Crée un nouveau projet"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    data = request.json
    project_name = data.get('name', '').strip()
    template = data.get('template', '').strip()
    description = data.get('description', '').strip()
    
    if not project_name or not template:
        return jsonify({"error": "Nom du projet et template requis"}), 400
    
    try:
        # Créer le projet avec l'agent meta
        project_info = create_project_with_meta_agent(project_name, template, description)
        return jsonify(project_info), 201
    except Exception as e:
        logger.error(f"Erreur lors de la création du projet: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/<project_id>/session', methods=['POST'])
def create_project_session(project_id):
    """Crée ou récupère une session tmux pour un projet spécifique"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    try:
        # Vérifier que le projet existe
        project_path = f"{DOCKER_PATH}/apps/{project_id}"
        if not os.path.exists(project_path):
            return jsonify({"error": "Projet non trouvé"}), 404
        
        # Créer ou récupérer la session tmux pour ce projet
        session_id = get_or_create_project_session(project_id)
        
        return jsonify({"session_id": session_id, "project_id": project_id})
    except Exception as e:
        logger.error(f"Erreur lors de la création de la session projet: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Supprime un projet"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "Non autorisé"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    
    try:
        project_path = f"{DOCKER_PATH}/apps/{project_id}"
        if not os.path.exists(project_path):
            return jsonify({"error": "Projet non trouvé"}), 404
        
        # Arrêter les services Docker du projet
        stop_project_services(project_id)
        
        # Supprimer la session tmux associée
        cleanup_project_session(project_id)
        
        # Supprimer le dossier du projet (optionnel - à commenter si trop dangereux)
        # import shutil
        # shutil.rmtree(project_path)
        
        return jsonify({"message": "Projet supprimé avec succès"})
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du projet: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================================
# FONCTIONS UTILITAIRES PROJETS
# ================================

def get_project_info(project_name, project_path):
    """Récupère les informations d'un projet"""
    try:
        # Lire docker-compose.yml pour déterminer le template
        compose_file = os.path.join(project_path, 'docker-compose.yml')
        template = "unknown"
        
        if os.path.exists(compose_file):
            # Analyser le docker-compose pour déterminer le template
            if os.path.exists(os.path.join(project_path, 'frontend')):
                if os.path.exists(os.path.join(project_path, 'backend')):
                    # Check pour React/Vue
                    package_json = os.path.join(project_path, 'frontend', 'package.json')
                    if os.path.exists(package_json):
                        with open(package_json, 'r') as f:
                            content = f.read()
                            if 'react' in content.lower():
                                template = "react-node-postgres"
                            elif 'vue' in content.lower():
                                template = "vue-flask-postgres"
                else:
                    template = "static-site"
            else:
                template = "api-backend"
        
        # Lire README.md pour la description
        readme_file = os.path.join(project_path, 'README.md')
        description = ""
        if os.path.exists(readme_file):
            with open(readme_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    description = lines[1].strip() if lines[1].startswith('#') else lines[0].strip()
        
        # Déterminer le statut
        status = "inactive"
        if docker_client:
            try:
                containers = docker_client.containers.list(filters={"name": project_name})
                if containers:
                    status = "active"
                else:
                    # Vérifier les conteneurs arrêtés
                    stopped_containers = docker_client.containers.list(all=True, filters={"name": project_name})
                    if stopped_containers:
                        status = "developing"
            except:
                pass
        
        # URLs du projet
        urls = {
            "staging": f"https://{project_name}-staging.colaig.fr",
            "production": f"https://{project_name}.colaig.fr",
            "development": f"http://localhost:3000"  # Port par défaut
        }
        
        return {
            "id": project_name,
            "name": project_name,
            "description": description or f"Projet {project_name}",
            "template": template,
            "status": status,
            "created_at": datetime.fromtimestamp(os.path.getctime(project_path)).isoformat(),
            "urls": urls
        }
    except Exception as e:
        logger.error(f"Erreur lors de la lecture des infos du projet {project_name}: {str(e)}")
        return {
            "id": project_name,
            "name": project_name,
            "description": f"Projet {project_name}",
            "template": "unknown",
            "status": "inactive",
            "created_at": datetime.now().isoformat(),
            "urls": {}
        }

def get_or_create_project_session(project_id):
    """Crée ou récupère une session tmux pour un projet"""
    session_name = f"claude_project_{project_id}"
    
    try:
        # D'abord vérifier si la session tmux existe
        result = subprocess.run(f"tmux has-session -t {session_name}", 
                              shell=True, capture_output=True)
        
        if result.returncode == 0:
            # Session tmux existe, vérifier si Claude Code fonctionne
            output = subprocess.run(f"tmux capture-pane -p -t {session_name}", 
                                  shell=True, capture_output=True, text=True)
            
            # Si la session ne contient pas l'interface Claude Code, relancer
            if "Try \"how do I log an error?\"" not in output.stdout and "cwd:" not in output.stdout:
                logger.info(f"Session {session_name} trouvée mais Claude Code non actif, relancement...")
                project_path = f"{DOCKER_PATH}/apps/{project_id}"
                
                # Configurer l'environnement et relancer Claude Code
                subprocess.run(f"tmux send-keys -t {session_name} 'cd {project_path}' C-m", shell=True)
                subprocess.run(f"tmux send-keys -t {session_name} 'export PROJECT_NAME={project_id}' C-m", shell=True)
                subprocess.run(f"tmux send-keys -t {session_name} 'export PROJECT_PATH={project_path}' C-m", shell=True)
                
                claude_md_path = f"{project_path}/CLAUDE.md"
                if os.path.exists(claude_md_path):
                    subprocess.run(f"tmux send-keys -t {session_name} 'export CLAUDE_PROJECT_CONTEXT=\"{claude_md_path}\"' C-m", shell=True)
                
                # Lancer Claude Code avec le chemin complet
                subprocess.run(f"tmux send-keys -t {session_name} '/root/.npm-global/bin/claude' C-m", shell=True)
                time.sleep(3)  # Attendre que Claude Code démarre
            
            # Récupérer ou créer l'ID de session
            if session_name not in project_sessions:
                session_id = str(uuid.uuid4())
                project_sessions[session_name] = session_id
                logger.info(f"Reconnexion à la session tmux {session_name}")
            else:
                session_id = project_sessions[session_name]
            return session_id
        else:
            # Créer une nouvelle session tmux pour ce projet
            project_path = f"{DOCKER_PATH}/apps/{project_id}"
            
            logger.info(f"Création de la session tmux pour le projet {project_id}")
            
            # Créer la session en arrière-plan
            subprocess.run(f"tmux new-session -d -s {session_name}", shell=True)
            
            # Configurer l'environnement pour Claude Code
            subprocess.run(f"tmux send-keys -t {session_name} 'cd {project_path}' C-m", shell=True)
            subprocess.run(f"tmux send-keys -t {session_name} 'export PROJECT_NAME={project_id}' C-m", shell=True)
            subprocess.run(f"tmux send-keys -t {session_name} 'export PROJECT_PATH={project_path}' C-m", shell=True)
            
            # Configurer le contexte CLAUDE.md si disponible
            claude_md_path = f"{project_path}/CLAUDE.md"
            if os.path.exists(claude_md_path):
                subprocess.run(f"tmux send-keys -t {session_name} 'export CLAUDE_PROJECT_CONTEXT=\"{claude_md_path}\"' C-m", shell=True)
                logger.info(f"Contexte CLAUDE.md configuré pour le projet {project_id}")
            
            # Démarrer Claude Code silencieusement
            subprocess.run(f"tmux send-keys -t {session_name} 'clear' C-m", shell=True)
            subprocess.run(f"tmux send-keys -t {session_name} '/root/.npm-global/bin/claude' C-m", shell=True)
            
            # Attendre que Claude Code soit prêt
            time.sleep(3)
            
            time.sleep(2)
            
        session_id = str(uuid.uuid4())
        project_sessions[session_name] = session_id
        
        logger.info(f"Session {session_id} créée pour le projet {project_id}")
        return session_id
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la session projet: {str(e)}")
        raise

def cleanup_project_session(project_id):
    """Nettoie la session tmux d'un projet"""
    session_name = f"claude_project_{project_id}"
    try:
        subprocess.run(f"tmux kill-session -t {session_name} 2>/dev/null || true", shell=True)
        if session_name in project_sessions:
            del project_sessions[session_name]
        logger.info(f"Session du projet {project_id} nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de la session {project_id}: {str(e)}")

def stop_project_services(project_id):
    """Arrête les services Docker d'un projet"""
    try:
        project_path = f"{DOCKER_PATH}/apps/{project_id}"
        compose_file = os.path.join(project_path, 'docker-compose.yml')
        
        if os.path.exists(compose_file):
            subprocess.run(f"cd {project_path} && docker-compose down", shell=True)
            logger.info(f"Services Docker du projet {project_id} arrêtés")
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt des services du projet {project_id}: {str(e)}")

def create_project_with_meta_agent(project_name, template, description):
    """Crée un nouveau projet en utilisant l'agent meta complet"""
    from meta_agent import meta_agent
    
    try:
        # Utiliser l'agent meta pour créer le projet
        result = meta_agent.create_project(
            project_name=project_name,
            template_id=template,
            description=description
        )
        
        logger.info(f"Projet {project_name} créé avec succès via l'agent meta")
        
        # Retourner les informations du projet créé
        project_path = result["path"]
        return get_project_info(project_name, project_path)
        
    except Exception as e:
        logger.error(f"Erreur lors de la création via l'agent meta: {str(e)}")
        raise

@socketio.on('connect')
def handle_connect():
    """Gère la connexion WebSocket"""
    logger.info(f"Client connecté: {request.sid}")

@socketio.on('join')
def handle_join(data):
    """Gère la connexion à une session spécifique"""
    session_id = data.get('session_id')
    token = data.get('token')
    
    payload = verify_token(token)
    if not payload:
        emit('error', {'message': 'Token invalide'})
        return
    
    user_id = payload['user_id']
    username = payload['username']
    
    if session_id not in active_sessions:
        try:
            # Si la session n'existe pas, on la crée
            create_tmux_session(session_id)
            active_sessions[session_id] = user_id
        except Exception as e:
            logger.error(f"Erreur lors de la création de la session {session_id}: {str(e)}")
            emit('error', {'message': f'Erreur lors de la création de la session: {str(e)}'})
            return
    
    # Récupérer la sortie de la session tmux
    output = get_tmux_output(session_id)
    logger.info(f"Utilisateur {username} a rejoint la session {session_id}")
    
    # Rejoindre la room avec l'ID du client
    join_room(request.sid)
    
    # Envoyer la sortie initiale
    emit('joined', {
        'session_id': session_id,
        'initial_output': output
    })
    
    # Démarrer un thread pour surveiller la sortie
    if session_id not in output_threads:
        output_threads[session_id] = threading.Thread(
            target=monitor_tmux_output,
            args=(session_id, request.sid),
            daemon=True
        )
        output_threads[session_id].start()

@socketio.on('message')
def handle_message(data):
    """Traite les messages envoyés par le client"""
    session_id = data.get('session_id')
    message = data.get('message')
    token = data.get('token')
    
    payload = verify_token(token)
    if not payload:
        emit('error', {'message': 'Token invalide'})
        return
    
    user_id = payload['user_id']
    username = payload['username']
    
    if session_id not in active_sessions:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    try:
        logger.info(f"Message de {username} pour session {session_id}: {message}")
        send_to_tmux(session_id, message)
        # La réponse sera envoyée par le thread de surveillance
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
        emit('error', {'message': f'Erreur lors de l\'envoi du message: {str(e)}'})

# ================================
# GESTIONNAIRES WEBSOCKET PROJETS
# ================================

@socketio.on('join_project')
def handle_join_project(data):
    """Gère la connexion à une session projet spécifique"""
    session_id = data.get('session_id')
    project_id = data.get('project_id')
    token = data.get('token')
    
    payload = verify_token(token)
    if not payload:
        emit('error', {'message': 'Token invalide'})
        return
    
    user_id = payload['user_id']
    username = payload['username']
    
    try:
        # Vérifier que le projet existe
        project_path = f"{DOCKER_PATH}/apps/{project_id}"
        if not os.path.exists(project_path):
            emit('error', {'message': 'Projet non trouvé'})
            return
        
        # Rejoindre la room pour ce projet
        join_room(f"project_{project_id}")
        
        # Récupérer la sortie initiale de la session tmux du projet
        session_name = f"claude_project_{project_id}"
        initial_output = get_project_tmux_output(session_name)
        
        logger.info(f"Utilisateur {username} a rejoint le projet {project_id}")
        
        emit('joined', {
            'session_id': session_id,
            'project_id': project_id,
            'initial_output': initial_output
        })
        
        # Démarrer le monitoring de la session projet
        if session_name not in output_threads:
            output_threads[session_name] = threading.Thread(
                target=monitor_project_tmux_output,
                args=(session_name, project_id, request.sid),
                daemon=True
            )
            output_threads[session_name].start()
            
    except Exception as e:
        logger.error(f"Erreur lors de la connexion au projet {project_id}: {str(e)}")
        emit('error', {'message': f'Erreur lors de la connexion au projet: {str(e)}'})

# Catch-all pour débugger
@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"SocketIO Error: {e}")

@socketio.on('project_message')
def handle_project_message(data):
    logger.info(f"RECEIVED project_message: {data}")
    """Traite les messages envoyés pour un projet spécifique"""
    session_id = data.get('session_id')
    project_id = data.get('project_id')
    message = data.get('message')
    token = data.get('token')
    
    payload = verify_token(token)
    if not payload:
        emit('error', {'message': 'Token invalide'})
        return
    
    user_id = payload['user_id']
    username = payload['username']
    
    try:
        session_name = f"claude_project_{project_id}"
        
        logger.info(f"Message de {username} pour projet {project_id}: {message}")
        send_to_project_tmux(session_name, message)
        
        # Récupérer immédiatement la sortie mise à jour et l'envoyer
        new_output = get_project_tmux_output(session_name)
        if new_output:
            # Envoyer au room du projet
            emit('output', {'output': new_output}, room=f"project_{project_id}")
            logger.info(f"Sortie mise à jour envoyée pour le projet {project_id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message au projet: {str(e)}")
        emit('error', {'message': f'Erreur lors de l\'envoi du message: {str(e)}'})

def get_project_tmux_output(session_name):
    """Récupère la sortie de la session tmux d'un projet"""
    try:
        cmd = f"tmux capture-pane -p -S -1000 -t {session_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        output = result.stdout
        
        # Si pas de contenu, créer un message d'accueil
        if len(output.strip()) < 10:
            output = f"Terminal du projet\n\nSession: {session_name}\nPrêt à recevoir vos commandes...\n"
        
        return output.rstrip()
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sortie du projet: {str(e)}")
        return f"Erreur de connexion au terminal du projet.\nDétails: {str(e)}"

def send_to_project_tmux(session_name, command):
    """Envoie une commande à la session Claude Code dédiée du projet"""
    try:
        # Échapper les caractères spéciaux
        escaped_command = command.replace("'", "'\\''")
        
        # Envoyer le message avec C-m inclus dans le message puis C-m pour l'exécuter
        cmd = f"tmux send-keys -t {session_name} '{escaped_command} C-m' C-m"
        subprocess.run(cmd, shell=True)
        
        logger.info(f"Message envoyé à Claude Code {session_name}: {command}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message à Claude Code: {str(e)}")
        raise

def monitor_project_tmux_output(session_name, project_id, client_id):
    """Surveille la sortie d'une session tmux de projet et envoie les mises à jour"""
    logger.info(f"Démarrage de la surveillance pour le projet {project_id}, session {session_name}")
    
    previous_output = ""
    
    while True:
        try:
            # Vérifier si la session tmux existe encore
            result = subprocess.run(f"tmux has-session -t {session_name}", 
                                  shell=True, capture_output=True)
            
            if result.returncode != 0:
                logger.info(f"Session tmux {session_name} fermée, arrêt de la surveillance")
                break
            
            # Récupérer la sortie actuelle
            current_output = get_project_tmux_output(session_name)
            
            # Si la sortie a changé, l'envoyer au client
            if current_output != previous_output:
                socketio.emit('output', {
                    'output': current_output,
                    'project_id': project_id,
                    'session_name': session_name
                }, room=f"project_{project_id}")
                
                previous_output = current_output
            
            # Attendre avant la prochaine vérification
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Erreur lors de la surveillance du projet {project_id}: {str(e)}")
            time.sleep(1)
    
    logger.info(f"Arrêt de la surveillance pour le projet {project_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """Gère la déconnexion WebSocket"""
    logger.info(f"Client déconnecté: {request.sid}")

if __name__ == '__main__':
    # Créer le répertoire des sessions s'il n'existe pas
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    
    # Récupérer les origines autorisées depuis les variables d'environnement
    cors_origins = os.environ.get('CORS_ALLOW_ORIGINS', 'https://claude.colaig.fr').split(',')
    logger.info(f"Origines CORS autorisées: {cors_origins}")
    
    # Démarrer le serveur avec les options simples (compatibles avec cette version de Flask-SocketIO)
    logger.info("Démarrage du serveur Claude Code Web")
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False
    )