# Archive des décisions structurantes — roberto

Décisions déplacées ici par `/close` quand la liste de `contexte.md` dépasse 10 entrées.

---
- 2026-08-28 : Vocabulaire commun figé (`_docs/vocabulaire.md`) : com_tel, bridge, projet,
  raccordé/autonome, canaux étanches. Termes retenus : "com_tel" (pas "Com"), "bridge" (pas "pont").

---
- 2026-08-28 : creazik_v2 raccordé au bridge ; fin de la dernière copie autonome. Tous les
  déploiements se font désormais en mode raccordé (autonome = référence historique seulement).

---
- 2026-08-28 : Roberto devient l'hôte du pont (le serveur y tourne) ; IA_Life et TSA sont des
  projets raccordés. `.env` d'IA_Life réutilisé tel quel (lien téléphone + push préservés).
  Commande `/com_telephone_init` ajoutée pour les futurs déploiements.

---
- 2026-08-28 : com_telephone rendu multi-projets (routage par `project`, `projects.json`, sélecteur
  PWA) — développé et durci dans IA_Life, puis promu ici comme template unique.

- 2026-08-20 : Initialisation du protocole vibecoding.
- 2026-08-21 : AUTH_TOKEN de com_telephone stocké dans server/.env (hors git), chargé par
  com_manager.py avant le lancement de node — pas de secret en dur dans le code.
- 2026-08-21 : Convention de déploiement : tout ce qui vient de ServOMorph s'installe dans un
  dossier ROBERTO à la racine du projet cible. Si le projet a déjà du contenu ServOMorph,
  l'analyser avant, ne jamais le vider.
- 2026-08-25 : com_telephone remplacé intégralement par la version validée en réel dans creazik_v2
  (nouvelle source de vérité pour les futurs déploiements).
- 2026-08-25 : com_manager.py affiche le lien appli (token) au démarrage et démarre tout par
  défaut sans argument — nécessite TUNNEL_URL dans .env en plus d'AUTH_TOKEN.
