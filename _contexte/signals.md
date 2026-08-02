# Signals — roberto (MAJ 2026-08-02)

## Actions ouvertes
- [P2|ouvert] Tester le mode `--duration` jusqu'à son terme naturel (arrêt automatique après délai, sans intervention manuelle) — fait quand : une session `conversation_test.py --duration N` va à son terme et le manifeste `arrete_duree_max` est vérifié correct, réf: conversation_test.py.
- [P2|ouvert] Planifier la prochaine roadmap fonctionnelle pour Ponganoid_v6 — la roadmap 10 niveaux/briques/bonus est terminée (6/6 phases) — fait quand : nouvelle roadmap créée et validée avec l'utilisateur, réf: D:\ServOMorph\Ponganoid_v6\_ROBERTO\roadmaps\roadmap_10_niveaux_briques_bonus.md ([FAIT]).
- [P3|ouvert] Compléter `VALIDATION_MANUELLE.md` de Ponganoid_v6 (partiellement rempli jusqu'à la phase 6) — fait quand : validation manuelle documentée pour l'ensemble du livrable 10 niveaux, réf: D:\ServOMorph\Ponganoid_v6\VALIDATION_MANUELLE.md.
- [P3|ouvert] Fiabilité OCR sur des valeurs de contexte hors 7 %/50 % — fait quand : au moins 3 valeurs supplémentaires vérifiées manuellement, réf: tests_manuels.md.

## Dernière session (2026-08-02)

# Session du 2026-08-02

## Décisions prises
- Roadmap fonctionnelle longue créée pour Ponganoid_v6 (10 niveaux vs IA, briques centrales, bonus), pilotée en session automatisée sans relecture humaine intermédiaire.
- Protocole de prompt allégé : suppression de la mention AGENTS.md et de l'écho du compte rendu précédent (redondants avec l'historique conservé par OpenCode).
- Les phases de roadmap peuvent être formulées de façon resserrée sans perte de qualité une fois les conventions du projet établies.
- `conversation_test.py` s'arrête désormais automatiquement quand la roadmap ne contient plus de phase `[EN COURS]`.

## Livrables produits ou modifiés
- `D:\ServOMorph\Ponganoid_v6\_ROBERTO\roadmaps\roadmap_10_niveaux_briques_bonus.md` : créée, 6/6 phases [FAIT].
- `conversation_test.py` : prompt allégé (`prompt_for_turn`), arrêt automatique (`roadmap_complete`), `ROADMAP_PATH` repointé.
- Ponganoid_v6 (via OpenCode) : briques, vies, bonus raquette agrandie, 10 niveaux, IA progressive, écrans victoire/game over — 158 tests, validations réelles OK.
- `/stop_opencode` : testé 4 fois en conditions réelles (bug OCR zone désalignée, timeout normal, arrêts manuels) — fonctionne, manifeste reconstruit à chaque fois.

## Hypothèses validées / invalidées
- VALIDE : OpenCode lit AGENTS.md seul, sans rappel dans le prompt.
- VALIDE : réafficher le compte rendu précédent dans le prompt est une redondance pure.
- VALIDE : des phases de roadmap resserrées donnent un résultat aussi rigoureux que des phases détaillées, une fois les conventions du projet établies.
- INVALIDE (bug tiers) : un chemin corrompu généré par OpenCode a bloqué un tour — corrigé côté OpenCode par l'utilisateur, hors périmètre Roberto.
- EN ATTENTE : mode `--duration` non testé jusqu'à son terme naturel cette session.

## Prochaine étape exacte
Définir la prochaine roadmap fonctionnelle pour Ponganoid_v6 (la roadmap actuelle est terminée), ou tester `--duration` jusqu'à son terme naturel.

## Question bloquante pour la session suivante
Aucune.
