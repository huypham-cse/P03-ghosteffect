"""Actual pinned GreenMail + reconstructed SMTP proxy; synthetic mail, no Android/LLM.

Requires project-local verified greenmail.jar and Java. Own JVM, fresh mailbox,
loopback only. Produces receipts for acceptance/lost-ACK/new-ID duplicate/reject.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import smtplib
import socket
import subprocess
import threading
import time
import uuid
import sys

from faultproxy import Journal, Faults, smtp_proxy
from grader import imap_count
from setup_assets import sha


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def run(output, java):
    if not __debug__:
        raise RuntimeError('verification assertions require Python without -O')
    output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    jar = root / 'runtime' / 'assets' / 'greenmail.jar'
    lock = json.loads((Path(__file__).parent / 'assets.lock.json').read_text())
    expected = next(a['sha256'] for a in lock['assets'] if a['file'] == 'greenmail.jar')
    if not jar.is_file() or sha(jar) != expected:
        raise RuntimeError('download and hash-verify the pinned GreenMail JAR first')
    smtp_port, imap_port = free_port(), free_port()
    if smtp_port == imap_port:
        imap_port = free_port()
    # These are newly generated disposable test credentials, never user secrets.
    password, username = uuid.uuid4().hex, 'gx_test'
    command = [java, '-Dgreenmail.smtp.hostname=127.0.0.1', '-Dgreenmail.smtp.port=' + str(smtp_port),
               '-Dgreenmail.imap.hostname=127.0.0.1', '-Dgreenmail.imap.port=' + str(imap_port),
               '-Dgreenmail.users=' + username + ':' + password + '@test.invalid', '-jar', str(jar)]
    faults = Faults(Journal(output / 'proxy.jsonl'), barrier_timeout=10)
    server = smtp_proxy(('127.0.0.1', smtp_port), faults)
    worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .02}, daemon=True)
    cases = []

    def send(mid, tag):
        client = smtplib.SMTP(*server.server_address, timeout=15)
        try:
            client.sendmail('sender@test.invalid', ['gx_test@test.invalid'],
                            'Message-ID: <%s@test.invalid>\r\nSubject: %s\r\n\r\n%s\r\n' % (mid, tag, tag))
        finally:
            client.close()

    def count(tag):
        return imap_count('127.0.0.1', imap_port, 'INBOX', tag, username, password)['copies']

    started = time.monotonic()
    with (output / 'greenmail.log').open('w', encoding='utf-8') as logfile:
        process = subprocess.Popen(command, stdout=logfile, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('GreenMail exited; inspect greenmail.log')
                try:
                    with socket.create_connection(('127.0.0.1', imap_port), timeout=.2), \
                         socket.create_connection(('127.0.0.1', smtp_port), timeout=.2):
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError('GreenMail startup timed out')
            worker.start()
            tag = 'GX_NOFAULT_' + uuid.uuid4().hex
            send('nofault', tag)
            assert count(tag) == 1
            cases.append(dict(case='nofault', receiver_copies=1))
            tag = 'GX_LOSTACK_' + uuid.uuid4().hex
            arm = faults.configure('drop', '<lost@test.invalid>')
            with ThreadPoolExecutor(1) as pool:
                future = pool.submit(send, 'lost', tag)
                if not faults.arm['reached'].wait(10):
                    raise RuntimeError('SMTP acceptance barrier not reached')
                # Server oracle is used ONLY by this injector-side smoke.
                assert count(tag) == 1 and not future.done()
                faults.release(arm, {'observed_class': 'none', 'purpose': 'protocol-smoke-not-app-fault'})
                try:
                    future.result()
                except smtplib.SMTPServerDisconnected:
                    pass
                else:
                    raise AssertionError('lost ACK unexpectedly reached client')
            cases.append(dict(case='committed_lost_ack', receiver_copies=count(tag)))
            send('redo-new-id', tag)
            assert count(tag) == 2
            cases.append(dict(case='synthetic_new_id_resend', receiver_copies=2,
                              scope='protocol resend, not a GUI or native-agent redo'))
            tag = 'GX_REJECT_' + uuid.uuid4().hex
            arm = faults.configure('reject', '<reject@test.invalid>')
            for attempt in range(2):
                try:
                    send('reject', tag)
                except smtplib.SMTPDataError as exc:
                    assert exc.smtp_code == 550
                else:
                    raise AssertionError('expected terminal reject')
                if attempt == 0:
                    faults.release(arm, {'observed_class': 'none'})
            assert count(tag) == 0
            cases.append(dict(case='preapply_reject_plus_late_same_id', receiver_copies=0,
                              scope='original ID blocked by proxy for process lifetime'))
        finally:
            if worker.is_alive():
                server.shutdown()
                worker.join(2)
            server.server_close()
            process.terminate()
            try:
                process.wait(10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    result = dict(status='PASS', kind='real GreenMail protocol integration with synthetic messages',
                  android=False, llm=False, app_fault=False, jar_sha256=expected,
                  seconds=time.monotonic() - started, cases=cases,
                  source_sha256={p.name: sha(p) for p in Path(__file__).parent.glob('*.py')})
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--java', default=shutil.which('java'))
    args = parser.parse_args()
    if args.output.exists():
        parser.error('fresh output directory required; previous results are never overwritten')
    if not args.java:
        parser.error('Java not found')
    try:
        print(json.dumps(run(args.output, args.java), indent=2))
    except Exception as exc:
        if args.output.is_dir():
            (args.output / 'RESULT.json').write_text(json.dumps(dict(status='FAIL', error_type=type(exc).__name__,
                                                                   reason=str(exc)), indent=2), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
