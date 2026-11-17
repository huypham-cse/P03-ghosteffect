"""Gather the AVD CalDAV fault trials (b-log 18/11) into artifact/results/real/emu_caldav/.

  python testbed/collect_caldav.py testbed/runs/emu/dev-c* testbed/runs/emu/dev-d* testbed/runs/emu/c* testbed/runs/emu/d* \
      --out artifact/results/real/emu_caldav

Writes trials.csv (every folder with a RESULT.json, INVALID included), receipts/<trial>.json and SUMMARY.md
(per fault: valid trials, exactly-once count, and the delay from the fault to DAVx5's next PUT of the same href).
"""
import argparse
import csv
import json
import shutil
import statistics
from pathlib import Path

FIELDS = ('trial', 'phase', 'fault', 'verdict', 'server_copies', 'puts', 'first_put_after_fault_s',
          'first_put_after_doze_exit_s', 'doze_state', 'lmkd_filled_mb', 'lmkd_line', 'dirty_after', 'nonce', 'href',
          'error_type', 'reason')


def row(run):
    r = json.loads((run / 'RESULT.json').read_text(encoding='utf-8'))
    f = r.get('fault_receipt') or {}
    doze = f.get('doze') or (f if f.get('observed_class') == 'device-doze-deep' else {})
    return dict(trial=run.name, phase='dev' if run.name.startswith('dev') else 'scheduled', fault=r.get('fault', ''),
                verdict=r['verdict'], server_copies=len(r['server_copies']) if 'server_copies' in r else '',
                puts=r.get('puts', ''), first_put_after_fault_s=r.get('first_put_after_fault_s', ''),
                first_put_after_doze_exit_s=r.get('first_put_after_doze_exit_s', ''), doze_state=doze.get('state', ''),
                lmkd_filled_mb=f.get('filled_mb', ''), lmkd_line=f.get('lmkd_line', ''),
                dirty_after=r.get('dirty_after', ''), nonce=r.get('nonce', ''), href=r.get('href', ''),
                error_type=r.get('error_type', ''), reason=r.get('reason', ''))


def summary(rows):
    lines = ['# DAVx5 + Etar + Radicale on the AVD: lost PUT reply, then a fault', '',
             'Rows: trials.csv. Delay = seconds from the fault to the next PUT of the same href (proxy journal).', '',
             '| Fault | Scheduled | Valid | Exactly once | Delay to next PUT, median [min, max] s |', '|---|---|---|---|---|']
    for fault in sorted({r['fault'] for r in rows if r['phase'] == 'scheduled'}):
        sched = [r for r in rows if r['phase'] == 'scheduled' and r['fault'] == fault]
        valid = [r for r in sched if r['verdict'] != 'INVALID']
        delays = [float(r['first_put_after_fault_s']) for r in valid if r['first_put_after_fault_s'] not in ('', None)]
        delay = '%.1f [%.1f, %.1f]' % (statistics.median(delays), min(delays), max(delays)) if delays else 'N/A'
        lines.append('| %s | %d | %d | %d | %s |' % (fault, len(sched), len(valid),
                                                    sum(r['verdict'] == 'EXACTLY_ONCE' for r in valid), delay))
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
