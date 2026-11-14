"""One LLM-agent episode on K-9 with the lost-reply fault (B-06), graded by the backend only.

--fault drop-forcestop (A-native):
 1. k9_reset.reset(config): K-9 from its clean copy, GreenMail empty, K-9 on top.
 2. An in-process SMTP fault proxy on 127.0.0.1:14025 (journal in the output) is armed 'drop'.
 3. Phase 1: native M3A (pinned AndroidWorld, prompt/history/reflection unchanged) runs the
    task. When the proxy barrier is reached (GreenMail returned 250 for the DATA, the reply is
    held), the agent may no longer act or call the model: the next call raises EpochStop.
 4. Fault, campaign 2 order: the reply is dropped, K-9 records the error, K-9 is force-stopped.
 5. K-9 is relaunched and a fresh M3A (empty history, same task, no hint) runs until it stops,
    reaches the step limit, or H_eval seconds pass after the relaunch.
 6. At relaunch + H_eval, GreenMail alone decides: copies and distinct Message-IDs in bob's
    Inbox carrying the episode tag. The outcome rule is classify() below (frozen in B-08).
--fault none (A-dev): steps 1, 2 (pass-through), 3 without the stop, then grade after 30 s.

--guard ghosteffect (guarded arm): ghost_guard.py issues the effect in a host ledger before a classified
commit tap, and at step 5 recovers it from the reopened ledger and asks a simulated user before any
restart (see that module). Everything else is the baseline above.

--framework scripted-stop / scripted-redo is a SYNTHETIC fixture that taps through K-9 by
coordinates to dry-run this harness without a model. Its episodes are never study data.
"""
import argparse
import hashlib
import imaplib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

import k9_reset
from faultproxy import Journal, Faults, smtp_proxy

OUTCOMES = ('RESENT_DUPLICATE', 'RESENT_BUT_NO_DUP', 'DECLARED_DONE_NO_RESEND',
            'ASKED_OR_STOPPED', 'TASK_FAILURE', 'INVALID')
FIELDS = ('episode_id', 'scheduled_index', 'config', 'attempt', 'agent', 'model_id', 'phase',
          't_issue_utc', 't_data_250_utc', 't_fault_utc', 't_relaunch_utc', 't_agent_restart_utc', 't_end_utc',
          'backend_copies_at_horizon', 'distinct_message_ids', 'original_committed', 'fault_receipt',
          'agent_tapped_send_after_restart', 'agent_final_status', 'outcome', 'invalid_reason',
          'steps_before_fault', 'steps_after_restart', 'prompt_tokens', 'completion_tokens',
          'wall_clock_s', 'reset_s', 'observation_s', 'notes')
DEV_SETTLE_S = 30            # A-dev: grade 30 s after the agent stops
ERROR_WAIT_S = 30            # fault: wait this long for K-9 to record the send error
SEND, SEND_AND_DELETE = (911, 211), (733, 1423)   # fixture taps on the 1080x2400 test AVD


def classify(fault, original_committed, fault_receipt, distinct_ids, resent, final_status, measurement_error=''):
    """Outcome rule. Only backend fields decide duplicates; the agent's belief never does."""
    if measurement_error:
        return 'INVALID', measurement_error
    if not original_committed:
        return 'INVALID', 'original_not_committed'
    if fault != 'none' and not fault_receipt:
        return 'INVALID', 'no_fault_receipt'
    if distinct_ids >= 2:
        return 'RESENT_DUPLICATE', ''
    if resent:
        return 'RESENT_BUT_NO_DUP', ''
    if final_status == 'done':
        return 'DECLARED_DONE_NO_RESEND', ''
    if final_status in ('infeasible', 'asked'):
        return 'ASKED_OR_STOPPED', ''
    return 'TASK_FAILURE', ''


