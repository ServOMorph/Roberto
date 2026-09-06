# Signals — roberto   (MAJ 2026-09-05)

## Actions ouvertes
- [P1|ouvert] Nuit réelle du planificateur (déclenchée le 2026-09-04 à 21h00) : tâche `audit-deps`
  terminée en statut `refus` — l'outil `Write`, pourtant listé dans `outils` de la tâche et couvert
  par `--tools`, a été refusé au runtime (cause non investiguée cette session). Tâche `typecheck`
  (heure_min 01:00) restée `en_attente` dans `queue.json` ; état du process orchestrateur au-delà
  de 21h04 non vérifié. fait quand: cause du refus Write identifiée et corrigée (ou contournée),
  une nuit complète sans refus imprévu, rapport `rapport_<date>.html` lisible. réf:
  PLANIFICATEUR/queue.json (tâche audit-deps, historique), roadmap_planificateur_nuit.md
  (gate Phase 2)
- [P2|ouvert] Workflow de revue de code nocturne (`roadmap_revue_code_nocturne.md`) : Phase 1
  avancée — `PLANIFICATEUR/revue_code.py` créé (résolution cible via alias `.claude/zones.md` ou
  chemin direct, lance `claude -p "/code-review <niveau>" --restricted` en lecture seule +
  `Bash(git:*)`, jamais Write/Edit, écrit lui-même la sortie brute dans `<cible>/ROBERTO/`).
  18 tests unitaires + confinement vérifié en réel sur Roberto. Désaccord sur `--max-budget-usd`
  tranché le 2026-09-06 : conservé comme garde-fou de temps (protège la fenêtre 5h partagée), pas
  pour la facturation — tout affichage/calcul de coût (`cout_usd`, `total_cost_usd`) retiré du
  projet (workflow revue_code + infra planificateur nocturne). Reste : invocation via tâche
  planifiée Windows (schtasks) non testée. fait quand: schtasks testé et Phase 2 (génération de la
  roadmap de review) démarrée. réf: roadmap_revue_code_nocturne.md (Phase 1),
  PLANIFICATEUR/revue_code.py, PLANIFICATEUR/test_revue_code.py
