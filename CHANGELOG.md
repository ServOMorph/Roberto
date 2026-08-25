## v0.3 — 2026-08-25

### Ajouté
- com_manager.py : affiche le lien appli (`https://<TUNNEL_URL>/?token=<AUTH_TOKEN>`) au démarrage
  de node. Action par défaut passée de `status` à `start` (appel sans argument = activation complète).
- com_telephone déployé dans D:\ServOMorph\IA_Life\ROBERTO\com_telephone (AUTH_TOKEN + VAPID +
  TUNNEL_URL dédiés), entrée v0.2 ajoutée à DEPLOYMENTS.md.

### Modifié
- com_telephone (source Roberto) remplacé intégralement par la version validée en conditions
  réelles dans creazik_v2 (notifications push VAPID, corrections serveur/mobile).

## v0.2 — 2026-08-22

### Ajouté
- com_telephone : DEPLOYMENTS.md (registre des installations) + convention de déploiement dans un
  dossier ROBERTO à la racine des projets cibles (analyser sans vider si contenu existant).
- Installation de com_telephone dans D:\ServOMorph\creazik_v2\ROBERTO\com_telephone (copie
  complète, AUTH_TOKEN dédié, npm install).

### Validé
- Correctif CSS de la bulle vocale (vert/orange après pause) confirmé en test réel — test manuel clos.

## v0.1 — 2026-08-21

### Corrigé
- com_telephone : troncature de message vocal lors d'une pause/reprise du micro (état
  d'enregistrement global partagé remplacé par des sessions isolées).
- com_telephone : bulle vocale bloquée sur la couleur "pause" (gris) au lieu de refléter
  l'état réel (envoi/réflexion), conflit d'ordre CSS entre `.paused` et `.done`/`.thinking`.

### Ajouté
- com_telephone : chargement de `server/.env` (AUTH_TOKEN) par `com_manager.py` avant le
  lancement du serveur Node.
