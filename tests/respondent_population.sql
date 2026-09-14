select 1 as population_mismatch
where
    (select count_big(*) from {{ ref('respondents') }})
    <> (select count_big(*) from {{ ref('cdpvd_fact_activity_current') }})
