# kyogo.cdpvd_dashboards_store.features

Package dbt à ajouter à un projet `cssXX.dashboards_store` dérivé de CDPVD pour générer des tables de poststratification pertinentes pour Kyogo.

Il s’appuie sur les données et modèles RH du Core/CDPVD déjà configurés dans le projet du CSS. Les variables sont préparées dans `models/marts`, puis assemblées dans `models/design`.

## Table produite

La table `respondents` contient une ligne par employé admissible, avec :

- le matricule et le courriel;
- la catégorie de corps d’emploi;
- la tranche d’ancienneté, calculée depuis la date d’entrée au CSS;
- le lieu de travail principal;
- le statut d’engagement.

La population reprend les employés actifs du modèle CDPVD avec une paie enregistrée dans les deux dernières semaines.

## Installation

Placer ce dépôt à côté du projet CSS et des dépôts `cdpvd_dashboards_store` et `core.dashboards_store`, puis l’ajouter au `packages.yml` du projet CSS :

```yaml
packages:
  - local: ../kyogo.cdpvd_dashboards_store.features
```

Le projet CSS doit activer les modèles RH nécessaires, notamment `cdpvd_fact_activity_current`, `dim_employees`, `i_pai_dos`, `i_pai_dos_empl` et `i_pai_tab_lieu_trav`.

## Configuration et exécution

Un premier mapping des corps d’emploi est fourni dans `seeds/marts/human_resources/mapping_corps_emploi.csv`. Les catégories proposées sont à valider pour le CSS.

Le lieu de travail vient de `i_pai_dos_empl.lieu_trav` pour l’emploi principal (`ind_empl_princ = 1`). Son libellé vient de `i_pai_tab_lieu_trav.descr`. Aucun mapping local des lieux n’est requis.

La seed `seeds/marts/human_resources/mapping_statuts_engagement.csv` est fournie avec les codes et descriptions du référentiel de test Core (`tooling/nightly/dbt/seeds/marts/human_resources/stat_eng.csv`). Les regroupements proposés sont à valider pour le CSS ; les catégories ambiguës restent vides. Compléter ces catégories et ajouter les codes locaux avant exécution : les tests refusent les catégories vides et les répondants sans statut reconnu.

Le fichier [profiles-sample.yaml](profiles-sample.yaml) fournit un exemple de connexion pour CSSVT. La destination des tables dépend du profil dbt utilisé.

Depuis le projet CSS configuré :

```bash
dbt deps
dbt build --select +respondents
dbt test --select respondent_population workplace_labels
```
