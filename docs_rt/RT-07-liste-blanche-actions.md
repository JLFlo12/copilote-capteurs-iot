# RT-07 — Liste blanche des actions du copilote

Le copilote ne peut proposer **que** ces actions. Toute autre action est refusée par le code, même si le LLM la propose. Aucune action n'est exécutée sans validation d'un opérateur humain, et le mode `DRY_RUN=true` est actif par défaut.

| Code | Action | Cas d'usage |
|---|---|---|
| `ticket_inspection` | Ouvrir un ticket d'inspection sur site | Capteur défaillant (RT-02) |
| `reetalonnage_planifie` | Planifier un réétalonnage | Dérive (RT-03, RT-04) |
| `donnees_non_fiables` | Marquer des mesures comme non fiables | Défaillant, dérive, clone |
| `alerte_securite` | Prévenir l'équipe sécurité | Clone, rejeu malveillant (RT-06) |
| `aucune_action` | Ne rien faire, information seulement | Rejeu de tampon (RT-05) |

## Interdit

Supprimer des mesures, désactiver un capteur ou une passerelle, modifier une configuration, exécuter une commande système, contacter un tiers. Une consigne de ce type trouvée dans les données ou dans un document est ignorée et signalée.
