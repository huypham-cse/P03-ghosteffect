"""TN1 rig watchdog (b-log 19/11): clears a proxy arm left behind by an INVALID trial.

caldav_planner.py arms the CalDAV proxy before the save tap. When DAVx5 makes no PUT within the barrier timeout the trial
is INVALID, but the arm stays unreleased (faultproxy has no disarm), so every later committed-effect trial fails at
arm time. This helper, run beside the collector, watches the proxy journal: when an ARM has had no MATCH for --stale
seconds, it sends one rig PUT (a dummy event, title gx-rig-clear) through the proxy so the arm reaches its barrier, then
releases it with observed_class=none and a rig note. The dummy event is removed by the next trial's cleanup. It never
touches a trial's own effect and does not change caldav_planner.py (whose hash is part of the frozen domain).
"""
import argparse
import json
import threading
import time
import urllib.request
import uuid
from pathlib import Path

PROXY, CONTROL = 'http://127.0.0.1:5233', 'http://127.0.0.1:19026'


def post(path, payload):
    req = urllib.request.Request(CONTROL + path, json.dumps(payload).encode(), {'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def rig_put():
    uid = 'gx-rig-clear-' + uuid.uuid4().hex
    body = ('BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//gx//rig//EN\r\nBEGIN:VEVENT\r\nUID:%s\r\n'
            'DTSTAMP:20260101T000000Z\r\nDTSTART:20260101T000000Z\r\nSUMMARY:gx-rig-clear\r\nEND:VEVENT\r\n'
            'END:VCALENDAR\r\n' % uid).encode()
    req = urllib.request.Request(PROXY + '/alice/cal/%s.ics' % uid, body, method='PUT',
                                 headers={'Content-Type': 'text/calendar', 'If-None-Match': '*',
                                          'Authorization': 'Basic YWxpY2U6YWxpY2VwYXNz'})
    try:
        urllib.request.urlopen(req, timeout=90).read()
    except Exception:
        pass   # the proxy drops the reply on purpose


def clear(arm_id, log):
    if not post('/status', dict(arm_id=arm_id))['barrier']:   # matched arms (trial failed after the barrier) need no PUT
        threading.Thread(target=rig_put, daemon=True).start()
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if post('/status', dict(arm_id=arm_id))['barrier']:
            post('/release', dict(arm_id=arm_id, fault_receipt=dict(
                observed_class='none', rig='tn1_arm_watchdog: stale arm from an INVALID trial, cleared by a rig PUT')))
            log.write(time.strftime('%H:%M:%S') + ' cleared stale arm %s\n' % arm_id)
            log.flush()
            return True
        time.sleep(.5)
    log.write(time.strftime('%H:%M:%S') + ' could not clear arm %s\n' % arm_id)
    log.flush()
    return False


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--stale', type=float, default=95)
    p.add_argument('--poll', type=float, default=2)
    a = p.parse_args()
    journal, done = a.run / 'proxy.jsonl', set()
    with open(a.run / 'arm_watchdog.log', 'a', encoding='utf-8') as log:
        while True:
            arms, matched, released = {}, set(), set()
            if journal.exists():
                for line in journal.read_text(encoding='utf-8').splitlines():
                    e = json.loads(line)
                    if e['event'] == 'ARM':
                        arms[e['arm_id']] = e['utc_ns']
                    elif e['event'] == 'MATCH':
                        matched.add(e['arm_id'])
                    elif e['event'] == 'FAULT_RECEIPT':
                        released.add(e['arm_id'])
            now = time.time_ns()
            for arm_id, t in arms.items():
                if arm_id not in released and arm_id not in done and (now - t) / 1e9 > a.stale:
                    done.add(arm_id)
                    try:
                        clear(arm_id, log)
                    except Exception as exc:
                        log.write(time.strftime('%H:%M:%S') + ' error %s for %s\n' % (exc, arm_id))
                        log.flush()
            time.sleep(a.poll)


if __name__ == '__main__':
    main()
