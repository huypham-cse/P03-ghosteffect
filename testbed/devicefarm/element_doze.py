"""Element under Doze after a lost reply, on a rented phone (pre-registered in team/b-log.md, 25/11).

  python3 testbed/devicefarm/element_doze.py --adb <adb> --serial <serial> --out <dir> [--trials d00:120,d01:600,...]

One trial: alice composes a nonce-tagged message in room "gx test"; the proxy runs in sticky mode (it forwards the PUT
so Synapse commits, holds the reply and drops every same-txnId retry until the fault receipt); the driver taps Send,
waits for the commit barrier, sends Element HOME (the agent died; Element stays alive in the background), unplugs the
battery, turns the screen off and forces deep idle (caldav_fault_case.doze_enter, as the DAVx5 Doze runs on the A36
and Pixel 9), releases the arm, and holds Doze for the trial's seconds while sampling the idle state and Element's PID
every 15 s. It then leaves Doze, relaunches Element and polls the timeline until the row reads "Sent" (at most 120 s
from the Doze exit); after 30 more seconds the server copies are graded as bob. From the proxy journal: every
same-txnId request after the fault receipt, timed from the Doze entry and exit (did Element re-send while dozing?).
Reuses element_planner.py's helpers without changing that file.
"""
import argparse
import json
from pathlib import Path
import random
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caldav_planner as cp   # noqa: E402
import element_planner as ep   # noqa: E402
from caldav_fault_case import doze_enter, doze_exit   # noqa: E402
from faultproxy import Journal, Faults, http_proxy   # noqa: E402
from k9_fault_case import CROCKFORD   # noqa: E402

POLL_SECONDS, SETTLE_SECONDS, SAMPLE_SECONDS = 120, 30, 15


def resend_times(journal, arm):
    """utc_ns of every request with the arm's txnId that reached the proxy after its fault receipt."""
    events = [json.loads(l) for l in journal.read_text(encoding='utf-8').splitlines()]
    bar = next((e for e in events if e['event'] == 'PRE_ACK_BARRIER' and e.get('arm_id') == arm), None)
    fault = next((e['utc_ns'] for e in events if e['event'] == 'FAULT_RECEIPT' and e.get('arm_id') == arm), None)
    if bar is None or fault is None:
        return []
    return [e['utc_ns'] for e in events if e['event'] == 'REQUEST' and e.get('request_id') == bar['request_id']
            and e['utc_ns'] > fault]


def trial(phone, grader, faults, out, hold_s, journal):
    out.mkdir(parents=True, exist_ok=False)
    phone.sh('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
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
    phone.sh('input keyevent KEYCODE_HOME')
    time.sleep(2)
    fault = doze_enter(phone.sh)
    fault['utc_ns'] = clock['doze_enter_utc_ns'] = time.time_ns()
    faults.release(arm, fault)
    samples, end = [], time.monotonic() + hold_s
    while time.monotonic() < end:
        samples.append(dict(utc_ns=time.time_ns(), deep=phone.sh('dumpsys deviceidle get deep'),
                            pid=phone.sh('pidof ' + ep.ELEMENT)))
        time.sleep(min(SAMPLE_SECONDS, max(0, end - time.monotonic())))
    doze_exit(phone.sh)
    clock['doze_exit_utc_ns'] = time.time_ns()
    phone.sh('wm dismiss-keyguard')
    copies_at_exit = len(grader.copies(nonce))
    ep.launch(phone)
    origin, lag = time.monotonic(), None
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
    resends = resend_times(journal, arm)
    result = dict(name=out.name, nonce=nonce, hold_s=hold_s, fault=fault, doze_states=sorted({s['deep'] for s in samples}),
                  element_alive_in_doze=all(s['pid'] for s in samples), samples=samples, copies_at_exit=copies_at_exit,
                  exit_to_sent_s=lag, server_copies_final=grader.copies(nonce),
                  resends_s_from_enter=[round((t - clock['doze_enter_utc_ns']) / 1e9, 2) for t in resends],
                  resends_during_doze=sum(t < clock['doze_exit_utc_ns'] for t in resends), clock=clock)
    cp.write_json(out / 'RESULT.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--trials', default='d00:120,d01:600,d02:600,d03:600', help='name:Doze seconds, in order')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    phone = cp.Phone(a.adb, a.serial)
    phone.adb('reverse', 'tcp:%d' % ep.PROXY_PORT, 'tcp:%d' % ep.PROXY_PORT)
    journal = a.out / 'proxy.jsonl'
    faults = Faults(Journal(journal), barrier_timeout=60)
    server = http_proxy(ep.SYNAPSE, 'matrix', faults, listen=('127.0.0.1', ep.PROXY_PORT))
    threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
    # Setup reached Synapse straight through the same phone port; Element keeps those HTTP connections alive, so its
    # sends would bypass the proxy (AVD 25/11: no committed PUT seen). A restart before the first trial opens new
    # connections, which go through the proxy.
    phone.sh('am force-stop ' + ep.ELEMENT)
    ep.launch(phone)
    time.sleep(8)
    grader = ep.Grader()
    streak = 0
    try:
        for item in a.trials.split(','):
            name, hold = item.split(':')
            try:
                r = trial(phone, grader, faults, a.out / name, int(hold), journal)
                line = '%s ok hold=%s states=%s alive=%s resends=%s during=%d exit_to_sent=%s copies=%d' % (
                    name, hold, r['doze_states'], r['element_alive_in_doze'], r['resends_s_from_enter'],
                    r['resends_during_doze'], r['exit_to_sent_s'], len(r['server_copies_final']))
                streak = 0
            except Exception as exc:   # rig failure: kept on disk, not scored, not replaced
                doze_exit(phone.sh)
                bad = a.out / name
                bad.mkdir(exist_ok=True)
                (bad / 'INVALID.json').write_text(json.dumps(dict(error_type=type(exc).__name__, reason=str(exc))))
                bad.rename(a.out / (name + '-INVALID-%d' % time.time_ns()))
                arm = faults.arm
                if arm and not arm['released'].is_set():
                    if arm['reached'].is_set():
                        faults.release(arm['id'], dict(observed_class='rig-abort'))
                    else:
                        arm['released'].set()
                line = '%s INVALID %s: %s' % (name, type(exc).__name__, exc)
                streak += 1
            with open(a.out / 'batch.log', 'a', encoding='utf-8') as f:
                f.write(time.strftime('%H:%M:%S ') + line + '\n')
            print(line, flush=True)
            if (name == 'd00' and streak) or streak >= 2:   # same abort rule as the DAVx5 runs
                with open(a.out / 'batch.log', 'a', encoding='utf-8') as f:
                    f.write(time.strftime('%H:%M:%S ') + 'ABORT: rig failure\n')
                break
    finally:
        doze_exit(phone.sh)
        server.shutdown()
        server.server_close()
        grader.close()


if __name__ == '__main__':
    main()
