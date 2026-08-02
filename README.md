# Macrodesk

Application Windows locale pour enregistrer et rejouer des macros clavier/souris, avec validation visuelle avant chaque clic, et pont d'automatisation vers un agent de code.

## Installation

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py run.py
```

L'application s'ouvre sur la moitié gauche de l'écran situé le plus à gauche du poste.

## Structure

| Dossier | Contenu |
|---------|---------|
| `macrodesk/` | Application : moteur de macros, stores, OCR, capture d'écran, UI HTML. |
| `bridge/` | Pont générique Macrodesk ↔ agent, sans connaissance de l'agent piloté. |
| `agents/` | Un profil par agent (macro d'envoi, zone OCR, compactage). |
| `scripts/` | Scripts de pilotage, lancés par `py -m scripts.<nom>`. |
| `tests/` | Suite pytest, lancée par `py -m pytest`. |
| `docs/` | Documentation du workflow et du protocole. |
| `data/` | Macros et zones enregistrées (hors Git). |

## Raccourcis globaux

- `F8` lance l'action active : l'enregistrement d'une nouvelle macro ou la lecture de la macro sélectionnée.
- `F9` arrête immédiatement l'enregistrement ou la lecture.

Les clics et frappes effectués dans la fenêtre Macrodesk sont ignorés par l'enregistrement.

La coche « Enregistrer les déplacements souris » permet de conserver ou non les mouvements du curseur. Même désactivée, les clics et la molette gardent leurs coordonnées et, pour les clics, leur contexte visuel.

## Sécurité de la lecture

Au moment de chaque clic enregistré, Macrodesk conserve une image du contexte visuel. À la lecture, il capture d'abord l'écran, recherche ce contexte près de la position attendue, et n'effectue le clic que si la correspondance est suffisamment fiable. En cas de doute, la lecture est arrêtée et le motif est affiché dans l'interface.

Les macros sont stockées localement dans `data/macros/`.

## Pont vers un agent

Le workflow d'envoi de prompts par macro est décrit dans `docs/workflow_opencode.md`. Après avoir enregistré la macro d'envoi du profil de l'agent, lancer :

```powershell
py -m scripts.workflow_check
```

Chaque agent est décrit par un `AgentProfile` dans `agents/` : macro d'envoi, zone OCR de contexte, sens de lecture du pourcentage, commande et accusé de compactage. `bridge/` et `scripts/` ne connaissent que ce profil, ce qui permet d'ajouter un agent sans toucher au pont. Tous les scripts acceptent `--agent <clé>`.

## Zones de surveillance (OCR)

Une zone est un rectangle d'écran déclaré dans l'UI (bouton « + Nouvelle », tracé à la souris sur n'importe lequel des écrans). Macrodesk y lit un texte par OCR (Tesseract), utile par exemple pour surveiller le pourcentage de contexte affiché par l'agent. Les zones sont stockées dans `data/zones.json`.

Les scripts acceptent `--watch-zone <nom> --watch-threshold <n>` : avant chaque envoi de prompt, la zone est relue et l'envoi est refusé si le seuil est atteint ou si la lecture est illisible. Si le seuil est atteint, la commande de compactage du profil est envoyée automatiquement et sa confirmation écrite attendue avant de reprendre l'envoi.

`py -m scripts.conversation` accepte aussi `--duration <minutes>` : passé ce délai, plus aucun nouveau tour n'est envoyé (le tour en cours va jusqu'à son terme). Sans `--turns` explicite, `--duration` seul ne plafonne plus le nombre de tours. `--project` et `--roadmap` permettent de viser un autre projet cible que la valeur par défaut. En cas d'arrêt forcé du process (hors Échap), la commande Claude Code `/stop_opencode` reconstruit le `manifest.json` manquant et nettoie les flags de contrôle laissés actifs.

Pendant toute prise de contrôle de la machine (macro ou session de pont), une bannière rouge clignotante s'affiche dans l'UI.

Le projet cible piloté par l'agent peut définir un `AGENTS.md` à sa racine : les règles fixes (contraintes, format de compte rendu) y sont centralisées une fois pour toutes, et le prompt de chaque tour se limite au contexte dynamique.

## Tests

```powershell
py -m pytest
```

## État actuel

Macrodesk est fonctionnel sur Windows : enregistrement/relecture multi-écrans, validation visuelle des clics, renommage de macros, option de ne pas enregistrer les mouvements souris, zones de surveillance OCR (overlay corrigé pour couvrir l'écran de l'UI elle-même) et bannière de contrôle. Le pont a été fiabilisé et éprouvé de bout en bout sur une roadmap fonctionnelle complète pour Ponganoid_v6 (10 niveaux vs IA, briques centrales, bonus — 6/6 phases, 158 tests, validations réelles OK), pilotée en session automatisée. Le protocole de prompt de tour a été optimisé (plus d'écho du compte rendu précédent ni de rappel d'AGENTS.md) et la session s'arrête automatiquement quand la roadmap active est terminée. `/stop_opencode` est validé en conditions réelles ; le mode `--duration` reste à observer jusqu'à son terme naturel.

Le code a été restructuré en packages (`macrodesk/`, `bridge/`, `agents/`, `scripts/`) pour accueillir un second agent aux côtés d'OpenCode. Seul le profil OpenCode est implémenté à ce stade.