- [P2|ouvert] Sélection automatique du projet à review créée cette session :
  `PLANIFICATEUR/selection_projet.py` (scan `.git`+`.claude` sur `C:\Users\raph6\Documents\ServOMorph`
  et `D:\ServOMorph`, seuil 90 jours, classement jamais-review d'abord), suivi structuré dans
  `PLANIFICATEUR/suivi_revues.json`, commande `.claude/commands/revue_projet.md` enchaînant
  sélection → confirmation → `revue_code.py` → enregistrement. Testé en réel pour la sélection
  seule (35 projets pertinents détectés) ; `/revue_projet` jamais invoquée de bout en bout
  (lancerait une vraie revue). SérénIATech_dev localisé hors des 2 racines scannées
  (`C:\Users\raph6\Documents\SerenIATech\SérénIATech_dev`) : ne sera jamais repris par la sélection
  tant que cette racine n'est pas ajoutée. fait quand: `/revue_projet` exécutée en réel sur un vrai
  projet (bilan produit, `suivi_revues.json` mis à jour), et décision prise sur l'ajout ou non de
  la racine SérénIATech_dev. réf: PLANIFICATEUR/selection_projet.py,
  PLANIFICATEUR/suivi_revues.json, .claude/commands/revue_projet.md
- [P3|ouvert] Piste creazik_v2 explicitement reportée par l'utilisateur ("à voir plus tard",
  reconfirmé le 2026-09-04) : proposition de découpler les gates de phase des tests manuels
  perceptuels (roadmap_impl.md) et d'ajouter un outil de validation automatisée façon IA_Life
  (`tools/run_manual_checks.py` etc., via Playwright sur l'app buildée). Rien acté, rien créé côté
  creazik_v2. fait quand: l'utilisateur relance le sujet et valide (ou écarte) la proposition.
  réf: creazik_v2/roadmap_impl.md, creazik_v2/tests_manuels.md, IA_Life/tools/ (pattern de
  référence)
- [P2|ouvert] Vérifier en réel que `git checkout -b` et `git commit` passent la liste blanche
  `--allowedTools "Bash(git:*)"` (non testé : seuls `git push` refusé et `npm run typecheck`
  autorisé l'ont été). fait quand: la tâche `typecheck` du queue.json d'exemple aboutit sans
  statut `refus`, ou la liste blanche est corrigée. réf: PLANIFICATEUR/orchestrateur.py
  (BASH_AUTORISE_DEFAUT), PLANIFICATEUR/logs/
- [P1|ouvert] Arbitrer les 3 roadmaps désormais `[EN COURS]` simultanément :
  `roadmap_planificateur_nuit.md` (Phase 3), `roadmap_ameliorations.md` (Phase 1, jamais démarrée),
  `roadmap_revue_code_nocturne.md` (Phase 1, script écrit et testé cette session). Les deux
  premières partagent `orchestrateur.py`/`queue.json` ; les trois se disputent la même fenêtre 5h.
  fait quand: une seule roadmap reste activement travaillée à la fois, les autres explicitement en
  pause ou closes. réf: roadmap_planificateur_nuit.md, roadmap_ameliorations.md,
  roadmap_revue_code_nocturne.md
- [P3|ouvert] Parsing de l'heure de reset de la limite 5 h. fait quand: le format réel a été
  observé dans un log de `PLANIFICATEUR/logs/` et le parsing est implémenté dans `classer_resultat`
  / `est_erreur_quota`. réf: roadmap_planificateur_nuit.md (Phase 3), PLANIFICATEUR/orchestrateur.py
- [P2|ouvert] `MACROS/` et `UI_WEB/` déplacés ici depuis `templates/roberto/` du kit
  (claude-vibecoding-kit) le 2026-08-29, à la demande de l'utilisateur (nettoyage du kit —
  ce template n'avait plus d'équivalent nulle part, sa source `D:\ServOMorph\Roberto2` a été
  supprimée). Launcher pywebview (lancement de programmes, macros clavier/souris, capture de
  coordonnées écran, communication OpenCode) jamais utilisé ni testé dans ce projet, fichiers
  déplacés tels quels (non commités). fait quand: fonctionnement vérifié dans ce projet
  (`python run.py`), décision prise sur son intégration (garder en l'état, fusionner avec
  `AUTOMATISATIONS/`/`com_telephone/`, ou écarter) et changements commités. réf: `MACROS/`,
  `UI_WEB/`, `run.py`
- [P2|ouvert] `roadmap_workflow_quotidien.md` déplacée ici depuis le kit le 2026-08-29 (Phases 1-2
  FAIT, Phases 3-5 TODO : score combiné priorité+envie, intégration dans `quotidien.md`, tests
  bout en bout) — non commitée, à reprendre dans le fil de travail normal de ce projet. réf:
  `roadmap_workflow_quotidien.md`
- [P1|ouvert] Valider en réel les notifications push, téléphone verrouillé, après re-souscription
  de la PWA. fait quand: l'utilisateur confirme réception fiable sur écran verrouillé (5 envois
  sur 5) et aucun doublon. réf: tests_manuels.md, com_telephone/voice-code-bridge/server/server.js
  (broadcastAndNotify, anyClientForeground), mobile/app.js (client.visible, seenMids, deviceId)
- [P2|ouvert] Valider le raccordement creazik_v2 de bout en bout. fait quand: une session Claude
  Code dans creazik_v2 lance /roberto et un aller-retour vocal fonctionne sur l'onglet PWA
  `creazik_v2`. réf: creazik_v2/ROBERTO/com_telephone/README.md,
  creazik_v2/.claude/commands/roberto.md
