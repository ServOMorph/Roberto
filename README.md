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
`com_telephone` (assistant vocal) est opérationnel de bout en bout, testé en conditions réelles
depuis un iPhone via tunnel Cloudflare. Un correctif de couleur d'interface reste à reconfirmer
par l'utilisateur (voir `tests_manuels.md`). Processus serveur actuellement arrêtés.
