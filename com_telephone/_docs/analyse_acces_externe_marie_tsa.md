# Analyse — donner à Marie un canal com_tel pour travailler avec Appli_TSA_SDI_TDAH

Demande (2026-08-28) : permettre à une deuxième personne (Marie) d'utiliser un canal du bridge
pour interagir avec le projet `tsa`, avec « toutes les sécurités nécessaires ». Analyse de
faisabilité, non implémentée.

## Ce que l'architecture actuelle permet / interdit

- **Un seul secret** : `AUTH_TOKEN` unique, partagé. Quiconque a le token + l'URL du tunnel a
  accès à **tous** les projets (tous les onglets), à toutes leurs réponses, à l'upload de
  fichiers, et aux commandes `!` (qui exécutent des procédures — git compris — sans confirmation).
- **Diffusion non cloisonnée** : le serveur envoie `assistant.text` / `assistant.audio` de
  **tous** les projets à **tous** les clients connectés ; le filtrage par projet est fait
  côté PWA seulement. Un client tiers recevrait donc aussi les réponses de `roberto`,
  `ia_life`, `creazik_v2`.
- **Notifications** : `sendPushNotification` diffuse à tous les abonnements, sans notion de
  projet autorisé.
- **Pas d'identité, pas d'audit** : impossible de savoir quel utilisateur a envoyé quel message.
- **Révocation** : changer le token coupe tout le monde (valeur unique dans `.env`).

Conclusion : donner le token actuel à Marie = lui donner le contrôle de **tous** les projets,
y compris l'exécution de commandes. Inacceptable pour un accès limité à `tsa`.

## Risque de fond (indépendant du bridge)

Piloter la session Claude Code de `tsa`, c'est disposer d'un quasi-accès complet au projet :
lecture de fichiers, exécution d'outils, actions git. « Sécuriser le canal » ne réduit pas ce
risque — il faut décider ce que Marie a le droit de faire faire à la session `tsa`, et vérifier
ce que le dépôt `tsa` contient (données nominatives éventuelles). Si Marie doit réellement
*opérer* le projet, c'est un rôle de développeuse (accès dépôt + compte), pas un canal téléphone.

## Voie A — multi-utilisateurs dans le bridge actuel

Travail nécessaire (vrai chantier, pas un réglage) :

1. **Registre de jetons** `tokens.json` (hors git) remplaçant le token unique :
   `{ "<token>": { "label": "marie", "projects": ["tsa"], "allowCommands": false } }`.
   Garder `AUTH_TOKEN` comme super-jeton propriétaire (tous projets, commandes autorisées).
2. **Cloisonnement WebSocket** : `verifyClient` résout le jeton -> périmètre ; la connexion
   est étiquetée. `assistant.text` / `assistant.audio` ne sont envoyés qu'aux clients
   autorisés pour le projet concerné.
3. **`user.message`** : le projet est forcé / limité à la liste autorisée du jeton ; rejet sinon.
4. **`GET /projects`** : ne renvoie que les projets autorisés (la PWA de Marie n'affiche que
   l'onglet `tsa`).
5. **Commandes `!`** : si `allowCommands` est faux, le serveur annote la ligne de log
   (`[canal:texte|externe]`) ; la session `tsa` (règle `/roberto` + section CLAUDE.md) ne doit
   **jamais** exécuter un `!` venant d'un envoyeur externe — juste le signaler.
6. **Notifications** : abonnements push étiquetés par jeton/projets ; `sendPushNotification`
   filtre par projet.
7. **Audit** : journaliser le `label` du jeton pour chaque message entrant.
8. **Révocation** : retirer une entrée de `tokens.json` + `restart node`.
9. **Doc** : README bridge + `Appli_TSA_SDI_TDAH` (`/roberto`, section « Bridge ROBERTO »)
   mis à jour pour la règle « envoyeur externe = pas de commandes ».

Effort estimé : moyen. Touche `server.js` en profondeur (auth, broadcast, push) + docs +
côté TSA. À faire après S4/S7 de l'audit sécurité (le token dans l'URL et le contournement de
`isLoopback` restent des sujets ouverts).

## Voie B — second bridge dédié à `tsa`

Lancer une deuxième instance du serveur (ports 5100+), `projects.json` ne contenant que `tsa`,
son propre `.env` (token distinct, VAPID distinct), son propre tunnel. Marie reçoit ce lien.

- Avantages : isolation totale, **zéro modification de code**, révocation = couper l'instance.
- Inconvénients : deux serveurs + deux tunnels à maintenir ; la session `tsa` doit surveiller
  le log de cette instance (pas celui du hub) ; va à l'encontre de la consolidation en un hub
  unique faite cette session. `allowCommands` reste à gérer (même règle côté session TSA).
- C'est en pratique le mode `autonome` de `/com_telephone_init`, appliqué à un usage « invité ».

## Recommandation

- Si le besoin de Marie est **d'échanger avec la session `tsa`** (envoyer des infos/fichiers,
  recevoir un statut) sans piloter le projet : Voie A, avec `allowCommands: false`.
- Si c'est ponctuel / test : Voie B, plus rapide et sans risque de régression sur le hub.
- Dans les deux cas : trancher d'abord ce que Marie peut faire faire à la session `tsa`, et
  auditer le contenu du dépôt `tsa`.

## À clarifier avec l'utilisateur

1. « Travailler avec `appli_tsa` » = échanger avec la session, ou opérer le projet ?
2. Marie doit-elle pouvoir lancer des commandes `!` ?
3. Accès permanent ou temporaire ?
4. Le dépôt `tsa` contient-il des données sensibles / nominatives ?
