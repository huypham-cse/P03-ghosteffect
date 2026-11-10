"""Part A tests: certification and calibration guarantees (A-01 and later)."""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ARTIFACT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ARTIFACT / 'scripts'))
import planner_sim as planner


def _early_reads(clock, downtime=15.0, n_per_seed=150):
    """Run product and joint certification on the measured Element profile with `downtime` seconds between ISSUED
    and the class's observable origin r_e.  For every effect the planner retried on its own (concluded absent),
    return how many end-to-end reads happened before r_e + w, where w is the certified wait of that effect.

    Times are converted to "seconds since r_e" the same way the simulator's visibility oracle does: for agent death
    r_e = t0 = recovery start - downtime, for every other class r_e = recovery start."""
    ov = planner.real_overrides()
    if not ov:
        raise unittest.SkipTest('no artifact/results/real/params.csv')
    ov.pop('elem_tail_ub', None)
    waits, reads, result = {}, {}, {}
    active = []
    lag_wait, e2e_state, resolve_v2 = planner.lag_wait, planner.e2e_state, planner.resolve_v2

    # The same effect objects are resolved by every policy, so records are keyed by (policy, effect).
    def rec_wait(lagx, A, e, share, delta):
        w = lag_wait(lagx, A, e, share, delta)
        if active:
            waits.setdefault((active[-1], id(e)), []).append(w)
        return w

    def rec_state(e, t):
        if active:
            since_r = t + e['down'] if (e.get('down') and e.get('fault') == 'agent-kill') else t
            reads.setdefault((active[-1], id(e)), []).append(since_r)
        return e2e_state(e, t)

    def rec_resolve(policy, e, *args):
        active.append(policy)
        try:
            out = resolve_v2(policy, e, *args)
        finally:
            active.pop()
        result[(policy, id(e))] = out[0]
        return out

    with patch.object(planner, 'lag_wait', rec_wait), patch.object(planner, 'e2e_state', rec_state), \
            patch.object(planner, 'resolve_v2', rec_resolve):
        planner.run(['ghost', 'ghost-joint'], seeds=[101], n_per_seed=n_per_seed,
                    overrides=dict(ov, catalog='measured', only_app='element', cal_pop='fault', keyed='all',
                                   downtime=downtime, clock=clock))
    early = checked = 0
    for k, retried in result.items():
        if retried is not True or k not in waits or k not in reads:
            continue
        checked += 1
        early += sum(t < min(waits[k]) - 1e-9 for t in reads[k])
    return early, checked


class AnchorTests(unittest.TestCase):
    """YC-A1: the planner does not conclude "absent" from end-to-end reads before r_e + w."""

    def test_no_absent_conclusion_before_origin_plus_wait(self):
        early, checked = _early_reads('origin')
        self.assertGreater(checked, 0, 'no retried effect with a certified wait was exercised')
        self.assertEqual(0, early)

    def test_waiting_from_issued_reads_too_early(self):
        # Control: waiting from ISSUED for every class (the wrong anchor of the t0down rows) must be caught.
        early, checked = _early_reads('t0')
        self.assertGreater(checked, 0)
        self.assertGreater(early, 0)


if __name__ == '__main__':
    unittest.main()
