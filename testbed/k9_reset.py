"""Reset K-9 Mail + GreenMail to the clean start state of one config (B-03).

Restores K-9's data directory from a saved clean copy on the device
(/data/local/tmp/ghosteffect/k9-<config>.tar, made once as in RUNBOOK_B.md
section 6b) and relabels it for SELinux; restarts the pinned GreenMail (its
store is in memory, so it starts empty, as in campaign 2) with the two
synthetic test accounts and, for config sent, creates the sender's Sent
folder; relaunches K-9 and checks the result.

Needs a root-capable AVD (google_apis image); adbd is left running as root.
Not used, and why (b-log, 10/11): AVD snapshots (after a load with -gpu host,
restored processes drew no text and the guest clock was 80 s off) and IMAP
DELETE of Sent (GreenMail 2.1.2 throws in signalDeletion and drops the
connection, so the folder stays).
"""
import argparse
import imaplib
import json
import os
import signal
import socket
import subprocess
import time
from pathlib import Path

from setup_assets import sha

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'com.fsck.k9'
LAUNCH = PACKAGE + '/.activity.MessageHomeActivity'
FORWARDER = 'com.google.androidenv.accessibilityforwarder'
DATA = '/data/data/' + PACKAGE
ARCHIVE = '/data/local/tmp/ghosteffect/k9-%s.tar'
GREENMAIL_PID = ROOT / 'runtime' / 'greenmail.pid'
# Synthetic accounts on the loopback GreenMail only, never real credentials.
ACCOUNTS = {'alice': 'alicepass', 'bob': 'bobpass'}
SMTP_PORT, IMAP_PORT = 3025, 3143
REVERSE_PORTS = (14025, IMAP_PORT)   # SMTP via the fault proxy (listens on 14025), IMAP


def port_open(port):
    with socket.socket() as s:
        s.settimeout(.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def wait(condition, seconds, what):
    deadline = time.monotonic() + seconds
    while not condition():
        if time.monotonic() > deadline:
            raise RuntimeError('timed out waiting for ' + what)
        time.sleep(.2)


def fresh_greenmail(java, log_path):
    """Stop the GreenMail a previous reset started and start an empty one."""
    jar = ROOT / 'runtime' / 'assets' / 'greenmail.jar'
    lock = json.loads((ROOT / 'testbed' / 'assets.lock.json').read_text())
    if not jar.is_file() or sha(jar) != next(a['sha256'] for a in lock['assets'] if a['file'] == 'greenmail.jar'):
        raise RuntimeError('pinned GreenMail JAR missing or hash mismatch')
    if GREENMAIL_PID.exists():
        try:
            os.kill(int(GREENMAIL_PID.read_text()), signal.SIGTERM)
        except (OSError, ValueError):
            pass
    wait(lambda: not port_open(IMAP_PORT) and not port_open(SMTP_PORT), 15, 'old GreenMail to stop')
    users = ','.join(f'{u}:{p}@test.invalid' for u, p in ACCOUNTS.items())
    command = [java, '-Dgreenmail.smtp.hostname=127.0.0.1', f'-Dgreenmail.smtp.port={SMTP_PORT}',
               '-Dgreenmail.imap.hostname=127.0.0.1', f'-Dgreenmail.imap.port={IMAP_PORT}',
               '-Dgreenmail.users=' + users, '-jar', str(jar)]
    detach = dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS) \
        if os.name == 'nt' else dict(start_new_session=True)
    with open(log_path, 'ab') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **detach)
    GREENMAIL_PID.write_text(str(process.pid))
    wait(lambda: port_open(IMAP_PORT) and port_open(SMTP_PORT), 30, 'GreenMail to listen')
    return process.pid


def prepare_mailboxes(want_sent):
    counts = {}
    for user, password in ACCOUNTS.items():
        client = imaplib.IMAP4('127.0.0.1', IMAP_PORT)
        try:
            client.login(user, password)
            if user == 'alice' and want_sent:
                client.create('Sent')
            boxes = [line.decode().rsplit(' ', 1)[-1].strip('"') for line in client.list()[1]]
            counts[user] = {box: int(client.select(box, readonly=True)[1][0]) for box in boxes}
        finally:
            client.logout()
    return counts