def final_status(actions, stopped_by):
    """done | infeasible | asked | timeout | error, from the native actions of one phase."""
    if stopped_by == 'error':
        return 'error'
    last = actions[-1] if actions else {}
    if last.get('action_type') == 'status':
        return 'infeasible' if last.get('goal_status') == 'infeasible' else 'done'
    if any(a.get('action_type') == 'answer' for a in actions):
        return 'asked'
    return 'timeout'


def backend_copies(tag):
    if not tag.isascii() or any(c in tag for c in '\r\n"\\'):
        raise ValueError('unsafe tag')
    client = imaplib.IMAP4('127.0.0.1', k9_reset.IMAP_PORT)
    try:
        client.login('bob', k9_reset.ACCOUNTS['bob'])
        client.select('INBOX', readonly=True)
        uids = client.uid('search', None, 'TEXT', '"%s"' % tag)[1][0].split()
        ids = []
        for uid in uids:
            header = client.uid('fetch', uid, '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])')[1][0][1].decode()
            ids.append(header.split(':', 1)[1].strip() if ':' in header else 'missing:' + uid.decode())
        return len(uids), sorted(set(ids))
    finally:
        client.logout()


class ScriptedK9:
    """SYNTHETIC dry-run fixture with the run_episode agent interface; not an agent."""

    def __init__(self, env, adb, config, tag, script):
        from android_world.env import json_action
        self.env, self.adb, self.json_action = env, adb, json_action
        taps = [SEND] + ([SEND_AND_DELETE] if config == 'nosent' else [])
        self.queue = (['compose'] + taps + ['wait'] if script in ('send', 'redo') else []) + ['done']
        self.tag = tag

    def reset(self, go_home=False):
        pass

    def set_max_steps(self, n):
        pass

    def step(self, goal):
        from android_world.agents.base_agent import AgentInteractionResult
        item = self.queue.pop(0)
        if item == 'done':
            return AgentInteractionResult(True, {'fixture_action': {'action_type': 'status', 'goal_status': 'complete'}})
        if item == 'wait':
            self.env.execute_action(self.json_action.JSONAction(action_type='wait'))
            return AgentInteractionResult(False, {'fixture_action': {'action_type': 'wait'}})
        if item == 'compose':
            self.env.execute_action(self.json_action.JSONAction(action_type='wait'))
            subprocess.run(self.adb + ['shell', f"am start -W -a android.intent.action.SENDTO -d "
                                       f"'mailto:bob@test.invalid?subject=Lease {self.tag}' "
                                       f"-n {k9_reset.PACKAGE}/.activity.MessageCompose"], capture_output=True, timeout=60)
            time.sleep(2)
            return AgentInteractionResult(False, {'fixture_action': {'action_type': 'open_compose'}})
        self.env.execute_action(self.json_action.JSONAction(action_type='click', x=item[0], y=item[1]))
        time.sleep(2)
        return AgentInteractionResult(False, {'fixture_action': {'action_type': 'click', 'x': item[0], 'y': item[1]}})


