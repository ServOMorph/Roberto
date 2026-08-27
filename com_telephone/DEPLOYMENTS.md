# Deployments — com_telephone

Liste des installations de com_telephone (assistant vocal distant pour Claude Code).

Convention : tout déploiement se fait dans un dossier `ROBERTO` à la racine du projet cible
(`D:\<projet>\ROBERTO\com_telephone`). Si le projet contient déjà du contenu ServOMorph,
l'analyser d'abord — ne jamais le vider.

> Migration en cours (cf. `Roberto/roadmap_com_telephone_hub.md`) : le pont partagé passe de
> IA_Life à Roberto comme hôte, et `Roberto/com_telephone/` devient le template de référence.
> Tant que la phase 2 n'est pas faite, le serveur tourne encore dans `IA_Life\ROBERTO\com_telephone`.

Depuis v0.3, le serveur (Node + STT + TTS + tunnel + PWA) est **partagé** : un seul pont, hébergé
par le projet hôte, dessert plusieurs projets. Le routage se fait par le champ `project` (cf.
`voice-code-bridge/server/projects.json`) : chaque projet a son log `logs/messages_<id>.log`, son
dossier de captures, et une session Claude Code qui surveille son propre log. La PWA téléphone
affiche un sélecteur de projet. Un déploiement « raccordé » (creazik_v2 excepté, resté autonome) ne
copie pas le serveur : il ajoute seulement un `ROBERTO/com_telephone/README.md`, une commande de
surveillance, et une entrée dans `projects.json` du pont hôte.

| Version | Projet | Chemin | Type | Date |
|---------|--------|--------|------|------|
| v0.1 | creazik_v2 | D:\ServOMorph\creazik_v2\ROBERTO\com_telephone | copie autonome | 2026-08-21 |
| v0.2 | IA_Life | D:\ServOMorph\IA_Life\ROBERTO\com_telephone | pont hôte (partagé) | 2026-08-25 |
| v0.3 | Appli_TSA_SDI_TDAH | D:\ServOMorph\Appli_TSA_SDI_TDAH\ROBERTO\com_telephone | raccordé au pont IA_Life | 2026-08-27 |
