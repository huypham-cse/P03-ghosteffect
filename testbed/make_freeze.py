"""Write testbed/agent_study.freeze.json (B-08) before the first scheduled A-native episode.

Pins what YC-B3 lists: model and revision, serving and decoding, the native M3A source (prompt
hash), task, APK/AVD/K-9 copy hashes, H_eval, outcome rule, and the episode order with one tag per
attempt, drawn here once. Commit and merge the file before scheduled index 1 runs; check_agent_data.py
compares every scheduled receipt with it.

Order (B-09): indices 1 to 20 alternate nosent, sent; 21 to 30 are used only if fewer than 10 of
1 to 20 are valid, in order, and stop once 10 are valid or 30 is reached. Attempt 2 of an index runs
only after a measurement error (invalid_reason measurement_error:*, grading_failed:*, harness_timeout).
"""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import secrets
import subprocess
import sys
import time

TESTBED = Path(__file__).resolve().parent
ROOT = TESTBED.parent
CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
CODE = ('agent_episode.py', 'androidworld_env.py', 'faultproxy.py', 'k9_reset.py', 'local_model.py',
        'native_episode.py', 'serve_model.py', 'ui.py', 'ghost_guard.py', 'controller.py', 'classifier.py')
RULES = __doc__[__doc__.index('Order (B-09)'):].strip()
USER_ERROR_RATE = 0.05   # the paper's simulation: the user answers an ask wrongly 5% of the time
GUARD = dict(
    name='ghosteffect', module='testbed/ghost_guard.py on testbed/controller.py and testbed/classifier.py',
    commit='classifier.py English lexicon on the element the action targets; the effect is ISSUED in the host '
           'SQLite ledger (WAL, synchronous=FULL) before the native tap',
    recovery='after the kill and relaunch the ledger is reopened; K-9 has no runtime certificate, so recover() asks',
    user='simulated: answers from GreenMail whether the mail arrived, wrong exactly on the attempts with user_error 1',
    delivered='COMMITTED; the step is done and the agent is not restarted',
    not_delivered='ABSENT; retry permitted and the agent restarts as in the baseline',
    no_candidate='the classifier missed the commit tap; the agent restarts unguarded and the miss stays in the data',
    baseline='agent_study.freeze.json, scheduled s01 to s20: same task, fault, model, decoding, configs and outcome rule',
    user_error_rate=USER_ERROR_RATE)
RULES_ARM = dict(
    name='rules', module='testbed/ghost_guard.py Rules on testbed/controller.py and testbed/classifier.py',
    commit=GUARD['commit'],
    recovery="the paper's same-evidence rule cascade (RQ3; planner_sim.resolve_rules): hop 1 is K-9's Outbox listing "
             "(not G2, so no vote), a fixed 10 s wait, then the end-to-end family, K-9's Sent list; read exactly from "
             "K-9's database, an upper bound on a perception-based reader",
    decision='mail in the Sent list: COMMITTED, agent not restarted; absent: every family absent, ABSENT, the agent '
             'restarts (retry); no reading: ask the simulated user as in the guarded arm',
    configs='sent only: without a Sent folder the only end-to-end family is the VLM, which has no real reader here',
    baseline=GUARD['baseline'], guarded='agent_study_guarded.freeze.json, scheduled g01 to g20',
    user_error_rate=USER_ERROR_RATE)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tags(n, draw=None):
    draw = draw or (lambda: 'gx:' + ''.join(secrets.choice(CROCKFORD) for _ in range(6)))
    out = []
    while len(out) < n:
        tag = draw()
        if tag not in out:
            out.append(tag)
    return out


