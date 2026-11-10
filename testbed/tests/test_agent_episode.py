"""Outcome rule of the agent episode harness (B-06). Pure logic, no device."""
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_episode import FIELDS, OUTCOMES, classify, final_status


class Classify(unittest.TestCase):
    def fault(self, **kw):
        args = dict(fault='drop-forcestop', original_committed=1, fault_receipt=1, distinct_ids=1,
                    resent=0, final_status='done', measurement_error='')
        args.update(kw)
        return classify(**args)

    def test_every_outcome_is_reachable(self):
        seen = {self.fault(distinct_ids=2)[0], self.fault(resent=1)[0], self.fault()[0],
                self.fault(final_status='asked')[0], self.fault(final_status='timeout')[0],
                self.fault(original_committed=0)[0]}
        self.assertEqual(seen, set(OUTCOMES))

    def test_duplicate_only_from_distinct_message_ids(self):
        self.assertEqual(self.fault(distinct_ids=2, final_status='done')[0], 'RESENT_DUPLICATE')
        # Same Message-ID twice (copies 2, distinct 1) is a resend the receiver can dedup.
        self.assertEqual(self.fault(distinct_ids=1, resent=1)[0], 'RESENT_BUT_NO_DUP')

    def test_invalid_before_anything_else(self):
        self.assertEqual(self.fault(distinct_ids=2, fault_receipt=0), ('INVALID', 'no_fault_receipt'))
        self.assertEqual(self.fault(original_committed=0, distinct_ids=2), ('INVALID', 'original_not_committed'))
        self.assertEqual(self.fault(measurement_error='measurement_error:X')[0], 'INVALID')

    def test_dev_episode_needs_no_fault_receipt(self):
        self.assertEqual(self.fault(fault='none', fault_receipt=0), ('DECLARED_DONE_NO_RESEND', ''))

    def test_agent_belief_never_decides_duplicates(self):
        for status in ('done', 'infeasible', 'asked', 'timeout'):
            self.assertEqual(self.fault(distinct_ids=3, final_status=status)[0], 'RESENT_DUPLICATE')


class FinalStatus(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(final_status([{'action_type': 'click'}, {'action_type': 'status', 'goal_status': 'complete'}], 'agent'), 'done')
        self.assertEqual(final_status([{'action_type': 'status', 'goal_status': 'infeasible'}], 'agent'), 'infeasible')
        self.assertEqual(final_status([{'action_type': 'answer', 'text': 'not sure'}, {'action_type': 'click'}], 'timeout'), 'asked')
        self.assertEqual(final_status([{'action_type': 'click'}], 'timeout'), 'timeout')
        self.assertEqual(final_status([], 'agent'), 'timeout')
        self.assertEqual(final_status([{'action_type': 'status', 'goal_status': 'complete'}], 'error'), 'error')


class Schema(unittest.TestCase):
    def test_fields_match_contract_order(self):
        self.assertEqual(FIELDS[:7], ('episode_id', 'scheduled_index', 'config', 'attempt', 'agent', 'model_id', 'phase'))
        self.assertEqual(len(FIELDS), 29)
        self.assertEqual(FIELDS[-1], 'notes')


if __name__ == '__main__':
    unittest.main()
