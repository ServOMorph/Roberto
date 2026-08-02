# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Créer une application Windows locale de gestion de macros avec une UI HTML sombre, enregistrement/relecture fiables et validation visuelle des clics.

## Stack / contraintes techniques (stable, rarement modifié)
Python 3.13, PyWebView (UI HTML), pynput (entrées globales), MSS/OpenCV (captures et reconnaissance), pyperclip (prompts dynamiques). Windows multi-écrans ; UI placée sur la moitié gauche de l'écran le plus à gauche.

## État actuel (réécrit intégralement à chaque /close)
Pont OpenCode fiabilisé et éprouvé sur une roadmap fonctionnelle complète pour Ponganoid_v6 (`roadmap_10_niveaux_briques_bonus.md`, 6/6 phases [FAIT], 158 tests, validations réelles OK) menée de bout en bout par session automatisée `conversation_test.py`.
Protocole de prompt optimisé : plus d'écho du compte rendu du tour précédent ni de rappel explicite d'AGENTS.md (OpenCode conserve son propre historique et le lit seul) ; les phases de roadmap peuvent être formulées de façon resserrée sans perte de qualité une fois les conventions du projet établies.
`/stop_opencode` validé à 4 reprises en conditions réelles (reconstruction du `manifest.json`, nettoyage des flags). `conversation_test.py` s'arrête désormais automatiquement (statut `roadmap_terminee`) quand la roadmap active ne contient plus de phase `[EN COURS]`.
En attente : mode `--duration` non observé jusqu'à son terme naturel cette session (session menée avec `--turns` + arrêt manuel) ; fiabilité OCR sur des valeurs de contexte hors 7 %/50 % toujours en attente ; `VALIDATION_MANUELLE.md` de Ponganoid_v6 partiellement rempli.
Le lanceur principal reste `py run.py`.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-02 : Les scripts de workflow OpenCode peuvent refuser un envoi de prompt selon une zone OCR et un seuil de contexte (`--watch-zone`/`--watch-threshold`).
- 2026-08-02 : Avant toute relance de conversation_test.py/workflow_test.py (prise de contrôle machine vers OpenCode), inspecter l'état réel du projet cible (fichiers, roadmap) plutôt que supposer la continuité — aucune perte d'information tolérée. Échap interrompt la session en cours et journalise l'état pour reprise.
- 2026-08-02 : Quand une macro Macrodesk est recréée/réenregistrée, analyser son macro.json (events, contextes de vérification visuelle) avant de relancer un test — un clic avec image de référence sur un arrière-plan de chat qui évolue (historique) échoue quasi systématiquement ; le remplacement du clic « Envoyer » par un appui sur Entrée (sans vérification image) contourne ce problème.
- 2026-08-02 : Quand le seuil de contexte OCR est atteint, `conversation_test.py` envoie automatiquement `/compact` à OpenCode et attend sa confirmation écrite avant de renvoyer le prompt (`compact_opencode` dans `workflow_test.py`) — pas de blocage manuel à arbitrer à chaque fois.
- 2026-08-02 : `AGENTS.md` à la racine du projet cible centralise les règles fixes pour OpenCode (phase unique, contraintes, format de compte rendu) — le prompt de tour se limite au contexte dynamique, réduisant fortement sa taille sans perte d'exigence.
- 2026-08-02 : Correction de l'overlay de sélection de zone (déplacer le HWND toplevel Tk, pas le HWND enfant) et retrait de la vérification image sur les clics de la macro `OPENCODE-envoyer` — les deux causes de blocage récurrent du pont OpenCode.
- 2026-08-02 : Bannière de contrôle validée en conditions réelles (session `conversation_test.py` de 3 tours) : le code était déjà correct depuis la session précédente, le symptôme observé (bannière qui s'éteint après validation du prompt) venait d'une instance `py run.py` non redémarrée depuis la modification.
- 2026-08-02 : `conversation_test.py` limite la session par durée (`--duration`) plutôt que par nombre de tours fixe — arrêt de l'envoi de nouveaux tours après le délai, sans couper le tour en cours ; un arrêt forcé du process (hors Échap) contourne son `finally` et laisse les flags de contrôle actifs, d'où `/stop_opencode` pour nettoyer et journaliser manuellement.
- 2026-08-02 : Protocole de prompt de tour allégé (`prompt_for_turn`) : suppression de la mention explicite d'AGENTS.md (OpenCode le lit déjà seul, comme Claude Code avec CLAUDE.md) et de l'écho du compte rendu du tour précédent (jusqu'à 6000 caractères) — OpenCode conserve son propre historique de conversation entre les tours, ce rappel était une pure redondance de tokens. Aucune perte de qualité constatée sur 3 phases enchaînées après ce changement.
- 2026-08-02 : Les phases de roadmap destinées à OpenCode peuvent être formulées de façon très resserrée (directives courtes, sans sous-explications ni rappel de pattern) sans perte de qualité de résultat, une fois que le projet a déjà établi ses propres conventions de code sur les phases précédentes — testé sur les phases 5 et 6 de `roadmap_10_niveaux_briques_bonus.md`, résultat identique en rigueur aux phases 1-4 rédigées de façon détaillée.
- 2026-08-02 : `conversation_test.py` arrête désormais automatiquement la session (`roadmap_complete()`, statut `roadmap_terminee`) quand la roadmap active ne contient plus aucune phase `[EN COURS]` — évite d'envoyer des tours sans direction une fois le livrable atteint (constaté sur `roadmap_10_niveaux_briques_bonus.md`, 6/6 phases terminées).
