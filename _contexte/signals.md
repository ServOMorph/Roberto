# Signals — roberto   (MAJ 2026-08-29)

## Actions ouvertes
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
# Session du 2026-08-29 (suite)

## Décisions prises
- Aucune. Accès externe Marie : 4 questions identifiées, décision en attente de réponses.

## Livrables produits ou modifiés
- Analyse `com_telephone/_docs/analyse_acces_externe_marie_tsa.md` relue ; 4 questions
  clarifiées pour décision (type accès, commandes !, durée, données sensibles).

## Hypothèses validées / invalidées
- EN ATTENTE : voie accès externe Marie (multi-utilisateurs vs second serveur).

## Prochaine étape exacte
L'utilisateur répond aux 4 questions. Ensuite : trancher voie A ou B et passer à
l'implémentation.

## Question bloquante pour la session suivante
Les réponses aux 4 questions de clarification sur l'accès externe de Marie.
