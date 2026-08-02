# Macrodesk

Application Windows locale pour enregistrer et rejouer des macros clavier/souris, avec validation visuelle avant chaque clic.

## Installation

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py run.py
```

L'application s'ouvre sur la moitié gauche de l'écran situé le plus à gauche du poste.

## Raccourcis globaux

- `F8` lance l'action active : l'enregistrement d'une nouvelle macro ou la lecture de la macro sélectionnée.
- `F9` arrête immédiatement l'enregistrement ou la lecture.

Les clics et frappes effectués dans la fenêtre Macrodesk sont ignorés par l'enregistrement.

La coche « Enregistrer les déplacements souris » permet de conserver ou non les mouvements du curseur. Même désactivée, les clics et la molette gardent leurs coordonnées et, pour les clics, leur contexte visuel.

## Sécurité de la lecture

Au moment de chaque clic enregistré, Macrodesk conserve une image du contexte visuel. À la lecture, il capture d'abord l'écran, recherche ce contexte près de la position attendue, et n'effectue le clic que si la correspondance est suffisamment fiable. En cas de doute, la lecture est arrêtée et le motif est affiché dans l'interface.

Les macros sont stockées localement dans `data/macros/`.

## Test avec OpenCode

Le workflow d'envoi de prompts par macro est décrit dans `WORKFLOW_OPENCODE.md`. Après avoir enregistré la macro `opencode-envoyer`, lancer `py workflow_test.py`.

## Zones de surveillance (OCR)

Une zone est un rectangle d'écran déclaré dans l'UI (bouton « + Nouvelle », tracé à la souris sur n'importe lequel des écrans). Macrodesk y lit un texte par OCR (Tesseract), utile par exemple pour surveiller le pourcentage de contexte affiché par OpenCode. Les zones sont stockées dans `data/zones.json`.

`workflow_test.py` et `conversation_test.py` acceptent `--watch-zone <nom> --watch-threshold <n>` : avant chaque envoi de prompt, la zone est relue et l'envoi est refusé si le seuil est atteint ou si la lecture est illisible. Si le seuil est atteint, un `/compact` est envoyé automatiquement à OpenCode et sa confirmation écrite attendue avant de reprendre l'envoi.

`conversation_test.py` accepte aussi `--duration <minutes>` : passé ce délai, plus aucun nouveau tour n'est envoyé (le tour en cours va jusqu'à son terme). Sans `--turns` explicite, `--duration` seul ne plafonne plus le nombre de tours. En cas d'arrêt forcé du process (hors Échap), la commande Claude Code `/stop_opencode` reconstruit le `manifest.json` manquant et nettoie les flags de contrôle laissés actifs.

Pendant toute prise de contrôle de la machine (macro ou session `workflow_test.py`/`conversation_test.py`), une bannière rouge clignotante s'affiche dans l'UI.

Le projet cible piloté par OpenCode peut définir un `AGENTS.md` à sa racine : les règles fixes (contraintes, format de compte rendu) y sont centralisées une fois pour toutes, et le prompt de chaque tour se limite au contexte dynamique.

## État actuel

Macrodesk est fonctionnel sur Windows : enregistrement/relecture multi-écrans, validation visuelle des clics, renommage de macros, option de ne pas enregistrer les mouvements souris, zones de surveillance OCR (overlay corrigé pour couvrir l'écran de l'UI elle-même) et bannière de contrôle. Le pont OpenCode a été fiabilisé (retrait de la vérification image sur les clics fragiles, `/compact` automatique au seuil de contexte) et validé sur plusieurs sessions consécutives de plusieurs tours sans échec de macro. `conversation_test.py` peut désormais limiter une session par durée (`--duration`) plutôt que par nombre de tours fixe ; ce mode reste à valider jusqu'à son terme.
