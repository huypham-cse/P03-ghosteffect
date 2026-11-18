#!/usr/bin/env python3
"""Reproduce the paper artifact in a fresh workspace without overwriting archives.

CPU/simulation/host measurements only: this does not run Android, agents or a VLM.
All subprocess exits and expected CSVs are checked before rendering, including
REAL4. Planner parallelism is bounded; scientific parameters and RNG stay intact.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
PART_OUTPUTS = {
    'main': ['planner_sim.csv', 'planner_class.csv'],
    'seedvariance': ['planner_seed_variance.csv'],
    'rulesweep': ['planner_rules_sweep.csv'],
    **{'stress%d/6' % i: ['planner_stress.part%d.csv' % i] for i in range(6)},
    'sweep': ['planner_alpha_sweep.csv'], 'user': ['planner_user.csv'],
    'sens': ['planner_sensitivity.csv'], 'ncal': ['planner_ncal.csv'],
    'decomp': ['planner_decomp.csv'], 'share': ['planner_share.csv'],
    'real': ['planner_real.csv'],
    'real4': ['planner_real4_%s.csv' % tag for tag in (
        'match2k', 'match5k', 'matchk9', 'matchk9sent',
        'vet', 'vetk9', 'vetk9sent', 'lag2k', 'lag5k', 'lag10k', 'lag20k',
        'boot10k', 'tail5', 'tail5tied', 'down5', 'down15', 't0down5',
        't0down15', 'netlab', 'netlabkey')],
}
NUMERIC_JOBS = [
    ('sim_sprt.py', ['sprt_validation.csv', 'sprt_asym.csv', 'calibration.csv', 'correlation.csv']),
    ('sim_impossibility.py', ['impossibility.csv', 'bayes_floor.csv', 'cost_policy.csv', 'late_commit.csv', 'lag_wait.csv']),
    ('sim_saga.py', ['saga_alloc.csv', 'saga_mixed.csv']),
    ('sim_nonce.py', ['nonce.csv', 'nonce_before.csv']),
    ('markov_planner.py', ['markov_planner.csv', 'prism_instance_dp.csv']),
    ('real_params.py', ['real/params.csv']),
]


def validate_csv(path):
    """Reject missing, empty, truncated and malformed CSV outputs."""
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames
        if not header or not all(header) or len(set(header)) != len(header):
            raise ValueError('empty or duplicate CSV header: ' + str(path))
        rows = list(reader)
        if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError('empty or malformed CSV: ' + str(path))
    return dict(rows=len(rows), columns=header,
                sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def run_command(command, cwd, log, expected=(), timeout=7200):
    started = time.monotonic()
    print('RUN', log.stem, flush=True)
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT,
                                timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError('%s exited %s; see %s' % (command, result.returncode, log))
    outputs = {str(p.relative_to(cwd)): validate_csv(p) for p in expected}
    print('PASS', log.stem, flush=True)
    return dict(command=command, log=str(log), seconds=time.monotonic() - started, outputs=outputs)


def prepare_workspace(destination):
    destination = Path(destination).resolve()
    for protected in (ROOT / 'artifact', ROOT / 'manuscript', ROOT / 'others'):
        if destination == protected or protected in destination.parents or destination in protected.parents:
            raise ValueError('workspace must be separate from source/archived data: ' + str(destination))
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree(ROOT / 'artifact' / 'scripts', destination / 'artifact' / 'scripts',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    # Fresh aggregate outputs; real/ is the preserved input provenance/corpus.
    shutil.copytree(ROOT / 'artifact' / 'results' / 'real', destination / 'artifact' / 'results' / 'real')
    shutil.copytree(ROOT / 'manuscript', destination / 'manuscript',
                    ignore=shutil.ignore_patterns('generated', 'main.pdf', '*.aux', '*.log', '*.bbl', '*.blg', '*.out'))
    (destination / 'artifact' / 'prism').mkdir()
    (destination / 'logs').mkdir()
    inputs = {p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in destination.rglob('*') if p.is_file()}
    return destination, inputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--jobs', type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument('--timeout', type=float, default=7200, help='hard timeout per subprocess, seconds')
    args = parser.parse_args(argv)
    if args.jobs < 1 or args.timeout <= 0:
        parser.error('jobs and timeout must be positive')
    if os.name != 'posix':
        parser.error('full suite includes POSIX SIGKILL; use Linux/WSL, not native Windows')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination = args.output_dir or ROOT / 'codex' / 'runs' / ('artifact_%s_%s' % (stamp, os.getpid()))
    destination, inputs = prepare_workspace(destination)
    scripts, results = destination / 'artifact' / 'scripts', destination / 'artifact' / 'results'
    manifest = dict(status='RUNNING', kind='artifact-reproduction', created_utc=stamp,
                    workspace=str(destination), source_inputs=inputs, jobs=args.jobs,
                    timeout_seconds=args.timeout, completed=[], errors=[])
    manifest_path = destination / 'RUN.json'

    def save():
        temp = manifest_path.with_suffix('.tmp')
        temp.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        os.replace(temp, manifest_path)

    def run(name, script, expected, *extra):
        return run_command([sys.executable, '-u', str(scripts / script), *extra], destination,
                           destination / 'logs' / (name + '.log'),
                           [results / p for p in expected], args.timeout)

    save()
    try:
        for script, expected in NUMERIC_JOBS:
            manifest['completed'].append(run(Path(script).stem, script, expected))
            save()
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(run, 'planner_' + part.replace('/', '_'), 'planner_sim.py', expected, part): part
                       for part, expected in PART_OUTPUTS.items()}
            for future in as_completed(futures):
                try:
                    manifest['completed'].append(future.result())
                except Exception as exc:
                    manifest['errors'].append('%s: %s' % (futures[future], exc))
                    for pending in futures:
                        pending.cancel()
                save()
        if manifest['errors']:
            raise RuntimeError('planner jobs failed; rendering was not started')
        for script, expected in (('sample_size.py', ['sample_size.csv']), ('bench_ledger.py', ['ledger_bench.csv'])):
            manifest['completed'].append(run(Path(script).stem, script, expected))
            save()
        manifest['completed'].append(run('render', 'render.py', []))
        generated = destination / 'manuscript' / 'generated'
        if not (generated / 'macros.tex').is_file() or not (generated / 'tab_real4.tex').is_file():
            raise RuntimeError('renderer did not publish expected fragments')
        manifest['status'] = 'PASS'
    except BaseException as exc:
        manifest['status'] = 'FAILED'
        manifest['errors'].append(type(exc).__name__ + ': ' + str(exc))
        raise
    finally:
        save()
        print('run manifest:', manifest_path, flush=True)


if __name__ == '__main__':
    main()
