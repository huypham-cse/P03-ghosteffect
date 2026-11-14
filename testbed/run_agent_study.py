"""Run the A-dev (B-07) or A-native (B-09) episodes back to back, so the GPU never waits for typing.

  python testbed/run_agent_study.py --phase dev --serving-receipt testbed/runs/SERVING.json --adb <adb>
  python testbed/run_agent_study.py --phase scheduled --serving-receipt testbed/runs/SERVING.json --adb <adb>

dev: dev-01 to dev-NN, no fault, configs alternate, fresh tags. scheduled: follows the committed freeze
(testbed/agent_study.freeze.json): indices 1 to 20, attempt 2 only after a measurement error, extra
indices 21 to 30 only while fewer than 10 are valid. Episodes already in --out are skipped, so the
command can be run again after an interruption. Each episode is one agent_episode.py process.
The endpoint must answer as the receipt says before each episode, and two measurement errors in a row
stop the run. Scheduled index 1 starts only once the freeze is merged into origin/main and matches the
live code, task and GPU profile.
"""
import argparse
import json
from pathlib import Path
import secrets
import subprocess
import sys
import time

TESTBED = Path(__file__).resolve().parent
FREEZE = TESTBED / 'agent_study.freeze.json'
MEASUREMENT = ('measurement_error:', 'grading_failed:', 'harness_timeout')
ENDPOINT = 'http://127.0.0.1:8101/v1'


def outcome(folder):
    for name in ('RESULT.json', 'TIMEOUT.json'):
        if (folder / name).is_file():
            return json.loads((folder / name).read_text(encoding='utf-8'))['row']
    return None


def episode(args, episode_id, config, tag, phase, fault, extra=()):
    folder = args.out / episode_id
    if outcome(folder) is None:
        from native_episode import serving_contract
        try:   # a dead tunnel stops the run here instead of spending the attempts of the next indices
            serving_contract(args.serving_receipt, ENDPOINT)
        except Exception as exc:
            raise SystemExit('model endpoint not ready (%s: %s); reopen the tunnel, then run the same command'
                             % (type(exc).__name__, exc))
        if folder.exists():
            raise SystemExit('%s exists without a result; move it aside and note it in b-log' % folder)
        command = [sys.executable, '-B', str(TESTBED / 'agent_episode.py'), '--framework', 'm3a', '--config', config,
                   '--fault', fault, '--phase', phase, '--episode-id', episode_id, '--goal-file', str(args.goal_file),
                   '--tag', tag, '--serving-receipt', str(args.serving_receipt), '--adb', str(args.adb),
                   '--output', str(folder), *extra]
        started = time.monotonic()
        subprocess.run(command)
        print('%s %s %s in %.0f s' % (episode_id, config, tag, time.monotonic() - started), flush=True)
    row = outcome(folder)
    print('  -> %s %s' % (row['outcome'], row['invalid_reason']), flush=True)
    return row


def freeze_problems(freeze, serving_receipt, goal_file):
    """Why scheduled index 1 must not start yet; empty when the freeze is merged and matches what will run."""
    import hashlib
    from make_freeze import CODE, sha
    git = lambda *a: subprocess.run(['git', *a], cwd=TESTBED, capture_output=True, text=True)
    commit = git('log', '-1', '--format=%H', '--', str(FREEZE)).stdout.strip()
    problems = []
    if not commit or git('diff', '--quiet', 'HEAD', '--', str(FREEZE)).returncode:
        problems.append('the freeze is not committed')
    elif git('merge-base', '--is-ancestor', commit, 'origin/main').returncode:
        problems.append('the freeze commit is not in origin/main (merge the freeze PR, then git fetch)')
    problems += ['%s changed since the freeze' % n for n in CODE if sha(TESTBED / n) != freeze['testbed_code_sha256'][n]]
    if hashlib.sha256(goal_file.read_text(encoding='utf-8').strip().encode()).hexdigest() != freeze['task']['goal_sha256']:
        problems.append('task text differs from the freeze')
    if json.loads(serving_receipt.read_text(encoding='utf-8')).get('gpu_profile') != freeze['model']['gpu_profile']:
        problems.append('GPU profile of the serving receipt differs from the freeze')
    return problems


def scheduled(args):
    freeze = json.loads(FREEZE.read_text(encoding='utf-8'))
    problems = freeze_problems(freeze, args.serving_receipt, args.goal_file)
    if problems:
        raise SystemExit('not starting scheduled episodes: ' + '; '.join(problems))
    common = ['--h-eval', str(freeze['fault']['h_eval_s']), '--max-steps', str(freeze['agent']['max_steps'])]
    valid = 0
    for planned in freeze['order']:
        index = planned['scheduled_index']
        if planned['extra'] and valid >= 10:
            break
        run = lambda attempt, suffix: episode(args, 's%02d%s' % (index, suffix), planned['config'],
                                              planned['tags'][str(attempt)], 'scheduled', 'drop-forcestop',
                                              common + ['--scheduled-index', str(index), '--attempt', str(attempt)])
        row = run(1, '')
        if row['invalid_reason'].startswith(MEASUREMENT):
            row = run(2, '-r2')
            if row['invalid_reason'].startswith(MEASUREMENT):
                raise SystemExit('two measurement errors in a row at index %d; find the cause first' % index)
        valid += row['outcome'] != 'INVALID'
        print('  valid so far: %d' % valid, flush=True)
    print('scheduled done: %d valid' % valid)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--phase', choices=('dev', 'scheduled'), required=True)
    parser.add_argument('--serving-receipt', type=Path, required=True)
    parser.add_argument('--goal-file', type=Path, default=TESTBED / 'agent_goal.txt')
    parser.add_argument('--adb', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=TESTBED / 'runs' / 'agent')
    parser.add_argument('--dev-n', type=int, default=10)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.phase == 'scheduled':
        return scheduled(args)
    for k in range(1, args.dev_n + 1):
        tag = 'gx:' + ''.join(secrets.choice('0123456789ABCDEFGHJKMNPQRSTVWXYZ') for _ in range(6))
        episode(args, 'dev-%02d' % k, 'nosent' if k % 2 else 'sent', tag, 'dev', 'none')


if __name__ == '__main__':
    main()
