import csv
from collections import Counter
from pathlib import Path

import yaml


root = Path(__file__).resolve().parents[1]
mapping_path = root / 'seeds/marts/human_resources/mapping_corps_emploi.csv'
with mapping_path.open(encoding='utf-8', newline='') as source:
    mapped = list(csv.DictReader(source))

assert mapped
assert len({row['corp_empl'] for row in mapped}) == len(mapped)
assert all(row['corp_empl'].isdigit() and len(row['corp_empl']) == 4 for row in mapped)
schema = yaml.safe_load((root / 'models/design/schema.yml').read_text())
column = next(col for col in schema['models'][0]['columns'] if col['name'] == 'corps_emploi')
allowed = next(test['accepted_values']['values'] for test in column['data_tests'] if isinstance(test, dict))
assert all(row['corps_emploi'] in allowed or row['corps_emploi'] == '' for row in mapped)
by_code = {row['corp_empl']: row['corps_emploi'] for row in mapped}
assert by_code['1150'] == 'Gestionnaire'
assert by_code['3103'] == 'Enseignant'
assert by_code['4207'] == 'Technique'
assert by_code['4284'] == 'Paratechnique'
assert by_code['5104'] == 'Manuel'
assert all(by_code[code] == '' for code in ['0105', '4000', '4999', '5000', '5999', '6001', '9700'])
print(f'PASS: {len(mapped)} codes uniques; formats et categories valides.')
print(dict(Counter(row['corps_emploi'] or 'À déterminer' for row in mapped)))

with (root / 'seeds/marts/human_resources/mapping_statuts_engagement.csv').open(
    encoding='utf-8', newline=''
) as source:
    statuses = list(csv.DictReader(source))
assert statuses
assert len({row['stat_eng'] for row in statuses}) == len(statuses)
assert all(row['stat_eng'] and row['description_stat_eng'] for row in statuses)
column = next(col for col in schema['models'][0]['columns'] if col['name'] == 'statut_engagement')
allowed = next(test['accepted_values']['values'] for test in column['data_tests'] if isinstance(test, dict))
assert all(row['statut_engagement'] in allowed or row['statut_engagement'] == '' for row in statuses)
by_code = {row['stat_eng']: row['statut_engagement'] for row in statuses}
assert by_code['E1'] == by_code['S2'] == 'Régulier'
assert by_code['E8'] == by_code['P3'] == 'Temporaire ou remplaçant'
assert by_code['E6'] == 'Occasionnel'
assert by_code['97'] == by_code['SA'] == ''
print(f'PASS: {len(statuses)} statuts uniques; formats et categories valides.')
print(dict(Counter(row['statut_engagement'] or 'À déterminer' for row in statuses)))
