"""Copy finished agent episodes into artifact/results/real/agent/ (B-10, B-11).

  python testbed/collect_agent.py testbed/runs/agent/* --out artifact/results/real/agent

Writes episodes.csv (one row per run, dev, scheduled, invalid and reruns alike, schema of
CONTRIBUTOR_FIXED.md section 4), receipts/<episode_id>.json, label_cost.csv over the scheduled runs, and
freeze.json (a byte copy of testbed/agent_study.freeze.json). Append-only: rows already in episodes.csv
must come back unchanged. Then run check_agent_data.py on the output.
"""
import argparse
import csv
import json
from pathlib import Path
import shutil
import statistics

from agent_episode import FIELDS

TESTBED = Path(__file__).resolve().parent
COMPONENTS = ('reset', 'compose', 'fault', 'relaunch', 'observation', 'grading', 'total')


def receipt_of(run):
    for name in ('RESULT.json', 'TIMEOUT.json'):
        if (run / name).is_file():
            return json.loads((run / name).read_text(encoding='utf-8'))
    raise SystemExit('%s has neither RESULT.json nor TIMEOUT.json; keep the folder and note it in b-log' % run)


def label_cost(receipts):
    rows = []
    for component in COMPONENTS:
        values = [float(r['label_cost'][component]) for r in receipts
                  if r['row']['phase'] == 'scheduled' and r.get('label_cost', {}).get(component) not in (None, '')]
        rows.append(dict(component=component, n=len(values),
                         **({k: round(f(values), 1) for k, f in (('min_s', min), ('median_s', statistics.median),
                                                                  ('max_s', max))} if values else
                            dict(min_s='', median_s='', max_s=''))))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('runs', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--freeze', type=Path, default=TESTBED / 'agent_study.freeze.json')
    args = parser.parse_args()
    (args.out / 'receipts').mkdir(parents=True, exist_ok=True)
    found = {}
    for run in sorted(p for p in args.runs if p.is_dir()):
        receipt = receipt_of(run)
        row = {f: str(receipt['row'][f]) for f in FIELDS}
        if row['episode_id'] in found:
            raise SystemExit('episode_id %s appears twice' % row['episode_id'])
        found[row['episode_id']] = (row, receipt)
    table = args.out / 'episodes.csv'
    if table.exists():
        for old in csv.DictReader(table.open(encoding='utf-8', newline='')):
            if found.get(old['episode_id'], (None,))[0] != old:
                raise SystemExit('episodes.csv is append-only; %s changed or is missing' % old['episode_id'])
    receipts = []
    with table.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        for row, receipt in sorted(found.values(), key=lambda x: int(x[0]['t_end_utc'])):
            writer.writerow(row)
            (args.out / 'receipts' / (row['episode_id'] + '.json')).write_text(
                json.dumps(receipt, indent=2, default=str), encoding='utf-8')
            receipts.append(receipt)
    with (args.out / 'label_cost.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=('component', 'n', 'min_s', 'median_s', 'max_s'), lineterminator='\n')
        writer.writeheader()
        writer.writerows(label_cost(receipts))
    shutil.copyfile(args.freeze, args.out / 'freeze.json')
    print('%d runs -> %s' % (len(found), args.out))


if __name__ == '__main__':
    main()
