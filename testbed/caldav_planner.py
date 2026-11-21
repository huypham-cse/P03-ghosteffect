"""TN1 (b-log 19/11): held-out validation of the GUI-only planner (recovery.py) on Etar + DAVx5 + Radicale (AVD only).

  python testbed/caldav_planner.py schedule --split calibration|test --seed N --out <schedule.json>
  python testbed/caldav_planner.py collect --schedule <schedule.json> --out <run dir> [--store <store.json>] --adb <adb>
  python testbed/caldav_planner.py report --run <test run dir>

One trial is one interrupted effect: "create an event whose title is a fresh nonce" in Etar, synced by DAVx5 to Radicale.
  X=1: the agent taps DONE, DAVx5 PUTs, Radicale commits, the proxy holds the reply; the fault lands; the reply is dropped.
  X=0: the agent opens the edit screen with the title filled in, and the fault lands before DONE (nothing is saved:
       Etar keeps no draft on pause, kill or force-stop; checked on the AVD 19/11).
Fault classes, applied to both apps of the effect (Etar and DAVx5): none; app-kill (kill -9); force-stop.
The planner then reads only Etar's GUI. Family hop1 (the app's local store, shown from the save tap on) has two views:
  search: Etar's search for the nonce; agenda: Etar's agenda, where the event is placed 2 h after now.
There is no GUI view of the hop-2 acknowledgement (DAVx5 shows no per-event or last-sync state, and Android's account
sync page lists none of its adapters), so the stratum declares G2 unusable: a committed effect cannot be certified and
is asked; an absent one can be certified from hop1 and retried. Backend truth (Radicale's store) and the calendar
provider are read only for grading and cleanup, never by the planner.
Calibration rows follow calibration.compile_store; the test split runs recovery.Recovery with the frozen store and
executes its decision (RETRY: the agent recomposes the same event through the GUI).
"""
import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caldav_fault_case as cf   # noqa: E402
from faultproxy import Journal, Faults, http_proxy, control_server   # noqa: E402
from k9_fault_case import CROCKFORD   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ETAR, DAVX5 = cf.ETAR, cf.DAVX5
CLASSES = ('none', 'app-kill', 'force-stop')
STRATUM = 'etar-davx5-avd'
SA_EVENTS = ('content://com.android.calendar/events?caller_is_syncadapter=true'
             '&account_name=alice&account_type=bitfire.at.davdroid')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_source(path):
    """Revision hash of a source file, independent of the CRLF/LF checkout (git autocrlf on this host)."""
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def domain():
    """Exact-match runtime domain; reader and policy revisions are the hashes of this file and recovery.py."""
    return dict(app_package=ETAR, app_version='etar-1.0.57(57)',
                backend_revision='radicale-3.9.0;davx5-4.5.21-ose(405210002);faultproxy',
                reader_revision=sha_source(__file__), verifier_revision='none', locale='en-US', abi='x86_64',
                load_profile='avd-api33-x86_64-whpx-host', policy_revision=sha_source(ROOT / 'testbed/recovery.py'),
                origin_kind='recovery')


class Phone:
    def __init__(self, adb, serial):
        self.base = [str(adb), '-s', serial]

    def sh(self, cmd, timeout=60):
        return subprocess.run(self.base + ['shell', cmd], capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=timeout).stdout.strip()

    def adb(self, *args, timeout=60):
        return subprocess.run(self.base + list(args), capture_output=True, text=True, timeout=timeout).stdout.strip()

    def nodes(self):
        xml = self.sh('uiautomator dump /sdcard/gx_ui.xml >/dev/null && cat /sdcard/gx_ui.xml; rm -f /sdcard/gx_ui.xml')
        return xml, (list(ET.fromstring(xml[xml.index('<'):]).iter('node')) if '<' in xml else [])


