"""Regression checks for the paper's invariants, numerical bounds and failure paths.

Run: python -m unittest discover -s artifact/tests -v
Runtime dependencies stay stdlib-only. The optional SciPy reference test is an
independent numerical cross-check; it is not used by experiment code.
"""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ARTIFACT = Path(__file__).resolve().parents[1]
ROOT = ARTIFACT.parent
sys.path.insert(0, str(ARTIFACT / 'scripts'))
from ge_core import cp_upper_one_sided
from ledger import Ledger
import planner_sim as planner
from sample_size import n_rate, n_zero
import sim_nonce

spec = importlib.util.spec_from_file_location('artifact_runner', ARTIFACT / 'run_all.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'ledger.db'
        self.ledger = Ledger(str(self.path))

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def plan(self, eid='e', nonce='gx:ABC123'):
        self.ledger.plan(eid, 'workflow', 1, 'test.app', 'send', nonce, 'before-digest')

    def test_replan_cannot_erase_commit_or_attempt(self):
        self.plan()
        self.ledger.issue('e')
        self.ledger.settle('e', 'COMMITTED')
        before = self.ledger.db.execute('SELECT * FROM effects').fetchone()
        self.plan()
        self.assertEqual(before, self.ledger.db.execute('SELECT * FROM effects').fetchone())
        with self.assertRaises(ValueError):
            self.ledger.issue('e')

    def test_id_collision_cannot_change_nonce_or_description(self):
        self.plan()
        with self.assertRaises(ValueError):
            self.plan(nonce='gx:DIFF12')
        self.assertEqual('PLANNED', self.ledger.state('e'))

    def test_missing_ids_and_invalid_transitions_fail_without_dangling_transaction(self):
        for operation in (lambda: self.ledger.issue('missing'),
                          lambda: self.ledger.settle('missing', 'COMMITTED')):
            with self.assertRaises(KeyError):
                operation()
            self.assertFalse(self.ledger.db.in_transaction)
        self.plan()
        with self.assertRaises(ValueError):
            self.ledger.settle('e', 'COMMITTED')
        with self.assertRaises(ValueError):
            self.ledger.settle('e', 'ISSUED')
        with self.assertRaises(ValueError):
            self.ledger.plan('', 'w', 0, 'a', 'x', 'gx:ABC123')

    def test_retry_requires_absent_and_preserves_original_origin_nonce_and_digest(self):
        with patch('ledger.time.time', side_effect=[10., 11., 12., 13.]):
            self.plan()
            self.ledger.issue('e')
            self.ledger.settle('e', 'ABSENT')
            self.ledger.issue('e')
        row = self.ledger.db.execute('SELECT nonce,digest,attempt,t_issued,t_updated FROM effects').fetchone()
        self.assertEqual(('gx:ABC123', 'before-digest', 2, 11., 13.), row)

    def test_restart_keeps_ambiguous_pending_and_asked_records(self):
        for eid, state in (('issued', None), ('pending', 'PENDING_MONITOR'), ('asked', 'ASKED')):
            self.plan(eid)
            self.ledger.issue(eid)
            if state:
                self.ledger.settle(eid, state)
        self.ledger.close()
        self.ledger = Ledger(str(self.path))
        self.assertEqual({'issued', 'pending', 'asked'}, set(self.ledger.candidates()))
        self.assertEqual('PENDING', self.ledger.state('pending'))
        for eid in self.ledger.candidates():
            with self.assertRaises(ValueError):
                self.ledger.issue(eid)

    def test_readonly_database_never_authorizes_a_tap(self):
        self.plan()
        self.ledger.db.execute('PRAGMA query_only=ON')
        tapped = False
        with self.assertRaises(sqlite3.OperationalError):
            self.ledger.issue('e')
            tapped = True
        self.assertFalse(tapped)
        self.assertEqual('PLANNED', self.ledger.state('e'))
        self.assertFalse(self.ledger.db.in_transaction)

    def test_two_connections_can_authorize_only_one_dispatch(self):
        self.plan()
        ready = threading.Barrier(2)
        def worker():
            ledger = Ledger(str(self.path))
            try:
                ready.wait(timeout=5)
                try:
                    ledger.issue('e')
                    return 'tap-authorized'
                except ValueError:
                    return 'blocked'
            finally:
                ledger.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: worker(), range(2)))
        self.assertCountEqual(['tap-authorized', 'blocked'], outcomes)
        self.assertEqual(1, self.ledger.db.execute('SELECT attempt FROM effects').fetchone()[0])

    def test_compensation_cannot_reopen_the_original_committed_effect(self):
        self.plan()
        self.ledger.issue('e')
        self.ledger.settle('e', 'COMMITTED')
        self.ledger.settle('e', 'COMPENSATING')
        self.assertIn('e', self.ledger.candidates())
        for state in ('ASKED', 'ABSENT', 'ISSUED'):
            with self.assertRaises(ValueError):
                self.ledger.settle('e', state)
        self.ledger.settle('e', 'COMPENSATED')
        with self.assertRaises(ValueError):
            self.ledger.issue('e')


