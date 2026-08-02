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

## État actuel

Macrodesk est fonctionnel sur Windows : enregistrement/relecture multi-écrans, validation visuelle des clics, renommage de macros et option de ne pas enregistrer les mouvements souris. Le pont OpenCode a été validé sur un échange de deux tours et une conversation de dix tours.
