"""Reconstructed test-account proxy, not the missing historical source.

HTTP reverse proxy: Matrix PUT /send/.../txnId or CalDAV PUT href.
SMTP: unencrypted local test transport, end-of-DATA barrier. No STARTTLS.
The control listener and receipts belong to the injector/grader, NEVER the agent.
"""
import argparse
import email.parser
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import socket
import socketserver
import struct
import threading
import time
from urllib.parse import urlsplit, unquote
import uuid


class Journal:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.run_id = uuid.uuid4().hex

    def emit(self, event, **fields):
        row = dict(run_id=self.run_id, event=event, mono_ns=time.monotonic_ns(),
                   utc_ns=time.time_ns(), **fields)
        with self.lock, self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=True) + '\n')
            f.flush()
            os.fsync(f.fileno())
        return row


class Faults:
    """One armed target per isolated proxy. Same-ID rejection persists until exit.

    Holding a response is NOT by itself proof that an app fault occurred. The
    injector must record the actual PID/network/agent receipt, then release it.
    """
    MODES = {'pass', 'reject', 'drop', 'sticky', 'withhold'}

    def __init__(self, journal, barrier_timeout=60, withhold_seconds=180):
        self.log = journal
        self.lock = threading.RLock()
        self.arm = None
        self.history = []
        self.rejected = set()
        self.barrier_timeout = barrier_timeout
        self.withhold_seconds = withhold_seconds

    def configure(self, mode, request_id=None):
        if mode not in self.MODES:
            raise ValueError('unknown fault mode')
        with self.lock:
            if self.arm and not self.arm['released'].is_set():
                raise ValueError('previous arm is not released')
            a = dict(id=uuid.uuid4().hex, mode=mode, request_id=request_id,
                     matched=False, reached=threading.Event(), released=threading.Event(),
                     fault_recorded=False)
            self.arm = a
            self.history.append(a)
            self.log.emit('ARM', arm_id=a['id'], mode=mode, target_id=request_id)
            return a['id']

    def select(self, rid):
        with self.lock:
            if rid in self.rejected:
                return 'reject', None
            a = self.arm
            if not a or (a['request_id'] is not None and a['request_id'] != rid):
                return 'pass', None
            if a['matched']:
                if a['mode'] == 'sticky' and a['request_id'] == rid and not a['released'].is_set():
                    return 'sticky-retry', a
                return 'pass', None
            a['matched'], a['request_id'] = True, rid
            if a['mode'] == 'reject':
                self.rejected.add(rid)
            self.log.emit('MATCH', arm_id=a['id'], request_id=rid)
            return a['mode'], a

    def status(self, arm_id):
        with self.lock:
            a = next((x for x in self.history if x['id'] == arm_id), None)
            if a is None:
                raise KeyError(arm_id)
            return dict(arm_id=arm_id, mode=a['mode'], request_id=a['request_id'],
                        matched=a['matched'], barrier=a['reached'].is_set(),
                        released=a['released'].is_set(), fault_recorded=a['fault_recorded'])

    def release(self, arm_id, fault_receipt):
        with self.lock:
            a = next((x for x in self.history if x['id'] == arm_id), None)
            if a is None:
                raise KeyError(arm_id)
            if not a['reached'].is_set():
                raise ValueError('no verified upstream acceptance/rejection barrier')
            if not isinstance(fault_receipt, dict) or not fault_receipt.get('observed_class'):
                raise ValueError('injector fault receipt required; no-fault uses observed_class=none')
            self.log.emit('FAULT_RECEIPT', arm_id=arm_id, receipt=fault_receipt)
            a['fault_recorded'] = True
            a['released'].set()

    def terminal_reject(self, rid, a):
        self.log.emit('TERMINAL_REJECT', request_id=rid, arm_id=a['id'] if a else None,
                      scope='same original request ID; proxy did not forward')
        if a:
            a['reached'].set()

    def after_accept(self, rid, mode, a, **receipt):
        # Acceptance is protocol-specific, not a claim of receiver UI visibility.
        self.log.emit('UPSTREAM_ACCEPT', request_id=rid, arm_id=a['id'] if a else None, **receipt)
        if not a or mode == 'pass':
            if a:
                a['reached'].set()
            return False
        if mode == 'sticky-retry':
            self.log.emit('RETRY_REPLY_DROP', request_id=rid, arm_id=a['id'])
            return True
        self.log.emit('PRE_ACK_BARRIER', request_id=rid, arm_id=a['id'])
        a['reached'].set()
        if mode == 'withhold':
            # Client timeout, or injector release; never fabricate a timeout receipt.
            released = a['released'].wait(self.withhold_seconds)
            self.log.emit('WITHHOLD_END', arm_id=a['id'], released=released)
        else:
            released = a['released'].wait(self.barrier_timeout)
            if not released:
                self.log.emit('INVALID_BARRIER_TIMEOUT', arm_id=a['id'])
        self.log.emit('REPLY_DROP', request_id=rid, arm_id=a['id'], mode=mode)
        return True


