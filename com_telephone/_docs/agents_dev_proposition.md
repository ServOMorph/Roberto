# Proposition — agents de dev pour com_tel (à décider plus tard)

Proposé le 2026-08-28, mis en attente par l'utilisateur ("note le pour plus tard").
But : découper le développement de com_tel en agents spécialisés (modèle zone-agent,
cf. `agent_role.md` du kit). Non validé, non implémenté.

## Agent Bridge (serveur)
Périmètre : `voice-code-bridge/server/server.js`, protocole WebSocket, routage multi-projets,
endpoints HTTP, `projects.json`, `push_subs.json`, sécurité (audit `audit_securite_2026-08-28.md`),
serveurs Python STT (`stt_server.py`) et TTS (`tts_server.py`).
Responsabilités : fiabilité de livraison des messages, modèle de menace, format du protocole.
Hors périmètre : UI PWA, procédures de déploiement.

## Agent PWA (mobile)
Périmètre : `voice-code-bridge/mobile/` (`index.html`, `app.js`, `sw.js`).
Responsabilités : UX téléphone (écran d'accueil, chat, capture vocale, validations, choix),
notifications push côté client, compatibilité iOS/Safari (safe-area, standalone, bfcache,
socket zombie), offline / service worker, dé-duplication `mid`.
Hors périmètre : logique serveur, TTS/STT.

## Agent Déploiement & Ops
Périmètre : `_commands/com_manager.py`, commandes `/roberto` et `/com_telephone_init`
(Roberto + projets raccordés), `DEPLOYMENTS.md`, `_docs/`, `tests_manuels.md`.
Responsabilités : onboarding d'un projet raccordé, procédures de bascule / redémarrage du
bridge, registre des déploiements, documentation (dont `vocabulaire.md`), file des tests manuels.
Hors périmètre : code applicatif serveur/PWA.

## Interfaces communes
- `vocabulaire.md` : glossaire partagé, autorité sur les termes.
- Le protocole WebSocket est le contrat entre Bridge et PWA : tout changement de message
  (`type`, champs) se décide à deux.
- Toute évolution de `projects.json` ou d'un endpoint passe par Déploiement pour la doc.

## À faire si validé
- Créer `com_telephone/AGENTS.md` ou un `agent_role.md` par sous-dossier.
- Mettre à jour `zones.md` si les agents deviennent des zones à part entière.
