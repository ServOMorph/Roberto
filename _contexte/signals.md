# Signals — roberto   (MAJ 2026-08-29)

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
# Session du 2026-08-29

## Décisions prises
- Aucune décision structurante. Analyse « accès externe Marie -> tsa » produite puis mise en
  attente (voir action ouverte P3 dédiée).

## Livrables produits ou modifiés
- PWA : pastille sur le bouton "Projets" du bandeau (signale des non-lus dans un autre projet
  que le projet courant, en vue chat) ; bouton "Mettre le PC en veille" sur l'écran d'accueil
  (confirmation inline Confirmer/Annuler -> message WS `client.sleep`).
- Serveur : handler `client.sleep` (SetSuspendState Windows / systemctl suspend, debounce 5 s).
- `com_telephone/_docs/analyse_acces_externe_marie_tsa.md` : faisabilité + 2 voies + questions.
- `com_telephone/_docs/audit_securite_2026-08-28.md` : ligne S8 sur `client.sleep`.
- tests_manuels.md : test réel de la mise en veille ajouté.

## Hypothèses validées / invalidées
- EN ATTENTE : pastille du bouton "Projets" (à confirmer en usage réel).
- EN ATTENTE : mise en veille du PC depuis la PWA (non testable sans endormir la machine).
- EN ATTENTE : tests de la session précédente inchangés (push tél verrouillé, raccordement
  creazik_v2).

## Prochaine étape exacte
L'utilisateur teste la pastille "Projets", la mise en veille depuis l'accueil, puis les tests en
attente (push, creazik_v2). Ensuite : trancher la voie pour l'accès de Marie et le point S4.

## Question bloquante pour la session suivante
Aucune
