# Journal de décisions

Une ligne par décision, la plus récente en bas.

| Date | Décision | Pourquoi | Alternatives écartées | Qui |
|---|---|---|---|---|
| 2026-10-27 | Terrain IoT « parc de capteurs » | Signatures mesurables, fausse alerte réaliste, tout se simule | Énergie d'un bâtiment | Groupe |
| 2026-10-27 | Trames avec `seq` + `ts_measure` + `ts_received` | Seul moyen de distinguer un rejeu de tampon d'un clone | Un seul horodatage | Groupe |
| 2026-10-27 | Inférence 100 % locale avec Ollama | Règle n° 3 du sujet | API cloud | Groupe |
| 2026-10-29 | Parc de 40 capteurs, 4 passerelles, 8 zones, 1 trame / 5 min, 14 jours | 5 capteurs par zone : assez de voisins pour la médiane ; 161 280 trames, un CSV suffit | 100 capteurs (inutilement lourd) | Groupe |
| 2026-10-29 | Capteur combiné : `temp_c` et `hum_pct` dans la même trame | Chaque capteur a 4 voisins comparables ; un seul `seq` par trame | `value` + `unit`, une trame par mesure | Groupe |
| 2026-10-29 | Transport par fichier CSV | Suffisant pour la détection, reproductible | MQTT local (option si le temps le permet) | Groupe |
| 2026-10-29 | Rejeu de tampon signalé « probablement normal », niveau info, sans action | L'opérateur voit la rafale ; il faut lui expliquer pourquoi ce n'est pas un incident | Ne rien signaler | Groupe (à confirmer au point jalon) |
| 2026-10-29 | Coupure de passerelle = événement d'exploitation, pas incident capteur | Elle touche le transport, pas la mesure | Incident à part entière | Groupe (à confirmer au point jalon) |
| 2026-10-29 | Rejeu malveillant (`seq` déjà vus, sans trou de réception) traité comme `clone` | Même parade : données non fiables + alerte sécurité | Quatrième incident à part | Groupe |
| 2026-10-29 | Score : règles + Isolation Forest + CUSUM ; le LLM explique seulement | Le score doit être calculé et testable | LLM qui décide | Groupe |
| 2026-10-29 | LLM `llama3.2:3b`, repli `llama3.2:1b` | Tient sur une VM de 8 Go ; 4 s au premier appel, 0,1 s ensuite (PC perso) | `llama3.1:8b` (16 Go de RAM) | Groupe (latence à remesurer sur la VM) |

## Questions pour le point jalon

- Le `.docx` du kit et la page en ligne divergent (8 ou 15 tests, démo de 5 ou 20 min, rapport de 4 à 6 pages ou libre) : quelle version fait foi ?
- Le dataset JSONL et la base de 5 documents du kit sont-ils attendus ?
- La coupure de passerelle doit-elle être signalée comme un incident à part ?
- Un transport MQTT local est-il un plus, ou le CSV suffit-il ?
- Quel modèle LLM est réaliste sur les VM de la salle ?

Réponses de l'enseignant : …
