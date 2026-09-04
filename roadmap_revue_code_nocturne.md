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

### Points non résolus, assumés provisoirement

- Interface exacte de la commande de lancement (paramètres : dossier cible, éventuellement projet
  nommé via `zones.md`) : à trancher en Phase 1.
- Confinement de `/code-review` niveau max quand lancé sans surveillance (comportement par défaut
  vs `--restricted` façon planificateur) : à vérifier en Phase 1.
- Format précis de conversion « constat `/code-review` -> tâche `queue.json` » (Phase 2 -> Phase 4) :
  à définir en Phase 2.

---

## Phase 1 — Commande de lancement de l'analyse [TODO]

- [ ] Script/commande unique : prend le dossier cible en paramètre, lance `/code-review` niveau
      max dessus, capture la sortie brute
- [ ] Invocable manuellement et par tâche planifiée Windows (ou `/schedule`) sans surveillance
- [ ] Confinement vérifié (pas d'écriture hors du dossier cible et de `<cible>/ROBERTO/`)
- [ ] Tests

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
- `/code-review` niveau max lancé sans surveillance : comportement de confinement (accès fichiers,
  outils) non vérifié — à valider en Phase 1 avant tout déploiement planifié.
