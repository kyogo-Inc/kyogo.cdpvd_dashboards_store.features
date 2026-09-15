select
    active.matr,
    nullif(lower(ltrim(rtrim(employee.email_address))), '') as courriel,
    active.corp_empl,
    employment.lieu_trav,
    active.stat_eng,
    cast(dossier.date_entr as date) as date_entree,
    cast(getdate() as date) as date_reference
from {{ ref('cdpvd_fact_activity_current') }} as active
left join {{ ref('dim_employees') }} as employee on employee.matr = active.matr
left join {{ ref('i_pai_dos') }} as dossier on dossier.matr = active.matr
left join {{ ref('i_pai_dos_empl') }} as employment
    on employment.matr = active.matr and employment.ind_empl_princ = 1
