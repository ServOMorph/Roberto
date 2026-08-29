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
Roberto héberge le **bridge com_tel** (serveur Node + STT + TTS, lancé par `com_manager.py`) et
en est le template de référence. Projets raccordés : `ia_life`, `tsa`, `roberto`, `creazik_v2`
(tous en mode raccordé, plus aucune copie autonome). PWA : écran d'accueil avec pastille de
messages non lus (aussi sur le bouton "Projets" en vue chat) et bouton de mise en veille du PC
(avec confirmation), partage image + JSON, notifications fiabilisées (détection premier-plan,
anti-doublon `mid`, un abonnement par `deviceId`). Docs `com_telephone/_docs/` : audit sécurité
(S1-S3+S6 corrigés), glossaire, analyse accès externe Marie (en attente). Registre :
`com_telephone/DEPLOYMENTS.md`. En attente : validation réelle des notifications (téléphone
verrouillé), du raccordement creazik_v2, et de la mise en veille depuis la PWA.
