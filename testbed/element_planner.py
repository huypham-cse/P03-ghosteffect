"""TN4 (b-log 22/11): held-out validation of the GUI-only planner (recovery.py) on Element + Synapse (AVD), where both
outcome sides can be certified.

  python testbed/element_planner.py schedule --split calibration|test --seed N --out <schedule.json>
  python testbed/element_planner.py collect --schedule <schedule.json> --out <run dir> [--store <store.json>] --adb <adb>
  python testbed/element_planner.py report --run <test run dir>

One trial is one interrupted effect: alice sends a message whose body carries a fresh nonce in room "gx test" (the
body is counterparty-visible, so the accounts are opted-in test accounts on a local Synapse).
  X=1: the agent taps Send, the proxy forwards Element's PUT /send, Synapse commits, the proxy holds the reply until the
       fault receipt and then drops it; Element's own same-txnId retry is not dropped.
  X=0: the message is typed in the composer and the fault lands before Send (nothing is sent).
Fault classes: none; app-kill (HOME, then kill -9); force-stop; netcut (Wi-Fi and mobile data off for 20 s, Element
in the foreground). The recovery origin is the controller's relaunch of Element, after the network is back for netcut.
The planner reads only Element's GUI. One end-to-end family, nonce, with the two views the calibration format asks for:
  timeline: the room's timeline has a message row whose text carries the nonce (the composer never counts);
  roomlist: the room's row in the room list shows the nonce in its last-message line.
Views within a family may depend on each other arbitrarily, and one family needs no cross-family independence (A2).
Element has no hop-1 family (its send state is drawn with the lagged row), so both sides are certified from the nonce
family after a certified wait from the per-class lag table. Backend truth (Synapse, read as bob) is used only for
grading and the calibration labels, never by the planner.
"""
import argparse
import json
import os
import random
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caldav_planner as cp   # noqa: E402  (Phone, write_json, sha_source)
from faultproxy import Journal, Faults, http_proxy   # noqa: E402
from k9_fault_case import CROCKFORD   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ELEMENT = 'im.vector.app'
ROOM = 'gx test'
CLASSES = ('none', 'app-kill', 'force-stop')   # as TN1; netcut is implemented but not in the frozen design (sizes)
STRATUM = 'element-synapse-avd'
SYNAPSE = 'http://127.0.0.1:8008'
PROXY_PORT = 18008
ACCOUNTS = Path(os.environ.get('GX_ELEMENT_ACCOUNTS', str(ROOT / 'runtime' / 'element.local.json')))   # ignored file
NETCUT_SECONDS = 20
ABSENT_WAIT = 15        # calibration of X=0 reads waits as long as a typical certified wait before reading


def domain():
    return dict(app_package=ELEMENT, app_version='element-classic-1.6.62(40106624)',
                backend_revision='synapse-1.164.2;faultproxy', reader_revision=cp.sha_source(__file__),
                verifier_revision='none', locale='en-US', abi='x86_64', load_profile='avd-api33-x86_64-whpx-host',
                policy_revision=cp.sha_source(ROOT / 'testbed/recovery.py'), origin_kind='recovery')


class Grader:
    """Backend truth as bob (a second, read-only device); never consulted by the planner."""

    def __init__(self):
        self.cfg = json.loads(ACCOUNTS.read_text())
        self.room = self.cfg['room_id']
        self.token = self.call('POST', '/_matrix/client/v3/login', dict(
            type='m.login.password', identifier=dict(type='m.id.user', user='bob'),
            password=self.cfg['bob']['password'], device_id='GXGRADER'))['access_token']

    def call(self, method, path, body=None):
        req = urllib.request.Request(SYNAPSE + path, method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={'Content-Type': 'application/json',
                                              **({'Authorization': 'Bearer ' + self.token}
                                                 if getattr(self, 'token', None) else {})})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    def copies(self, nonce):
        q = urllib.parse.quote(self.room)
        events = self.call('GET', '/_matrix/client/v3/rooms/%s/messages?dir=b&limit=60' % q)['chunk']
        return [e['event_id'] for e in events if e.get('type') == 'm.room.message'
                and e.get('sender') == '@alice:ghost.test' and nonce in (e.get('content') or {}).get('body', '')]

    def close(self):
        try:
            self.call('POST', '/_matrix/client/v3/logout', {})
        except OSError:
            pass


