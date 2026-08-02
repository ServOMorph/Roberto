# Changelog

## v0.7 — 2026-08-02

### Ajouté
- Package `agents/` : un `AgentProfile` décrit entièrement un agent pilotable (macro d'envoi, zone OCR de contexte, sens de lecture du pourcentage, commande et accusé de compactage). Registre dans `agents/__init__.py`, accès par `agents.get(<clé>)`. Seul le profil `opencode` est implémenté.
- Option `--agent <clé>` sur tous les scripts de pilotage ; options `--project` et `--roadmap` sur `scripts.conversation`.
- Suite de tests `tests/` (123 tests, `py -m pytest`) : OCR, touches, capture d'écran, stores, flags de contrôle, protocole de fichiers du pont, prompts, registre d'agents, importabilité de tous les modules.

### Modifié
- Restructuration complète en packages : `macrodesk/` (moteur, stores, OCR, écran, UI), `bridge/` (pont générique agnostique de l'agent), `agents/`, `scripts/`, `tests/`, `docs/`. La racine ne conserve que `run.py`, `ollama_call.py` et les fichiers de configuration.
- Scripts renommés et déplacés : `workflow_test.py` → `scripts/workflow_check.py`, `conversation_test.py` → `scripts/conversation.py`, `context_watch_test.py` → `scripts/context_watch.py`, `ocr_reliability_test.py` → `scripts/ocr_reliability.py`. Lancement par `py -m scripts.<nom>`.
- `compact_opencode()` devient `bridge.compact_agent()`, paramétré par le profil de l'agent.
- `MacroStore` et `ZoneStore` acceptent leur emplacement en paramètre ; `MacroStore.find_by_name()` remplace la recherche dupliquée dans les scripts.
- Ouverture et fermeture d'une session de contrôle factorisées dans `scripts.common.controlled_session()` (drapeau de session, écoute d'Échap, arrêt des listeners).
- `ui/` déplacé dans `macrodesk/ui/`, `WORKFLOW_OPENCODE.md` dans `docs/workflow_opencode.md`, `_docs/` fusionné dans `docs/`, zone vibecoding `OPENCODE/` déplacée dans `_zones/OPENCODE/` (alias `zones.md` inchangé).

## v0.6 — 2026-08-02

### Ajouté
- `conversation_test.py` : arrêt automatique de la session (`roadmap_complete()`, statut `roadmap_terminee`) quand la roadmap active ne contient plus de phase `[EN COURS]`.

### Modifié
- `conversation_test.py` : prompt de tour allégé (`prompt_for_turn`) — suppression du rappel d'AGENTS.md (lu seul par OpenCode) et de l'écho du compte rendu du tour précédent (redondant avec l'historique conservé par OpenCode).

### Corrigé
- `/stop_opencode` : validé en conditions réelles à 4 reprises (reconstruction du `manifest.json`, nettoyage des flags de contrôle).

## v0.5 — 2026-08-02

### Ajouté
- `conversation_test.py --duration <minutes>` : limite une session par durée plutôt que par nombre de tours fixe, sans couper le tour en cours d'OpenCode ; `--turns` devient illimité par défaut si utilisé seul avec `--duration`.
- Commande Claude Code `/stop_opencode` : arrête proprement une session `conversation_test.py`/`workflow_test.py` interrompue de force (reconstruction du `manifest.json`, nettoyage des flags de contrôle).

## v0.4 — 2026-08-02

### Corrigé
- Bannière de contrôle : validation en conditions réelles après redémarrage de `py run.py` (le code était déjà correct, la persistance de la bannière sur toute une session multi-tours était masquée par un process non redémarré).

## v0.3 — 2026-08-02

### Ajouté
- Bannière de contrôle rouge clignotante dans l'UI, affichée pendant toute prise de contrôle de la machine (flags `mark_control_active`/`mark_session_active`).
- `compact_opencode()` : envoi automatique de `/compact` à OpenCode et attente de confirmation écrite quand le seuil de contexte OCR est atteint, avant de reprendre l'envoi du prompt.
- Support d'un `AGENTS.md` à la racine du projet cible : règles fixes centralisées, prompt de tour réduit au contexte dynamique.

### Corrigé
- Overlay de sélection de zone qui se réduisait sur l'écran occupé par l'UI -> déplacement du HWND toplevel Tk (et non du HWND enfant), fonctionne désormais sur tout écran.
- Fragilité de la vérification image sur les clics de macro dans un chat au contenu changeant (`MATCH_THRESHOLD` abaissé, vérification retirée sur les clics concernés).

## v0.2 — 2026-08-02

### Ajouté
- Zones de surveillance OCR dans Macrodesk : sélection par overlay multi-écrans, lecture de pourcentage par Tesseract, gestion CRUD dans l'UI.
- Options `--watch-zone`/`--watch-threshold` dans `workflow_test.py` et `conversation_test.py` pour bloquer l'envoi d'un prompt si le contexte dépasse le seuil.
- Scripts `context_watch_test.py` et `ocr_reliability_test.py` pour valider le pont OpenCode et la fiabilité OCR en conditions réelles.

### Corrigé
- Overlay de sélection de zone limité à l'écran principal -> couvre désormais tout le bureau virtuel (3 écrans).
- Pipeline OCR peu fiable sur petites zones -> agrandissement, binarisation Otsu, liste de caractères restreinte, essai multi-PSM.

## v0.1 — 2026-08-02

### Ajouté
- Macrodesk : UI HTML sombre, enregistrement/relecture globale F8/F9, bibliothèque de macros et validation visuelle des clics.
- Pont OpenCode avec prompts collés par macro, réponses-fichiers, test de deux tours et conversation de dix tours.

### Corrigé
- Renommage directement accessible sur chaque macro.
- Normalisation de `Ctrl+V` pour les macros enregistrées sous Windows.
