# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
Roberto héberge le **bridge com_tel** et en est le **template de référence**. Serveur
(Node 5000 + STT 5001 + TTS 5002) lancé via `com_telephone/_commands/com_manager.py` ; `.env`
(AUTH_TOKEN, TUNNEL_URL, VAPID) hors git. `projects.json` (non versionné) : `ia_life`, `tsa`,
`roberto`, `creazik_v2` — **tous raccordés**, plus aucune copie autonome active (creazik_v2
raccordé le 2026-08-28). PWA : écran d'accueil (liste projets + pastille non-lus persistée),
partage image + JSON (`_docs/fichiers/`), notifications fiabilisées (détection premier-plan
`client.visible`, anti-doublon `mid`, un abonnement par `deviceId`). Sécurité : audit
`_docs/audit_securite_2026-08-28.md` — S1-S3+S6 corrigés, S4 (TTS cloud) / S5 / S7 (token) / S8
ouverts. Glossaire `_docs/vocabulaire.md`. Commande `/com_telephone_init <cible> <mode>`.
Roadmap `roadmap_com_telephone_hub.md` : phases 1 à 5 FAIT.

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
- 2026-08-28 : Vocabulaire commun figé (`_docs/vocabulaire.md`) : com_tel, bridge, projet,
  raccordé/autonome, canaux étanches. Termes retenus : "com_tel" (pas "Com"), "bridge" (pas "pont").
- 2026-08-28 : creazik_v2 raccordé au bridge ; fin de la dernière copie autonome. Tous les
  déploiements se font désormais en mode raccordé (autonome = référence historique seulement).
- 2026-08-28 : Audit sécurité (`_docs/audit_securite_2026-08-28.md`). Corrigés : `/send` et
  `/push/test` refusent les requêtes proxifiées (S1), nettoyage `\r\n\t` des textes journalisés
  (S2), extension image assainie + limites de taille + maxPayload WS (S3/S6).
