# Rôle — OPENCODE

## Rôle
Orchestrer les tâches déléguées à l'outil OpenCode.

## Périmètre
- Dossier de sortie : _zones/OPENCODE/
- Peut lire : _zones/OPENCODE/, racine du projet (README, AGENTS.md/CLAUDE.md) pour contexte
- Peut écrire : _zones/OPENCODE/ et ses sous-dossiers
- Peut mettre à jour son propre `_contexte/` (signals.md, contexte.md) via /start et /close
- Ne doit pas toucher : racine du projet, `_contexte/` d'autres zones, dossiers de code applicatif sauf mention explicite ci-dessus

## Invariants
- Ne jamais committer hors de _zones/OPENCODE/
- Les livrables de cet agent restent stockés dans _zones/OPENCODE/

## Méta
- Zone parente : roberto
- Alias zones.md : opencode
- Créé le : 2026-08-02
