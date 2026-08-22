# Signals — roberto   (MAJ 2026-08-22)

## Actions ouvertes
- [P1|ouvert] Récupérer la version corrigée de com_manager.md par l'utilisateur depuis la copie ROBERTO de creazik_v2 (il modifie et teste, bugs constatés au lancement). fait quand: l'utilisateur confirme que ses tests sont OK et demande de prendre sa version. réf: D:\ServOMorph\creazik_v2\ROBERTO\com_telephone\_commands\com_manager.md (version en test), D:\ServOMorph\Roberto\com_telephone\_commands\com_manager.md (source à mettre à jour)
- [P2|ouvert] Fiabiliser la livraison des messages `/send` en cas de coupure WebSocket (Safari iOS décharge l'onglet en arrière-plan, message perdu sans rattrapage). fait quand: un mécanisme de file d'attente ou de ré-émission est en place, ou décision explicite de ne pas le faire. réf: com_telephone/voice-code-bridge/server/server.js (endpoint /send), com_telephone/voice-code-bridge/mobile/app.js (reconnectTimer)

## Dernière session
<!-- Écrasé intégralement par /close. Synthèse < 25 lignes. -->
# Session du 2026-08-22

## Décisions prises
- Convention de déploiement : tout livrable ServOMorph s'installe dans un dossier ROBERTO à la
  racine du projet cible ; si du contenu ServOMorph y existe déjà, l'analyser sans le vider.

## Livrables produits ou modifiés
- com_telephone/DEPLOYMENTS.md : créé (registre des installations, convention en en-tête)
- D:\ServOMorph\creazik_v2\ROBERTO\com_telephone : installé (copie complète, AUTH_TOKEN dédié, npm install)
- tests_manuels.md : vidé (correctif bulle validé)

## Hypothèses validées / invalidées
- VALIDE : correctif CSS bulle (vert/orange après pause) — confirmé par l'utilisateur
- EN ATTENTE : com_manager.md modifié et testé par l'utilisateur côté creazik_v2 (bugs constatés
  au lancement) — récupération de sa version à sa demande

## Prochaine étape exacte
Quand l'utilisateur confirme ses tests sur com_manager.md (copie creazik_v2\ROBERTO), copier cette
version vers la source com_telephone/_commands/.

## Question bloquante pour la session suivante
Aucune
