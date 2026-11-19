# Contexte — roberto

## Objectif (immuable sauf décision explicite)
Copie réorganisée de claude-vibecoding-kit, réalisée étape par étape.

## Stack / contraintes techniques (stable, rarement modifié)
Markdown, Python (ollama_call.py), templates de commandes Claude Code

## État actuel (réécrit intégralement à chaque /close)
Roberto conserve son **bridge com_tel** (Node 5000, STT 5001, TTS 5002), raccordé à VibeObs (relais des
sessions en service) et durci le 2026-11-19 : appairage du 1er appareil, liste blanche `!`, écoute locale,
notifications discrètes, voix unique, vocal regroupé. Pont arrêté en fin de session ; `/roberto` le
démarre et relance l'écoute toutes les 30 min, le tunnel reste lancé par l'utilisateur. Planificateur
nocturne : Phase 3 ; revue nocturne : Phase 1 ; `/refacto_projet` : plan et roadmap non destructifs.

## Décisions structurantes (append only — 10 entrées max, 5 lignes max/entrée, archiver au-delà)
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
- 2026-11-17 : Un message reçu du téléphone vaut confirmation de l'utilisateur, y compris pour
  répondre aux autres sessions Claude locales (`SendMessage`) ; action destructive ou irréversible :
  confirmation explicite redemandée. Envoi vers le téléphone via `send_message.py` : `curl` sous
  Windows corrompt les accents (le TTS n'est pas en cause). Détail : `_contexte/memory.md`.
- 2026-11-17 : VibeObs est raccordé au pont com_telephone (entrée `vibeobs`, ligne dans
  `DEPLOYMENTS.md`), ce qui revient en partie sur l'entrée du 2026-09-13 ; `/roberto` démarre le pont
  si besoin (port 5000 libéré seulement si `node.exe`). Le tunnel est lancé par l'utilisateur seul,
  jamais par Claude. Procédure : `com_telephone/README.md`, section « Relais des sessions par VibeObs ».
- 2026-11-19 : Audit de sécurité du pont (`_docs/audit_securite_2026-11-17.md`) : sessions jointes en
  `auto` (choix de l'utilisateur) ; depuis le téléphone, commit permis mais push et actions destructives
  attendent le PC (remplace l'autorisation du 2026-08-26) ; liste blanche `!` ; le 1er appareil appairé
  verrouille le pont ; tunnel laissé à l'utilisateur. Détail : `_contexte/memory.md`.
- 2026-11-19 : Un Monitor expire après 30 min au plus (plafond de l'outil) : `/roberto` relance l'écoute à
  chaque expiration. Vocal : accusé, regroupement 4 s, alerte 60 s, silence 1,8 s, durée maximale 90 s,
  une seule voix (demandes de VibeObs, non testées sur iPhone).
