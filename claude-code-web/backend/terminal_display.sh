#!/bin/bash

# Script de test pour l'affichage du terminal Claude Code

# Créer une session tmux pour le test
SESSION_NAME="claude-code-session"
USER_SESSION="claude_test123"

# Nettoyer les sessions existantes
tmux kill-session -t $SESSION_NAME 2>/dev/null || true
tmux kill-session -t $USER_SESSION 2>/dev/null || true

# Créer une nouvelle session avec du contenu visible
tmux new-session -d -s $SESSION_NAME

# Ajouter du contenu coloré et visible
tmux send-keys -t $SESSION_NAME "clear" C-m
tmux send-keys -t $SESSION_NAME "echo -e '\033[1;32m===================================\033[0m'" C-m
tmux send-keys -t $SESSION_NAME "echo -e '\033[1;36mCLAUDE CODE WEB - TEST DE TERMINAL\033[0m'" C-m
tmux send-keys -t $SESSION_NAME "echo -e '\033[1;32m===================================\033[0m'" C-m
tmux send-keys -t $SESSION_NAME "echo ''" C-m
tmux send-keys -t $SESSION_NAME "echo 'Répertoire actuel:'" C-m
tmux send-keys -t $SESSION_NAME "pwd" C-m
tmux send-keys -t $SESSION_NAME "echo ''" C-m
tmux send-keys -t $SESSION_NAME "echo 'Contenu du répertoire:'" C-m
tmux send-keys -t $SESSION_NAME "ls -la" C-m
tmux send-keys -t $SESSION_NAME "echo ''" C-m
tmux send-keys -t $SESSION_NAME "echo -e '\033[1;33mPrêt à recevoir vos commandes...\033[0m'" C-m

# Créer une session utilisateur liée à la session principale
tmux new-session -d -s $USER_SESSION -t $SESSION_NAME

# Capturer la sortie
echo "Contenu de la session principale:"
tmux capture-pane -p -S -500 -t $SESSION_NAME

# Vérifier si les sessions existent
echo ""
echo "Liste des sessions tmux:"
tmux ls

echo ""
echo "Script terminé avec succès." 