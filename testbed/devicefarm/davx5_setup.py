"""Set up DAVx5 on a freshly wiped rented phone (b-log 18/11).

One CalDAV account for the synthetic user alice on Radicale, reached at the phone's 127.0.0.1:5233 through
`adb reverse`, with collection alice/cal synced. Screens and labels were recorded on the AVD on 18/11: the VIEW
intent opens DAVx5's "Login with URL and user name" with the base URL filled, then User name, Password, Login,
the account-name screen (Finish), and the account screen with the collection switch and "Synchronize now".
Taps go by label, never by coordinate, and only nodes of the DAVx5 package are considered.
"""
import re
import time
import xml.etree.ElementTree as ET

DAVX5 = 'at.bitfire.davdroid'


def screen(shell):
    xml = shell('uiautomator dump /sdcard/gx_ui.xml >/dev/null && cat /sdcard/gx_ui.xml; rm -f /sdcard/gx_ui.xml')
    return ET.fromstring(xml[xml.index('<'):]) if '<' in xml else None


def find(root, key, package=DAVX5):
    """Centre of the first node of `package` whose text, content-desc or resource-id suffix is `key`."""
    for node in root.iter('node') if root is not None else ():
        if node.get('package') != package:
            continue
        rid = node.get('resource-id') or ''
        if key in (node.get('text'), node.get('content-desc')) or rid.endswith('/' + key):
            x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
            return (x1 + x2) // 2, (y1 + y2) // 2
    return None


def tap(shell, key, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        hit = find(screen(shell), key)
        if hit:
            shell('input tap %d %d' % hit)
            return hit
        time.sleep(1)
    raise RuntimeError('DAVx5 setup: %r not on screen' % key)


def hide_ime(shell):
    if 'mInputShown=true' in shell('dumpsys input_method | grep mInputShown'):
        shell('input keyevent KEYCODE_BACK')
        time.sleep(1)


def calendars(shell, user):
    rows = shell('content query --uri content://com.android.calendar/calendars --projection _id:account_name:sync_events')
    return [r for r in rows.splitlines() if 'account_name=%s,' % user in r and 'sync_events=1' in r]


def setup(shell, url='http://127.0.0.1:5233/alice/', user='alice', password='alicepass'):
    for permission in ('READ_CALENDAR', 'WRITE_CALENDAR', 'POST_NOTIFICATIONS'):
        shell('pm grant %s android.permission.%s' % (DAVX5, permission))
    shell("am start -W -a android.intent.action.VIEW -d '%s' -n %s/.ui.setup.LoginActivity" % (url, DAVX5))
    tap(shell, 'User name')
    shell('input text ' + user)
    hide_ime(shell)
    tap(shell, 'Password')
    shell('input text ' + password)
    hide_ime(shell)
    tap(shell, 'Login')
    tap(shell, 'Finish', timeout=60)          # account name defaults to the user name
    try:
        tap(shell, 'synchronize this collection', timeout=30)
    except RuntimeError:                      # the collection list can load late: refresh once
        tap(shell, 'Refresh list')
        tap(shell, 'synchronize this collection', timeout=60)
    tap(shell, 'Synchronize now')
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if calendars(shell, user):
            return dict(calendar=calendars(shell, user)[0], utc_ns=time.time_ns())
        time.sleep(2)
    raise RuntimeError('DAVx5 calendar for %s did not appear with sync on' % user)


if __name__ == '__main__':   # python davx5_setup.py <adb> <serial> [url [user]]
    import json
    import subprocess
    import sys
    adb = [sys.argv[1], '-s', sys.argv[2]]
    run = lambda c: subprocess.run(adb + ['shell', c], capture_output=True, text=True, encoding='utf-8',
                                   errors='replace', timeout=120).stdout.strip()
    print(json.dumps(setup(run, *sys.argv[3:5])))
