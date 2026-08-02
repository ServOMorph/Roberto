# Signals — roberto (MAJ 2026-08-02)

## Dernière session (2026-08-02)

# Session du 2026-08-02

## Décisions prises
- Ajout de zones de surveillance OCR à Macrodesk pour lire le pourcentage de contexte affiché par OpenCode.
- Sélection de zone par overlay plein bureau virtuel (les 3 écrans), pas seulement l'écran principal.
- Arrêt volontaire du travail sur la fiabilité OCR après validation sur une seule valeur de contexte (7 %).

## Livrables produits ou modifiés
- `app.py` : `ZoneStore`, overlay de sélection multi-écrans (`select_zone_rectangle`), pipeline OCR renforcé (`read_zone_text`/`extract_percent`), API zones (créer/renommer/supprimer/tester).
- `ui/index.html`, `ui/app.js` : section « Zones de surveillance » (créer, tester, renommer, supprimer).
- `workflow_test.py`, `conversation_test.py` : options `--watch-zone`/`--watch-threshold`, arrêt d'envoi via `ContextLimitReached`.
- `context_watch_test.py`, `ocr_reliability_test.py` : scripts de test en conditions réelles avec OpenCode (exécutés).
- `requirements.txt` : ajout `pytesseract`, `Pillow`.
- `tests_manuels.md` : créé, 2 contrôles en attente.
- `.claude/memory.md` : créé, entrée sur le setup 3 écrans de l'utilisateur.

## Hypothèses validées / invalidées
- VALIDE : le pipeline OCR renforcé (agrandissement 4×, binarisation Otsu bidirectionnelle, whitelist, multi-PSM) lit correctement `7%` sur 6/6 lectures consécutives via `ocr_reliability_test.py`.
- INVALIDE : `-fullscreen` Tk suffit pour l'overlay de sélection de zone -> pivot vers positionnement explicite (`MoveWindow`) sur tout le bureau virtuel.
- EN ATTENTE : fiabilité OCR sur des valeurs de contexte autres que 7 % — le contexte OpenCode n'a pas varié pendant les tests. Reste dans `tests_manuels.md`.
- EN ATTENTE : stabilité du clic de la macro `opencode-envoyer` sur plusieurs tours consécutifs — un échec de reconnaissance visuelle observé lors du premier test à 3 échanges, cause non investiguée.

## Prochaine étape exacte
Reprendre `tests_manuels.md` quand le contexte OpenCode variera naturellement : valider la lecture OCR sur plusieurs pourcentages réels, puis la stabilité du clic de macro sur plusieurs tours.

## Question bloquante pour la session suivante
Aucune.
