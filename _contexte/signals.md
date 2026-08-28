# Signals — roberto   (MAJ 2026-08-28)

## Actions ouvertes
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
- [P3|ouvert] Traiter S5, S7, S8 de l'audit (check anti-traversée statique sans séparateur ;
  cycle de vie du token : cookie 1 an, token imprimé par com_manager, rotation non documentée ;
  divers). fait quand: chaque constat corrigé ou explicitement écarté. réf:
  com_telephone/_docs/audit_securite_2026-08-28.md
- [P3|ouvert] Décider la proposition des 3 agents de dev (Bridge / PWA / Déploiement-Ops).
  fait quand: validée (agent_role.md créés) ou rejetée. réf:
  com_telephone/_docs/agents_dev_proposition.md

## Dernière session
<!-- Écrasé intégralement par /close. Synthèse < 25 lignes. -->
# Session du 2026-08-28

## Décisions prises
- Terme figé : "com_tel" (pas "Com"), "bridge" (pas "le pont"). Glossaire `_docs/vocabulaire.md`
  (5 termes : com_tel, bridge, projet, raccordé/autonome, canaux étanches).
- creazik_v2 raccordé au bridge ; suppression de sa copie autonome. Tous les déploiements se font
  désormais en mode raccordé ; "autonome" conservé pour référence historique seulement.
- Audit sécurité livré (`_docs/audit_securite_2026-08-28.md`, 8 constats). Corrigés cette session :
  S1 (/send et /push/test refusent les requêtes proxifiées), S2 (nettoyage \r\n\t des logs),
  S3+S6 (extension image assainie, limites de taille, maxPayload WS).

## Livrables produits ou modifiés
- PWA : écran d'accueil (liste projets + pastille non-lus persistée, bouton retour, chat = projet
  courant seul), correctif bandeau iOS (safe-area, connLabel masqué, meta apple-mobile-web-app),
  partage de fichier JSON (bouton, user.file, _docs/fichiers/, log [FICHIER]).
- Notifications : détection premier-plan (client.visible), push si aucun client premier-plan < 8 s,
  message conservé pour rejeu, `mid` anti-doublon, dédoublonnage des abonnements par `deviceId`,
  push_subs.json vidé.
- creazik_v2 : raccordé (README, /roberto, section CLAUDE.md, entrée projects.json, DEPLOYMENTS.md).
- Docs : `_docs/vocabulaire.md`, `_docs/audit_securite_2026-08-28.md`, `_docs/agents_dev_proposition.md`.
- .gitignore racine : `_docs/captures/`.

## Hypothèses validées / invalidées
- VALIDE : tests manuels PWA écran d'accueil + migration com_telephone (utilisateur : "Tout").
- VALIDE : partage JSON de bout en bout (utilisateur : "Ça marche").
- VALIDE : correctifs S1-S3 (requête forwardée -> 403, newline -> ligne unique, MIME traversal
  -> fichier confiné dans captures).
- EN ATTENTE : notifications push en réel, téléphone verrouillé (checklist tests_manuels.md).
- EN ATTENTE : raccordement creazik_v2 en réel (session Claude + /roberto + aller-retour PWA).

## Prochaine étape exacte
L'utilisateur : re-souscrire la PWA puis tester les notifications téléphone verrouillé ; ouvrir
une session Claude Code dans creazik_v2, lancer /roberto, aller-retour sur l'onglet creazik_v2.
Puis décider S4 (Piper par défaut ou README corrigé).

## Question bloquante pour la session suivante
Aucune
