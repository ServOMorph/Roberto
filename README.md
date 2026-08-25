# Roberto

## Objectif
Copie réorganisée de `claude-vibecoding-kit`, réalisée étape par étape.

## Stack
Markdown, Python (`ollama_call.py`), templates de commandes Claude Code.

## Structure
- `.claude/` : configuration du protocole vibecoding (CLAUDE.md, zones, commandes)
- `_contexte/` : mémoire de session (contexte.md, signals.md)
- `_docs/` : documentation du protocole et du but du projet
- `AUTOMATISATIONS/` : workflows automatisés (quotidien, urgences, avancement)
- `com_telephone/` : assistant vocal distant pour Claude Code (`voice-code-bridge/`)

## État actuel
`com_telephone` (source) remplacé par la version validée en conditions réelles dans creazik_v2
(push VAPID, corrections). `com_manager` affiche le lien appli (token) au démarrage et démarre
tout par défaut sans argument. Déployé dans `D:\ServOMorph\creazik_v2\ROBERTO` et
`D:\ServOMorph\IA_Life\ROBERTO` (convention : dossier `ROBERTO` à la racine des projets cibles).
Registre : `com_telephone/DEPLOYMENTS.md`. En attente : test réel utilisateur (Monitor + réponse
téléphone) côté IA_Life.
