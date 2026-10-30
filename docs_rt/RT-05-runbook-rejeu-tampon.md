# RT-05 — Runbook : rejeu de tampon après coupure de passerelle

## Ce que c'est

Quand une passerelle perd sa liaison, ses capteurs gardent leurs mesures en mémoire et les renvoient en rafale au retour. Les mesures sont vraies : seul leur transport a été retardé. **Ce n'est pas un incident capteur.**

## Les 5 critères, tous nécessaires

1. Aucune trame reçue de **tous** les capteurs de la passerelle pendant au moins 15 min.
2. Au retour, `ts_received − ts_measure` > 5 min pour les trames de la rafale.
3. Les `seq` reprennent exactement à la suite du dernier reçu, sans doublon.
4. Les `ts_measure` comblent le trou.
5. Même `hw_fingerprint` qu'avant la coupure.

## Conduite à tenir

- Si les 5 critères sont réunis : signaler « probablement normal : rejeu de tampon après coupure de GW-x », niveau info, action `aucune_action`. Noter la coupure comme événement d'exploitation.
- Si un seul critère manque (`seq` déjà vu, empreinte différente, pas de vrai trou de réception) : ce n'est **pas** un rejeu de tampon. Traiter comme un clone ou un rejeu malveillant, voir RT-06.
