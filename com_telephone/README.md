# com_telephone

## Objectif
Assistant vocal distant pour Claude Code : dialoguer par la voix depuis un téléphone avec une
session Claude Code tournant sur le PC, sans clavier ni intervention manuelle côté PC pendant la
conversation. Prototype construit à partir de `specification_assistant_vocal_claude_code.pdf`.

## Structure
- `specification_assistant_vocal_claude_code.pdf` : spécification fonctionnelle et technique d'origine.
- `voice-code-bridge/` : implémentation — PWA mobile (chat + écran d'écoute vocale), serveur Node
  (HTTP + WebSocket), STT Whisper local, TTS Piper local. Voir `voice-code-bridge/README.md` pour
  l'installation et le détail des composants.
- `_commands/` : `com_manager.py` (+ `com_manager.md`, commande Claude Code) pour démarrer/arrêter/
  vérifier les 3 processus serveur en une seule commande, avec activation automatique de la
  surveillance du fichier d'échange (`messages.log`).

## Fonctionnement
Le téléphone ouvre la PWA (accès distant via un tunnel déjà configuré côté utilisateur — Cloudflare
Tunnel, Tailscale, etc.), écrit ou parle un message. Le serveur journalise chaque message dans
`voice-code-bridge/server/messages.log`. Un agent Claude Code surveille ce fichier en continu et
répond via `POST /send` (texte + audio synthétisé), renvoyé au téléphone et lu automatiquement — le
tout en boucle conversationnelle continue (écoute → réponse → réécoute).

## Lancement rapide
```
python _commands/com_manager.py start
```
Démarre les 3 processus (STT, TTS, puis Node) et active la surveillance de `messages.log`.

## Règle absolue : deux canaux distincts
La conversation Claude Code (terminal/IDE) et l'appli téléphone sont deux canaux séparés. Répondre
dans l'un ne transmet rien à l'autre. Dès qu'un message vient de `messages.log` (donc du téléphone),
la réponse doit systématiquement passer aussi par `POST /send` — même si elle est déjà écrite dans
la conversation Claude Code. Oubli déjà constaté le 2026-08-24 (correctif scroll répondu uniquement
dans Claude Code, jamais reçu côté téléphone).

## Style des réponses (POST /send)
L'utilisateur écoute la réponse (TTS), il ne la lit pas. Chaque message envoyé via `POST /send`
doit être reformulé pour l'oral, pas recopié depuis un fichier ou un résultat d'outil :
- Une idée à la fois, phrases courtes.
- Aucune info superflue (chemins de fichiers, formatage markdown, listes à puces brutes,
  détails techniques non demandés).
- Si plusieurs éléments à annoncer, les résumer en une phrase de synthèse plutôt que tout lister.

## État
Fonctionnel de bout en bout, testé en conditions réelles (iPhone/Safari). Pas d'authentification sur
l'UI à ce stade — ne pas exposer durablement sans en ajouter une.
