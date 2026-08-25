# Signals — roberto   (MAJ 2026-08-25)

## Actions ouvertes
- [P1|ouvert] Valider en conditions réelles que `/com_manager` (via `@com_manager.md`, sans argument) active tout et permet à l'agent `ia-life-83` de répondre aux messages du téléphone (Monitor). fait quand: l'utilisateur confirme avoir reçu une réponse vocale sur le téléphone après un message envoyé depuis l'appli déployée dans IA_Life. réf: D:\ServOMorph\IA_Life\ROBERTO\com_telephone\_commands\com_manager.md, session ia-life-83
- [P2|ouvert] Fiabiliser la livraison des messages `/send` en cas de coupure WebSocket (Safari iOS décharge l'onglet en arrière-plan, message perdu sans rattrapage). fait quand: un mécanisme de file d'attente ou de ré-émission est en place, ou décision explicite de ne pas le faire. réf: com_telephone/voice-code-bridge/server/server.js (endpoint /send), com_telephone/voice-code-bridge/mobile/app.js (reconnectTimer)

## Dernière session
<!-- Écrasé intégralement par /close. Synthèse < 25 lignes. -->
# Session du 2026-08-25

## Décisions prises
- com_telephone (Roberto) remplacé intégralement par la version fonctionnelle de creazik_v2
  (push notifications VAPID, corrections serveur/mobile).
- Déploiement de com_telephone dans un nouveau projet : IA_Life (D:\ServOMorph\IA_Life\ROBERTO).
- com_manager affiche désormais le lien appli (token inclus) au démarrage de node ; nécessite
  TUNNEL_URL en plus d'AUTH_TOKEN dans .env.
- Action par défaut de com_manager changée de `status` à `start` : appel sans argument = activation
  automatique complète.

## Livrables produits ou modifiés
- com_telephone/ (README, com_manager.md/.py, gitignore, app.js, index.html, package.json/lock,
  server.js, tts_server.py, _docs/, sw.js, salutations.json) : remplacés/mis à jour depuis creazik_v2
- com_telephone/voice-code-bridge/server/.env : ajout TUNNEL_URL
- com_telephone/DEPLOYMENTS.md : entrée v0.2 IA_Life ajoutée
- D:\ServOMorph\IA_Life\ROBERTO\com_telephone : déployé (copie + .env dédié AUTH_TOKEN/VAPID/TUNNEL_URL)

## Hypothèses validées / invalidées
- VALIDE : affichage du lien avec token au démarrage (curl : 401 sans token, 200 avec)
- VALIDE : démarrage automatique sans argument (testé en direct sur IA_Life)
- EN ATTENTE : test réel utilisateur via `/com_manager` dans la session VSCode IA_Life, avec
  activation effective du Monitor et réponse depuis le téléphone

## Prochaine étape exacte
Utilisateur teste "applique @com_manager.md" (sans argument) dans la session VSCode ouverte sur
IA_Life ; vérifier lien affiché + réponse effective reçue sur le téléphone.

## Question bloquante pour la session suivante
Aucune