def tree(phone):
    xml = phone.sh('uiautomator dump /sdcard/gx_ui.xml >/dev/null && cat /sdcard/gx_ui.xml; rm -f /sdcard/gx_ui.xml')
    root = ET.fromstring(xml[xml.index('<'):]) if '<' in xml else None
    return xml, root


def rid(node):
    return (node.get('resource-id') or '').split('/')[-1]


def find(root, ident):
    return [] if root is None else [n for n in root.iter('node') if rid(n) == ident and n.get('package') == ELEMENT]


def center(node):
    x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap(phone, node):
    phone.sh('input tap %d %d' % center(node))


def launch(phone):
    phone.sh('monkey -p %s -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1' % ELEMENT)


def in_room(root):
    return any((n.get('text') or '') == ROOM for n in find(root, 'roomToolbarTitleView')) and bool(find(root, 'composerEditText'))


def room_row(root):
    """The room list's row for ROOM: (name node, subtitle node) or (None, None)."""
    for row in find(root, 'itemRoomLayout'):
        names = [n for n in row.iter('node') if rid(n) == 'roomNameView' and (n.get('text') or '') == ROOM]
        if names:
            subs = [n for n in row.iter('node') if rid(n) == 'subtitleView']
            return names[0], (subs[0] if subs else None)
    return None, None


def dismiss(phone, root):
    """Close the notification-permission rationale (Element) or the system permission prompt; True if one was shown.
    Notifications stay denied on this AVD so that no heads-up banner covers a read."""
    if root is None:
        return False
    for n in root.iter('node'):
        ident, text = rid(n), (n.get('text') or '').upper()
        if (ident == 'button2' and text == 'NOT NOW' and n.get('package') == ELEMENT) or ident == 'permission_deny_button':
            tap(phone, n)
            time.sleep(1)
            return True
    return False


def to_room(phone, timeout=25):
    """Navigate to ROOM's timeline from wherever Element is; returns the dump that verified it, or raises."""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        xml, root = tree(phone)
        if dismiss(phone, root):
            continue
        if in_room(root):
            return xml, root
        pkg = root.find('.//node').get('package') if root is not None and root.find('.//node') is not None else ''
        name, _ = room_row(root)
        if name is not None:
            tap(phone, name)
        elif pkg != ELEMENT:
            launch(phone)
        else:
            phone.sh('input keyevent KEYCODE_BACK')
        time.sleep(1.5)
    raise RuntimeError('could not reach the room timeline')


def to_list(phone, timeout=25):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        xml, root = tree(phone)
        if dismiss(phone, root):
            continue
        name, sub = room_row(root)
        if name is not None and sub is not None:
            return xml, root
        pkg = root.find('.//node').get('package') if root is not None and root.find('.//node') is not None else ''
        if pkg != ELEMENT:
            launch(phone)
        else:
            phone.sh('input keyevent KEYCODE_BACK')
        time.sleep(1.5)
    raise RuntimeError('could not reach the room list')


def row_has(root, nonce):
    """A timeline row with the nonce counts only once the server's echo replaced Element's local echo: its send-state
    indicator, when drawn, must read "Sent" (A1: an end-to-end view shows only applied effects)."""
    if root is None:
        return False
    for row in root.iter('node'):
        texts = [n for n in row if rid(n) == 'messageTextView' and nonce in (n.get('text') or '')]
        if texts:
            states = [n.get('content-desc') or '' for n in row if rid(n) == 'messageSendStateImageView']
            if not states or states[0] == 'Sent':
                return True
    return False


