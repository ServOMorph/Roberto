---
description: Lance le workflow complet de revue de code — sélection du projet le plus pertinent, exécution de la revue, enregistrement dans le suivi
argument-hint: [niveau] (low|medium|high|max, défaut: max)
model: sonnet
allowed-tools: Bash(python PLANIFICATEUR/selection_projet.py:*), Bash(python PLANIFICATEUR/revue_code.py:*), PowerShell(python PLANIFICATEUR/selection_projet.py*), PowerShell(python PLANIFICATEUR/revue_code.py*), Read
---

# /revue_projet [niveau]

## Objectif

Enchaîne les 3 étapes du workflow de revue de code (`PLANIFICATEUR/selection_projet.py`,
`PLANIFICATEUR/revue_code.py`, `roadmap_revue_code_nocturne.md`) : sélection automatique du projet
le plus pertinent parmi `C:\Users\raph6\Documents\ServOMorph` et `D:\ServOMorph`, lancement de
`/code-review` dessus, puis enregistrement du résultat dans `PLANIFICATEUR/suivi_revues.json`.

Niveau = $ARGUMENTS si fourni, sinon `max`.

## Procédure

1. Depuis `PLANIFICATEUR/`, exécuter :
   ```
   python selection_projet.py prochain
   ```
   - Si la sortie contient `"message": "aucun projet pertinent jamais review"` : l'afficher et
     s'arrêter, rien à faire.
   - Sinon, extraire `chemin` et `nom` du JSON retourné.

2. Annoncer à l'utilisateur le projet choisi (`nom`, `chemin`) et demander confirmation avant de
   lancer la revue — ~10-15 min sans surveillance. Ne pas continuer sans confirmation explicite.

3. Lancer la revue :
   ```
   python revue_code.py "<chemin>" --niveau <niveau>
   ```

4. Lire le fichier de sortie annoncé (`<chemin>\ROBERTO\revue_brute_<date>.json`) avec l'outil
   Read. En extraire :
   - `code_retour` et `timeout_atteint` (échec si `code_retour != 0` ou timeout atteint)
   - un résumé en 1-2 lignes du contenu de la revue (nombre de constats, gravité dominante)

5. Si échec (étape 4) : afficher l'erreur brute à l'utilisateur, ne pas appeler `marquer` — le
   projet reste en tête de liste pour un prochain essai. S'arrêter.

6. Si succès : enregistrer dans le suivi :
   ```
   python selection_projet.py marquer "<chemin>" --niveau <niveau> --resultat "<résumé étape 4>"
   ```

7. Afficher un bilan : projet review, chemin du fichier de sortie brut, résumé.

## Point d'attention

3 roadmaps se disputent déjà la fenêtre nocturne de 5h partagée avec `PLANIFICATEUR/` (cf.
`signals.md`, arbitrage P1 non tranché). Cette commande est un déclenchement manuel, à la demande
— elle ne s'invite pas dans le planificateur nocturne.
