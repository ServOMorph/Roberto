# Signals — roberto   (MAJ 2026-09-04)

## Actions ouvertes
- [P1|ouvert] Première nuit réelle du planificateur : créer la tâche planifiée Windows (heure de
  coucher à fournir), lancer `claude setup-token`, laisser tourner une nuit sur creazik_v2 avec
  le `queue.json` d'exemple. fait quand: une nuit réelle s'est exécutée, rapport
  `PLANIFICATEUR/rapport_<date>.html` lisible au réveil, aucun `git push`, commits uniquement
  locaux sur branches dédiées. réf: roadmap_planificateur_nuit.md (gate Phase 2), tests_manuels.md,
  PLANIFICATEUR/queue.json
- [P2|ouvert] Vérifier en réel que `git checkout -b` et `git commit` passent la liste blanche
  `--allowedTools "Bash(git:*)"` (non testé : seuls `git push` refusé et `npm run typecheck`
  autorisé l'ont été). fait quand: la tâche `typecheck` du queue.json d'exemple aboutit sans
  statut `refus`, ou la liste blanche est corrigée. réf: PLANIFICATEUR/orchestrateur.py
  (BASH_AUTORISE_DEFAUT), PLANIFICATEUR/logs/
- [P2|ouvert] Arbitrer les deux roadmaps avec une phase [EN COURS] simultanée :
  `roadmap_planificateur_nuit.md` (Phase 3) et `roadmap_ameliorations.md` (Phase 1, jamais
  démarrée). fait quand: une seule des deux reste [EN COURS], l'autre est mise en pause explicite
  ou close. réf: roadmap_planificateur_nuit.md, roadmap_ameliorations.md
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
- Planificateur nocturne : code dans `Roberto/PLANIFICATEUR/`, confinement natif `--restricted`
  (pas de hook maison en MVP).
- Un run dont des outils ont été refusés = statut `refus` (échec), jamais compté comme succès.
- Tâche interrompue par un crash = `echouee/interrompue`, aucun rejeu automatique.
- Tâche planifiée Windows non créée cette session (heure de coucher non fixée, modif système).
- Phase 3 poursuivie sans `/compact` ni gate Phase 2 franchi (écart de procédure assumé).

## Livrables produits ou modifiés
- `PLANIFICATEUR/` créé : orchestrateur.py, rapport.py, tache.py (CLI), notifier.py, allowlist.txt,
  queue.json, lancer_nuit.cmd, .gitignore, test_planificateur.py (36 tests verts).
- `tests_manuels.md` : + tâche planifiée Windows, + nuit réelle (gate Phase 2).
- `roadmap_planificateur_nuit.md` : Phases 1 et 2 [FAIT], Phase 3 [EN COURS] (5 items sur 6).

## Hypothèses validées / invalidées
- VALIDE : confinement `--restricted` (écriture hors périmètre refusée ; `git push` refusé malgré
  `Bash(git:*)` ; `npm run typecheck` autorisé) ; timeout + kill de l'arbre `node` ; push
  com_telephone (HTTP 200 réel) ; `--max-budget-usd` sous abonnement.
- INVALIDE : `sauver_queue`/`charger_queue`/`charger_allowlist` figeaient le chemin par défaut à
  l'import -> corrigé en liaison tardive (bug trouvé par le smoke test).
- EN ATTENTE : format de l'erreur de quota (non provocable) ; `git checkout -b` / `git commit`
  passent-ils la liste blanche ; gate Phase 2 = une nuit réelle.

## Prochaine étape exacte
Fournir l'heure de coucher, créer la tâche planifiée Windows, lancer `claude setup-token`, puis
première nuit réelle sur creazik_v2 avec le `queue.json` d'exemple.

## Question bloquante pour la session suivante
Heure de coucher pour la tâche planifiée Windows.
