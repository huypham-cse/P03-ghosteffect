"""C-owned checks for the shared submission tools (no Android required)."""
import importlib.util
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import random

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('readability', ROOT / 'team/readability_count.py')
readability = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readability)
sys.path.insert(0, str(ROOT / 'artifact/scripts'))
import planner_sim as planner
SHELL = shutil.which('sh')
if not SHELL and os.name == 'nt':
    program_files = os.environ.get('ProgramFiles')
    candidate = Path(program_files or (os.environ.get('SystemDrive', 'C:') + '/Program Files')) / 'Git/bin/sh.exe'
    if candidate.is_file():
        SHELL = str(candidate)


class MatchedInputTests(unittest.TestCase):
    def scenario(self, app='element'):
        values = dict(planner.real_overrides(), catalog='measured', only_app=app,
                      cal_pop='fault', ncal_scale=.025, nlag=64, matched_inputs=True)
        if app == 'element':
            values['keyed'] = 'all'
        result = planner.scen('default')
        result.update(values)
        return result, values

    def test_shared_records_produce_the_unchanged_joint_calibration(self):
        for app in ('element', 'k9', 'k9sent'):
            with self.subTest(app=app):
                scenario, _ = self.scenario(app)
                eps, _ = planner.app_errors(random.Random(101), scenario)
                delta = planner.calibration_deltas(.01, .01, scenario.get('keyed') == 'all')[1]
                reference = planner.calibrate(random.Random(3138), eps, scenario, delta, 'joint')
                labels = planner.matched_labels(random.Random(3138), eps, scenario)
                self.assertEqual(reference, planner.joint_from_matched(labels, scenario, delta))

    def test_run_passes_identical_records_and_lag_object_to_both_policies(self):
        _, overrides = self.scenario()
        with patch.object(planner, 'cal_effects', wraps=planner.cal_effects) as effects, \
             patch.object(planner, 'matched_labels', wraps=planner.matched_labels) as labels, \
             patch.object(planner, 'joint_calibration', wraps=planner.joint_calibration) as joint, \
             patch.object(planner, 'lag_tables', wraps=planner.lag_tables) as lags, \
             patch.object(planner, 'vetting', wraps=planner.vetting) as vetted, \
             patch.object(planner, 'resolve_v2', wraps=planner.resolve_v2) as resolve:
            planner.run(['rules-vetted', 'ghost-joint'], seeds=[101], n_per_seed=8, overrides=overrides)
        self.assertEqual(1, labels.call_count)
        self.assertEqual(1, lags.call_count)
        shared = vetted.call_args.kwargs['labels']
        self.assertEqual(2 * sum(len(per) for per in shared.values()), effects.call_count)
        shared_lags = vetted.call_args.kwargs['lagx']
        self.assertIsNotNone(shared_lags)
        self.assertTrue(resolve.call_count)
        self.assertTrue(all(call.args[6] is shared_lags for call in resolve.call_args_list))
        all_labels = [pair for per in shared.values() for pair in per.values()]
        self.assertEqual(len(all_labels), joint.call_count)
        for call, (e1, e0) in zip(joint.call_args_list, all_labels):
            self.assertIs(call.args[2], e1)
            self.assertIs(call.args[3], e0)

    def test_new_tags_use_equal_explicit_budgets_and_all_profiles(self):
        for tag, app, budget in (('match2k', 'element', 2000), ('match5k', 'element', 5000),
                                 ('matchk9', 'k9', 2000), ('matchk9sent', 'k9sent', 2000)):
            actual_app, extra, policies = planner.REAL4[tag]
            self.assertEqual(app, actual_app)
            self.assertEqual(budget, extra['nlag'])
            self.assertEqual(budget, round(planner.NCAL * extra.get('ncal_scale', 1)))
            self.assertTrue(extra['matched_inputs'])
            self.assertEqual(['rules-vetted', 'ghost-joint'], policies)

    def test_mismatched_shared_input_is_rejected(self):
        scenario, _ = self.scenario()
        with self.assertRaises(ValueError):
            planner.vetting(random.Random(1), {}, scenario, 'rules-vetted', labels={})
        with self.assertRaises(ValueError):
            planner.vetting(random.Random(1), {}, scenario, 'rules-vetted-small', labels={}, lagx={})

    def test_renderer_rejects_unequal_budgets_and_keeps_published_output(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            inputs, output = work / 'results', work / 'generated'
            shutil.copytree(ROOT / 'artifact/results', inputs)
            source = inputs / 'planner_real4_match2k.csv'
            with source.open(newline='') as stream:
                reader = csv.DictReader(stream)
                header, rows = reader.fieldnames, list(reader)
            rows[1]['nlag'] = str(int(rows[0]['nlag']) + 1)
            with source.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
                writer.writerows(rows)
            output.mkdir()
            published = output / 'macros.tex'
            published.write_bytes(b'previously reviewed output')
            result = subprocess.run([sys.executable, str(ROOT / 'artifact/scripts/render.py'),
                                     '--results-dir', str(inputs), '--output-dir', str(output)],
                                    text=True, capture_output=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('matched input metadata disagree', result.stderr)
            self.assertEqual(b'previously reviewed output', published.read_bytes())
            self.assertEqual([published], list(output.iterdir()))


class SeedVarianceMetadataTests(unittest.TestCase):
    def test_metadata_has_reproducibility_provenance(self):
        metadata = json.loads((ROOT / 'artifact/results/planner_seed_variance.meta.json').read_text(encoding='utf-8'))
        for key in ('command', 'git_commit', 'seed', 'python_version', 'date', 'host',
                    'csv_sha256', 'script_sha256', 'cases'):
            self.assertIn(key, metadata)
        self.assertEqual(64, len(metadata['csv_sha256']))
        self.assertEqual(64, len(metadata['script_sha256']))


class ReadabilityTests(unittest.TestCase):
    def count(self, source):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'sample.tex'
            path.write_text(source, encoding='utf-8')
            return readability.count_file(path)

    def test_detects_long_sentence_but_not_comments_or_math(self):
        report = self.count('% ' + 'comment ' * 80 + '\n'
                            + '$' + 'math ' * 80 + '$.\n\n'
                            + 'word ' * 46 + '.\n\n' + 'word ' * 45 + '.')
        self.assertEqual([46], [r['words'] for r in report['long_sentences']])

    def test_counts_commands_and_semicolons_separately_for_each_para(self):
        report = self.count(r'\para{First} One; two.' + '\n'
                            + r'\para{Second} Three; four; five. \emph{A}. % \emph{B}')
        self.assertEqual(2, report['para'])
        self.assertEqual(1, report['emph'])
        self.assertEqual([2], [r['count'] for r in report['semicolon_paragraphs']])

    def test_abbreviations_and_decimal_do_not_split_long_sentence(self):
        report = self.count('Fig. 2 shows 12.7 and e.g. ' + 'word ' * 45 + '.')
        self.assertEqual(1, len(report['long_sentences']))

    def test_strict_scope_limit_is_combined_across_files(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = []
            for name in ('a.tex', 'b.tex'):
                path = Path(temp) / name
                path.write_text('\\para{Short} Text.\n\n' * 3, encoding='utf-8')
                paths.append(str(path))
            command = [sys.executable, str(ROOT / 'team/readability_count.py'), '--json', '--strict']
            result = subprocess.run(command + paths, capture_output=True, text=True)
            self.assertEqual(1, result.returncode)
            self.assertEqual(6, json.loads(result.stdout)['totals']['para'])
            result = subprocess.run(command + ['--scope', 'paper'] + paths, capture_output=True, text=True)
            self.assertEqual(0, result.returncode)


@unittest.skipUnless(SHELL, 'POSIX shell or Git Bash required')
class ScrubTests(unittest.TestCase):
    def run_scrub(self, path):
        env = dict(os.environ, PYTHON=sys.executable)
        return subprocess.run([SHELL, str(ROOT / 'team/scrub_check.sh'), str(path)],
                              capture_output=True, text=True, env=env)

    def test_clean_input_passes_and_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'clean.txt'
            path.write_text('Anonymous artifact. https://developer.android.com/docs. Synthetic test data.', encoding='utf-8')
            self.assertEqual(0, self.run_scrub(path).returncode)
            self.assertEqual(2, self.run_scrub(path.with_name('missing.txt')).returncode)

    def test_reserved_test_domains_are_not_identity_findings(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixtures.txt'
            path.write_text('alice@test.invalid\nbob@ghost.local\n', encoding='utf-8')
            self.assertEqual(0, self.run_scrub(path).returncode)

    def test_flags_identity_paths_and_keys_without_echoing_secret(self):
        cases = ['/' + 'Users/abc/private', 'C:' + chr(92) + 'Users' + chr(92) + 'abc',
                 'D:' + chr(92) + 'work', 'Bá ' + 'Nguyên', 'Gia ' + 'Huy', 'Trung ' + 'Nguyên',
                 'nguyennguyen938' + '-debug', 'author' + '@' + 'private.example',
                 'sk-' + 'Z' * 24, 'hf_' + 'X' * 24]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture.txt'
            for content in cases:
                with self.subTest(content=content):
                    path.write_text(content, encoding='utf-8')
                    result = self.run_scrub(path)
                    self.assertEqual(1, result.returncode, result.stderr)
                    self.assertNotIn(content, result.stdout)

    def test_recurses_and_rejects_forbidden_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'sub').mkdir()
            (root / 'sub/.env').write_text('harmless=value', encoding='utf-8')
            self.assertEqual(1, self.run_scrub(root).returncode)


if __name__ == '__main__':
    unittest.main()
