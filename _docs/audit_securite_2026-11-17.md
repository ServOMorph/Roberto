# Audit de sécurité — pont com_telephone (2026-11-17, corrections 2026-11-18)

Périmètre : `server.js`, `com_manager.py`, PWA (`app.js`), `.gitignore`, `.claude/settings.json`,
dépendances npm. Le tunnel est hors périmètre (lancé et configuré par l'utilisateur seul).

## Points déjà solides
- Token `AUTH_TOKEN` de 192 bits, comparaison en temps constant.
- `/send` et `/push/test` réservés aux appels locaux non proxifiés.
- STT et TTS liés à `127.0.0.1`.
- Cookie `SameSite=Strict` : pas de pilotage depuis un autre site.
- Noms et tailles des images et fichiers assainis.
- `npm audit` : 0 vulnérabilité.
- `.env`, logs, `projects.json` et `push_subs.json` gitignorés.

## Faiblesses relevées

| Gravité | Faiblesse | Statut |
|---|---|---|
| Critique | Posséder le token revient à contrôler le PC : un message du téléphone vaut confirmation, les commandes `!` lancent des procédures avec commit et push, Roberto relaie vers les autres sessions, et `defaultMode: "auto"` est actif. | En partie corrigé (liste blanche `!`, push réservé au PC). Reste : authentification au niveau du tunnel. |
| Élevé | `com_manager.py start` affichait le token, qui finissait dans les historiques de session. | Corrigé |
| Élevé | Token dans l'URL (historique, raccourci, captures). | Ouvert (mesure 4) |
| Élevé | Un seul token, valable un an, sans révocation par appareil. | En partie : cookie d'appareil et alerte. Reste la mesure 4. |
| Élevé | Node écoutait toutes les interfaces, donc tout le réseau Wi-Fi. | Corrigé (`127.0.0.1`, `BIND_HOST` pour changer) |
| Élevé | Clés VAPID affichées dans une conversation Claude. | Corrigé (régénérées) |
| Élevé | Ancien `AUTH_TOKEN` stocké comme variable d'environnement Windows (niveau utilisateur). | Ouvert, à supprimer par l'utilisateur |
| Moyen | Mise en veille du PC par tout client connecté. | Corrigé (désactivée sauf `ALLOW_REMOTE_SLEEP=1`) |
| Moyen | Aucune limite de connexions, de débit ni de taille. | Corrigé |
| Moyen | Aucune alerte en cas de nouvel appareil. | Corrigé |
| Moyen | Contenu des réponses visible dans les notifications sur l'écran verrouillé. | Ouvert (mesure 9) |
| Faible | Pas de contrôle d'`Origin` sur le WebSocket, pas de CSP, contrôle de chemin sans séparateur final. | Séparateur final corrigé. Le reste est ouvert. |
| Faible | Logs et historique du chat (`localStorage`) en clair. | Ouvert |

## Corrections appliquées le 2026-11-18
- **Liste blanche `!`** : `BANG_ALLOWLIST` dans `.env` (défaut `close,start`). Le serveur répond
  « Commande refusée » sans rien écrire dans le log.
- **Règle push** : depuis le téléphone, une procédure peut committer, mais le push et toute action
  destructive attendent le PC. Règle écrite dans le README com_telephone, dans `/roberto` et dans
  la mémoire de zone.
- **Token masqué** : `start` n'affiche plus le lien. `com_manager.py lien` l'ouvre dans le
  Bloc-notes, via le fichier gitignoré `_commands/lien_appli.local.txt`.
- **Écoute locale** : Node écoute sur `127.0.0.1`.
- **Appairage du premier appareil** : cookie `dev`, liste dans `known_devices.json`, exigé pour le
  WebSocket et l'API. Le premier appareil verrouille le pont : tout autre appareil est refusé (403)
  même avec le bon lien, avec ligne `ALERTE` dans le log et notification push. Révocation :
  supprimer le fichier. Limite : le premier arrivé gagne, donc ouvrir le lien soi-même en premier.
- **Limites** : 5 connexions WebSocket, 30 messages par minute, 10 envois de fichiers par 10 minutes,
  corps de requête plafonnés (64 Ko pour le JSON, 10 Mo pour l'audio).
- **Clés VAPID** : régénérées. La clé publique est désormais servie par `/vapid-public`.
- **Tests** : 12 contrôles d'intégration passés sur un serveur de test (port 5099). Les tests en
  conditions réelles sont listés dans `tests_manuels.md`.

## Mesures restantes recommandées
1. Authentification au niveau du tunnel (compte ou code e-mail), configurée par l'utilisateur.
   C'est la seule protection efficace si le lien fuite.
2. Sessions jointes en voiture hors du mode `auto`. Roberto lui-même est en `auto`
   (`.claude/settings.json`) : à arbitrer, car le relais vocal y fait des appels Bash.
3. Mesure 4 : appairage à usage unique, cookie d'appareil seul valable 30 jours, attribut `Secure`,
   token retiré de l'URL.
4. Mesure 9 : notifications discrètes (« Nouveau message » sans contenu).
5. Contrôle d'`Origin` sur le WebSocket, en-tête CSP.
