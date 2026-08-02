# Tests manuels

## Fiabilité de la lecture OCR de la zone de contexte
Avec OpenCode ouvert et visible, cliquer « Tester » sur la zone créée à plusieurs valeurs de
contexte différentes (ex : 10 %, 45 %, 80 %) et vérifier que le pourcentage affiché dans
l'alerte correspond exactement à celui affiché par OpenCode. (50 % déjà confirmé en conditions
réelles le 2026-08-02.)

## Lancement de l'UI après restructuration en packages
Lancer `py run.py` et vérifier : la fenêtre s'ouvre sur la moitié gauche de l'écran le plus à
gauche, la liste des macros et des zones existantes s'affiche, un enregistrement F8/F9 se
sauvegarde bien dans `data/macros/`, et le bouton « Tester » d'une zone renvoie un pourcentage.
Objectif : confirmer que le déplacement de `ui/` dans `macrodesk/ui/` et la découpe de `app.py`
n'ont rien cassé au démarrage.

## Pont vers OpenCode après restructuration
Avec OpenCode ouvert, lancer `py -m scripts.workflow_check` et vérifier que le test va à son
terme (`TEST PASSED`) et que le manifeste produit dans `_workflow_test/` contient bien le champ
`agent: "opencode"`. Objectif : confirmer que le renommage des scripts et le passage par le
profil d'agent n'ont pas altéré le comportement du pont.

## Session de conversation après restructuration
Lancer `py -m scripts.conversation --watch-zone OPENCODE_context --duration 5` sur une roadmap
comportant une phase `[EN COURS]`, et vérifier : la bannière de contrôle s'affiche, le manifeste
final est écrit avec `agent`, `status` et `turnsCompleted` cohérents. Objectif : confirmer que
`controlled_session()` nettoie bien les flags en sortie, y compris sur arrêt par Échap.
