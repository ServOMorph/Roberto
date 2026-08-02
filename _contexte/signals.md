# Signals — roberto (MAJ 2026-08-02)

## Actions ouvertes
- [P1|ouvert] Valider les 3 tests manuels de la refacto (lancement UI, pont OpenCode réel, session `scripts.conversation`) — fait quand : les 3 sections de `tests_manuels.md` sont passées et supprimées du fichier, réf: tests_manuels.md.
- [P2|ouvert] Tester le mode `--duration` jusqu'à son terme naturel (arrêt automatique après délai, sans intervention manuelle) — fait quand : une session `py -m scripts.conversation --duration N` va à son terme et le manifeste `arrete_duree_max` est vérifié correct, réf: scripts/conversation.py.
- [P2|ouvert] Planifier la prochaine roadmap fonctionnelle pour Ponganoid_v6 — la roadmap 10 niveaux/briques/bonus est terminée (6/6 phases) — fait quand : nouvelle roadmap créée et validée avec l'utilisateur, réf: D:\ServOMorph\Ponganoid_v6\_ROBERTO\roadmaps\roadmap_10_niveaux_briques_bonus.md ([FAIT]).
- [P3|ouvert] Écrire le profil `agents/claudecode.py` (macro d'envoi, zone OCR, sens de lecture du contexte) — fait quand : profil créé, enregistré dans `agents/__init__.py`, macro et zone déclarées dans Macrodesk, réf: agents/base.py, agents/opencode.py.
- [P3|ouvert] Compléter `VALIDATION_MANUELLE.md` de Ponganoid_v6 (partiellement rempli jusqu'à la phase 6) — fait quand : validation manuelle documentée pour l'ensemble du livrable 10 niveaux, réf: D:\ServOMorph\Ponganoid_v6\VALIDATION_MANUELLE.md.
- [P3|ouvert] Fiabilité OCR sur des valeurs de contexte hors 7 %/50 % — fait quand : au moins 3 valeurs supplémentaires vérifiées manuellement, réf: tests_manuels.md.

## Dernière session (2026-08-02)

# Session du 2026-08-02

## Décisions prises
- Restructuration complète en packages (`macrodesk/`, `bridge/`, `agents/`, `scripts/`, `tests/`, `docs/`) pour accueillir un second agent, CLAUDECODE, sans y coder quoi que ce soit à ce stade.
- Un `AgentProfile` (`agents/base.py`) porte tout ce qui varie entre agents ; `bridge/` et `scripts/` restent génériques et prennent `--agent <clé>`.
- Suite de tests écrite avant la refacto (baseline 80 tests verts), puis seul le point d'adaptation `tests/_compat.py` a été modifié pendant la refacto pour garantir zéro changement de comportement.
- Zone vibecoding `OPENCODE/` déplacée dans `_zones/OPENCODE/` ; `ui/` déplacé dans `macrodesk/ui/`.

## Livrables produits ou modifiés
- `macrodesk/` : nouveau package (paths, control, keys, screen, ocr, store, engine, api, app, ui/) — remplace `app.py`.
- `bridge/` : nouveau package générique (errors, files, lookup, session) — remplace la logique de `workflow_test.py` propre au pont.
- `agents/` : nouveau package, `AgentProfile` + profil `opencode` enregistré.
- `scripts/` : `conversation.py`, `workflow_check.py`, `context_watch.py`, `ocr_reliability.py`, `common.py` — remplacent les `*_test.py` racine.
- `tests/` : 123 tests (9 fichiers + `_compat.py`), `pytest.ini` ajouté.
- `run.py`, `README.md`, `CHANGELOG.md` (v0.7), `docs/workflow_opencode.md`, `.claude/zones.md`, `.claude/commands/stop_opencode.md`, `_zones/OPENCODE/agent_role.md`, `tests_manuels.md` : mis à jour pour la nouvelle structure.

## Hypothèses validées / invalidées
- VALIDE : geler la suite de tests avant refacto puis ne faire varier que le point d'adaptation (`_compat.py`) permet de vérifier une non-régression stricte (80/80 identiques avant/après, sur assertions inchangées).
- VALIDE : un seul champ (`context_metric`) suffit à couvrir le cas où un futur agent afficherait le contexte restant plutôt que consommé, sans changer la logique de seuil appelante.
- EN ATTENTE : aucun test manuel réel de la refacto encore passé (UI, pont, session longue) — ajoutés à `tests_manuels.md`, non exécutés cette session.

## Prochaine étape exacte
Valider les 3 tests manuels de la refacto (`tests_manuels.md`) avant toute nouvelle session de pilotage OpenCode ; puis écrire le profil `agents/claudecode.py` si CLAUDECODE devient prioritaire.

## Question bloquante pour la session suivante
Aucune.
