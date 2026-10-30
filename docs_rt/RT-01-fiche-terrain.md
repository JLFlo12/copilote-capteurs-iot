# RT-01 — Fiche terrain du parc de capteurs

Parc fictif de 40 capteurs combinés température + humidité (`CAPT-001` à `CAPT-040`), répartis dans 2 bâtiments (A, B) de 4 étages. Une zone = un étage d'un bâtiment (`BAT-A-E1` … `BAT-B-E4`), 5 capteurs par zone.

| Passerelle | Zones | Capteurs |
|---|---|---|
| GW-A | BAT-A-E1, BAT-A-E2 | CAPT-001 à 010 |
| GW-B | BAT-A-E3, BAT-A-E4 | CAPT-011 à 020 |
| GW-C | BAT-B-E1, BAT-B-E2 | CAPT-021 à 030 |
| GW-D | BAT-B-E3, BAT-B-E4 | CAPT-031 à 040 |

## Valeurs normales

- Une trame toutes les 5 min. Latence normale entre `ts_measure` et `ts_received` : moins de 10 s.
- Température : 19 à 23 °C, cycle jour/nuit (minimum vers 3 h, maximum vers 15 h).
- Humidité : 40 à 55 %.
- Batterie : 3000 à 3100 mV, baisse lente. En dessous de 2700 mV, prévoir un remplacement.
- RSSI : −85 à −60 dBm, stable pour un capteur fixe.

## Identité d'un capteur

- `hw_fingerprint` : empreinte matérielle, unique et fixe par capteur physique.
- `seq` : compteur strictement croissant, +1 à chaque trame.
- Un capteur est fixé au mur : il passe toujours par la même passerelle.

Toute contradiction sur ces trois points est un signal de sécurité, pas un défaut de mesure.
