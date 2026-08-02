# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Créer une application Windows locale de gestion de macros avec une UI HTML sombre, enregistrement/relecture fiables et validation visuelle des clics.

## Stack / contraintes techniques (stable, rarement modifié)
Python 3.13, PyWebView (UI HTML), pynput (entrées globales), MSS/OpenCV (captures et reconnaissance), pyperclip (prompts dynamiques). Windows multi-écrans ; UI placée sur la moitié gauche de l'écran le plus à gauche.

## État actuel (réécrit intégralement à chaque /close)
Pont OpenCode fiabilisé : overlay de sélection de zone corrigé (multi-écrans, y compris l'écran de l'UI), vérification image retirée sur les clics fragiles de la macro `OPENCODE-envoyer`, blocage automatique + `/compact` + reprise quand le contexte OCR atteint le seuil (`compact_opencode`). Quatre sessions `conversation_test.py` consécutives réussies (12 tours au total, 0 échec macro).
Bannière de contrôle rouge clignotante (flags fichiers `mark_control_active`/`mark_session_active`) validée en conditions réelles après redémarrage de `py run.py` : reste affichée du premier clic jusqu'à la fin de la session, sur toute la durée des échanges avec OpenCode (pas seulement pendant la prise de contrôle souris/clavier). Test manuel retiré de `tests_manuels.md`.
`AGENTS.md`, ajouté dans le projet cible piloté par OpenCode, centralise les règles fixes et réduit fortement la taille des prompts de tour envoyés — validé (roadmap de test à 1 phase, 1 tour, succès).
En attente : fiabilité OCR sur d'autres valeurs de contexte que 7 %/50 % ; `ROADMAP_PATH` de `conversation_test.py` pointe encore vers une roadmap terminée.
Le lanceur principal reste `py run.py`.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-02 : Macrodesk utilise Python/PyWebView avec hooks globaux, validation OpenCV des clics et stockage local des macros.
- 2026-08-02 : Le contrôle d'OpenCode passe par le presse-papiers (`Ctrl+V`) et des réponses-fichiers afin de préserver une boucle agentique observable.
- 2026-08-02 : Ajout de zones de surveillance OCR (lecture du contexte OpenCode) avec sélection par overlay multi-écrans et pipeline OCR renforcé.
- 2026-08-02 : Les scripts de workflow OpenCode peuvent refuser un envoi de prompt selon une zone OCR et un seuil de contexte (`--watch-zone`/`--watch-threshold`).
- 2026-08-02 : Avant toute relance de conversation_test.py/workflow_test.py (prise de contrôle machine vers OpenCode), inspecter l'état réel du projet cible (fichiers, roadmap) plutôt que supposer la continuité — aucune perte d'information tolérée. Échap interrompt la session en cours et journalise l'état pour reprise.
- 2026-08-02 : Quand une macro Macrodesk est recréée/réenregistrée, analyser son macro.json (events, contextes de vérification visuelle) avant de relancer un test — un clic avec image de référence sur un arrière-plan de chat qui évolue (historique) échoue quasi systématiquement ; le remplacement du clic « Envoyer » par un appui sur Entrée (sans vérification image) contourne ce problème.
- 2026-08-02 : Quand le seuil de contexte OCR est atteint, `conversation_test.py` envoie automatiquement `/compact` à OpenCode et attend sa confirmation écrite avant de renvoyer le prompt (`compact_opencode` dans `workflow_test.py`) — pas de blocage manuel à arbitrer à chaque fois.
- 2026-08-02 : `AGENTS.md` à la racine du projet cible centralise les règles fixes pour OpenCode (phase unique, contraintes, format de compte rendu) — le prompt de tour se limite au contexte dynamique, réduisant fortement sa taille sans perte d'exigence.
- 2026-08-02 : Correction de l'overlay de sélection de zone (déplacer le HWND toplevel Tk, pas le HWND enfant) et retrait de la vérification image sur les clics de la macro `OPENCODE-envoyer` — les deux causes de blocage récurrent du pont OpenCode.
- 2026-08-02 : Bannière de contrôle validée en conditions réelles (session `conversation_test.py` de 3 tours) : le code était déjà correct depuis la session précédente, le symptôme observé (bannière qui s'éteint après validation du prompt) venait d'une instance `py run.py` non redémarrée depuis la modification.
