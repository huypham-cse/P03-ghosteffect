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


def audit(args, shell, nonce, outbox):
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
                k9_outbox_after_action=shell(outbox))


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
            verdict='INVALID', config=args.config, action=args.action, error_type=type(exc).__name__,
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
        return subprocess.run(adb + ['shell', command], capture_output=True, text=True, timeout=60).stdout.strip()

    reset = k9_reset.reset(args.adb, args.serial, args.config, args.output, args.adb_server_port, args.java)
    if reset['verdict'] != 'PASS':
        raise RuntimeError('reset failed: ' + json.dumps(reset['checks']))
    nonce = 'gx:' + ''.join(random.SystemRandom().choice(CROCKFORD) for _ in range(6))
    shell(f"am start -W -a android.intent.action.SENDTO -d 'mailto:bob@test.invalid?subject={nonce}' "
          f"--es android.intent.extra.TEXT 'synthetic test message' -n {k9_reset.PACKAGE}/.activity.MessageCompose")
    time.sleep(3)
    if args.config == 'nosent':
        shell('input tap %d %d' % SEND)   # opens the dialog; nothing is sent before "Send and Delete"
        time.sleep(2)
    db = f'$(ls {k9_reset.DATA}/databases/*.db | grep -v preferences)'
    outbox = f'sqlite3 {db} "select send_state, number_of_send_attempts, error from outbox_state"'
    # Campaign 2 order: the reply is dropped first and K-9 records the error, then the app dies.
    # (run_case's own --fault force-stop kills K-9 while the reply is still held; K-9 then keeps
    # the mail queued as "ready", not "error", a different state; b-log 10/11.)
    case = run_case.run(Namespace(
        adb=Path(args.adb).resolve(), serial=args.serial, package=k9_reset.PACKAGE, component=k9_reset.LAUNCH,
        control=args.control, mode='drop', fault='none', request_id=None,
        tap=list(SEND_AND_DELETE if args.config == 'nosent' else SEND), barrier_timeout=45,
        output=args.output / 'case', profile=None, fixture_text=None, nonce=None,
        observation_seconds=300, pre_fault_delay=0))
    deadline = time.monotonic() + 30
    while not shell(outbox).startswith('error|') and time.monotonic() < deadline:
        time.sleep(.5)
    pre_fault = shell(outbox)
    device = run_case.ADB(Path(args.adb).resolve(), args.serial)
    fault = device.force_stop(k9_reset.PACKAGE)
    recovery = device.launch(k9_reset.LAUNCH)
    time.sleep(args.observe)
    server = imap_count('127.0.0.1', k9_reset.IMAP_PORT, 'INBOX', nonce, 'bob', 'bobpass')
    sent = imap_count('127.0.0.1', k9_reset.IMAP_PORT, 'Sent', nonce, 'alice', 'alicepass') \
        if args.config == 'sent' else None
    k9_folders = shell(f'sqlite3 {db} "select f.name from messages m join folders f on f.id=m.folder_id '
                       f"where m.subject='{nonce}' and m.deleted=0\"").split()
    k9_outbox = shell(outbox)
    checks = dict(reply_dropped_after_commit=case.get('status') == 'CAPTURED_NOT_GRADED',
                  error_before_fault=pre_fault.startswith('error|'),
                  app_killed_and_relaunched=recovery['foreground'].startswith(k9_reset.PACKAGE + '/'),
                  one_server_copy=server['copies'] == 1,
                  k9_kept_in_outbox=k9_folders == ['Outbox'],
                  k9_marked_error=k9_outbox.startswith('error|'),
                  sent_folder_empty=sent is None or sent['copies'] == 0)
    result = dict(verdict='REPRODUCED' if all(checks.values()) else 'NOT_REPRODUCED', config=args.config,
                  nonce=nonce, checks=checks, server=server, sent=sent, k9_folders=k9_folders,
                  k9_outbox_state=k9_outbox, k9_outbox_before_fault=pre_fault, fault=fault,
                  observe_s=args.observe, request_id=case.get('request_id'),
                  reset_archive_sha256=reset['archive_sha256'], utc_ns=time.time_ns())
    if args.action:
        result['audit'] = audit(args, shell, nonce, outbox)
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['verdict'] == 'REPRODUCED' else 1)


if __name__ == '__main__':
    main()