class ElementObserver:
    """GUI-only reads. read() returns 1, 0, or None (view not verified); every read keeps its dump."""

    def __init__(self, phone, nonce, outdir):
        self.phone, self.nonce, self.outdir, self.reads = phone, nonce, outdir, []

    def verify_context(self):
        focus = self.phone.sh('dumpsys window | grep -E "mCurrentFocus"')
        return 'Not Responding' not in focus and 'NotificationShade' not in focus and 'Keyguard' not in focus

    def read(self, family, view):
        value, xml = None, ''
        try:
            if (family, view) == ('nonce', 'timeline'):
                xml, root = to_room(self.phone)
                if find(root, 'jumpToBottomView'):   # absent only on a timeline scrolled to the bottom
                    tap(self.phone, find(root, 'jumpToBottomView')[0])
                    time.sleep(1)
                    xml, root = tree(self.phone)
                if row_has(root, self.nonce):
                    value = 1
                elif in_room(root) and find(root, 'messageTextView') and not find(root, 'jumpToBottomView'):
                    time.sleep(1.5)   # a row can arrive right after the room opens: one more look
                    xml, root = tree(self.phone)
                    value = 1 if row_has(root, self.nonce) else (0 if in_room(root) else None)
            elif (family, view) == ('nonce', 'roomlist'):
                xml, root = to_list(self.phone)
                _, sub = room_row(root)
                value = None if sub is None else (1 if self.nonce in (sub.get('text') or '') else 0)
            else:
                raise ValueError((family, view))
        except RuntimeError:
            value = None
        name = 'read-%d-%s.xml' % (len(self.reads), view)
        (self.outdir / name).write_text(xml, encoding='utf-8')
        self.reads.append(dict(family=family, view=view, value=value, utc_ns=time.time_ns(), dump=name))
        return value

    def monitor(self):
        return dict(state='stuck')   # no hop-1 family: never reached


def clear_composer(phone):
    _, root = tree(phone)
    box = find(root, 'composerEditText')
    if box and (box[0].get('text') or '') not in ('', 'Message…', 'Message\u2026', 'Message'):
        tap(phone, box[0])
        phone.sh('input keyevent KEYCODE_MOVE_END; for i in $(seq 1 60); do input keyevent KEYCODE_DEL; done')


def compose(phone, body):
    _, root = to_room(phone)
    box = find(root, 'composerEditText')
    tap(phone, box[0])
    phone.sh("input text '%s'" % body.replace(' ', '%s'))
    time.sleep(.5)
    _, root = tree(phone)
    if not any(body in (n.get('text') or '') for n in find(root, 'composerEditText')):
        raise RuntimeError('composer does not hold the message')
    return root


def tap_send(phone):
    _, root = tree(phone)
    send = find(root, 'sendButton')
    if not send:
        raise RuntimeError('no Send button')
    tap(phone, send[0])
    return dict(utc_ns=time.time_ns(), mono=time.monotonic())


def network(phone, on):
    verb = 'enable' if on else 'disable'
    phone.sh('svc wifi %s; svc data %s' % (verb, verb))


def apply_fault(phone, cls):
    receipt = dict(fault_class=cls, utc_ns=time.time_ns())
    if cls == 'app-kill':
        phone.sh('input keyevent KEYCODE_HOME')
        time.sleep(1)
        before = phone.sh('pidof ' + ELEMENT).split()
        if before:
            phone.sh('kill -9 ' + ' '.join(before))
        receipt.update(observed_class='app-sigkill', pids_before=before, pids_after=phone.sh('pidof ' + ELEMENT).split())
    elif cls == 'force-stop':
        phone.sh('am force-stop ' + ELEMENT)
        receipt.update(observed_class='app-force-stop', pids_after=phone.sh('pidof ' + ELEMENT).split())
    elif cls == 'netcut':
        network(phone, False)
        receipt.update(observed_class='network-cut', seconds=NETCUT_SECONDS)
    elif cls == 'none':
        receipt.update(observed_class='none')
    else:
        raise ValueError(cls)
    return receipt