def reset(adb_path, serial, config, output, adb_server_port='5038', java='java'):
    adb = [str(Path(adb_path).resolve()), '-P', str(adb_server_port), '-s', serial]

    def run(*cmd):
        return subprocess.run(adb + list(cmd), capture_output=True, text=True, timeout=120).stdout.strip()

    if run('shell', 'whoami') != 'root':
        run('root')
        run('wait-for-device')
    # AndroidWorld's accessibility forwarder crashes ("keeps stopping") whenever no AndroidWorld session holds
    # its gRPC server, and the dialog covers K-9 (b-log 12/11). agent_episode.py re-enables it after this reset.
    run('shell', 'settings put secure enabled_accessibility_services "" && am force-stop ' + FORWARDER)
    archive = ARCHIVE % config
    restore = (f'am force-stop {PACKAGE} && test -f {archive} && rm -rf {DATA}/* && '
               f'tar -xpf {archive} -C /data/data && chcon -R "$(stat -c %C {DATA})" {DATA} && '
               f'sha256sum {archive}')
    archive_sha = run('shell', restore).split(' ')[0]
    db = run('shell', f'ls {DATA}/databases/*.db | grep -v preferences').splitlines()[0]
    sql = 'select count(*) from messages; select count(*) from outbox_state; select count(*) from pending_commands'
    k9_rows = [int(n) for n in run('shell', f'sqlite3 {db} "{sql}"').split()]
    sent_pref = run('shell', f'sqlite3 {DATA}/databases/preferences_storage '
                             '"select value from preferences_storage where primkey like \'%.sentFolderId\'"')
    for port in REVERSE_PORTS:
        run('reverse', f'tcp:{port}', f'tcp:{port}')
    pid = fresh_greenmail(java, output / 'greenmail.log')
    mailboxes = prepare_mailboxes(config == 'sent')
    run('shell', 'am', 'start', '-W', '-n', LAUNCH)
    top = ''
    for _ in range(20):
        top = next((l.strip() for l in run('shell', 'dumpsys', 'activity', 'activities').splitlines()
                    if 'topResumedActivity' in l), '')
        if PACKAGE + '/' in top:
            break
        time.sleep(.5)
    focus = ''
    for _ in range(3):   # a system error dialog left over K-9 takes the focus; BACK closes it
        focus = next((l.strip() for l in run('shell', 'dumpsys', 'window').splitlines() if 'mCurrentFocus' in l), '')
        if PACKAGE + '/' in focus:
            break
        run('shell', 'input', 'keyevent', 'KEYCODE_BACK')
        time.sleep(1)
    notifications = run('shell', 'dumpsys', 'notification').count(f'pkg={PACKAGE}')
    reverse = run('reverse', '--list')
    checks = dict(archive_restored=len(archive_sha) == 64,
                  k9_store_empty=k9_rows == [0, 0, 0],
                  sent_setting=bool(sent_pref) == (config == 'sent'),
                  mailboxes_empty=all(n == 0 for boxes in mailboxes.values() for n in boxes.values()),
                  server_sent_folder=('Sent' in mailboxes['alice']) == (config == 'sent'),
                  k9_on_top=PACKAGE + '/' in top,
                  k9_focused=PACKAGE + '/' in focus,
                  no_k9_notifications=notifications == 0,
                  reverse_ports=all(f'tcp:{p}' in reverse for p in REVERSE_PORTS))
    return dict(verdict='PASS' if all(checks.values()) else 'FAIL', config=config, checks=checks,
                archive=archive, archive_sha256=archive_sha, k9_messages_outbox_pending=k9_rows,
                greenmail_pid=pid, mailboxes=mailboxes, top_activity=top, focus=focus, utc_ns=time.time_ns())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', choices=['nosent', 'sent'], required=True)
    parser.add_argument('--adb', required=True)
    parser.add_argument('--adb-server-port', default='5038')
    parser.add_argument('--serial', default='emulator-5580')
    parser.add_argument('--java', default='java')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = reset(args.adb, args.serial, args.config, args.output, args.adb_server_port, args.java)
    (args.output / 'RESET.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['verdict'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
