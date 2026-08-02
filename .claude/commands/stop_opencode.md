---
description: Arrête proprement le workflow de communication avec OpenCode (conversation_test.py / workflow_test.py) et journalise l'état pour une reprise ultérieure
argument-hint: [id de tâche de fond]
model: sonnet
allowed-tools: Bash(*), TaskOutput, TaskStop
---

# /stop_opencode [id de tâche de fond]

## Objectif
Arrêter une session `conversation_test.py` ou `workflow_test.py` en cours (prise de
contrôle machine vers OpenCode) sans perte d'information : contrairement à un arrêt via
Échap (qui déclenche le `finally` du script et journalise proprement), un arrêt externe
du process contourne ce nettoyage. Cette commande le fait manuellement à la place.

## Procédure

1. Identifier la session en cours :
   - Si un argument (id de tâche) est fourni ($ARGUMENTS), l'utiliser directement.
   - Sinon, lister les tâches de fond actives et repérer celle dont la commande contient
     `conversation_test.py` ou `workflow_test.py`.
   - Si aucune tâche de fond trouvée : vérifier tout de même l'état des flags
     (`data/control.flag`, `data/control_session.flag` sous `D:\ServOMorph\Roberto`) et le
     dossier de session le plus récent sans `manifest.json` — un process a pu mourir sans
     passer par cette commande. S'il n'y a ni tâche, ni flag actif, ni session non
     journalisée : répondre "Aucun workflow OpenCode actif détecté." et s'arrêter.

2. Arrêter le process :
   - Si une tâche de fond a été identifiée, l'arrêter (`TaskStop`).
   - Ne jamais tuer un process qui ne correspond pas explicitement à
     `conversation_test.py` ou `workflow_test.py`.

3. Reconstituer l'état de la session interrompue :
   - **Cas `conversation_test.py`** (dossier `D:\ServOMorph\Ponganoid_v6\_ROBERTO\conversations\`) :
     repérer le sous-dossier `session-<horodatage>` le plus récent sans `manifest.json`.
     Lister les paires `prompt-NN.md` / `reponse-NN.md` ; un tour ne compte comme complété
     que si `reponse-NN.md` existe et n'est pas vide. Écrire `manifest.json` avec :
     `status: "interrompu_manuel"`, `project`, `roadmap` (lus dans `prompt-01.md` ou
     déduits du script), `turnsCompleted`, `responses` (liste `{turn, response}`),
     `turnInterrompu` (numéro du prompt sans réponse correspondante, s'il y en a un).
   - **Cas `workflow_test.py`** (dossier `D:\ServOMorph\Roberto\_workflow_test\`) :
     repérer le `*-manifest.json` le plus récent dont `status` vaut encore `"started"` et
     le mettre à jour avec `status: "interrompu_manuel"`.
   - Si aucune session non journalisée n'est trouvée (le script avait déjà écrit son
     manifeste final avant l'arrêt) : passer à l'étape suivante sans rien écrire.

4. Nettoyer les flags de contrôle :
   - Vérifier `data/control.flag` et `data/control_session.flag`.
   - Les supprimer uniquement si aucune tâche de fond légitime (étape 1) ne tourne encore
     — ne jamais les supprimer si une autre session Macrodesk est réellement active.

5. Rapport final (concis) :
   - Dossier de session concerné et fichier `manifest.json` écrit ou déjà présent.
   - Nombre de tours complétés, tour interrompu le cas échéant.
   - État des flags de contrôle (nettoyés / déjà propres / laissés actifs et pourquoi).
   - Rappel explicite : pour reprendre, relire la roadmap correspondante (phase `[EN COURS]`
     réelle) avant toute relance — ne jamais supposer la continuité.

<!-- SPECIFICITES PROJET : DEBUT (préservé par /update, ne pas toucher hors de ce bloc) -->
<!-- Convention : toute règle liée à une étape précise de la Procédure ci-dessus doit la
     référencer explicitement par son numéro (ex: "Étape 3 : ..."), plutôt que compter sur la
     position physique de cette zone (toujours en fin de fichier). -->
<!-- SPECIFICITES PROJET : FIN -->
