# Tests manuels en attente

## Couleurs de la bulle vocale après pause/reprise
Vérifier sur le téléphone (com_telephone) qu'après une pause puis reprise du micro, la bulle passe
bien au vert ("Compris, j'envoie a Titi"), puis à l'orange ("Titi reflechit..."), puis de nouveau au
vert ("Titi vous repond...") — au lieu de rester grise. Correctif appliqué dans
`com_telephone/voice-code-bridge/mobile/app.js` et `index.html` (réordonnancement CSS + retrait
explicite de la classe `paused`), non reconfirmé par l'utilisateur avant fin de session.
