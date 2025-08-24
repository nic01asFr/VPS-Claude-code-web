FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    tmux \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Rendre le script claude-tmux.sh exécutable
RUN chmod +x /app/claude-tmux.sh

# Création du dossier pour les sessions tmux
RUN mkdir -p /app/tmux-sessions

# Configuration pour Claude Code
ENV PATH="/root/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"
ENV ANTHROPIC_API_KEY="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"

# On n'installe plus npm et Claude CLI dans le conteneur
# car ils sont déjà disponibles sur l'hôte et montés via volumes
RUN mkdir -p /root/.npm-global

# Exposition du port
EXPOSE 5000

# Démarrage de l'application
CMD ["python", "app.py"] 