class EtarObserver:
    """GUI-only reads of family hop1. read() returns 1 (row with the nonce), 0 (the view loaded and has no such row),
    or None (the view could not be verified). Each read saves its screen dump next to the trial's probes."""

    def __init__(self, phone, nonce, outdir):
        self.phone, self.nonce, self.outdir, self.reads = phone, nonce, outdir, []

    def verify_context(self):
        focus = self.phone.sh('dumpsys window | grep -E "mCurrentFocus"')
        return 'Not Responding' not in focus and 'NotificationShade' not in focus and 'Keyguard' not in focus

    def read(self, family, view):
        if family != 'hop1':
            raise ValueError('only hop1 is defined for Etar')
        # -S: every read relaunches Etar into a known view; with Etar's task alive, a SEARCH intent only brought the
        # agenda back to front (AVD check 19/11).
        if view == 'search':
            self.phone.sh('am start -S -W -n %s/com.android.calendar.SearchActivity -a android.intent.action.SEARCH '
                          "--es query '%s'" % (ETAR, self.nonce))
        elif view == 'agenda':
            self.phone.sh('am start -S -W -n %s/com.android.calendar.AllInOneActivity -a android.intent.action.MAIN'
                          % ETAR)
        else:
            raise ValueError(view)
        deadline, value, xml, loaded = time.monotonic() + 10, None, '', False
        while time.monotonic() < deadline:
            xml, nodes = self.phone.nodes()
            etar = [n for n in nodes if n.get('package') == ETAR]
            ids = {(n.get('resource-id') or '').split('/')[-1]: n for n in etar}
            # Either list has loaded when its "Touch to view events after ..." footer is shown; search also needs
            # its query box to hold this nonce.
            footer = any((n.get('text') or '').startswith('Touch to view events after') for n in etar)
            query = ids.get('search_src_text')
            loaded = footer and (view == 'agenda' or (query is not None and (query.get('text') or '') == self.nonce))
            hit = any((n.get('resource-id') or '').endswith('/title') and (n.get('text') or '') == self.nonce for n in etar)
            if hit:
                value = 1
                break
            if loaded:
                time.sleep(1.5)   # rows can arrive after the header; one more look before calling it absent
                xml, nodes = self.phone.nodes()
                hit = any(n.get('package') == ETAR and (n.get('resource-id') or '').endswith('/title')
                          and (n.get('text') or '') == self.nonce for n in nodes)
                value = 1 if hit else 0
                break
            time.sleep(.5)
        name = 'read-%d-%s.xml' % (len(self.reads), view)
        (self.outdir / name).write_text(xml, encoding='utf-8')
        self.reads.append(dict(family=family, view=view, value=value, utc_ns=time.time_ns(), dump=name))
        self.phone.sh('input keyevent KEYCODE_HOME')
        return value

    def monitor(self):
        # Never reached with G2 unusable; kept explicit so a changed store cannot silently claim an ack.
        return dict(state='stuck')


def local_rows(phone, nonce):
    out = phone.sh("content query --uri content://com.android.calendar/events --projection _id:title:dirty:deleted "
                   "--where \"title='%s'\"" % nonce)
    return [] if out.startswith('No result') else [line for line in out.splitlines() if line.startswith('Row:')]


def cleanup(phone, nonce=None):
    """Rig cleanup between trials: hard-delete test events as the sync adapter (no dirty flag, so DAVx5 uploads
    nothing) and remove their .ics from Radicale's store. Keeps the agenda to the current trial's event."""
    phone.sh('am force-stop ' + ETAR)   # discards an unsaved draft (X=0, class none)
    phone.sh("content delete --uri '%s' --where \"title LIKE 'gx:%%'\"" % SA_EVENTS)
    folder = cf.STORE / 'collection-root' / 'alice' / 'cal'
    removed = 0
    for path in folder.glob('*.ics'):
        if nonce is None or 'gx:' in path.read_text(encoding='utf-8', errors='replace'):
            path.unlink()
            removed += 1
    return removed


def apply_fault(phone, cls):
    receipt = dict(fault_class=cls, utc_ns=time.time_ns())
    if cls == 'app-kill':
        pids = {pkg: phone.sh('pidof ' + pkg).split() for pkg in (ETAR, DAVX5)}
        for pkg_pids in pids.values():
            if pkg_pids:
                phone.sh('kill -9 ' + ' '.join(pkg_pids))
        receipt.update(observed_class='app-sigkill', pids_before=pids,
                       pids_after={pkg: phone.sh('pidof ' + pkg).split() for pkg in (ETAR, DAVX5)})
    elif cls == 'force-stop':
        for pkg in (ETAR, DAVX5):
            phone.sh('am force-stop ' + pkg)
        receipt.update(observed_class='app-force-stop')
    elif cls == 'none':
        receipt.update(observed_class='none')
    else:
        raise ValueError(cls)
    return receipt


def open_edit(phone, nonce, begin_ms):
    phone.sh('am force-stop ' + ETAR)
    phone.sh("am start -W -n %s/com.android.calendar.EditEventActivity -a android.intent.action.INSERT "
             "-t vnd.android.cursor.item/event --es title '%s' --el beginTime %d --el endTime %d"
             % (ETAR, nonce, begin_ms, begin_ms + 3_600_000))
    time.sleep(3)


def edit_screen_up(phone):
    _, nodes = phone.nodes()
    return any(n.get('package') == ETAR and (n.get('resource-id') or '').endswith('/action_done') for n in nodes)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return dict(path=path.relative_to(path.parents[1]).as_posix(), sha256=sha_file(path))


