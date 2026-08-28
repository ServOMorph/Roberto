# Audit de sécurité — com_tel (2026-08-28)

Périmètre : `voice-code-bridge/` (serveur Node `server.js`, PWA `mobile/`, STT/TTS Python),
`com_manager`, modèle de déploiement raccordé. Analyse statique du code présent dans le dépôt.

## Modèle de menace

- Le bridge est exposé sur Internet via un tunnel (Cloudflare Tunnel / équivalent) qui termine
  en local et proxie vers `127.0.0.1:5000`.
- Authentification unique : un `AUTH_TOKEN` (48 hex) passé en `?token=` puis stocké en cookie
  `HttpOnly; SameSite=Strict`, valable 1 an. Le même token protège la PWA, le WebSocket,
  `/projects`, `/transcribe`, `/push/*`.
- `/send` et `/push/test` sont réservés à `127.0.0.1` (pas de token).
- STT (5001) et TTS (5002) écoutent sur `127.0.0.1` uniquement — non exposés. OK.
- Aucun secret dans git (`.env`, `push_subs.json`, `projects.json`, `voices/` ignorés — vérifié).

## État des correctifs (2026-08-28)

- **S1 — CORRIGÉ** : `/send` et `/push/test` passent par `isLocalOnly()` = loopback **et**
  absence d'en-têtes de tunnel (`x-forwarded-for`, `cf-connecting-ip`, `forwarded`, `x-real-ip`,
  `x-forwarded-host`, `fly-client-ip`, `true-client-ip`). Testé : requête locale directe → 200,
  requête avec `X-Forwarded-For` ou `CF-Connecting-IP` → 403.
- **S2 — CORRIGÉ** : `oneLine()` retire `\r \n \t` de `msg.text` (user.message), `msg.caption`
  (user.image / user.file), `client.log`, `/debug`. Testé : `text` avec `\n` + `!close` →
  une seule ligne de log, ne commençant pas par `!`.
- **S3 — CORRIGÉ** : extension image = `mime.split("/")[1]` filtré `[^a-z0-9]` puis tronqué à
  8, fallback `png` ; contrôle de taille serveur (rejet hors ]0, 8 Mo]). Testé : MIME
  `image/../../../../evil` → fichier reste dans `captures`, rien écrit ailleurs.
- **S6 — CORRIGÉ** : `maxPayload: 12 Mo` sur le WebSocketServer.
- **S4, S5, S7, S8 — ouverts** (voir plan d'action).

---

## Constat prioritaire

### S1 — `isLoopback()` contourné par le tunnel (élevé, sous réserve du type de tunnel)

`isLoopback()` teste `req.socket.remoteAddress`. Un tunnel qui termine en local (cas de
Cloudflare Tunnel, `cloudflared`, localhost.run, ssh -R...) présente **toutes** les requêtes
distantes comme `127.0.0.1`. Conséquence : `POST /send` et `POST /push/test` deviennent
accessibles à quiconque connaît l'URL du tunnel, sans token.

Impact :
- injection de faux messages « assistant » (texte + audio) dans la PWA du propriétaire ;
- spam de notifications push ;
- consommation TTS arbitraire — et le texte part chez Microsoft (voir S4) ;
- pas de lecture des logs ni d'usurpation du téléphone (le WebSocket, lui, exige le token).

Correctif proposé :
- exiger le token sur `/send` et `/push/test` **en plus** de la restriction loopback
  (les appelants locaux — agents Claude, scripts — peuvent lire `.env`) ; ou
- rejeter la requête si elle porte des en-têtes de tunnel (`x-forwarded-for`,
  `x-forwarded-host`, `cf-connecting-ip`, `forwarded`) — défense simple, non spoofable par un
  tiers qui ne contrôle pas le tunnel.
Recommandé : les deux (token requis + rejet si en-têtes forwarded présents).

## Autres constats

### S2 — Injection de lignes de log via `user.message` → exécution de commandes `!` (élevé, token requis)

`server.js` écrit `msg.text` brut dans `logs/messages_<projet>.log` :
`${date}\t${msg.text}\t[canal:...]`. `msg.text` n'est ni typé ni nettoyé. Un `text` contenant
`\n` injecte des lignes supplémentaires dans le log surveillé par la session Claude.

La convention `!<commande>` fait qu'une ligne commençant par `!` (ex. `!close`, `!deploy`) est
exécutée par l'agent **sans confirmation** (« l'envoi depuis le téléphone vaut confirmation »).
Un client authentifié (ou quiconque a récupéré le token via une URL fuitée) peut donc smuggler
`\n<timestamp>\t!close ...` et déclencher des actions git dans les sessions raccordées.

Aggravant : `user.message` avec un `project` inconnu retombe sur `DEFAULT_PROJECT` — pas besoin
de connaître un id valide.

Correctif : côté serveur, `String(msg.text)` puis retirer `\r` et `\n` (idem `msg.caption` de
`user.image` / `user.file`, idem `client.log`). Optionnel : refuser un `user.message` dont le
texte commence par `!` si on veut réserver les commandes à un canal distinct.

### S3 — Traversée de chemin dans `user.image` via le type MIME (moyen, token requis)

