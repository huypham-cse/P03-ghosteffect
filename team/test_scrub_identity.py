"""Team-only test that scrub_check.sh flags team member names and the team account.

Kept under team/, which make_bundle.sh leaves out of the anonymous artifact, so the shipped artifact tests name no
team member or account. Run from the repository root: python -m unittest team/test_scrub_identity.py
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SHELL = shutil.which('sh')
if not SHELL and os.name == 'nt':
    for candidate in (Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Git' / 'bin' / 'sh.exe',):
        if candidate.exists():
            SHELL = str(candidate)


@unittest.skipUnless(SHELL, 'POSIX shell or Git Bash required')
class TeamIdentityScrubTests(unittest.TestCase):
    def test_flags_team_names_and_account_without_echoing_them(self):
        cases = ['Bá ' + 'Nguyên', 'Gia ' + 'Huy', 'Trung ' + 'Nguyên', 'nguyennguyen938' + '-debug']
        env = dict(os.environ, PYTHON=sys.executable)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture.txt'
            for content in cases:
                with self.subTest(content=content):
                    path.write_text(content, encoding='utf-8')
                    result = subprocess.run([SHELL, str(ROOT / 'team/scrub_check.sh'), str(path)],
                                            capture_output=True, text=True, env=env)
                    self.assertEqual(1, result.returncode, result.stderr)
                    self.assertNotIn(content, result.stdout)


if __name__ == '__main__':
    unittest.main()