def trial(ctx, item, store):
    phone, out = ctx['phone'], ctx['out'] / item['name']
    out.mkdir(parents=True, exist_ok=False)
    x, cls = item['x'], item['fault_class']
    phone.sh('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
    removed = cleanup(phone)
    if cf.dirty_events(phone.sh) != 'No result found.':
        raise RuntimeError('dirty events left after cleanup; not a clean start')
    nonce = 'gx:' + ''.join(random.SystemRandom().choice(CROCKFORD) for _ in range(6))
    begin_ms = (int(time.time()) // 60 + 120) * 60_000
    clock = dict(start_utc_ns=time.time_ns(), removed_before=removed)
    if x == 1:
        arm = cf.control('arm', dict(mode='drop', request_id=None))['arm_id']
        open_edit(phone, nonce, begin_ms)
        issued_mono = time.monotonic()
        clock['save_tap'] = cf.device_tap_save(phone.sh, dump=out / 'ui_no_done.xml')
        deadline = time.monotonic() + 90
        while not cf.control('status', {'arm_id': arm})['barrier']:
            if time.monotonic() > deadline:
                raise RuntimeError('no committed PUT within the barrier timeout')
            time.sleep(.1)
        clock['barrier_utc_ns'] = time.time_ns()
        fault = apply_fault(phone, cls)
        cf.control('release', dict(arm_id=arm, fault_receipt=fault))
    else:
        open_edit(phone, nonce, begin_ms)
        issued_mono = time.monotonic()
        if not edit_screen_up(phone):
            raise RuntimeError("Etar's edit screen is not up")
        fault = apply_fault(phone, cls)
    clock['fault_utc_ns'] = fault['utc_ns']
    time.sleep(2)   # the reply drop and the kill settle before the controller relaunches
    origin_mono, clock['origin_utc_ns'] = time.monotonic(), time.time_ns()
    observer = EtarObserver(phone, nonce, out)
    copies_at_origin = cf.server_copies(nonce)
    if (x == 1) != bool(copies_at_origin):
        raise RuntimeError('intended outcome %d but %d server copies at the origin' % (x, len(copies_at_origin)))
    result = dict(name=item['name'], split=item['split'], x=x, fault_class=cls, nonce=nonce)
    if store is None:
        views = [observer.read('hop1', v) for v in ('search', 'agenda')]
        result['views'] = views
    else:
        from recovery import Recovery
        context = dict(fault_class=cls, origin_kind='recovery', origin_verified=True, origin_mono_seconds=origin_mono,
                       g2_eligible=False, force_stopped=cls == 'force-stop', issued_mono_seconds=issued_mono,
                       dedup_horizon_seconds=86400, lookalike=False)
        decision = Recovery(store, observer).resolve(domain(), context)
        result.update(decision=decision['decision'], reason=decision['reason'], trace=decision['trace'],
                      views=[r['value'] for r in observer.reads])
        if decision['decision'] == 'RETRY':   # the agent recomposes the same event through the GUI
            open_edit(phone, nonce, begin_ms)
            result['redo_tap'] = cf.device_tap_save(phone.sh, dump=out / 'ui_no_done_redo.xml')
            end = time.monotonic() + 90
            while time.monotonic() < end and not cf.server_copies(nonce):
                time.sleep(1)
            time.sleep(5)
    time.sleep(1)
    result['server_copies_final'] = cf.server_copies(nonce)
    result['local_rows_final'] = local_rows(phone, nonce)
    backend = dict(server_copies_at_origin=copies_at_origin, server_copies_final=result['server_copies_final'],
                   local_rows_final=result['local_rows_final'], proxy_journal='proxy.jsonl')
    refs = dict(backend=write_json(out / 'backend.json', backend), fault=write_json(out / 'fault.json', fault),
                probes=write_json(out / 'probes.json', observer.reads), clock=write_json(out / 'clock.json', clock))
    result['evidence'] = refs
    write_json(out / 'RESULT.json', result)
    return result


def calibration_row(r):
    return dict(stratum=STRATUM, fault_class=r['fault_class'], X_backend=r['x'], split='calibration',
                effect_id=r['nonce'], domain=domain(), population='interrupted',
                evidence_kind='interrupted_measurement', origin_kind='recovery', origin_verified=True,
                terminal_fate='committed' if r['x'] else 'terminal_nonapply', probe_eligibility_verified=True,
                views=dict(hop1=r['views']), lag_upper_seconds=None, evidence=r['evidence'])


def collect(args):
    schedule = json.loads(args.schedule.read_text(encoding='utf-8'))
    args.out.mkdir(parents=True, exist_ok=True)
    phone = Phone(args.adb, args.serial)
    if phone.sh('whoami') != 'root':
        phone.adb('root', timeout=60)
        phone.adb('wait-for-device', timeout=120)
    phone.adb('reverse', 'tcp:%d' % cf.PROXY_PORT, 'tcp:%d' % cf.PROXY_PORT)
    if not cf.port_open(cf.RADICALE_PORT):
        cf.start_radicale(ROOT / 'runtime' / 'radicale.log')
    cf.make_calendar()
    store = None
    if args.store:
        sys.path.insert(0, str(ROOT / 'testbed'))
        from calibration import load_store
        store = load_store(args.store)
        if [s['domain'] for s in store['strata']] != [domain()]:   # a changed reader or policy is a new domain
            raise SystemExit('store domain does not match this reader/policy revision; recalibrate')
    faults = Faults(Journal(args.out / 'proxy.jsonl'), barrier_timeout=60)
    servers = [http_proxy('http://127.0.0.1:%d' % cf.RADICALE_PORT, 'caldav', faults, listen=('127.0.0.1', cf.PROXY_PORT)),
               control_server(faults, listen=('127.0.0.1', cf.CONTROL_PORT))]
    for server in servers:
        threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
    ctx = dict(phone=phone, out=args.out)
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
                line = '%s ok x=%d %s views=%s %s' % (item['name'], r['x'], r['fault_class'], r['views'],
                                                      r.get('decision', ''))
                if args.out.joinpath(item['name'], 'RESULT.json').exists():
                    with open(args.out / ('effects.jsonl' if store is None else 'decisions.jsonl'), 'a',
                              encoding='utf-8') as f:
                        f.write(json.dumps(calibration_row(r) if store is None else r) + '\n')
            except Exception as exc:   # a rig failure: INVALID, kept on disk, replaced at the end of the queue
                bad = args.out / item['name']
                bad.mkdir(exist_ok=True)
                (bad / 'INVALID.json').write_text(json.dumps(dict(error_type=type(exc).__name__, reason=str(exc))))
                bad.rename(args.out / (item['name'] + '-INVALID-%d' % time.time_ns()))
                replacements += 1
                if replacements > schedule.get('max_replacements', 60):
                    raise SystemExit('too many INVALID trials: rig failure')
                queue.append(item)
                line = '%s INVALID %s: %s' % (item['name'], type(exc).__name__, exc)
            with open(log, 'a', encoding='utf-8') as f:
                f.write(time.strftime('%H:%M:%S ') + line + '\n')
            print(line, flush=True)
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        cleanup(phone)


def make_schedule(args):
    if args.split == 'calibration':
        counts = {1: 133, 0: 30}
    else:
        counts = {1: 40, 0: 40}
    items = [dict(x=x, fault_class=c) for c in CLASSES for x, n in counts.items() for _ in range(n)]
    random.Random(args.seed).shuffle(items)
    prefix = 'c' if args.split == 'calibration' else 't'
    for i, item in enumerate(items):
        item.update(name='%s%04d' % (prefix, i), split=args.split)
    args.out.write_text(json.dumps(dict(split=args.split, seed=args.seed, counts={str(k): v for k, v in counts.items()},
                                        classes=list(CLASSES), max_replacements=60, trials=items), indent=1),
                        encoding='utf-8')
    print(args.out, len(items))


def report(args):
    rows = [json.loads(line) for line in (args.run / 'decisions.jsonl').read_text(encoding='utf-8').splitlines()]
    table = {}
    for r in rows:
        key = (r['fault_class'], r['x'])
        cell = table.setdefault(key, dict(n=0, RETRY=0, COMMITTED=0, ASK=0, PENDING=0, copies_final={}))
        cell['n'] += 1
        cell[r['decision']] = cell.get(r['decision'], 0) + 1
        k = str(len(r['server_copies_final']))
        cell['copies_final'][k] = cell['copies_final'].get(k, 0) + 1
    summary = dict(trials=len(rows), cells={'%s/X=%d' % k: v for k, v in sorted(table.items())},
                   retries_of_committed=sum(r['x'] == 1 and r['decision'] == 'RETRY' for r in rows),
                   committed=sum(r['x'] == 1 for r in rows),
                   declared_committed_when_absent=sum(r['x'] == 0 and r['decision'] == 'COMMITTED' for r in rows),
                   absent=sum(r['x'] == 0 for r in rows),
                   asks=sum(r['decision'] == 'ASK' for r in rows))
    (args.run / 'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('schedule')
    s.add_argument('--split', choices=['calibration', 'test'], required=True)
    s.add_argument('--seed', type=int, required=True)
    s.add_argument('--out', type=Path, required=True)
    c = sub.add_parser('collect')
    c.add_argument('--schedule', type=Path, required=True)
    c.add_argument('--out', type=Path, required=True)
    c.add_argument('--store', type=Path)
    c.add_argument('--adb', required=True)
    c.add_argument('--serial', default='emulator-5580')
    r = sub.add_parser('report')
    r.add_argument('--run', type=Path, required=True)
    a = p.parse_args()
    os.environ.setdefault('ANDROID_ADB_SERVER_PORT', '5038')
    dict(schedule=make_schedule, collect=collect, report=report)[a.cmd](a)


if __name__ == '__main__':
    main()
