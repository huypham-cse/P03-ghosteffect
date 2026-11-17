"""Gather the phone K-9 trials (b-log 18/11) into artifact/results/real/device_k9/.

  python testbed/collect_device_k9.py testbed/runs/device-k9/* --out artifact/results/real/device_k9

Writes trials.csv (one row per trial folder, INVALID ones included), receipts/<trial>.json (RESULT.json
byte copy; case/ logs stay local because they name the device serial) and SUMMARY.md. A trial is valid
when every pre-redo check passed (verdict REPRODUCED); a redo duplicate is two server copies with two
distinct Message-IDs after the GUI redo.
"""
import argparse
import csv
import json
import math
import shutil
from pathlib import Path

CHECKS = ('reply_dropped_after_commit', 'error_before_fault', 'app_killed_and_relaunched', 'one_server_copy',
          'k9_kept_in_outbox', 'sent_folder_empty', 'no_resend_after_relaunch')
FIELDS = ('trial', 'phase', 'config', 'kill', 'verdict', *CHECKS, 'server_copies', 'smtp_data_after_fault', 'action',
          'redo_server_copies', 'redo_distinct_ids', 'redo_smtp_data', 'redo_duplicate', 'k9_notice_before_fault',
          'manufacturer', 'model', 'android', 'nonce', 'error_type', 'reason')


def row(run):
    r = json.loads((run / 'RESULT.json').read_text(encoding='utf-8'))
    a, c, d = r.get('audit') or {}, r.get('checks') or {}, r.get('device') or {}
    d = d if isinstance(d, dict) else dict(model=d)   # AVD trials record device='avd'
    dup = a.get('server_copies_after_action') == 2 and a.get('distinct_message_ids_after_action') == 2
    return dict(trial=run.name, phase='dev' if run.name.startswith('dev') else 'scheduled', config=r['config'],
                kill=r.get('kill', 'force-stop'), verdict=r['verdict'], **{k: c.get(k, '') for k in CHECKS},
                server_copies=(r.get('server') or {}).get('copies', ''), smtp_data_after_fault=r.get('smtp_data_after_fault', ''),
                action=a.get('action', ''), redo_server_copies=a.get('server_copies_after_action', ''),
                redo_distinct_ids=a.get('distinct_message_ids_after_action', ''),
                redo_smtp_data=a.get('smtp_data_after_action', ''), redo_duplicate=dup if a else '',
                k9_notice_before_fault=' | '.join(r.get('k9_outbox_before_fault') or []),
                manufacturer=d.get('manufacturer', ''), model=d.get('model', ''), android=d.get('android', ''),
                nonce=r.get('nonce', ''), error_type=r.get('error_type', ''), reason=r.get('reason', ''))


def wilson(k, n, z=1.959964):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0.0, c - h), 100 * min(1.0, c + h)


def summary(rows):
    lines = ['# K-9 lost reply on a physical phone', '',
             'Rows: trials.csv. Valid = every pre-redo check passed. Redo duplicate = 2 server copies, 2 Message-IDs.', '',
             '| Kill | Config | Scheduled | Valid | No resend after relaunch | Redo duplicates | 95% Wilson |',
             '|---|---|---|---|---|---|---|']
    kills = sorted({r['kill'] for r in rows if r['phase'] == 'scheduled'})
    for kill, config in [(k, c) for k in kills for c in ('sent', 'nosent')] + [('all', 'all')]:
        sched = [r for r in rows if r['phase'] == 'scheduled' and kill in (r['kill'], 'all') and config in (r['config'], 'all')]
        valid = [r for r in sched if r['verdict'] == 'REPRODUCED']
        dup = sum(r['redo_duplicate'] is True for r in valid)
        ci = '[%.1f, %.1f]' % wilson(dup, len(valid)) if valid else 'N/A'
        lines.append('| %s | %s | %d | %d | %d | %d/%d | %s |' % (kill, config, len(sched), len(valid),
                     sum(r['no_resend_after_relaunch'] is True for r in valid), dup, len(valid), ci))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    runs = sorted(p for p in args.runs if (p / 'RESULT.json').is_file())
    rows = [row(p) for p in runs]
    (args.out / 'receipts').mkdir(parents=True, exist_ok=True)
    for p in runs:
        shutil.copyfile(p / 'RESULT.json', args.out / 'receipts' / (p.name + '.json'))
    with open(args.out / 'trials.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    (args.out / 'SUMMARY.md').write_text(summary(rows), encoding='utf-8')
    print(summary(rows))


if __name__ == '__main__':
    main()
