select
    matr,
    courriel,
    corps_emploi,
    tranche_anciennete,
    lieu_travail_principal,
    statut_engagement
from {{ ref('fct_respondent_categories') }}
