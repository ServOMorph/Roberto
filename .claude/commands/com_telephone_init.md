---
description: Installe com_telephone dans un projet cible (raccorde au pont Roberto, ou copie autonome)
argument-hint: <projet-cible> <raccorde|autonome>
model: sonnet
---

# /com_telephone_init <projet-cible> <mode>

Installe l'assistant vocal `com_telephone` dans un projet cible, depuis Roberto (projet hôte et
template de référence). Deux modes :

- **`raccorde`** : le projet utilise le pont partagé hébergé par Roberto. Aucune copie du serveur —
  juste un README, une commande `/roberto`, une entrée dans le registre du pont, la section
  CLAUDE.md. C'est le mode par défaut recommandé pour un projet sur la même machine.
- **`autonome`** : copie complète et indépendante du serveur (modèle `creazik_v2`). Nécessite ses
  propres ports, son `.env` (AUTH_TOKEN, TUNNEL_URL, VAPID), son `npm install`. À réserver aux
  projets qui doivent tourner sans dépendre du pont Roberto.

## Constantes (pont hôte Roberto)

- Racine hôte : `D:\ServOMorph\Roberto\com_telephone\`
- Template : `D:\ServOMorph\Roberto\com_telephone\voice-code-bridge\`
- Registre : `D:\ServOMorph\Roberto\com_telephone\voice-code-bridge\server\projects.json`
- Registre des déploiements : `D:\ServOMorph\Roberto\com_telephone\DEPLOYMENTS.md`
- `com_manager.py` : `D:\ServOMorph\Roberto\com_telephone\_commands\com_manager.py`

## Étape 0 — Résolution et garde-fous

1. Lire `$ARGUMENTS` : 1er mot = `<projet-cible>`, 2e mot = `<mode>` (`raccorde` par défaut si absent).
   Mode inconnu → s'arrêter, lister `raccorde | autonome`.
2. Résoudre `<projet-cible>` en chemin absolu :
   - chercher `D:\ServOMorph\<projet-cible>` puis
     `C:\Users\raph6\Documents\ServOMorph\<projet-cible>` (cf. `D:\ServOMorph\PROJETS.md`).
   - Introuvable → s'arrêter, demander le chemin exact.
3. `id` du projet : proposer `slug(<nom-dossier>)` (minuscules, non alphanumérique → `_`).
   Si le pont Roberto tourne, confirmer `id` + `label` (nom lisible) via `POST /send`
   (`project: <id-d-une-session-active>`, options courtes). Sinon demander en terminal.
   Refuser un `id` déjà présent dans `projects.json`.
4. Si `<cible>\ROBERTO\` existe et contient déjà du contenu ServOMorph : l'**analyser**, ne jamais
   le vider ; ajouter `com_telephone/` à côté.

## Mode `raccorde`

1. Créer `<cible>\ROBERTO\com_telephone\_commands\`.
2. Écrire `<cible>\ROBERTO\com_telephone\_commands\.gitignore` :
   ```
   *.pid
   monitor.lock
   monitor_<id>.lock
   ```
3. Écrire `<cible>\ROBERTO\com_telephone\README.md` à partir du modèle raccordé
   (`D:\ServOMorph\IA_Life\ROBERTO\com_telephone\README.md` est la référence à jour) : remplacer
   `IA_Life` / `ia_life` par le nom et l'`id` de la cible, garder les chemins pointant vers Roberto.
4. Ajouter une entrée à `projects.json` du pont Roberto :
   ```json
   {
     "id": "<id>",
     "label": "<label>",
     "racine": "<chemin-cible-en-slash>",
     "log": "logs/messages_<id>.log",
     "captures": "<chemin-cible-en-slash>/_docs/captures"
   }
   ```
5. Écrire `<cible>\.claude\commands\roberto.md` à partir de
   `D:\ServOMorph\IA_Life\.claude\commands\roberto.md` : remplacer `IA_Life` / `ia_life` par le nom
   et l'`id` de la cible (le log surveillé reste `...\Roberto\...\logs\messages_<id>.log`, le verrou
   devient `monitor_<id>.lock`).
6. Ajouter la section « Bridge ROBERTO (assistant vocal téléphone, raccordé) » à
   `<cible>\.claude\CLAUDE.md`, sous « Spécificités projet », en reprenant celle d'IA_Life adaptée
   à l'`id`. Si le fichier n'a pas de section « Spécificités projet », l'ajouter en fin de fichier.
7. Ajouter une ligne à `DEPLOYMENTS.md` (Roberto) : `| v0.x | <nom> | <chemin> | raccordé au pont Roberto | <date> |`.
8. Recharger le registre du pont : si les 3 process tournent,
   `py -3.11 "D:\ServOMorph\Roberto\com_telephone\_commands\com_manager.py" restart node`
   (server.js lit `projects.json` au démarrage). Sinon rien, ce sera pris au prochain `start`.
9. Test bout-en-bout : envoyer un message WS de test avec `project: <id>` et vérifier qu'il arrive
   dans `logs/messages_<id>.log` du pont Roberto ; `POST /send` avec `project: <id>` → 200.
10. Dire à l'utilisateur : ouvrir une session Claude Code dans `<cible>`, lancer `/roberto`, puis
    sélectionner le projet dans la PWA.

## Mode `autonome`

1. Créer `<cible>\ROBERTO\com_telephone\`.
2. Copier depuis le template Roberto : `voice-code-bridge/` (server + mobile ; `node_modules/`,
   `voices/`, `.env`, `messages.log`, `logs/`, `projects.json`, `push_subs.json` **exclus**),
   `_commands/com_manager.py`, `_commands/com_manager.md`, `_commands/com_stop.md`,
   `_commands/.gitignore`, `README.md`, `voice-code-bridge/README.md`, `DEPLOYMENTS.md`,
   `specification_assistant_vocal_claude_code.pdf`.
3. Copier `voice-code-bridge/server/voices/` (modèles Piper) depuis le template Roberto.
4. `npm install` dans `<cible>\ROBERTO\com_telephone\voice-code-bridge\server\`.
5. Écrire `<cible>\...\server\.env` :
   ```
   AUTH_TOKEN=<nouveau : py -c "import secrets;print(secrets.token_hex(24))">
   TUNNEL_URL=<a completer par l'utilisateur>
   PORT=5100
   STT_PORT=5101
   TTS_PORT=5102
   VAPID_PUBLIC=<a completer : npx web-push generate-vapid-keys>
   VAPID_PRIVATE=<a completer>
   ```
   Ports différents de 5000/5001/5002 si le pont Roberto tourne sur la même machine.
6. Écrire `<cible>\...\server\projects.json` : une seule entrée pour la cible
   (`id`, `label`, `racine`, `log: "logs/messages_<id>.log"`, `captures`).
7. Ajouter une ligne à `DEPLOYMENTS.md` (Roberto) : `| v0.x | <nom> | <chemin> | copie autonome | <date> |`.
8. Dire à l'utilisateur ce qu'il reste à faire : compléter `.env` (TUNNEL_URL, VAPID), vérifier les
   ports, `py -3.11 _commands\com_manager.py start`, ouvrir le lien appli affiché.

## Rappels

- Ne jamais mettre de secret en dur : `.env` hors git, généré, complété par l'utilisateur.
- `projects.json`, `logs/`, `.env`, `voices/`, `push_subs.json`, `node_modules/` : non versionnés
  (cf. `voice-code-bridge/.gitignore`).
- Après un `raccorde`, commiter côté Roberto (`projects.example.json` inchangé, `DEPLOYMENTS.md`),
  côté cible (`ROBERTO/com_telephone/`, `.claude/`). `projects.json` du pont n'est pas versionné.
