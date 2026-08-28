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