```
const mime = match[1];                    // \d'après /^data:([^;]+);base64,(.+)$/
const ext = mime.split("/")[1] || "png";  // non filtré : peut contenir ../ \ .
const filename = `${date}.${ext}`;
const target = path.join(project.captures, filename);
fs.writeFile(target, Buffer.from(b64, "base64"), () => {});
```

`mime` ne peut pas contenir `;` mais peut contenir `/`, `.`, `\`. `ext` peut donc valoir
`../../../x` → écriture hors de `captures`. Pas de whitelist d'extension, **pas de contrôle de
taille côté serveur** (le 8 Mo est seulement côté client).

Correctif : `ext = (mime.split("/")[1] || "png").replace(/[^a-z0-9]/gi, "").slice(0, 8) || "png"` ;
vérifier `Buffer.byteLength` avant écriture ; `user.file` est déjà correctement assaini, s'en
inspirer.

### S4 — Le texte des réponses part dans le cloud Microsoft (moyen, vie privée)

`tts_server.py` appelle `edge_tts` (service cloud `fr-FR-DeniseNeural`) **en premier**, Piper
local seulement en secours. Chaque réponse « assistant » est donc envoyée à Microsoft. Le
README affirme « Aucune donnée envoyée en cloud » — c'est faux en l'état.

Correctif : soit inverser l'ordre (Piper par défaut, edge derrière un flag `TTS_ALLOW_CLOUD`),
soit assumer et corriger le README. Décision produit à prendre.

### S5 — Contrôle anti-traversée statique sans séparateur (faible)

`if (!filePath.startsWith(MOBILE_DIR))` — `MOBILE_DIR` sans `path.sep` final. Un répertoire
frère nommé `mobileXXX` passerait le test. Aucun frère de ce type aujourd'hui, mais à durcir :
`startsWith(MOBILE_DIR + path.sep)`.

### S6 — Pas de limite de taille WebSocket / DoS mémoire (faible, token requis)

`new WebSocketServer({ server })` sans `maxPayload`. Un client authentifié peut envoyer des
trames volumineuses. Ajouter `maxPayload: 12 * 1024 * 1024` et les contrôles de taille S3.

### S7 — Cycle de vie du token (moyen, opérationnel)

- cookie 1 an, pas de rotation ni de révocation documentée ;
- `com_manager` imprime l'URL complète **avec le token** dans la console/les logs de process ;
- un token fuité = contrôle total du canal téléphone (envoyer des `user.message`, piloter
  l'agent, recevoir les réponses).

Correctif : réduire le `Max-Age` (ex. 30 j) ; documenter la rotation (changer `.env`,
`restart node`, ré-ouvrir la PWA — les clés VAPID inchangées préservent les abonnements) ;
n'imprimer que le chemin, l'utilisateur ajoute le token depuis `.env`.

### S8 — Divers (faible)

- `console.log("Recu:", msg)` journalise les images base64 sur stdout (bruit, taille).
- `/debug` (authentifié) permet une croissance illimitée de `messages.log`.
- `verifyClient` du WebSocket ne vérifie pas l'`Origin` (CSWSH déjà bloqué par
  `SameSite=Strict`, mais un contrôle d'`Origin` serait une défense en profondeur).
- `deviceId` fourni par le client dans `/push/subscribe` : un client authentifié peut purger
  les abonnements des autres appareils en rejouant un `deviceId`. Impact limité (DoS notif).
- `client.sleep` (2026-08-29) : tout client authentifié peut mettre le PC en veille (debounce
  5 s). Faible gravité (non destructif), mais à réserver au super-jeton propriétaire quand le
  multi-utilisateurs sera en place (cf. `analyse_acces_externe_marie_tsa.md`).

## Friction (ergonomie)

- **Token dans l'URL** : première ouverture obligatoire avec `?token=` ; si le cookie saute
  (vidage de cache, nouveau navigateur), il faut re-fournir l'URL complète. Tension
  sécurité/confort inhérente.
- **Révocation = redémarrage** : changer le token impose un `restart node` + ré-ouverture PWA.
- **`/roberto` à relancer** à chaque session de chaque projet (inhérent au modèle).
- **Écran d'accueil** : un tap obligatoire même pour un déploiement mono-projet.
- **Hallucinations STT** filtrées par liste en dur (`WHISPER_HALLUCINATIONS`) — fragile.

## Plan d'action proposé (par priorité)

1. S1 — token requis sur `/send` + `/push/test`, et rejet si en-têtes forwarded. (petit patch serveur + 1 ligne dans les commandes `/roberto`)
2. S2 — nettoyage `\r\n` de `msg.text` / `msg.caption` / `client.log`. (petit patch serveur)
3. S3 + S6 — assainir l'extension image, contrôle de taille serveur, `maxPayload` WS. (petit patch serveur)
4. S4 — décider : Piper par défaut, ou corriger le README. (décision utilisateur)
5. S7 — `Max-Age` réduit, `com_manager` n'imprime plus le token, doc rotation. (petit patch)
6. S5 + S8 — durcissements mineurs.

Aucune de ces corrections n'est bloquante pour l'usage actuel ; S1 et S2 sont les plus
importantes si le tunnel reste ouvert en permanence.
