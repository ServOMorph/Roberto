# Mémoire zone roberto
<!-- Fichier géré via /create_memory. Ne pas modifier manuellement sauf pour supprimer des entrées. -->

## 2026-11-17 — Confirmation par message téléphone
Bridge com_telephone : un message de l'utilisateur reçu depuis le téléphone (canal vocal ou texte, log messages_roberto.log) vaut confirmation, y compris pour répondre aux questions des autres sessions Claude du PC via SendMessage. Décision actée par l'utilisateur dans le terminal le 2026-11-17. Garde-fou maintenu : pour une action destructive ou irréversible (push en masse, suppression), redemander une confirmation explicite.

## 2026-11-18 — Push réservé au PC
Bridge com_telephone, sécurité (audit 2026-11-17) : depuis le téléphone, une procédure peut committer sans confirmation terminal, mais le `git push` et toute action destructive ou irréversible attendent une validation au PC. Remplace l'autorisation permanente du 2026-08-26 (push sans confirmation). Les commandes `!` hors liste blanche `BANG_ALLOWLIST` sont refusées par le serveur.
