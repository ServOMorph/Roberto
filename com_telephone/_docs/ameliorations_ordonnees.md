# Améliorations com_telephone — ordonnancement

Date : 2026-08-21. Cas d'usage retenu pour développer et tester : **le développement du projet CREAZIK_V2** (la communication avec l'assistant sert à avancer sur ce projet).

## Décisions actées

- TTS : **100% local** (principe du projet maintenu, aucune donnée cloud). **Révisé le 2026-08-21** : après écoute, l'utilisateur a choisi la voix **Microsoft Denise** (edge-tts, cloud) — « Oui c'est parfait ». Piper (fr_FR-upmc-medium) conservé en secours automatique si edge-tts est indisponible.
- Screenshots : **téléphone ET PC**.
- Prise de contrôle PC : réutiliser le proto existant `D:\ServOMorph\claude-vibecoding-kit\templates\control_PC` (Python, capture de fenêtre ciblée, clic avec confirmation `--confirm-click`, halo, journalisation).
- Alignement : **bilan périodique** (rituel, pas de dashboard continu).

## Ordre retenu (du plus simple au plus lourd)

| # | Chantier | Effort | Dépend de |
|---|---|---|---|
| 1 | Encodage français (accents) | très faible | — |
| 2 | Salutations (10 bonjours) | très faible | 4 (validation) |
| 3 | UI micro : icône rouge bas droite + mode auto/manuel | faible | — |
| 4 | Boutons Validé / Corrigé dans l'appli | faible | — |
| 5 | Voix plus réaliste (upmc immédiat, Kokoro ensuite) | moyen | — |
| 6 | Latence : audit + fixes par ordre | moyen | — |
| 7 | Screenshots téléphone + PC | moyen | — |
| 8 | Logging des conversations + bilan d'alignement | moyen | — |
| 9 | Commandes vocales | important | 8 (logging pour tracer) |
| 10 | Contrôle PC (intégration du proto) | important | — |
| 11 | Apprentissage autonome (record/replay) | très important | 10 |
| 12 | Réponse adaptée au canal (écrit → écrit, vocal → vocal, notifs pour les deux) | faible | — |

## Détail par chantier

### 1. Encodage français (accents)
**Demande** : les accents et lettres françaises s'affichent mal dans l'appli.
**Constat** : messages.log contient « regardÃ© » (UTF-8 relu en latin-1 quelque part dans la chaîne STT → serveur → WebSocket → appli). Le code mobile évite d'ailleurs les accents (« Ecoute », « Reponse »), symptôme d'un problème connu non traité.
**Action** : diagnostiquer la chaîne d'encodage (stt_server.py → server.js → app.js), corriger, réintroduire les accents dans les libellés mobiles.
**Effort** : < 1 session.

### 2. Salutations (10 bonjours)
**Demande** : à chaque initialisation de conversation, l'utilisateur dit bonjour ; l'assistant répond avec une des ~10 variantes fournies par l'utilisateur.
**Action** : table de salutations (fichier de données + tirage), déclenchement sur « bonjour » en début de session.
**Variantes fournies par l'utilisateur (2026-08-24)** :
1. Salut ça farte ?
2. Ça roule ma poule ?
3. Yeppa
4. Ah non j'ai pas fini ma partie de candy crush
5. Olé olé !!!
6. Ola! Que tal ?
7. Salut l'ami
8. Je suis fatigué aujourd'hui, tu peux me laisser un jour de congé ?
9. Ah donf !!!
10. On va tout déchirer

### 3. UI micro : icône rouge bas droite + mode auto/manuel
**Demande** : l'écran micro devient une icône micro en bas à droite de l'appli, rouge quand l'enregistrement est possible. À côté, un bouton de choix du mode : automatique (actuel, détection de silence) ou manuel (maintenir appuyé, relâcher = envoyer).
**Action** : restructuration de la barre basse, `pointerdown`/`pointerup` pour le push-to-talk, bascule de mode.
**Inspiration** : ListenClaw (pattern push-to-talk WebSocket), Orbital P.A.I (détection de fin de phrase).
**Effort** : ~1 session.

### 4. Boutons Validé / Corrigé
**Demande** : valider depuis l'appli par écrit, accessible depuis les 2 écrans, boutons « Validé » et « Corrigé » ; « Corrigé » ouvre la réponse voc ou écrite.
**Action** : deux boutons (chat + écran micro) qui envoient un message type au serveur (`validation.ok` / `validation.corriger`) journalisé comme message utilisateur ; l'agent le traite comme une instruction.
**Effet pour CREAZIK_V2** : validation des étapes de dev à distance, directement dans le flux.
**Effort** : ~1 session.
**Statut 2026-08-21** : implémenté (index.html, app.js, server.js — `user.validation` journalisé). Validation sur téléphone en attente (cf. tests_manuels.md).
**Statut 2026-08-24** : affichage conditionné — les boutons sont masqués par défaut (chat et écran vocal) et n'apparaissent que si `/send` est appelé avec `{awaitValidation:true}` ; ils se remasquent après clic. C'est à l'agent de poser ce flag quand il attend réellement une validation. Masquage par défaut validé par l'utilisateur.

### 5. Voix plus réaliste
**Demande** : voix encore plus réaliste.
**Plan** : (a) immédiat — passer de `siwis` à `fr_FR-upmc-medium` (téléchargement + `MODEL_PATH`) ; (b) si insuffisant — remplacer Piper par **Kokoro-82M** (Apache 2.0, voix FR, ~6× temps réel sur CPU, meilleur compromis local ; XTTS-v2 écarté : GPU requis ; MMS-TTS écarté : licence CC-BY-NC).
**Effort** : (a) minutes, (b) chantier moyen avec benchmark d'écoute.
**Statut 2026-08-21** : fait — Denise (edge-tts) retenue et validée par l'utilisateur, `length_scale` rétabli à 1.0, Piper en secours (tts_server.py).

