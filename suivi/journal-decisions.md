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
| 2026-10-30 | Graine 2026, début le 02/11/2026 ; dérive à partir du jour 5 (10 jours) | Retrouve les ≈ 5 760 trames du plan ; données identiques à chaque génération | Données aléatoires à chaque fois | Florian |
| 2026-10-30 | Rejeu GW-C au jour 10 laissé sur CAPT-023 en dérive (9 trames étiquetées rejeu) | Cas réaliste : deux phénomènes en même temps | Décaler la coupure | Florian |
| 2026-10-30 | Pseudonymes HMAC tronqués (`CAPTEUR_f924e5`) plutôt que numéros (`CAPTEUR_1`) | Stables d'une alerte à l'autre, non réversibles sans la clé | Compteur (dépend de l'ordre d'arrivée) | Florian |
| 2026-10-30 | 7 documents `docs_rt` (RT-01 à RT-07) au lieu de 6 | Rejeu de tampon et clone séparés : le LLM cite le bon runbook | Un seul runbook « sécurité » | Florian |
| 2026-10-30 | 20 cas de test (`expected`, `forbidden`, `requires_sources`, format inspiré du TP5) | Grille de tests exigée par le sujet (≥ 8) ; couvre ses 8 questions adaptées à l'IoT et les attaques | Format maison | Florian |
| 2026-10-30 | Dataset `datasets/instructions-copilote.jsonl` (12 exemples `instruction/input/output`, pseudonymisés) | Livrable exigé par le sujet ; fixe le style de réponse attendu du copilote | Pas de dataset | Florian |
| 2026-10-30 | Rangement : seuls les README à la racine ; `suivi/` et `guides/` ; noms en minuscules-tirets ; une seule source par information | Dépôt plus lisible, plus de doublons | Garder les fichiers à la racine | Florian |
| 2026-10-30 | Rejeu de tampon reconnu par les 5 critères de RT-05 ; toute trame en retard qui en rate un est classée clone | Une fausse coupure ou un rejeu malveillant ne passe pas pour une panne réseau | Classer tous les retards en info | Florian |
| 2026-10-30 | Dérive : résidu lissé sur 24 h, CUSUM (k = 0,05, h = 20) ou pente > 0,1 °C/j sur 72 h ; alerte maintenue jusqu'au réétalonnage | Le lissage efface le cycle jour/nuit : 0 fausse alerte ; prix : 1,9 jour de délai | Seuil sur la valeur brute (bruit, cycle) | Florian |
| 2026-10-30 | Isolation Forest entraîné sur toutes les trames, 8 192 par arbre, 0,1 % signalées | Entraîné sur les jours 1 à 3, il ne trouvait rien (pas d'extrapolation) ; 256 par arbre ratait les anomalies rares | Jours 1 à 3 seulement | Florian |
| 2026-10-30 | Fusion : clone > défaillant > rejeu > dérive > inhabituel | La sécurité passe avant la maintenance ; un rejeu ne cache pas un clone | Une alerte par détecteur | Florian |
| 2026-10-30 | Interface web en Streamlit (`interface/app.py`), locale | En Python comme le reste : les 4 membres peuvent la modifier ; démo plus claire qu'un terminal | Flask + HTML/JS (plus long), terminal seul | Florian |

## Questions pour le point jalon

- Le `.docx` du kit et la page en ligne divergent (8 ou 15 tests, démo de 5 ou 20 min, rapport de 4 à 6 pages ou libre) : quelle version fait foi ?
- Le dataset JSONL et la base de 5 documents du kit sont-ils attendus ?
- La coupure de passerelle doit-elle être signalée comme un incident à part ?
- Un transport MQTT local est-il un plus, ou le CSV suffit-il ?
- Quel modèle LLM est réaliste sur les VM de la salle ?

Réponses de l'enseignant : …
