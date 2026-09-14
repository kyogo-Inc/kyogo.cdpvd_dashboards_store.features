# kyogo.cdpvd_dashboards_store.features

Package dbt SQL Server consommé par un projet CSS dérivé de CDPVD. Il produit `respondents`, une table catégorielle contenant une ligne par employé admissible, à partir des modèles CDPVD/Core déjà configurés par le CSS.

Le nom dbt du package est `kyogo_cdpvd_dashboards_store_features`.

## Organisation

- `models/marts/human_resources/staging` : population admissible, courriel du Core et date d’entrée.
- `models/marts/human_resources/features` : correspondances des codes et calcul des catégories.
- `models/design` : table catégorielle finale, matérialisée en table.
- `seeds/marts/human_resources` : proposition de mapping des corps d’emploi et contrats des mappings locaux.
- `references` : copie intacte du référentiel de départ et décisions de classement à valider.
- `tests` : conservation de la population et validité des libellés de lieux.
- `dev/check.py` : contrôles SQL avec données fictives uniquement.

Les modèles intermédiaires sont éphémères. Le package ne crée pas de matrice numérique ni de modèle statistique MRP.

## Nommage et destination

Aucun modèle, seed ou test ne porte de préfixe `kyogo`. Le nom du projet dbt reste celui du package. La base et le préfixe de schéma viennent du profil du consommateur; les suffixes fonctionnels sont `human_resources` et `design`.

Le package hérite des macros `generate_schema_name` et `generate_alias_name` de dbt Core, comme le Core/CDPVD local, sans les recopier ni les remplacer. Une surcharge définie par le projet consommateur reste prioritaire. Avec les macros par défaut et `target.schema: kyogo`, la table finale est `<target.database>.kyogo_design.respondents`. Avec un autre profil, le nom `respondents` reste identique et sa destination change.

## Contrat de sortie

| Colonne | Contenu |
|---|---|
| `matr` | Identifiant employé dans le CSS, unique et non nul |
| `courriel` | Courriel du Core, normalisé, unique et non nul |
| `corps_emploi` | Enseignant, Soutien administratif, Technique, Paratechnique, Manuel, Professionnel ou Gestionnaire |
| `tranche_anciennete` | 0–5 ans, 6–10 ans, 11–15 ans, 16–20 ans ou 21 ans et plus |
| `lieu_travail_principal` | École ou regroupement CSS, selon la seed locale |
| `statut_engagement` | Régulier, Temporaire ou remplaçant, Occasionnel |

Seules les quatre dernières colonnes sont des variables catégorielles. Le matricule et le courriel servent à l’identification et au contact; ils ne sont pas des prédicteurs MRP. Aucun nom, âge, date de naissance ou montant de paie n’est ajouté.

## Dépendances et intégration

L’arborescence locale attendue est :

```text
workspace/
├── core.dashboards_store/
├── cdpvd_dashboards_store/
├── kyogo.cdpvd_dashboards_store.features/
└── cssXX.dashboards_store/
```

Le `packages.yml` livré utilise CDPVD comme dépendance locale. Le projet consommateur doit résoudre une seule version de CDPVD et du Core, compatible avec son dérivé. Pour une installation distante, remplacer le chemin local par la référence Git validée lors de la publication du package; aucune référence distante n’est inventée ici.

Ajouter dans le `packages.yml` du consommateur :

```yaml
packages:
  - local: ../kyogo.cdpvd_dashboards_store.features
```

Conserver les configurations CDPVD/Core du consommateur. Les trois modèles amont suivants et leurs dépendances doivent être activés et construits :

| Modèle | Colonnes consommées |
|---|---|
| `cdpvd_fact_activity_current` | `matr`, `corp_empl`, `lieu_trav`, `stat_eng` |
| `dim_employees` | `matr`, `email_address` |
| `i_pai_dos` | `matr`, `date_entr` |

Les `ref()` sont volontairement non qualifiés pour respecter les surcharges du projet CSS dérivé. Le package ne modifie ni n’active globalement CDPVD/Core. CDPVD désactive ses marts par défaut : le consommateur doit activer le sous-graphe nécessaire, comme pour ses autres fonctionnalités RH.

## Mappings et seeds locales

Le package fournit une première `mapping_corps_emploi.csv` de 585 codes, dont 567 classés et 18 sans proposition. Les trois colonnes d’origine sont conservées et la catégorie proposée est ajoutée dans `corps_emploi`. Voir [la provenance, les choix et les cas à valider](references/MAPPING.md). Ce mapping doit être revu pour le CSS consommateur avant utilisation.