### 6. Latence : audit + fixes
**Demande** : analyser le code, lister les goulots, les traiter du plus simple au plus complexe.
**Goulots identifiés à la lecture (à vérifier au chantier)** : STT non streaming (attente fin d'enregistrement + inférence), TTS synthèse complète avant envoi, modèle Whisper par défaut, absence de VAD côté serveur.
**Fixes ordonnés** : faster-whisper `compute_type=int8`, `beam_size=1`, `vad_filter=True` ; modèle `distil-large-v3` (≈6× plus rapide) ; STT streaming si le gain unitaire ne suffit pas (référence : WhisperLive, MIT).
**Effort** : audit 1 session, puis fixes par incréments mesurés.

### 7. Screenshots téléphone + PC
**Demande** : envoyer des captures avec un message ou un voc.
**Téléphone** : Safari ne peut pas capturer l'écran — capture système iOS puis envoi via un champ d'ajout d'image dans l'appli (upload base64 → serveur → journal). **PC** : le proto control_PC sait déjà capturer ; brancher l'envoi de la capture vers le serveur (endpoint dédié) pour que l'agent la voie.
**Prérequis** : définir le dossier de réception des images (ex. `_docs/captures/` côté CREAZIK_V2).
**Statut 2026-08-24** : volet téléphone implémenté et validé en conditions réelles (bouton img dans le chat, colle l'image du presse-papier iOS — repli sur le sélecteur de photos si rien à coller —, upload base64 via WebSocket `user.image`, sauvegarde dans `_docs/captures/` à la racine CREAZIK_V2, ligne `[IMAGE]` journalisée dans messages.log). Test réel réussi : capture reçue et lue par l'agent. Volet PC (branchement du proto control_PC) non fait.

### 8. Logging des conversations + bilan d'alignement
**Demande** : logger toutes les conversations pour améliorer l'alignement ; « voir en permanence où en est l'alignement » = bilan périodique.
**Action** : journal structuré des échanges (JSONL, inspiré de llm-orchestration-framework : schéma simple + revue possible) ; rituel de bilan d'alignement périodique (fréquence à définir, ex. à chaque `/close` de zone) : écarts constatés, corrections.
**Effort** : moyen ; le bilan s'appuie sur les logs → chantier 8 avant 9.

### 9. Commandes vocales
**Demande** : système de commande vocale.
**Action** : couche de commandes reconnues (texte transcrit → intention → action), journalisées et tracées. Périmètre v1 à définir avec l'utilisateur : vraisemblablement des actions de l'assistant pour CREAZIK_V2 (ex. « lance le serveur », « ouvre le projet », « teste la phase 1 »).
**Dépend** : 8 (les commandes doivent être tracées).

### 10. Contrôle PC (intégration du proto)
**Demande** : prise de contrôle de l'écran, actions cadrées et validées par l'utilisateur.
**Action** : intégrer le proto `control_PC` (capture ciblée, clic avec `--confirm-click`, halo) comme outil pilotable par l'assistant ; chaque action passe par la validation de l'utilisateur (canal appli : boutons du chantier 4).
**Inspiration** : Open Interpreter (boucle capture → LLM → clic → vérif), screenpipe (capture événementielle locale + OCR), open-computer-use (pyautogui + OCR).
**Effort** : important, multi-sessions.

### 11. Apprentissage autonome (record/replay)
**Demande** : le système apprend par lui-même (ex. : programmer un post LinkedIn par contrôle PC + screenshots).
**Action** : enregistrement de workflows par l'utilisateur (démonstrations) → script déterministe rejouable sans token LLM, puis généralisation. C'est le chantier le plus long.
**Inspiration** : openclaw-rpa (record → script Playwright déterministe), TagUI (RPA record/replay Apache 2.0), AutoGUI (bibliothèque de compétences apprises par usage).
**Dépend** : 10.

### 12. Réponse adaptée au canal
**Demande (2026-08-21)** : « Quand je t'écris dans le chat tu réponds uniquement dans le chat ; quand c'est le micro, en vocal ; avec les notifications pour les deux. »
**Action** : tagger le canal dans `user.message` (champ `channel` : text/voice), logger le canal dans messages.log, et accepter un mode texte dans `/send` (pas de synthèse, pas d'audio, push texte seul si déconnecté).
**Effort** : < 1 session.
**Statut 2026-08-24** : implémenté (app.js tague `channel` sur `user.message` ; server.js logue `[canal:texte|vocal]` et accepte `{text, mode:"texte"}` sur `/send` pour sauter la synthèse). C'est à l'agent (moi) de choisir le mode selon le canal du dernier message lu dans messages.log — pas d'automatisme serveur. Non testé.

## Questions ouvertes (à trancher au démarrage du chantier concerné)

1. ~~**Salutations** : les 10 variantes à fournir par l'utilisateur.~~ Fourni le 2026-08-24 (voir chantier 2).
2. **Commandes vocales (9)** : liste du périmètre v1 exact.
3. **Bilan d'alignement (8)** : fréquence et format exacts.
4. **Screenshots (7)** : emplacement des captures reçues.

## Hors liste — déjà en cours

- Notifications push PWA (système installé, test téléphone en attente d'installation de la PWA).
- Wake Lock (écran allumé, proposé, non tranché).