def reset_connection(conn):
    # Linux/Windows differ in linger's ABI. Failure still closes the connection,
    # and the journal deliberately says drop, not packet-level RST verified.
    try:
        value = struct.pack('hh' if os.name == 'nt' else 'ii', 1, 0)
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, value)
    except OSError:
        pass
    conn.close()


def http_proxy(upstream, protocol, faults, listen=('127.0.0.1', 0)):
    target = urlsplit(upstream)
    if target.scheme not in ('http', 'https') or target.username or target.query or target.path not in ('', '/'):
        raise ValueError('upstream must be an http(s) origin without credentials or path')
    if protocol not in ('matrix', 'caldav'):
        raise ValueError('expected matrix or caldav')

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, *args):
            pass  # never print authorization headers, bodies, or token query strings

        def handle_request(self):
            # http.client supplies Content-Length on normal app requests. Refuse
            # unsupported framing explicitly instead of forwarding a truncated PUT.
            if self.headers.get('Transfer-Encoding'):
                self.send_error(501, 'chunked requests not supported by reconstructed proxy')
                return
            size = int(self.headers.get('Content-Length', '0'))
            if size < 0 or size > 16 * 1024 * 1024:
                self.send_error(413)
                return
            body = self.rfile.read(size)
            path = urlsplit(self.path).path
            match = re.fullmatch(r'/_matrix/client/(?:r0|v3)/rooms/[^/]+/send/[^/]+/([^/]+)', path)
            rid = None
            if self.command == 'PUT':
                rid = unquote(match.group(1)) if protocol == 'matrix' and match else (path if protocol == 'caldav' else None)
            mode, a = faults.select(rid) if rid is not None else ('pass', None)
            if rid is not None:
                faults.log.emit('REQUEST', request_id=rid, protocol=protocol,
                                body_sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
            if mode == 'reject':
                faults.terminal_reject(rid, a)
                data = b'{"errcode":"M_FORBIDDEN","error":"testbed terminal rejection"}'
                self.send_response(403)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            cls = http.client.HTTPSConnection if target.scheme == 'https' else http.client.HTTPConnection
            conn = cls(target.hostname, target.port, timeout=35)
            try:
                headers = {k: v for k, v in self.headers.items()
                           if k.lower() not in ('host', 'connection', 'proxy-connection', 'transfer-encoding')}
                conn.request(self.command, self.path, body=body, headers=headers)
                response = conn.getresponse()
                data, status, response_headers = response.read(), response.status, response.getheaders()
                receipt = dict(status=status)
                accepted = protocol == 'caldav' and status in (201, 204)
                if protocol == 'matrix' and status == 200:
                    try:
                        receipt['event_id'] = json.loads(data)['event_id']
                        accepted = isinstance(receipt['event_id'], str) and bool(receipt['event_id'])
                    except (ValueError, KeyError, TypeError):
                        accepted = False
                if rid is not None and accepted and faults.after_accept(rid, mode, a, protocol=protocol, **receipt):
                    self.close_connection = True
                    reset_connection(self.connection)
                    return
                if rid is not None and not accepted:
                    faults.log.emit('UPSTREAM_NOT_ACCEPTED', request_id=rid, status=status)
                self.send_response(status)
                for k, v in response_headers:
                    if k.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                        self.send_header(k, v)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                if rid is not None:
                    faults.log.emit('ACK_WRITE', request_id=rid, status=status,
                                    scope='proxy write completed; not client-consumption proof')
            except (OSError, http.client.HTTPException) as exc:
                faults.log.emit('TRANSPORT_ERROR', request_id=rid, error_type=type(exc).__name__)
                self.close_connection = True
            finally:
                conn.close()

        do_GET = do_POST = do_PUT = do_DELETE = do_PROPFIND = do_REPORT = do_OPTIONS = do_MKCOL = handle_request

    return ThreadingHTTPServer(listen, Handler)


def smtp_proxy(upstream, faults, listen=('127.0.0.1', 0)):
    """Pass SMTP commands through; inspect only DATA's Message-ID and final 250.

    Local GreenMail/Postfix must disable STARTTLS/PIPELINING advertisements. The
    proxy removes them and rejects an unsolicited STARTTLS. Test accounts only.
    """
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            self.connection.settimeout(240)
            with socket.create_connection(upstream, timeout=35) as remote:
                stream = remote.makefile('rwb')

                def reply():
                    lines = []
                    while True:
                        line = stream.readline(65537)
                        if len(line) < 4 or len(line) > 65536:
                            raise OSError('malformed SMTP response')
                        lines.append(line)
                        if line[3:4] != b'-':
                            return lines

                def send_reply(lines):
                    self.wfile.write(b''.join(lines))
                    self.wfile.flush()

                send_reply(reply())
                while True:
                    command = self.rfile.readline(65537)
                    if not command:
                        return
                    verb = command.split(None, 1)[0].upper()
                    if verb in (b'STARTTLS', b'BDAT'):
                        send_reply([b'502 testbed requires local SMTP DATA without TLS\r\n'])
                        continue
                    stream.write(command)
                    stream.flush()
                    lines = reply()
                    if verb == b'EHLO' and lines[0].startswith(b'250'):
                        values = [x[4:].rstrip(b'\r\n') for x in lines
                                  if x[4:].split(None, 1)[0].upper() not in (b'STARTTLS', b'PIPELINING', b'CHUNKING')]
                        lines = [b'250' + (b' ' if i == len(values)-1 else b'-') + x + b'\r\n'
                                 for i, x in enumerate(values)]
                    send_reply(lines)
                    if verb == b'QUIT':
                        return
                    if verb != b'DATA' or not lines[-1].startswith(b'354'):
                        continue
                    chunks, size = [], 0
                    while True:
                        line = self.rfile.readline(65537)
                        if not line or len(line) > 65536:
                            raise OSError('incomplete SMTP DATA')
                        if line == b'.\r\n':
                            break
                        chunks.append(line)
                        size += len(line)
                        if size > 16 * 1024 * 1024:
                            raise OSError('SMTP DATA too large')
                    data = b''.join(chunks)
                    parsed = email.parser.BytesHeaderParser().parsebytes(data)
                    ids = parsed.get_all('Message-ID', [])
                    rid = str(ids[0]).strip() if len(ids) == 1 else None
                    mode, a = faults.select(rid) if rid else ('pass', None)
                    faults.log.emit('SMTP_DATA', request_id=rid, bytes=size,
                                    body_sha256=hashlib.sha256(data).hexdigest())
                    if mode == 'reject':
                        # SMTP upstream has entered DATA. Abort that transaction
                        # WITHOUT forwarding the terminating dot or message body.
                        faults.terminal_reject(rid, a)
                        send_reply([b'550 5.7.1 testbed terminal rejection\r\n'])
                        return
                    stream.write(data + b'.\r\n')
                    stream.flush()
                    ack = reply()
                    if ack[-1].startswith(b'250') and rid:
                        drop = faults.after_accept(rid, mode, a, protocol='smtp', status=250,
                                                   scope='SMTP accepted; not Sent-folder or inbox visibility')
                        if drop:
                            reset_connection(self.connection)
                            return
                    else:
                        faults.log.emit('UPSTREAM_NOT_ACCEPTED', request_id=rid,
                                        status=ack[-1][:3].decode('ascii', errors='replace'))
                    send_reply(ack)
                    faults.log.emit('ACK_WRITE', request_id=rid, status=250 if ack[-1].startswith(b'250') else None,
                                    scope='proxy write completed; not client-consumption proof')

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True
    return Server(listen, Handler)


def control_server(faults, listen=('127.0.0.1', 0)):
    if listen[0] != '127.0.0.1':
        raise ValueError('injector control must bind loopback')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            try:
                n = int(self.headers.get('Content-Length', '0'))
                if not 0 < n <= 65536:
                    raise ValueError('invalid control request size')
                payload = json.loads(self.rfile.read(n))
                if self.path == '/arm':
                    result = {'arm_id': faults.configure(payload['mode'], payload.get('request_id'))}
                elif self.path == '/status':
                    result = faults.status(payload['arm_id'])
                elif self.path == '/release':
                    faults.release(payload['arm_id'], payload['fault_receipt'])
                    result = {'ok': True}
                else:
                    raise ValueError('unknown endpoint')
                data, code = json.dumps(result).encode(), 200
            except (ValueError, KeyError, TypeError) as exc:
                data, code = json.dumps({'error': str(exc)}).encode(), 400
            self.send_response(code)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    return ThreadingHTTPServer(listen, Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', choices=['matrix', 'caldav', 'smtp'], required=True)
    parser.add_argument('--upstream', required=True, help='HTTP origin, or smtp://host:port')
    parser.add_argument('--listen-port', type=int, required=True)
    parser.add_argument('--control-port', type=int, required=True)
    parser.add_argument('--journal', type=Path, required=True)
    args = parser.parse_args()
    if args.journal.exists():
        parser.error('fresh journal required; one proxy process per isolated run')
    journal = Journal(args.journal)
    faults = Faults(journal)
    target = urlsplit(args.upstream)
    if args.protocol == 'smtp':
        if target.scheme != 'smtp' or not target.hostname or not target.port:
            parser.error('expected smtp://host:port')
        server = smtp_proxy((target.hostname, target.port), faults, ('127.0.0.1', args.listen_port))
    else:
        server = http_proxy(args.upstream, args.protocol, faults, ('127.0.0.1', args.listen_port))
    control = control_server(faults, ('127.0.0.1', args.control_port))
    journal.emit('START', protocol=args.protocol, kind='reconstruction', pid=os.getpid())
    threading.Thread(target=control.serve_forever, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        control.shutdown()
        control.server_close()


if __name__ == '__main__':
    main()
