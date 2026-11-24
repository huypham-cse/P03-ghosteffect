"""Sign Element 1.6.62 in as alice on a freshly wiped rented phone (b-log 24/11), for element_planner.py.

The homeserver is the test host's Synapse, reached at the phone's http://127.0.0.1:18008 through `adb reverse` (during
setup straight to Synapse; during trials element_planner.py puts its fault proxy on that port). Screens recorded on
the AVD on 24/11: splash SIGN IN, "Welcome back!" with EDIT next to the server, "Select your server" (clear the field,
type the URL, NEXT), user name and password, NEXT, "Help improve Element Classic" (NOT NOW), then the room list. The
first sync after sign-in may not draw the room list; Element is then restarted once. Taps go by resource id, label or
widget class of Element's own nodes, never by coordinate. The password is typed, never printed or logged.
"""
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ELEMENT = 'im.vector.app'
ROOM = 'gx test'


def screen(shell):
    xml = shell('uiautomator dump /sdcard/gx_ui.xml >/dev/null && cat /sdcard/gx_ui.xml; rm -f /sdcard/gx_ui.xml')
    return ET.fromstring(xml[xml.index('<'):]) if '<' in xml else None


def find(root, key=None, cls=None):
    """Centre of the first Element node whose resource-id suffix, text or content-desc is `key` (or whose class is
    `cls`)."""
    for node in root.iter('node') if root is not None else ():
        if node.get('package') != ELEMENT:
            continue
        rid = (node.get('resource-id') or '').split('/')[-1]
        if (key and key in (rid, node.get('text'), node.get('content-desc'))) or (cls and node.get('class') == cls):
            x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
            return (x1 + x2) // 2, (y1 + y2) // 2
    return None


def hide_ime(shell):
    if 'mInputShown=true' in shell('dumpsys input_method | grep mInputShown'):
        shell('input keyevent KEYCODE_BACK')
        time.sleep(1)


def wait_for(shell, key=None, cls=None, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        hit = find(screen(shell), key, cls)
        if hit:
            return hit
        time.sleep(1.5)
    return None


def tap(shell, key=None, cls=None, timeout=60):
    hit = wait_for(shell, key, cls, timeout)
    if not hit:
        raise RuntimeError('Element setup: %r not on screen' % (key or cls))
    shell('input tap %d %d' % hit)
    time.sleep(1.5)
    return hit


def launch(shell):
    shell('monkey -p %s -c android.intent.category.LAUNCHER 1' % ELEMENT)
    time.sleep(4)


def room_listed(shell, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root = screen(shell)
        if root is not None and any(n.get('package') == ELEMENT and (n.get('text') or '') == ROOM
                                    and (n.get('resource-id') or '').endswith('/roomNameView') for n in root.iter('node')):
            return True
        time.sleep(2)
    return False


def setup(shell, user, password, url='http://127.0.0.1:18008'):
    shell('pm grant %s android.permission.POST_NOTIFICATIONS' % ELEMENT)
    launch(shell)
    tap(shell, 'loginSplashAlreadyHaveAccount')          # SIGN IN
    tap(shell, 'editServerButton')                       # EDIT next to matrix.org
    tap(shell, 'Clear text')
    tap(shell, cls='android.widget.EditText')
    shell('input text ' + url)
    hide_ime(shell)
    tap(shell, 'chooseServerSubmit')                     # NEXT
    tap(shell, 'loginEditText')
    shell('input text ' + user)
    hide_ime(shell)
    tap(shell, 'loginPasswordEditText')
    shell('input text ' + password)
    hide_ime(shell)
    tap(shell, 'loginSubmit')                            # NEXT
    if wait_for(shell, 'later', timeout=60):             # "Help improve Element Classic": NOT NOW
        tap(shell, 'later')
    listed = room_listed(shell, 45)
    restarted = False
    if not listed:                                       # first sync did not draw the list (AVD 24/11): restart once
        shell('am force-stop ' + ELEMENT)
        launch(shell)
        restarted = True
        listed = room_listed(shell, 90)
    if not listed:
        raise RuntimeError('Element setup: room %r not listed after sign-in' % ROOM)
    return dict(room_listed=True, restarted=restarted, utc_ns=time.time_ns())


if __name__ == '__main__':   # python3 element_setup.py <adb> <serial> <accounts.json>
    adb = [sys.argv[1], '-s', sys.argv[2]]
    alice = json.loads(open(sys.argv[3], encoding='utf-8').read())['alice']
    run = lambda c: subprocess.run(adb + ['shell', c], capture_output=True, text=True, encoding='utf-8',
                                   errors='replace', timeout=120).stdout.strip()
    print(json.dumps(setup(run, alice['user'], alice['password'])))
