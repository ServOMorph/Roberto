# Deployments — com_telephone

Liste des installations de com_telephone (assistant vocal distant pour Claude Code).

Convention : tout déploiement se fait dans un dossier `ROBERTO` à la racine du projet cible
(`D:\<projet>\ROBERTO\com_telephone`). Si le projet contient déjà du contenu ServOMorph,
l'analyser d'abord — ne jamais le vider.

Depuis v0.3, le serveur (Node + STT + TTS + tunnel + PWA) est **partagé** : un seul pont, hébergé
par **Roberto** depuis le 2026-08-28 (auparavant IA_Life), dessert plusieurs projets. Le routage se
fait par le champ `project` (cf. `voice-code-bridge/server/projects.json`) : chaque projet a son log
`logs/messages_<id>.log`, son dossier de captures, et une session Claude Code qui surveille son
propre log. La PWA téléphone affiche un sélecteur de projet. Un déploiement « raccordé » (creazik_v2
excepté, resté autonome) ne copie pas le serveur : il ajoute seulement un
`ROBERTO/com_telephone/README.md`, une commande de surveillance (`/roberto`), et une entrée dans
`projects.json` du pont hôte. Voir `Roberto/roadmap_com_telephone_hub.md` pour la migration et la
commande d'init.

| Version | Projet | Chemin | Type | Date |
|---------|--------|--------|------|------|
| v0.1 | creazik_v2 | D:\ServOMorph\creazik_v2\ROBERTO\com_telephone | copie autonome | 2026-08-21 |
| v0.4 | Roberto | D:\ServOMorph\Roberto\com_telephone | pont hôte + template + raccordé (onglet `Roberto`) | 2026-08-28 |
| v0.4 | IA_Life | D:\ServOMorph\IA_Life\ROBERTO\com_telephone | raccordé au pont Roberto | 2026-08-28 |
| v0.4 | Appli_TSA_SDI_TDAH | D:\ServOMorph\Appli_TSA_SDI_TDAH\ROBERTO\com_telephone | raccordé au pont Roberto | 2026-08-27 |
