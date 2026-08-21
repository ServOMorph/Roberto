# Signals — roberto   (MAJ 2026-08-21)

## Actions ouvertes
- [P1|ouvert] Confirmer sur le téléphone que le correctif CSS (bulle verte/orange après pause) fonctionne. fait quand: l'utilisateur confirme voir vert puis orange après une pause/reprise du micro. réf: tests_manuels.md, com_telephone/voice-code-bridge/mobile/app.js et index.html
- [P2|ouvert] Fiabiliser la livraison des messages `/send` en cas de coupure WebSocket (Safari iOS décharge l'onglet en arrière-plan, message perdu sans rattrapage). fait quand: un mécanisme de file d'attente ou de ré-émission est en place, ou décision explicite de ne pas le faire. réf: com_telephone/voice-code-bridge/server/server.js (endpoint /send), com_telephone/voice-code-bridge/mobile/app.js (reconnectTimer)

## Dernière session (2026-08-21)
<!-- Écrasé intégralement par /close. Synthèse < 25 lignes. -->
Mise en service et débogage en conditions réelles de l'assistant vocal com_telephone (test depuis
un iPhone via le tunnel Cloudflare vertia-test.serenia-tech.fr). Prérequis manquants résolus :
npm install, AUTH_TOKEN généré (server/.env, chargé par com_manager.py), modèle vocal Piper
téléchargé. Bug confirmé et corrigé : pause/reprise du micro tronquait la fin du message (état
global partagé entre sessions d'enregistrement concurrentes) — refonte en sessions isolées dans
app.js, validée par test réel. Deuxième bug identifié : la bulle vocale reste grise (couleur pause)
au lieu de passer au vert/orange lors de l'envoi et de la réflexion — cause probable : conflit
CSS entre `.voiceCircle.paused` et `.voiceCircle.done/.thinking` (même spécificité, ordre de
déclaration). Correctif appliqué (réordonnancement CSS + retrait explicite de la classe `paused`
aux transitions), mais non reconfirmé par l'utilisateur avant l'arrêt des process en fin de
session. Les 3 process (node/stt/tts) et le Monitor de messages.log ont été arrêtés à la demande
de l'utilisateur.
