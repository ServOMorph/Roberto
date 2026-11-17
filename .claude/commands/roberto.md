---
description: (Re)lance la surveillance du log ROBERTO pour la session Roberto (assistant vocal téléphone)
argument-hint: (aucun)
model: haiku
---

# /roberto

## Objectif

Roberto héberge le pont `com_telephone` et en est aussi un projet raccordé : l'onglet `Roberto`
de la PWA parle à une session Claude Code ouverte dans ce projet. Cette commande met (ou remet)
la session en écoute du log de messages propre à Roberto. Si le pont est arrêté, la commande le
démarre elle-même (étape 1).

Le tunnel n'est jamais lancé par Claude : c'est l'utilisateur qui le lance. Ne pas le démarrer,
ne pas proposer de le démarrer à sa place.

## Constantes

- Log surveillé :
  `D:\ServOMorph\Roberto\com_telephone\voice-code-bridge\server\logs\messages_roberto.log`
- Fichier de verrou :
  `D:\ServOMorph\Roberto\com_telephone\_commands\monitor_roberto.lock`

## Procédure

1. Vérifier que les 3 process du pont tournent :
   ```
   py -3.11 "D:\ServOMorph\Roberto\com_telephone\_commands\com_manager.py" status
   ```
   Si un process est `[KO]`, démarrer le pont sans demander de validation :
   1. Libérer le port 5000 (voir `com_telephone/_commands/com_manager.md`, étape 2) :
      ```
      netstat -ano | findstr :5000
      ```
      Si une ligne `LISTENING` donne un PID, contrôler son nom avec
      `tasklist /FI "PID eq <pid>"`. Si c'est `node.exe`, l'arrêter avec
      `taskkill /F /T /PID <pid>`. Si c'est un autre programme, ne pas le tuer : le signaler à
      l'utilisateur et s'arrêter.
   2. Lancer :
      ```
      py -3.11 "D:\ServOMorph\Roberto\com_telephone\_commands\com_manager.py" start
      ```
   3. Relancer `status`, puis donner à l'utilisateur la ligne `Lien appli : ...` affichée par
      `start` (10 à 20 secondes de chargement des modèles avant que le serveur soit utilisable).
   Le tunnel reste à lancer par l'utilisateur.

2. Se fier au fichier de verrou, jamais à la mémoire de la conversation :
   1. Si `monitor_roberto.lock` existe, lire le `task_id` et appeler `TaskStop` dessus (échec
      silencieux accepté). Ne pas sauter cette étape : deux Monitor = notifications en double.
   2. Lancer un nouveau Monitor :
      ```
      command: tail -f --retry -n 0 "D:/ServOMorph/Roberto/com_telephone/voice-code-bridge/server/logs/messages_roberto.log"
      persistent: true
      ```
   3. Écrire le `task_id` retourné dans `monitor_roberto.lock` (écrasant tout contenu précédent).

3. Confirmer à l'utilisateur que Roberto est en écoute (préciser : sélectionner `Roberto` dans
   l'appli téléphone).

## Répondre aux messages reçus

Tout message dans `messages_roberto.log` (ligne sans `[DEBUG]`) → réponse via
`POST http://127.0.0.1:5000/send`, corps JSON avec les clés `text` (non vide) et
`project` (`"roberto"`) — pas `message`, pas `body`. Sans `text` valide : HTTP 400. Un message
commençant par `!` est une commande directe : appliquer `.claude/commands/<nom>.md` de ce projet.
