import csv
from collections import Counter
from pathlib import Path

import yaml


root = Path(__file__).resolve().parents[1]
source_path = root / 'references/eff_categories_emploi.csv'
mapping_path = root / 'seeds/marts/human_resources/mapping_corps_emploi.csv'
with source_path.open(encoding='utf-8-sig', newline='') as source:
    original = list(csv.DictReader(source))
with mapping_path.open(encoding='utf-8', newline='') as source:
    mapped = list(csv.DictReader(source))

assert len(mapped) == len(original)
assert len({row['corp_empl'] for row in mapped}) == len(mapped)
assert [{key: row[key] for key in original[0]} for row in mapped] == original
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
print(f'PASS: {len(mapped)} codes uniques; valeurs source et zeros initiaux conserves.')
print(dict(Counter(row['corps_emploi'] or 'À déterminer' for row in mapped)))
