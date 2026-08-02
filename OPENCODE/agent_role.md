# Rôle — OPENCODE

## Rôle
Orchestrer les tâches déléguées à l'outil OpenCode.

## Périmètre
- Dossier de sortie : OPENCODE/
- Peut lire : OPENCODE/, racine du projet (README, AGENTS.md/CLAUDE.md) pour contexte
- Peut écrire : OPENCODE/ et ses sous-dossiers
- Peut mettre à jour son propre `_contexte/` (signals.md, contexte.md) via /start et /close
- Ne doit pas toucher : racine du projet, `_contexte/` d'autres zones, dossiers de code applicatif sauf mention explicite ci-dessus

## Invariants
- Ne jamais committer hors de OPENCODE/
- Les livrables de cet agent restent stockés dans OPENCODE/

## Méta
- Zone parente : roberto
- Alias zones.md : opencode
- Créé le : 2026-08-02
