# Mesures de la détection (J3)

Généré par `evaluation/mesures.py`. Les détecteurs ne lisent jamais `label` : il sert seulement ici, à mesurer.

Données : 160824 trames, graine 2026.

## Par type de trame

| Type | Trames réelles | Trames détectées | Correctes | Précision | Rappel |
|---|---|---|---|---|---|
| defaillant | 90 | 90 | 90 | 100.0% | 100.0% |
| derive | 5751 | 4683 | 4683 | 100.0% | 81.4% |
| clone | 288 | 288 | 288 | 100.0% | 100.0% |
| replay_tampon | 150 | 150 | 150 | 100.0% | 100.0% |

## Objectifs

| Objectif | Résultat |
|---|---|
| Trames normales classées en incident | 0 |
| Rejeux de tampon classés en incident (objectif : 0) | 0 |
| Silence de CAPT-036 signalé | oui |
| Délai de détection de la dérive | CAPT-007 : 1.9 j, CAPT-023 : 1.8 j |

## Alertes produites

| Type | Alertes |
|---|---|
| inhabituel | 11 |
| defaillant | 3 |
| derive | 2 |
| replay_tampon | 2 |
| clone | 1 |

## Isolation Forest seul

Ce que le modèle signale sans les règles (les 0,1 % de trames les plus isolées). Dans la fusion, ces trames prennent le verdict des règles quand une règle s'applique.

| Type de trame | Trames | Signalées par l'Isolation Forest |
|---|---|---|
| normal | 154545 | 11 |
| defaillant | 90 | 33 |
| derive | 5751 | 5 |
| clone | 288 | 0 |
| replay_tampon | 150 | 112 |

## Attaques

| Scénario | Attendu | Résultat |
|---|---|---|
| Fausse coupure : 5 trames à empreinte inconnue dans une rafale de GW-B | clone | 5/5 |
| Rejeu malveillant : 12 anciennes trames renvoyées sans coupure | clone | 12/12 |
