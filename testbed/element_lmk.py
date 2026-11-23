"""ELMK (b-log 23/11): Element reaped by the real low-memory killer after a lost reply (AVD, root).

  python testbed/element_lmk.py run --out <run dir> --adb <adb> [--serial emulator-5582] [--trials 10] [--prefix k]
  python testbed/element_lmk.py summarize --run <run dir> [--out artifact/results/real/emu_element_lmk]

One trial: alice composes a nonce-tagged message in room "gx test"; the proxy runs in sticky mode (it forwards the PUT
so Synapse commits, holds the reply, then drops every same-txnId retry until the fault receipt); the driver taps Send,
waits for the commit barrier, clears logcat, sends Element HOME and fills a tmpfs with random bytes until lmkd reaps
Element (E1's lmk_kill), frees the memory, releases the arm, relaunches Element and polls the timeline until the row
reads "Sent" (lag from the relaunch, at most 120 s). After 30 more seconds the server copies are graded as bob.
If 6,000 MB do not make lmkd reap Element, the trial is recorded as not reaped (an answer, not a rig failure).
Reuses element_planner.py's helpers without changing that file (its hash is in the TN4 store's domain)."""
import argparse
import csv
import json
import random
import statistics
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caldav_planner as cp   # noqa: E402
import element_planner as ep   # noqa: E402
from faultproxy import Journal, Faults, http_proxy   # noqa: E402
from k9_fault_case import CROCKFORD, lmk_kill   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POLL_SECONDS, SETTLE_SECONDS = 120, 30


class Pids:
    """The device interface lmk_kill expects."""

    def __init__(self, phone):
        self.phone = phone

    def pids(self, package):
        return self.phone.sh('pidof ' + package)


