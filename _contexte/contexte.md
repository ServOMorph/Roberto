# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
com_telephone opérationnel de bout en bout, installé dans creazik_v2 (dossier ROBERTO, AUTH_TOKEN
dédié). Registre des déploiements : com_telephone/DEPLOYMENTS.md. Correctif bulle validé en réel.
En attente : récupération de la version corrigée de com_manager.md depuis la copie creazik_v2
(tests utilisateur en cours). Process serveur arrêtés.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-20 : Initialisation du protocole vibecoding.
- 2026-08-21 : AUTH_TOKEN de com_telephone stocké dans server/.env (hors git), chargé par
  com_manager.py avant le lancement de node — pas de secret en dur dans le code.
- 2026-08-21 : Convention de déploiement : tout ce qui vient de ServOMorph s'installe dans un
  dossier ROBERTO à la racine du projet cible. Si le projet a déjà du contenu ServOMorph,
  l'analyser avant, ne jamais le vider.
