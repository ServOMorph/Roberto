# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Créer une application Windows locale de gestion de macros avec une UI HTML sombre, enregistrement/relecture fiables et validation visuelle des clics.

## Stack / contraintes techniques (stable, rarement modifié)
Python 3.13, PyWebView (UI HTML), pynput (entrées globales), MSS/OpenCV (captures et reconnaissance), pyperclip (prompts dynamiques). Windows multi-écrans ; UI placée sur la moitié gauche de l'écran le plus à gauche.

## État actuel (réécrit intégralement à chaque /close)
Macrodesk gère macros (F8/F9) et zones de surveillance OCR, créées via un overlay couvrant les 3 écrans de l'utilisateur.
Le pipeline OCR (agrandissement, binarisation, whitelist, multi-PSM) lit fiablement un pourcentage stable (validé 6/6 sur 7 %).
`workflow_test.py`/`conversation_test.py` supportent `--watch-zone`/`--watch-threshold` pour bloquer un envoi si le contexte OCR dépasse le seuil ou est illisible.
En attente : fiabilité OCR sur d'autres valeurs de contexte et stabilité du clic de macro sur plusieurs tours (`tests_manuels.md`).
Le lanceur principal reste `py run.py`.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-02 : Initialisation du protocole vibecoding.
- 2026-08-02 : Macrodesk utilise Python/PyWebView avec hooks globaux, validation OpenCV des clics et stockage local des macros.
- 2026-08-02 : Le contrôle d'OpenCode passe par le presse-papiers (`Ctrl+V`) et des réponses-fichiers afin de préserver une boucle agentique observable.
- 2026-08-02 : Ajout de zones de surveillance OCR (lecture du contexte OpenCode) avec sélection par overlay multi-écrans et pipeline OCR renforcé.
- 2026-08-02 : Les scripts de workflow OpenCode peuvent refuser un envoi de prompt selon une zone OCR et un seuil de contexte (`--watch-zone`/`--watch-threshold`).
