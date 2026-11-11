"""C-owned checks for the shared submission tools (no Android required)."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('readability', ROOT / 'team/readability_count.py')
readability = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readability)
SHELL = shutil.which('sh')
if not SHELL and os.name == 'nt':
    program_files = os.environ.get('ProgramFiles')
    candidate = Path(program_files or (os.environ.get('SystemDrive', 'C:') + '/Program Files')) / 'Git/bin/sh.exe'
    if candidate.is_file():
        SHELL = str(candidate)


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