def trial(phone, grader, faults, out):
    out.mkdir(parents=True, exist_ok=False)
    phone.sh('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
    ep.network(phone, True)
    ep.to_room(phone)
    ep.clear_composer(phone)
    nonce = 'gx:' + ''.join(random.SystemRandom().choice(CROCKFORD) for _ in range(6))
    ep.compose(phone, 'gx test message %s' % nonce)
    arm = faults.configure('sticky')
    clock = dict(send_tap=ep.tap_send(phone))
    deadline = time.monotonic() + 30
    while not faults.status(arm)['barrier']:
        if time.monotonic() > deadline:
            raise RuntimeError('no committed PUT within the barrier timeout')
        time.sleep(.05)
    clock['barrier_utc_ns'] = time.time_ns()
    phone.sh('logcat -c')
    try:
        fault = lmk_kill(phone.sh, Pids(phone), ep.ELEMENT)
        reaped = True
    except RuntimeError as exc:
        if 'memory pressure did not reap' not in str(exc):
            raise
        fault, reaped = dict(observed_class='lmk-not-reaped', reason=str(exc)), False
    fault['utc_ns'] = time.time_ns()
    faults.release(arm, fault)
    time.sleep(2)
    ep.launch(phone)
    origin = time.monotonic()
    clock['relaunch_utc_ns'] = time.time_ns()
    copies_at_origin = len(grader.copies(nonce))
    lag = None
    while time.monotonic() < origin + POLL_SECONDS:
        try:
            _, root = ep.to_room(phone, timeout=10)
            if ep.row_has(root, nonce):
                lag = time.monotonic() - origin
                break
        except RuntimeError:
            pass
        time.sleep(.3)
    time.sleep(SETTLE_SECONDS)
    events = [json.loads(l) for l in (out.parent / 'proxy.jsonl').read_text(encoding='utf-8').splitlines()]
    mine = [e for e in events if e.get('arm_id') == arm]
    result = dict(name=out.name, nonce=nonce, reaped=reaped, fault=fault, copies_at_origin=copies_at_origin,
                  lag_s=lag, server_copies_final=grader.copies(nonce),
                  retry_replies_dropped=sum(e.get('event') == 'RETRY_REPLY_DROP' for e in mine), clock=clock)
    cp.write_json(out / 'RESULT.json', result)
    return result


def run(args):
    args.out.mkdir(parents=True, exist_ok=True)
    phone = cp.Phone(args.adb, args.serial)
    if phone.sh('whoami') != 'root':
        phone.adb('root', timeout=60)
        time.sleep(3)
    faults = Faults(Journal(args.out / 'proxy.jsonl'), barrier_timeout=60)
    server = http_proxy(ep.SYNAPSE, 'matrix', faults, listen=('127.0.0.1', ep.PROXY_PORT))
    threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
    grader = ep.Grader()
    names = ['%s%02d' % (args.prefix, i) for i in range(1, args.trials + 1)]
    done = {p.name for p in args.out.iterdir() if (p / 'RESULT.json').exists()}
    try:
        for name in names:
            if name in done:
                continue
            try:
                r = trial(phone, grader, faults, args.out / name)
                line = '%s ok reaped=%s mb=%s lag=%s copies=%d/%d drops=%d' % (
                    name, r['reaped'], r['fault'].get('filled_mb'), r['lag_s'], r['copies_at_origin'],
                    len(r['server_copies_final']), r['retry_replies_dropped'])
            except Exception as exc:   # rig failure: keep the folder, mark it, move on (counted, never scored)
                bad = args.out / name
                bad.mkdir(exist_ok=True)
                (bad / 'INVALID.json').write_text(json.dumps(dict(error_type=type(exc).__name__, reason=str(exc))))
                bad.rename(args.out / (name + '-INVALID-%d' % time.time_ns()))
                a = faults.arm
                if a and not a['released'].is_set():
                    if a['reached'].is_set():
                        faults.release(a['id'], dict(observed_class='rig-abort'))
                    else:
                        a['released'].set()
                line = '%s INVALID %s: %s' % (name, type(exc).__name__, exc)
            with open(args.out / 'batch.log', 'a', encoding='utf-8') as f:
                f.write(time.strftime('%H:%M:%S ') + line + '\n')
            print(line, flush=True)
    finally:
        server.shutdown()
        server.server_close()
        grader.close()


def resends(events, barrier_utc_ns):
    """Requests with the trial's txnId that reached the proxy after the fault receipt (Element's own re-send after the
    relaunch). The trial's arm is the one whose commit barrier is the last one at or before the driver saw it."""
    bars = [e for e in events if e['event'] == 'PRE_ACK_BARRIER' and e['utc_ns'] <= barrier_utc_ns]
    if not bars:
        return ''
    arm, rid = bars[-1]['arm_id'], bars[-1]['request_id']
    fault = next(e['utc_ns'] for e in events if e['event'] == 'FAULT_RECEIPT' and e.get('arm_id') == arm)
    return sum(e['event'] == 'REQUEST' and e.get('request_id') == rid and e['utc_ns'] > fault for e in events)


def summarize(args):
    rows = []
    events = [json.loads(l) for l in (args.run / 'proxy.jsonl').read_text(encoding='utf-8').splitlines()]
    for f in sorted(args.run.glob('k[0-9][0-9]/RESULT.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        line = d['fault'].get('lmkd_line', '')
        adj = line.split('oom_score_adj')[1].split()[0].strip(',;') if 'oom_score_adj' in line else ''
        rows.append(dict(trial=d['name'], reaped=d['reaped'], filled_mb=d['fault'].get('filled_mb', ''),
                         oom_score_adj=adj, copies_at_relaunch=d['copies_at_origin'],
                         relaunch_to_sent_s=round(d['lag_s'], 2) if d['lag_s'] is not None else '',
                         server_copies_final=len(d['server_copies_final']),
                         retry_replies_dropped=d['retry_replies_dropped'],
                         resends_after_fault=resends(events, d['clock']['barrier_utc_ns'])))
    invalid = sum(1 for p in args.run.iterdir() if p.is_dir() and 'INVALID' in p.name and p.name.startswith('k'))
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / 'trials.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    reaped = [r for r in rows if r['reaped']]
    lags = [r['relaunch_to_sent_s'] for r in reaped if r['relaunch_to_sent_s'] != '']
    mbs = [r['filled_mb'] for r in reaped]
    lines = ['# Element reaped by lmkd after a lost reply (ELMK, b-log 23/11)', '',
             'Generated by `testbed/element_lmk.py summarize` from the run directory (outside the repo). AVD x86_64, '
             'Element classic 1.6.62, Synapse 1.164.2 behind the fault proxy in sticky mode.', '',
             '| Trial | Reaped | Filled (MB) | oom_score_adj | Copies at relaunch | Relaunch to "Sent" (s) | Final copies '
             '| Retry replies dropped | Same-txnId re-sends after the fault |', '|---|---|---|---|---|---|---|---|---|']
    lines += ['| ' + ' | '.join(str(r[k]) for k in rows[0]) + ' |' for r in rows]
    lines += ['', '- Valid trials: %d (INVALID, rig: %d). lmkd reaped Element in %d of them.' % (len(rows), invalid,
                                                                                            len(reaped))]
    if reaped:
        lines += ['- Memory filled when reaped: from %d to %d MB (median %d).' % (min(mbs), max(mbs),
                                                                                 statistics.median(mbs)),
                  '- Exactly one server copy after the relaunch: %d of %d reaped trials.' % (
                      sum(r['server_copies_final'] == 1 for r in reaped), len(reaped)),
                  '- Element re-sent the same txnId after the relaunch in %d of %d reaped trials (Synapse kept one '
                  'copy); the rest reconciled without a re-send.' % (
                      sum(bool(r['resends_after_fault']) for r in reaped), len(reaped))]
    if lags:
        lines.append('- Relaunch to a "Sent" row: min %.1f, median %.1f, max %.1f s (%d of %d reaped trials seen).' % (
            min(lags), statistics.median(lags), max(lags), len(lags), len(reaped)))
    (args.out / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--out', type=Path, required=True)
    r.add_argument('--adb', required=True)
    r.add_argument('--serial', default='emulator-5582')
    r.add_argument('--trials', type=int, default=10)
    r.add_argument('--prefix', default='k')
    s = sub.add_parser('summarize')
    s.add_argument('--run', type=Path, required=True)
    s.add_argument('--out', type=Path, default=ROOT / 'artifact/results/real/emu_element_lmk')
    a = p.parse_args()
    run(a) if a.cmd == 'run' else summarize(a)


if __name__ == '__main__':
    main()
