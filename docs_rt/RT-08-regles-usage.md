# RT-08 — Règles d'usage du copilote et des données

## Rafales d'alertes

- Quand beaucoup d'alertes du même type arrivent en peu de temps sur une même passerelle (par exemple 200 alertes de batterie basse en 10 min), on ne crée pas un ticket par capteur.
- On regroupe les alertes par passerelle et par fenêtre de temps, et on ouvre un seul ticket qui les liste.
- Le nombre de tickets d'inspection est plafonné à 10 par jour et par passerelle. Au-delà, un humain décide.
- Une rafale soudaine sur toute une passerelle peut aussi venir de données falsifiées : vérifier les empreintes et les `seq` avant d'agir (RT-06).

## Données à ne jamais mettre dans un dataset ni dans un prompt

- Les identifiants réels des capteurs, passerelles et zones : on utilise les pseudonymes (`CAPTEUR_xxxxxx`, `GW_xxxxxx`, `ZONE_xxxxxx`).
- La clé de pseudonymisation `PSEUDO_KEY`, les mots de passe, les jetons et tout autre secret.
- La colonne `label` (vérité terrain) : elle sert seulement à l'évaluation.
- Des données réelles de personnes ou de sites.

## Validation humaine

- Le copilote propose, l'opérateur décide. Aucune action n'est exécutée sans validation humaine.
- Le mode `DRY_RUN` est actif par défaut : l'action validée est affichée et journalisée, pas exécutée.
- Une question sans réponse dans la documentation reçoit la réponse « information insuffisante » : le copilote n'invente pas de procédure.
