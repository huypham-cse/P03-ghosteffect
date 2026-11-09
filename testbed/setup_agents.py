"""Pinned AndroidWorld source and the Python 3.11.8 agent venv (task B-02).

Clones only what the M3A experiment needs (AndroidWorld, which ships M3A and
T3A) at the commit pinned in androidworld_env.py, verifies a clean checkout,
installs it into runtime/agent-venv with uv, and checks that M3A imports.
Writes runtime/agents/SETUP.json and <output>/RESULT.json. Re-running is safe.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from androidworld_env import ANDROID_WORLD_COMMIT

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = 'https://github.com/google-research/android_world.git'
PYTHON = '3.11.8'


def run(command):
    print('+', ' '.join(map(str, command)), flush=True)
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    vendor = ROOT / 'runtime' / 'vendor' / 'android_world_full'  # path read by capture_androidworld.py and native_episode.py
    venv = ROOT / 'runtime' / 'agent-venv'
    if not vendor.exists():
        run(['git', 'clone', '--quiet', REPO_URL, str(vendor)])
    run(['git', '-C', str(vendor), 'checkout', '--quiet', ANDROID_WORLD_COMMIT])
    head = run(['git', '-C', str(vendor), 'rev-parse', 'HEAD'])
    if head != ANDROID_WORLD_COMMIT:
        raise SystemExit('AndroidWorld checkout is not at the pinned commit')
    if run(['git', '-C', str(vendor), 'status', '--porcelain', '--untracked-files=no']):
        raise SystemExit('pinned AndroidWorld checkout has local changes')
    run(['uv', 'python', 'install', PYTHON])
    if not venv.exists():
        run(['uv', 'venv', '--python', PYTHON, str(venv)])
    python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    run(['uv', 'pip', 'install', '--python', str(python), '-r', str(vendor / 'requirements.txt')])
    run(['uv', 'pip', 'install', '--python', str(python), '--no-deps', '-e', str(vendor)])
    version = run([str(python), '-c', 'import sys, android_world.agents.m3a; print(sys.version.split()[0])'])
    if version != PYTHON:
        raise SystemExit('agent venv runs Python ' + version + ', expected ' + PYTHON)
    receipt = dict(status='READY', python=version, venv=str(venv.relative_to(ROOT)),
                   android_world=dict(url=REPO_URL, commit=head, tracked_source_clean=True),
                   m3a_import='OK', utc_ns=time.time_ns())
    for path in (ROOT / 'runtime' / 'agents' / 'SETUP.json', args.output / 'RESULT.json'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print('READY', json.dumps(receipt))


if __name__ == '__main__':
    main()
