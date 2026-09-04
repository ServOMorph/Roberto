# Tests manuels en attente

## Token d'authentification longue durée (planificateur nocturne)

Prérequis du planificateur : sans token longue durée, l'authentification peut expirer en pleine
nuit et toutes les tâches restantes échouent.

1. Dans un terminal interactif, lancer `claude setup-token` et suivre la procédure.
2. Vérifier ensuite qu'un `claude -p "dis bonjour" --output-format json` fonctionne dans un
   terminal neuf, sans invite d'authentification.

## Tâche planifiée Windows (planificateur nocturne)

Non créée : l'heure du coucher n'a pas été fixée et c'est une modification du système hors dépôt.
Remplacer `23:30` par l'heure voulue, dans un terminal **administrateur** :

```
schtasks /Create /TN "Planificateur nocturne Claude" /TR "\"D:\ServOMorph\Roberto\PLANIFICATEUR\lancer_nuit.cmd\"" /SC DAILY /ST 23:30 /F
```

1. `schtasks /Query /TN "Planificateur nocturne Claude"` renvoie bien la tâche.
2. `schtasks /Run /TN "Planificateur nocturne Claude"` : l'orchestrateur démarre, écrit dans
   `PLANIFICATEUR/logs/`, et le rapport HTML s'ouvre à la fin.
3. Vérifier que la tâche se déclenche bien session verrouillée (cocher "Exécuter même si
   l'utilisateur n'est pas connecté" seulement si nécessaire — cela demande le mot de passe).

## Nuit réelle (gate de la Phase 2 du planificateur)

1. Remplir `PLANIFICATEUR/queue.json` avec 2-3 tâches réelles sur `D:\ServOMorph\creazik_v2`.
2. Lancer `lancer_nuit.cmd` avant de dormir (ou laisser la tâche planifiée le faire).
3. Au réveil : le rapport `PLANIFICATEUR/rapport_<date>.html` est lisible, les statuts
   correspondent à l'état réel du dépôt, aucun `git push` n'a eu lieu.
4. Contrôler `git log` et `git branch` de creazik_v2 : uniquement des commits locaux sur des
   branches dédiées.
5. Si une limite de 5 h a été atteinte pendant la nuit : récupérer le log brut de la tentative
   dans `PLANIFICATEUR/logs/` et le conserver — c'est la donnée qui manque pour le parsing de
   l'heure de reset (Phase 3).

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
