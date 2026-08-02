# Workflow de test Macrodesk ↔ OpenCode

Ce workflow utilise une macro pour envoyer des prompts variables à OpenCode, puis attend ses réponses dans des fichiers du dossier partagé. Les fichiers de test sont créés dans `_workflow_test/` et ignorés par Git.

## 1. Enregistrer la macro d'envoi

Ouvrir Macrodesk et OpenCode côte à côte. Créer une macro nommée exactement `opencode-envoyer`.

1. Désactiver « Enregistrer les déplacements souris ».
2. Appuyer sur `F8`.
3. Cliquer dans la zone de chat OpenCode.
4. Presser `Ctrl+V` — ne pas écrire de prompt fixe.
5. Cliquer le bouton d'envoi.
6. Appuyer sur `F9`.

Laisser un texte quelconque dans le presse-papiers pendant cet enregistrement est suffisant. Lors des exécutions, `workflow_test.py` y placera le prompt à envoyer.

> Si une macro a déjà été enregistrée, le bouton **Renommer** affiché directement à sa droite permet de l'appeler `opencode-envoyer`. Redémarrer Macrodesk après toute mise à jour pour charger cette interface.

## 2. Lancer le test

Garder OpenCode ouvert, visible et connecté à ce même dossier, puis lancer :

```powershell
py workflow_test.py
```

Le test réalise deux tours :

1. OpenCode reçoit une demande de créer un fichier témoin et d'écrire un premier compte rendu dans `_workflow_test/`.
2. Le workflow lit ce fichier et renvoie automatiquement une demande de vérification. OpenCode écrit alors un verdict final dans un second fichier.

Chaque tour attend au plus 180 secondes. `F9` reste l'arrêt d'urgence pendant le lancement de la macro.

## Résultat

Le script affiche `TEST PASSED` lorsque le fichier témoin contient exactement `macro bridge OK` et que le verdict final d'OpenCode contient `SUCCÈS`. Le manifeste JSON produit dans `_workflow_test/` contient les réponses complètes et le résultat.
