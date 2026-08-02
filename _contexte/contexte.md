# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Créer une application Windows locale de gestion de macros avec une UI HTML sombre, enregistrement/relecture fiables et validation visuelle des clics.

## Stack / contraintes techniques (stable, rarement modifié)
Python 3.13, PyWebView (UI HTML), pynput (entrées globales), MSS/OpenCV (captures et reconnaissance), pyperclip (prompts dynamiques). Windows multi-écrans ; UI placée sur la moitié gauche de l'écran le plus à gauche.

## État actuel (réécrit intégralement à chaque /close)
Macrodesk est opérationnel avec F8/F9, bibliothèque de macros, renommage et choix d'enregistrer ou non les déplacements souris.
Chaque clic est contrôlé par contexte visuel et coordonnées avant lecture.
Le workflow OpenCode a réussi un test de 2 tours et une conversation de 10 tours, dans `_workflow_test/` ignoré par Git.
Le lanceur principal est `py run.py`.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-02 : Initialisation du protocole vibecoding.
- 2026-08-02 : Macrodesk utilise Python/PyWebView avec hooks globaux, validation OpenCV des clics et stockage local des macros.
- 2026-08-02 : Le contrôle d'OpenCode passe par le presse-papiers (`Ctrl+V`) et des réponses-fichiers afin de préserver une boucle agentique observable.
