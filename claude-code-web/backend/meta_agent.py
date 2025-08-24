#!/usr/bin/env python3
"""
Agent Meta Claude Code - Orchestrateur de Projets
=================================================

Cet agent meta orchestre la création et la gestion des projets selon les règles
définies dans CLAUDE.md et les templates disponibles.

Fonctionnalités :
- Analyse des exigences de projet
- Sélection automatique du template optimal
- Application des standards Docker/Traefik
- Configuration SSL automatique
- Génération de la structure complète
- Application des règles de conformité
"""

import os
import json
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class MetaAgent:
    """Agent Meta pour l'orchestration des projets Claude Code"""
    
    def __init__(self, docker_path="/root/docker"):
        self.docker_path = docker_path
        self.apps_path = os.path.join(docker_path, "apps")
        self.templates_path = os.path.join(docker_path, "templates")
        self.claude_md_path = os.path.join(docker_path, "CLAUDE.md")
        
        # Templates disponibles et leurs caractéristiques
        self.templates = {
            "react-node-postgres": {
                "name": "React + Node.js + PostgreSQL",
                "description": "Stack moderne pour applications web complexes",
                "tech_stack": ["React", "Node.js", "Express", "PostgreSQL", "Vite"],
                "use_cases": ["spa", "dashboard", "app web", "interface utilisateur"],
                "complexity": "high",
                "ports": {"frontend": 3000, "backend": 5000, "db": 5432}
            },
            "vue-flask-postgres": {
                "name": "Vue.js + Flask + PostgreSQL", 
                "description": "Stack Python pour développement rapide",
                "tech_stack": ["Vue.js", "Flask", "SQLAlchemy", "PostgreSQL"],
                "use_cases": ["api", "prototype", "mvp", "python"],
                "complexity": "medium",
                "ports": {"frontend": 8080, "backend": 5000, "db": 5432}
            },
            "static-site": {
                "name": "Site Statique",
                "description": "Site web statique optimisé",
                "tech_stack": ["HTML", "CSS", "JavaScript", "Nginx"],
                "use_cases": ["blog", "vitrine", "documentation", "landing"],
                "complexity": "low",
                "ports": {"frontend": 80}
            },
            "api-backend": {
                "name": "API Backend",
                "description": "Service API backend uniquement",
                "tech_stack": ["Node.js", "Express", "PostgreSQL", "MongoDB"],
                "use_cases": ["api", "microservice", "backend", "service"],
                "complexity": "medium",
                "ports": {"backend": 5000, "db": 5432}
            }
        }
        
        # Règles de conformité (basées sur CLAUDE.md)
        self.compliance_rules = {
            "mandatory_files": [
                "docker-compose.yml",
                "README.md",
                ".env.example"
            ],
            "mandatory_labels": [
                "traefik.enable=true",
                "traefik.http.routers.{app}.rule=Host(`{app}.colaig.fr`)",
                "traefik.http.routers.{app}.entrypoints=websecure",
                "traefik.http.routers.{app}.tls=true",
                "traefik.http.routers.{app}.tls.certresolver=letsencrypt"
            ],
            "required_structure": [
                "frontend/",
                "backend/", 
                "database/",
                "tests/",
                "docs/"
            ],
            "environments": ["development", "staging", "production"]
        }

    def analyze_project_requirements(self, description, preferences=None):
        """Analyse les exigences du projet et recommande un template"""
        description_lower = description.lower()
        preferences = preferences or {}
        
        scores = {}
        
        for template_id, template in self.templates.items():
            score = 0
            
            # Score basé sur les mots-clés dans la description
            for use_case in template["use_cases"]:
                if use_case in description_lower:
                    score += 3
            
            # Score basé sur les technologies mentionnées
            for tech in template["tech_stack"]:
                if tech.lower() in description_lower:
                    score += 2
            
            # Ajustements basés sur les préférences
            if preferences.get("complexity") == template["complexity"]:
                score += 1
            
            if preferences.get("preferred_tech"):
                for tech in preferences["preferred_tech"]:
                    if tech.lower() in [t.lower() for t in template["tech_stack"]]:
                        score += 2
            
            scores[template_id] = score
        
        # Retourner le template avec le meilleur score
        best_template = max(scores, key=scores.get)
        
        logger.info(f"Analyse terminée - Template recommandé: {best_template} (score: {scores[best_template]})")
        logger.info(f"Scores détaillés: {scores}")
        
        return {
            "recommended": best_template,
            "scores": scores,
            "template_info": self.templates[best_template]
        }

    def create_project(self, project_name, template_id, description, user_preferences=None):
        """Crée un projet complet avec le template spécifié"""
        logger.info(f"Création du projet '{project_name}' avec le template '{template_id}'")
        
        # Valider les entrées
        if not self._validate_project_inputs(project_name, template_id):
            raise ValueError("Paramètres de projet invalides")
        
        project_path = os.path.join(self.apps_path, project_name)
        
        # Vérifier que le projet n'existe pas déjà
        if os.path.exists(project_path):
            raise FileExistsError(f"Le projet '{project_name}' existe déjà")
        
        try:
            # 1. Créer la structure de base
            self._create_base_structure(project_path, project_name)
            
            # 2. Copier et adapter le template
            self._apply_template(project_path, template_id, project_name)
            
            # 3. Générer les fichiers de configuration
            self._generate_config_files(project_path, project_name, template_id, description)
            
            # 4. Appliquer les règles de conformité
            self._apply_compliance_rules(project_path, project_name, template_id)
            
            # 5. Initialiser les tests
            self._setup_testing_framework(project_path, template_id)
            
            # 6. Créer la documentation
            self._generate_documentation(project_path, project_name, template_id, description)
            
            logger.info(f"Projet '{project_name}' créé avec succès")
            
            return {
                "status": "success",
                "project_name": project_name,
                "template": template_id,
                "path": project_path,
                "urls": self._generate_project_urls(project_name),
                "next_steps": self._get_next_steps(template_id)
            }
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            logger.error(f"Erreur lors de la création du projet: {str(e)}")
            raise

    def _validate_project_inputs(self, project_name, template_id):
        """Valide les paramètres d'entrée du projet"""
        # Valider le nom du projet
        if not project_name or not project_name.replace("-", "").replace("_", "").isalnum():
            return False
        
        # Valider le template
        if template_id not in self.templates:
            return False
        
        return True

    def _create_base_structure(self, project_path, project_name):
        """Crée la structure de dossiers de base"""
        logger.info(f"Création de la structure de base pour {project_name}")
        
        os.makedirs(project_path, exist_ok=True)
        
        # Créer les dossiers obligatoires
        for folder in ["frontend", "backend", "database", "tests", "docs"]:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)

    def _apply_template(self, project_path, template_id, project_name):
        """Copie et adapte le template choisi"""
        logger.info(f"Application du template {template_id}")
        
        template_path = os.path.join(self.templates_path, template_id)
        
        # Si le template existe physiquement, le copier
        if os.path.exists(template_path):
            for item in os.listdir(template_path):
                src = os.path.join(template_path, item)
                dst = os.path.join(project_path, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        else:
            # Générer la structure selon le template
            self._generate_template_structure(project_path, template_id, project_name)

    def _generate_template_structure(self, project_path, template_id, project_name):
        """Génère la structure du template si les fichiers template n'existent pas"""
        template_info = self.templates[template_id]
        
        if template_id == "react-node-postgres":
            self._create_react_node_structure(project_path, project_name)
        elif template_id == "vue-flask-postgres":
            self._create_vue_flask_structure(project_path, project_name)
        elif template_id == "static-site":
            self._create_static_site_structure(project_path, project_name)
        elif template_id == "api-backend":
            self._create_api_backend_structure(project_path, project_name)

    def _generate_config_files(self, project_path, project_name, template_id, description):
        """Génère les fichiers de configuration"""
        logger.info("Génération des fichiers de configuration")
        
        # Générer CLAUDE.md spécialisé (NOUVEAU)
        self._generate_specialized_claude_md(project_path, project_name, template_id, description)
        
        # Générer docker-compose.yml
        self._generate_docker_compose(project_path, project_name, template_id)
        
        # Générer .env.example
        self._generate_env_example(project_path, template_id)
        
        # Générer README.md
        self._generate_readme(project_path, project_name, template_id, description)
        
        # Générer scripts de développement (NOUVEAU)
        self._generate_development_scripts(project_path, project_name, template_id)

    def _generate_docker_compose(self, project_path, project_name, template_id):
        """Génère le fichier docker-compose.yml avec les labels Traefik"""
        template_info = self.templates[template_id]
        ports = template_info["ports"]
        
        compose_content = f"""version: '3.8'

services:"""

        # Frontend (si applicable)
        if "frontend" in ports:
            compose_content += f"""
  frontend:
    build: ./frontend
    container_name: {project_name}-frontend
    restart: always
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - proxy
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{project_name}.rule=Host(`{project_name}.colaig.fr`)"
      - "traefik.http.routers.{project_name}.entrypoints=websecure"
      - "traefik.http.routers.{project_name}.tls=true"
      - "traefik.http.routers.{project_name}.tls.certresolver=letsencrypt"
      - "traefik.http.services.{project_name}.loadbalancer.server.port={ports['frontend']}"
      - "traefik.docker.network=proxy"
      - "traefik.http.routers.{project_name}-staging.rule=Host(`{project_name}-staging.colaig.fr`)"
      - "traefik.http.routers.{project_name}-staging.entrypoints=websecure"
      - "traefik.http.routers.{project_name}-staging.tls=true"
      - "traefik.http.routers.{project_name}-staging.tls.certresolver=letsencrypt"
"""

        # Backend (si applicable)
        if "backend" in ports:
            compose_content += f"""
  backend:
    build: ./backend
    container_name: {project_name}-backend
    restart: always
    volumes:
      - ./backend:/app
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@database:5432/{project_name}
    networks:
      - internal
    depends_on:
      - database
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{project_name}-api.rule=Host(`{project_name}-api.colaig.fr`)"
      - "traefik.http.routers.{project_name}-api.entrypoints=websecure"
      - "traefik.http.routers.{project_name}-api.tls=true"
      - "traefik.http.routers.{project_name}-api.tls.certresolver=letsencrypt"
      - "traefik.http.services.{project_name}-api.loadbalancer.server.port={ports['backend']}"
      - "traefik.docker.network=proxy"
"""

        # Database (si applicable)
        if "db" in ports:
            compose_content += f"""
  database:
    image: postgres:15
    container_name: {project_name}-db
    restart: always
    environment:
      - POSTGRES_DB={project_name}
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3
"""

        # Networks et volumes
        compose_content += f"""

networks:
  proxy:
    external: true
  internal:
    driver: bridge

volumes:
  postgres_data:
"""

        with open(os.path.join(project_path, "docker-compose.yml"), "w") as f:
            f.write(compose_content)

    def _generate_env_example(self, project_path, template_id):
        """Génère le fichier .env.example"""
        env_content = f"""# Configuration {template_id}
# Copier vers .env et modifier selon vos besoins

# Base de données
DATABASE_URL=postgresql://postgres:password@localhost:5432/myproject
POSTGRES_DB=myproject
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Application
NODE_ENV=development
PORT=3000
API_PORT=5000

# Sécurité
JWT_SECRET=your-jwt-secret-here
SESSION_SECRET=your-session-secret-here

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:5000
"""

        with open(os.path.join(project_path, ".env.example"), "w") as f:
            f.write(env_content)

    def _generate_readme(self, project_path, project_name, template_id, description):
        """Génère le README.md du projet"""
        template_info = self.templates[template_id]
        
        readme_content = f"""# {project_name}

{description}

## 🚀 Template utilisé
**{template_info['name']}** - {template_info['description']}

### Technologies
{' • '.join(template_info['tech_stack'])}

## 📋 Prérequis
- Docker et Docker Compose
- Node.js (pour développement local)
- Git

## 🛠️ Installation

### Développement local
```bash
# Cloner le projet
cd /root/docker/apps/{project_name}

# Copier les variables d'environnement
cp .env.example .env

# Modifier .env selon vos besoins
nano .env

# Démarrer les services
docker-compose up -d --build

# Voir les logs
docker-compose logs -f
```

## 🌐 URLs d'accès

### Environnements
- **Development**: http://localhost:{template_info['ports'].get('frontend', 3000)}
- **Staging**: https://{project_name}-staging.colaig.fr
- **Production**: https://{project_name}.colaig.fr

### APIs (si applicable)
- **API Development**: http://localhost:{template_info['ports'].get('backend', 5000)}
- **API Staging**: https://{project_name}-api-staging.colaig.fr
- **API Production**: https://{project_name}-api.colaig.fr

## 🧪 Tests
```bash
# Tests frontend
cd frontend && npm test

# Tests backend
cd backend && npm test

# Tests complets
docker-compose -f docker-compose.test.yml up --build
```

## 📁 Structure du projet
```
{project_name}/
├── frontend/              # Application client-side
├── backend/               # API server-side
├── database/              # Configurations DB et migrations
├── tests/                 # Tests automatisés
├── docs/                  # Documentation
├── docker-compose.yml     # Orchestration Docker
├── .env.example           # Variables d'environnement
└── README.md              # Cette documentation
```

## 🚀 Déploiement

Le déploiement se fait automatiquement via Docker et Traefik :
- SSL automatique via Let's Encrypt
- Reverse proxy configuré
- Environnements de staging et production

## 📖 Documentation

Consultez le dossier `docs/` pour une documentation détaillée.

---
*Projet créé le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} avec Claude Code Web*
"""

        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)

    def _generate_specialized_claude_md(self, project_path, project_name, template_id, description):
        """Génère un fichier CLAUDE.md spécialisé pour le projet"""
        logger.info(f"Génération du CLAUDE.md spécialisé pour {template_id}")
        
        template_info = self.templates[template_id]
        
        # Base commune pour tous les CLAUDE.md
        claude_md_content = f"""# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**{project_name}** - {description}

### Template: {template_info['name']}
{template_info['description']}

### Technology Stack
{' • '.join(template_info['tech_stack'])}

### Project Complexity: {template_info['complexity'].title()}

## Architecture

"""
        
        # Ajouter l'architecture spécifique selon le template
        if template_id == "react-node-postgres":
            claude_md_content += self._get_react_node_architecture(project_name, template_info)
        elif template_id == "vue-flask-postgres":
            claude_md_content += self._get_vue_flask_architecture(project_name, template_info)
        elif template_id == "static-site":
            claude_md_content += self._get_static_site_architecture(project_name, template_info)
        elif template_id == "api-backend":
            claude_md_content += self._get_api_backend_architecture(project_name, template_info)
        
        # Section commune de développement
        claude_md_content += f"""

## Development Commands

### Quick Start
```bash
# Copy environment variables
cp .env.example .env

# Edit configuration
nano .env

# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### Development Workflow
```bash
# Development mode
./scripts/start.sh

# Build for production  
./scripts/build.sh

# Run tests
./scripts/test.sh

# Deploy to staging
./scripts/deploy.sh staging
```

### Container Management
```bash
# Stop all services
docker-compose down

# Restart specific service
docker-compose restart frontend

# Rebuild and restart
docker-compose up -d --build frontend

# View service logs
docker-compose logs -f frontend
```

## Environment URLs

### Development
- Frontend: http://localhost:{template_info['ports'].get('frontend', 3000)}"""
        
        if 'backend' in template_info['ports']:
            claude_md_content += f"""
- Backend API: http://localhost:{template_info['ports']['backend']}"""
        
        if 'db' in template_info['ports']:
            claude_md_content += f"""
- Database: localhost:{template_info['ports']['db']}"""
            
        claude_md_content += f"""

### Staging
- Frontend: https://{project_name}-staging.colaig.fr"""
        
        if 'backend' in template_info['ports']:
            claude_md_content += f"""
- API: https://{project_name}-api-staging.colaig.fr"""
            
        claude_md_content += f"""

### Production  
- Frontend: https://{project_name}.colaig.fr"""
        
        if 'backend' in template_info['ports']:
            claude_md_content += f"""
- API: https://{project_name}-api.colaig.fr"""

        # Ajouter les spécificités de développement selon le template
        claude_md_content += self._get_template_specific_guidance(template_id, project_name, template_info)
        
        # Footer commun
        claude_md_content += f"""

## Code Conventions

### Naming
- Files: kebab-case (my-component.js)
- Variables: camelCase (myVariable)
- Constants: UPPER_SNAKE_CASE (API_URL)
- Components: PascalCase (MyComponent)

### Git Workflow
- Main branch: `main`
- Feature branches: `feature/feature-name`
- Commit format: `type: description` (feat: add user authentication)

## Deployment

### Docker & Traefik
All services are automatically configured with:
- SSL certificates via Let's Encrypt
- Reverse proxy routing
- Health checks
- Auto-restart policies

### Environment Variables
Required variables are documented in `.env.example`. Never commit actual `.env` files.

### Database
Database migrations and seeds are in the `database/` directory.

## Security Considerations

- All secrets in environment variables
- HTTPS only in production
- CORS configured for specific origins
- Database access restricted to backend services
- Regular security updates via Docker images

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Claude Code Web Meta Agent*
"""
        
        with open(os.path.join(project_path, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write(claude_md_content)

    def _generate_development_scripts(self, project_path, project_name, template_id):
        """Génère les scripts de développement automatiques"""
        logger.info("Génération des scripts de développement")
        
        scripts_path = os.path.join(project_path, "scripts")
        os.makedirs(scripts_path, exist_ok=True)
        
        template_info = self.templates[template_id]
        
        # Script start.sh - Démarrage développement
        start_script = self._generate_start_script(template_id, project_name, template_info)
        with open(os.path.join(scripts_path, "start.sh"), "w") as f:
            f.write(start_script)
        os.chmod(os.path.join(scripts_path, "start.sh"), 0o755)
        
        # Script build.sh - Build production
        build_script = self._generate_build_script(template_id, project_name, template_info)
        with open(os.path.join(scripts_path, "build.sh"), "w") as f:
            f.write(build_script)
        os.chmod(os.path.join(scripts_path, "build.sh"), 0o755)
        
        # Script test.sh - Tests automatisés
        test_script = self._generate_test_script(template_id, project_name, template_info)
        with open(os.path.join(scripts_path, "test.sh"), "w") as f:
            f.write(test_script)
        os.chmod(os.path.join(scripts_path, "test.sh"), 0o755)
        
        # Script deploy.sh - Déploiement
        deploy_script = self._generate_deploy_script(template_id, project_name, template_info)
        with open(os.path.join(scripts_path, "deploy.sh"), "w") as f:
            f.write(deploy_script)
        os.chmod(os.path.join(scripts_path, "deploy.sh"), 0o755)

    def _generate_start_script(self, template_id, project_name, template_info):
        """Génère le script start.sh selon le template"""
        base_script = f"""#!/bin/bash
# Script de démarrage pour {project_name}
# Template: {template_id}

set -e

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

echo -e "${{BLUE}}🚀 Démarrage de {project_name}${{NC}}"
echo -e "${{BLUE}}============================${{NC}}"

# Vérifier que .env existe
if [ ! -f .env ]; then
    echo -e "${{YELLOW}}⚠️  Fichier .env manquant, copie depuis .env.example${{NC}}"
    cp .env.example .env
    echo -e "${{YELLOW}}📝 Veuillez modifier .env selon vos besoins${{NC}}"
fi

"""
        
        if template_id == "react-node-postgres":
            base_script += f"""
# Démarrer la base de données
echo -e "${{BLUE}}🗄️  Démarrage de PostgreSQL...${{NC}}"
docker-compose up -d database
sleep 5

# Démarrer le backend
echo -e "${{BLUE}}🔧 Démarrage du backend Node.js...${{NC}}"
cd backend
if [ ! -d node_modules ]; then
    echo -e "${{YELLOW}}📦 Installation des dépendances backend...${{NC}}"
    npm install
fi
npm run dev &
BACKEND_PID=$!
cd ..

# Démarrer le frontend  
echo -e "${{BLUE}}🎨 Démarrage du frontend React...${{NC}}"
cd frontend
if [ ! -d node_modules ]; then
    echo -e "${{YELLOW}}📦 Installation des dépendances frontend...${{NC}}"
    npm install
fi
npm start &
FRONTEND_PID=$!
cd ..

echo -e "${{GREEN}}✅ Services démarrés avec succès!${{NC}}"
echo -e "${{GREEN}}🌐 Frontend: http://localhost:{template_info['ports']['frontend']}${{NC}}"
echo -e "${{GREEN}}🔌 Backend API: http://localhost:{template_info['ports']['backend']}${{NC}}"
echo -e "${{GREEN}}🗄️  Database: localhost:{template_info['ports']['db']}${{NC}}"
echo ""
echo -e "${{BLUE}}Pour arrêter les services, utilisez Ctrl+C${{NC}}"

# Attendre que l'utilisateur interrompe
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose stop; exit' INT
wait
"""
        
        elif template_id == "vue-flask-postgres":
            base_script += f"""
# Démarrer la base de données
echo -e "${{BLUE}}🗄️  Démarrage de PostgreSQL...${{NC}}"
docker-compose up -d database
sleep 5

# Démarrer le backend Flask
echo -e "${{BLUE}}🔧 Démarrage du backend Flask...${{NC}}"
cd backend
if [ ! -d venv ]; then
    echo -e "${{YELLOW}}🐍 Création de l'environnement virtuel Python...${{NC}}"
    python3 -m venv venv
fi
source venv/bin/activate
if [ ! -f "requirements_installed.flag" ]; then
    echo -e "${{YELLOW}}📦 Installation des dépendances Python...${{NC}}"
    pip install -r requirements.txt
    touch requirements_installed.flag
fi
python app.py &
BACKEND_PID=$!
cd ..

# Démarrer le frontend Vue
echo -e "${{BLUE}}🎨 Démarrage du frontend Vue.js...${{NC}}"
cd frontend
if [ ! -d node_modules ]; then
    echo -e "${{YELLOW}}📦 Installation des dépendances frontend...${{NC}}"
    npm install
fi
npm run serve &
FRONTEND_PID=$!
cd ..

echo -e "${{GREEN}}✅ Services démarrés avec succès!${{NC}}"
echo -e "${{GREEN}}🌐 Frontend: http://localhost:{template_info['ports']['frontend']}${{NC}}"
echo -e "${{GREEN}}🔌 Backend API: http://localhost:{template_info['ports']['backend']}${{NC}}"
echo -e "${{GREEN}}🗄️  Database: localhost:{template_info['ports']['db']}${{NC}}"
echo ""
echo -e "${{BLUE}}Pour arrêter les services, utilisez Ctrl+C${{NC}}"

# Attendre que l'utilisateur interrompe
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose stop; exit' INT
wait
"""
        
        elif template_id == "static-site":
            base_script += f"""
# Démarrer le serveur de développement
echo -e "${{BLUE}}🌐 Démarrage du serveur de développement...${{NC}}"
cd frontend

# Utiliser live-server si disponible, sinon Python
if command -v live-server &> /dev/null; then
    echo -e "${{GREEN}}📡 Utilisation de live-server pour auto-reload${{NC}}"
    npx live-server --port={template_info['ports']['frontend']} --open=/
else
    echo -e "${{YELLOW}}📡 Utilisation du serveur Python simple${{NC}}"
    python3 -m http.server {template_info['ports']['frontend']}
fi
"""
        
        elif template_id == "api-backend":
            base_script += f"""
# Démarrer la base de données
echo -e "${{BLUE}}🗄️  Démarrage de PostgreSQL...${{NC}}"
docker-compose up -d database
sleep 5

# Démarrer l'API backend
echo -e "${{BLUE}}🔌 Démarrage de l'API backend...${{NC}}"
cd backend
if [ ! -d node_modules ]; then
    echo -e "${{YELLOW}}📦 Installation des dépendances...${{NC}}"
    npm install
fi
npm run dev &
BACKEND_PID=$!
cd ..

echo -e "${{GREEN}}✅ API démarrée avec succès!${{NC}}"
echo -e "${{GREEN}}🔌 API: http://localhost:{template_info['ports']['backend']}${{NC}}"
echo -e "${{GREEN}}🗄️  Database: localhost:{template_info['ports']['db']}${{NC}}"
echo -e "${{GREEN}}📖 API Docs: http://localhost:{template_info['ports']['backend']}/docs${{NC}}"
echo ""
echo -e "${{BLUE}}Pour arrêter les services, utilisez Ctrl+C${{NC}}"

# Attendre que l'utilisateur interrompe
trap 'kill $BACKEND_PID 2>/dev/null; docker-compose stop; exit' INT
wait
"""
        
        return base_script

    def _generate_build_script(self, template_id, project_name, template_info):
        """Génère le script build.sh selon le template"""
        return f"""#!/bin/bash
# Script de build pour {project_name}
# Template: {template_id}

set -e

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

echo -e "${{BLUE}}🔨 Build de {project_name}${{NC}}"
echo -e "${{BLUE}}=====================${{NC}}"

# Build selon le template
{self._get_build_commands(template_id)}

echo -e "${{GREEN}}✅ Build terminé avec succès!${{NC}}"
echo -e "${{BLUE}}🚀 Prêt pour le déploiement${{NC}}"
"""

    def _generate_test_script(self, template_id, project_name, template_info):
        """Génère le script test.sh selon le template"""
        return f"""#!/bin/bash
# Script de tests pour {project_name}
# Template: {template_id}

set -e

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

echo -e "${{BLUE}}🧪 Tests de {project_name}${{NC}}"
echo -e "${{BLUE}}==================${{NC}}"

# Tests selon le template
{self._get_test_commands(template_id)}

echo -e "${{GREEN}}✅ Tous les tests sont passés!${{NC}}"
"""

    def _generate_deploy_script(self, template_id, project_name, template_info):
        """Génère le script deploy.sh selon le template"""
        return f"""#!/bin/bash
# Script de déploiement pour {project_name}
# Template: {template_id}

set -e

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

ENVIRONMENT=${{1:-staging}}

echo -e "${{BLUE}}🚀 Déploiement de {project_name} ($ENVIRONMENT)${{NC}}"
echo -e "${{BLUE}}============================================${{NC}}"

# Validation de l'environnement
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${{RED}}❌ Environnement invalide. Utilisez: staging ou production${{NC}}"
    exit 1
fi

# Build avant déploiement
echo -e "${{BLUE}}🔨 Build de l'application...${{NC}}"
./scripts/build.sh

# Tests avant déploiement
echo -e "${{BLUE}}🧪 Exécution des tests...${{NC}}"
./scripts/test.sh

# Déploiement Docker
echo -e "${{BLUE}}🐳 Déploiement Docker...${{NC}}"
docker-compose down
docker-compose up -d --build

# Attendre que les services soient prêts
echo -e "${{YELLOW}}⏳ Attente de la disponibilité des services...${{NC}}"
sleep 10

# Vérification de santé
echo -e "${{BLUE}}🏥 Vérification de la santé des services...${{NC}}"
{self._get_health_checks(template_id, project_name)}

echo -e "${{GREEN}}✅ Déploiement réussi!${{NC}}"
echo -e "${{GREEN}}🌐 URL $ENVIRONMENT: https://{project_name}{"-$ENVIRONMENT" if "$ENVIRONMENT" == "staging" else ""}.colaig.fr${{NC}}"
"""

    def _get_build_commands(self, template_id):
        """Retourne les commandes de build selon le template"""
        if template_id == "react-node-postgres":
            return """
# Build frontend React
echo -e "${BLUE}🎨 Build du frontend React...${NC}"
cd frontend
npm install
npm run build
cd ..

# Build backend Node.js  
echo -e "${BLUE}🔧 Build du backend Node.js...${NC}"
cd backend
npm install
# Pas de build spécifique pour Node.js en général
cd ..

# Build des images Docker
echo -e "${BLUE}🐳 Build des images Docker...${NC}"
docker-compose build
"""
        elif template_id == "vue-flask-postgres":
            return """
# Build frontend Vue.js
echo -e "${BLUE}🎨 Build du frontend Vue.js...${NC}"
cd frontend
npm install
npm run build
cd ..

# Préparer backend Flask
echo -e "${BLUE}🐍 Préparation du backend Flask...${NC}"
cd backend
if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Build des images Docker
echo -e "${BLUE}🐳 Build des images Docker...${NC}"
docker-compose build
"""
        elif template_id == "static-site":
            return """
# Optimisation du site statique
echo -e "${BLUE}🌐 Optimisation du site statique...${NC}"
cd frontend

# Minification CSS/JS (si outils disponibles)
if command -v uglifyjs &> /dev/null; then
    echo -e "${YELLOW}📦 Minification JavaScript...${NC}"
    find . -name "*.js" -not -path "./node_modules/*" -exec uglifyjs {} -o {} \\;
fi

if command -v cleancss &> /dev/null; then
    echo -e "${YELLOW}📦 Minification CSS...${NC}"
    find . -name "*.css" -not -path "./node_modules/*" -exec cleancss {} -o {} \\;
fi

cd ..

# Build de l'image Docker
echo -e "${BLUE}🐳 Build de l'image Docker...${NC}"
docker-compose build
"""
        elif template_id == "api-backend":
            return """
# Build backend API
echo -e "${BLUE}🔌 Build du backend API...${NC}"
cd backend
npm install
# Tests de l'API
npm test
cd ..

# Build de l'image Docker
echo -e "${BLUE}🐳 Build de l'image Docker...${NC}"
docker-compose build
"""
        return ""

    def _get_test_commands(self, template_id):
        """Retourne les commandes de test selon le template"""
        if template_id in ["react-node-postgres", "vue-flask-postgres"]:
            return """
# Tests frontend
if [ -d "frontend" ]; then
    echo -e "${BLUE}🎨 Tests frontend...${NC}"
    cd frontend
    npm test -- --watchAll=false
    cd ..
fi

# Tests backend
if [ -d "backend" ]; then
    echo -e "${BLUE}🔧 Tests backend...${NC}"
    cd backend
    npm test || python -m pytest
    cd ..
fi

# Tests d'intégration avec Docker
echo -e "${BLUE}🐳 Tests d'intégration...${NC}"
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
docker-compose -f docker-compose.test.yml down
"""
        elif template_id == "static-site":
            return """
# Validation HTML
if command -v html5validator &> /dev/null; then
    echo -e "${BLUE}📝 Validation HTML...${NC}"
    html5validator --root frontend/
fi

# Tests de liens brisés
if command -v linkchecker &> /dev/null; then
    echo -e "${BLUE}🔗 Vérification des liens...${NC}"
    linkchecker frontend/index.html
fi

# Tests de performance
echo -e "${BLUE}⚡ Tests de performance basiques...${NC}"
cd frontend
python3 -m http.server 8000 &
SERVER_PID=$!
sleep 2
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s" http://localhost:8000
kill $SERVER_PID
cd ..
"""
        elif template_id == "api-backend":
            return """
# Tests API backend
echo -e "${BLUE}🔌 Tests API backend...${NC}"
cd backend
npm test
cd ..

# Tests d'intégration API
echo -e "${BLUE}🧪 Tests d'intégration API...${NC}"
docker-compose up -d database
sleep 5
cd backend
npm run test:integration || python -m pytest tests/integration/
cd ..
docker-compose stop database
"""
        return ""

    def _get_health_checks(self, template_id, project_name):
        """Retourne les vérifications de santé selon le template"""
        checks = []
        
        if template_id in ["react-node-postgres", "vue-flask-postgres"]:
            frontend_port = self.templates[template_id]['ports']['frontend']
            backend_port = self.templates[template_id]['ports']['backend']
            checks.append(f'curl -f http://localhost:{frontend_port} > /dev/null || echo -e "${{RED}}❌ Frontend non accessible${{NC}}"')
            checks.append(f'curl -f http://localhost:{backend_port}/health > /dev/null || echo -e "${{RED}}❌ Backend non accessible${{NC}}"')
        elif template_id == "static-site":
            frontend_port = self.templates[template_id]['ports']['frontend']
            checks.append(f'curl -f http://localhost:{frontend_port} > /dev/null || echo -e "${{RED}}❌ Site non accessible${{NC}}"')
        elif template_id == "api-backend":
            backend_port = self.templates[template_id]['ports']['backend']
            checks.append(f'curl -f http://localhost:{backend_port}/health > /dev/null || echo -e "${{RED}}❌ API non accessible${{NC}}"')
        
        return '\n'.join(checks) if checks else 'echo -e "${GREEN}✅ Aucune vérification spécifique${NC}"'

    def _apply_compliance_rules(self, project_path, project_name, template_id):
        """Applique les règles de conformité obligatoires"""
        logger.info("Application des règles de conformité")
        
        # Vérifier les fichiers obligatoires
        for file_name in self.compliance_rules["mandatory_files"]:
            file_path = os.path.join(project_path, file_name)
            if not os.path.exists(file_path):
                logger.warning(f"Fichier obligatoire manquant: {file_name}")

    def _setup_testing_framework(self, project_path, template_id):
        """Configure le framework de tests"""
        logger.info("Configuration du framework de tests")
        
        # Créer les fichiers de tests de base
        tests_path = os.path.join(project_path, "tests")
        
        # Test basique de santé
        test_content = f"""# Tests pour {template_id}

## Tests automatisés

Ce dossier contient tous les tests du projet :
- Tests unitaires
- Tests d'intégration
- Tests end-to-end

### Commandes
```bash
# Exécuter tous les tests
npm test

# Tests en mode watch
npm run test:watch

# Coverage
npm run test:coverage
```
"""
        with open(os.path.join(tests_path, "README.md"), "w") as f:
            f.write(test_content)

    def _generate_documentation(self, project_path, project_name, template_id, description):
        """Génère la documentation technique"""
        logger.info("Génération de la documentation")
        
        docs_path = os.path.join(project_path, "docs")
        
        # Documentation API
        api_doc = f"""# API Documentation - {project_name}

## Aperçu
{description}

## Endpoints

### Authentification
- `POST /api/auth/login` - Connexion utilisateur
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/profile` - Profil utilisateur

### Ressources principales
- `GET /api/items` - Liste des éléments
- `POST /api/items` - Créer un élément
- `GET /api/items/:id` - Récupérer un élément
- `PUT /api/items/:id` - Modifier un élément
- `DELETE /api/items/:id` - Supprimer un élément

## Schéma de base de données

### Tables principales
- `users` - Utilisateurs
- `items` - Éléments principaux

## Configuration

Voir `.env.example` pour toutes les variables de configuration.
"""
        
        with open(os.path.join(docs_path, "api.md"), "w") as f:
            f.write(api_doc)

    def _generate_project_urls(self, project_name):
        """Génère les URLs du projet"""
        return {
            "development": f"http://localhost:3000",
            "staging": f"https://{project_name}-staging.colaig.fr",
            "production": f"https://{project_name}.colaig.fr",
            "api_development": f"http://localhost:5000",
            "api_staging": f"https://{project_name}-api-staging.colaig.fr",
            "api_production": f"https://{project_name}-api.colaig.fr"
        }

    def _get_next_steps(self, template_id):
        """Retourne les prochaines étapes selon le template"""
        base_steps = [
            "Modifier le fichier .env selon vos besoins",
            "Démarrer les services : docker-compose up -d --build",
            "Tester l'application en local",
            "Personnaliser le code selon vos besoins"
        ]
        
        if template_id in ["react-node-postgres", "vue-flask-postgres"]:
            base_steps.extend([
                "Configurer la base de données",
                "Implémenter les APIs",
                "Ajouter les tests"
            ])
        
        return base_steps

    # Méthodes de génération spécifiques aux templates
    def _create_react_node_structure(self, project_path, project_name):
        """Crée la structure React + Node.js"""
        # Frontend package.json
        frontend_package = {
            "name": f"{project_name}-frontend",
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0",
                "axios": "^1.3.0",
                "@mui/material": "^5.11.0",
                "@emotion/react": "^11.10.0",
                "@emotion/styled": "^11.10.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test --watchAll=false",
                "eject": "react-scripts eject"
            },
            "devDependencies": {
                "react-scripts": "5.0.1",
                "@testing-library/react": "^13.4.0",
                "@testing-library/jest-dom": "^5.16.0"
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        with open(os.path.join(project_path, "frontend", "package.json"), "w") as f:
            json.dump(frontend_package, f, indent=2)
            
        # Frontend Dockerfile
        frontend_dockerfile = f"""FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(os.path.join(project_path, "frontend", "Dockerfile"), "w") as f:
            f.write(frontend_dockerfile)
            
        # Nginx config for frontend
        nginx_config = """events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    server {
        listen 3000;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # API proxy
        location /api {
            proxy_pass http://backend:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
"""
        
        with open(os.path.join(project_path, "frontend", "nginx.conf"), "w") as f:
            f.write(nginx_config)
            
        # Create basic React structure
        src_path = os.path.join(project_path, "frontend", "src")
        os.makedirs(src_path, exist_ok=True)
        os.makedirs(os.path.join(src_path, "components"), exist_ok=True)
        os.makedirs(os.path.join(src_path, "pages"), exist_ok=True)
        os.makedirs(os.path.join(src_path, "services"), exist_ok=True)
        
        # App.js
        app_js = f"""import React from 'react';
import {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';
import {{ ThemeProvider, createTheme }} from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Home from './pages/Home';

const theme = createTheme();

function App() {{
  return (
    <ThemeProvider theme={{theme}}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={{<Home />}} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}}

export default App;
"""
        
        with open(os.path.join(src_path, "App.js"), "w") as f:
            f.write(app_js)
            
        # Backend package.json
        backend_package = {
            "name": f"{project_name}-backend",
            "version": "1.0.0",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js",
                "test": "jest",
                "migrate": "sequelize-cli db:migrate",
                "seed": "sequelize-cli db:seed:all"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^6.0.1",
                "dotenv": "^16.0.3",
                "pg": "^8.8.0",
                "sequelize": "^6.28.0",
                "jsonwebtoken": "^9.0.0",
                "bcryptjs": "^2.4.3",
                "joi": "^17.7.0"
            },
            "devDependencies": {
                "nodemon": "^2.0.20",
                "jest": "^29.3.0",
                "supertest": "^6.3.0",
                "sequelize-cli": "^6.5.2"
            }
        }
        
        with open(os.path.join(project_path, "backend", "package.json"), "w") as f:
            json.dump(backend_package, f, indent=2)
            
        # Backend Dockerfile
        backend_dockerfile = f"""FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

USER nodejs

EXPOSE 5000

CMD ["npm", "start"]
"""
        
        with open(os.path.join(project_path, "backend", "Dockerfile"), "w") as f:
            f.write(backend_dockerfile)
            
        # Basic server.js
        server_js = f"""const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Routes
app.get('/health', (req, res) => {{
  res.json({{ status: 'OK', timestamp: new Date().toISOString() }});
}});

app.get('/api/hello', (req, res) => {{
  res.json({{ message: 'Hello from {project_name} API!' }});
}});

// Error handling
app.use((err, req, res, next) => {{
  console.error(err.stack);
  res.status(500).json({{ error: 'Something went wrong!' }});
}});

// 404 handler
app.use('*', (req, res) => {{
  res.status(404).json({{ error: 'Route not found' }});
}});

app.listen(PORT, () => {{
  console.log(`🚀 Server running on port ${{PORT}}`);
}});
"""
        
        with open(os.path.join(project_path, "backend", "server.js"), "w") as f:
            f.write(server_js)

    def _create_vue_flask_structure(self, project_path, project_name):
        """Crée la structure Vue.js + Flask"""
        # Frontend package.json pour Vue
        frontend_package = {
            "name": f"{project_name}-frontend",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "serve": "vue-cli-service serve",
                "build": "vue-cli-service build",
                "test:unit": "vue-cli-service test:unit",
                "lint": "vue-cli-service lint"
            },
            "dependencies": {
                "vue": "^3.2.45",
                "vue-router": "^4.1.6",
                "pinia": "^2.0.32",
                "axios": "^1.3.0",
                "vuetify": "^3.1.0"
            },
            "devDependencies": {
                "@vue/cli-service": "~5.0.0",
                "@vue/test-utils": "^2.3.0",
                "jest": "^29.0.0"
            }
        }
        
        with open(os.path.join(project_path, "frontend", "package.json"), "w") as f:
            json.dump(frontend_package, f, indent=2)
            
        # Frontend Dockerfile
        frontend_dockerfile = f"""FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(os.path.join(project_path, "frontend", "Dockerfile"), "w") as f:
            f.write(frontend_dockerfile)
            
        # Create Vue app structure
        src_path = os.path.join(project_path, "frontend", "src")
        os.makedirs(src_path, exist_ok=True)
        os.makedirs(os.path.join(src_path, "components"), exist_ok=True)
        os.makedirs(os.path.join(src_path, "views"), exist_ok=True)
        os.makedirs(os.path.join(src_path, "stores"), exist_ok=True)
        os.makedirs(os.path.join(src_path, "services"), exist_ok=True)
        
        # main.js
        main_js = f"""import {{ createApp }} from 'vue'
import {{ createPinia }} from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
"""
        
        with open(os.path.join(src_path, "main.js"), "w") as f:
            f.write(main_js)
            
        # Backend requirements.txt
        requirements = f"""Flask==2.2.3
Flask-CORS==3.0.10
Flask-JWT-Extended==4.4.4
Flask-SQLAlchemy==3.0.3
Flask-Migrate==4.0.4
psycopg2-binary==2.9.5
python-dotenv==1.0.0
marshmallow==3.19.0
gunicorn==20.1.0
"""
        
        with open(os.path.join(project_path, "backend", "requirements.txt"), "w") as f:
            f.write(requirements)
            
        # Backend Dockerfile
        backend_dockerfile = f"""FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
"""
        
        with open(os.path.join(project_path, "backend", "Dockerfile"), "w") as f:
            f.write(backend_dockerfile)
            
        # Flask app.py
        app_py = f"""from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/{project_name}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# Health check route
@app.route('/health')
def health():
    return jsonify({{'status': 'OK', 'timestamp': '{{}}'}})

@app.route('/api/hello')
def hello():
    return jsonify({{'message': 'Hello from {project_name} API!'}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
        
        with open(os.path.join(project_path, "backend", "app.py"), "w") as f:
            f.write(app_py)

    def _create_static_site_structure(self, project_path, project_name):
        """Crée la structure site statique"""
        # Create full structure
        css_path = os.path.join(project_path, "frontend", "css")
        js_path = os.path.join(project_path, "frontend", "js")
        images_path = os.path.join(project_path, "frontend", "images")
        os.makedirs(css_path, exist_ok=True)
        os.makedirs(js_path, exist_ok=True)
        os.makedirs(images_path, exist_ok=True)
        
        # Index HTML
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{project_name} - Site web moderne">
    <meta name="keywords" content="{project_name}, web, site">
    <title>{project_name}</title>
    <link rel="stylesheet" href="css/main.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="container">
                <div class="nav-brand">
                    <h1>{project_name}</h1>
                </div>
                <ul class="nav-menu">
                    <li><a href="#home">Accueil</a></li>
                    <li><a href="#about">À propos</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main>
        <section id="home" class="hero">
            <div class="container">
                <h2>Bienvenue sur {project_name}</h2>
                <p>Site créé avec Claude Code Web</p>
                <button class="btn btn-primary">En savoir plus</button>
            </div>
        </section>

        <section id="about" class="about">
            <div class="container">
                <h2>À propos</h2>
                <p>Votre contenu ici...</p>
            </div>
        </section>

        <section id="contact" class="contact">
            <div class="container">
                <h2>Contact</h2>
                <form class="contact-form">
                    <input type="text" placeholder="Nom" required>
                    <input type="email" placeholder="Email" required>
                    <textarea placeholder="Message" required></textarea>
                    <button type="submit" class="btn btn-primary">Envoyer</button>
                </form>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {project_name}. Tous droits réservés.</p>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
        
        with open(os.path.join(project_path, "frontend", "index.html"), "w") as f:
            f.write(html_content)
            
        # CSS principal
        css_content = f"""/* Reset et base */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    color: #333;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
.header {{
    background: #fff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
}}

.nav {{
    padding: 1rem 0;
}}

.nav .container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.nav-brand h1 {{
    color: #2563eb;
    font-size: 1.5rem;
    font-weight: 600;
}}

.nav-menu {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-menu a {{
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: color 0.3s;
}}

.nav-menu a:hover {{
    color: #2563eb;
}}

/* Sections */
section {{
    padding: 80px 0;
}}

.hero {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    margin-top: 70px;
}}

.hero h2 {{
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: 600;
}}

.hero p {{
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

/* Boutons */
.btn {{
    display: inline-block;
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s;
}}

.btn-primary {{
    background: #2563eb;
    color: white;
}}

.btn-primary:hover {{
    background: #1d4ed8;
    transform: translateY(-2px);
}}

/* About */
.about {{
    background: #f8fafc;
}}

.about h2 {{
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2.5rem;
    color: #1e293b;
}}

/* Contact */
.contact h2 {{
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2.5rem;
    color: #1e293b;
}}

.contact-form {{
    max-width: 600px;
    margin: 0 auto;
    display: grid;
    gap: 1rem;
}}

.contact-form input,
.contact-form textarea {{
    padding: 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-family: inherit;
}}

.contact-form textarea {{
    min-height: 120px;
    resize: vertical;
}}

/* Footer */
.footer {{
    background: #1e293b;
    color: white;
    text-align: center;
    padding: 2rem 0;
}}

/* Responsive */
@media (max-width: 768px) {{
    .nav .container {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .nav-menu {{
        gap: 1rem;
    }}
    
    .hero h2 {{
        font-size: 2rem;
    }}
    
    section {{
        padding: 60px 0;
    }}
}}
"""
        
        with open(os.path.join(css_path, "main.css"), "w") as f:
            f.write(css_content)
            
        # JavaScript principal
        js_content = f"""// {project_name} - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {{
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');
    
    navLinks.forEach(link => {{
        link.addEventListener('click', function(e) {{
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {{
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight;
                
                window.scrollTo({{
                    top: targetPosition,
                    behavior: 'smooth'
                }});
            }}
        }});
    }});
    
    // Contact form handling
    const contactForm = document.querySelector('.contact-form');
    
    if (contactForm) {{
        contactForm.addEventListener('submit', function(e) {{
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const name = this.querySelector('input[type="text"]').value;
            const email = this.querySelector('input[type="email"]').value;
            const message = this.querySelector('textarea').value;
            
            // Simple validation
            if (!name || !email || !message) {{
                alert('Veuillez remplir tous les champs');
                return;
            }}
            
            // Simulate form submission
            alert('Merci pour votre message ! Nous vous répondrons bientôt.');
            this.reset();
        }});
    }}
    
    // Add scroll effect to header
    window.addEventListener('scroll', function() {{
        const header = document.querySelector('.header');
        
        if (window.scrollY > 100) {{
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.backdropFilter = 'blur(10px)';
        }} else {{
            header.style.background = '#fff';
            header.style.backdropFilter = 'none';
        }}
    }});
}});
"""
        
        with open(os.path.join(js_path, "main.js"), "w") as f:
            f.write(js_content)
            
        # Dockerfile for static site
        dockerfile_content = f"""FROM nginx:alpine

# Copy static files
COPY . /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(os.path.join(project_path, "frontend", "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
            
        # Nginx config
        nginx_config = """events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # Cache static assets
        location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
"""
        
        with open(os.path.join(project_path, "frontend", "nginx.conf"), "w") as f:
            f.write(nginx_config)

    def _create_api_backend_structure(self, project_path, project_name):
        """Crée la structure API backend"""
        # Create detailed backend structure
        src_path = os.path.join(project_path, "backend", "src")
        controllers_path = os.path.join(src_path, "controllers")
        models_path = os.path.join(src_path, "models")
        routes_path = os.path.join(src_path, "routes")
        middleware_path = os.path.join(src_path, "middleware")
        utils_path = os.path.join(src_path, "utils")
        
        for path in [src_path, controllers_path, models_path, routes_path, middleware_path, utils_path]:
            os.makedirs(path, exist_ok=True)
            
        # Package.json pour l'API
        backend_package = {
            "name": f"{project_name}-api",
            "version": "1.0.0",
            "description": f"API Backend for {project_name}",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js",
                "test": "jest --detectOpenHandles",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage",
                "migrate": "sequelize-cli db:migrate",
                "migrate:undo": "sequelize-cli db:migrate:undo",
                "seed": "sequelize-cli db:seed:all",
                "docs:generate": "swagger-jsdoc -d swaggerDef.js ./src/routes/*.js -o ./docs/swagger.yaml"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^6.0.1",
                "express-rate-limit": "^6.7.0",
                "dotenv": "^16.0.3",
                "joi": "^17.7.0",
                "jsonwebtoken": "^9.0.0",
                "bcryptjs": "^2.4.3",
                "pg": "^8.8.0",
                "sequelize": "^6.28.0",
                "swagger-jsdoc": "^6.2.8",
                "swagger-ui-express": "^4.6.0",
                "winston": "^3.8.2",
                "morgan": "^1.10.0"
            },
            "devDependencies": {
                "nodemon": "^2.0.20",
                "jest": "^29.3.0",
                "supertest": "^6.3.0",
                "sequelize-cli": "^6.5.2",
                "@types/jest": "^29.2.0"
            }
        }
        
        with open(os.path.join(project_path, "backend", "package.json"), "w") as f:
            json.dump(backend_package, f, indent=2)
            
        # Dockerfile
        dockerfile_content = f"""FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app
USER nodejs

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["npm", "start"]
"""
        
        with open(os.path.join(project_path, "backend", "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
            
        # Main server.js
        server_js = f"""const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');
const winston = require('winston');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Configure logger
const logger = winston.createLogger({{
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({{ stack: true }}),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({{ filename: 'logs/error.log', level: 'error' }}),
    new winston.transports.File({{ filename: 'logs/combined.log' }}),
    new winston.transports.Console({{
      format: winston.format.simple()
    }})
  ]
}});

// Rate limiting
const limiter = rateLimit({{
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
}});

// Middleware
app.use(helmet());
app.use(cors());
app.use(limiter);
app.use(morgan('combined'));
app.use(express.json({{ limit: '10mb' }}));
app.use(express.urlencoded({{ extended: true }}));

// Swagger Documentation
try {{
  const swaggerDocument = YAML.load('./docs/swagger.yaml');
  app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
}} catch (error) {{
  logger.warn('Swagger documentation not available');
}}

// Routes
app.get('/health', (req, res) => {{
  res.json({{
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  }});
}});

// API Routes
app.use('/api/v1', require('./src/routes'));

// Error handling middleware
app.use((err, req, res, next) => {{
  logger.error(err.stack);
  
  const status = err.status || 500;
  const message = process.env.NODE_ENV === 'production' 
    ? 'Internal Server Error' 
    : err.message;
    
  res.status(status).json({{
    error: {{
      message,
      status,
      timestamp: new Date().toISOString()
    }}
  }});
}});

// 404 handler
app.use('*', (req, res) => {{
  res.status(404).json({{
    error: {{
      message: 'Route not found',
      status: 404,
      path: req.originalUrl
    }}
  }});
}});

// Graceful shutdown
process.on('SIGTERM', () => {{
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
}});

app.listen(PORT, () => {{
  logger.info(`🚀 {project_name} API Server running on port ${{PORT}}`);
}});

module.exports = app;
"""
        
        with open(os.path.join(project_path, "backend", "server.js"), "w") as f:
            f.write(server_js)
            
        # Routes index
        routes_index = f"""const express = require('express');
const router = express.Router();

// Import route modules
const authRoutes = require('./auth');
const userRoutes = require('./users');

// Health check for API
router.get('/', (req, res) => {{
  res.json({{
    message: 'Welcome to {project_name} API',
    version: '1.0.0',
    endpoints: [
      'GET /health - Health check',
      'GET /docs - API Documentation',
      'POST /api/v1/auth/login - User login',
      'GET /api/v1/users - Get users'
    ]
  }});
}});

// Route modules
router.use('/auth', authRoutes);
router.use('/users', userRoutes);

module.exports = router;
"""
        
        with open(os.path.join(routes_path, "index.js"), "w") as f:
            f.write(routes_index)
            
        # Auth routes
        auth_routes = f"""const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const {{ validateLogin }} = require('../middleware/validation');

/**
 * @swagger
 * /api/v1/auth/login:
 *   post:
 *     summary: User login
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - password
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *               password:
 *                 type: string
 *                 minLength: 6
 *     responses:
 *       200:
 *         description: Login successful
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 token:
 *                   type: string
 *                 user:
 *                   type: object
 */
router.post('/login', validateLogin, authController.login);

/**
 * @swagger
 * /api/v1/auth/register:
 *   post:
 *     summary: User registration
 *     tags: [Authentication]
 */
router.post('/register', authController.register);

module.exports = router;
"""
        
        with open(os.path.join(routes_path, "auth.js"), "w") as f:
            f.write(auth_routes)
            
        # Users routes
        users_routes = f"""const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const {{ authenticateToken }} = require('../middleware/auth');

/**
 * @swagger
 * /api/v1/users:
 *   get:
 *     summary: Get all users
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of users
 */
router.get('/', authenticateToken, userController.getAllUsers);

/**
 * @swagger
 * /api/v1/users/{{id}}:
 *   get:
 *     summary: Get user by ID
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 */
router.get('/:id', authenticateToken, userController.getUserById);

module.exports = router;
"""
        
        with open(os.path.join(routes_path, "users.js"), "w") as f:
            f.write(users_routes)
            
        # Controllers
        auth_controller = f"""const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const {{ User }} = require('../models');
const {{ validationResult }} = require('express-validator');

class AuthController {{
  async login(req, res) {{
    try {{
      const errors = validationResult(req);
      if (!errors.isEmpty()) {{
        return res.status(400).json({{ errors: errors.array() }});
      }}

      const {{ email, password }} = req.body;
      
      // Find user
      const user = await User.findOne({{ where: {{ email }} }});
      if (!user) {{
        return res.status(401).json({{ error: 'Invalid credentials' }});
      }}

      // Check password
      const validPassword = await bcrypt.compare(password, user.password);
      if (!validPassword) {{
        return res.status(401).json({{ error: 'Invalid credentials' }});
      }}

      // Generate token
      const token = jwt.sign(
        {{ userId: user.id, email: user.email }},
        process.env.JWT_SECRET,
        {{ expiresIn: '24h' }}
      );

      res.json({{
        token,
        user: {{
          id: user.id,
          email: user.email,
          name: user.name
        }}
      }});

    }} catch (error) {{
      console.error('Login error:', error);
      res.status(500).json({{ error: 'Internal server error' }});
    }}
  }}

  async register(req, res) {{
    try {{
      const {{ name, email, password }} = req.body;

      // Check if user exists
      const existingUser = await User.findOne({{ where: {{ email }} }});
      if (existingUser) {{
        return res.status(400).json({{ error: 'User already exists' }});
      }}

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 10);

      // Create user
      const user = await User.create({{
        name,
        email,
        password: hashedPassword
      }});

      res.status(201).json({{
        message: 'User created successfully',
        user: {{
          id: user.id,
          name: user.name,
          email: user.email
        }}
      }});

    }} catch (error) {{
      console.error('Registration error:', error);
      res.status(500).json({{ error: 'Internal server error' }});
    }}
  }}
}}

module.exports = new AuthController();
"""
        
        with open(os.path.join(controllers_path, "authController.js"), "w") as f:
            f.write(auth_controller)

    def _get_react_node_architecture(self, project_name, template_info):
        """Architecture spécifique React + Node.js + PostgreSQL"""
        return f"""### Full-Stack React Application

**Frontend (React + Vite)**
- Modern React 18 with functional components and hooks
- Vite for fast development and building  
- Client-side routing with React Router
- State management with Context API or Redux Toolkit
- Material-UI or Tailwind CSS for styling

**Backend (Node.js + Express)**
- RESTful API with Express.js
- JWT authentication and authorization
- PostgreSQL database with Prisma ORM
- Input validation with Joi or Yup
- Error handling and logging middleware

**Database (PostgreSQL)**
- Relational database with migrations
- Connection pooling
- Backup and recovery strategies

### File Structure
```
{project_name}/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level components  
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API calls and business logic
│   │   ├── store/          # State management
│   │   └── utils/          # Helper functions
│   ├── public/             # Static assets
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── controllers/    # Request handlers
│   │   ├── models/         # Database models
│   │   ├── routes/         # API routes
│   │   ├── middleware/     # Express middleware
│   │   └── utils/          # Helper functions
│   └── package.json
└── database/
    ├── migrations/         # Database schema changes
    ├── seeds/              # Sample data
    └── init/               # Initialization scripts
```"""

    def _get_vue_flask_architecture(self, project_name, template_info):
        """Architecture spécifique Vue.js + Flask + PostgreSQL"""
        return f"""### Vue.js + Python Flask Application

**Frontend (Vue.js 3)**
- Vue 3 Composition API with TypeScript support
- Vue Router for client-side routing
- Pinia for state management
- Vuetify or Quasar for UI components
- Vite for development and building

**Backend (Flask + SQLAlchemy)**
- Flask web framework with Blueprints
- SQLAlchemy ORM for database operations
- Flask-JWT-Extended for authentication
- Flask-CORS for cross-origin requests
- Flask-Migrate for database migrations

**Database (PostgreSQL)**
- PostgreSQL with SQLAlchemy models
- Database migrations with Flask-Migrate
- Connection pooling and optimization

### File Structure
```
{project_name}/
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page-level components
│   │   ├── composables/    # Vue 3 composables
│   │   ├── services/       # API communication
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router config
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # Flask blueprints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   ├── migrations/         # Database migrations
│   └── requirements.txt
└── database/
    ├── seeds/              # Sample data
    └── init/               # Initialization scripts
```"""

    def _get_static_site_architecture(self, project_name, template_info):
        """Architecture spécifique Site Statique"""
        return f"""### Static Website with Modern Tooling

**Frontend (HTML + CSS + JavaScript)**
- Semantic HTML5 structure
- Modern CSS with Flexbox/Grid
- Vanilla JavaScript or lightweight framework
- Responsive design principles
- SEO optimization

**Build System**
- Nginx for serving static files
- Asset optimization and compression
- Progressive Web App capabilities
- Performance optimization

### File Structure
```
{project_name}/
├── frontend/
│   ├── index.html          # Main entry point
│   ├── css/
│   │   ├── main.css        # Main stylesheet
│   │   └── components/     # Component styles
│   ├── js/
│   │   ├── main.js         # Main JavaScript
│   │   └── modules/        # JS modules
│   ├── images/             # Image assets
│   └── assets/             # Other static assets
└── docs/
    └── seo/                # SEO documentation
```"""

    def _get_api_backend_architecture(self, project_name, template_info):
        """Architecture spécifique API Backend"""
        return f"""### RESTful API Backend Service

**Backend (Node.js + Express)**
- RESTful API with Express.js
- OpenAPI/Swagger documentation
- JWT authentication and authorization  
- Rate limiting and security middleware
- Request validation and error handling

**Database (PostgreSQL)**
- PostgreSQL with connection pooling
- Database migrations and seeding
- Query optimization
- Backup strategies

**API Design**
- RESTful endpoints following conventions
- Consistent error responses
- Pagination and filtering
- API versioning strategy

### File Structure
```
{project_name}/
├── backend/
│   ├── src/
│   │   ├── controllers/    # API controllers
│   │   ├── models/         # Database models
│   │   ├── routes/         # API routes
│   │   ├── middleware/     # Express middleware
│   │   ├── services/       # Business logic
│   │   ├── validators/     # Input validation
│   │   └── utils/          # Helper functions
│   ├── docs/
│   │   └── swagger.yaml    # API documentation
│   └── package.json
├── database/
│   ├── migrations/         # Schema migrations
│   ├── seeds/              # Sample data
│   └── init/               # DB initialization
└── tests/
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── e2e/                # End-to-end tests
```"""

    def _get_template_specific_guidance(self, template_id, project_name, template_info):
        """Guidance spécifique selon le template"""
        if template_id == "react-node-postgres":
            return f"""

## React + Node.js Specific Guidance

### Frontend Development
```bash
# Start React development server
cd frontend && npm start

# Build for production
cd frontend && npm run build

# Run frontend tests
cd frontend && npm test
```

### Backend Development  
```bash
# Start Node.js API server
cd backend && npm run dev

# Run database migrations
cd backend && npm run migrate

# Seed database with sample data
cd backend && npm run seed
```

### Common Patterns
- Use React hooks for component logic
- Implement proper error boundaries
- Use React Query for API state management
- Follow REST API conventions in backend
- Implement proper authentication flows

### Database Operations
```bash
# Create new migration
cd backend && npm run migration:create add_users_table

# Run migrations
cd backend && npm run migrate

# Rollback last migration  
cd backend && npm run migrate:rollback
```"""

        elif template_id == "vue-flask-postgres":
            return f"""

## Vue.js + Flask Specific Guidance

### Frontend Development
```bash
# Start Vue development server
cd frontend && npm run serve

# Build for production
cd frontend && npm run build

# Run frontend tests
cd frontend && npm run test:unit
```

### Backend Development
```bash
# Start Flask development server
cd backend && python app.py

# Run database migrations
cd backend && flask db upgrade

# Create new migration
cd backend && flask db migrate -m "description"
```

### Common Patterns
- Use Vue 3 Composition API for better code organization
- Implement Pinia stores for state management
- Use Flask Blueprints for API organization
- Implement proper CORS configuration
- Use SQLAlchemy relationships effectively

### Database Operations
```bash
# Initialize database
cd backend && flask db init

# Create migration
cd backend && flask db migrate -m "Add user table"

# Apply migrations
cd backend && flask db upgrade
```"""

        elif template_id == "static-site":
            return f"""

## Static Site Specific Guidance

### Development
```bash
# Serve locally for development
cd frontend && python -m http.server 8000

# Or use live-server for auto-reload
npx live-server frontend/
```

### Build Process
```bash
# Optimize images
cd frontend && npm run optimize:images

# Minify CSS and JS
cd frontend && npm run build

# Deploy to production
./scripts/deploy.sh production
```

### Performance Optimization
- Optimize images and use modern formats (WebP, AVIF)
- Implement lazy loading for images
- Minify CSS and JavaScript
- Use CDN for assets
- Implement proper caching headers

### SEO Best Practices
- Use semantic HTML structure
- Implement proper meta tags
- Add structured data markup
- Optimize for Core Web Vitals
- Create XML sitemap"""

        elif template_id == "api-backend":
            return f"""

## API Backend Specific Guidance

### API Development
```bash
# Start API server in development
cd backend && npm run dev

# Generate API documentation
cd backend && npm run docs:generate

# Run API tests
cd backend && npm test
```

### Database Operations
```bash
# Run migrations
cd backend && npm run migrate

# Seed database
cd backend && npm run seed

# Create new migration
cd backend && npm run migration:create
```

### API Best Practices
- Follow RESTful conventions
- Implement proper HTTP status codes
- Use consistent error response format
- Implement rate limiting
- Add request/response logging
- Use API versioning

### Security
- Implement JWT authentication
- Use HTTPS in production
- Validate all inputs
- Implement rate limiting
- Add CORS configuration
- Use security headers

### Testing Strategy
```bash
# Unit tests
npm run test:unit

# Integration tests  
npm run test:integration

# End-to-end tests
npm run test:e2e

# Test coverage
npm run test:coverage
```"""

        return ""


# Instance globale de l'agent meta
meta_agent = MetaAgent()