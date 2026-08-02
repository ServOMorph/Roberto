# Changelog

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
