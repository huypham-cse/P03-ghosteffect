#!/usr/bin/env python3
"""E7 (REAL, host measurement): ledger append latency and write-ahead invariant under SIGKILL.

1. Latency: 2,000 PLANNED->ISSUED appends (WAL, synchronous=FULL) on the build host, with and
   without F_FULLFSYNC (macOS).  Bytes per effect from the database size.
2. Crash safety: 300 trials.  A child process (the "controller") loops: plan, issue (durable),
   then performs the "commit tap" by appending TAP <id> to a separate log (an external side effect
   that survives the death of the writer), then settles.  The parent SIGKILLs the child at a random
   time.  Invariant: every tapped id is ISSUED or later in the ledger.  This tests process death of
   the writer, not power loss (macOS fsync without F_FULLFSYNC does not force the disk cache).
Timing numbers depend on the host and are not byte-reproducible; the invariant check is.
"""
import csv
import os
import random
import signal
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import Ledger, db_bytes

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')


def child(db, taplog):
    lg = Ledger(db)
    fd = os.open(taplog, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    i = 0
    while True:
        eid = f'e{i}'
        lg.plan(eid, 'wf', i, 'app', 'send message', 'gx:ABC123')
        lg.issue(eid)
        os.write(fd, f'TAP {eid}\n'.encode())       # the commit tap (external effect)
        lg.settle(eid, 'COMMITTED')
        i += 1


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def latency(fullfsync, n=2000):
    d = tempfile.mkdtemp()
    p = os.path.join(d, 'l.db')
    lg = Ledger(p, fullfsync=fullfsync)
    ts = []
    for i in range(n):
        lg.plan(f'e{i}', 'wf', i, 'org.example.app', 'transfer 1200 to Alex', 'gx:7K2Q9F', digest='x' * 64)
        t = time.perf_counter()
        lg.issue(f'e{i}')
        ts.append(1000 * (time.perf_counter() - t))
    lg.close()
    lg = Ledger(p)
    lg.db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    lg.close()
    return pct(ts, 0.5), pct(ts, 0.95), db_bytes(p) / n


def crash_trials(k=300, seed=7):
    rng = random.Random(seed)
    viol = taps = cand = 0
    for _ in range(k):
        d = tempfile.mkdtemp()
        db, tl = os.path.join(d, 'l.db'), os.path.join(d, 'tap.log')
        pr = subprocess.Popen([sys.executable, '-I', os.path.abspath(__file__), '--child', db, tl])
        time.sleep(rng.uniform(0.05, 0.25))
        pr.send_signal(signal.SIGKILL)
        pr.wait()
        if not os.path.exists(db):
            continue
        lg = Ledger(db)
        tapped = [ln.split()[1] for ln in open(tl)] if os.path.exists(tl) else []
        for eid in tapped:
            taps += 1
            if lg.state(eid) not in ('ISSUED', 'COMMITTED'):
                viol += 1
        cand += len(lg.candidates())
        lg.close()
    return k, taps, viol, cand


def main():
    p50, p95, bpe = latency(False)
    f50, f95, _ = latency(True, n=500)
    k, taps, viol, cand = crash_trials()
    row = dict(issue_p50_ms=round(p50, 2), issue_p95_ms=round(p95, 2), fullfsync_p50_ms=round(f50, 2),
               fullfsync_p95_ms=round(f95, 2), bytes_per_effect=round(bpe), kill_trials=k, taps_checked=taps,
               invariant_violations=viol, ghost_candidates=cand)
    print(row)
    with open(os.path.join(RES, 'ledger_bench.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        w.writeheader()
        w.writerow(row)


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--child':
        child(sys.argv[2], sys.argv[3])
    else:
        main()
