"""Real loopback protocol tests using SYNTHETIC backends/screens, not Android data."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import smtplib
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from faultproxy import Journal, Faults, http_proxy, smtp_proxy, control_server
from ui import ADB, read_nonce, focused_window
from controller import HostController
import grader
from app_driver import poll_history, navigate


@contextmanager
def serving(server):
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
    thread.start()
    try:
        yield server.server_address
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)


class TestProtocols(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'proxy.jsonl'
        self.faults = Faults(Journal(self.path), barrier_timeout=2, withhold_seconds=.1)
        self.requests = []
        owner = self

        class Backend(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_PUT(self):
                data = self.rfile.read(int(self.headers.get('Content-Length', 0)))
                owner.requests.append((self.path, data))
                if owner.status == 200:
                    reply = b'{"event_id":"$synthetic"}'
                else:
                    reply = b''
                self.send_response(owner.status)
                self.send_header('Content-Length', str(len(reply)))
                self.end_headers()
                self.wfile.write(reply)
        self.status = 200
        self.backend = ThreadingHTTPServer(('127.0.0.1', 0), Backend)

    def tearDown(self):
        self.backend.server_close()
        self.temp.cleanup()

    def events(self):
        return [json.loads(x) for x in self.path.read_text().splitlines()]

    def request(self, address, path='/_matrix/client/v3/rooms/room/send/m.room.message/id1'):
        conn = http.client.HTTPConnection(*address, timeout=4)
        try:
            conn.request('PUT', path, b'{"body":"synthetic"}')
            response = conn.getresponse()
            return response.status, response.read()
        finally:
            conn.close()

    def proxy(self, address, protocol='matrix'):
        return http_proxy('http://%s:%s' % address, protocol, self.faults)

    def test_backend_accepted_before_drop_but_no_ack_is_forwarded(self):
        arm = self.faults.configure('drop', 'id1')
        with serving(self.backend) as upstream, serving(self.proxy(upstream)) as proxy, ThreadPoolExecutor(1) as pool:
            future = pool.submit(self.request, proxy)
            self.assertTrue(self.faults.arm['reached'].wait(2))
            self.assertEqual(len(self.requests), 1)
            self.assertFalse(future.done(), 'response must still be held at the fault barrier')
            self.faults.release(arm, {'observed_class': 'synthetic-app-death'})
            with self.assertRaises((OSError, http.client.HTTPException)):
                future.result()
        events = [x['event'] for x in self.events()]
        self.assertLess(events.index('UPSTREAM_ACCEPT'), events.index('PRE_ACK_BARRIER'))
        self.assertLess(events.index('FAULT_RECEIPT'), events.index('REPLY_DROP'))
        self.assertNotIn('ACK_WRITE', events)

    def test_terminal_reject_never_forwards_original_or_late_same_id(self):
        arm = self.faults.configure('reject', 'id1')
        with serving(self.backend) as upstream, serving(self.proxy(upstream)) as proxy:
            self.assertEqual(self.request(proxy)[0], 403)
            self.faults.release(arm, {'observed_class': 'none'})
            self.assertEqual(self.request(proxy)[0], 403)
            self.assertEqual(self.requests, [])
            self.assertEqual(self.request(proxy, '/_matrix/client/v3/rooms/room/send/m.room.message/NEW_ID')[0], 200)
        self.assertEqual(len(self.requests), 1)

    def test_successful_caldav_put_enters_commit_barrier(self):
        self.status = 201
        arm = self.faults.configure('drop', '/alice/calendar/test.ics')
        with serving(self.backend) as upstream, serving(self.proxy(upstream, 'caldav')) as proxy, ThreadPoolExecutor(1) as pool:
            future = pool.submit(self.request, proxy, '/alice/calendar/test.ics')
            self.assertTrue(self.faults.arm['reached'].wait(2))
            self.faults.release(arm, {'observed_class': 'none'})
            with self.assertRaises((OSError, http.client.HTTPException)):
                future.result()

    def test_server_failure_is_not_a_commit_barrier(self):
        self.status = 500
        self.faults.configure('drop', 'id1')
        with serving(self.backend) as upstream, serving(self.proxy(upstream)) as proxy:
            self.assertEqual(self.request(proxy)[0], 500)
            self.assertFalse(self.faults.arm['reached'].is_set())

    def test_sticky_drops_same_id_retry_until_release_then_allows_ack(self):
        arm = self.faults.configure('sticky', 'id1')
        with serving(self.backend) as upstream, serving(self.proxy(upstream)) as proxy, ThreadPoolExecutor(1) as pool:
            first = pool.submit(self.request, proxy)
            self.assertTrue(self.faults.arm['reached'].wait(2))
            with self.assertRaises((OSError, http.client.HTTPException)):
                self.request(proxy)
            self.faults.release(arm, {'observed_class': 'synthetic-app-death'})
            with self.assertRaises((OSError, http.client.HTTPException)):
                first.result()
            self.assertEqual(self.request(proxy)[0], 200)
        self.assertEqual(len(self.requests), 3)  # forwarding != deduplicating; backend owns dedup

    def test_withhold_and_missing_fault_receipt_stay_explicit(self):
        self.faults.configure('withhold', 'id1')
        with serving(self.backend) as upstream, serving(self.proxy(upstream)) as proxy:
            with self.assertRaises((OSError, http.client.HTTPException)):
                self.request(proxy)
        self.assertFalse(self.faults.arm['fault_recorded'])
        self.assertFalse(next(x for x in self.events() if x['event'] == 'WITHHOLD_END')['released'])

    def test_control_cannot_release_before_barrier_and_logs_no_body(self):
        arm = self.faults.configure('drop', 'id1')
        with self.assertRaises(ValueError):
            self.faults.release(arm, {'observed_class': 'none'})
        with self.assertRaises(ValueError):
            control_server(self.faults, ('0.0.0.0', 0))


class TestSMTP(unittest.TestCase):
    def test_smtp_data_accept_is_held_and_reject_data_is_never_forwarded(self):
        received = []

        class Backend(socketserver.StreamRequestHandler):
            def handle(self):
                self.wfile.write(b'220 synthetic SMTP\r\n')
                while True:
                    line = self.rfile.readline()
                    if not line:
                        return
                    verb = line.split()[0].upper()
                    if verb == b'DATA':
                        self.wfile.write(b'354 send DATA\r\n')
                        data = []
                        while True:
                            item = self.rfile.readline()
                            if not item:
                                return
                            if item == b'.\r\n':
                                break
                            data.append(item)
                        received.append(b''.join(data))
                        self.wfile.write(b'250 stored\r\n')
                    elif verb == b'EHLO':
                        self.wfile.write(b'250-synthetic\r\n250-PIPELINING\r\n250 STARTTLS\r\n')
                    elif verb == b'QUIT':
                        self.wfile.write(b'221 bye\r\n')
                        return
                    else:
                        self.wfile.write(b'250 OK\r\n')

        class Server(socketserver.ThreadingTCPServer):
            daemon_threads = True

        def send(address, message_id):
            client = smtplib.SMTP(*address, timeout=4)
            try:
                client.ehlo()
                self.assertNotIn('starttls', client.esmtp_features)
                self.assertNotIn('pipelining', client.esmtp_features)
                client.sendmail('alice@test.invalid', ['bob@test.invalid'],
                                'Message-ID: %s\r\nSubject: synthetic\r\n\r\nbody\r\n' % message_id)
            finally:
                client.close()

        with tempfile.TemporaryDirectory() as temp:
            faults = Faults(Journal(Path(temp) / 'smtp.jsonl'), barrier_timeout=3)
            with serving(Server(('127.0.0.1', 0), Backend)) as upstream, serving(smtp_proxy(upstream, faults)) as proxy:
                arm = faults.configure('drop', '<first@test.invalid>')
                with ThreadPoolExecutor(1) as pool:
                    future = pool.submit(send, proxy, '<first@test.invalid>')
                    self.assertTrue(faults.arm['reached'].wait(2))
                    self.assertEqual(len(received), 1)
                    self.assertFalse(future.done())
                    faults.release(arm, {'observed_class': 'synthetic-app-death'})
                    with self.assertRaises(smtplib.SMTPServerDisconnected):
                        future.result()
                arm = faults.configure('reject', '<rejected@test.invalid>')
                with self.assertRaises(smtplib.SMTPDataError):
                    send(proxy, '<rejected@test.invalid>')
                faults.release(arm, {'observed_class': 'none'})
                with self.assertRaises(smtplib.SMTPDataError):
                    send(proxy, '<rejected@test.invalid>')
                self.assertEqual(len(received), 1)


XML = b'''<hierarchy><node resource-id="account" text="alice"/><node resource-id="title" text="test-room"/>
<node resource-id="timeline"><node resource-id="anchor" text="previous"/>
<node resource-id="row"><node resource-id="outgoing"/><node resource-id="ack"/>
<node text="hello gx:ABC123"/></node></node></hierarchy>'''


class TestGUI(unittest.TestCase):
    def test_failed_focus_check_retains_the_actual_window_and_input_dumps(self):
        class Device(ADB):
            def shell(self,*args):
                return 'mCurrentFocus=null' if args==('dumpsys','window','displays') else 'DispatchFrozen: true'
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'failed-focus'
            with self.assertRaises(RuntimeError):Device('not-executed','emulator-5554').foreground_window(output)
            self.assertEqual((output/'window-displays.txt').read_text(),'mCurrentFocus=null')
            self.assertEqual((output/'input.txt').read_text(),'DispatchFrozen: true')

    def test_malformed_capture_is_saved_without_retry_and_cleanup_cannot_hide_it(self):
        calls=[]
        class Device(ADB):
            def foreground_window(self,diagnostics=None):
                return dict(component='test.app/.Main', token='abc', user=0, display_id=0)
            def run(self, *args, **kwargs):
                calls.append(args)
                if args[:2]==('shell','uiautomator'):return b'ERROR: could not get idle state.\r\n'
                if args[:2]==('exec-out','cat'):return b'not an XML tree\r\n'
                if args[:2]==('shell','rm'):raise OSError('synthetic cleanup failure')
                raise AssertionError(args)
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'capture'
            with self.assertRaises(ET.ParseError):
                Device('not-executed','emulator-5554').capture(output)
            self.assertEqual((output/'first/tree.raw.xml').read_bytes(),b'not an XML tree\r\n')
            self.assertTrue((output/'first/cleanup-error.json').is_file())
            self.assertEqual(json.loads((output/'capture-error.json').read_text())['stage'],'first_tree')
            self.assertFalse((output/'capture.json').exists())
            self.assertEqual(sum(c[:2]==('shell','uiautomator') for c in calls),1)

    def test_well_formed_non_hierarchy_is_not_a_valid_gui_capture(self):
        class Device(ADB):
            def run(self,*args,**kwargs):
                return b'<error>synthetic command failure</error>' if args[0]=='exec-out' else b''
        with self.assertRaisesRegex(ValueError,'not a hierarchy'):
            Device('not-executed','emulator-5554').tree()

    def test_focus_uses_live_display_state_not_last_anr_or_resumed_activity(self):
        class Device(ADB):
            focus='mCurrentFocus=Window{abc u0 test.app/.Main}'
            def shell(self,*args):
                if args==('dumpsys','window','displays'):
                    return self.focus+'\nmFocusedApp=ActivityRecord{def u0 other.app/.Main}'
                if args==('dumpsys','input'):
                    return "DispatchEnabled: true\nDispatchFrozen: false\nFocusedDisplayId: 0\nFocusedWindows:\n  displayId=0, name='abc test.app/.Main'\nFocusRequests:\n"
                if args==('dumpsys','window'):
                    return 'Last ANR\n mCurrentFocus=Window{old u0 other.app/.Main}\n'+self.focus
                return 'window enumeration without focus'
        device=Device('not-executed','emulator-5554')
        self.assertEqual(device.foreground(),'test.app/.Main')
        device.focus='mCurrentFocus=null'
        with self.assertRaises(RuntimeError):device.foreground()
        device.focus='mCurrentFocus=Window{a u0 test.app/.Main}\nmCurrentFocus=Window{b u0 other.app/.Main}'
        with self.assertRaises(RuntimeError):device.foreground()

    def test_observed_anr_modal_blocks_underlying_application_focus(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/anr-focus.json').read_text())
        self.assertIn('RequestRoleActivity',fixture['display_dump'])
        self.assertIn('Application Not Responding',fixture['input_dump'])
        with self.assertRaisesRegex(RuntimeError,'input focus differs'):
            focused_window(fixture['display_dump'],fixture['input_dump'])

    def test_input_frozen_missing_other_window_or_other_display_is_not_ready(self):
        display='mCurrentFocus=Window{abc u0 test.app/.Main}'
        inp="DispatchEnabled: true\nDispatchFrozen: false\nFocusedDisplayId: 0\nFocusedWindows:\n  displayId=0, name='abc test.app/.Main'\nFocusRequests:\n"
        self.assertEqual(focused_window(display,inp)['token'],'abc')
        self.assertEqual(focused_window(display,inp.replace('\n','\r\n'))['token'],'abc')
        for text in (inp.replace('DispatchEnabled: true','DispatchEnabled: false'),
                     inp.replace('DispatchFrozen: false','DispatchFrozen: true'),
                     inp.replace('FocusedDisplayId: 0','FocusedDisplayId: 1'),
                     inp.replace('abc test.app/.Main','def test.app/.Dialog'),
                     inp.replace("  displayId=0, name='abc test.app/.Main'",'')):
            with self.assertRaises(RuntimeError):focused_window(display,text)

    def setUp(self):
        self.profile = dict(frozen=True, profile_id='SYNTHETIC-ONLY', package='test.app',
                            account={'resource-id': 'account', 'text': 'alice'},
                            title={'resource-id': 'title', 'text': 'test-room'},
                            timeline={'resource-id': 'timeline'}, anchor={'resource-id': 'anchor'},
                            row={'resource-id': 'row'}, outgoing={'resource-id': 'outgoing'},
                            acknowledged={'resource-id': 'ack'}, exclude=[{'resource-id': 'failed'}])

    def read(self, xml=XML, **changes):
        capture = dict(stable_tree=True, same_foreground=True, mono_start_ns=0, mono_end_ns=1_000_000_000,
                       foreground_after='test.app/.Main', tree_sha256=hashlib.sha256(xml).hexdigest())
        capture.update(changes)
        return read_nonce(xml, capture, self.profile, 'gx:ABC123')

    def test_positive_is_gui_observation_only(self):
        self.assertEqual(self.read()['verdict'], 'com')
        self.assertIn('requires calibration', self.read()['scope'])

    def test_wrong_account_room_foreground_stability_are_bot(self):
        for xml in (XML.replace(b'alice', b'other'), XML.replace(b'test-room', b'wrong-room')):
            self.assertEqual(self.read(xml)['verdict'], 'BOT')
        self.assertEqual(self.read(foreground_after='evil.app/.Main')['verdict'], 'BOT')
        self.assertEqual(self.read(stable_tree=False)['verdict'], 'BOT')

    def test_failed_or_not_acknowledged_nonce_is_not_positive(self):
        for xml in (XML.replace(b'"ack"', b'"failed"'), XML.replace(b'"outgoing"', b'"incoming"')):
            self.assertEqual(self.read(xml)['verdict'], 'BOT')

    def test_absence_requires_bound_bottom_receipt(self):
        xml = XML.replace(b'ABC123', b'ZZZZZZ')
        cap = dict(stable_tree=True, same_foreground=True, mono_start_ns=0, mono_end_ns=1,
                   foreground_after='test.app/.Main', tree_sha256=hashlib.sha256(xml).hexdigest())
        self.assertEqual(read_nonce(xml, cap, self.profile, 'gx:ABC123')['verdict'], 'BOT')
        receipt = dict(direction='latest', unchanged_swipes=2, tree_sha256=cap['tree_sha256'])
        self.assertEqual(read_nonce(xml, cap, self.profile, 'gx:ABC123', receipt)['verdict'], 'abs')
        receipt['tree_sha256'] = 'stale'
        self.assertEqual(read_nonce(xml, cap, self.profile, 'gx:ABC123', receipt)['verdict'], 'BOT')

    def test_unfrozen_profile_and_bad_nonce_are_bot(self):
        self.profile['frozen'] = False
        self.assertEqual(self.read()['verdict'], 'BOT')
        with self.assertRaises(ValueError):
            ADB('adb', 'personal-phone-serial')

    def test_nonce_token_bound_is_enforced_before_analytic_use(self):
        crowded=XML.replace(b'hello gx:ABC123',b' '.join([b'gx:ABC123']*41))
        self.assertEqual(self.read(crowded)['verdict'],'BOT')

    def test_adb_connection_error_cannot_be_app_death_receipt(self):
        device = ADB('adb', 'emulator-5554')
        failed = subprocess.CompletedProcess([], 1, b'', b'error: device not found')
        with patch('ui.subprocess.run', return_value=failed):
            with self.assertRaises(RuntimeError):
                device.pids('test.app')

    def test_unconfigured_navigation_refuses_and_bot_poll_is_censored(self):
        with self.assertRaises(ValueError):
            navigate(None, {'frozen': False}, [])
        with tempfile.TemporaryDirectory() as temp:
            result = poll_history(None, {}, 'gx:ABC123', Path(temp)/'polls', time.monotonic_ns(),
                                  horizon=.04, interval=.01)
            self.assertTrue(result['right_censored'])
            self.assertIsNone(result['first_gui_com_seconds'])
            self.assertIsNone(result['last_verified_abs_seconds'])


class TestController(unittest.TestCase):
    def test_durable_before_tap_and_restart_never_reissues(self):
        with tempfile.TemporaryDirectory() as temp:
            database = Path(temp) / 'ledger.db'
            owner = self

            class Device:
                def foreground(self):
                    return 'test.app/.Main'

                def tap(self, x, y):
                    from ledger import Ledger
                    checker = Ledger(str(database))
                    owner.assertEqual(checker.state('e1'), 'ISSUED')
                    checker.close()
                    raise OSError('synthetic adb error after possible input')
            journal = Journal(Path(temp) / 'controller.jsonl')
            controller = HostController(database, Device(), journal)
            with self.assertRaises(ValueError):
                controller.prepare('e1', 'wf', 0, 'test.app', 'send', b'old', 'visible')
            nonce = controller.prepare('e1', 'wf', 0, 'test.app', 'send', b'old', 'private')
            self.assertEqual(len(nonce), 9)
            with self.assertRaises(OSError):
                controller.dispatch('e1', 'test.app', 10, 20)
            controller.close()
            restarted = HostController(database, Device(), journal)
            self.assertEqual(restarted.prepare('e1', 'wf', 0, 'test.app', 'send', b'old', 'private'), nonce)
            self.assertEqual(restarted.recover('e1')['decision'], 'ASK')
            with self.assertRaises(ValueError):
                restarted.dispatch('e1', 'test.app', 10, 20)
            restarted.close()


class TestGrader(unittest.TestCase):
    def test_matrix_pagination_counts_distinct_server_events(self):
        pages = [dict(chunk=[{'type': 'm.room.message', 'event_id': 'one', 'content': {'body': 'GX_TAG'}},
                             {'type': 'm.room.message', 'event_id': 'other', 'content': {'body': 'not-matching'}}], end='p1'),
                 dict(chunk=[{'type': 'm.room.message', 'event_id': 'two', 'content': {'body': 'GX_TAG'}}], end='p2'),
                 dict(chunk=[])]
        with patch.object(grader, 'fetch', side_effect=[json.dumps(x).encode() for x in pages]):
            result = grader.matrix_count('http://127.0.0.1', '!room:test.invalid', 'GX_TAG', 'synthetic-token')
        self.assertEqual(result['copies'], 2)
        self.assertTrue(result['scan_complete'])

    def test_incomplete_matrix_scan_fails_instead_of_claiming_zero(self):
        page = dict(chunk=[{'type': 'other'}], end='p1')
        with patch.object(grader, 'fetch', return_value=json.dumps(page).encode()):
            with self.assertRaises(RuntimeError):
                grader.matrix_count('http://127.0.0.1', '!room:test.invalid', 'GX_TAG', 'synthetic-token', max_pages=1)

    def test_caldav_refuses_cross_origin_href(self):
        tree = b'<d:multistatus xmlns:d="DAV:"><d:response><d:href>http://other.invalid/private</d:href></d:response></d:multistatus>'
        with patch.object(grader, 'fetch', return_value=tree):
            with self.assertRaises(RuntimeError):
                grader.caldav_count('http://127.0.0.1/calendar/', 'GX_TAG', 'synthetic', 'synthetic')


if __name__ == '__main__':
    unittest.main()
