# Claude Code Web

Claude Code Web est une application web permettant d'interagir avec Claude d'Anthropic via une interface de codage en ligne.

## Caractéristiques

- Interface web pour interagir avec Claude
- Terminal en ligne avec tmux
- Support pour différents projets
- Configuration par environnement
- Déploiement simplifié via Docker et Traefik

## Structure du projet

```
claude-code-web/
├── backend/            # API Python Flask
├── frontend/           # Application Vue.js
├── docker-compose.example.yml  # Configuration Docker exemple
└── README.md.example   # Documentation
```

## Prérequis

- Docker et Docker Compose
- Traefik (pour le proxy reverse et SSL)
- Node.js et NPM (pour le développement frontend)
- Python 3.8+ (pour le développement backend)

## Installation

1. Clonez ce dépôt
2. Copiez `env.example` vers `.env` et configurez les variables
3. Copiez `claude-code-web/docker-compose.example.yml` vers `claude-code-web/docker-compose.yml`
4. Personnalisez les configurations selon votre environnement

## Configuration

Consultez le fichier `env.example` pour la liste complète des variables d'environnement.

## Démarrage

```bash
cd claude-code-web
docker-compose up -d
```

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Remerciements

- Anthropic pour Claude
- La communauté open source pour les outils et bibliothèques utilisés
