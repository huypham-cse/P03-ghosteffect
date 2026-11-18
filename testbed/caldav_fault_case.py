"""DAVx5 + Etar + Radicale on the AVD under a lost PUT reply, then a fault (b-log 18/11, emulator only).

Setup as campaign 2 (C2-4): Etar 1.0.57 + DAVx5 4.5.21-ose + Radicale 3.9.0, DAVx5 account "alice" on
http://10.0.2.2:5233/alice/ (fault proxy, then Radicale on 127.0.0.1:5232), calendar alice/cal. One trial:
create an event in Etar whose title is a fresh nonce; DAVx5 PUTs it; Radicale commits and the proxy holds the
reply, the fault lands while DAVx5 still waits, then the reply is dropped. Faults: none, force-stop, kill -9 and
lmk (background, then real memory pressure until lmkd reaps it) on DAVx5; doze (screen off, unplugged and forced
deep idle, entered before the drop and kept for --doze-seconds).
Graded from Radicale's store (copies of the nonce) and the proxy journal (every PUT of the event's href, so
the retry lag after the fault). kill9 and lmk need root on the AVD.
Rented phones (AWS Device Farm, b-log 18/11): only the rootless faults run there (none, force-stop, doze, and
stop-app, which kills the app but keeps its scheduled jobs and alarms, so it stands in for kill -9); the phone
reaches Radicale through `adb reverse` at http://127.0.0.1:5233/alice/, and GX_PHYSICAL_SERIAL must name it.
Every trial samples the app's process every 10 s from the barrier on: procstate, frozen as seen by the activity
manager and by the cgroup, and the deep-idle state.
"""
import argparse
import json
import os
import random
import re
import subprocess
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from faultproxy import Journal, Faults, http_proxy, control_server
from k9_fault_case import CROCKFORD, lmk_kill
from k9_reset import port_open
from ui import ADB

ROOT = Path(__file__).resolve().parents[1]
DAVX5, ETAR = 'at.bitfire.davdroid', 'ws.xsoh.etar'
RADICALE_PORT, PROXY_PORT, CONTROL_PORT = 5232, 5233, 19026
STORE = ROOT / 'runtime' / 'radicale-store'


