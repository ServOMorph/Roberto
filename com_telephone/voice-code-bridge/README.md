# voice-code-bridge

Prototype d'assistant vocal distant pour Claude Code : PWA mobile (chat + capture vocale) connectée
en WebSocket à un serveur Node local, avec transcription (Whisper local) et synthèse vocale (Piper
local). Aucune donnée envoyée en cloud.

## Composants

- `mobile/` : PWA (HTML/JS statique), servie par le serveur Node.
- `server/server.js` : serveur HTTP + WebSocket (port 5000). Sert la PWA, relaie STT/TTS, journalise
  les échanges dans `server/messages.log`.
- `server/stt_server.py` : serveur Whisper local (`faster-whisper`, port 5001).
- `server/tts_server.py` : serveur Piper local (port 5002), nécessite le modèle de voix (voir plus bas).

## Installation

```bash
cd server
npm install
pip install faster-whisper piper-tts
```

Télécharger le modèle de voix Piper français (non versionné, ~63 Mo) :
```bash
mkdir voices
curl -L -o voices/fr_FR-siwis-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
curl -L -o voices/fr_FR-siwis-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
```

## Authentification

`node server.js` exige la variable d'environnement `AUTH_TOKEN` (le serveur refuse de démarrer
sans elle). Générer un jeton aléatoire, par exemple :

```bash
AUTH_TOKEN=$(openssl rand -hex 24)
export AUTH_TOKEN
```

## Lancement (3 processus séparés)

```bash
python stt_server.py      # port 5001
python tts_server.py      # port 5002
AUTH_TOKEN=... node server.js   # port 5000
```

Accès depuis le téléphone : exposer le port 5000 via un tunnel (Cloudflare Tunnel, Tailscale, etc.)
pour un accès hors LAN, puis ouvrir une première fois `https://<url-tunnel>/?token=<AUTH_TOKEN>`.
Le serveur pose un cookie de session ; les visites suivantes n'ont plus besoin du paramètre `token`
dans l'URL. `POST /send` (utilisé par l'agent Claude Code local) n'est accessible que depuis
`127.0.0.1`, indépendamment du jeton.

## Traitement des messages

Le serveur ne répond pas automatiquement. Le pont est multi-projets (`server/projects.json`) :
chaque message utilisateur est journalisé dans `server/logs/messages_<projet>.log` selon le champ
`project` envoyé par la PWA. Un agent Claude Code par projet surveille son propre log et répond via
`POST /send` (`{"text": "...", "project": "<id>"}` — `project` obligatoire, 400 sinon), qui
synthétise l'audio et le pousse au client connecté. `server/messages.log` (sans suffixe) ne reçoit
plus que les lignes `[DEBUG]`. Endpoint `GET /projects` : liste `[{id,label}]` pour la PWA.

Livraison : le message est poussé en WebSocket à tous les clients connectés **et** une notification
push est envoyée sauf si un client s'est signalé au premier plan (`client.visible`) dans les 8
dernières secondes — ceci couvre le cas iOS où l'onglet verrouillé garde un WebSocket zombie. Tant
qu'aucun client au premier plan n'a reçu le message, il est conservé et rejoué à la reconnexion ;
chaque message porte un `mid` pour que le client ignore les doublons (rejeu + push).

Abonnements push : la PWA envoie un `deviceId` stable (localStorage) avec l'abonnement ;
`POST /push/subscribe` supprime alors les abonnements du même `deviceId` (et les anciens sans
`deviceId`) pour éviter l'accumulation qui provoquait des notifications en double. `push_subs.json`
n'est pas versionné.

Pièces jointes : le bouton `img` de la PWA envoie une image (journalisée `[IMAGE] -> <chemin>`,
fichier dans `<racine-projet>/_docs/captures/`) ; le bouton `json` envoie un fichier JSON
(validé côté client et serveur, max 8 Mo, journalisé `[FICHIER] -> <chemin>`, fichier dans
`<racine-projet>/_docs/fichiers/`). L'agent lit le fichier au chemin indiqué dans le log.