class SampleSizeTests(unittest.TestCase):
    def test_discontinuous_search_returns_193_instead_of_221(self):
        target, delta = math.sqrt(.005), .01 / 110
        self.assertEqual(193, n_rate(target, delta, .01))
        self.assertGreater(cp_upper_one_sided(2, 192, delta), target)
        self.assertLessEqual(cp_upper_one_sided(2, 193, delta), target)
        self.assertLessEqual(cp_upper_one_sided(2, 200, delta), target)
        self.assertGreater(cp_upper_one_sided(3, 201, delta), target)
        self.assertEqual(200, n_rate(target, delta, .01, lo=200, hi=201))

    def test_zero_event_minimum_and_bounded_failure(self):
        self.assertEqual(4947, n_zero(.002, .00005))
        self.assertEqual(4947, n_rate(.002, .00005, 0))
        self.assertTrue(math.isinf(n_rate(.002, .00005, 0, hi=4946)))
        self.assertTrue(math.isinf(n_rate(.01, .05, .01)))
        for args in ((0, .05), (.1, 0), (.1, 1)):
            with self.assertRaises(ValueError):
                n_zero(*args)

    def test_minimum_against_independent_scipy_exhaustive_reference(self):
        try:
            import numpy as np
            from scipy.stats import binom
        except ImportError:
            self.skipTest('optional independent SciPy reference unavailable')
        ns = np.arange(1, 601)
        for target in (.05, .1, .2):
            for p in (0., .005, .01, .049):
                for delta in (.01, .05):
                    with self.subTest(target=target, p=p, delta=delta):
                        feasible = ns[binom.cdf(np.ceil(p * ns), ns, target) <= delta]
                        expected = int(feasible[0]) if len(feasible) else float('inf')
                        self.assertEqual(expected, n_rate(target, delta, p, lo=1, hi=600))


class PlannerTests(unittest.TestCase):
    def test_asymmetric_calibration_pays_both_budgets_and_all_classes(self):
        for alpha, beta in ((.01, .01), (.01, .001), (.001, .01)):
            for keyed in (False, True):
                deltas = planner.calibration_deltas(alpha, beta, keyed)
                for k, delta in zip((11, 5, 8), deltas):
                    spent = k * (len(planner.CLASSES) if keyed else 1) * delta
                    self.assertLessEqual(spent, min(alpha, beta) * .1 + 1e-16)

    def test_no_effects_are_na_not_zero_error(self):
        out, effects = planner.run(['redo'], seeds=[])
        row = planner.summarize(out, effects, ['redo'])[0]
        for key in ('dup','loss','ask','obs','secs','bg','cdup','cdup_hi','closs','closs_hi','q1','q0'):
            self.assertTrue(math.isnan(row[key]), key)
        self.assertEqual(0, row['n'])

    def test_conditional_asks_count_effects_not_workflows(self):
        policies = ['redo', 'always-ask']
        out, effects = planner.run(policies, seeds=[101], n_per_seed=30, overrides={'user_err': 0.})
        rows = {r['policy']: r for r in planner.summarize(out, effects, policies)}
        for p in policies:
            row, counts = rows[p], effects[p]
            self.assertEqual(row['n1'] + row['n0'], counts['amb'])
            self.assertGreater(row['n1'], 0)
            self.assertGreater(row['n0'], 0)
            self.assertEqual(100. if p == 'always-ask' else 0., row['q1'])
            self.assertEqual(100. if p == 'always-ask' else 0., row['q0'])
        self.assertEqual(0., rows['always-ask']['user_e1'])


