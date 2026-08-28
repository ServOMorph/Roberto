# Vocabulaire commun — com_tel

Glossaire de référence pour développer l'appli et les process du système de communication
vocale téléphone / Claude Code. Défini avec l'utilisateur, terme par terme. Vivant : de
nouveaux termes seront ajoutés au fil des sessions.

## com_tel
Le système complet de communication vocale entre le téléphone et les sessions Claude Code :
la PWA mobile, le bridge, et les commandes associées.

## bridge
Les trois processus serveur qui relaient les messages :
- Node — port 5000, HTTP + WebSocket, sert la PWA ;
- STT — port 5001, transcription vocale ;
- TTS — port 5002, synthèse vocale.

Hébergé par le projet Roberto.

## projet
Une base de code raccordée au bridge, représentée par un bouton dans le sélecteur de la PWA.
Chaque projet a son identifiant, son log de messages, son dossier de captures, et une session
Claude Code qui surveille son log. Exemples : `roberto`, `ia_life`, `tsa`, `creazik_v2`.

## raccordé / autonome (modes de déploiement)
- **raccordé** — le projet utilise le bridge partagé de Roberto, sans copie du serveur
  (README + commande `/roberto` + entrée dans le registre). Mode par défaut et standard :
  tous les nouveaux déploiements se font en raccordé.
- **autonome** — copie complète et indépendante du serveur, avec ses propres ports et sa
  propre config. Modèle d'origine de creazik. Conservé pour référence historique, plus
  utilisé pour les nouveaux déploiements.

## canaux étanches
Le téléphone (la PWA) et la conversation Claude Code sont deux canaux séparés. Écrire dans
l'un ne transmet rien à l'autre. Toute réponse à un message venu du téléphone doit repartir
explicitement par le bridge (`POST /send`), même si elle est déjà écrite dans la conversation
Claude Code.
