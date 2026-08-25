# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
com_telephone (source Roberto) remplacé par la version testée en conditions réelles dans creazik_v2
(push VAPID, corrections). com_manager affiche le lien appli (token) au démarrage et démarre tout
par défaut sans argument. Déployé dans D:\ServOMorph\IA_Life\ROBERTO\com_telephone (AUTH_TOKEN +
VAPID + TUNNEL_URL dédiés). Registre : com_telephone/DEPLOYMENTS.md (v0.2 IA_Life). En attente :
test réel utilisateur (Monitor + réponse téléphone) côté IA_Life. Process serveur arrêtés.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-20 : Initialisation du protocole vibecoding.
- 2026-08-21 : AUTH_TOKEN de com_telephone stocké dans server/.env (hors git), chargé par
  com_manager.py avant le lancement de node — pas de secret en dur dans le code.
- 2026-08-21 : Convention de déploiement : tout ce qui vient de ServOMorph s'installe dans un
  dossier ROBERTO à la racine du projet cible. Si le projet a déjà du contenu ServOMorph,
  l'analyser avant, ne jamais le vider.
- 2026-08-25 : com_telephone remplacé intégralement par la version validée en réel dans creazik_v2
  (nouvelle source de vérité pour les futurs déploiements).
- 2026-08-25 : com_manager.py affiche le lien appli (token) au démarrage et démarre tout par défaut
  sans argument — nécessite TUNNEL_URL dans .env en plus d'AUTH_TOKEN.
