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


def k9_long(logs, command):
    rows = []
    for log in logs:
        for d in sorted(log.glob('l0*/RESULT.json')):
            r = json.loads(d.read_text())
            rows.append(dict(trial=d.parent.name, verdict=r['verdict'], config=r['config'], kill=r['kill'],
                             observe_s=r.get('observe_s'), server_copies=r['server']['copies'],
                             smtp_data_after_fault=r.get('smtp_data_after_fault'),
                             kept_in_outbox=r['checks'].get('k9_kept_in_outbox'), all_checks=all(r['checks'].values())))
    rows.sort(key=lambda r: r['trial'])
    out = OUT / 'device_k9_long_pixel'
    write_csv(out / 'trials.csv', rows)
    meta(out / 'trials.csv', command, dict(rig='k9_fault_case.py --observe 2100, no redo; the emulator K9L cases'))
    (out / 'device.txt').write_text((logs[0] / 'device.txt').read_text())
    rep = sum(r['verdict'] == 'REPRODUCED' for r in rows)
    (out / 'SUMMARY.md').write_text(
        '# K-9 long observation on a rented Pixel 9 Pro XL (Android 17)\n\n'
        f'{rep}/{len(rows)} REPRODUCED over the emulator K9L cases (nosent/sent x force-stop/background): after the lost '
        f'SMTP reply and 2,100 s of observation after the relaunch, one server copy and no new SMTP DATA in '
        f'{sum(r["server_copies"] == 1 and r["smtp_data_after_fault"] == 0 for r in rows)}/{len(rows)}; the mail stayed in '
        "K-9's Outbox.\n")
    return rep, len(rows)


def doze(log, command):
    rows = []
    for d in sorted(log.glob('doze/d0*/RESULT.json')):
        r = json.loads(d.read_text())
        c = r['clock']
        rows.append(dict(trial=r['name'], dev=r['name'] == 'd00', doze_s=r['hold_s'], doze_states='|'.join(r['doze_states']),
                         element_alive_in_doze=r['element_alive_in_doze'],
                         resends_s_from_doze_entry='|'.join(str(x) for x in r['resends_s_from_enter']),
                         resends_during_doze=r['resends_during_doze'], copies_at_doze_exit=r['copies_at_exit'],
                         exit_to_sent_s=round(r['exit_to_sent_s'], 2) if r['exit_to_sent_s'] is not None else '',
                         server_copies_final=len(r['server_copies_final']),
                         commit_to_doze_entry_s=round((c['doze_enter_utc_ns'] - c['barrier_utc_ns']) / 1e9, 2)))
    out = OUT / 'device_element_doze_pixel'
    write_csv(out / 'trials.csv', rows)
    meta(out / 'trials.csv', command, dict(rig='testbed/devicefarm/element_doze.py (sticky proxy as ELMK; doze_enter/doze_exit of the DAVx5 rig)'))
    (out / 'device.txt').write_text((log / 'device.txt').read_text())
    main = [r for r in rows if not r['dev']]
    (out / 'SUMMARY.md').write_text(
        '# Element under Doze after a lost reply, rented Pixel 9 Pro XL (Android 17)\n\n'
        f'{len(main)} trials with 600 s of forced deep idle (d00, 120 s, is the dev trial). In each, Element was alive in '
        'the background, the held reply was dropped at the Doze entry, and Element sent the same txnId again within '
        f'{max(float(x) for r in main for x in r["resends_s_from_doze_entry"].split("|")):.2f} s (an immediate HTTP retry '
        'of the dropped request); Synapse deduplicated it. One server copy in '
        f'{sum(r["server_copies_final"] == 1 for r in main)}/{len(main)}; the row read "Sent" '
        f'{min(r["exit_to_sent_s"] for r in main)} to {max(r["exit_to_sent_s"] for r in main)} s after the Doze exit. '
        'Not tested: a retry scheduled later that falls inside Doze.\n')
    return len(main)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--k9', type=Path)
    p.add_argument('--tn4', type=Path, nargs=2)
    p.add_argument('--k9-long', type=Path, nargs='+')
    p.add_argument('--doze', type=Path)
    a = p.parse_args()
    command = 'python testbed/devicefarm/collect_df_pixel.py ' + ' '.join(
        flag for flag, v in (('--k9 <r1>', a.k9), ('--tn4 <r3> <r4>', a.tn4), ('--k9-long <k9l-1> <k9l-2>', a.k9_long),
                             ('--doze <doze>', a.doze)) if v)
    if a.k9:
        print('K-9:', k9(a.k9, command))
    if a.tn4:
        print('TN4 transfer:', json.dumps(tn4(a.tn4, command)))
    if a.k9_long:
        print('K-9 long:', k9_long(a.k9_long, command))
    if a.doze:
        print('Element Doze trials:', doze(a.doze, command))


if __name__ == '__main__':
    main()
