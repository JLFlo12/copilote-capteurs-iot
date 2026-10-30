# RT-06 — Procédure : capteur cloné ou rejeu malveillant

## Symptômes

- Deux `hw_fingerprint` différentes pour le même `sensor_id` en moins d'1 h.
- Le même `seq` reçu deux fois avec des valeurs différentes.
- Un capteur fixe vu sur deux passerelles.
- Rejeu malveillant : des `seq` déjà reçus, sans coupure réelle de la passerelle avant.

## Conduite à tenir

1. Considérer **toutes** les données de cet identifiant comme suspectes depuis la première anomalie.
2. Actions de la liste blanche : `donnees_non_fiables` **et** `alerte_securite`.
3. L'équipe sécurité identifie l'émetteur légitime (empreinte connue dans l'inventaire).
4. Ne pas désactiver le capteur ni supprimer de données à distance : les traces servent à l'enquête.
