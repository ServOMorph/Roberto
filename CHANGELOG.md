## v0.4 — 2026-08-28

### Ajouté
- PWA : écran d'accueil (liste des projets + pastille de messages non lus persistée), bouton de
  retour depuis le chat, partage de fichier JSON depuis le composer (`user.file`, `_docs/fichiers/`,
  ligne de log `[FICHIER]`).
- com_telephone : `_docs/vocabulaire.md` (glossaire commun : com_tel, bridge, projet,
  raccordé/autonome, canaux étanches), `_docs/audit_securite_2026-08-28.md` (8 constats + plan),
  `_docs/agents_dev_proposition.md` (3 agents de dev, en attente de décision).
- creazik_v2 raccordé au bridge (fin de la dernière copie autonome) ; entrée DEPLOYMENTS.md mise à jour.

### Modifié
- Notifications push : détection premier-plan (`client.visible`), push envoyé dès qu'aucun client
  premier-plan n'a été vu depuis 8 s, message conservé pour rejeu, identifiant `mid` anti-doublon,
  dédoublonnage des abonnements par `deviceId`.
- Bandeau PWA : padding haut forcé sous la barre d'état iOS, `connLabel` masqué, méta
  `apple-mobile-web-app` ajoutées.

### Corrigé
- Sécurité S1 : `/send` et `/push/test` refusent les requêtes portant des en-têtes de tunnel
  (contournement de `isLoopback` par un tunnel local).
- Sécurité S2 : `\r \n \t` retirés des textes journalisés (plus d'injection de fausse ligne
  `!commande` dans le log surveillé par l'agent).
- Sécurité S3 / S6 : extension d'image assainie, contrôle de taille serveur, `maxPayload` WebSocket.
- Notifications reçues en double (abonnements APNs périmés accumulés) : `push_subs.json` réinitialisé.
- `.gitignore` racine : `_docs/captures/` ignoré.

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
