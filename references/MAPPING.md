# Proposition de mapping des corps d’emploi

## Provenance

La copie `references/eff_categories_emploi.csv` reproduit octet pour octet la seed `core.dashboards_store/seeds/dashboards/human_resources/efficacite/eff_categories_emploi.csv`. Elle contient les mêmes 585 lignes et valeurs que la seed personnalisée de CSSDL. Aucun CSV propre à CSSDHR n’a été trouvé : la documentation CSSDHR renvoie au mapper du Core, sans prouver que cette seed est son mapping spécifique. Cette provenance reste donc à confirmer avec le demandeur.

La seed dbt `mapping_corps_emploi.csv` conserve les trois colonnes d’origine, leur ordre, les valeurs, les accents, les codes avec zéros initiaux et les 585 lignes. Elle ajoute uniquement `corps_emploi`, la catégorie proposée. La copie originale reste hors du chemin des seeds dbt et n’est pas chargée comme une seconde table.

Il s’agit de propositions issues de la lecture des titres et de leur contexte dans le référentiel, pas d’une classification RH certifiée. Les 267 titres de la famille enseignante incluent des matières de formation professionnelle : « Frm prf électricité » désigne ainsi un enseignant, pas un électricien d’entretien. Le code générique de création Web de cette famille reste non classé.

## Répartition

| Catégorie proposée | Codes |
|---|---:|
| À déterminer | 18 |
| Gestionnaire | 144 |
| Professionnel | 45 |
| Enseignant | 266 |
| Soutien administratif | 11 |
| Paratechnique | 23 |
| Technique | 26 |
| Manuel | 52 |

## Choix proposés à vérifier

- Directions, directions adjointes, gestionnaires, coordonnateurs, régisseurs et contremaîtres : `Gestionnaire`, même si l’ancienne catégorie était « Professionnels direct ».
- Bibliothécaires, conseillers, psychologues, orthophonistes, analystes, ingénieurs et autres titres de la famille professionnelle : `Professionnel`.
- Secrétariat, agents de bureau, achat et téléphonie : `Soutien administratif`.
- Techniciens : `Technique`, y compris en administration, éducation spécialisée et service de garde.
- Éducateurs en milieu scolaire, préposés aux élèves handicapés, surveillants, appariteurs et fonctions auxiliaires/opérateurs : `Paratechnique`.
- Métiers de construction, entretien, conciergerie, cuisine et conduite : `Manuel`.

Les titres tronqués ou locaux suivants demandent particulièrement une validation :

| Codes | Proposition | Point à confirmer |
|---|---|---|
| 1316, 1400, 1412, 1430, 1442 | Gestionnaire | Conseiller en gestion/direction dans la famille cadre, et non professionnel conseil |
| 1603, 1612, 1613, 1810, 1811, 1820, 1926, 1956 | Gestionnaire | Adjoint administratif, agent d’administration ou chef de secrétariat dans la famille cadre |
| 4104, 4105, 4201, 4202, 4203 | Paratechnique | Auxiliaires et opérateurs informatiques, distincts des techniciens |
| 4108, 4109, 4110 | Paratechnique | Magasiniers : frontière locale avec le soutien administratif |
| 4117, 4118, 4221, 4229, 4232, 4233, 4283 | Paratechnique | Reprographie, imprimerie et reliure : frontière avec le manuel |
| 4206 | Technique | Infirmier : catégorie du poste à confirmer, pas son titre professionnel au sens réglementaire |
| 4217 | Paratechnique | Infirmier auxiliaire : classification locale à confirmer |
| 4219, 4222, 4227 | Technique | Dessinateur, photographe et taxidermie |
| 4282 | Paratechnique | Inspecteur en transport scolaire |
| 4284, 4288 | Paratechnique | Éducateur scolaire et classe principale, distincts du technicien en service de garde |
| 4199 | Soutien administratif | Ancien code de soutien aux élections |
| 9104, 9108, 9120 | Professionnel | Conseil pédagogique externe, animation pastorale et analyse; admissibilité à la population gérée en amont |

## Codes sans proposition

La catégorie reste vide lorsque le titre ne permet pas un choix fiable parmi les sept catégories. Aucune huitième catégorie « Autre » n’est créée et aucun code n’est supprimé. Le test de complétude de `respondents` échoue si un de ces codes est effectivement utilisé dans la population admissible.

| Code | Titre source |
|---|---|
| 0105 | Commissaire |
| 0106 | Représ. Parents |
| 0107 | Étudiant activité sport. |
| 0109 | Membre du CA |
| 0110 | Tuteur |
| 0505 | Louage de services n/a |
| 2999 | PNE création pour Web |
| 3999 | Ens création pour Web |
| 4000 | Soutien |
| 4999 | 4*** création pour Web |
| 5000 | Soutien |
| 5999 | 5*** création pour Web |
| 6001 | Autre |
| 9107 | Anim. ext. |
| 9200 | Tuteur collégial |
| 9500 | Organisation d'évènements |
| 9600 | Entraineur/activité |
| 9700 | Stagiaire |
