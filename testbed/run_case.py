"""Injector-side native development trial with a REAL post-accept/pre-ACK barrier.

Precondition: the test app is on the prepared compose screen, test accounts and
empty queues verified, and proxy already running. This is NOT an LLM agent run.
No account credentials or backend truth is sent to a host recovery controller.
"""
import argparse
import json
import re
from pathlib import Path
import time
import urllib.request

from faultproxy import Journal
from ui import ADB, validate_package
from app_driver import navigate, poll_history


def control(base, action, payload):
    if not base.startswith('http://127.0.0.1:'):
        raise ValueError('injector control must be on loopback')
    request = urllib.request.Request(base + '/' + action, json.dumps(payload).encode(),
                                     {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def run(args):
    args.output.mkdir(parents=True, exist_ok=False)
    log = Journal(args.output / 'injector.jsonl')
    adb = ADB(args.adb, args.serial)
    validate_package(args.package)
    if not adb.foreground().startswith(args.package + '/'):
        raise RuntimeError('target app is not foreground; prepare compose screen first')
    profile = json.loads(args.profile.read_text(encoding='utf-8')) if args.profile else None
    if profile:
        if profile.get('package') != args.package:
            raise ValueError('profile/package mismatch')
        if not args.nonce:
            raise ValueError('--nonce required for profile-based visibility polling')
        navigate(adb, profile, profile.get('prepare_actions', []), args.fixture_text)
    arm = control(args.control, 'arm', dict(mode=args.mode, request_id=args.request_id))['arm_id']
    log.emit('START', kind='native-scripted-reconstruction', arm_id=arm,
             planned_fault=args.fault, serial=args.serial)
    adb.capture(args.output / 'before')
    log.emit('TAP_BEGIN')
    adb.tap(*args.tap)
    deadline = time.monotonic() + args.barrier_timeout
    status = None
    while time.monotonic() < deadline:
        status = control(args.control, 'status', {'arm_id': arm})
        if status['barrier']:
            break
        time.sleep(.05)
    else:
        raise RuntimeError('arm miss or upstream acceptance absent; trial is INVALID')
    log.emit('BARRIER_OBSERVED', arm_id=arm, request_id=status['request_id'])
    if args.pre_fault_delay:
        log.emit('PRE_FAULT_DELAY', seconds=args.pre_fault_delay, client_timeout_verified=False)
        time.sleep(args.pre_fault_delay)
    if args.fault == 'force-stop':
        receipt = adb.force_stop(args.package)
    else:
        receipt = dict(observed_class='none')
    log.emit('FAULT_APPLIED', **receipt)
    control(args.control, 'release', dict(arm_id=arm, fault_receipt=receipt))
    recovery = adb.launch(args.component) if args.fault == 'force-stop' else dict(
        recovery_origin_mono_ns=time.monotonic_ns(), foreground=adb.foreground())
    log.emit('RECOVERY', **recovery)
    adb.capture(args.output / 'recovered')
    visibility = None
    if profile:
        navigate(adb, profile, profile.get('history_actions', []))
        visibility = poll_history(adb, profile, args.nonce, args.output / 'visibility',
                                  recovery['recovery_origin_mono_ns'], args.observation_seconds)
    result = dict(status='CAPTURED_NOT_GRADED', kind='scripted Android development trial',
                  arm_id=arm, request_id=status['request_id'], recovery=recovery,
                  visibility=visibility,
                  missing=['backend copy-count/grader',
                           'native agent continuation; this driver is scripted'])
    if not profile:
        result['missing'].append('verified history navigation and polling')
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', required=True)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--package', required=True)
    parser.add_argument('--component', required=True)
    parser.add_argument('--control', required=True)
    parser.add_argument('--mode', required=True, choices=['pass', 'reject', 'drop', 'sticky', 'withhold'])
    parser.add_argument('--fault', choices=['none', 'force-stop'], required=True)
    parser.add_argument('--request-id', help='exact txnId, CalDAV path or Message-ID; otherwise first matching request')
    parser.add_argument('--tap', nargs=2, type=int, required=True)
    parser.add_argument('--barrier-timeout', type=float, default=45)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', type=Path, help='actual frozen per-app GUI profile')
    parser.add_argument('--fixture-text', help='safe ASCII test-only content, including opted-in nonce when applicable')
    parser.add_argument('--nonce')
    parser.add_argument('--observation-seconds', type=float, default=300)
    parser.add_argument('--pre-fault-delay', type=float, default=0,
                        help='explicit timing intervention; does not prove a client timeout')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('fresh output directory required; previous results are never overwritten')
    if not args.component.startswith(args.package + '/'):
        parser.error('component must belong to the target package')
    if args.nonce and not re.fullmatch(r'gx:[0-9ABCDEFGHJKMNPQRSTVWXYZ]{6}', args.nonce):
        parser.error('invalid Crockford nonce')
    if not 0 <= args.pre_fault_delay <= 120 or not 0 < args.observation_seconds <= 300:
        parser.error('invalid delay/horizon')
    if args.mode == 'withhold' and args.pre_fault_delay <= 0:
        parser.error('withhold needs an explicit pre-fault delay; client-timeout evidence still required')
    try:
        print(json.dumps(run(args), indent=2))
    except Exception as exc:
        if args.output.is_dir():
            result = dict(status='INVALID', error_type=type(exc).__name__, reason=str(exc))
            (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