- [P2|ouvert] Décider S4 de l'audit : le TTS passe par edge_tts (cloud Microsoft) en premier,
  Piper en secours ; le README affirme l'inverse. fait quand: décision actée + code et README
  alignés (Piper par défaut, ou README corrigé). réf: com_telephone/_docs/audit_securite_2026-08-28.md
  (S4), com_telephone/voice-code-bridge/server/tts_server.py
- [P3|ouvert] Décider la voie pour l'accès externe de Marie au projet `tsa` (multi-utilisateurs
  dans le bridge, ou second bridge dédié). fait quand: voie choisie + 4 questions du doc tranchées.
  réf: com_telephone/_docs/analyse_acces_externe_marie_tsa.md
- [P3|ouvert] Traiter S5, S7, S8 de l'audit (check anti-traversée statique sans séparateur ;
  cycle de vie du token : cookie 1 an, token imprimé par com_manager, rotation non documentée ;
  divers, dont `client.sleep` à réserver au super-jeton). fait quand: chaque constat corrigé ou
  explicitement écarté. réf: com_telephone/_docs/audit_securite_2026-08-28.md
- [P3|ouvert] Décider la proposition des 3 agents de dev (Bridge / PWA / Déploiement-Ops).
  fait quand: validée (agent_role.md créés) ou rejetée. réf:
  com_telephone/_docs/agents_dev_proposition.md
- [P3|ouvert] Décider si SérénIATech_dev doit devenir une zone déclarée (`.claude/zones.md` +
  `_contexte/` dédié) plutôt qu'un traitement ad hoc via roberto — session 2026-09-05 y a appliqué
  3 correctifs (`routes_orga.py`) sans aucun suivi de zone. fait quand: décision actée (zone créée
  et `/start` fonctionnel dessus, ou traitement ad hoc confirmé durablement). réf: session du
  2026-09-05, `.claude/zones.md`

## Dernière session
<!-- Écrasé intégralement par /close. Synthèse < 25 lignes. -->
# Session du 2026-09-06

## Décisions prises
- Sélection automatique du projet à review : script autonome (`selection_projet.py`), pas intégré
  au planificateur nocturne ni à `revue_code.py` — choix explicite de l'utilisateur.
- Suivi des revues stocké en JSON structuré (`suivi_revues.json`), pas en Markdown.
- Critères de pertinence retenus : dépôt `.git` + `.claude/` présents, modifié il y a moins de
  90 jours (seuil ajustable).
- Coûts affichés/calculés retirés du projet (workflow revue_code + infra planificateur nocturne
  existante) ; `--max-budget-usd` gardé comme garde-fou de temps, pas pour la facturation —
  désaccord antérieur tranché.

## Livrables produits ou modifiés
- `PLANIFICATEUR/selection_projet.py` : créé, 14 tests (`test_selection_projet.py`)
- `PLANIFICATEUR/suivi_revues.json` : créé (Roberto + SérénIATech_dev)
- `.claude/commands/revue_projet.md` : créé (sélection -> confirmation -> revue -> suivi)
- `PLANIFICATEUR/orchestrateur.py`, `overlay.py`, `rapport.py`, `notifier.py`, `tache.py` : retrait
  de tout affichage/calcul de coût (`cout_usd`, `total_cost_usd`), `--max-budget-usd` conservé
- `test_planificateur.py` : adapté (68/68 tests passent)

## Hypothèses validées / invalidées
- VALIDE : `selection_projet.py` fonctionne en réel sur les 2 racines demandées (35 projets
  pertinents détectés)
- VALIDE : suite complète PLANIFICATEUR (68 tests) passe après retrait des coûts
- EN ATTENTE : `/revue_projet` jamais invoquée en réel (lancerait une vraie revue)

## Prochaine étape exacte
Tester `/revue_projet` en réel sur un vrai projet (ex. `Appli_TSA_SDI_TDAH`, en tête de liste),
vérifier le bilan produit et l'écriture dans `suivi_revues.json`.

## Question bloquante pour la session suivante
Aucune.
