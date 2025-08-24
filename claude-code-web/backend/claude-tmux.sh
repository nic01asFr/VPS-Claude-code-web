#!/bin/bash

# Script pour interagir avec Claude Code via tmux
# Permet à Claude Assistant d'envoyer des commandes à Claude Code

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SESSION_NAME="claude-code-session"
WINDOW_NAME="claude-code"

# Détection automatique du répertoire de travail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="/root/docker" # Répertoire de travail sur l'hôte
HOST_PATH=${HOST_PATH:-"/root"}

echo -e "${BLUE}🤖 Claude Code TMux Bridge${NC}"
echo -e "${BLUE}==========================${NC}"
echo -e "${BLUE}📁 Répertoire de travail: $WORK_DIR${NC}"
echo -e "${BLUE}🏠 Répertoire hôte: $HOST_PATH${NC}"
echo

# Fonction pour installer tmux si nécessaire
install_tmux() {
    if ! command -v tmux &> /dev/null; then
        echo -e "${YELLOW}📦 tmux est nécessaire sur l'hôte${NC}"
    fi
}

# Fonction pour démarrer Claude Code dans tmux
start_claude_in_tmux() {
    echo -e "${BLUE}🚀 Démarrage de Claude Code dans tmux sur l'hôte...${NC}"
    
    # Créer une nouvelle session tmux
    tmux new-session -d -s "$SESSION_NAME" -n "$WINDOW_NAME"
    
    # Configurer l'environnement et lancer Claude Code
    # Utilisez le chemin de Claude Code installé sur l'hôte
    tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME" "export PATH=$HOST_PATH/.npm-global/bin:/usr/local/bin:/usr/bin:/bin" C-m
    tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME" "cd '$WORK_DIR'" C-m
    tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME" "claude" C-m
    
    echo -e "${GREEN}✅ Claude Code démarré dans tmux session '${SESSION_NAME}'${NC}"
    sleep 3
}

# Fonction pour vérifier si la session existe
check_session() {
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Fonction pour envoyer une commande à Claude Code
send_command() {
    local command="$1"
    local output_file="/tmp/claude_tmux_output.txt"
    
    echo -e "${BLUE}🔄 Envoi de la commande: ${command}${NC}"
    
    if ! check_session; then
        echo -e "${RED}❌ Session tmux non trouvée${NC}"
        echo -e "${YELLOW}💡 Lancez d'abord: $0 --start${NC}"
        return 1
    fi
    
    # Effacer le fichier de sortie précédent
    > "$output_file"
    
    # Envoyer la commande
    tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME" "$command" C-m
    
    # Attendre un peu pour la réponse
    echo -e "${YELLOW}⏳ Attente de la réponse...${NC}"
    sleep 5
    
    # Capturer la sortie de la session tmux
    tmux capture-pane -t "$SESSION_NAME:$WINDOW_NAME" -p > "$output_file"
    
    if [ -f "$output_file" ]; then
        echo -e "${GREEN}🤖 Sortie de Claude Code:${NC}"
        echo -e "${BLUE}────────────────────────${NC}"
        tail -n 20 "$output_file"
        echo -e "${BLUE}────────────────────────${NC}"
    else
        echo -e "${RED}❌ Pas de sortie récupérée${NC}"
    fi
}

# Fonction pour attacher à la session
attach_session() {
    if check_session; then
        echo -e "${GREEN}🔗 Attachement à la session Claude Code...${NC}"
        tmux attach-session -t "$SESSION_NAME"
    else
        echo -e "${RED}❌ Session non trouvée${NC}"
        echo -e "${YELLOW}💡 Lancez d'abord: $0 --start${NC}"
    fi
}

# Fonction pour afficher le statut
show_status() {
    echo -e "${BLUE}📊 Statut de la session:${NC}"
    if check_session; then
        echo -e "${GREEN}✅ Session '$SESSION_NAME' active${NC}"
        echo -e "${BLUE}Sessions tmux:${NC}"
        tmux list-sessions
    else
        echo -e "${RED}❌ Session '$SESSION_NAME' inactive${NC}"
    fi
}

# Fonction pour arrêter la session
stop_session() {
    if check_session; then
        echo -e "${YELLOW}🛑 Arrêt de la session Claude Code...${NC}"
        tmux kill-session -t "$SESSION_NAME"
        echo -e "${GREEN}✅ Session arrêtée${NC}"
    else
        echo -e "${YELLOW}⚠️ Session déjà arrêtée${NC}"
    fi
}

# Fonction d'aide
show_help() {
    echo -e "${BLUE}Utilisation:${NC}"
    echo "  $0 --start                   # Démarrer Claude Code dans tmux"
    echo "  $0 --command \"question\"     # Envoyer une commande"
    echo "  $0 --attach                  # Attacher à la session"
    echo "  $0 --status                  # Voir le statut"
    echo "  $0 --stop                    # Arrêter la session"
    echo "  $0 --help                    # Afficher cette aide"
    echo ""
    echo -e "${BLUE}Exemples:${NC}"
    echo "  $0 --start"
    echo "  $0 --command \"Bonjour Claude Code\""
    echo "  $0 --attach"
}

# Fonction principale
main() {
    install_tmux
    
    case "${1:-}" in
        --start)
            if check_session; then
                echo -e "${YELLOW}⚠️ Session déjà active${NC}"
                show_status
            else
                start_claude_in_tmux
            fi
            ;;
        --command)
            if [ -n "$2" ]; then
                send_command "$2"
            else
                echo -e "${RED}❌ Commande manquante${NC}"
                echo "Usage: $0 --command \"votre commande\""
            fi
            ;;
        --attach)
            attach_session
            ;;
        --status)
            show_status
            ;;
        --stop)
            stop_session
            ;;
        --help)
            show_help
            ;;
        *)
            echo -e "${YELLOW}Mode interactif${NC}"
            echo -e "${BLUE}Tapez vos commandes (ou 'quit' pour quitter):${NC}"
            while true; do
                read -p "💬 Commande: " user_command
                if [ "$user_command" = "quit" ] || [ "$user_command" = "exit" ]; then
                    break
                fi
                if [ -n "$user_command" ]; then
                    send_command "$user_command"
                fi
            done
            ;;
    esac
}

main "$@" 