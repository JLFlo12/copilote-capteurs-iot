# RT-02 — Runbook : capteur défaillant

## Symptômes

- **Valeur figée** : écart-type nul sur au moins 12 trames (1 h) alors que les voisins de zone varient.
- **Pics hors plage** : température hors [−20 ; 60] °C ou humidité hors [0 ; 100] %. Physiquement impossible en intérieur.
- **Silence** : plus de trame depuis 15 min alors que les autres capteurs de la même passerelle émettent.

## Diagnostic

1. Comparer aux voisins de la zone : s'ils sont normaux, le problème est le capteur, pas la pièce.
2. Si **toute** la passerelle se tait : ce n'est pas un défaut capteur, voir RT-05.
3. Vérifier `battery_mv` : une batterie basse explique souvent un silence ou des pics.

## Action

- Action de la liste blanche : `ticket_inspection` (inspection sur site).
- En attendant, les mesures concernées peuvent être marquées `donnees_non_fiables`.
- Ne jamais supprimer les mesures : elles servent de preuve.
