# RT-03 — Runbook : dérive d'un capteur

## Symptômes

Une dérive est lente : chaque valeur prise seule reste plausible. Elle n'apparaît qu'en comparant le capteur à ses voisins.

- Résidu = valeur du capteur − médiane des 4 autres capteurs de la zone.
- Dérive probable si la pente du résidu dépasse 0,1 °C/jour sur 72 h, ou si le CUSUM du résidu dépasse son seuil.

## Diagnostic

1. Vérifier que les voisins sont stables entre eux (sinon, c'est la pièce qui change, pas le capteur).
2. Vérifier qu'il n'y a pas eu d'intervention récente (déplacement du capteur, source de chaleur).
3. Une dérive n'est pas urgente : les mesures restent exploitables avec une correction.

## Action

- Action de la liste blanche : `reetalonnage_planifie` (voir RT-04 pour la procédure).
- Noter l'écart estimé (en °C) dans le ticket pour l'intervenant.
