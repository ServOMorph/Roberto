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
Roberto conserve le **bridge com_tel** (Node, STT et TTS), raccordé à VibeObs et durci le 2026-11-19 :
appairage du premier appareil, liste blanche des commandes `!`, écoute locale, notifications
discrètes, voix unique, messages vocaux regroupés. `/roberto` démarre le pont et relance l'écoute
toutes les 30 minutes ; le tunnel est lancé par l'utilisateur seul. Le planificateur nocturne est en
Phase 3 : `typecheck` a réussi lors de la nuit réelle, mais `audit-deps` refuse encore `Write`.
La revue nocturne est en Phase 1 ; restent le déclenchement Windows et une revue complète.
`/refacto_projet` produit un plan et une roadmap non destructifs.
