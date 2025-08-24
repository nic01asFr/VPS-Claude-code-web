#!/bin/bash
# Script d'initialisation de session Claude Code pour projets
# Usage: ./init-project-session.sh <project_id>

set -e

PROJECT_ID="$1"
PROJECT_PATH="/root/docker/apps/$PROJECT_ID"
CLAUDE_MD_PATH="$PROJECT_PATH/CLAUDE.md"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Fonction d'aide
show_help() {
    echo -e "${BLUE}Script d'initialisation de session Claude Code pour projets${NC}"
    echo ""
    echo "Usage: $0 <project_id>"
    echo ""
    echo "Arguments:"
    echo "  project_id    Identifiant du projet (dossier dans /root/docker/apps/)"
    echo ""
    echo "Exemples:"
    echo "  $0 mon-ecommerce"
    echo "  $0 blog-personnel"
    echo ""
    echo "Ce script configure l'environnement pour Claude Code avec:"
    echo "  - Contexte du projet via CLAUDE.md"
    echo "  - Variables d'environnement spécifiques"
    echo "  - Répertoire de travail du projet"
}

# Validation des arguments
if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Erreur: Project ID requis${NC}"
    show_help
    exit 1
fi

# Vérification que le projet existe
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}❌ Erreur: Projet '$PROJECT_ID' non trouvé dans $PROJECT_PATH${NC}"
    echo -e "${YELLOW}💡 Projets disponibles:${NC}"
    ls -1 /root/docker/apps/ 2>/dev/null || echo "Aucun projet trouvé"
    exit 1
fi

echo -e "${BLUE}🚀 Initialisation de la session Claude Code pour le projet '$PROJECT_ID'${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Affichage des informations du projet
echo -e "${CYAN}📁 Répertoire du projet:${NC} $PROJECT_PATH"

# Vérification et configuration du contexte CLAUDE.md
if [ -f "$CLAUDE_MD_PATH" ]; then
    echo -e "${GREEN}📖 Fichier CLAUDE.md trouvé:${NC} $CLAUDE_MD_PATH"
    
    # Extraire quelques informations du CLAUDE.md
    if grep -q "## Project Overview" "$CLAUDE_MD_PATH"; then
        PROJECT_DESC=$(sed -n '/## Project Overview/,/##/p' "$CLAUDE_MD_PATH" | head -5 | tail -3 | head -1)
        echo -e "${CYAN}📝 Description:${NC} $PROJECT_DESC"
    fi
    
    if grep -q "### Technology Stack" "$CLAUDE_MD_PATH"; then
        TECH_STACK=$(sed -n '/### Technology Stack/,/##/p' "$CLAUDE_MD_PATH" | head -2 | tail -1)
        echo -e "${CYAN}🛠️  Stack technique:${NC} $TECH_STACK"
    fi
else
    echo -e "${YELLOW}⚠️  Fichier CLAUDE.md non trouvé - Session standard${NC}"
fi

echo ""

# Configuration des variables d'environnement
echo -e "${BLUE}🔧 Configuration de l'environnement...${NC}"

export PROJECT_NAME="$PROJECT_ID"
export PROJECT_PATH="$PROJECT_PATH"

if [ -f "$CLAUDE_MD_PATH" ]; then
    export CLAUDE_PROJECT_CONTEXT="$CLAUDE_MD_PATH"
    echo -e "${GREEN}✅ CLAUDE_PROJECT_CONTEXT=$CLAUDE_MD_PATH${NC}"
fi

echo -e "${GREEN}✅ PROJECT_NAME=$PROJECT_NAME${NC}"
echo -e "${GREEN}✅ PROJECT_PATH=$PROJECT_PATH${NC}"

# Changement vers le répertoire du projet
echo ""
echo -e "${BLUE}📂 Changement vers le répertoire du projet...${NC}"
cd "$PROJECT_PATH"
echo -e "${GREEN}✅ Répertoire courant: $(pwd)${NC}"

# Affichage du contenu du projet
echo ""
echo -e "${BLUE}📋 Contenu du projet:${NC}"
ls -la --color=auto

# Vérification des fichiers importants
echo ""
echo -e "${BLUE}🔍 Vérification des fichiers de configuration...${NC}"

important_files=("docker-compose.yml" "package.json" "requirements.txt" ".env.example" "README.md")
for file in "${important_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${YELLOW}⚪ $file (non trouvé)${NC}"
    fi
done

# Vérification des scripts de développement
if [ -d "scripts" ]; then
    echo ""
    echo -e "${BLUE}📜 Scripts de développement disponibles:${NC}"
    ls -1 scripts/*.sh 2>/dev/null | while read script; do
        echo -e "${GREEN}✅ $script${NC}"
    done
fi

# Instructions finales
echo ""
echo -e "${BLUE}🎯 Environnement configuré avec succès!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${CYAN}💡 Prochaines étapes suggérées:${NC}"

if [ -f "scripts/start.sh" ]; then
    echo -e "   ${GREEN}1.${NC} Démarrer le projet: ${YELLOW}./scripts/start.sh${NC}"
fi

if [ -f "docker-compose.yml" ]; then
    echo -e "   ${GREEN}2.${NC} Ou avec Docker: ${YELLOW}docker-compose up -d --build${NC}"
fi

if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    echo -e "   ${GREEN}3.${NC} Configurer l'environnement: ${YELLOW}cp .env.example .env && nano .env${NC}"
fi

echo -e "   ${GREEN}4.${NC} Ouvrir Claude Code pour commencer le développement"

echo ""
echo -e "${GREEN}🚀 Prêt à développer avec Claude Code!${NC}"

# Si nous sommes dans une session tmux, afficher des informations supplémentaires
if [ -n "$TMUX" ]; then
    echo ""
    echo -e "${CYAN}📡 Session tmux détectée${NC}"
    echo -e "${CYAN}   Session: $(tmux display-message -p '#S')${NC}"
    echo -e "${CYAN}   Fenêtre: $(tmux display-message -p '#W')${NC}"
fi

# Optionnel: Démarrer Claude Code automatiquement si le paramètre --auto est passé
if [ "$2" = "--auto" ]; then
    echo ""
    echo -e "${BLUE}🤖 Démarrage automatique de Claude Code...${NC}"
    
    # Vérifier si Claude Code est disponible
    if command -v claude &> /dev/null; then
        echo -e "${GREEN}✅ Claude Code trouvé, démarrage...${NC}"
        claude
    elif [ -f "/root/.npm-global/bin/claude" ]; then
        echo -e "${GREEN}✅ Claude Code trouvé dans npm global, démarrage...${NC}"
        /root/.npm-global/bin/claude
    else
        echo -e "${YELLOW}⚠️  Claude Code non trouvé dans le PATH${NC}"
        echo -e "${CYAN}💡 Installez Claude Code ou ajustez le PATH${NC}"
    fi
fi