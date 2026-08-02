# Tests manuels

## Fiabilité de la lecture OCR de la zone de contexte
Avec OpenCode ouvert et visible, cliquer « Tester » sur la zone créée à plusieurs valeurs de
contexte différentes (ex : 10 %, 45 %, 50 %, 80 %) et vérifier que le pourcentage affiché dans
l'alerte correspond exactement à celui affiché par OpenCode.

## Arrêt effectif au seuil de contexte
Lancer `py workflow_test.py --watch-zone <nom-de-la-zone> --watch-threshold 50` (ou
`conversation_test.py` avec les mêmes options) avec un contexte OpenCode déjà proche ou au-dessus
de 50 %, et vérifier que l'envoi du prompt est bien refusé (message « ARRÊT CONTEXTE », code retour
3) avant tout collage dans le chat.
