# Roadmap — Planificateur de tâches nocturnes

## Objectif

Exécuter automatiquement des tâches Claude Code pendant la nuit, sans supervision, en exploitant
les tokens restants de l'abonnement et en encaissant la limite glissante de 5 h (attente du reset
puis reprise). Un rapport HTML est généré et ouvert en fin de process.

Créée le : 2026-09-03. Emplacement du code : `Roberto/PLANIFICATEUR/`.

---

## Cadrage acté (ne pas supprimer — survit aux /compact)

| Décision | Choix |
|---|---|
| Projet cible MVP | `D:\ServOMorph\creazik_v2` (un seul projet pour commencer) |
| Portée | Liste blanche explicite de dossiers (`allowlist.txt`) |
| Confinement | Natif : `--restricted` + `--tools` + `--allowedTools`. Pas de hook maison en MVP |
| Limite 5 h atteinte | Attendre et reprendre (retry périodique), jusqu'au butoir |
| Heure butoir | 06:00 — aucune nouvelle tâche lancée au-delà |
| Rendu | `rapport_<date>.html`, charte VERTIA, lecture seule, ouvert en fin de process |
| Veille PC | Hors périmètre : déjà désactivée par l'utilisateur |
| Git | Branche dédiée par tâche, commit local, jamais de push |

### Commande type

```
cwd = <dossier de la tache>

claude -p "<prompt>"
  --restricted
  --tools "Read,Edit,Write,Glob,Grep,Bash"
  --allowedTools "Bash(git *) Bash(npm test) Bash(npm run typecheck)"
  --permission-prompts none
  --output-format json
  --model <sonnet|haiku|opus>
  --max-budget-usd <budget>
```

### Flags vérifiés dans `claude --help` (2026-09-03)

