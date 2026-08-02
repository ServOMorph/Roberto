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

`workflow_test.py` et `conversation_test.py` acceptent `--watch-zone <nom> --watch-threshold <n>` : avant chaque envoi de prompt, la zone est relue et l'envoi est refusé si le seuil est atteint ou si la lecture est illisible.

## État actuel

Macrodesk est fonctionnel sur Windows : enregistrement/relecture multi-écrans, validation visuelle des clics, renommage de macros, option de ne pas enregistrer les mouvements souris, et zones de surveillance OCR. Le pont OpenCode a été validé sur un échange de deux tours, une conversation de dix tours, et un contrôle de fiabilité OCR sur cinq échanges.
