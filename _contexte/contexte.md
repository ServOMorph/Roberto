# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
Roberto est désormais l'**hôte du pont com_telephone** et son **template de référence**.
`com_telephone/` contient la version multi-projets aboutie (routage par `project` via
`voice-code-bridge/server/projects.json`, endpoint `GET /projects`, logs `logs/messages_<id>.log`,
captures par projet, validations `project`/`text` sur `POST /send`, sélecteur de projet dans la
PWA, correctif double-connexion WebSocket). Le serveur (Node 5000 + STT 5001 + TTS 5002) tourne
depuis `D:\ServOMorph\Roberto\com_telephone\_commands\com_manager.py` ; `.env` (AUTH_TOKEN,
TUNNEL_URL, VAPID) repris d'IA_Life pour préserver le lien téléphone et les abonnements push.
Registre : `projects.json` = `ia_life` + `tsa` (non versionné). Projets raccordés : IA_Life et TSA
(README léger + `/roberto` + section CLAUDE.md ; surveillent `logs/messages_<id>.log` chez Roberto).
creazik_v2 reste une copie autonome. Commande `/com_telephone_init <cible> <mode>` pour installer
dans un nouveau projet (`raccorde` | `autonome`). Roadmap : `roadmap_com_telephone_hub.md`
(phases 1 à 5 faites, statuts à finaliser par /close). Reliquat : dossier vide
`IA_Life\ROBERTO\com_telephone\voice-code-bridge\` (rmdir bloqué par un handle Windows).

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-20 : Initialisation du protocole vibecoding.
- 2026-08-21 : AUTH_TOKEN de com_telephone stocké dans server/.env (hors git), chargé par
  com_manager.py avant le lancement de node — pas de secret en dur dans le code.
- 2026-08-21 : Convention de déploiement : tout ce qui vient de ServOMorph s'installe dans un
  dossier ROBERTO à la racine du projet cible. Si le projet a déjà du contenu ServOMorph,
  l'analyser avant, ne jamais le vider.
- 2026-08-25 : com_telephone remplacé intégralement par la version validée en réel dans creazik_v2
  (nouvelle source de vérité pour les futurs déploiements).
- 2026-08-25 : com_manager.py affiche le lien appli (token) au démarrage et démarre tout par défaut
  sans argument — nécessite TUNNEL_URL dans .env en plus d'AUTH_TOKEN.
- 2026-08-28 : com_telephone rendu multi-projets (routage par `project`, `projects.json`, sélecteur
  PWA) — développé et durci dans IA_Life, puis promu ici comme template unique.
- 2026-08-28 : Roberto devient l'hôte du pont (le serveur y tourne) ; IA_Life et TSA sont des
  projets raccordés. `.env` d'IA_Life réutilisé tel quel (lien téléphone + push préservés).
  Commande `/com_telephone_init` ajoutée pour les futurs déploiements.
