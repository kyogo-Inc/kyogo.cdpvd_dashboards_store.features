with
    tenure as (
        select
            matr,
            courriel,
            corp_empl,
            lieu_trav,
            stat_eng,
            case
                when date_entree <= date_reference
                then
                    datediff(year, date_entree, date_reference)
                    - case
                        when
                            dateadd(
                                year,
                                datediff(year, date_entree, date_reference),
                                date_entree
                            ) > date_reference
                        then 1
                        else 0
                    end
            end as annees_presence
        from {{ ref('stg_respondents') }}
    )
select
    tenure.matr,
    tenure.courriel,
    jobs.corps_emploi,
    case
        when tenure.annees_presence between 0 and 5 then N'0–5 ans'
        when tenure.annees_presence between 6 and 10 then N'6–10 ans'
        when tenure.annees_presence between 11 and 15 then N'11–15 ans'
        when tenure.annees_presence between 16 and 20 then N'16–20 ans'
        when tenure.annees_presence >= 21 then N'21 ans et plus'
    end as tranche_anciennete,
    workplaces.lieu_travail_principal,
    engagement.statut_engagement
from tenure
left join {{ ref('mapping_corps_emploi') }} as jobs
    on jobs.corp_empl = tenure.corp_empl
left join {{ ref('mapping_lieux_travail') }} as workplaces
    on workplaces.lieu_trav = tenure.lieu_trav
left join {{ ref('mapping_statuts_engagement') }} as engagement
    on engagement.stat_eng = tenure.stat_eng