class NonceTests(unittest.TestCase):
    def test_fast_threshold_matches_levenshtein_on_exhaustive_edit_cases(self):
        tokens = [''.join(s) for n in range(5) for s in itertools.product('ab', repeat=n)]
        for a in tokens:
            for b in tokens:
                for threshold in (0, 1, 2):
                    self.assertEqual(sim_nonce.ham(a,b) <= threshold,
                                     sim_nonce.within_edit_distance(a,b,threshold), (a,b,threshold))

    def test_seeded_ocr_monte_carlo_is_identical_to_full_distance(self):
        for k,t in ((4,0),(6,1),(8,1)):
            for ec in (.005,.02,.05):
                with patch.object(sim_nonce, 'within_edit_distance', side_effect=lambda a,b,t: sim_nonce.ham(a,b)<=t):
                    reference = sim_nonce.mc(k,t,ec,seed=19,n=40)
                self.assertEqual(reference, sim_nonce.mc(k,t,ec,seed=19,n=40))


class RunnerTests(unittest.TestCase):
    def test_successful_command_records_relative_paths_exit_code_and_output_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            (work / 'logs').mkdir()
            output = work / 'result.csv'
            result = runner.run_command(
                [sys.executable, '-c', "open('result.csv','w').write('n,value\\n1,0\\n')"],
                work, work / 'logs' / 'child.log', [output])
            self.assertEqual(0, result['exit_code'])
            self.assertEqual('logs/child.log', result['log'])
            self.assertEqual(64, len(result['outputs']['result.csv']['sha256']))
            self.assertTrue(all(not str(value).startswith(str(work))
                                for value in result.values() if isinstance(value, str)))

    def test_child_failure_cannot_pass_with_an_old_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            old = work / 'result.csv'
            old.write_text('n,value\n1,0\n', encoding='utf-8')
            with self.assertRaises(RuntimeError):
                runner.run_command([sys.executable, '-c', 'raise SystemExit(7)'], work,
                                   work / 'child.log', [old])

    def test_success_without_required_output_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            with self.assertRaises(FileNotFoundError):
                runner.run_command([sys.executable, '-c', 'pass'], work, work / 'child.log', [work / 'missing.csv'])

    def test_csv_rejects_empty_duplicate_headers_and_truncated_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'result.csv'
            for content in ('', 'n,value\n', 'n,n\n1,2\n', ',value\n1,2\n', 'n,value\n1\n', 'n,value\n1,2,3\n'):
                with self.subTest(content=content):
                    path.write_text(content, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        runner.validate_csv(path)

    def test_workspace_cannot_reuse_results_or_target_source(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileExistsError):
                runner.prepare_workspace(Path(temp))
        with self.assertRaises(ValueError):
            runner.prepare_workspace(ARTIFACT / 'results' / 'bad-workspace')

    def test_real4_job_covers_all_existing_sensitivity_files(self):
        existing = {p.name for p in (ARTIFACT / 'results').glob('planner_real4_*.csv')}
        declared = {'planner_real4_%s.csv' % tag for tag in planner.REAL4}
        self.assertEqual(declared, set(runner.PART_OUTPUTS['real4']))
        self.assertEqual(existing, declared)

    def test_agent_input_hashes_include_only_the_four_agent_corpora(self):
        inputs = {
            'artifact/results/real/agent_guarded/episodes.csv': 'guarded',
            'artifact/results/real/agent_rules/episodes.csv': 'rules',
            'artifact/results/real/agent_t3a/episodes.csv': 't3a',
            'artifact/results/real/agent_killagent/episodes.csv': 'killagent',
            'artifact/results/real/agent/episodes.csv': 'legacy',
            'artifact/results/real/params.csv': 'params',
        }
        selected = runner.agent_input_hashes(inputs)
        self.assertEqual({
            'artifact/results/real/agent_guarded/episodes.csv',
            'artifact/results/real/agent_rules/episodes.csv',
            'artifact/results/real/agent_t3a/episodes.csv',
            'artifact/results/real/agent_killagent/episodes.csv',
        }, set(selected))

    @unittest.skipUnless(os.name == 'posix', 'full runner uses POSIX host-crash semantics')
    def test_parallel_job_failure_records_failed_and_never_renders(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            scripts = work / 'artifact' / 'scripts'
            scripts.mkdir(parents=True)
            (work / 'artifact' / 'results').mkdir()
            (work / 'logs').mkdir()
            (scripts / 'planner_sim.py').write_text('raise SystemExit(19)\n', encoding='utf-8')
            with patch.object(runner, 'prepare_workspace', return_value=(work, {})), \
                 patch.object(runner, 'NUMERIC_JOBS', []), \
                 patch.object(runner, 'PART_OUTPUTS', {'bad': ['missing.csv']}):
                with self.assertRaises(RuntimeError):
                    runner.main(['--output-dir', str(work), '--jobs', '1'])
            manifest = json.loads((work / 'RUN.json').read_text(encoding='utf-8'))
            self.assertEqual('FAILED', manifest['status'])
            self.assertTrue(manifest['errors'])
            self.assertFalse((work / 'manuscript' / 'generated').exists())


class RendererTests(unittest.TestCase):
    def render(self, results, output):
        return subprocess.run([sys.executable, str(ARTIFACT / 'scripts' / 'render.py'),
                               '--results-dir', str(results), '--output-dir', str(output)],
                              text=True, capture_output=True, timeout=60)

    def test_failure_after_partial_generation_preserves_prior_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            inputs, output = work / 'inputs', work / 'generated'
            inputs.mkdir()
            output.mkdir()
            shutil.copy2(ARTIFACT / 'results' / 'sprt_validation.csv', inputs)
            (output / 'macros.tex').write_text('previous valid macros', encoding='utf-8')
            (output / 'old.tex').write_text('previous valid table', encoding='utf-8')
            before = {p.name:p.read_bytes() for p in output.iterdir()}
            result = self.render(inputs, output)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(before, {p.name:p.read_bytes() for p in output.iterdir()})

    def test_success_replaces_stale_tex_preserves_notes_and_renders_real4(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'generated'
            output.mkdir()
            (output / 'stale.tex').write_text('stale', encoding='utf-8')
            (output / 'notes.txt').write_text('keep', encoding='utf-8')
            result = self.render(ARTIFACT / 'results', output)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertFalse((output / 'stale.tex').exists())
            self.assertEqual('keep', (output / 'notes.txt').read_text(encoding='utf-8'))
            self.assertTrue((output / 'macros.tex').is_file())
            real4 = (output / 'tab_real4.tex').read_text(encoding='utf-8')
            self.assertIn('t0down15', real4)
            self.assertIn('tail5tied', real4)
            self.assertIn('not fresh device or agent runs', real4)

    def test_split_macro_ownership_and_deterministic_output(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            outputs = [work / 'first', work / 'second']
            for output in outputs:
                result = self.render(ARTIFACT / 'results', output)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            first = {p.name: p.read_bytes() for p in outputs[0].iterdir()}
            second = {p.name: p.read_bytes() for p in outputs[1].iterdir()}
            self.assertEqual(first, second)
            import re
            seen = set()
            for filename, producer in (('macros.tex', 'render.py'),
                                       ('macros_real.tex', 'render_real.py'),
                                       ('macros_guarantee.tex', 'render_guarantee.py')):
                source = first[filename].decode('utf-8')
                self.assertIn(producer, source.splitlines()[0])
                names = re.findall(r'\\newcommand\{\\(\w+)\}', source)
                self.assertFalse(seen.intersection(names))
                seen.update(names)
                for name in names:
                    if filename == 'macros_real.tex':
                        self.assertTrue(name.startswith(('Real', 'Agent', 'Ledger', 'LabelTrial')), name)
                    elif filename == 'macros.tex':
                        self.assertFalse(name.startswith(('Real', 'Agent', 'Ledger', 'LabelTrial', 'Cert')), name)
            self.assertIn('RsimElemJointAsk', seen)
            self.assertIn('RealElemN', seen)
            self.assertIn('LedgerPfifty', seen)

    def test_measurement_failure_after_simulation_tables_preserves_all_macro_files(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            inputs, output = work / 'inputs', work / 'generated'
            shutil.copytree(ARTIFACT / 'results', inputs)
            result = self.render(inputs, output)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            before = {p.name: p.read_bytes() for p in output.iterdir()}
            (inputs / 'real/campaign2/c2_element_first_visible.csv').unlink()
            result = self.render(inputs, output)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_failed_publication_restores_the_original_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'generated'
            output.mkdir()
            (output / 'macros.tex').write_text('old macros', encoding='utf-8')
            (output / 'notes.txt').write_text('keep', encoding='utf-8')
            before = {p.name:p.read_bytes() for p in output.iterdir()}
            # Inject an OS rename failure after staging completes and the old
            # directory was moved aside. The rollback must restore old bytes.
            code = ('import os,runpy,sys\nfrom pathlib import Path\n'
                    'original=os.replace\nout=Path(sys.argv[2])\n'
                    'def replace(src,dst):\n'
                    '    if Path(dst)==out and Path(src).name=="generated":\n'
                    '        raise OSError("injected publication failure")\n'
                    '    return original(src,dst)\n'
                    'os.replace=replace\nscript=sys.argv[1]\n'
                    'sys.argv=[script,"--results-dir",sys.argv[3],"--output-dir",str(out)]\n'
                    'runpy.run_path(script,run_name="__main__")\n')
            result = subprocess.run([sys.executable, '-c', code, str(ARTIFACT / 'scripts' / 'render.py'),
                                     str(output), str(ARTIFACT / 'results')],
                                    text=True, capture_output=True, timeout=60)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('injected publication failure', result.stderr)
            self.assertEqual(before, {p.name:p.read_bytes() for p in output.iterdir()})


class HostBenchmarkTests(unittest.TestCase):
    def test_violation_is_recorded_and_exits_as_failure(self):
        import bench_ledger
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(bench_ledger.os, 'name', 'posix'), \
                 patch.object(bench_ledger, 'RES', temp), \
                 patch.object(bench_ledger, 'latency', return_value=(.1,.2,100)), \
                 patch.object(bench_ledger, 'crash_trials', return_value=(300,1,1,0)):
                with self.assertRaisesRegex(RuntimeError, 'invariant violated'):
                    bench_ledger.main()
            self.assertTrue((Path(temp) / 'ledger_bench.csv').is_file())

    def test_zero_taps_cannot_pass_as_zero_violations(self):
        import bench_ledger
        with patch.object(bench_ledger.os, 'name', 'posix'), \
             patch.object(bench_ledger, 'latency', return_value=(.1,.2,100)), \
             patch.object(bench_ledger, 'crash_trials', return_value=(300,0,0,0)):
            with self.assertRaisesRegex(RuntimeError, 'no taps'):
                bench_ledger.main()


class ProvenanceTests(unittest.TestCase):
    def test_measured_values_unchanged_but_unverified_k9_action_claim_is_removed(self):
        spec = importlib.util.spec_from_file_location('measured_params', ARTIFACT / 'scripts' / 'real_params.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import csv
        with tempfile.TemporaryDirectory() as temp:
            real = Path(temp) / 'real'
            shutil.copytree(ARTIFACT / 'results' / 'real', real)
            with (real / 'params.csv').open(newline='', encoding='utf-8') as stream:
                before = {r['name']:r['value'] for r in csv.DictReader(stream)}
            with patch.object(module, 'REAL', str(real)), patch.object(module, 'C2', str(real / 'campaign2')):
                module.main()
            with (real / 'params.csv').open(newline='', encoding='utf-8') as stream:
                after = {r['name']:r for r in csv.DictReader(stream)}
            self.assertEqual(before, {k:r['value'] for k,r in after.items()})
            provenance = after['k9_failed_commit']['provenance']
            self.assertIn('Send-messages tap recorded 8/20', provenance)
            self.assertIn('not verified', provenance)
            self.assertNotIn('0 new DATA on Sync or Send-messages, in 20/20', provenance)


class BuildScriptTests(unittest.TestCase):
    def setUp(self):
        candidates = [shutil.which('bash'), 'C:/Program Files/Git/bin/bash.exe']
        self.bash = next((p for p in candidates if p and Path(p).is_file() and
                          ('system32' not in p.lower())), None)
        if not self.bash:
            self.skipTest('POSIX shell/Git Bash unavailable')

    def fixture(self, latex_status=0, bib_status=0, undefined=False):
        temp = tempfile.TemporaryDirectory()
        work = Path(temp.name)
        manuscript, scripts, tools = work / 'manuscript', work / 'artifact' / 'scripts', work / 'tools'
        for directory in (manuscript, scripts, tools):
            directory.mkdir(parents=True)
        shutil.copy2(ROOT / 'manuscript' / 'build.sh', manuscript)
        (scripts / 'render.py').write_text('pass\n', encoding='utf-8')
        log = 'LaTeX Warning: Citation x undefined.' if undefined else 'Output written on main.pdf'
        for name, status in (('pdflatex', latex_status), ('bibtex', bib_status)):
            script = '#!/bin/sh\necho '+name+' >> "$CALL_LOG"\n'
            if name == 'pdflatex':
                script += "printf 'fixture PDF' > main.pdf\nprintf '%s\\n' '" + log + "' > main.log\n"
            script += 'exit %s\n' % status
            path = tools / name
            path.write_text(script, encoding='utf-8', newline='\n')
            path.chmod(0o755)
        env = os.environ.copy()
        env.update(PATH=str(tools) + os.pathsep + env.get('PATH',''),
                   PYTHON=sys.executable, CALL_LOG=str(work / 'calls'))
        return temp, work, manuscript / 'build.sh', env

    def run_fixture(self, **kwargs):
        temp, work, script, env = self.fixture(**kwargs)
        try:
            result = subprocess.run([self.bash, script.as_posix()], cwd=work, env=env,
                                    text=True, capture_output=True, timeout=30)
            calls = (work / 'calls').read_text(encoding='utf-8').splitlines() if (work / 'calls').exists() else []
            return result, calls
        finally:
            temp.cleanup()

    def test_first_latex_failure_stops_before_bibtex(self):
        result, calls = self.run_fixture(latex_status=17)
        self.assertEqual(17, result.returncode, result.stdout + result.stderr)
        self.assertEqual(['pdflatex'], calls)

    def test_bibtex_failure_stops_remaining_latex_passes(self):
        result, calls = self.run_fixture(bib_status=23)
        self.assertEqual(23, result.returncode, result.stdout + result.stderr)
        self.assertEqual(['pdflatex','bibtex'], calls)

    def test_final_undefined_reference_is_not_a_successful_build(self):
        result, calls = self.run_fixture(undefined=True)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual(['pdflatex','bibtex','pdflatex','pdflatex'], calls)

    def test_clean_build_path_runs_all_passes(self):
        result, calls = self.run_fixture()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(['pdflatex','bibtex','pdflatex','pdflatex'], calls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
