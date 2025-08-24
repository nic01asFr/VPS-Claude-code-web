# Claude Code Web

## 🌟 Vue d'ensemble

Claude Code Web est une interface web conçue pour les abonnés de Claude Pro/Team d'Anthropic, permettant d'exploiter pleinement les capacités de codage avancées de Claude dans un environnement de développement web intégré. Cette solution vous permet de coder depuis n'importe où, de prototyper rapidement vos idées, et de les déployer pour tests, le tout via une interface intuitive orientée projet.

## 🚀 Pourquoi Claude Code Web?

Les abonnés Claude Pro/Team ont accès au meilleur assistant de codage IA actuel, mais interagir avec lui dans un terminal ou via des interfaces textuelles traditionnelles limite son potentiel pour le développement. Claude Code Web offre:

* **Développement web de pointe**: Accédez à Claude depuis n'importe où pour transformer vos idées en code

* **Flux de travail orienté projet**: Organisez votre travail par projet pour un développement structuré

* **Environnement de codage intégré**: Sessions tmux persistantes accessibles via votre navigateur

* **Prototypage ultra-rapide**: Passez de l'idée au code fonctionnel en un temps record

* **Déploiement simplifié**: Testez vos créations immédiatement dans un environnement conteneurisé

![Capture d’écran 2025-08-22 012756.png](https://docs.numerique.gouv.fr/media/e66a8191-4329-44c6-b306-e12d8a02c7c5/attachments/5729e75d-339d-4065-ab0d-4cf0cd818e3f.png)

## 💻 Comment ça transforme votre workflow

1. **Idéation et prototypage rapide**:

   * Décrivez votre idée à Claude dans l'interface web

   * Obtenez un code fonctionnel instantanément

   * Itérez et raffinez avec l'aide de Claude

2. **Développement de n'importe où**:

   * Travaillez sur vos projets depuis n'importe quel appareil avec un navigateur

   * Continuez exactement où vous vous êtes arrêté grâce aux sessions persistantes

   * Codez dans le train, en déplacement ou depuis votre tablette

3. **Test et déploiement immédiat**:

   * Exécutez votre code directement dans l'environnement intégré

   * Déployez des versions de test pour validation

   * Exportez votre travail vers des environnements de production

![Capture d’écran 2025-08-22 012912.png](https://docs.numerique.gouv.fr/media/e66a8191-4329-44c6-b306-e12d8a02c7c5/attachments/ddc540b9-7b78-40f3-826c-1e33578ba0a1.png)

## 🛠️ Fonctionnalités principales

* **Interface projet intuitive**: Organisation claire de vos différentes idées et projets

* **Terminal web intégré**: Accès complet à un environnement de développement Linux

* **Sessions persistantes**: Reprenez votre travail exactement où vous l'avez laissé

* **Intégration Claude Pro/Team**: Exploitez toute la puissance de votre abonnement Claude

* **Multi-langages**: Support pour tous les langages de programmation populaires

* **Responsive design**: Travaillez depuis votre ordinateur, tablette ou même smartphone

## 🖥️ Architecture technique

```javascript
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

```javascript
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

```shellscript
./add-app.sh nom_app template_type [options]
```

Par exemple:

```shellscript
./add-app.sh mon-blog nodejs
```

Cela va:

1. Créer `/root/docker/apps/mon-blog/`

2. Copier le template NodeJS

3. Configurer Docker Compose

4. Ajouter les règles Traefik nécessaires

### Templates disponibles

Les templates (stockés dans `/root/docker/apps/templates/`) comprennent:

* **nodejs**: Application Node.js/Express

* **python**: Application Flask/FastAPI

* **vue**: Frontend Vue.js avec API

* **wordpress**: Site WordPress

* **static**: Site statique simple

* et plus encore...

### Intégration avec Claude Code Web

Claude Code Web détecte automatiquement les projets dans le dossier `apps/` et permet:

1. D'y accéder directement via l'interface de projets

2. De créer de nouveaux projets à partir des templates

3. De déployer/redémarrer les applications

## 💡 Cas d'usage idéaux

1. **Développeurs nomades**:

   * Codez pendant vos déplacements sans avoir à configurer d'environnement local

   * Accédez à un environnement de développement complet depuis n'importe quel appareil

2. **Prototypage d'idées**:

   * Transformez rapidement vos concepts en applications fonctionnelles

   * Validez vos idées avec un code opérationnel en minutes plutôt qu'en heures

3. **Projets secondaires (side projects)**:

   * Développez vos projets personnels sans configuration complexe

   * Avancez efficacement sur vos idées avec l'aide de Claude

4. **Formations et démonstrations**:

   * Créez des exemples de code en direct lors de présentations

   * Enseignez la programmation avec un assistant IA intégré

## 🚀 Installation

### Prérequis

* Docker et Docker Compose

* Un abonnement Claude Pro/Team d'Anthropic

* Un serveur Linux (VPS recommandé)

* Un domaine configuré

### Installation rapide

1. Clonez ce dépôt:

```shellscript
git clone https://github.com/nic01asFr/claude-code-web.git
cd claude-code-web
```
