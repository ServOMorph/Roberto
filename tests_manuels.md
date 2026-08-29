# Tests manuels en attente

## Notifications push — téléphone verrouillé (fix socket zombie iOS)

Pré-requis : pont démarré depuis Roberto, PWA rechargée (fermer complètement, rouvrir),
notifications autorisées pour la PWA.

1. **Verrouillé, app en arrière-plan** : ouvrir la PWA, la mettre en arrière-plan, verrouiller le
   téléphone. Depuis une session PC, `POST /send` sur le projet sélectionné → notification reçue
   sur l'écran verrouillé dans les secondes qui suivent. Répéter 5 fois d'affilée à ~30 s
   d'intervalle : les 5 notifications arrivent.
2. **Au premier plan** : PWA ouverte et visible → `POST /send` → le message s'affiche dans le fil
   sans notification push (pas de spam).
3. **Retour après verrouillage** : après le test 1, déverrouiller et rouvrir la PWA → chaque
   message est présent une seule fois (pas de doublon dû au rejeu + push).
4. **Coupure réseau courte** : couper le wifi du téléphone 20 s pendant un `POST /send`, le
   rétablir → le message finit par arriver (rejoué à la reconnexion), une seule fois.

## Mise en veille du PC depuis la PWA

Pré-requis : bridge démarré, PWA rechargée.

1. **Confirmation** : écran d'accueil → bouton "Mettre le PC en veille" → une barre
   Annuler / Confirmer apparaît. "Annuler" → retour au bouton, rien ne se passe.
2. **Déclenchement** : "Confirmer" → le PC (Windows) se met effectivement en veille dans les
   secondes qui suivent ; la ligne `client.sleep: mise en veille du PC demandee` apparaît dans
   `server/messages.log`.
3. **Anti-rebond** : deux "Confirmer" à moins de 5 s d'intervalle → une seule mise en veille.
4. **Reprise** : au réveil du PC, le bridge tourne toujours (les 3 process survivent à la veille)
   ou, si besoin, `com_manager.py start` les relance.

## Pastille du bouton "Projets" (vue chat)

1. Être dans le chat d'un projet A. Faire répondre une session d'un projet B via `POST /send`
   → une pastille bleue apparaît sur le bouton "Projets" du bandeau.
2. Taper "Projets" → accueil → ouvrir B → revenir : la pastille du bouton disparaît une fois
   B ouvert (plus aucun autre projet non lu).
