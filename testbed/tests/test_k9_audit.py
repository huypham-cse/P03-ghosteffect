"""B-12 audit table: valid rows, failed trials kept with their reason, run order. SYNTHETIC receipts."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TESTBED = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TESTBED))
from k9_audit_table import COLUMNS, row

VALID = dict(verdict='REPRODUCED', config='nosent', nonce='gx:ABC123', request_id='<x@test.invalid>',
             k9_outbox_before_fault='error|1|Unable to send message', server=dict(copies=1),
             audit=dict(action='recompose', taps=[dict(label='Send'), dict(label='Send and Delete')], window_s=60,
                        smtp_data_after_action=1, server_copies_after_action=2, distinct_message_ids_after_action=2,
                        k9_outbox_after_action='error|1|Unable to send message', action_start_utc_ns=5))


class AuditTable(unittest.TestCase):
    def test_valid_row(self):
        r = row('t04-recompose', VALID, '')
        self.assertEqual((r['valid'], r['action'], r['taps'], r['still_in_outbox_error']), (1, 'recompose', 'Send|Send and Delete', 1))
        self.assertEqual(r['distinct_message_ids_after_action'], 2)

    def test_failed_trials_are_kept_with_a_reason(self):
        invalid = row('t05-sync', dict(verdict='INVALID', config='nosent', reason='reset failed: {}'), '')
        self.assertEqual((invalid['valid'], invalid['action'], invalid['invalid_reason']), (0, 'sync', 'reset failed: {}'))
        crashed = row('t06-none', None, 'Traceback\nurllib.error.HTTPError: HTTP Error 400: Bad Request\n')
        self.assertEqual((crashed['valid'], crashed['invalid_reason']), (0, 'urllib.error.HTTPError: HTTP Error 400: Bad Request'))

    def test_action_must_match_the_trial_name(self):
        with self.assertRaises(AssertionError):
            row('t01-sync', VALID, '')

    def test_csv_keeps_run_order_and_every_trial(self):
        with tempfile.TemporaryDirectory() as temp:
            runs = Path(temp) / 'audit'
            (runs / 't02-recompose').mkdir(parents=True)
            (runs / 't02-recompose' / 'RESULT.json').write_text(json.dumps(VALID), encoding='utf-8')
            (runs / 't01-sync').mkdir()
            (runs / 't01-sync.log').write_text('RuntimeError: focused application window cannot be verified\n', encoding='utf-8')
            out = Path(temp) / 'audit.csv'
            subprocess.run([sys.executable, str(TESTBED / 'k9_audit_table.py'), str(runs), '--output', str(out)],
                           check=True, capture_output=True)
            rows = list(csv.DictReader(out.open(encoding='utf-8')))
            self.assertEqual(tuple(rows[0]), COLUMNS)
            self.assertEqual([(r['trial'], r['valid']) for r in rows], [('t01-sync', '0'), ('t02-recompose', '1')])


if __name__ == '__main__':
    unittest.main()
