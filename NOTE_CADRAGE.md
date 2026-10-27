# Note de cadrage — Copilote IA, parc de capteurs IoT

Groupe : …  ·  Date : …

## 1. Terrain choisi et justification

Parcours IoT, terrain « parc de capteurs ». Pourquoi ce choix : …

## 2. Le parc simulé

| Paramètre | Choix |
|---|---|
| Nombre de capteurs | |
| Types de mesure | |
| Passerelles | |
| Zones | |
| Période d'émission | |
| Durée simulée | |
| Part de trames anormales | |
| Transport simulé | |

Champs de trame : `sensor_id`, `hw_fingerprint`, `gateway_id`, `seq`, `ts_measure`, `ts_received`, `value`, `unit`, `battery_mv`, `rssi_dbm`, `zone`, `label`.

## 3. Ce que l'IA détecte

| Cas | Ce qu'on injecte | Signature | Action proposée | Étiquette |
|---|---|---|---|---|
| Capteur défaillant | | | | `defaillant` |
| Dérive | | | | `derive` |
| Capteur cloné | | | | `clone` |

## 4. La fausse alerte

Rejeu de tampon : pourquoi ce n'est pas un incident, comment le reconnaître, comment le distinguer d'un rejeu malveillant.

## 5. Premiers choix d'IA

| Besoin | Famille retenue | Pourquoi | Alternative écartée |
|---|---|---|---|
| | | | |

Modèle LLM retenu : … (latence mesurée : …)

## 6. Premiers risques

| Menace | Exemple | Parade prévue |
|---|---|---|
| | | |

## 7. Rôles

Données : … · Modèles : … · Intégration : … · Sécurité & évaluation : …
