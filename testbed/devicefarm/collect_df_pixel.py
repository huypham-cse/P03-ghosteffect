"""Collect the rented-Pixel runs of 24-25/11 (b-log) into the artifact. Run data stays outside git (drive D).

  python testbed/devicefarm/collect_df_pixel.py --k9 <r1 log dir> --tn4 <r3 log dir> <r4 log dir>

Writes artifact/results/real/device_k9_pixel/ (K-9 Table 1a, five trials of the R1 rig) and
artifact/results/real/tn4_transfer_pixel/ (the TN4 transfer check: emulator store, Pixel 9 Pro XL test, two halves),
each with trials.csv, SUMMARY.md, device.txt and a .meta.json for every CSV (YC-07).
"""
import argparse
import csv
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifact/results/real'


def meta(csv_path, command, extra):
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    csv_path.with_suffix('.meta.json').write_text(json.dumps(dict(
        command=command, git_commit=commit, python=sys.version.split()[0], date_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        host='collector: ' + platform.node(), runs='AWS Device Farm, Google Pixel 9 Pro XL, Android 17 (CP2A.260605.012)', **extra), indent=2))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def k9(log, command):
    rows = []
    for d in sorted(log.glob('k0*/RESULT.json')):
        r = json.loads(d.read_text())
        a = r.get('audit') or {}
        rows.append(dict(trial=d.parent.name, verdict=r['verdict'], server_copies_after_fault=r['server']['copies'],
                         smtp_data_after_fault=r.get('smtp_data_after_fault'), kept_in_outbox=r['checks'].get('k9_kept_in_outbox'),
                         no_resend_after_relaunch=r['checks'].get('no_resend_after_relaunch'), action=a.get('action'),
                         server_copies_after_redo=a.get('server_copies_after_action'),
                         distinct_message_ids_after_redo=a.get('distinct_message_ids_after_action')))
    out = OUT / 'device_k9_pixel'
    write_csv(out / 'trials.csv', rows)
    meta(out / 'trials.csv', command, dict(rig='k9_fault_case.py --config sent --kill force-stop --observe 60 --action recompose --action-window 30'))
    (out / 'device.txt').write_text((log / 'device.txt').read_text())
    n, rep = len(rows), sum(r['verdict'] == 'REPRODUCED' for r in rows)
    dup = sum(r['server_copies_after_redo'] == 2 and r['distinct_message_ids_after_redo'] == 2 for r in rows)
    (out / 'SUMMARY.md').write_text(
        '# K-9 on a rented Pixel 9 Pro XL (Android 17), Table 1a\n\n'
        f'{rep}/{n} trials REPRODUCED the trap: after the lost SMTP reply the server held one copy, K-9 sent nothing more '
        f'(SMTP DATA after the fault: {sum(r["smtp_data_after_fault"] == 0 for r in rows)}/{n} zero) and kept the mail in its '
        f'Outbox. The scripted GUI redo left two server copies with two Message-IDs in {dup}/{n} trials. Same rig as the '
        'A36 pilot p01 (18/11); on Android 17 K-9 is opened through its launcher intent (b-log 24/11).\n')
    return rep, n, dup


def tn4(logs, command):
    rows = []
    for half, log in zip('AB', logs):
        for line in (next(log.glob('tn4x-*/decisions.jsonl'))).read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            rows.append(dict(half=half, trial=r['name'], x=r['x'], fault_class=r['fault_class'], decision=r['decision'],
                             reason=r['reason'], view_timeline=r['views'][0], view_roomlist=r['views'][1],
                             server_copies=len(r['server_copies_final'])))
    invalid = sum(len(list(log.glob('tn4x-*/*INVALID*'))) for log in logs)
    out = OUT / 'tn4_transfer_pixel'
    write_csv(out / 'trials.csv', rows)
    meta(out / 'trials.csv', command, dict(store='testbed/tn4/tn4_store.json (emulator calibration, alpha=beta=10%)',
                                           schedules='testbed/devicefarm/tn4x_A.json, tn4x_B.json (seed 20261124)',
                                           runner='testbed/devicefarm/diag_collect.py (element_planner.collect, unchanged module, screen reads recorded)'))
    (out / 'device.txt').write_text((logs[0] / 'device.txt').read_text())
    com = [r for r in rows if r['x'] == 1]
    ab = [r for r in rows if r['x'] == 0]
    c = lambda rs, d: sum(r['decision'] == d for r in rs)
    upper = 100 * (1 - 0.05 ** (1 / len(com)))
    s = dict(committed=len(com), committed_retried=c(com, 'RETRY'), committed_committed=c(com, 'COMMITTED'), committed_ask=c(com, 'ASK'),
             committed_one_copy=sum(r['server_copies'] == 1 for r in com), absent=len(ab), absent_retried=c(ab, 'RETRY'),
             absent_ask=c(ab, 'ASK'), absent_declared_committed=c(ab, 'COMMITTED'),
             duplicates=sum(r['server_copies'] > 1 for r in rows), invalid=invalid, cp_upper_pct=round(upper, 2))
    (out / 'SUMMARY.md').write_text(
        '# TN4 transfer check on a rented Pixel 9 Pro XL (Android 17)\n\n'
        'The emulator calibration store (alpha=beta=10%) applied unchanged; fault classes none and force-stop; '
        f'{len(rows)} valid trials in two halves, {invalid} INVALID (rig, replaced).\n\n'
        f'- Committed: {s["committed_retried"]}/{s["committed"]} retried (one-sided 95% CP upper {s["cp_upper_pct"]}%), '
        f'{s["committed_committed"]} COMMITTED, {s["committed_ask"]} ASK; one server copy in {s["committed_one_copy"]}/{s["committed"]}.\n'
        f'- Absent: {s["absent_retried"]}/{s["absent"]} retried, {s["absent_ask"]} ASK, {s["absent_declared_committed"]} declared committed.\n'
        f'- Duplicates: {s["duplicates"]}.\n\n```json\n{json.dumps(s, indent=1)}\n```\n')
    return s


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--k9', type=Path, required=True)
    p.add_argument('--tn4', type=Path, nargs=2, required=True)
    a = p.parse_args()
    command = 'python testbed/devicefarm/collect_df_pixel.py --k9 <r1> --tn4 <r3> <r4>'
    print('K-9:', k9(a.k9, command))
    print('TN4 transfer:', json.dumps(tn4(a.tn4, command)))


if __name__ == '__main__':
    main()
