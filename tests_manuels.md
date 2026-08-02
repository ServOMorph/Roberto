# Tests manuels

## Fiabilité de la lecture OCR de la zone de contexte
Avec OpenCode ouvert et visible, cliquer « Tester » sur la zone créée à plusieurs valeurs de
contexte différentes (ex : 10 %, 45 %, 80 %) et vérifier que le pourcentage affiché dans
l'alerte correspond exactement à celui affiché par OpenCode. (50 % déjà confirmé en conditions
réelles via `conversation_test.py` le 2026-08-02.)

## Bannière de contrôle affichée tout le workflow
Redémarrer `py run.py`, lancer une session `conversation_test.py`, et vérifier que la bannière
rouge clignotante reste affichée dans l'UI depuis le tout début du workflow (avant même le
premier clic) jusqu'à la fin de la session — pas seulement pendant les phases de clic/frappe.
