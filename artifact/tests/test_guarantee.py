"""Part A tests: certification and calibration guarantees (A-01 and later)."""

import hashlib
import inspect
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ARTIFACT = Path(__file__).resolve().parents[1]
RESULTS = ARTIFACT / 'results'
RENDERER = ARTIFACT / 'scripts' / 'render_guarantee.py'
sys.path.insert(0, str(ARTIFACT / 'scripts'))
import planner_sim as planner
import render_guarantee as rg


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




# ------------------------------------------------------------------ render_guarantee.py (YC-A4, YC-A9)
INPUTS = (['planner_real.csv', 'planner_sim.csv', 'real/params.csv']
          + [f'planner_real4_{t}.csv' for t, _ in rg.CLOCK_ROWS + rg.TIED_ROWS + rg.TAIL_ROWS + rg.APP_ROWS])


def _copy_inputs(dst, skip=None):
    for name in INPUTS:
        if name != skip:
            (dst / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RESULTS / name, dst / name)


def _run(results, output):
    return subprocess.run([sys.executable, str(RENDERER), '--results-dir', str(results), '--output-dir', str(output)],
                          capture_output=True, text=True, timeout=120)


def _digest(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(folder).iterdir())}


class RenderGuaranteeTests(unittest.TestCase):

    def test_parameters_match_the_simulator(self):
        self.assertEqual(rg.N_CLASSES, len(planner.CLASSES))
        self.assertEqual((rg.K_PRODUCT, rg.K_JOINT), (planner.K_PRODUCT, planner.K_JOINT))
        self.assertEqual(rg.N_LAG, planner.N_LAG)
        defaults = inspect.signature(planner.run).parameters
        self.assertEqual(rg.ALPHA_PCT / 100, defaults['alpha'].default)
        self.assertEqual(rg.BETA_PCT / 100, defaults['beta'].default)
        d_prod, d_joint, _ = planner.calibration_deltas(rg.ALPHA_PCT / 100, rg.BETA_PCT / 100, keyed=True)
        self.assertAlmostEqual(rg.delta(rg.K_PRODUCT), d_prod)
        self.assertAlmostEqual(rg.delta(rg.K_JOINT), d_joint)

    def test_two_runs_are_byte_identical_and_write_only_part_a_files(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / 'a', Path(t) / 'b'
            self.assertEqual(0, _run(RESULTS, a).returncode)
            self.assertEqual(0, _run(RESULTS, b).returncode)
            self.assertEqual(_digest(a), _digest(b))
            for name in _digest(a):
                self.assertTrue(name == 'macros_guarantee.tex' or name.startswith('tab_cert_'), name)

    def test_missing_csv_fails_and_keeps_old_outputs(self):
        with tempfile.TemporaryDirectory() as t:
            results, out = Path(t) / 'results', Path(t) / 'generated'
            out.mkdir()
            (out / 'macros_guarantee.tex').write_text('old', encoding='utf-8')
            for skip in ('planner_real4_tail5tied.csv', 'real/params.csv', 'planner_sim.csv'):
                shutil.rmtree(results, ignore_errors=True)
                _copy_inputs(results, skip=skip)
                result = _run(results, out)
                self.assertNotEqual(0, result.returncode, skip)
                self.assertIn('missing input CSV', result.stderr)
                self.assertEqual(['macros_guarantee.tex'], [p.name for p in out.iterdir()])
                self.assertEqual('old', (out / 'macros_guarantee.tex').read_text(encoding='utf-8'))

    def test_values_follow_the_csvs(self):
        files = rg.render(RESULTS)
        macros = dict(re.findall(r'\\newcommand\{\\(\w+)\}\{(.*)\\xspace\}', files['macros_guarantee.tex']))
        self.assertEqual(105, len(macros))
        row = next(r for r in rg.read_csv(RESULTS, 'planner_real4_t0down5.csv') if r['policy'] == 'ghost')
        self.assertEqual(rg.cert_f2(row['cdup']), macros['CertClockTzeroDownFiveProdPv'])
        self.assertEqual(rg.cert_f2(row['cdup_hi']), macros['CertClockTzeroDownFiveProdPvHi'])
        # Composed bound by hand from the Element product row: alpha + (ask1/n1) * user_e1.
        r = next(r for r in rg.read_csv(RESULTS, 'planner_real.csv') if r['tag'] == 'main' and r['policy'] == 'ghost')
        by_hand = rg.ALPHA_PCT + 100 * float(r['ask1']) / float(r['n1']) * float(r['user_e1']) / 100
        self.assertEqual(rg.cert_f2(by_hand), macros['CertBoundElemProdDup'])
        # Over-budget labels agree with the CP bound against alpha.
        for name, value in macros.items():
            if name.endswith('Over'):
                over = float(macros[name[:-4] + 'PvHi']) > rg.ALPHA_PCT
                self.assertEqual('over budget' if over else 'within budget', value)
        self.assertEqual({'CertLabelMedS', 'CertDeviceHoursFive'} if not (RESULTS / 'real/agent/label_cost.csv').exists()
                         else set(), {k for k, v in macros.items() if v == '??'})

    def test_label_cost_gives_device_hours(self):
        with tempfile.TemporaryDirectory() as t:
            results = Path(t)
            _copy_inputs(results)
            (results / 'real/agent').mkdir(parents=True)
            (results / 'real/agent/label_cost.csv').write_text(
                'component,n,min_s,median_s,max_s\ntotal,10,90,120,300\n', encoding='utf-8')
            files = rg.render(results)
        text = files['macros_guarantee.tex']
        self.assertIn(r'\newcommand{\CertLabelMedS}{120\xspace}', text)
        # 5,000 labels x 4 classes x 2 outcomes x 120 s = 1,333.3 h
        self.assertIn(r'\newcommand{\CertDeviceHoursFive}{1{,}333\xspace}', text)
        self.assertNotIn('??', text)

    def test_zero_denominators_print_na(self):
        nobody = dict(n1='0', ask1='0', user_e1='nan', n0='0', ask0='0', user_e0='nan')
        q, eps, bound = rg.composed_bound(nobody, 1, 'fixture')
        self.assertEqual(['N/A'] * 3, [rg.cert_f2(q), rg.cert_f2(eps), rg.cert_f2(bound)])
        never_asked = dict(n1='50', ask1='0', user_e1='nan')
        q, eps, bound = rg.composed_bound(never_asked, 1, 'fixture')
        self.assertEqual(('0.00', 'N/A', rg.cert_f2(rg.ALPHA_PCT)), (rg.cert_f2(q), rg.cert_f2(eps), rg.cert_f2(bound)))
        with self.assertRaises(rg.InputError):
            rg.composed_bound(dict(n1='50', ask1='5', user_e1=''), 1, 'fixture')


if __name__ == '__main__':
    unittest.main()
