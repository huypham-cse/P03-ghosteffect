"""Scripted K-9 lost-reply case (B-04). No LLM: this checks the fault, not an agent.

Reset (k9_reset.py), open K-9's compose screen through an intent with a fresh
nonce as the subject, then run_case.py (--fault none): tap Send, GreenMail
accepts the DATA, the proxy drops the SMTP reply. Once K-9 has recorded the
error, force-stop K-9 and relaunch it (campaign 2 order). After
--observe seconds, grade from the server (bob's Inbox copies, alice's Sent)
and read K-9's own store (root). Expected: one server copy, K-9 keeps the mail
in its Outbox with an error, and with config sent the Sent folder stays empty.
Runs its own SMTP fault proxy (listen 14025, control 19025) with the journal in
the output, so a failed trial never leaves an armed proxy behind; do not run
another proxy on those ports at the same time. A failed trial still writes
RESULT.json with verdict INVALID.

On a physical phone (b-log 18/11) there is no root, so K-9's store is not read:
taps are found by label, the error before the fault is K-9's own notification,
and the Outbox after relaunch is read from K-9's message list on screen.
"""
import argparse
import json
import os
import random
import re
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from argparse import Namespace
from pathlib import Path

import k9_reset
import run_case
from faultproxy import Journal, Faults, smtp_proxy, control_server
from grader import imap_count

# Tap targets on the 1080x2400 test AVD.
SEND = (911, 211)                # compose toolbar Send
SEND_AND_DELETE = (733, 1423)    # "Sent folder not found" dialog, config nosent only
CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'


ACTIONS = ('none', 'sync', 'send_messages', 'recompose')
# K-9's notification after the dropped reply on the phone (dev trial t01, 18/11). After force-stop and relaunch
# K-9 shows no error mark in the Outbox list or message view, so the phone checks that it did not resend instead.
PHONE_ERROR = 'Failed to send some messages'


def background_kill(shell, device):
    """Kill as the low-memory killer does: K-9 goes to the background (HOME), then `am kill`, which only kills
    background processes and, unlike force-stop, does not cancel K-9's scheduled work (H3, §7.9)."""
    before = device.pids(k9_reset.PACKAGE)
    if not before:
        raise RuntimeError('target has no live PID before fault; not an app-death trial')
    shell('input keyevent KEYCODE_HOME')
    time.sleep(2)
    shell('am kill ' + k9_reset.PACKAGE)
    deadline = time.monotonic() + 10
    while device.pids(k9_reset.PACKAGE) and time.monotonic() < deadline:
        time.sleep(.5)
    after = device.pids(k9_reset.PACKAGE)
    if after:
        raise RuntimeError('am kill left K-9 running')
    return dict(observed_class='app-background-kill', package=k9_reset.PACKAGE, pids_before=before.split(), pids_after=[])


def lmk_kill(shell, device, package=k9_reset.PACKAGE, max_mb=3600):
    """AVD only (root): put the app in the background, then fill a tmpfs 64 MB at a time until the
    low-memory killer reaps it, and free the memory again. Returns lmkd's own log lines for the app."""
    before = device.pids(package)
    if not before:
        raise RuntimeError('target has no live PID before fault; not an app-death trial')
    shell('input keyevent KEYCODE_HOME')
    time.sleep(2)
    mem = '/data/local/tmp/gx_mem'
    shell(f'mkdir -p {mem} && mount -t tmpfs -o size={max_mb}m tmpfs {mem}')
    filled = 0
    try:
        while device.pids(package) and filled < max_mb:
            shell(f'dd if=/dev/zero of={mem}/f{filled} bs=1048576 count=64 2>/dev/null')
            filled += 64
    finally:
        shell(f'rm -f {mem}/*; umount {mem}')
    after = device.pids(package)
    lmkd = [line for line in shell('logcat -d -s lowmemorykiller:I').splitlines() if package in line]
    if after or not lmkd:
        raise RuntimeError('memory pressure did not reap %s through lmkd (%d MB filled)' % (package, filled))
    return dict(observed_class='app-lmkd-kill', package=package, pids_before=before.split(), pids_after=[],
                filled_mb=filled, lmkd_line=lmkd[-1])


k9_notices = k9_reset.k9_notices


def k9_texts(xml):
    """Visible texts of K-9's own nodes in one UI dump."""
    root = ET.fromstring(xml[xml.index('<'):])
    return [n.get('text') for n in root.iter('node') if n.get('package') == k9_reset.PACKAGE and n.get('text')]


def outbox_on_screen(shell, nonce):
    """Open K-9's Outbox from the message list (unless it is already open) and count items carrying the nonce."""
    dump = lambda: k9_texts(shell('uiautomator dump /sdcard/gx_ui.xml >/dev/null && cat /sdcard/gx_ui.xml; '
                                  'rm -f /sdcard/gx_ui.xml'))
    texts = dump()
    if texts[:1] != ['Outbox']:   # the first K-9 text is the toolbar title
        for key in ('Navigate up', 'Outbox'):
            shell('input tap %d %d' % k9_reset.locate(shell, key))
            time.sleep(2)
        texts = dump()
    return dict(nonce_items=sum(nonce in t for t in texts), texts=texts, utc_ns=time.time_ns())


