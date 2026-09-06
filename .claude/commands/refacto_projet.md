---
description: Sélectionne un projet et prépare, dans Codex Astra, un plan complet de refactorisation avec stratégie de tests
argument-hint: [chemin-projet]
allowed-tools: Bash(python PLANIFICATEUR/selection_projet.py:*), PowerShell(python PLANIFICATEUR/selection_projet.py*), Read, Glob, Grep, Write, Bash(git status:*), Bash(git log:*), Bash(git diff:*)
---

# /refacto_projet [chemin-projet]

## Objectif

Préparer un plan de refactorisation complet et non destructif pour un projet : comprendre son
architecture et ses dettes techniques, relever les risques, définir les étapes de refactorisation,
et prévoir les tests de référence avant comme les contrôles après chaque étape.

Le livrable est un unique fichier
`<projet>\ROBERTO\plan_refacto_<date>.md`. Cette commande ne modifie jamais le code applicatif,
ne crée pas de branche et ne lance pas de refactorisation.

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

6. Relire le plan pour vérifier qu'il est actionnable sans jargon inutile et qu'aucune action de
   code n'a été réalisée. Afficher un bilan concis : chemin du plan, nombre de constats par
   priorité, commandes de référence exécutées et éventuels blocages.

## Règles de sécurité

- Analyse et planification seulement : pas de `Edit`, `git checkout`, création de branche,
  installation de dépendance, migration ou formatage global. `Write` est réservé au seul plan
  final décrit ci-dessous.
- Le seul fichier autorisé à être créé est le plan final dans `<projet>\ROBERTO\`.
- Un échec de test initial est une information à préserver dans le plan, jamais une correction
  implicite.
- Toute exécution future du plan devra être une demande distincte, validée étape par étape.
