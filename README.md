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
- `PLANIFICATEUR/` : orchestrateur de tâches Claude Code nocturnes (confinées, butoir, rapport)

## État actuel
Roberto héberge le **bridge com_tel** (serveur Node + STT + TTS, lancé par `com_manager.py`) et
en est le template de référence. Projets raccordés : `ia_life`, `tsa`, `roberto`, `creazik_v2`
(tous en mode raccordé, plus aucune copie autonome). PWA : écran d'accueil avec pastille de
messages non lus (aussi sur le bouton "Projets" en vue chat) et bouton de mise en veille du PC
(avec confirmation), partage image + JSON, notifications fiabilisées (détection premier-plan,
anti-doublon `mid`, un abonnement par `deviceId`). Docs `com_telephone/_docs/` : audit sécurité
(S1-S3+S6 corrigés), glossaire, analyse accès externe Marie (en attente). Registre :
`com_telephone/DEPLOYMENTS.md`.

Chantier en cours : **planificateur nocturne** (`PLANIFICATEUR/`, `roadmap_planificateur_nuit.md`) —
lance des `claude -p --restricted` la nuit, confinés par `allowlist.txt`, butoir 06:00, retry sur
la limite 5 h, rapport HTML + push com_tel, overlays plein écran d'annonce et de bilan (validés
visuellement). Phases 1-2 [FAIT] (36 tests + validations réelles), Phase 3 [EN COURS]. Nuit réelle
du 2026-09-04 21h00 déclenchée mais gate Phase 2 non franchi (une tâche en `refus`, `Write` refusé
malgré `--tools`, cause non investiguée).

Chantier en cours : **revue de code nocturne** (`roadmap_revue_code_nocturne.md`) — `/code-review`
niveau max déclenché par une tâche planifiée par l'utilisateur (pas d'overlay), sortie unique dans
`<projet cible>/ROBERTO/` en langage simple priorisé par urgence, discussion vocale via
com_telephone, correctifs exécutés la nuit suivante par le planificateur. Phase 1 [EN COURS] :
`PLANIFICATEUR/revue_code.py` écrit et testé (18 tests + confinement vérifié en réel), invocation
via tâche planifiée Windows non testée.

En attente (validation réelle) : notifications téléphone verrouillé, raccordement creazik_v2,
mise en veille depuis la PWA, première nuit du planificateur.
