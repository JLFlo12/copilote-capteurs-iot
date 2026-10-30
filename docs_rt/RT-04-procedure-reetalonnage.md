# RT-04 — Procédure de réétalonnage

Applicable après une alerte de dérive (RT-03).

1. Planifier l'intervention dans les 7 jours ; la dérive n'est pas une urgence.
2. Sur site, poser une sonde de référence étalonnée à côté du capteur pendant 30 min.
3. Calculer l'écart moyen capteur − référence.
4. Si l'écart dépasse 0,5 °C : appliquer la correction dans la configuration du capteur.
5. Si l'écart dépasse 2 °C ou revient en moins d'un mois : remplacer le capteur.
6. Marquer les mesures entre le début estimé de la dérive et l'intervention comme `donnees_non_fiables`.
7. Clôturer le ticket avec l'écart mesuré et la correction appliquée.

Le copilote ne réétalonne rien lui-même : il propose seulement de planifier l'intervention.
