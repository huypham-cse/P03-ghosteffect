"""ghost_guard.py on SYNTHETIC UI elements: issue before the commit tap, reopen, ask, settle. No AVD or model."""
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from faultproxy import Journal
from ghost_guard import Guard, simulated_user, capture


def element(text='', desc='', box=(0, 0, 100, 100)):
    return NS(text=text, content_description=desc, resource_name='',
              bbox_pixels=NS(x_min=box[0], y_min=box[1], x_max=box[2], y_max=box[3]))


SCREEN = [element(desc='Send', box=(900, 100, 1000, 200)), element(text='Subject', box=(0, 300, 1080, 400))]
DIALOG = [element(text='Cancel', box=(0, 1300, 500, 1400)), element(text='Send and Delete', box=(600, 1300, 1080, 1400))]


class GhostGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.guard = Guard(self.tmp, 'g01', 'goal', Journal(self.tmp / 'guard.jsonl'))
        self.addCleanup(self.guard.close)

    def test_only_the_send_tap_issues_and_the_dialog_is_the_same_effect(self):
        self.assertIsNone(self.guard.before(NS(action_type='input_text', index=1), SCREEN, 'phase1'))
        self.assertFalse(self.guard.before(NS(action_type='click', index=1), SCREEN, 'phase1')['commit_candidate'])
        self.assertIsNone(self.guard.controller.ledger.state(self.guard.effect))
        self.assertEqual(self.guard.before(NS(action_type='click', index=0), SCREEN, 'phase1')['ledger'], 'issued')
        self.assertEqual(self.guard.before(NS(action_type='click', index=1), DIALOG, 'phase1')['ledger'], 'same_effect')
        self.assertEqual(self.guard.controller.ledger.state(self.guard.effect), 'ISSUED')

    def test_delivered_answer_settles_committed_after_reopening(self):
        self.guard.before(NS(action_type='click', index=0), SCREEN, 'phase1')
        record = self.guard.restart(lambda: simulated_user(True, 0))
        self.assertEqual((record['decision'], record['answer'], record['state']), ('ASK', 'delivered', 'COMMITTED'))
        with self.assertRaises(RuntimeError):   # a later commit tap on a committed effect is refused
            self.guard.before(NS(action_type='click', index=0), SCREEN, 'phase2')

    def test_wrong_answer_permits_a_retry(self):
        self.guard.before(NS(action_type='click', index=0), SCREEN, 'phase1')
        record = self.guard.restart(lambda: simulated_user(True, 1))
        self.assertEqual((record['answer'], record['state']), ('not_delivered', 'ABSENT'))
        self.assertEqual(self.guard.before(NS(action_type='click', index=0), SCREEN, 'phase2')['ledger'], 'issued')

    def test_missed_tap_leaves_no_candidate(self):
        self.assertEqual(self.guard.restart(lambda: self.fail('no ask without a candidate'))['decision'], 'NO_CANDIDATE')

    def test_pixel_click_and_enter(self):
        action, xml = capture(SCREEN, NS(action_type='click', index=None, x=950, y=150))
        self.assertIn('content-desc="Send"', xml)
        self.assertEqual(capture(SCREEN, NS(action_type='keyboard_enter', index=None))[0]['action_type'], 'keyboard_enter')

    def test_simulated_user(self):
        self.assertEqual([simulated_user(t, e) for t in (True, False) for e in (0, 1)], [True, False, False, True])


if __name__ == '__main__':
    unittest.main()
