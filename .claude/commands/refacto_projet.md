---
description: Sélectionne un projet et prépare, dans Codex Astra, un plan complet puis sa roadmap de refactorisation
argument-hint: [chemin-projet]
allowed-tools: Bash(python PLANIFICATEUR/selection_projet.py:*), PowerShell(python PLANIFICATEUR/selection_projet.py*), Read, Glob, Grep, Write, Bash(git status:*), Bash(git log:*), Bash(git diff:*)
---

# /refacto_projet [chemin-projet]

## Objectif

Préparer un plan de refactorisation complet et non destructif pour un projet : comprendre son
architecture et ses dettes techniques, relever les risques, définir les étapes de refactorisation,
et prévoir les tests de référence avant comme les contrôles après chaque étape. Transformer ensuite
ce plan en roadmap exécutable, structurée en phases.

Les livrables sont :
- `<projet>\ROBERTO\plan_refacto_<date>.md` : analyse, preuves et stratégie complète ;
- `<projet>\roadmap_refactorisation_<date>.md` : phases de réalisation dérivées du plan.

Cette commande ne modifie jamais le code applicatif, ne crée pas de branche et ne lance pas de
refactorisation.

## Précondition impérative : Codex Astra

Cette analyse doit être réalisée dans **Codex avec le modèle `gpt-6-astra` (Astra)**.

1. Si l'assistant courant n'est pas Codex/Astra, ne pas commencer l'analyse technique.
2. Si aucun chemin n'a été fourni, sélectionner d'abord la cible selon l'étape 1 ci-dessous.
3. Afficher le chemin choisi et demander à l'utilisateur de passer sur Codex, de choisir Astra,
   puis de relancer exactement :
   ```
   /refacto_projet "<chemin>"
   ```
4. S'arrêter. Ne pas supposer que le changement d'outil ou de modèle a été fait.

Si la commande est bien exécutée dans Codex/Astra avec un chemin explicite, poursuivre la
procédure ci-dessous.

## Procédure

1. Déterminer la cible.
   - Si `$ARGUMENTS` est un chemin de dossier existant, l'utiliser.
   - Sinon, depuis `PLANIFICATEUR/`, exécuter :
     ```
     python selection_projet.py prochain
     ```
   - Si la sortie contient `"message": "aucun projet pertinent jamais review"`, l'afficher et
     s'arrêter ; l'utilisateur devra fournir un chemin explicite.
   - Sinon, extraire `chemin` et `nom` du JSON, puis appliquer la précondition Codex Astra.

2. Vérifier que la cible est un dépôt Git. Lire, sans les modifier :
   - `AGENTS.md`, `CLAUDE.md` et `GEMINI.md` s'ils existent ;
   - `_contexte/signals.md`, puis `_contexte/contexte.md` s'ils existent ;
   - le manifeste et les scripts de build/test pertinents (`package.json`, `pyproject.toml`,
     `requirements*.txt`, `Cargo.toml`, etc.) ;
   - l'arborescence utile, les points d'entrée, les modules centraux et leurs tests.

3. Établir la base de départ, sans masquer les problèmes existants.
   - Relever `git status --short` et ne jamais attribuer les changements préexistants au plan.
   - Identifier la ou les commandes de test, de vérification statique et de build réellement
     prévues par le projet.
   - Exécuter uniquement les contrôles non interactifs, bornés et adaptés au projet. Noter pour
     chacun la commande, le résultat, la durée approximative et les échecs déjà présents.
   - Si aucun test automatisé n'existe, le signaler explicitement et proposer la plus petite
     couverture de caractérisation à créer avant toute refactorisation.

4. Analyser le dossier en lecture seule. Distinguer clairement les faits observés des hypothèses.
   Chercher notamment : responsabilités mélangées, duplications, dépendances circulaires,
   interfaces instables, couplage aux I/O, erreurs mal isolées, code mort, dette de tests,
   problèmes de performances ou de sécurité visibles. Ne pas transformer une préférence de style
   en chantier sans bénéfice concret.

5. Écrire `<projet>\ROBERTO\plan_refacto_<date>.md` avec ce format :
   - résumé simple : objectif, bénéfices attendus et périmètre exclu ;
   - état initial : architecture observée, fichiers concernés, changements Git préexistants et
     résultats exacts des tests de référence ;
   - constats priorisés `P1` / `P2` / `P3`, chacun avec preuve, impact et risque si inchangé ;
   - plan par petites étapes réversibles : fichiers touchés, changement attendu, dépendances,
     risque, critère de sortie et stratégie de rollback ;
   - stratégie de tests **avant** : commandes et tests de caractérisation à exécuter avant chaque
     étape ;
   - stratégie de tests **après** : tests unitaires/intégration à ajouter ou adapter, commandes
     à relancer après chaque étape, puis suite complète finale ;
   - contrôles manuels indispensables et critères d'acceptation globaux ;
   - ordre d'exécution recommandé et points qui exigent une décision de l'utilisateur.

6. Transformer le plan en `<projet>\roadmap_refactorisation_<date>.md`.
   - Lire les `roadmap_*.md` déjà présentes à la racine de la cible afin d'éviter les doublons,
     les phases concurrentes et les conflits de fichiers. Ne pas modifier ces roadmaps existantes.
   - Créer une phase par chantier cohérent, dans l'ordre recommandé par le plan. Chaque phase
     contient : objectif, périmètre de fichiers, dépendances, actions à cocher, tests avant/après,
     critère de validation et stratégie de rollback.
   - Reprendre les décisions nécessaires sous une section dédiée, sans les trancher à la place de
     l'utilisateur. Les points seulement suspects restent conditionnels et ne deviennent pas des
     travaux affirmés.
   - Initialiser chaque phase en `[TODO]`. La création de la roadmap ne démarre aucune phase ; une
     future session en mettra une seule à `[EN COURS]` selon les règles de la cible.
   - Ajouter après chaque phase le checkpoint exact exigé par les instructions de la cible. En
     l'absence de règle plus précise, utiliser :
     ```
     **⏸ Checkpoint** — Demander à l'utilisateur de faire `/compact` avant de continuer.
     Attendre sa réponse écrite. Ne pas commencer la phase suivante sans confirmation.
     ```
   - Ajouter une section finale d'acceptation globale, avec les contrôles transverses et la
     première action à effectuer. Distinguer les contrôles déjà exécutés de ceux prévus pour la
     réalisation.
   - Si `roadmap_refactorisation_<date>.md` existe déjà, ne pas l'écraser : s'arrêter et demander
     un nom ou une instruction de mise à jour explicite.

7. Relire le plan et la roadmap pour vérifier qu'ils sont actionnables, cohérents entre eux, sans
   jargon inutile et qu'aucune action de code n'a été réalisée. Afficher un bilan concis : chemins
   des deux livrables, nombre de constats par priorité, nombre de phases, commandes de référence
   exécutées et éventuels blocages.

## Règles de sécurité

- Analyse et planification seulement : pas de `Edit`, `git checkout`, création de branche,
  installation de dépendance, migration ou formatage global. `Write` est réservé aux deux
  livrables décrits ci-dessus.
- Les seuls fichiers autorisés à être créés sont le plan final dans `<projet>\ROBERTO\` et sa
  roadmap à la racine de `<projet>`.
- Un échec de test initial est une information à préserver dans le plan, jamais une correction
  implicite.
- Toute exécution future du plan devra être une demande distincte, validée étape par étape.