- `--restricted` : retire Bash/PowerShell/REPL/WebFetch sauf si `--tools` les nomme, confine les
  outils fichiers aux working directories (`--add-dir` inclus), refuse `bypassPermissions`,
  **ignore les settings user/project/local** (managed settings et `--settings` s'appliquent encore).
- `--permission-prompts none` : tout ce qui déclencherait une demande est refusé automatiquement.
- `--settings <file-or-json>` : seule voie pour injecter un hook en mode `--restricted`.
- `--max-budget-usd` : plafond par run, `--print` uniquement. Sémantique sous abonnement à valider.
- `--output-format json`, `--json-schema`, `--model`, `--fallback-model`, `--setting-sources`.
- `claude setup-token` : token d'authentification longue durée (requiert un abonnement).
- Pas de `--max-turns` dans l'aide ; `--max-budget-usd` joue ce rôle.

### Contraintes propres à creazik_v2

Electron + Vite + TypeScript, tests vitest, branche `main`.
Scripts npm : `dev`, `build`, `package`, `typecheck`, `test`, `test:watch`.
À ne jamais autoriser la nuit : `npm run dev` et `npm run test:watch` (ne rendent jamais la main,
figeraient l'orchestrateur), `npm run package` (electron-builder, long et lourd).

### Charte graphique VERTIA (source : `JeGeekUtile/VERTIA/site/styles.css`)

```
--bg #08110f   --surface #101e1a   --line #29443c
--text #d8e5df --muted #9ab1a7     --accent #7de7b8   --accent-dark #082117
Arial, sans-serif · titres line-height 1.05, letter-spacing -.045em · radius 4px
bouton : fond accent / texte accent-dark, hover fond transparent + texte accent
eyebrow : accent, uppercase, letter-spacing .12em, .78rem, 700
```

### Point non résolu, assumé

L'erreur de quota **n'est pas provocable à la demande** : impossible de la tester sans épuiser la
fenêtre. La MVP retente donc en aveugle et **archive intégralement stdout/stderr et l'exit code**
de chaque échec. Le parsing de l'heure de reset attend d'avoir observé le format réel (Phase 3).

### Acquis du spike (2026-09-03, sur creazik_v2, aucun fichier modifié)

Confinement effectif, vérifié en réel :
- `Write` vers `D:\ServOMorph\Roberto\...` depuis un run confiné à creazik_v2 : **refusé**.
- `curl` avec `--allowedTools "Bash(git status:*)"` : **refusé**, aucune surface d'approbation.
- Aucun fichier créé hors périmètre, `git status` de creazik_v2 resté vide.

Structure de la sortie `--output-format json` (champs utiles au rapport) :
`result`, `is_error`, `subtype`, `stop_reason`, `terminal_reason`, `total_cost_usd`,
`duration_ms`, `duration_api_ms`, `num_turns`, `session_id`, `usage`, `modelUsage`,
`api_error_status`, `permission_denials`.

**Piège majeur** : un run dont les outils ont été refusés rend `is_error: false` et
`subtype: "success"`. La tâche « réussit » sans rien produire. L'orchestrateur ne doit jamais
se fier à `is_error` seul — **inspecter `permission_denials`** (liste des appels refusés, avec
`tool_name` et `tool_input`) et le remonter dans le rapport.

`--max-budget-usd` fonctionne sous abonnement : dépassement -> `is_error: true`,
`subtype: "error_max_budget_usd"`, `terminal_reason: "budget_exhausted"`, `result` absent.
La coupure intervient en fin d'itération, pas au centime près (0.0067 dépensé pour un plafond
à 0.001) : prévoir une marge sur le budget par tâche.

Conséquence pour la Phase 3 : `subtype` et `terminal_reason` sont des codes machine, pas du
texte libre. L'erreur de quota aura vraisemblablement son propre code — c'est là qu'il faudra
regarder plutôt que de parser un message. Valeur exacte inconnue tant que la limite n'a pas été
atteinte en réel.

---

## Phase 1 — Spike de validation  [FAIT]

Valider empiriquement le confinement avant d'écrire l'orchestrateur.

- [x] Prompt trivial en lecture seule sur creazik_v2 : commande type OK, structure JSON relevée.
- [x] Tentative d'écriture hors du dossier autorisé : refusée.
- [x] Tentative de `git push` : refusée.
- [x] Comportement de `--max-budget-usd` sous abonnement : plafond effectif, code dédié.
- [ ] `claude setup-token` : mise en place du token longue durée (à la charge de l'utilisateur,
      cf. tests_manuels.md — interactif).

Gate : atteint. Refus effectifs, sortie JSON parsable, aucun fichier de creazik_v2 modifié.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

---

## Phase 2 — MVP  [FAIT]

```
Roberto/PLANIFICATEUR/
  allowlist.txt         dossiers autorises (un par ligne)
  queue.json            {id, dossier, prompt, modele, budget_usd, heure_min, timeout_min, ...}
  orchestrateur.py      boucle sequentielle, retry, butoir, reprise, timeout+kill, rapport, push
  rapport.py            generation du HTML (charte VERTIA)
  tache.py              CLI add/list/rm/reset (validation allowlist immediate)
  notifier.py           push du resume sur com_telephone
  lancer_nuit.cmd       point d'entree pour la tache planifiee
  logs/<id>_<n>.log     stdout/stderr bruts par tentative
  rapport_<date>.html
```

- [x] `allowlist.txt` + validation du dossier de chaque tâche avant lancement.
- [x] `queue.json` + statuts persistés à chaque transition (reprise après crash sans rejeu :
      tâche `en_cours` -> `echouee/interrompue`).
- [x] Orchestrateur séquentiel : une tâche à la fois, timeout wall-clock, kill de l'arbre, capture brute.
- [x] Retry périodique en cas d'échec quota (25 min), jusqu'au butoir 06:00.
- [x] Butoir : au-delà, tâches restantes marquées `reportee`, rapport écrit, fin.
- [x] Rapport HTML charte VERTIA : bandeau de synthèse + une ligne par tâche, ouverture auto.
      Un run avec `permission_denials` est classé `refus`, pas `faite`.
- [ ] Tâche Planificateur de tâches Windows : commande prête (tests_manuels.md), non créée
      (heure de coucher non fixée, modif système hors dépôt).
- [x] Tests : 36 tests (`test_planificateur.py`), tous verts. Validations réelles sur creazik_v2 :
      confinement, `git push` refusé, `npm run typecheck` autorisé, timeout+kill, push com_tel.

Gate : NON franchi. Exige une nuit réelle sur creazik_v2 avec 2-3 tâches, rapport lisible au
réveil (cf. tests_manuels.md « Nuit réelle »). Code et tests faits ; validation terrain en attente.
Tentative de test supervisé le 2026-09-04 (réveil de session programmé pour 21:00) abandonnée en
cours de route (utilisateur passé à d'autres sujets) — aucun lancement réel n'a eu lieu.

**⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.

---

## Phase 3 — Durcissement  [EN COURS]

- [ ] Parsing de l'heure de reset dans l'erreur de quota (bloqué : format non observé en réel ;
      `est_erreur_quota` fait la détection heuristique en attendant).
- [x] Timeout et kill fiabilisés par tâche (`_tuer_arbre`, `taskkill /T` sur Windows, testé).
- [x] CLI d'ajout de tâche dans la queue (`tache.py`).
- [ ] Hook `PreToolUse` via `--settings` si la liste blanche `--allowedTools` s'avère trop rigide
      (pas nécessaire à ce stade).
- [x] Push du rapport sur le téléphone via `com_telephone` (`notifier.py`, HTTP 200 réel).
- [ ] Ouverture à d'autres projets de la liste blanche (une ligne dans `allowlist.txt`).
- [x] Overlays plein écran (annonce au lancement, bilan à la fin) intégrés à `orchestrateur.py`
      (`overlay.py`, flag `--no-overlay`), testés visuellement et validés par l'utilisateur.

---

## Risques

- Les tâches nocturnes consomment la fenêtre de 5 h qui servira au réveil — d'où le butoir 06:00.
- Commande bloquante autorisée par erreur : fige l'orchestrateur. Parade : liste blanche stricte
  + timeout wall-clock.
- Expiration d'authentification en pleine nuit : parade `claude setup-token`.
- `--restricted` ignore les settings projet : un hook posé dans `.claude/settings.json` de la
  cible ne serait jamais chargé. Toujours passer par `--settings`.
- Exécution non supervisée : le confinement repose sur le harness, pas sur `CLAUDE.md`, qui n'est
  qu'une instruction au modèle et ne contraint rien.
