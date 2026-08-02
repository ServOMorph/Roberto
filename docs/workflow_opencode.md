# Workflow de test Macrodesk ↔ agent

Ce workflow utilise une macro pour envoyer des prompts variables à un agent (OpenCode aujourd'hui), puis attend ses réponses dans des fichiers du dossier partagé. Les fichiers de test sont créés dans `_workflow_test/` et ignorés par Git.

Tout ce qui est propre à un agent (nom de la macro d'envoi, zone OCR de contexte, commande de compactage) est décrit dans `agents/<nom>.py`. Les scripts de `scripts/` acceptent `--agent <clé>` et n'ont aucune connaissance directe de l'agent piloté.

## 1. Enregistrer la macro d'envoi

Ouvrir Macrodesk et l'agent côte à côte. Créer une macro nommée exactement comme le `send_macro` du profil (`opencode-envoyer` pour OpenCode).

1. Désactiver « Enregistrer les déplacements souris ».
2. Appuyer sur `F8`.
3. Cliquer dans la zone de chat de l'agent.
4. Presser `Ctrl+V` — ne pas écrire de prompt fixe.
5. Envoyer, de préférence par la touche Entrée : un clic avec vérification visuelle sur un fond de chat qui défile échoue quasi systématiquement.
6. Appuyer sur `F9`.

Laisser un texte quelconque dans le presse-papiers pendant cet enregistrement est suffisant. Lors des exécutions, le script y placera le prompt à envoyer.

> Si une macro a déjà été enregistrée, le bouton **Renommer** affiché directement à sa droite permet de la renommer. Redémarrer Macrodesk après toute mise à jour pour charger cette interface.

## 2. Lancer le test

Garder l'agent ouvert, visible et connecté à ce même dossier, puis lancer depuis la racine du projet :

```powershell
py -m scripts.workflow_check
```

Le test réalise deux tours :

1. L'agent reçoit une demande de créer un fichier témoin et d'écrire un premier compte rendu dans `_workflow_test/`.
2. Le workflow lit ce fichier et renvoie automatiquement une demande de vérification. L'agent écrit alors un verdict final dans un second fichier.

Chaque tour attend au plus 180 secondes. `F9` reste l'arrêt d'urgence pendant le lancement de la macro, `Échap` arrête toute la session.

## Résultat

Le script affiche `TEST PASSED` lorsque le fichier témoin contient exactement `macro bridge OK` et que le verdict final de l'agent contient `SUCCÈS`. Le manifeste JSON produit dans `_workflow_test/` contient les réponses complètes, la clé de l'agent piloté et le résultat.

## Scripts disponibles

| Script | Rôle |
|--------|------|
| `py -m scripts.workflow_check` | Test de bout en bout du pont, deux tours. |
| `py -m scripts.conversation` | Session longue : fait avancer une roadmap dans un projet cible. |
| `py -m scripts.context_watch` | Lecture OCR de la zone de contexte sur 3 échanges. |
| `py -m scripts.ocr_reliability` | Fiabilité de la lecture OCR sur 5 échanges. |

Options communes : `--agent <clé>`, `--watch-zone <nom>`, `--watch-threshold <n>`.

## Brancher un nouvel agent

1. Créer `agents/<nom>.py` exposant un `AgentProfile` nommé `PROFILE`.
2. L'ajouter au dictionnaire `_PROFILES` de `agents/__init__.py`.
3. Enregistrer la macro d'envoi et déclarer la zone OCR portant les noms du profil.

Si l'agent affiche le contexte **restant** plutôt que le contexte **consommé**, poser `context_metric=CONTEXT_REMAINING` : la comparaison au seuil s'inverse automatiquement.
