# Signals — roberto (MAJ 2026-08-02)

## Dernière session (2026-08-02)

# Session du 2026-08-02

## Décisions prises
- Application Windows locale en Python, UI HTML sombre à gauche et macros globales F8/F9.
- Les clics rejoués exigent une reconnaissance visuelle du contexte avant d'être exécutés.
- Le pont OpenCode utilise une macro `Ctrl+V` et des réponses-fichiers dans `_workflow_test/`.

## Livrables produits ou modifiés
- Macrodesk : enregistrement/relecture clavier-souris, bibliothèque et renommage fiable.
- `workflow_test.py` : test de deux échanges avec OpenCode.
- `conversation_test.py` : conversation validée de 10 échanges autour d'un script Python.

## Hypothèses validées / invalidées
- VALIDE : la macro `opencode-envoyer` injecte des prompts et déclenche l'envoi correctement.
- VALIDE : OpenCode écrit les réponses attendues dans le dossier partagé ; 10/10 tours réussis.
- INVALIDE : le caractère de contrôle Windows brut suffit pour `Ctrl+V` -> normalisation vers `v` ajoutée.

## Prochaine étape exacte
Utiliser `py run.py` pour les macros courantes, ou relancer les scripts de workflow avec OpenCode ouvert et visible.

## Question bloquante pour la session suivante
Aucune.
