# Décisions archivées — roberto

- 2026-08-02 : Initialisation du protocole vibecoding.
- 2026-08-02 : Macrodesk utilise Python/PyWebView avec hooks globaux, validation OpenCV des clics et stockage local des macros.
- 2026-08-02 : Le contrôle d'OpenCode passe par le presse-papiers (`Ctrl+V`) et des réponses-fichiers afin de préserver une boucle agentique observable.
- 2026-08-02 : Ajout de zones de surveillance OCR (lecture du contexte OpenCode) avec sélection par overlay multi-écrans et pipeline OCR renforcé.
- 2026-08-02 : Les scripts de workflow OpenCode peuvent refuser un envoi de prompt selon une zone OCR et un seuil de contexte (`--watch-zone`/`--watch-threshold`).
- 2026-08-02 : Avant toute relance de conversation_test.py/workflow_test.py (prise de contrôle machine vers OpenCode), inspecter l'état réel du projet cible (fichiers, roadmap) plutôt que supposer la continuité — aucune perte d'information tolérée. Échap interrompt la session en cours et journalise l'état pour reprise.
- 2026-08-02 : Quand une macro Macrodesk est recréée/réenregistrée, analyser son macro.json (events, contextes de vérification visuelle) avant de relancer un test — un clic avec image de référence sur un arrière-plan de chat qui évolue (historique) échoue quasi systématiquement ; le remplacement du clic « Envoyer » par un appui sur Entrée (sans vérification image) contourne ce problème.
- 2026-08-02 : Quand le seuil de contexte OCR est atteint, le pont envoie automatiquement une commande de compactage à l'agent et attend sa confirmation écrite avant de renvoyer le prompt — pas de blocage manuel à arbitrer à chaque fois.
- 2026-08-02 : Un `AGENTS.md` à la racine du projet cible centralise les règles fixes pour l'agent piloté (phase unique, contraintes, format de compte rendu) — le prompt de tour se limite au contexte dynamique, réduisant fortement sa taille sans perte d'exigence.
