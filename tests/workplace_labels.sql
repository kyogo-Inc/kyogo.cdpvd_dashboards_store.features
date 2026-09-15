select 1 as invalid_workplace_label
where exists (
    select 1
    from {{ ref('respondents') }}
    where nullif(ltrim(rtrim(lieu_travail_principal)), '') is null
)
