## v0.1 — 2026-08-21

### Corrigé
- com_telephone : troncature de message vocal lors d'une pause/reprise du micro (état
  d'enregistrement global partagé remplacé par des sessions isolées).
- com_telephone : bulle vocale bloquée sur la couleur "pause" (gris) au lieu de refléter
  l'état réel (envoi/réflexion), conflit d'ordre CSS entre `.paused` et `.done`/`.thinking`.

### Ajouté
- com_telephone : chargement de `server/.env` (AUTH_TOKEN) par `com_manager.py` avant le
  lancement du serveur Node.