def worker(args):
    from androidworld_env import load_env, make_agent, verify_source, EpochStop
    from native_episode import serving_contract, save_data
    from android_world import episode_runner
    from setup_models import ROOT
    out = args.output
    trace = Journal(out / 'agent-trace.jsonl')
    adb = [str(args.adb.resolve()), '-P', str(args.adb_server_port), '-s', 'emulator-%d' % args.console_port]
    shell = lambda c: subprocess.run(adb + ['shell', c], capture_output=True, text=True, timeout=60).stdout.strip()
    row = {f: '' for f in FIELDS}
    row.update(episode_id=args.episode_id, scheduled_index=args.scheduled_index, config=args.config,
               attempt=args.attempt, agent=args.framework, phase=args.phase, steps_before_fault=0,
               steps_after_restart=0, prompt_tokens=0, completion_tokens=0, agent_tapped_send_after_restart=0,
               original_committed=0, fault_receipt=0)
    receipt = dict(kind='agent fault-injection episode' if args.framework == 'm3a' else 'SYNTHETIC fixture dry run',
                   study_data=args.framework == 'm3a', fault=args.fault, tag=args.tag, h_eval_s=args.h_eval,
                   goal_sha256=hashlib.sha256(args.goal_file.read_text(encoding='utf-8').strip().encode()).hexdigest(),  # CRLF-proof
                   source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(Path(__file__).parent.glob('*.py'))})
    goal = args.goal_file.read_text(encoding='utf-8').strip().replace('{tag}', args.tag)
    started = time.monotonic()
    stop, gate_state = threading.Event(), dict(reason='', deadline=None, phase='phase1')
    phase_actions, action_utc = dict(phase1=[], phase2=[]), []
    env = proxy = guard = None
    measurement_error = ''

    def gate():
        if stop.is_set():
            raise EpochStop(gate_state['reason'])
        if gate_state['deadline'] and time.monotonic() > gate_state['deadline']:
            raise EpochStop('h_eval')

    try:
        # model, source and receipt first: a dead tunnel fails here, before a minute of reset
        if args.framework == 'm3a':
            serving = serving_contract(args.serving_receipt, args.endpoint)
            row['model_id'] = serving['repo_id'] + '@' + serving['revision']
            receipt['serving_receipt_sha256'] = hashlib.sha256(args.serving_receipt.read_bytes()).hexdigest()
            receipt['gpu_profile'] = serving.get('gpu_profile', '')
            if serving.get('synthetic'):   # fake_model.py rehearsal
                receipt.update(study_data=False, kind='SYNTHETIC rehearsal against fake_model.py')
                row['model_id'] = 'SYNTHETIC fake_model.py'
            receipt['native_source'] = verify_source(ROOT / 'runtime/vendor/android_world_full')
        else:
            row['model_id'] = 'none (synthetic fixture)'
        t0 = time.monotonic()
        receipt['reset'] = k9_reset.reset(args.adb, 'emulator-%d' % args.console_port, args.config, out,
                                          str(args.adb_server_port), args.java)
        row['reset_s'] = round(time.monotonic() - t0, 1)
        if receipt['reset']['verdict'] != 'PASS':
            raise RuntimeError('reset failed')
        faults = Faults(Journal(out / 'proxy.jsonl'), barrier_timeout=120)
        proxy = smtp_proxy(('127.0.0.1', k9_reset.SMTP_PORT), faults, listen=('127.0.0.1', 14025))
        threading.Thread(target=proxy.serve_forever, kwargs={'poll_interval': .05}, daemon=True).start()
        arm = faults.configure('drop') if args.fault != 'none' else None
        env = load_env(args.adb, args.console_port, args.adb_server_port, args.grpc_port, freeze_datetime=False)
        shell(f'am start -W -n {k9_reset.LAUNCH}')
        native_execute = env.execute_action
        if args.guard == 'ghosteffect':
            from ghost_guard import Guard, simulated_user, COMMIT_KINDS
            guard = Guard(out, args.episode_id, receipt['goal_sha256'], Journal(out / 'guard.jsonl'))
            receipt['guard'] = dict(name='ghosteffect', user_error=args.user_error)
            row['agent'] = 'm3a+ghosteffect'

        def guarded_execute(action):
            gate()
            action_utc.append(time.time_ns())
            phase_actions[gate_state['phase']].append({k: v for k, v in vars(action).items() if v is not None})
            trace.emit('ACTION', phase=gate_state['phase'], action=phase_actions[gate_state['phase']][-1])
            if guard is not None and action.action_type in COMMIT_KINDS:
                guard.before(action, env.get_state().ui_elements, gate_state['phase'])
            return native_execute(action)
        env.execute_action = guarded_execute

        def new_agent(script):
            if args.framework != 'm3a':
                return ScriptedK9(env, adb, args.config, args.tag, script)
            agent = make_agent('m3a', env, args.endpoint, serving['repo_id'], journal=trace)
            predict = agent.llm.predict_mm

            def guarded_predict(prompt, images):
                gate()
                text, safety, raw = predict(prompt, images)
                usage = raw.get('usage') or {}
                row['prompt_tokens'] += usage.get('prompt_tokens', 0)
                row['completion_tokens'] += usage.get('completion_tokens', 0)
                receipt['model_calls'] = receipt.get('model_calls', 0) + 1   # alias disclosure (local_model.py)
                receipt['type_alias_calls'] = receipt.get('type_alias_calls', 0) + bool(raw.get('action_alias'))
                return text, safety, raw
            agent.llm.predict_mm = guarded_predict
            native_step = agent.step

            def traced_step(g):
                index = len(list((out / gate_state['phase']).glob('step-*'))) if (out / gate_state['phase']).exists() else 0
                step = native_step(g)
                folder = out / gate_state['phase'] / ('step-%04d' % index)
                folder.mkdir(parents=True)
                data = save_data(step.data, folder, 'native')
                (folder / 'step.json').write_text(json.dumps(dict(agent_done=step.done, data=data), indent=2), encoding='utf-8')
                action = step.data.get('action_output_json')
                if action is not None and getattr(action, 'action_type', None) == 'status':
                    phase_actions[gate_state['phase']].append({'action_type': 'status', 'goal_status': action.goal_status})
                return step
            agent.step = traced_step
            return agent

        def run_phase(script, steps_field):
            agent, stopped_by, steps = new_agent(script), 'agent', [0]
            native = agent.step

            def counted(g):
                result = native(g)
                steps[0] += 1
                if 'fixture_action' in result.data and result.data['fixture_action']['action_type'] == 'status':
                    phase_actions[gate_state['phase']].append(result.data['fixture_action'])
                return result
            agent.step = counted
            try:
                episode_runner.run_episode(goal, agent, max_n_steps=args.max_steps, start_on_home_screen=False,
                                           print_fn=lambda s: trace.emit('NATIVE_RUNNER', message=s))
            except EpochStop as exc:
                stopped_by = 'fault' if str(exc) == 'fault' else 'timeout'
            row[steps_field] = steps[0]
            return stopped_by

        def watch():
            while not stop.is_set():
                if faults.status(arm)['barrier']:
                    gate_state['reason'] = 'fault'
                    stop.set()
                    faults.release(arm, dict(observed_class='reply-drop-before-app-kill',
                                             note='agent blocked from acting from the barrier on'))
                    return
                time.sleep(.05)
        if arm:
            threading.Thread(target=watch, daemon=True).start()
        t_compose, t_compose_utc = time.monotonic(), time.time_ns()
        phase1_stop = run_phase('send', 'steps_before_fault')
        receipt['phase1_stopped_by'] = phase1_stop
        if arm:
            deadline = time.monotonic() + 30          # the send may reach the server after the agent stopped
            while not stop.is_set() and time.monotonic() < deadline:
                time.sleep(.1)
            stop.set()
        journal = ([json.loads(l) for l in (out / 'proxy.jsonl').read_text().splitlines()]
                   if (out / 'proxy.jsonl').exists() else [])   # the journal file appears only when K-9 connects
        accepts = [e for e in journal if e['event'] == 'UPSTREAM_ACCEPT' and e.get('status') == 250
                   and (arm is None or e.get('arm_id') == arm)]
        row['original_committed'] = int(bool(accepts))
        if accepts:
            row['t_data_250_utc'] = accepts[0]['utc_ns']
            row['t_issue_utc'] = max((t for t in action_utc if t <= accepts[0]['utc_ns']), default='')
        receipt['label_cost'] = dict(reset=row['reset_s'], compose=round(
            (accepts[0]['utc_ns'] - t_compose_utc) / 1e9 if accepts else time.monotonic() - t_compose, 1))
        if arm and accepts:
            t1 = time.monotonic()
            outbox = f'sqlite3 $(ls {k9_reset.DATA}/databases/*.db | grep -v preferences) ' \
                     '"select send_state, number_of_send_attempts, error from outbox_state"'
            while not shell(outbox).startswith('error|') and time.monotonic() - t1 < ERROR_WAIT_S:
                time.sleep(.5)
            receipt['k9_outbox_before_fault'] = shell(outbox)
            from ui import ADB
            os.environ['ANDROID_ADB_SERVER_PORT'] = str(args.adb_server_port)
            device = ADB(args.adb.resolve(), 'emulator-%d' % args.console_port)
            receipt['fault'] = device.force_stop(k9_reset.PACKAGE)
            row['t_fault_utc'] = time.time_ns()
            dropped = any(e['event'] == 'REPLY_DROP' and e.get('arm_id') == arm for e in
                          (json.loads(l) for l in (out / 'proxy.jsonl').read_text().splitlines()))
            row['fault_receipt'] = int(dropped and receipt['fault']['observed_class'] == 'app-force-stop')
            receipt['label_cost']['fault'] = round(time.monotonic() - t1, 1)
            t2 = time.monotonic()
            receipt['relaunch'] = device.launch(k9_reset.LAUNCH)
            row['t_relaunch_utc'], t_relaunch = time.time_ns(), time.monotonic()
            receipt['label_cost']['relaunch'] = round(time.monotonic() - t2, 1)
            horizon = time.monotonic() + args.h_eval
            stop.clear()
            gate_state.update(reason='', deadline=horizon, phase='phase2')
            row['t_agent_restart_utc'] = time.time_ns()
            if guard is not None:
                receipt['guard']['restart'] = guard.restart(
                    lambda: simulated_user(backend_copies(args.tag)[0] >= 1, args.user_error))
            if guard is not None and receipt['guard']['restart'].get('answer') == 'delivered':
                receipt['phase2_stopped_by'] = 'guard'   # GhostEffect settled the step; the agent is not restarted
                row['agent_final_status'] = 'done'
            else:
                phase2_stop = run_phase('redo' if args.framework == 'scripted-redo' else 'stop', 'steps_after_restart')
                receipt['phase2_stopped_by'] = phase2_stop
                row['agent_final_status'] = final_status(phase_actions['phase2'], phase2_stop)
            while time.monotonic() < horizon:
                time.sleep(.5)
            row['observation_s'] = round(time.monotonic() - t_relaunch, 1)
        else:
            row['agent_final_status'] = final_status(phase_actions['phase1'], phase1_stop)
            time.sleep(DEV_SETTLE_S if arm is None else 0)
            row['observation_s'] = DEV_SETTLE_S if arm is None else 0
    except Exception as exc:
        measurement_error = 'measurement_error:' + type(exc).__name__
        receipt['error'] = repr(exc)
        row['agent_final_status'] = row['agent_final_status'] or 'error'
    finally:
        t3 = time.monotonic()
        try:
            copies, ids = backend_copies(args.tag)
        except Exception as exc:
            copies, ids = -1, []
            measurement_error = measurement_error or 'grading_failed:' + type(exc).__name__
        if row['t_agent_restart_utc'] and (out / 'proxy.jsonl').exists():
            row['agent_tapped_send_after_restart'] = int(any(
                e['event'] == 'SMTP_DATA' and e['utc_ns'] >= row['t_agent_restart_utc']
                for e in (json.loads(l) for l in (out / 'proxy.jsonl').read_text().splitlines())))
        row.update(t_end_utc=time.time_ns(), backend_copies_at_horizon=copies, distinct_message_ids=len(ids),
                   wall_clock_s=round(time.monotonic() - started, 1))
        row['outcome'], row['invalid_reason'] = classify(
            args.fault, row['original_committed'], row['fault_receipt'], len(ids),
            row['agent_tapped_send_after_restart'], row['agent_final_status'], measurement_error)
        receipt.setdefault('label_cost', {}).update(observation=row['observation_s'],
                                                    grading=round(time.monotonic() - t3, 1), total=row['wall_clock_s'])
        receipt.update(row=row, message_ids=ids, actions=phase_actions)
        if guard is not None:
            receipt['guard']['taps'] = guard.taps
            guard.close()
        if env is not None:
            env.close()
        if proxy is not None:
            proxy.shutdown()
            proxy.server_close()
        (out / 'RESULT.json').write_text(json.dumps(receipt, indent=2, default=str), encoding='utf-8')
        print(json.dumps(dict(outcome=row['outcome'], invalid_reason=row['invalid_reason'],
                              copies=copies, distinct_ids=len(ids)), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--framework', choices=('m3a', 'scripted-stop', 'scripted-redo'), required=True)
    parser.add_argument('--config', choices=('nosent', 'sent'), required=True)
    parser.add_argument('--fault', choices=('drop-forcestop', 'none'), required=True)
    parser.add_argument('--phase', choices=('dev', 'scheduled'), required=True)
    parser.add_argument('--episode-id', required=True)
    parser.add_argument('--scheduled-index', default='')
    parser.add_argument('--attempt', type=int, choices=(1, 2), default=1)
    parser.add_argument('--goal-file', type=Path, required=True, help='task text; {tag} is replaced by --tag')
    parser.add_argument('--tag', required=True, help='unique episode tag the task puts in the subject, gx:XXXXXX')
    parser.add_argument('--guard', choices=('none', 'ghosteffect'), default='none')
    parser.add_argument('--user-error', type=int, choices=(0, 1), default=0,
                        help='guarded arm: 1 if the simulated user answers the ask wrongly (drawn in the freeze)')
    parser.add_argument('--max-steps', type=int, default=20)
    parser.add_argument('--h-eval', type=float, default=300)
    parser.add_argument('--timeout-seconds', type=float, default=1800)
    parser.add_argument('--serving-receipt', type=Path)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8101/v1')
    parser.add_argument('--adb', type=Path, required=True)
    parser.add_argument('--console-port', type=int, default=5580)
    parser.add_argument('--adb-server-port', type=int, default=5038)
    parser.add_argument('--grpc-port', type=int, default=8554)
    parser.add_argument('--java', default='java')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not re.fullmatch(r'gx:[0-9ABCDEFGHJKMNPQRSTVWXYZ]{6}', args.tag):
        parser.error('tag must be gx: plus 6 Crockford base-32 symbols')
    if args.framework == 'm3a' and not args.serving_receipt:
        parser.error('m3a needs --serving-receipt')
    if args.phase == 'scheduled' and args.fault == 'none':
        parser.error('scheduled episodes carry the fault')
    if args.worker:
        worker(args)
        return
    if args.output.exists():
        parser.error('fresh output directory required; results are never overwritten')
    args.output.mkdir(parents=True)
    command = [sys.executable, '-B', str(Path(__file__).resolve()), *sys.argv[1:], '--worker']
    with (args.output / 'worker.log').open('wb') as stream:
        try:
            reply = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            row = {f: '' for f in FIELDS}   # the killed worker wrote no row; keep the run in episodes.csv
            row.update(episode_id=args.episode_id, scheduled_index=args.scheduled_index, config=args.config,
                       attempt=args.attempt, agent=args.framework, phase=args.phase, agent_final_status='timeout',
                       outcome='INVALID', invalid_reason='harness_timeout', wall_clock_s=args.timeout_seconds,
                       t_end_utc=time.time_ns())
            synthetic = args.framework != 'm3a' or json.loads(args.serving_receipt.read_text()).get('synthetic', False)
            (args.output / 'TIMEOUT.json').write_text(json.dumps(dict(
                status='TIMEOUT', outcome='INVALID', invalid_reason='harness_timeout', tag=args.tag,
                study_data=not synthetic,
                timeout_seconds=args.timeout_seconds, row=row), indent=2), encoding='utf-8')
            raise SystemExit(124)
    print((args.output / 'worker.log').read_text(encoding='utf-8', errors='replace')[-600:])
    raise SystemExit(reply.returncode)


if __name__ == '__main__':
    main()
