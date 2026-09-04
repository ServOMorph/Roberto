## v0.8 — 2026-09-04

### Ajouté
- `roadmap_revue_code_nocturne.md` : spécification du workflow de revue de code nocturne (4
  phases) — `/code-review` niveau max déclenché par une tâche planifiée par l'utilisateur (pas
  d'overlay), sortie unique dans `<cible>/ROBERTO/` en langage simple priorisé par urgence,
  discussion vocale via com_telephone, correctifs exécutés la nuit suivante par le planificateur.

## v0.7 — 2026-09-04

### Ajouté
- `PLANIFICATEUR/overlay.py` : overlays plein écran (charte VERTIA) au lancement (annonce des
  tâches, butoir, bouton OK) et à la fin (bilan des statuts, coût, durée, bouton Fermer) de
  l'orchestrateur, désactivables via `--no-overlay`. Testés visuellement, validés par l'utilisateur.

## v0.6 — 2026-09-04

### Ajouté
- `PLANIFICATEUR/` : orchestrateur de tâches Claude Code nocturnes. `orchestrateur.py` (boucle
  séquentielle, retry sur limite 5 h, butoir 06:00, reprise après crash sans rejeu, timeout
  wall-clock + kill de l'arbre de processus), `rapport.py` (HTML charte VERTIA, un run avec
  outils refusés classé `refus` et non `faite`), `tache.py` (CLI add/list/rm/reset avec
  validation d'allowlist immédiate), `notifier.py` (push du résumé sur com_telephone),
  `allowlist.txt`, `queue.json`, `lancer_nuit.cmd`, `test_planificateur.py` (36 tests).
- `roadmap_planificateur_nuit.md` : Phases 1-2 [FAIT], Phase 3 [EN COURS].

### Modifié
- `tests_manuels.md` : ajout de la création de la tâche planifiée Windows et de la première nuit
  réelle du planificateur (gate Phase 2).

## v0.5 — 2026-08-29

### Ajouté
- PWA : pastille de messages non lus sur le bouton "Projets" du bandeau (vue chat), signalant
  des non-lus dans un autre projet que le projet courant.
- PWA : bouton "Mettre le PC en veille" sur l'écran d'accueil (confirmation inline), message
  WebSocket `client.sleep` -> le serveur lance `SetSuspendState` (Windows) / `systemctl suspend`,
  debounce 5 s.
- com_telephone : `_docs/analyse_acces_externe_marie_tsa.md` (faisabilité d'un canal pour une
  personne externe limitée au projet `tsa` : deux voies + questions à trancher).

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
