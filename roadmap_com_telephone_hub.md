# Roadmap — Roberto, hôte et centre de pilotage de com_telephone

> Migration structurelle. CLAUDE.md recommande **Opus** pour cette roadmap.
> Rédigée le 2026-08-28 depuis la session IA_Life (pilotage téléphone via le bridge).

## Objectif

Faire de `D:\ServOMorph\Roberto\` l'hôte unique et le centre de pilotage de `com_telephone` :
- le serveur du pont partagé (Node + STT + TTS + tunnel + PWA) tourne dans `Roberto\com_telephone\` ;
- `Roberto\com_telephone\` est le **template de référence** (version multi-projets aboutie dans IA_Life) ;
- une commande d'init, lancée depuis Roberto, installe `com_telephone` dans un projet cible
  (copie autonome **ou** raccordement au pont partagé) ;
- `projects.json` et `DEPLOYMENTS.md` sont pilotés depuis Roberto ;
- IA_Life redevient un simple projet raccordé (comme TSA) ; creazik_v2 reste une copie autonome.

## État de départ (2026-08-28)

- Pont partagé multi-projets fonctionnel, **hébergé dans `IA_Life\ROBERTO\com_telephone\`** :
  server.js multi-projets (`projects.json` ia_life + tsa, endpoint `GET /projects`, routage
  `logs/messages_<id>.log`, captures par projet, validations `project` + `text`), PWA avec
  sélecteur de projet, correctif double-connexion WebSocket.
- `Roberto\com_telephone\` : version **mono-projet obsolète** (antérieure au routage multi-projets).
- Déploiements : creazik_v2 (copie autonome), IA_Life (hôte actuel), TSA (raccordé au pont IA_Life).
- Sessions Claude actives surveillant leur log : IA_Life (`messages_ia_life.log`),
  TSA (`messages_tsa.log`, via `/roberto`).
- `.env` du pont (IA_Life) : `AUTH_TOKEN`, `TUNNEL_URL`, `VAPID_PUBLIC/PRIVATE` — non versionnés.

## Décisions actées

- Serveur du pont : **déplacé dans Roberto** (Roberto devient l'hôte). Validé par l'utilisateur.
- `.env` : **réutiliser les valeurs actuelles d'IA_Life** (AUTH_TOKEN, TUNNEL_URL, VAPID) sur
  Roberto → le lien déjà installé sur le téléphone et les abonnements push restent valides.
- creazik_v2 : hors scope, ne pas toucher.

---

## Phase 1 — Promotion du template dans Roberto  [FAIT]

- Remplacer dans `Roberto\com_telephone\` par les versions d'IA_Life :
  `voice-code-bridge/server/server.js`, `voice-code-bridge/mobile/` (index.html, app.js, sw.js),
  `voice-code-bridge/README.md`, `_commands/com_manager.py`, `_commands/com_manager.md`,
  `README.md`, `DEPLOYMENTS.md`, `voice-code-bridge/.gitignore`.
- Ajouter `voice-code-bridge/server/projects.example.json` (1 entrée générique).
- Ne PAS versionner : `projects.json`, `server/logs/`, `server/messages.log`, `server/.env`,
  `server/voices/`, `server/push_subs.json` — vérifier le `.gitignore` du bridge.
- Purger du template les résidus d'IA_Life (`logs/`, `messages*.log`, `push_subs.json`, `.env`,
  `projects.json`) s'ils ont été copiés.
- Tests : `node -c server.js` ; parse OK de `projects.example.json` ; `com_manager.py status`
  (3 process attendus KO, c'est normal).
- Commit Roberto : « template com_telephone promu en version multi-projets ».

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 2 — Mise en service du pont sur Roberto  [FAIT]

- Créer `Roberto\com_telephone\voice-code-bridge\server\.env` avec les valeurs actuelles d'IA_Life
  (`AUTH_TOKEN`, `TUNNEL_URL`, `VAPID_PUBLIC`, `VAPID_PRIVATE`).
- Copier `server/voices/` (modèles Piper) depuis IA_Life.
- Créer `Roberto\...\server\projects.json` avec les projets réels : `ia_life` et `tsa`
  (racines et dossiers `_docs/captures` inchangés).
- Fenêtre de bascule (pont indisponible quelques minutes) :
  1. Arrêter les 3 process hébergés par IA_Life (`com_manager.py stop` côté IA_Life) + son Monitor.
  2. Libérer les ports 5000/5001/5002 si besoin.
  3. `com_manager.py start` depuis `Roberto\com_telephone\_commands\`.
  4. Re-lancer le Monitor de cette session sur `Roberto\...\logs\messages_ia_life.log`,
     mettre à jour `_commands/monitor.lock` (côté Roberto).
- Prévenir la session TSA : relancer `/roberto` (le chemin du log passe sous Roberto — adapter
  `IA_Life`/`TSA` `.claude/commands/roberto.md` en Phase 3).
- Tests : `GET /projects` OK ; `POST /send` + message WS routés sur `ia_life` et `tsa` ;
  ouverture du lien appli inchangé depuis le téléphone ; notif push reçue.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 3 — Reconversion d'IA_Life en projet raccordé  [FAIT]

- `IA_Life\ROBERTO\com_telephone\` : supprimer `voice-code-bridge/` et l'ancien `_commands/com_manager.*`.
  Garder / créer :
  - `README.md` de raccordement (pont hébergé par Roberto, log `messages_ia_life.log`,
    `POST /send` avec `"project": "ia_life"`, préfixe `!`, canaux étanches) — modèle TSA.
  - `_commands/.gitignore` (`monitor_ia_life.lock`).
- `IA_Life\.claude\commands\roberto.md` : commande de surveillance du log `messages_ia_life.log`
  chez Roberto (modèle `TSA\.claude\commands\roberto.md`), écrit `monitor_ia_life.lock`.
- `IA_Life\.claude\CLAUDE.md` section « Bridge ROBERTO » : réécrire (pont hébergé par Roberto,
  chemins Roberto, `project: "ia_life"`).
- `IA_Life\roadmap_roberto_multiprojet.md` : marquer la migration (statuts par `/close`).
- `Roberto\com_telephone\DEPLOYMENTS.md` : IA_Life passe de « pont hôte » à « raccordé ».
- Tests : depuis une session IA_Life, `/roberto` met en écoute le bon log ; aller-retour
  téléphone sur l'onglet `IA_Life` ; onglet `TSA` toujours fonctionnel.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 4 — Commande d'init depuis Roberto  [FAIT]

- `Roberto\.claude\commands\com_telephone_init.md` : commande `<projet-cible> <mode>`,
  `mode` = `raccorde` | `autonome`.
  - `raccorde` : crée `<cible>\ROBERTO\com_telephone\` (README + `_commands/.gitignore`),
    ajoute l'entrée dans `projects.json` du pont Roberto, crée `<cible>\.claude\commands\roberto.md`,
    ajoute la section « Bridge ROBERTO » au CLAUDE.md de la cible, met à jour `DEPLOYMENTS.md`.
    Ne copie pas le serveur.
  - `autonome` : copie complète du template `voice-code-bridge/` + `_commands/` dans
    `<cible>\ROBERTO\com_telephone\`, génère un `.env` dédié (nouveau `AUTH_TOKEN`), met à jour
    `DEPLOYMENTS.md`. Modèle creazik_v2.
  - Garde-fous : si `<cible>\ROBERTO\` contient déjà du contenu ServOMorph, l'analyser,
    ne jamais vider ; refuser un `<cible>` inconnu.
- `Roberto\com_telephone\README.md` : section « Initialiser un projet » (les 2 modes, critères
  de choix).
- Tests : `com_telephone_init` en mode `raccorde` sur un projet cible de test, routage
  bout-en-bout vérifié, puis rollback de la cible de test.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

## Phase 5 — Vérification globale + nettoyage  [FAIT]

> Clôturée le 2026-08-28. creazik_v2 également raccordé (plus aucune copie autonome active).
> Reliquats suivis dans `_contexte/signals.md`.

- Revue de l'état cible : Roberto (hôte + template + init), IA_Life (raccordé), TSA (raccordé),
  creazik_v2 (autonome, intact).
- `Roberto\_contexte\contexte.md` : nouveau rôle (hôte du pont, template de référence, init).
- Supprimer les reliquats d'IA_Life (ancienne `com_manager.md`, roadmap absorbée si applicable).
- `Roberto\tests_manuels.md` : checklist finale (2 onglets PWA, init des 2 modes, push, tunnel,
  correctif double-connexion).
- Test final : redémarrage complet du pont depuis Roberto, sessions IA_Life + TSA raccordées,
  aller-retour vocal sur chaque projet.

## Risques / points d'attention

- **Fenêtre d'indisponibilité** en Phase 2 (arrêt IA_Life → démarrage Roberto).
- Les sessions Claude actives (IA_Life, TSA) doivent relancer leur Monitor sur les chemins Roberto
  après Phases 2/3.
- Ports 5000/5001/5002 : un seul pont à la fois. Ne jamais laisser les deux tourner.
- `push_subs.json` : lié aux clés VAPID. Réutiliser le même `.env` préserve les abonnements ;
  en changer imposerait une re-souscription depuis le téléphone.
- creazik_v2 : ne pas toucher.
