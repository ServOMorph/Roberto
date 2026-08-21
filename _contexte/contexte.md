# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
com_telephone (assistant vocal) opérationnel de bout en bout, testé en conditions réelles depuis
un iPhone. Deux bugs corrigés lors de la session du 2026-08-21 (troncature de message à la reprise
du micro ; couleur de bulle bloquée sur gris). Le correctif couleur reste à reconfirmer par
l'utilisateur (voir tests_manuels.md). Process serveur actuellement arrêtés.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-20 : Initialisation du protocole vibecoding.
- 2026-08-21 : AUTH_TOKEN de com_telephone stocké dans server/.env (hors git), chargé par
  com_manager.py avant le lancement de node — pas de secret en dur dans le code.
