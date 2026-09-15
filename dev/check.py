import os
from pathlib import Path

import jinja2
import pyodbc


ROOT = Path(__file__).resolve().parents[1]
ENV = jinja2.Environment(undefined=jinja2.StrictUndefined)


def check(connection):
    connection.timeout = 30
    cursor = connection.cursor()

    def query(relative_path):
        sql = (ROOT / relative_path).read_text()
        assert all(marker not in sql for marker in ('--', '/*', '{#'))
        rendered = ENV.from_string(sql).render(ref=lambda name: '#' + name)
        cursor.execute(rendered)
        return [tuple(row) for row in cursor.fetchall()]

    cursor.execute('''
        create table #cdpvd_fact_activity_current (
            matr nvarchar(20), corp_empl nvarchar(20),
            lieu_trav nvarchar(20), stat_eng nvarchar(20)
        );
        create table #dim_employees (matr nvarchar(20), email_address nvarchar(100));
        create table #i_pai_dos (matr nvarchar(20), date_entr date);
        create table #i_pai_dos_empl (
            matr nvarchar(20), lieu_trav nvarchar(20), ind_empl_princ int
        );
        insert into #cdpvd_fact_activity_current values ('TEST', 'J', 'OLD', 'S');
        insert into #i_pai_dos_empl values ('TEST', 'W', 1), ('TEST', 'SECONDARY', 0);
        insert into #dim_employees values
            ('TEST', ' TEST@example.invalid '), ('OUTSIDE', 'outside@example.invalid');
        insert into #i_pai_dos values ('TEST', '2020-09-14'), ('OUTSIDE', '2020-09-14');
    ''')
    staged = query('models/marts/human_resources/staging/stg_respondents.sql')
    assert len(staged) == 1 and staged[0][0:2] == ('TEST', 'test@example.invalid')
    assert staged[0][3] == 'W'
    cursor.execute("delete from #i_pai_dos_empl where ind_empl_princ = 1")
    missing_workplace = query('models/marts/human_resources/staging/stg_respondents.sql')
    assert len(missing_workplace) == 1 and missing_workplace[0][3] is None

    cursor.execute('''
        create table #stg_respondents (
            matr nvarchar(20), courriel nvarchar(100), corp_empl nvarchar(20),
            lieu_trav nvarchar(20), stat_eng nvarchar(20),
            date_entree date, date_reference date
        );
        create table #mapping_corps_emploi (
            corp_empl nvarchar(20), corps_emploi nvarchar(100)
        );
        create table #i_pai_tab_lieu_trav (
            lieu_trav nvarchar(20), descr nvarchar(200)
        );
        create table #mapping_statuts_engagement (
            stat_eng nvarchar(20), statut_engagement nvarchar(100)
        );
        insert into #mapping_corps_emploi values ('J', N'Enseignant');
        insert into #i_pai_tab_lieu_trav values ('W', N'École fictive');
        insert into #mapping_statuts_engagement values ('S', N'Régulier');
    ''')
    cases = [
        ('2026-09-14', '2026-09-14', '0–5 ans'),
        ('2020-09-15', '2026-09-14', '0–5 ans'),
        ('2020-09-14', '2026-09-14', '6–10 ans'),
        ('2015-09-15', '2026-09-14', '6–10 ans'),
        ('2015-09-14', '2026-09-14', '11–15 ans'),
        ('2010-09-15', '2026-09-14', '11–15 ans'),
        ('2010-09-14', '2026-09-14', '16–20 ans'),
        ('2005-09-15', '2026-09-14', '16–20 ans'),
        ('2005-09-14', '2026-09-14', '21 ans et plus'),
        ('2020-02-29', '2026-02-27', '0–5 ans'),
        ('2020-02-29', '2026-02-28', '6–10 ans'),
        (None, '2026-09-14', None),
        ('2026-09-15', '2026-09-14', None),
    ]
    cursor.executemany(
        'insert into #stg_respondents values (?, ?, ?, ?, ?, ?, ?)',
        [(str(i), f'test{i}@example.invalid', 'J', 'W', 'S', entry, asof)
         for i, (entry, asof, _) in enumerate(cases)],
    )
    model = 'models/marts/human_resources/features/fct_respondent_categories.sql'
    rows = query(model)
    assert len(rows) == len(cases)
    assert {row[0]: row[3] for row in rows} == {
        str(i): expected for i, (_, _, expected) in enumerate(cases)
    }
    assert all(row[2] == 'Enseignant' and row[4:] == ('École fictive', 'Régulier') for row in rows)

    cursor.execute('''
        create table #fct_respondent_categories (
            matr nvarchar(20), courriel nvarchar(100), corps_emploi nvarchar(100),
            tranche_anciennete nvarchar(100), lieu_travail_principal nvarchar(200),
            statut_engagement nvarchar(100)
        );
    ''')
    cursor.executemany('insert into #fct_respondent_categories values (?, ?, ?, ?, ?, ?)', rows)
    assert sorted(query('models/design/respondents.sql')) == sorted(rows)

    for table, column in [
        ('mapping_corps_emploi', 2),
        ('i_pai_tab_lieu_trav', 4),
        ('mapping_statuts_engagement', 5),
    ]:
        cursor.execute('save transaction mapping_check')
        cursor.execute(f'delete from #{table}')
        unmapped = query(model)
        assert len(unmapped) == len(cases) and all(row[column] is None for row in unmapped)
        cursor.execute('rollback transaction mapping_check')

    cursor.execute("insert into #mapping_corps_emploi values ('J', N'Manuel')")
    assert len(query(model)) == 2 * len(cases)
    cursor.execute("delete from #mapping_corps_emploi where corps_emploi = N'Manuel'")
    cursor.execute("update #i_pai_tab_lieu_trav set descr = ' '")
    assert all(row[4] is None for row in query(model))

    cursor.execute('''
        select matr, cast(N'École fictive' as nvarchar(200)) as lieu_travail_principal
        into #respondents from #cdpvd_fact_activity_current;
    ''')
    assert query('tests/workplace_labels.sql') == []
    cursor.execute("update #respondents set lieu_travail_principal = ' '")
    assert query('tests/workplace_labels.sql') == [(1,)]
    assert query('tests/respondent_population.sql') == []
    cursor.execute("insert into #respondents (matr) values ('DUPLICATE')")
    assert query('tests/respondent_population.sql') == [(1,)]
    print('PASS: staging, 13 cas de dates, projection, mappings absents, doublons et controles SQL.')


if __name__ == '__main__':
    connection = pyodbc.connect(os.environ['KYOGO_TEST_CONNECTION_STRING'], timeout=10)
    try:
        check(connection)
    finally:
        connection.rollback()
        connection.close()
