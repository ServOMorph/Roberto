# Signals — roberto   (MAJ 2026-09-04)

## Actions ouvertes
- [P1|ouvert] Première nuit réelle du planificateur : créer la tâche planifiée Windows (heure de
  coucher à fournir), lancer `claude setup-token`, laisser tourner une nuit sur creazik_v2 avec
  le `queue.json` d'exemple. Une tentative de test supervisé ce soir (réveil de session programmé
  pour 21:00) a été abandonnée en cours de route, sujet détourné avant l'heure cible — statut d'un
  éventuel réveil resté programmé non vérifié. fait quand: une nuit réelle s'est exécutée, rapport
  `PLANIFICATEUR/rapport_<date>.html` lisible au réveil, aucun `git push`, commits uniquement
  locaux sur branches dédiées. réf: roadmap_planificateur_nuit.md (gate Phase 2), tests_manuels.md,
  PLANIFICATEUR/queue.json
- [P2|ouvert] Workflow de revue de code nocturne (nouvelle demande, esquissée puis interrompue par
  /close) : overlay fenêtré (3/4 écran, centré, boutons Fermer/Annuler) demandant le dossier projet
  à analyser, lancement d'une analyse de code, roadmap de revue générée et stockée dans
  `<projet cible>/ROBERTO/`, priorisée par urgence et expliquée sans jargon technique (usage prévu :
  discussion vocale via com_telephone en voiture), roadmap validée exécutée la nuit suivante par le
  planificateur. Aucun fichier créé, spécification à reprendre depuis zéro. fait quand: le workflow
  est spécifié en détail (déclenchement de l'overlay, format de la roadmap de revue, intégration au
  planificateur) et validé par l'utilisateur avant tout code. réf: [à préciser]
- [P3|ouvert] Piste creazik_v2 explicitement reportée par l'utilisateur ("à voir plus tard") :
  proposition de découpler les gates de phase des tests manuels perceptuels (roadmap_impl.md) et
  d'ajouter un outil de validation automatisée façon IA_Life (`tools/run_manual_checks.py` etc., via
  Playwright sur l'app buildée). Rien acté, rien créé côté creazik_v2. fait quand: l'utilisateur
  relance le sujet et valide (ou écarte) la proposition. réf: creazik_v2/roadmap_impl.md,
  creazik_v2/tests_manuels.md, IA_Life/tools/ (pattern de référence)
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
# Session du 2026-09-04 (suite)

## Décisions prises
- Overlays plein écran ajoutés au planificateur : annonce au lancement (liste des tâches, butoir,
  bouton OK), bilan à la fin (statuts, coût, durée, bouton Fermer), flag `--no-overlay` pour les
  désactiver.
- Test réel programmé ce soir à 21h abandonné en cours de route : l'utilisateur a enchaîné sur
  d'autres sujets avant l'heure cible.
- Piste creazik_v2 (découplage gates/tests manuels) explicitement reportée par l'utilisateur.
- Nouvelle piste (workflow de revue de code nocturne) esquissée puis interrompue par /close, aucun
  travail commencé.

## Livrables produits ou modifiés
- `PLANIFICATEUR/overlay.py` : créé (overlays tkinter, charte VERTIA).
- `PLANIFICATEUR/orchestrateur.py` : appel des overlays dans `main()`, `depart` passé explicitement
  à `executer()`.
- `roadmap_planificateur_nuit.md` : Phase 3, item overlay coché.
- Tests : 36/36 verts, aucune régression.

## Hypothèses validées / invalidées
- VALIDE : overlays plein écran lisibles et fonctionnels (confirmation visuelle explicite de
  l'utilisateur : "overlays parfait").
- EN ATTENTE : gate Phase 2 (nuit réelle) toujours non franchi ; workflow de revue de code nocturne
  à spécifier de zéro.

## Prochaine étape exacte
Clarifier si la nuit réelle du planificateur est encore visée, puis spécifier le workflow de revue
de code nocturne (overlay sélection dossier, roadmap dans `<cible>/ROBERTO/`, triage par urgence
sans jargon pour restitution vocale com_telephone).

## Question bloquante pour la session suivante
Le workflow de revue de code nocturne doit-il être repris en priorité, ou la nuit réelle du
planificateur reste-t-elle l'objectif immédiat ?
