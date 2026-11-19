"""Phone ledger benchmark harness (b-log 19/11, TN3), the phone counterpart of artifact/scripts/bench_ledger.py.

  python harness.py --adb <adb> --serial <serial> --apk build/ledgerbench.apk --out <dir> [--kills 100] [--seed 7]

1. Latency: `am instrument -e mode latency` with synchronous FULL (twice) and NORMAL (once, context only):
   p50/p95/max of issue() over 2,000 effects and bytes per effect, on the phone's own SQLite in app storage.
2. Kill test: `--kills` trials. The writer loops plan, issue (durable), TAP to a separate file, settle; the harness waits
   for its first tap, then `am force-stop` (SIGKILL) after a seeded uniform 0.05 to 0.25 s; `mode verify` checks that
   every tapped id is ISSUED or COMMITTED. This tests process death of the writer, not power loss (as on the host).
Writes latency.csv, kills.csv and SUMMARY.json into --out. Uses only adb; needs no root and touches only this package.
"""
import argparse
import csv
import json
import random
import subprocess
import time
from pathlib import Path

PKG = 'org.ghosteffect.ledgerbench'
STARTED = '/sdcard/Android/data/%s/files/started' % PKG


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', required=True)
    p.add_argument('--apk', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--kills', type=int, default=100)
    p.add_argument('--seed', type=int, default=7)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    adb = [a.adb, '-s', a.serial]

    def run(*cmd, timeout=600):
        return subprocess.run(adb + list(cmd), capture_output=True, text=True, timeout=timeout).stdout.replace('\r', '')

    def instrument(**extras):
        cmd = ['shell', 'am', 'instrument', '-w']
        for k, v in extras.items():
            cmd += ['-e', k, str(v)]
        out = run(*cmd, PKG + '/.Bench')
        result = {}
        for line in out.splitlines():
            if line.startswith('INSTRUMENTATION_RESULT: ') and '=' in line:
                k, v = line[len('INSTRUMENTATION_RESULT: '):].split('=', 1)
                result[k] = v
            elif line.startswith('INSTRUMENTATION_CODE: '):
                result['code'] = line.split(': ', 1)[1]
        if result.get('code') != '0' or 'error' in result:
            raise RuntimeError('instrumentation failed: %r' % (result or out[-500:]))
        return result

    install = run('install', '-r', str(a.apk), timeout=180).strip().splitlines()
    summary = dict(install=install[-1] if install else '', utc_start=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    rows = []
    for sync, rep in (('FULL', 1), ('FULL', 2), ('NORMAL', 1)):
        r = instrument(mode='latency', n=2000, sync=sync)
        r.update(rep=rep)
        rows.append(r)
        print('latency', sync, rep, r['issue_p50_ms'], r['issue_p95_ms'], r['bytes_per_effect'], flush=True)
    with open(a.out / 'latency.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader()
        w.writerows(rows)

    rng = random.Random(a.seed)
    run('shell', 'am', 'force-stop', PKG)
    instrument(mode='verify')   # clean slate: removes any ledger or tap file left by an earlier run
    kills = []
    for i in range(a.kills):
        run('shell', 'rm', '-f', STARTED)
        subprocess.Popen(adb + ['shell', 'am', 'instrument', '-e', 'mode', 'writer', PKG + '/.Bench'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 30
        while 'y' not in run('shell', 'test -e %s && echo y' % STARTED):
            if time.monotonic() > deadline:
                raise RuntimeError('writer did not tap within 30 s (trial %d)' % i)
            time.sleep(.05)
        delay = rng.uniform(.05, .25)
        time.sleep(delay)
        run('shell', 'am', 'force-stop', PKG)
        alive = run('shell', 'pidof', PKG).strip()
        v = instrument(mode='verify')
        kills.append(dict(trial=i, delay_s=round(delay, 3), alive_after_kill=bool(alive), **{k: v[k] for k in (
            'db_existed', 'taps_checked', 'invariant_violations', 'ghost_candidates')}))
        print('kill', i, kills[-1]['taps_checked'], kills[-1]['invariant_violations'], flush=True)
    with open(a.out / 'kills.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(kills[0]))
        w.writeheader()
        w.writerows(kills)
    full = [r for r in rows if r['sync_requested'] == 'FULL']
    summary.update(device=rows[0]['device'], android_release=rows[0]['android_release'], sdk_int=rows[0]['sdk_int'],
                   build_display=rows[0]['build_display'], sqlite_version=rows[0]['sqlite_version'],
                   full_issue_p50_ms=[r['issue_p50_ms'] for r in full], full_issue_p95_ms=[r['issue_p95_ms'] for r in full],
                   full_bytes_per_effect=[r['bytes_per_effect'] for r in full], kill_trials=len(kills),
                   taps_checked=sum(int(k['taps_checked']) for k in kills),
                   invariant_violations=sum(int(k['invariant_violations']) for k in kills),
                   ghost_candidates=sum(int(k['ghost_candidates']) for k in kills),
                   writer_alive_after_kill=sum(k['alive_after_kill'] for k in kills), seed=a.seed,
                   utc_end=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    (a.out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    run('shell', 'pm', 'uninstall', PKG)


if __name__ == '__main__':
    main()
