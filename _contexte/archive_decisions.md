# Archive des décisions structurantes — roberto

Décisions déplacées ici par `/close` quand la liste de `contexte.md` dépasse 10 entrées.

- 2026-08-20 : Initialisation du protocole vibecoding.
- 2026-08-21 : AUTH_TOKEN de com_telephone stocké dans server/.env (hors git), chargé par
  com_manager.py avant le lancement de node — pas de secret en dur dans le code.
- 2026-08-21 : Convention de déploiement : tout ce qui vient de ServOMorph s'installe dans un
  dossier ROBERTO à la racine du projet cible. Si le projet a déjà du contenu ServOMorph,
  l'analyser avant, ne jamais le vider.
- 2026-08-25 : com_telephone remplacé intégralement par la version validée en réel dans creazik_v2
  (nouvelle source de vérité pour les futurs déploiements).