Comme dans Core/CDPVD, le consommateur fournit les autres CSV sous `seeds/marts/human_resources/` :

| Fichier | En-tête CSV |
|---|---|
| `mapping_lieux_travail.csv` | `lieu_trav,lieu_travail_principal` |
| `mapping_statuts_engagement.csv` | `stat_eng,statut_engagement` |

Renseigner une ligne par code source, en conservant les zéros initiaux. Les catégories sont définies dans le contrat de sortie. Plusieurs lieux administratifs peuvent être associés au même libellé `CSS`; les écoles gardent leurs libellés propres. Un statut régulier à temps partiel reste `Régulier` : la stabilité de l’engagement ne représente pas le temps de travail.

Les propositions de corps d’emploi sont explicites dans le CSV : aucun classement heuristique n’est effectué dans les modèles SQL. Les correspondances doivent être validées par le CSS. Les contrats et tests des seeds sont fournis par le package.

Pour fournir un mapping de corps d’emploi propre au CSS, désactiver la seed du package dans le `dbt_project.yml` consommateur, puis créer une seed locale du même nom avec les colonnes `corp_empl,corps_emploi`. Déclarer ses types et tests dans le projet consommateur afin de conserver les zéros initiaux et l’unicité des codes :

```yaml
seeds:
  kyogo_cdpvd_dashboards_store_features:
    marts:
      human_resources:
        mapping_corps_emploi:
          +enabled: false
```

## Population et calcul des années

La population provient exclusivement de `cdpvd_fact_activity_current`, qui porte le statut actif, l’emploi principal et le filtre `last_pay_date > dateadd(week, -2, getdate())`. Ce filtre inclut les périodes à venir déjà enregistrées. Il reste sous la responsabilité du package amont et de ses éventuelles surcharges.

Le lieu et le corps d’emploi proviennent du même emploi principal. La date retenue est `i_pai_dos.date_entr`, convertie en date et comparée au jour de construction SQL Server. Le nombre d’années est corrigé si l’anniversaire n’est pas encore atteint. Pour une entrée le 29 février, l’anniversaire d’une année non bissextile est le 28 février, selon `DATEADD` SQL Server.

Une date absente ou future donne une tranche nulle, donc un échec du contrôle de complétude. Aucun âge ou autre champ ne la remplace automatiquement. La durée représente la présence depuis l’entrée au CSS; elle ne certifie pas l’ancienneté conventionnelle et ne retranche pas les interruptions.

## Construction et contrôles

Depuis le projet consommateur correctement configuré :

```bash
dbt deps
dbt build --select +respondents
dbt test --select respondent_population workplace_labels
```

L’exécution autonome du package sans consommateur n’est pas prévue : les mappings de lieux et statuts ainsi que les interfaces locales sont des contrats obligatoires. Une population amont vide produit une table vide, sans inventer de répondants.

Les jointures de mapping sont externes : un code absent ne supprime pas un employé. Une catégorie absente pour un employé admissible, un doublon de code, une identité absente ou dupliquée, ou une catégorie invalide doit faire échouer les tests. Les codes du référentiel dont la catégorie est encore vide ne bloquent pas le build tant qu’ils ne sont pas utilisés par la population admissible. Aucune déduplication arbitraire ne choisit un emploi parmi plusieurs.

Exporter uniquement après réussite de la construction et des tests. Un échec de test dbt ne constitue pas un rollback garanti de la table matérialisée. L’export et les autorisations de lecture restent à la charge du consommateur; aucun export automatique n’est fourni. Ne pas activer `--store-failures` sur des données réelles si cela crée des copies individuelles non autorisées.

Pour vérifier les calculs avec des tables temporaires fictives sur un SQL Server de test, utiliser l’environnement Python dbt existant (`jinja2`, `pyodbc`) et une chaîne ODBC fournie hors du dépôt :

```bash
python dev/check.py
```

Le script lit `KYOGO_TEST_CONNECTION_STRING`, ne consulte aucune table métier, ne retourne aucune ligne individuelle et annule sa transaction à la fin. Il couvre les bornes des tranches, les anniversaires, le 29 février, les dates invalides, les mappings manquants, les duplications et la projection finale.

Le contrôle du référentiel ne nécessite aucune connexion :

```bash
python dev/check_mapping.py
```

Il vérifie la conservation des colonnes sources, des codes et de leur ordre, l’unicité, les catégories autorisées et plusieurs classements représentatifs.
