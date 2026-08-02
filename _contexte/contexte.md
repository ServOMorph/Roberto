# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Créer une application Windows locale de gestion de macros avec une UI HTML sombre, enregistrement/relecture fiables et validation visuelle des clics.

## Stack / contraintes techniques (stable, rarement modifié)
Python 3.13, PyWebView (UI HTML), pynput (entrées globales), MSS/OpenCV (captures et reconnaissance), pyperclip (prompts dynamiques). Windows multi-écrans ; UI placée sur la moitié gauche de l'écran le plus à gauche.

## État actuel (réécrit intégralement à chaque /close)
Projet restructuré en packages pour accueillir un second agent aux côtés d'OpenCode : `macrodesk/` (moteur, stores, OCR, écran, UI), `bridge/` (pont générique, agnostique de l'agent), `agents/` (un `AgentProfile` par agent — `context_metric` gère aussi bien un contexte affiché comme "consommé" que "restant"), `scripts/` (lancés par `py -m scripts.<nom>`), `tests/` (123 tests pytest). Seul le profil `opencode` existe ; aucun code écrit pour CLAUDECODE, uniquement le point d'extension.
Suite pytest écrite avant la refacto (80 tests, baseline verte), repointée sur la nouvelle arborescence sans changer les assertions, puis étendue (agents, importabilité) : 123 tests verts après refacto.
Scripts renommés : `workflow_test.py`→`scripts/workflow_check.py`, `conversation_test.py`→`scripts/conversation.py`, `context_watch_test.py`→`scripts/context_watch.py`, `ocr_reliability_test.py`→`scripts/ocr_reliability.py`. Zone vibecoding `OPENCODE/` déplacée dans `_zones/OPENCODE/` (alias `zones.md` inchangé).
En attente : aucun test manuel de la refacto encore passé (lancement UI, pont réel, session longue — 3 tests ajoutés à `tests_manuels.md`) ; mode `--duration` non observé jusqu'à son terme naturel ; fiabilité OCR hors 7 %/50 % toujours en attente ; `VALIDATION_MANUELLE.md` de Ponganoid_v6 partiellement rempli.
Le lanceur principal reste `py run.py`.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-02 : Correction de l'overlay de sélection de zone (déplacer le HWND toplevel Tk, pas le HWND enfant) et retrait de la vérification image sur les clics de la macro `OPENCODE-envoyer` — les deux causes de blocage récurrent du pont OpenCode.
- 2026-08-02 : Bannière de contrôle validée en conditions réelles (session `conversation_test.py` de 3 tours) : le code était déjà correct depuis la session précédente, le symptôme observé (bannière qui s'éteint après validation du prompt) venait d'une instance `py run.py` non redémarrée depuis la modification.
- 2026-08-02 : `conversation_test.py` limite la session par durée (`--duration`) plutôt que par nombre de tours fixe — arrêt de l'envoi de nouveaux tours après le délai, sans couper le tour en cours ; un arrêt forcé du process (hors Échap) contourne son `finally` et laisse les flags de contrôle actifs, d'où `/stop_opencode` pour nettoyer et journaliser manuellement.
- 2026-08-02 : Protocole de prompt de tour allégé (`prompt_for_turn`) : suppression de la mention explicite d'AGENTS.md et de l'écho du compte rendu du tour précédent — l'agent conserve son propre historique de conversation entre les tours, ce rappel était une pure redondance de tokens.
- 2026-08-02 : Les phases de roadmap destinées à l'agent peuvent être formulées de façon très resserrée (directives courtes, sans sous-explications ni rappel de pattern) sans perte de qualité de résultat, une fois que le projet a déjà établi ses propres conventions de code sur les phases précédentes.
- 2026-08-02 : `conversation_test.py` arrête désormais automatiquement la session (`roadmap_complete()`, statut `roadmap_terminee`) quand la roadmap active ne contient plus aucune phase `[EN COURS]` — évite d'envoyer des tours sans direction une fois le livrable atteint.
- 2026-08-02 : Refacto en packages pour accueillir un second agent (CLAUDECODE, à venir) : `AgentProfile` (`agents/base.py`) porte tout ce qui varie entre agents (macro d'envoi, zone OCR, sens de lecture du contexte, compactage) ; `bridge/` et `scripts/` restent génériques et acceptent `--agent <clé>`.
- 2026-08-02 : Avant toute refacto structurelle, écrire la suite de tests contre le code existant et faire tourner un baseline vert, puis ne modifier que le point d'adaptation entre tests et code (`tests/_compat.py`) pendant la refacto — garantit qu'aucune assertion n'a changé de sens en cours de route.
- 2026-08-02 : `MacroStore`/`ZoneStore` acceptent leur emplacement de fichiers en paramètre (au lieu d'une constante de module figée) — nécessaire pour les isoler en test et pour un futur usage multi-instance.
- 2026-08-02 : Ouverture/fermeture d'une session de contrôle machine (drapeau de session, écoute d'Échap, arrêt des listeners) factorisée dans `scripts.common.controlled_session()` — élimine la duplication entre les 4 scripts de pilotage.
