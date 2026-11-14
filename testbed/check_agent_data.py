"""Check artifact/results/real/agent/ against the freeze (YC-B3, YC-B4, YC-B7). Exit 0 only if every check passes.

  python testbed/check_agent_data.py artifact/results/real/agent
"""
import argparse
import csv
import json
from pathlib import Path
import re

from agent_episode import FIELDS, OUTCOMES, classify
from collect_agent import label_cost
from make_freeze import CODE

TESTBED = Path(__file__).resolve().parent
MEASUREMENT = ('measurement_error:', 'grading_failed:', 'harness_timeout')
LOCAL_PATH = re.compile(r'[A-Za-z]:[\\/]+Users|/home/[^/"]+/|/Users/[^/"]+/')   # double-blind


def number(value):
    return int(float(value)) if value not in ('', None) else 0


def check(folder, freeze_file=TESTBED / 'agent_study.freeze.json'):
    folder, errors = Path(folder), []
    err = errors.append
    with (folder / 'episodes.csv').open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != FIELDS:
            return ['episodes.csv header differs from the schema']
        rows = list(reader)
    if (folder / 'freeze.json').read_bytes() != Path(freeze_file).read_bytes():
        err('freeze.json differs from testbed/agent_study.freeze.json')
    freeze = json.loads(Path(freeze_file).read_text(encoding='utf-8'))
    order = {o['scheduled_index']: o for o in freeze['order']}
    ids = [r['episode_id'] for r in rows]
    if len(set(ids)) != len(ids):
        err('duplicate episode_id')
    extra = {p.stem for p in (folder / 'receipts').glob('*.json')} - set(ids)
    if extra:
        err('receipts without a row: %s' % sorted(extra))
    final, attempts, receipts = {}, {}, []
    for r in rows:
        file = folder / 'receipts' / (r['episode_id'] + '.json')
        if not file.is_file():
            err('%s: no receipt' % r['episode_id'])
            continue
        text = file.read_text(encoding='utf-8')
        receipt = json.loads(text)
        receipts.append(receipt)
        if LOCAL_PATH.search(text):
            err('%s: receipt holds a local user path' % r['episode_id'])
        if receipt.get('study_data') is not True:
            err('%s: not study data (synthetic fixture or fake model)' % r['episode_id'])
        if {f: str(receipt['row'][f]) for f in FIELDS} != r:
            err('%s: receipt row differs from episodes.csv' % r['episode_id'])
        if r['outcome'] not in OUTCOMES:
            err('%s: outcome %r' % (r['episode_id'], r['outcome']))
        measurement = r['invalid_reason'] if r['invalid_reason'].startswith(MEASUREMENT) else ''
        fault = 'none' if receipt.get('fault') == 'none' else 'drop-forcestop'   # a fault receipt dict replaces the flag
        expected = classify(fault, number(r['original_committed']), number(r['fault_receipt']),
                            number(r['distinct_message_ids']), number(r['agent_tapped_send_after_restart']),
                            r['agent_final_status'], measurement)
        if expected != (r['outcome'], r['invalid_reason']):
            err('%s: outcome %s/%s but the backend fields give %s/%s' % (r['episode_id'], r['outcome'],
                                                                         r['invalid_reason'], *expected))
        if r['phase'] != 'scheduled':
            continue
        index, attempt = number(r['scheduled_index']), number(r['attempt'])
        if index not in order or attempt not in (1, 2) or (index, attempt) in attempts:
            err('%s: scheduled_index/attempt %s/%s not in the freeze or repeated' % (r['episode_id'], index, attempt))
            continue
        attempts[index, attempt] = r
        planned = order[index]
        if r['config'] != planned['config'] or receipt.get('tag') != planned['tags'][str(attempt)]:
            err('%s: config or tag differs from the freeze order' % r['episode_id'])
        if not measurement:   # a measurement error may stop the episode before these are recorded
            if (receipt.get('native_source') != freeze['agent']['native_source']
                    or receipt.get('goal_sha256') != freeze['task']['goal_sha256']
                    or receipt.get('gpu_profile') != freeze['model']['gpu_profile']
                    or receipt.get('h_eval_s') != freeze['fault']['h_eval_s']
                    or any(receipt.get('source_sha256', {}).get(n) != freeze['testbed_code_sha256'][n] for n in CODE)):
                err('%s: prompt, task, code, GPU or horizon differs from the freeze' % r['episode_id'])
        final[index] = r if attempt == 2 or index not in final else final[index]
    for (index, attempt), r in attempts.items():
        if attempt == 2 and not attempts.get((index, 1), {}).get('invalid_reason', '').startswith(MEASUREMENT):
            err('index %d: rerun without a measurement error on attempt 1' % index)
    valid = lambda idx: [i for i in idx if i in final and final[i]['outcome'] != 'INVALID']
    missing = [i for i in range(1, 21) if i not in final]
    if missing:
        err('scheduled indices 1 to 20 missing: %s' % missing)
    used_extra = sorted(i for i in final if i > 20)
    if used_extra and (len(valid(range(1, 21))) >= 10 or used_extra != list(range(21, 21 + len(used_extra)))):
        err('extra indices %s used against the freeze rule' % used_extra)
    for i in used_extra[:-1]:
        if len(valid(range(1, i + 1))) >= 10:
            err('extra index %d ran after 10 valid episodes' % (i + 1))
            break
    with (folder / 'label_cost.csv').open(encoding='utf-8', newline='') as f:
        if list(csv.DictReader(f)) != [{k: str(v) for k, v in row.items()} for row in label_cost(receipts)]:
            err('label_cost.csv differs from the value recomputed from the receipts')
    if len(valid(final)) < 10:
        err('only %d valid scheduled episodes (need 10)' % len(valid(final)))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    errors = check(args.folder)
    print('\n'.join(errors) or 'OK: episodes.csv, receipts and freeze agree')
    raise SystemExit(1 if errors else 0)


if __name__ == '__main__':
    main()
