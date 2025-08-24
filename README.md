# Claude Code Web

![Claude Code Web Logo](placeholder-for-logo.png)

## 🌟 Vue d'ensemble

Claude Code Web est une interface web conçue pour les abonnés de Claude Pro/Team d'Anthropic, permettant d'exploiter pleinement les capacités de codage avancées de Claude dans un environnement de développement web intégré. Cette solution vous permet de coder depuis n'importe où, de prototyper rapidement vos idées, et de les déployer pour tests, le tout via une interface intuitive orientée projet.

## 🚀 Pourquoi Claude Code Web?

Les abonnés Claude Pro/Team ont accès au meilleur assistant de codage IA actuel, mais interagir avec lui dans un terminal ou via des interfaces textuelles traditionnelles limite son potentiel pour le développement. Claude Code Web offre:

- **Développement web de pointe**: Accédez à Claude depuis n'importe où pour transformer vos idées en code
- **Flux de travail orienté projet**: Organisez votre travail par projet pour un développement structuré
- **Environnement de codage intégré**: Sessions tmux persistantes accessibles via votre navigateur
- **Prototypage ultra-rapide**: Passez de l'idée au code fonctionnel en un temps record
- **Déploiement simplifié**: Testez vos créations immédiatement dans un environnement conteneurisé

![Interface projet de Claude Code Web](placeholder-for-project-view.png)

## 💻 Comment ça transforme votre workflow

1. **Idéation et prototypage rapide**: 
   - Décrivez votre idée à Claude dans l'interface web
   - Obtenez un code fonctionnel instantanément
   - Itérez et raffinez avec l'aide de Claude

2. **Développement de n'importe où**: 
   - Travaillez sur vos projets depuis n'importe quel appareil avec un navigateur
   - Continuez exactement où vous vous êtes arrêté grâce aux sessions persistantes
   - Codez dans le train, en déplacement ou depuis votre tablette

3. **Test et déploiement immédiat**:
   - Exécutez votre code directement dans l'environnement intégré
   - Déployez des versions de test pour validation
   - Exportez votre travail vers des environnements de production

![Workflow de développement mobile](placeholder-for-mobile-workflow.png)

## 🛠️ Fonctionnalités principales

- **Interface projet intuitive**: Organisation claire de vos différentes idées et projets
- **Terminal web intégré**: Accès complet à un environnement de développement Linux
- **Sessions persistantes**: Reprenez votre travail exactement où vous l'avez laissé
- **Intégration Claude Pro/Team**: Exploitez toute la puissance de votre abonnement Claude
- **Multi-langages**: Support pour tous les langages de programmation populaires
- **Responsive design**: Travaillez depuis votre ordinateur, tablette ou même smartphone

## 🖥️ Architecture technique

```
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│   Vue.js Frontend   │◄────►│   Flask Backend     │◄────►│ Abonnement Claude   │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
          │                           │                            │
          │                           │                            │
          ▼                           ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Interface Projet   │      │  Sessions Tmux      │      │  Modèles Claude Pro │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
```

## 📂 Organisation du VPS

Le système est conçu pour fonctionner sur un VPS (Serveur Privé Virtuel) avec une structure de dossiers optimisée pour la gestion de multiples projets. Cette structure n'est pas incluse dans le dépôt GitHub pour faciliter l'adaptation à différents environnements.

### Structure des dossiers

```
/root/docker/
├── claude-code-web/        # Application principale (dans ce dépôt)
├── reverse-proxy/          # Configuration Traefik (non inclus)
│   ├── docker-compose.yml
│   └── config/
├── apps/                   # Projets et applications (non inclus)
│   ├── app1/
│   │   ├── docker-compose.yml
│   │   └── ...
│   ├── app2/
│   │   └── ...
│   └── templates/          # Templates pour nouveaux projets
└── scripts/                # Scripts utilitaires (non inclus)
    ├── backup/
    ├── deployment/
    └── monitoring/
```

### Système de projets

Chaque projet développé avec Claude Code Web est généralement:
1. **Développé** dans l'environnement Claude Code Web
2. **Stocké** dans un sous-dossier de `/root/docker/apps/`
3. **Déployé** via Docker Compose avec une configuration spécifique
4. **Exposé** via Traefik (le reverse proxy) sur un sous-domaine

### Script de création d'application

Le fichier `add-app.sh` (non inclus dans ce dépôt) permet de créer rapidement un nouveau projet à partir d'un template:

```bash
./add-app.sh nom_app template_type [options]
```

Par exemple:
```bash
./add-app.sh mon-blog nodejs
```

Cela va:
1. Créer `/root/docker/apps/mon-blog/`
2. Copier le template NodeJS
3. Configurer Docker Compose
4. Ajouter les règles Traefik nécessaires

