# Archive des sessions — roberto

Sessions déplacées ici par `/close` (la plus récente reste dans `signals.md`).

---

# Session du 2026-09-04

## Décisions prises
- Phase 1 de `roadmap_revue_code_nocturne.md` tranchée : interface via alias `.claude/zones.md`
  (ou chemin direct), confinement `claude -p --restricted` (lecture seule + `Bash(git:*)`, jamais
  Write/Edit).
- Sortie brute écrite par le script Python lui-même dans `<cible>/ROBERTO/`, jamais par le process
  `claude` — renforce le confinement au-delà de ce que `--restricted` garantit seul.
- `--max-budget-usd` conservé dans `revue_code.py` malgré l'objection de l'utilisateur
  (abonnement) : protège la fenêtre de tokens partagée avec les autres tâches nocturnes, pas un
  enjeu de facturation — désaccord non tranché.

## Livrables produits ou modifiés
- `PLANIFICATEUR/revue_code.py` : créé (Phase 1 de `roadmap_revue_code_nocturne.md`).
- `PLANIFICATEUR/test_revue_code.py` : créé, 18 tests, mockés (aucun appel réel à `claude`).

## Hypothèses validées / invalidées
- VALIDE : confinement de `/code-review max` sans surveillance — vérifié en réel sur Roberto
  (`git status` avant/après identique hors `ROBERTO/`), coût réel 2,15 $, ~13 min.
- VALIDE (indirectement) : la revue elle-même a trouvé 3 défauts réels dans `revue_code.py` fraîchement
  écrit (pas de `--max-budget-usd`, `_tuer_arbre` non cross-platform, bug de parsing `charger_zones`)
  — tous corrigés, testés.
- EN ATTENTE : invocation via tâche planifiée Windows (schtasks), non testée.

## Prochaine étape exacte
Phase 2 de `roadmap_revue_code_nocturne.md` : conversion des constats `/code-review` en fichier
markdown priorisé, langage simple, écrit dans `<cible>/ROBERTO/roadmap_revue_<date>.md`.

## Question bloquante pour la session suivante
Garder `--max-budget-usd` dans `revue_code.py` (désaccord non tranché avec l'utilisateur) ou le
retirer ?

---

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

---

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
