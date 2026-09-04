# Signals — roberto   (MAJ 2026-09-04)

## Actions ouvertes
- [P1|ouvert] Première nuit réelle du planificateur : wakeup automatique programmé ce soir pour
  21h00 (heure Windows), en attente de déclenchement au moment du close (dernière vérif 20h56) —
  lancera seul `lancer_nuit.cmd` puis surveillera l'exécution. fait quand: une nuit réelle s'est
  exécutée, rapport `PLANIFICATEUR/rapport_<date>.html` lisible au réveil, aucun `git push`,
  commits uniquement locaux sur branches dédiées. réf: roadmap_planificateur_nuit.md (gate
  Phase 2), tests_manuels.md, PLANIFICATEUR/queue.json
- [P2|ouvert] Workflow de revue de code nocturne : spécifié dans `roadmap_revue_code_nocturne.md`
  (4 phases — abandon de l'overlay/déclenchement custom, remplacé par `/code-review` niveau max
  déclenché par une tâche planifiée que l'utilisateur configure lui-même ; sortie unique dans
  `<cible>/ROBERTO/`, discussion vocale via com_telephone, correctifs exécutés la nuit suivante
  par le planificateur). Reste à trancher avant tout code : interface de la commande de lancement
  (chemin en dur vs nom de projet via `zones.md`) et vérification du confinement de `/code-review`
  sans surveillance. fait quand: Phase 1 de `roadmap_revue_code_nocturne.md` implémentée et
  testée. réf: roadmap_revue_code_nocturne.md (Phase 1, section « Points non résolus »)
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
- [P2|ouvert] Arbitrer les roadmaps avec un statut `[EN COURS]` simultané :
  `roadmap_planificateur_nuit.md` (Phase 3) et `roadmap_ameliorations.md` (Phase 1, jamais
  démarrée). Un 3e chantier (`roadmap_revue_code_nocturne.md`) partage la même infrastructure
  (`orchestrateur.py`, `queue.json`) mais n'a encore aucune phase `[EN COURS]`. fait quand: une
  seule des deux reste `[EN COURS]`, l'autre est mise en pause explicite ou close. réf:
  roadmap_planificateur_nuit.md, roadmap_ameliorations.md, roadmap_revue_code_nocturne.md
  (Risques)
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

## Dernière session
<!-- Écrasé intégralement par /close. Synthèse < 25 lignes. -->
# Session du 2026-09-04

## Décisions prises
- Workflow de revue de code nocturne repensé : abandon de l'overlay/déclenchement custom,
  remplacé par `/code-review` niveau max (jamais `ultra`, qui exige une confirmation interactive).
- Déclenchement confié à l'utilisateur (planification Windows ou `/schedule`), pas de code de
  trigger à écrire côté Roberto.
- Reste du workflow conservé : sortie unique dans `<cible>/ROBERTO/`, discussion vocale via
  com_telephone, correctifs exécutés la nuit suivante par le planificateur.
- Piste creazik_v2 reconfirmée reportée par l'utilisateur.
- Test réel du planificateur nocturne reprogrammé ce soir à 21h00 (wakeup automatique en attente).

## Livrables produits ou modifiés
- `roadmap_revue_code_nocturne.md` : créé, puis réécrit (4 phases : Commande de lancement,
  Génération roadmap, com_telephone, Exécution nocturne des correctifs).

## Hypothèses validées / invalidées
- EN ATTENTE : interface exacte de la commande de lancement de `/code-review` (Phase 1).
- EN ATTENTE : confinement de `/code-review` niveau max lancé sans surveillance, non vérifié.
- EN ATTENTE : wakeup 21h00 pour le test réel du planificateur nocturne — actif, pas encore
  déclenché au moment du close (20h56).

## Prochaine étape exacte
Trancher l'interface de la commande de lancement (Phase 1 de `roadmap_revue_code_nocturne.md`).
Le wakeup 21h00 est actif dans cette session et lancera seul `lancer_nuit.cmd` puis surveillera
l'exécution.

## Question bloquante pour la session suivante
Aucune.
