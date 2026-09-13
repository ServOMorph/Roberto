# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
Roberto conserve son **bridge com_tel** local (Node 5000, STT 5001, TTS 5002), sans projet externe
raccordé : le pilotage distant des environnements passe désormais par Remote Control. Planificateur
nocturne : Phase 3 [EN COURS], `typecheck` a réussi mais `audit-deps` refuse encore `Write`. Revue
nocturne : Phase 1 [EN COURS], scripts testés ; restent le déclenchement Windows et une revue de
bout en bout. `/refacto_projet` génère un plan et une roadmap non destructifs dans Codex/Astra.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
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
- 2026-09-04 : Phase 1 de `roadmap_revue_code_nocturne.md` : `revue_code.py` lance
  `claude -p "/code-review <niveau>" --restricted` (lecture seule + `Bash(git:*)`, jamais
  Write/Edit) et écrit lui-même la sortie brute dans `<cible>/ROBERTO/` (jamais le process
  `claude`). `--max-budget-usd` (défaut 5 $) conservé malgré l'abonnement de l'utilisateur :
  protège la fenêtre 5h partagée avec les autres tâches nocturnes, pas la facturation.
- 2026-09-06 : `selection_projet.py` choisit le projet le plus pertinent à review (`.git`+`.claude`
  présents, modifié <90j) parmi `Documents\ServOMorph` et `D:\ServOMorph`, suivi dans
  `suivi_revues.json` ; commande `/revue_projet` enchaîne sélection/confirmation/revue/suivi.
  Désaccord sur `--max-budget-usd` tranché : garde-fou de temps conservé, tout affichage/calcul de
  coût retiré ailleurs (workflow revue_code + planificateur nocturne).
- 2026-09-06 : `/refacto_projet` sélectionne une cible ou reçoit son chemin, impose la reprise dans
  Codex `gpt-6-astra`, puis produit un plan dans `ROBERTO/` et une roadmap à la racine de la cible,
  avec base de tests, contrôles avant/après, critères d'acceptation et rollback ; il ne modifie pas
  le code.
- 2026-09-13 : `com_telephone` est conservé uniquement dans Roberto ; les raccordements IA_Life,
  TSA et creazik_v2 sont retirés, Remote Control assurant désormais le pilotage distant des
  environnements de codage.