def tap_text(shell, *labels):
    """Tap the first node whose text or content-desc equals one of the labels; return the UI receipt."""
    shell('uiautomator dump /sdcard/gx_ui.xml')
    xml = shell('cat /sdcard/gx_ui.xml')
    root = ET.fromstring(xml[xml.index('<'):])
    for label in labels:
        for node in root.iter('node'):
            if label in (node.get('text'), node.get('content-desc')):
                x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
                shell('input tap %d %d' % ((x1 + x2) // 2, (y1 + y2) // 2))
                time.sleep(2)
                return dict(label=label, bounds=[x1, y1, x2, y2], utc_ns=time.time_ns())
    raise RuntimeError('UI element not found: ' + ' / '.join(labels))


def audit(args, shell, nonce, read_outbox):
    """B-12: after the lost reply, do one action, wait, and count what reached the server (R19)."""
    from agent_episode import backend_copies
    start = time.time_ns()
    taps = []
    if args.action == 'sync':
        taps += [tap_text(shell, 'Navigate up'), tap_text(shell, 'Sync account')]
    elif args.action == 'send_messages':
        taps += [tap_text(shell, 'Navigate up'), tap_text(shell, 'Outbox'), tap_text(shell, 'More options'),
                 tap_text(shell, 'Send messages')]
    elif args.action == 'recompose':
        shell(f"am start -W -a android.intent.action.SENDTO -d 'mailto:bob@test.invalid?subject={nonce}' "
              f"--es android.intent.extra.TEXT 'synthetic test message' -n {k9_reset.PACKAGE}/.activity.MessageCompose")
        time.sleep(3)
        taps.append(tap_text(shell, 'Send'))
        if args.config == 'nosent':
            taps.append(tap_text(shell, 'Send and Delete'))
    time.sleep(args.action_window)
    events = [json.loads(line) for line in args.journal.read_text(encoding='utf-8').splitlines()]
    copies, ids = backend_copies(nonce)
    return dict(action=args.action, taps=taps, action_start_utc_ns=start, window_s=args.action_window,
                smtp_data_after_action=sum(1 for e in events if e['event'] == 'SMTP_DATA' and e['utc_ns'] >= start),
                server_copies_after_action=copies, distinct_message_ids_after_action=len(ids),
                k9_outbox_after_action=read_outbox())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', choices=['nosent', 'sent'], required=True)
    parser.add_argument('--adb', required=True)
    parser.add_argument('--adb-server-port', default='5038')
    parser.add_argument('--serial', default='emulator-5580')
    parser.add_argument('--java', default='java')
    parser.add_argument('--observe', type=float, default=60, help='seconds after relaunch before grading')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--action', choices=ACTIONS, help='B-12 audit: one user action after the fault')
    parser.add_argument('--action-window', type=float, default=60, help='seconds after the action before grading')
    parser.add_argument('--kill', choices=['force-stop', 'background', 'lmk'], default='force-stop',
                        help='how K-9 dies after its error: force-stop (campaign 2), HOME then am kill, '
                             'or HOME then real memory pressure until lmkd reaps it (AVD only)')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    args.control, args.journal = 'http://127.0.0.1:19025', args.output / 'proxy.jsonl'
    faults = Faults(Journal(args.journal), barrier_timeout=60)
    servers = [smtp_proxy(('127.0.0.1', k9_reset.SMTP_PORT), faults, listen=('127.0.0.1', 14025)),
               control_server(faults, listen=('127.0.0.1', 19025))]
    for server in servers:
        threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
    try:
        trial(args)
    except Exception as exc:
        (args.output / 'RESULT.json').write_text(json.dumps(dict(
            verdict='INVALID', config=args.config, kill=args.kill, action=args.action, error_type=type(exc).__name__,
            reason=str(exc), utc_ns=time.time_ns()), indent=2))
        raise
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()


def trial(args):
    os.environ['ANDROID_ADB_SERVER_PORT'] = args.adb_server_port   # ui.ADB reads the server port from env
    adb = [str(Path(args.adb).resolve()), '-P', args.adb_server_port, '-s', args.serial]

    def shell(command):
        return subprocess.run(adb + ['shell', command], capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=60).stdout.strip()

    phone = not args.serial.startswith('emulator-')
    reset = k9_reset.reset(args.adb, args.serial, args.config, args.output, args.adb_server_port, args.java)
    (args.output / 'RESET.json').write_text(json.dumps(reset, indent=2))
    if reset['verdict'] != 'PASS':
        raise RuntimeError('reset failed: ' + json.dumps(reset['checks']))
    nonce = 'gx:' + ''.join(random.SystemRandom().choice(CROCKFORD) for _ in range(6))
    shell(f"am start -W -a android.intent.action.SENDTO -d 'mailto:bob@test.invalid?subject={nonce}' "
          f"--es android.intent.extra.TEXT 'synthetic test message' -n {k9_reset.PACKAGE}/.activity.MessageCompose")
    time.sleep(3)
    send = k9_reset.locate(shell, 'Send') if phone else SEND
    if args.config == 'nosent':
        shell('input tap %d %d' % send)   # opens the dialog; nothing is sent before "Send and Delete"
        time.sleep(2)
    commit_tap = send if args.config == 'sent' else k9_reset.locate(shell, 'Send and Delete') if phone \
        else SEND_AND_DELETE
    if phone:   # no root: K-9's error notification before the fault, its Outbox list on screen after
        state = lambda: k9_notices(shell('dumpsys notification --noredact'))
        is_error = lambda notices: any(PHONE_ERROR in n for n in notices)
        read_outbox = lambda: outbox_on_screen(shell, nonce)
    else:
        db = f'$(ls {k9_reset.DATA}/databases/*.db | grep -v preferences)'
        outbox = f'sqlite3 {db} "select send_state, number_of_send_attempts, error from outbox_state"'
        state = read_outbox = lambda: shell(outbox)
        is_error = lambda row: row.startswith('error|')
    # Campaign 2 order: the reply is dropped first and K-9 records the error, then the app dies.
    # (run_case's own --fault force-stop kills K-9 while the reply is still held; K-9 then keeps
    # the mail queued as "ready", not "error", a different state; b-log 10/11.)
    case = run_case.run(Namespace(
        adb=Path(args.adb).resolve(), serial=args.serial, package=k9_reset.PACKAGE, component=k9_reset.LAUNCH,
        control=args.control, mode='drop', fault='none', request_id=None,
        tap=list(commit_tap), barrier_timeout=45,
        output=args.output / 'case', profile=None, fixture_text=None, nonce=None,
        observation_seconds=300, pre_fault_delay=0))
    deadline = time.monotonic() + 30
    while not is_error(state()) and time.monotonic() < deadline:
        time.sleep(.5)
    pre_fault = state()
    device = run_case.ADB(Path(args.adb).resolve(), args.serial)
    fault_utc_ns = time.time_ns()
    if args.kill == 'lmk' and phone:
        raise ValueError('--kill lmk fills the device memory; AVD only')
    fault = background_kill(shell, device) if args.kill == 'background' else lmk_kill(shell, device) \
        if args.kill == 'lmk' else device.force_stop(k9_reset.PACKAGE)
    recovery = device.launch(k9_reset.LAUNCH)
    time.sleep(args.observe)
    server = imap_count('127.0.0.1', k9_reset.IMAP_PORT, 'INBOX', nonce, 'bob', 'bobpass')
    sent = imap_count('127.0.0.1', k9_reset.IMAP_PORT, 'Sent', nonce, 'alice', 'alicepass') \
        if args.config == 'sent' else None
    events = [json.loads(line) for line in args.journal.read_text(encoding='utf-8').splitlines()]
    data_after_fault = sum(1 for e in events if e['event'] == 'SMTP_DATA' and e['utc_ns'] >= fault_utc_ns)
    if phone:
        k9_notices_after = state()
        k9_outbox = read_outbox()
        kept, marked = k9_outbox['nonce_items'] == 1, data_after_fault == 0
        stored = dict(k9_outbox_screen=k9_outbox, k9_notices_after=k9_notices_after, k9_evidence='notification+screen')
    else:
        k9_folders = shell(f'sqlite3 {db} "select f.name from messages m join folders f on f.id=m.folder_id '
                           f"where m.subject='{nonce}' and m.deleted=0\"").split()
        k9_outbox = shell(outbox)
        kept, marked = k9_folders == ['Outbox'], k9_outbox.startswith('error|')
        stored = dict(k9_folders=k9_folders, reset_archive_sha256=reset['archive_sha256'])
    checks = dict(reply_dropped_after_commit=case.get('status') == 'CAPTURED_NOT_GRADED',
                  error_before_fault=is_error(pre_fault),
                  app_killed_and_relaunched=recovery['foreground'].startswith(k9_reset.PACKAGE + '/'),
                  one_server_copy=server['copies'] == 1,
                  k9_kept_in_outbox=kept,
                  sent_folder_empty=sent is None or sent['copies'] == 0)
    checks['no_resend_after_relaunch' if phone else 'k9_marked_error'] = marked
    result = dict(verdict='REPRODUCED' if all(checks.values()) else 'NOT_REPRODUCED', config=args.config, kill=args.kill,
                  nonce=nonce, checks=checks, server=server, sent=sent,
                  k9_outbox_state=k9_outbox, k9_outbox_before_fault=pre_fault, fault=fault,
                  observe_s=args.observe, request_id=case.get('request_id'), smtp_data_after_fault=data_after_fault,
                  device=reset.get('device', 'avd'), utc_ns=time.time_ns(), **stored)
    if args.action:
        result['audit'] = audit(args, shell, nonce, read_outbox)
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['verdict'] == 'REPRODUCED' else 1)


if __name__ == '__main__':
    main()
