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
Roberto héberge le **bridge com_tel** (Node, STT et TTS) et demeure le template de référence des
projets raccordés. Le planificateur nocturne est en Phase 3 : `typecheck` a réussi lors de la nuit
réelle, mais `audit-deps` refuse encore l'outil `Write`. La revue nocturne est en Phase 1 ; son
script et la sélection automatique sont testés, mais le déclenchement Windows et une revue complète
restent à valider. `/refacto_projet` prépare désormais, dans Codex avec Astra, un plan non
destructif de refactorisation avec tests avant/après ; sa première exécution réelle est en attente.
