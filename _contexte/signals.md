# Signals — roberto (MAJ 2026-08-02)

## Actions ouvertes
- [P2|ouvert] Planifier la prochaine roadmap fonctionnelle pour Ponganoid_v6 (config dynamique persistée, difficulté IA, sons/effets — hors périmètre des roadmaps actuelles) — fait quand : roadmap créée et validée avec l'utilisateur, réf: D:\ServOMorph\Ponganoid_v6\_ROBERTO\roadmaps\ (roadmap_acceleration_victoire_menu.md, roadmap_ligne_mediane.md et roadmap_premier_niveau_ia.md toutes [FAIT]).
- [P2|ouvert] `conversation_test.py` : `ROADMAP_PATH` pointe encore vers `roadmap_ligne_mediane.md` (terminée) — fait quand : mis à jour vers la roadmap active suivante avant toute relance fonctionnelle, réf: conversation_test.py ligne ROADMAP_PATH.
- [P3|ouvert] Fiabilité OCR sur des valeurs de contexte hors 7 %/50 % — fait quand : au moins 3 valeurs supplémentaires vérifiées manuellement, réf: tests_manuels.md.

## Dernière session (2026-08-02)

# Session du 2026-08-02

## Décisions prises
- Bannière de contrôle validée en conditions réelles : le code de la session précédente était déjà correct, le symptôme rapporté venait d'une instance `py run.py` non redémarrée.

## Livrables produits ou modifiés
- `tests_manuels.md` : section « Bannière de contrôle affichée tout le workflow » retirée (test validé).
- `_contexte/archive_decisions.md` : créé, archive la décision la plus ancienne (limite de 10 atteinte dans `contexte.md`).

## Hypothèses validées / invalidées
- VALIDE : après redémarrage de `py run.py`, la bannière rouge clignotante reste affichée du premier clic jusqu'à la fin d'une session `conversation_test.py` de 3 tours, sans s'éteindre entre les tours.
- INVALIDE : l'hypothèse initiale d'un bug de code sur la portée du flag de session -> pivot vers un problème de process non redémarré (déjà identifié comme action P1 de la session précédente).

## Prochaine étape exacte
Décider avec l'utilisateur de la prochaine roadmap fonctionnelle pour Ponganoid_v6 et mettre à jour `ROADMAP_PATH` en conséquence avant toute relance.

## Question bloquante pour la session suivante
Aucune.
