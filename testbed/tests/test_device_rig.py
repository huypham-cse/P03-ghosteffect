"""Physical-phone K-9 rig (b-log 18/11): pure parsing and the guard that keeps it off unnamed devices. SYNTHETIC input."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import k9_fault_case
import k9_reset

DUMP = '''NOTIFICATION MANAGER (dumpsys notification)
  NotificationRecord(0x0a1: pkg=com.fsck.k9 user=UserHandle{0} id=7 tag=null importance=3 key=0|com.fsck.k9|7|null|10404: Notification(channel=misc))
      extras={
        android.title=String (Failed to send some messages)
        android.text=String (SmtpResponseParserException: Unexpected end of stream)
      }
  NotificationRecord(0x0b2: pkg=com.example.chat user=UserHandle{0} id=1 tag=null importance=4 key=x: Notification(channel=m))
      extras={
        android.title=String (Private person)
        android.text=String (private message text)
      }
'''

XML = ('<?xml version="1.0"?><hierarchy rotation="0">'
       '<node text="Outbox" resource-id="com.fsck.k9:id/toolbarTitle" package="com.fsck.k9" content-desc="" bounds="[158,137][310,220]"/>'
       '<node text="gx:ABC123" resource-id="" package="com.fsck.k9" content-desc="" bounds="[45,300][1000,360]"/>'
       '<node text="Private person" resource-id="" package="com.android.systemui" content-desc="" bounds="[0,0][10,10]"/>'
       '<node text="" resource-id="com.fsck.k9:id/account_setup_next_button" package="com.fsck.k9" content-desc="" '
       'bounds="[770,2025][990,2160]"/></hierarchy>')


class DeviceRig(unittest.TestCase):
    def test_only_k9_notifications_are_kept(self):
        self.assertEqual(k9_fault_case.k9_notices(DUMP),
                         ['Failed to send some messages', 'SmtpResponseParserException: Unexpected end of stream'])
        self.assertTrue(any(k9_fault_case.PHONE_ERROR in n for n in k9_fault_case.k9_notices(DUMP)))

    def test_screen_reads_only_k9_nodes(self):
        self.assertEqual(k9_fault_case.k9_texts(XML), ['Outbox', 'gx:ABC123'])
        self.assertEqual(k9_reset.find_node(XML, 'account_setup_next_button'), (880, 2092))
        self.assertIsNone(k9_reset.find_node(XML, 'Private person'))

    def test_setup_steps_choose_the_sent_folder_by_config(self):
        sent, nosent = k9_reset.phone_setup_steps(True), k9_reset.phone_setup_steps(False)
        self.assertIn(('tap', 'Sent'), sent)
        self.assertIn(('tap', 'None'), nosent[nosent.index(('tap', 'Sent folder')):])
        self.assertEqual(sent[-1], ('tap', 'Inbox'))
        self.assertIn(('type', 'Port*', '14025'), sent)   # SMTP through the fault proxy port

    def test_collector_counts_valid_trials_and_redo_duplicates(self):
        import collect_device_k9 as col, json, tempfile
        checks = {k: True for k in col.CHECKS}
        with tempfile.TemporaryDirectory() as tmp:
            for name, verdict, copies in (('s01', 'REPRODUCED', 2), ('s02', 'REPRODUCED', 1), ('s03', 'INVALID', None)):
                (Path(tmp) / name).mkdir()
                result = dict(config='sent', verdict=verdict)
                if copies:
                    result.update(checks=checks, audit=dict(action='recompose', server_copies_after_action=copies,
                                                            distinct_message_ids_after_action=copies))
                (Path(tmp) / name / 'RESULT.json').write_text(json.dumps(result))
            rows = [col.row(Path(tmp) / n) for n in ('s01', 's02', 's03')]
        self.assertEqual([r['redo_duplicate'] for r in rows], [True, False, ''])
        self.assertIn('| force-stop | sent | 3 | 2 | 2 | 1/2 |', col.summary(rows))

    def test_phone_reset_needs_the_serial_named(self):
        with patch.dict(os.environ, {'GX_PHYSICAL_SERIAL': 'other'}), self.assertRaises(ValueError):
            k9_reset.reset('adb', 'some-phone', 'sent', Path('.'))

    def test_caldav_copies_count_only_events_carrying_the_nonce(self):
        import caldav_fault_case as cal, tempfile
        with tempfile.TemporaryDirectory() as tmp, patch.object(cal, 'STORE', Path(tmp)):
            folder = Path(tmp) / 'collection-root' / 'alice' / 'cal'
            folder.mkdir(parents=True)
            for name, title in (('a.ics', 'gx:ABC123'), ('b.ics', 'gx:ABC123'), ('c.ics', 'gx:OTHER0')):
                (folder / name).write_text('BEGIN:VEVENT\nSUMMARY:%s\nEND:VEVENT\n' % title, encoding='utf-8')
            self.assertEqual(cal.server_copies('gx:ABC123'), ['a.ics', 'b.ics'])

    def test_lmk_and_doze_refuse_a_phone(self):
        import caldav_fault_case as cal
        with patch('sys.argv', ['x', '--adb', 'adb', '--serial', 'RFCX0', '--fault', 'doze', '--output', 'unused']), \
                self.assertRaises(SystemExit):
            cal.main()


if __name__ == '__main__':
    unittest.main()
