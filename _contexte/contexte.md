# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
Roberto héberge le **bridge com_tel** (serveur Node 5000 + STT 5001 + TTS 5002 via
`com_manager.py`, `.env` hors git) et en est le template de référence ; `ia_life`, `tsa`,
`roberto`, `creazik_v2` tous raccordés. Audit `_docs/audit_securite_2026-08-28.md` : S1-S3+S6
corrigés, S4/S5/S7/S8 ouverts. Chantier **planificateur nocturne** (`PLANIFICATEUR/`) : Phases 1-2
[FAIT], Phase 3 [EN COURS] ; gate Phase 2 (nuit réelle) test reprogrammé ce soir 21h00 via wakeup
automatique. Nouveau chantier **revue de code nocturne** (`roadmap_revue_code_nocturne.md`, 4
phases [TODO]) : `/code-review` niveau max déclenché par une tâche planifiée par l'utilisateur
(pas d'overlay), sortie dans `<cible>/ROBERTO/`, discussion vocale via com_telephone, correctifs
exécutés la nuit suivante.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
- 2026-08-25 : com_telephone remplacé intégralement par la version validée en réel dans creazik_v2
  (nouvelle source de vérité pour les futurs déploiements).
- 2026-08-25 : com_manager.py affiche le lien appli (token) au démarrage et démarre tout par défaut
  sans argument — nécessite TUNNEL_URL dans .env en plus d'AUTH_TOKEN.
- 2026-08-28 : com_telephone rendu multi-projets (routage par `project`, `projects.json`, sélecteur
  PWA) — développé et durci dans IA_Life, puis promu ici comme template unique.
- 2026-08-28 : Roberto devient l'hôte du pont (le serveur y tourne) ; IA_Life et TSA sont des
  projets raccordés. `.env` d'IA_Life réutilisé tel quel (lien téléphone + push préservés).
  Commande `/com_telephone_init` ajoutée pour les futurs déploiements.
- 2026-08-28 : Vocabulaire commun figé (`_docs/vocabulaire.md`) : com_tel, bridge, projet,
  raccordé/autonome, canaux étanches. Termes retenus : "com_tel" (pas "Com"), "bridge" (pas "pont").
- 2026-08-28 : creazik_v2 raccordé au bridge ; fin de la dernière copie autonome. Tous les
  déploiements se font désormais en mode raccordé (autonome = référence historique seulement).
- 2026-08-28 : Audit sécurité (`_docs/audit_securite_2026-08-28.md`). Corrigés : `/send` et
  `/push/test` refusent les requêtes proxifiées (S1), nettoyage `\r\n\t` des textes journalisés
  (S2), extension image assainie + limites de taille + maxPayload WS (S3/S6).
- 2026-09-04 : Planificateur nocturne (`PLANIFICATEUR/`) : exécute des tâches `claude -p`
  `--restricted` la nuit, confinées par une allowlist de dossiers, butoir 06:00, retry aveugle
  sur la limite 5 h, rapport HTML (charte VERTIA) + push com_tel. Le confinement repose sur le
  harness (`--restricted` + `--allowedTools` + `--disallowedTools`), jamais sur `CLAUDE.md`.
  Un run avec outils refusés est un échec ; une tâche interrompue n'est pas rejouée.
- 2026-09-04 : Overlays plein écran ajoutés au planificateur (`overlay.py`) : annonce au
  lancement, bilan à la fin, désactivables via `--no-overlay`. Validés visuellement par
  l'utilisateur.
- 2026-09-04 : Workflow de revue de code nocturne repensé : abandon de l'overlay et du
  déclenchement custom, remplacé par `/code-review` niveau max déclenché par une tâche planifiée
  par l'utilisateur (Windows ou `/schedule`). Reste : sortie unique dans `<cible>/ROBERTO/`,
  discussion vocale via com_telephone, correctifs exécutés la nuit suivante
  (`roadmap_revue_code_nocturne.md`).
