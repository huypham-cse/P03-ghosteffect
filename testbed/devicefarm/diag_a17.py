"""Rig diagnosis on the Pixel 9 Pro XL, Android 17 (b-log 24/11, after the four runs failed on the rig). Read-only use
of the existing helpers; nothing here changes element_planner.py. Writes every dump and command output under --out.

  python3 testbed/devicefarm/diag_a17.py --adb <adb> --serial <serial> --out <dir>   (Element already signed in)

K-9: what `cmd package resolve-activity` and `am start -W` return, and what is on screen after each launch method.
Element: from the room list, each step of element_planner.to_room's logic (first node's package, room_row, tap,
in_room and the ids it needs), the focused window, then the room list with the phone's server port removed and
restored (the red banner seen in the failed runs). No dump is taken on a screen that can show a password.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caldav_planner as cp   # noqa: E402
import element_planner as ep   # noqa: E402

K9 = 'com.fsck.k9'


def summary(root):
    nodes = list(root.iter('node')) if root is not None else []
    pkgs = sorted({n.get('package') for n in nodes})
    first = root.find('.//node').get('package') if root is not None and root.find('.//node') is not None else ''
    texts = [(ep.rid(n), (n.get('text') or n.get('content-desc') or '')[:60]) for n in nodes
             if (n.get('text') or n.get('content-desc')) and n.get('package') in (ep.ELEMENT, K9)]
    return dict(first_package=first, packages=pkgs, element_nodes=sum(n.get('package') == ep.ELEMENT for n in nodes),
                room_toolbar=[n.get('text') for n in ep.find(root, 'roomToolbarTitleView')],
                composer=len(ep.find(root, 'composerEditText')), room_row=ep.room_row(root)[0] is not None,
                in_room=ep.in_room(root), texts=texts[:40])


def root_prelude(phone, snap, out):
    """element_planner.collect's first steps on a non-root phone, one by one, with the real adb: whoami, `adb root`,
    wait-for-device, then a screen read, the trial's wake and network commands, and to_room. Run last: if `adb root`
    breaks the session, nothing after it in this run is trusted."""
    r = dict(whoami=phone.sh('whoami'))
    r['adb_root'] = phone.adb('root', timeout=60)
    r['wait'] = phone.adb('wait-for-device', timeout=120)
    time.sleep(3)
    r['whoami_after'] = phone.sh('whoami')
    raw = phone.sh('uiautomator dump /sdcard/gx_ui.xml; ls -l /sdcard/gx_ui.xml')
    r['dump_raw'] = raw[:300]
    r['after_root'] = snap('element_after_root')[1]
    r['wake'] = phone.sh('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
    r['network'] = phone.sh('svc wifi enable; svc data enable')
    r['after_network'] = snap('element_after_network')[1]
    try:
        ep.to_room(phone)
        r['to_room'] = 'ok'
    except RuntimeError as exc:
        r['to_room'] = str(exc)
    r['final'] = snap('element_after_root_to_room')[1]
    (out / 'diag_root.json').write_text(json.dumps(r, indent=1))
    print(json.dumps(dict(adb_root=r['adb_root'][:80], whoami_after=r['whoami_after'], to_room=r['to_room'],
                          read_after_root=r['after_root']['element_nodes'])))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--part', choices=['main', 'root'], default='main')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    phone = cp.Phone(a.adb, a.serial)
    report = dict(k9={}, element=[], banner={})

    def snap(name):
        xml, root = ep.tree(phone)
        (a.out / (name + '.xml')).write_text(xml, encoding='utf-8')
        s = summary(root)
        s['focus'] = phone.sh('dumpsys window | grep -E "mCurrentFocus|mFocusedApp"')
        return root, s

    if a.part == 'root':
        return root_prelude(phone, snap, a.out)

    # K-9 (installed by Device Farm as the app under test; first run only, no account, no password on screen)
    resolve = phone.sh('cmd package resolve-activity --brief -c android.intent.category.LAUNCHER ' + K9)
    report['k9']['resolve'] = resolve
    last = resolve.splitlines()[-1] if resolve else ''
    report['k9']['am_start'] = phone.sh('am start -W -n ' + last)
    time.sleep(5)
    report['k9']['after_am_start'] = snap('k9_after_am_start')[1]
    phone.sh('am force-stop ' + K9)
    phone.sh('monkey -p %s -c android.intent.category.LAUNCHER 1' % K9)
    time.sleep(5)
    report['k9']['after_monkey'] = snap('k9_after_monkey')[1]
    phone.sh('am force-stop ' + K9)

    # Element: element_planner.to_room's steps one by one, from wherever Element is after setup
    ep.launch(phone)
    time.sleep(4)
    for i in range(6):
        root, s = snap('element_step%d' % i)
        name, _ = ep.room_row(root)
        s['action'] = 'in room' if s['in_room'] else ('tap row' if name is not None else 'none')
        report['element'].append(s)
        if s['in_room']:
            break
        if name is not None:
            ep.tap(phone, name)
        time.sleep(2.5)
    try:
        ep.to_room(phone)
        report['to_room'] = 'ok'
    except RuntimeError as exc:
        report['to_room'] = str(exc)
    phone.sh('input keyevent KEYCODE_BACK')
    time.sleep(2)

    # The red banner: room list with the server port removed, then restored
    phone.adb('reverse', '--remove', 'tcp:18008')
    time.sleep(20)
    report['banner']['port_removed'] = snap('element_port_removed')[1]
    phone.adb('reverse', 'tcp:18008', 'tcp:8008')
    time.sleep(30)
    report['banner']['port_restored'] = snap('element_port_restored')[1]
    (a.out / 'diag.json').write_text(json.dumps(report, indent=1))
    print(json.dumps(dict(to_room=report.get('to_room'), k9_after_am_start=report['k9']['after_am_start']['first_package'],
                          steps=[s['action'] for s in report['element']])))


if __name__ == '__main__':
    main()