def build(serving, native_source, goal_bytes, archives, avd_config_sha256, host, h_eval=300, max_steps=20, draw=None,
          guard=None, error_draw=None, framework='m3a', fault='drop-forcestop'):
    """Pure part: every input is passed in, so tests can build a freeze without a device or server."""
    from agent_episode import classify, OUTCOMES, FIELDS, ERROR_WAIT_S
    assets = {a['file']: a['sha256'] for a in json.loads((TESTBED / 'assets.lock.json').read_text())['assets']}
    pool = iter(tags(60, draw))
    order = [dict(scheduled_index=i, config='sent' if guard == 'rules' else 'nosent' if i % 2 else 'sent', extra=i > 20,
                  tags={'1': next(pool), '2': next(pool)}) for i in range(1, 31)]
    if guard:
        error_draw = error_draw or (lambda: int(secrets.randbelow(10 ** 6) < USER_ERROR_RATE * 10 ** 6))
        for planned in order:
            planned['user_error'] = {'1': error_draw(), '2': error_draw()}
    return dict(guard={'ghosteffect': GUARD, 'rules': RULES_ARM, True: GUARD}.get(guard),
        kind='A-native freeze (B-08); written by testbed/make_freeze.py', created_utc_ns=time.time_ns(),
        model=dict(repo_id=serving['repo_id'], revision=serving['revision'], dtype=serving['dtype'],
                   engine='vLLM ' + serving['engine_version'], max_model_len=serving['max_model_len'],
                   image_policy=serving['image_policy'], history_policy=serving['history_policy'],
                   gpu_profile=serving['gpu_profile'], gpu_memory_utilization=serving['gpu_memory_utilization'],
                   max_num_seqs=serving['max_num_seqs']),
        decoding=dict(temperature=0, top_p=1, n=1, max_tokens=2048, server_seed=0, generation_config='vllm'),
        agent=dict(framework=framework, native_source=native_source, max_steps=max_steps,
                   output_alias='action name "type" -> "input_text" in local_model.py (lead decision 14/11, '
                                'after dev-01); prompt, history and reflection unchanged'),
        task=dict(goal=goal_bytes.decode('utf-8').strip(),
                  goal_sha256=hashlib.sha256(goal_bytes.decode('utf-8').strip().encode()).hexdigest(),
                  tag_rule='{tag} in the goal is replaced by the attempt tag below'),
        apps=dict(k9_apk_sha256=assets['com.fsck.k9_39046.apk'], greenmail_jar_sha256=assets['greenmail.jar'],
                  k9_clean_copy_sha256=archives,
                  avd_config_sha256=avd_config_sha256),
        fault=dict(kind=fault, order='reply dropped, K-9 records the error, force-stop, relaunch' if fault == 'drop-forcestop'
                   else 'reply dropped, K-9 records the error, the agent is killed and restarted; K-9 keeps running',
                   error_wait_s=ERROR_WAIT_S, h_eval_s=h_eval),
        outcome_rule=dict(outcomes=list(OUTCOMES), classify_sha256=hashlib.sha256(
            inspect.getsource(classify).encode()).hexdigest(), episodes_csv_fields=list(FIELDS)),
        testbed_code_sha256={name: sha(TESTBED / name) for name in CODE},
        host=host, rules=RULES, order=order)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--serving-receipt', type=Path, required=True, help='SERVING.json of the real engine')
    parser.add_argument('--goal-file', type=Path, required=True)
    parser.add_argument('--host', required=True, help='model host and AVD host, without identifying details')
    parser.add_argument('--adb', type=Path, required=True)
    parser.add_argument('--adb-server-port', default='5038')
    parser.add_argument('--serial', default='emulator-5580')
    parser.add_argument('--guard', choices=('ghosteffect', 'rules'), help='guarded arm and drawn simulated-user errors')
    parser.add_argument('--framework', choices=('m3a', 't3a'), default='m3a')
    parser.add_argument('--fault', choices=('drop-forcestop', 'drop-killagent'), default='drop-forcestop')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    args.output = args.output or TESTBED / {'ghosteffect': 'agent_study_guarded.freeze.json',
                                            'rules': 'agent_study_rules.freeze.json'}.get(args.guard) or (
        'agent_study_t3a.freeze.json' if args.framework == 't3a' else 'agent_study_killagent.freeze.json'
        if args.fault == 'drop-killagent' else 'agent_study.freeze.json')
    sys.path.insert(0, str(TESTBED))
    from androidworld_env import verify_source
    serving = json.loads(args.serving_receipt.read_text(encoding='utf-8'))
    if serving.get('synthetic') or serving.get('status') != 'MODEL_SERVING_READY':
        raise SystemExit('freeze needs the receipt of the real, ready engine')
    listing = subprocess.run([str(args.adb), '-P', args.adb_server_port, '-s', args.serial, 'shell',
                              'sha256sum /data/local/tmp/ghosteffect/k9-sent.tar /data/local/tmp/ghosteffect/k9-nosent.tar'],
                             capture_output=True, text=True, timeout=60, check=True).stdout.split()
    archives = {'sent': listing[0], 'nosent': listing[2]}
    if args.output.exists():
        raise SystemExit('%s exists; a freeze is written once' % args.output)
    freeze = build(serving, verify_source(ROOT / 'runtime/vendor/android_world_full'),
                   args.goal_file.read_bytes(), archives,
                   sha(ROOT / 'runtime/android-avd/ghosteffect_api33_x86_local.avd/config.ini'), args.host,
                   guard=args.guard, framework=args.framework, fault=args.fault)
    args.output.write_text(json.dumps(freeze, indent=2) + '\n', encoding='utf-8')
    print('wrote', args.output, 'sha256', sha(args.output))


if __name__ == '__main__':
    main()
