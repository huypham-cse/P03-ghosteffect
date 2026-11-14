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
        command = [sys.executable, '-B', str(TESTBED / 'agent_episode.py'), '--framework', args.framework, '--config', config,
                   '--fault', fault, '--phase', phase, '--episode-id', episode_id, '--goal-file', str(args.goal_file),
                   '--tag', tag, '--serving-receipt', str(args.serving_receipt), '--adb', str(args.adb),
                   '--output', str(folder), *extra]
        started = time.monotonic()
        subprocess.run(command)
        print('%s %s %s in %.0f s' % (episode_id, config, tag, time.monotonic() - started), flush=True)
    row = outcome(folder)
    print('  -> %s %s' % (row['outcome'], row['invalid_reason']), flush=True)
    return row


def freeze_problems(freeze, serving_receipt, goal_file, freeze_file=FREEZE):
    """Why scheduled index 1 must not start yet; empty when the freeze is merged and matches what will run."""
    import hashlib
    from make_freeze import CODE, sha
    git = lambda *a: subprocess.run(['git', *a], cwd=TESTBED, capture_output=True, text=True)
    commit = git('log', '-1', '--format=%H', '--', str(freeze_file)).stdout.strip()
    problems = []
    if not commit or git('diff', '--quiet', 'HEAD', '--', str(freeze_file)).returncode:
        problems.append('the freeze is not committed')
    elif git('merge-base', '--is-ancestor', commit, 'origin/main').returncode:
        problems.append('the freeze commit is not in origin/main (merge the freeze PR, then git fetch)')
    problems += ['%s changed since the freeze' % n for n, h in freeze['testbed_code_sha256'].items() if sha(TESTBED / n) != h]
    if hashlib.sha256(goal_file.read_text(encoding='utf-8').strip().encode()).hexdigest() != freeze['task']['goal_sha256']:
        problems.append('task text differs from the freeze')
    if json.loads(serving_receipt.read_text(encoding='utf-8')).get('gpu_profile') != freeze['model']['gpu_profile']:
        problems.append('GPU profile of the serving receipt differs from the freeze')
    return problems


def scheduled(args):
    freeze = json.loads(args.freeze.read_text(encoding='utf-8'))
    if (freeze.get('guard') or {}).get('name', 'none') != args.guard:
        raise SystemExit('--guard does not match the freeze')
    if freeze['agent']['framework'] != args.framework:
        raise SystemExit('--framework does not match the freeze')
    problems = freeze_problems(freeze, args.serving_receipt, args.goal_file, args.freeze)
    if problems:
        raise SystemExit('not starting scheduled episodes: ' + '; '.join(problems))
    common = ['--h-eval', str(freeze['fault']['h_eval_s']), '--max-steps', str(freeze['agent']['max_steps'])]
    valid = 0
    for planned in freeze['order']:
        index = planned['scheduled_index']
        if planned['extra'] and valid >= 10:
            break
        guard = lambda attempt: (['--guard', args.guard, '--user-error', str(planned['user_error'][str(attempt)])]
                                 if freeze.get('guard') else [])
        prefix = ({'ghosteffect': 'g', 'rules': 'r'}.get(args.guard) or ('t' if args.framework == 't3a' else
                  'k' if freeze['fault']['kind'] == 'drop-killagent' else 's'))
        run = lambda attempt, suffix: episode(args, '%s%02d%s' % (prefix, index, suffix),
                                              planned['config'], planned['tags'][str(attempt)], 'scheduled',
                                              freeze['fault']['kind'], common + guard(attempt) +
                                              ['--scheduled-index', str(index), '--attempt', str(attempt)])
        recorded = outcome(args.out / ('%s%02d-r2' % (prefix, index))) is not None   # both attempts from an earlier run
        row = run(1, '')
        if row['invalid_reason'].startswith(MEASUREMENT):
            row = run(2, '-r2')
            if row['invalid_reason'].startswith(MEASUREMENT):
                if not recorded:
                    raise SystemExit('two measurement errors in a row at index %d; find the cause first, then run the '
                                     'same command: the index stays INVALID (one rerun per index) and the run goes on'
                                     % index)
                print('  index %d: both attempts were measurement errors in an earlier run; it stays INVALID' % index,
                      flush=True)
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
    parser.add_argument('--guard', choices=('none', 'ghosteffect', 'rules'), default='none')
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--framework', choices=('m3a', 't3a'), default='m3a')
    parser.add_argument('--fault', choices=('drop-forcestop', 'drop-killagent'), default='drop-forcestop',
                        help='dev episodes of an arm with this fault (scheduled episodes take it from the freeze)')
    args = parser.parse_args()
    args.freeze = args.freeze or {'ghosteffect': TESTBED / 'agent_study_guarded.freeze.json',
                                  'rules': TESTBED / 'agent_study_rules.freeze.json'}.get(args.guard, FREEZE)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.phase == 'scheduled':
        return scheduled(args)
    for k in range(1, args.dev_n + 1):
        tag = 'gx:' + ''.join(secrets.choice('0123456789ABCDEFGHJKMNPQRSTVWXYZ') for _ in range(6))
        if args.guard != 'none':   # guarded dev episodes carry the fault: the guard acts only after it
            episode(args, '%sdev-%02d' % (args.guard[0], k), 'sent' if args.guard == 'rules' or k % 2 == 0 else 'nosent',
                    tag, 'dev', 'drop-forcestop', ['--guard', args.guard, '--user-error', '0'])
        elif args.framework != 'm3a' or args.fault != 'drop-forcestop':   # t3a or kill-only dev: with the fault
            episode(args, '%sdev-%02d' % ('t' if args.framework == 't3a' else 'k', k), 'nosent' if k % 2 else 'sent',
                    tag, 'dev', args.fault)
        else:
            episode(args, 'dev-%02d' % k, 'nosent' if k % 2 else 'sent', tag, 'dev', 'none')


if __name__ == '__main__':
    main()