def trial(ctx, item, store):
    phone, grader, faults, out = ctx['phone'], ctx['grader'], ctx['faults'], ctx['out'] / item['name']
    out.mkdir(parents=True, exist_ok=False)
    x, cls = item['x'], item['fault_class']
    phone.sh('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
    network(phone, True)
    to_room(phone)
    clear_composer(phone)
    nonce = 'gx:' + ''.join(random.SystemRandom().choice(CROCKFORD) for _ in range(6))
    body = 'gx test message %s' % nonce
    clock = dict(start_utc_ns=time.time_ns())
    compose(phone, body)
    issued_mono = time.monotonic()
    if x == 1:
        arm = faults.configure('drop')
        clock['send_tap'] = tap_send(phone)
        deadline = time.monotonic() + 30
        while not faults.status(arm)['barrier']:
            if time.monotonic() > deadline:
                raise RuntimeError('no committed PUT within the barrier timeout')
            time.sleep(.05)
        clock['barrier_utc_ns'] = time.time_ns()
        fault = apply_fault(phone, cls)
        faults.release(arm, fault)
    else:
        fault = apply_fault(phone, cls)
    clock['fault_utc_ns'] = fault['utc_ns']
    if cls == 'netcut':
        time.sleep(NETCUT_SECONDS)
        network(phone, True)
        fault['restored_utc_ns'] = time.time_ns()
    else:
        time.sleep(2)
    if cls in ('app-kill', 'force-stop'):
        launch(phone)
    origin_mono, clock['origin_utc_ns'] = time.monotonic(), time.time_ns()
    copies_at_origin = grader.copies(nonce)
    if x == 0 and copies_at_origin:
        raise RuntimeError('X=0 but the message reached the server')
    observer = ElementObserver(phone, nonce, out)
    result = dict(name=item['name'], split=item['split'], x=x, fault_class=cls, nonce=nonce)
    if store is None:
        lag = None
        if x == 1:   # poll the timeline until the row is visible: the upper end of the first dump that shows it
            end = origin_mono + 120
            while time.monotonic() < end:
                try:
                    _, root = to_room(phone, timeout=10)
                    if row_has(root, nonce):
                        lag = time.monotonic() - origin_mono
                        break
                except RuntimeError:
                    pass
                time.sleep(.3)
        else:
            time.sleep(ABSENT_WAIT)
        result['lag_upper_seconds'] = lag
        result['views'] = dict(nonce=[observer.read('nonce', 'timeline'), observer.read('nonce', 'roomlist')])
    else:
        from recovery import Recovery
        context = dict(fault_class=cls, origin_kind='recovery', origin_verified=True, origin_mono_seconds=origin_mono,
                       g2_eligible=False, force_stopped=cls == 'force-stop', issued_mono_seconds=issued_mono,
                       dedup_horizon_seconds=86400, lookalike=False)
        decision = Recovery(store, observer).resolve(domain(), context)
        result.update(decision=decision['decision'], reason=decision['reason'], trace=decision['trace'],
                      views=[r['value'] for r in observer.reads])
        if decision['decision'] == 'RETRY':   # the agent sends the same message again through the GUI
            to_room(phone)
            clear_composer(phone)
            compose(phone, body)
            result['redo_tap'] = tap_send(phone)
            end = time.monotonic() + 60
            while time.monotonic() < end and not grader.copies(nonce):
                time.sleep(1)
            time.sleep(3)
    time.sleep(1)
    to_room(phone)
    clear_composer(phone)
    result['server_copies_final'] = grader.copies(nonce)
    backend = dict(server_copies_at_origin=copies_at_origin, server_copies_final=result['server_copies_final'],
                   proxy_journal='proxy.jsonl')
    refs = dict(backend=cp.write_json(out / 'backend.json', backend), fault=cp.write_json(out / 'fault.json', fault),
                probes=cp.write_json(out / 'probes.json', observer.reads), clock=cp.write_json(out / 'clock.json', clock))
    result['evidence'] = refs
    cp.write_json(out / 'RESULT.json', result)
    return result


def calibration_row(r):
    return dict(stratum=STRATUM, fault_class=r['fault_class'], X_backend=r['x'], split='calibration',
                effect_id=r['nonce'], domain=domain(), population='interrupted',
                evidence_kind='interrupted_measurement', origin_kind='recovery', origin_verified=True,
                terminal_fate='committed' if r['x'] else 'terminal_nonapply', probe_eligibility_verified=True,
                views=r['views'], lag_upper_seconds=r['lag_upper_seconds'], evidence=r['evidence'])


def collect(args):
    schedule = json.loads(args.schedule.read_text(encoding='utf-8'))
    args.out.mkdir(parents=True, exist_ok=True)
    phone = cp.Phone(args.adb, args.serial)
    if phone.sh('whoami') != 'root':
        phone.adb('root', timeout=60)
        phone.adb('wait-for-device', timeout=120)
    phone.adb('reverse', 'tcp:%d' % PROXY_PORT, 'tcp:%d' % PROXY_PORT)
    store = None
    if args.store:
        from calibration import load_store
        store = load_store(args.store)
        if [s['domain'] for s in store['strata']] != [domain()]:
            raise SystemExit('store domain does not match this reader/policy revision; recalibrate')
    faults = Faults(Journal(args.out / 'proxy.jsonl'), barrier_timeout=60)
    server = http_proxy(SYNAPSE, 'matrix', faults, listen=('127.0.0.1', PROXY_PORT))
    threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
    grader = Grader()
    ctx = dict(phone=phone, out=args.out, grader=grader, faults=faults)
    log = args.out / 'batch.log'
    queue = list(schedule['trials'])
    done = {p.name for p in args.out.iterdir() if (p / 'RESULT.json').exists()}
    replacements = 0
    try:
        while queue:
            item = queue.pop(0)
            if item['name'] in done:
                continue
            try:
                r = trial(ctx, item, store)
                line = '%s ok x=%d %s views=%s %s lag=%s copies=%d' % (
                    item['name'], r['x'], r['fault_class'], r['views'], r.get('decision', ''),
                    r.get('lag_upper_seconds'), len(r['server_copies_final']))
                with open(args.out / ('effects.jsonl' if store is None else 'decisions.jsonl'), 'a', encoding='utf-8') as f:
                    f.write(json.dumps(calibration_row(r) if store is None else r) + '\n')
            except Exception as exc:   # a rig failure: INVALID, kept on disk, replaced at the end of the queue
                bad = args.out / item['name']
                bad.mkdir(exist_ok=True)
                (bad / 'INVALID.json').write_text(json.dumps(dict(error_type=type(exc).__name__, reason=str(exc))))
                bad.rename(args.out / (item['name'] + '-INVALID-%d' % time.time_ns()))
                replacements += 1
                network(phone, True)
                a = faults.arm
                if a and not a['released'].is_set():   # never leave an arm behind for the next trial
                    if a['reached'].is_set():
                        faults.release(a['id'], dict(observed_class='rig-abort'))
                    else:
                        faults.log.emit('RIG_ABORT_UNMATCHED_ARM', arm_id=a['id'])
                        a['released'].set()
                if replacements > schedule.get('max_replacements', 80):
                    raise SystemExit('too many INVALID trials: rig failure')
                queue.append(item)
                line = '%s INVALID %s: %s' % (item['name'], type(exc).__name__, exc)
            with open(log, 'a', encoding='utf-8') as f:
                f.write(time.strftime('%H:%M:%S ') + line + '\n')
            print(line, flush=True)
    finally:
        network(phone, True)
        server.shutdown()
        server.server_close()
        grader.close()


def make_schedule(args):
    counts = {1: args.committed, 0: args.absent} if args.split == 'calibration' else {1: 40, 0: 40}
    items = [dict(x=x, fault_class=c) for c in CLASSES for x, n in counts.items() for _ in range(n)]
    random.Random(args.seed).shuffle(items)
    prefix = 'c' if args.split == 'calibration' else 't'
    for i, item in enumerate(items):
        item.update(name='%s%04d' % (prefix, i), split=args.split)
    args.out.write_text(json.dumps(dict(split=args.split, seed=args.seed, counts={str(k): v for k, v in counts.items()},
                                        classes=list(CLASSES), max_replacements=80, trials=items), indent=1),
                        encoding='utf-8')
    print(args.out, len(items))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('schedule')
    s.add_argument('--split', choices=['calibration', 'test'], required=True)
    s.add_argument('--seed', type=int, required=True)
    s.add_argument('--committed', type=int, default=190)
    s.add_argument('--absent', type=int, default=170)
    s.add_argument('--out', type=Path, required=True)
    c = sub.add_parser('collect')
    c.add_argument('--schedule', type=Path, required=True)
    c.add_argument('--out', type=Path, required=True)
    c.add_argument('--store', type=Path)
    c.add_argument('--adb', required=True)
    c.add_argument('--serial', default='emulator-5582')
    r = sub.add_parser('report')
    r.add_argument('--run', type=Path, required=True)
    a = p.parse_args()
    os.environ.setdefault('ANDROID_ADB_SERVER_PORT', '5038')
    dict(schedule=make_schedule, collect=collect, report=cp.report)[a.cmd](a)


if __name__ == '__main__':
    main()