def start_radicale(log_path):
    """Radicale 3.9.0 from runtime/radicale-venv on loopback, no auth (synthetic user alice only)."""
    config = ROOT / 'runtime' / 'radicale.conf'
    config.write_text('[server]\nhosts = 127.0.0.1:%d\n[auth]\ntype = none\n[rights]\ntype = owner_only\n'
                      '[storage]\nfilesystem_folder = %s\n[logging]\nlevel = info\n'
                      % (RADICALE_PORT, STORE.as_posix()), encoding='utf-8')
    python = os.environ.get('GX_RADICALE_PYTHON') or ROOT / 'runtime' / 'radicale-venv' / 'Scripts' / 'python.exe'
    log = open(log_path, 'ab')
    process = subprocess.Popen([str(python), '-m', 'radicale', '--config', str(config)], stdout=log,
                               stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen('http://127.0.0.1:%d/.web/' % RADICALE_PORT, timeout=1)
            return process
        except OSError:
            time.sleep(.3)
    process.kill()
    raise RuntimeError('Radicale did not start')


def make_calendar():
    """MKCALENDAR alice/cal once; 405 means it already exists."""
    request = urllib.request.Request('http://127.0.0.1:%d/alice/cal/' % RADICALE_PORT, method='MKCALENDAR',
                                     headers={'Authorization': 'Basic YWxpY2U6YWxpY2VwYXNz'})
    try:
        return urllib.request.urlopen(request, timeout=5).status
    except urllib.error.HTTPError as exc:
        return exc.code


def server_copies(nonce):
    """Events in Radicale's store for alice/cal whose data carries the nonce."""
    folder = STORE / 'collection-root' / 'alice' / 'cal'
    return sorted(p.name for p in folder.glob('*.ics') if nonce in p.read_text(encoding='utf-8', errors='replace'))


def control(action, payload):
    request = urllib.request.Request('http://127.0.0.1:%d/%s' % (CONTROL_PORT, action), json.dumps(payload).encode(),
                                     {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def dirty_events(shell):
    return shell("content query --uri content://com.android.calendar/events --projection _id:title:dirty "
                 "--where 'dirty=1 AND deleted=0'")


def doze_enter(shell):
    """Screen off, unplugged and forced deep idle (AVD only); doze_exit() undoes all three."""
    shell('dumpsys battery unplug && input keyevent KEYCODE_SLEEP')
    time.sleep(2)
    state = shell('dumpsys deviceidle force-idle deep; dumpsys deviceidle get deep')
    return dict(observed_class='device-doze-deep', state=state.split()[-1] if state else '')


def doze_exit(shell):
    shell('dumpsys deviceidle unforce; dumpsys battery reset; input keyevent KEYCODE_WAKEUP')


def proc_sample(shell, package=DAVX5):
    """The app's process as the activity manager and the kernel see it (readable without root, pilot 18/11)."""
    pid = shell('pidof ' + package).split()
    sample = dict(utc_ns=time.time_ns(), pid=pid[0] if pid else None, deep=shell('dumpsys deviceidle get deep'))
    if pid:
        record = shell('dumpsys activity processes ' + package)
        events = shell('cat /sys/fs/cgroup/uid_*/pid_%s/cgroup.events' % pid[0])
        for key, pattern, cast in (('procstate', r'curProcState=(\d+)', int), ('am_frozen', r'isFrozen=(\w+)', str),
                                   ('cgroup_frozen', r'frozen (\d)', int)):
            match = re.search(pattern, events if key == 'cgroup_frozen' else record)
            sample[key] = cast(match.group(1)) if match else None
    return sample


class Sampler(threading.Thread):
    def __init__(self, shell, every=10):
        super().__init__(daemon=True)
        self.shell, self.every, self.samples, self.done = shell, every, [], threading.Event()

    def run(self):
        while not self.done.is_set():
            try:
                self.samples.append(proc_sample(self.shell))
            except Exception as exc:   # a failed sample is recorded, never fatal to the trial
                self.samples.append(dict(utc_ns=time.time_ns(), error=type(exc).__name__))
            self.done.wait(self.every)


def trial(args, shell, device, journal):
    receipt = dict(fault=args.fault, utc_ns=time.time_ns())
    deadline = time.monotonic() + 120
    while dirty_events(shell) != 'No result found.' and time.monotonic() < deadline:
        time.sleep(2)   # an earlier event still uploading would be the first PUT the proxy arms on
    receipt['dirty_before'] = dirty_events(shell)
    if receipt['dirty_before'] != 'No result found.':
        raise RuntimeError('calendar provider still has dirty events; not a clean start')
    nonce = 'gx:' + ''.join(random.SystemRandom().choice(CROCKFORD) for _ in range(6))
    arm = control('arm', dict(mode='drop', request_id=None))['arm_id']
    start = int(time.time() * 1000) + 86_400_000
    shell('am force-stop ' + ETAR)   # otherwise the intent goes to Etar's month view left on top by the last trial
    shell(f"am start -W -n {ETAR}/com.android.calendar.EditEventActivity -a android.intent.action.INSERT "
          f"-t vnd.android.cursor.item/event --es title '{nonce}' --el beginTime {start} --el endTime {start + 3_600_000}")
    time.sleep(3)
    receipt['save_tap'] = device_tap_save(shell)
    deadline, status = time.monotonic() + args.barrier_timeout, {}
    while time.monotonic() < deadline:
        status = control('status', {'arm_id': arm})
        if status['barrier']:
            break
        time.sleep(.1)
    else:
        raise RuntimeError('no committed PUT within the barrier timeout')
    # The proxy holds Radicale's reply here; the fault lands while DAVx5 still waits, then the reply is dropped.
    href, receipt['barrier_utc_ns'] = status['request_id'], time.time_ns()
    sampler = Sampler(shell)
    sampler.start()
    if args.fault == 'force-stop':
        receipt['fault_receipt'] = device.force_stop(DAVX5)
    elif args.fault in ('kill9', 'kill9-doze'):
        pids = device.pids(DAVX5)
        shell('kill -9 ' + pids)
        receipt['fault_receipt'] = dict(observed_class='app-sigkill', pids_before=pids.split())
        if args.fault == 'kill9-doze':   # the retry is then a rescheduled sync, which Doze can defer
            receipt['fault_receipt']['doze'] = doze_enter(shell)
    elif args.fault in ('stop-app', 'stop-app-doze'):   # rootless kill that keeps scheduled jobs and alarms
        pids = device.pids(DAVX5)
        shell('am stop-app ' + DAVX5)
        receipt['fault_receipt'] = dict(observed_class='app-stop-keep-jobs', pids_before=pids.split(),
                                        pids_after=shell('pidof ' + DAVX5).split())
        if args.fault == 'stop-app-doze':
            receipt['fault_receipt']['doze'] = doze_enter(shell)
    elif args.fault == 'lmk':
        receipt['fault_receipt'] = lmk_kill(shell, device, DAVX5)
    elif args.fault == 'doze':
        receipt['fault_receipt'] = doze_enter(shell)
    else:
        receipt['fault_receipt'] = dict(observed_class='none')
    receipt['fault_utc_ns'] = time.time_ns()
    control('release', dict(arm_id=arm, fault_receipt=receipt['fault_receipt']))
    if args.fault in ('doze', 'kill9-doze', 'stop-app-doze'):
        try:
            time.sleep(args.doze_seconds)
        finally:
            doze_exit(shell)
            receipt['doze_exit_utc_ns'] = time.time_ns()
    time.sleep(args.window)
    sampler.done.set()
    receipt['proc_samples'] = sampler.samples
    events = [json.loads(line) for line in journal.read_text(encoding='utf-8').splitlines()]
    puts = [e['utc_ns'] for e in events if e['event'] == 'REQUEST' and e.get('request_id') == href]
    after = [t for t in puts if t > receipt['fault_utc_ns']]
    receipt.update(nonce=nonce, href=href, puts=len(puts), server_copies=server_copies(nonce),
                   first_put_after_fault_s=(after[0] - receipt['fault_utc_ns']) / 1e9 if after else None,
                   dirty_after=dirty_events(shell))
    if 'doze_exit_utc_ns' in receipt and after:
        receipt['first_put_after_doze_exit_s'] = (after[0] - receipt['doze_exit_utc_ns']) / 1e9
    receipt['verdict'] = 'EXACTLY_ONCE' if len(receipt['server_copies']) == 1 else \
        'DUPLICATE' if len(receipt['server_copies']) > 1 else 'LOST'
    return receipt


def device_tap_save(shell, timeout=20):
    """Tap Etar's DONE (resource id action_done, recorded on the AVD 18/11); returns where it tapped."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        xml = shell('uiautomator dump /sdcard/gx_ui.xml >/dev/null && cat /sdcard/gx_ui.xml; rm -f /sdcard/gx_ui.xml')
        for node in ET.fromstring(xml[xml.index('<'):]).iter('node'):
            if node.get('package') == ETAR and (node.get('resource-id') or '').endswith('/action_done'):
                x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
                shell('input tap %d %d' % ((x1 + x2) // 2, (y1 + y2) // 2))
                return dict(at=[(x1 + x2) // 2, (y1 + y2) // 2], utc_ns=time.time_ns())
        time.sleep(.5)
    raise RuntimeError("Etar's DONE button not found")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', required=True)
    parser.add_argument('--adb-server-port', default='5038')
    parser.add_argument('--serial', default='emulator-5580')
    parser.add_argument('--fault', choices=['none', 'force-stop', 'kill9', 'lmk', 'doze', 'kill9-doze', 'stop-app',
                                            'stop-app-doze'], required=True)
    parser.add_argument('--doze-seconds', type=float, default=600)
    parser.add_argument('--window', type=float, default=180, help='seconds after the fault (or Doze exit) before grading')
    parser.add_argument('--barrier-timeout', type=float, default=90)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    phone = not args.serial.startswith('emulator-')
    if phone and args.serial != os.environ.get('GX_PHYSICAL_SERIAL'):
        raise SystemExit('a phone needs GX_PHYSICAL_SERIAL set to its serial (rented phones only, b-log 18/11)')
    if phone and args.fault in ('kill9', 'kill9-doze', 'lmk'):
        raise SystemExit('kill -9 of another app and the lmk tmpfs need root: AVD only')
    args.output.mkdir(parents=True, exist_ok=False)
    os.environ['ANDROID_ADB_SERVER_PORT'] = args.adb_server_port
    adb = [str(Path(args.adb).resolve()), '-P', args.adb_server_port, '-s', args.serial]
    shell = lambda c: subprocess.run(adb + ['shell', c], capture_output=True, text=True, encoding='utf-8',
                                     errors='replace', timeout=120).stdout.strip()
    if not phone and shell('whoami') != 'root':   # kill -9 of another app and the tmpfs for lmk need root on the AVD
        subprocess.run(adb + ['root'], capture_output=True, timeout=60)
        subprocess.run(adb + ['wait-for-device'], capture_output=True, timeout=120)
    if not port_open(RADICALE_PORT):   # one Radicale (and store) serves the DAVx5 setup and every trial
        start_radicale(ROOT / 'runtime' / 'radicale.log')
    make_calendar()
    journal = args.output / 'proxy.jsonl'
    faults = Faults(Journal(journal), barrier_timeout=60)
    servers = [http_proxy('http://127.0.0.1:%d' % RADICALE_PORT, 'caldav', faults, listen=('127.0.0.1', PROXY_PORT)),
               control_server(faults, listen=('127.0.0.1', CONTROL_PORT))]
    for server in servers:
        threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
    try:
        result = trial(args, shell, ADB(Path(args.adb).resolve(), args.serial), journal)
    except Exception as exc:
        result = dict(verdict='INVALID', fault=args.fault, error_type=type(exc).__name__, reason=str(exc))
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
