# Roadmap — Revue de code nocturne

## Objectif

Lancer une revue de code (`/code-review` niveau max) sur un projet cible, à une heure planifiée
par l'utilisateur (Windows ou `/schedule`, hors périmètre du code à écrire ici) ; générer une
roadmap de correctifs priorisée par urgence, écrite en langage simple, stockée dans
`<projet_cible>/ROBERTO/` ; discuter cette roadmap en voiture via com_telephone (validation ou
invalidation orale) ; puis, la nuit suivante, faire exécuter les correctifs validés par le
planificateur nocturne existant (`PLANIFICATEUR/`).

Créée le : 2026-09-04. Emplacement du code : à définir (probablement `Roberto/PLANIFICATEUR/`,
en réutilisant l'infrastructure existante).

---

## Cadrage acté (ne pas supprimer — survit aux /compact)

| Décision | Choix |
|---|---|
| Déclenchement | Pas d'overlay : commande/script que l'utilisateur planifie lui-même (Windows Task Scheduler ou `/schedule`) |
| Méthode d'analyse | `/code-review` niveau **max** (local, pas de confirmation interactive requise) |
| Cas exclu | Niveau `ultra` : cloud, facturé, confirmation interactive requise — ne peut pas être déclenché par une tâche planifiée automatique |
| Sortie | Un seul fichier `<projet_cible>/ROBERTO/roadmap_revue_<date>.md` |
| Format de la sortie | Langage simple, sans jargon technique, priorisé par urgence (P1/P2/P3) — pensé pour discussion vocale en voiture |
| Discussion | Vocale via com_telephone : lecture/discussion du fichier, validation ou invalidation par l'utilisateur |
| Exécution des correctifs | Nuit suivante : les points validés deviennent des tâches `queue.json` classiques, exécutées par l'orchestrateur du planificateur existant |
| Interface de lancement | Alias `.claude/zones.md` (racine Roberto, à enrichir au besoin) ou chemin absolu direct |
| Confinement | `claude -p "/code-review <niveau>" --restricted` (lecture seule + `Bash(git:*)`, jamais Write/Edit) ; la sortie brute est écrite par le script Python lui-même dans `<cible>/ROBERTO/`, jamais par le process `claude` |
| Coût sans surveillance | `--max-budget-usd` (défaut 5 $) — protège la fenêtre 5h partagée avec les autres tâches nocturnes, pas la facturation (utilisateur sous abonnement) |

### Points non résolus, assumés provisoirement

- Format précis de conversion « constat `/code-review` -> tâche `queue.json` » (Phase 2 -> Phase 4) :
  à définir en Phase 2.

---

## Phase 1 — Commande de lancement de l'analyse [EN COURS]

- [x] Script/commande unique (`PLANIFICATEUR/revue_code.py`) : résout la cible (alias
      `.claude/zones.md` ou chemin direct), lance `/code-review <niveau>` dessus, capture la
      sortie brute dans `<cible>/ROBERTO/`
- [ ] Invocable manuellement (fait, testé en réel) et par tâche planifiée Windows — `schtasks`
      non testé cette session
- [x] Confinement vérifié en réel sur Roberto : `git status` avant/après identique hors
      `<cible>/ROBERTO/`, aucune écriture du process `claude` lui-même (Read/Glob/Grep/
      `Bash(git:*)` uniquement, jamais Write/Edit)
- [x] Tests : 18 tests unitaires (`test_revue_code.py`), mockés — résolution de zones, construction
      de commande, écriture confinée. 3 défauts trouvés par le run réel dans `revue_code.py`
      lui-même (`--max-budget-usd` absent, `_tuer_arbre` non cross-platform, bug `charger_zones`
      sur la sous-chaîne "Alias"), corrigés et couverts par régression.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

---

## Phase 2 — Génération de la roadmap de review [TODO]

- [ ] Conversion des constats `/code-review` en fichier markdown unique, priorisé par urgence, en
      langage simple sans jargon technique
- [ ] Écriture dans `<projet_cible>/ROBERTO/roadmap_revue_<date>.md`
- [ ] Tests

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

---

## Phase 3 — Intégration com_telephone [TODO]

- [ ] Le fichier de roadmap de review devient consultable/discutable en voix
- [ ] Mécanisme de validation/invalidation orale des points par l'utilisateur
- [ ] Tests

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

---

## Phase 4 — Exécution nocturne des correctifs validés [TODO]

- [ ] Conversion des points validés en tâches `queue.json`
- [ ] Exécution par l'orchestrateur existant la nuit suivante
- [ ] Tests

---

## Risques

- Recoupement avec `roadmap_planificateur_nuit.md` (réutilisation de `orchestrateur.py`,
  `queue.json`) : les deux roadmaps peuvent se retrouver actives en même temps — arbitrage déjà
  signalé comme ouvert dans `signals.md` (P2), explicitement reporté par l'utilisateur le
  2026-09-04.
- Fichier de sortie unique servant à la fois de spec technique (Phase 4) et de support vocal
  (Phase 3) : risque de compromis si les deux usages tirent le format dans des directions
  différentes.
- `/code-review` niveau max lancé sans surveillance : confinement vérifié en réel sur Roberto
  (Phase 1, 2026-09-04). Reste à vérifier sur un déclenchement via tâche planifiée Windows réelle
  (`schtasks`), pas seulement en invocation manuelle.
