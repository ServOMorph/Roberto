# Signals — roberto (MAJ 2026-08-02)

## Actions ouvertes
- [P1|ouvert] Redémarrer `py run.py` et retester que la bannière de contrôle reste affichée tout le workflow (menu → prise de contrôle → fin) — fait quand : test manuel validé, réf: tests_manuels.md (« Bannière de contrôle affichée tout le workflow »), app.py (mark_control_active/mark_session_active).
- [P2|ouvert] Planifier la prochaine roadmap fonctionnelle pour Ponganoid_v6 (config dynamique persistée, difficulté IA, sons/effets — hors périmètre des roadmaps actuelles) — fait quand : roadmap créée et validée avec l'utilisateur, réf: D:\ServOMorph\Ponganoid_v6\_ROBERTO\roadmaps\ (roadmap_acceleration_victoire_menu.md et roadmap_ligne_mediane.md toutes deux terminées).
- [P2|ouvert] `conversation_test.py` : `ROADMAP_PATH` pointe encore vers `roadmap_ligne_mediane.md` (terminée) — fait quand : mis à jour vers la roadmap active suivante avant toute relance, réf: conversation_test.py ligne ROADMAP_PATH.
- [P3|ouvert] Fiabilité OCR sur des valeurs de contexte hors 7 %/50 % — fait quand : au moins 3 valeurs supplémentaires vérifiées manuellement, réf: tests_manuels.md.
- [P3|ouvert] `_contexte/contexte.md` a atteint 10 décisions structurantes (max) — fait quand : les plus anciennes archivées dans `_contexte/archive_decisions.md` au prochain `/close`, réf: _contexte/contexte.md.

## Dernière session (2026-08-02)

# Session du 2026-08-02

## Décisions prises
- Blocage de contexte OCR géré automatiquement : envoi de `/compact` à OpenCode et attente de confirmation écrite avant de renvoyer le prompt bloqué (`compact_opencode`).
- `AGENTS.md` (règles fixes) ajouté dans le projet cible pour réduire la taille des prompts de tour envoyés à OpenCode.
- Correction définitive de l'overlay de sélection de zone multi-écrans (HWND toplevel, pas enfant) et retrait de la vérification image sur les 2 clics de la macro `OPENCODE-envoyer`.

## Livrables produits ou modifiés
- `workflow_test.py` : `compact_opencode()`.
- `conversation_test.py` : intégration de `compact_opencode` sur `ContextLimitReached`, prompt de tour allégé (renvoie vers `AGENTS.md`).
- `app.py` : bannière de contrôle (flags `mark_control_active`/`mark_session_active`/`is_control_active`), correction overlay `select_zone_rectangle` (toplevel HWND), `MATCH_THRESHOLD` 0.86 -> 0.55.
- `ui/index.html`, `ui/app.js`, `ui/style.css` : bannière rouge clignotante « contrôle en cours ».
- `.claude/zones.md` : ajout de l'alias `opencode` -> `OPENCODE/` (sous-zone d'orchestration, scaffold initialisé, non travaillée).
- Côté projet cible (hors repo Roberto) : `D:\ServOMorph\Ponganoid_v6\AGENTS.md` créé ; roadmap « accélération/victoire/menu » terminée (4 phases, 78 tests) ; roadmap « ligne médiane » créée et terminée (1 phase, 85 tests) — validant `AGENTS.md`.

## Hypothèses validées / invalidées
- VALIDE : le retrait de la vérification image sur les clics de la macro `OPENCODE-envoyer` élimine la fragilité de reconnaissance visuelle observée précédemment — 3 sessions consécutives réussies (9 tours, 0 échec macro).
- VALIDE : l'arrêt automatique à seuil de contexte atteint fonctionne en conditions réelles (bloqué exactement à 50 % = seuil 50 %, sans envoi) ; test manuel correspondant retiré de `tests_manuels.md`.
- VALIDE : `compact_opencode` déclenche `/compact` et obtient confirmation écrite d'OpenCode avant de reprendre l'envoi.
- VALIDE : `AGENTS.md` + prompt de tour allégé sont bien lus et appliqués par OpenCode (roadmap de test dédiée, 1 tour, succès, règles respectées).
- EN ATTENTE : bannière de contrôle affichée tout le workflow — correction appliquée mais pas retestée en conditions réelles depuis (nécessite un redémarrage de `py run.py`).

## Prochaine étape exacte
Redémarrer `py run.py` et valider la bannière de contrôle en conditions réelles, puis décider avec l'utilisateur de la prochaine roadmap fonctionnelle pour Ponganoid_v6 (et mettre à jour `ROADMAP_PATH` en conséquence).

## Question bloquante pour la session suivante
Aucune.