### Templates disponibles

Les templates (stockés dans `/root/docker/apps/templates/`) comprennent:
- **nodejs**: Application Node.js/Express
- **python**: Application Flask/FastAPI
- **vue**: Frontend Vue.js avec API
- **wordpress**: Site WordPress
- **static**: Site statique simple
- et plus encore...

### Intégration avec Claude Code Web

Claude Code Web détecte automatiquement les projets dans le dossier `apps/` et permet:
1. D'y accéder directement via l'interface de projets
2. De créer de nouveaux projets à partir des templates
3. De déployer/redémarrer les applications

## 💡 Cas d'usage idéaux

1. **Développeurs nomades**:
   - Codez pendant vos déplacements sans avoir à configurer d'environnement local
   - Accédez à un environnement de développement complet depuis n'importe quel appareil

2. **Prototypage d'idées**:
   - Transformez rapidement vos concepts en applications fonctionnelles
   - Validez vos idées avec un code opérationnel en minutes plutôt qu'en heures

3. **Projets secondaires (side projects)**:
   - Développez vos projets personnels sans configuration complexe
   - Avancez efficacement sur vos idées avec l'aide de Claude

4. **Formations et démonstrations**:
   - Créez des exemples de code en direct lors de présentations
   - Enseignez la programmation avec un assistant IA intégré

## 🚀 Installation

### Prérequis

- Docker et Docker Compose
- Un abonnement Claude Pro/Team d'Anthropic
- Un serveur Linux (VPS recommandé)
- Un domaine configuré

### Installation rapide

1. Clonez ce dépôt:
   ```bash
   git clone https://github.com/nic01asFr/claude-code-web.git
   cd claude-code-web
   ```

2. Configurez votre environnement:
   ```bash
   cp env.example .env
   # Éditez .env avec vos identifiants Claude et vos paramètres
   cp claude-code-web/docker-compose.example.yml claude-code-web/docker-compose.yml
   # Ajustez la configuration selon vos besoins
   ```

3. Créez la structure de dossiers recommandée:
   ```bash
   mkdir -p /root/docker/apps/templates
   mkdir -p /root/docker/scripts/{backup,deployment,monitoring}
   ```

4. Démarrez l'application:
   ```bash
   cd claude-code-web
   docker-compose up -d
   ```

5. Accédez à votre instance Claude Code Web:
   ```
   https://votre-domaine.com
   ```

### Configuration complète du VPS

Pour une configuration complète avec le système de gestion de projets:

1. Configurez Traefik (reverse proxy):
   ```bash
   # Créez le réseau Docker
   docker network create proxy

   # Créez les fichiers de configuration Traefik (voir documentation)
   mkdir -p /root/docker/reverse-proxy/config
   
   # Démarrez Traefik
   cd /root/docker/reverse-proxy
   docker-compose up -d
   ```

2. Installez des templates de projet:
   ```bash
   # Clonez le dépôt de templates (non inclus dans ce dépôt principal)
   git clone https://github.com/votre-user/claude-templates.git /tmp/templates
   cp -r /tmp/templates/* /root/docker/apps/templates/
   ```

3. Configurez les scripts utilitaires:
   ```bash
   # Rendez le script de création d'app exécutable
   chmod +x /root/docker/add-app.sh
   ```

## 📊 Avantages par rapport aux alternatives

| Fonctionnalité | Claude Code Web | IDE traditionnels | Autres assistants IA |
|----------------|----------------|-------------------|----------------------|
| Mobilité       | ✅ Partout     | ❌ Installation locale | ⚠️ Variable         |
| Puissance IA   | ✅ Claude Pro  | ❌ Limitée        | ⚠️ Moins performant  |
| Orientation projet | ✅ Intégrée | ⚠️ Complexe      | ❌ Inexistante       |
| Déploiement    | ✅ Immédiat    | ❌ Configuration nécessaire | ❌ Non supporté |
| Sessions persistantes | ✅ Automatique | ⚠️ Avec configuration | ❌ Non supporté |

## 🔒 Sécurité

- Authentification sécurisée pour protéger votre compte Claude Pro
- Toutes les communications chiffrées via HTTPS
- Isolation des projets et des sessions
- Configuration soigneuse des droits d'accès

## 🚀 Démarrage rapide

Une fois installé:

1. Connectez-vous avec vos identifiants
2. Créez un nouveau projet
3. Commencez à interagir avec Claude dans le terminal web
4. Développez, testez et déployez vos idées

## 📜 Licence

Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**Claude Code Web** - Développé pour les abonnés Claude Pro/Team - Par Nicolas Laval - [GitHub](https://github.com/nic01asFr)