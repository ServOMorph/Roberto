# Tests manuels en attente

## Migration com_telephone vers Roberto — vérification finale

Pré-requis : pont démarré depuis Roberto (`py -3.11 com_telephone/_commands/com_manager.py status`
= 3 OK), appli PWA rechargée (fermer complètement, rouvrir).

1. **Lien téléphone inchangé** : ouvrir la PWA avec le lien habituel (token inclus) → elle se
   connecte sans redemander le token, sans réinstaller.
2. **Deux onglets** : la barre affiche `IA_Life` et `TSA` ; le bandeau du haut et la barre restent
   visibles sans scroller.
3. **Aller-retour IA_Life** : session Claude Code ouverte dans `D:\ServOMorph\IA_Life` + `/roberto`
   lancé. Sélectionner `IA_Life`, envoyer un message vocal → il arrive dans cette session (pas
   ailleurs), la réponse `POST /send` (`project: "ia_life"`) revient dans le fil et est lue.
4. **Aller-retour TSA** : session Claude Code ouverte dans `D:\ServOMorph\Appli_TSA_SDI_TDAH` +
   `/roberto` (re)lancé après la migration. Même test sur l'onglet `TSA`.
5. **Isolation** : les deux sessions actives → un message par onglet → chaque session ne voit que
   ses propres messages.
6. **Pas de doublon** : mettre l'appli en arrière-plan puis revenir plusieurs fois, envoyer un
   message → une seule bulle de réponse (correctif connexion WebSocket).
7. **Push** : appli fermée, faire répondre une session via `POST /send` → notification reçue,
   titrée `<label> · Assistant`.
8. **Init `raccorde`** : depuis une session dans Roberto, `/com_telephone_init <projet-test>
   raccorde` sur un vrai projet → entrée ajoutée au registre, `/roberto` dans ce projet, l'onglet
   apparaît dans la PWA, aller-retour OK.
9. **Init `autonome`** (optionnel) : `/com_telephone_init <projet-test> autonome` → serveur copié,
   `.env` à compléter, ports 5100+, `com_manager.py start` → lien appli distinct fonctionne.
10. **Reliquat IA_Life** : supprimer le dossier vide
    `D:\ServOMorph\IA_Life\ROBERTO\com_telephone\voice-code-bridge\` (`rmdir`) une fois le handle
    Windows libéré (fermer l'IDE si besoin).
