"""Laptop-side driver for the AWS Device Farm runs (b-log 18/11). Only `aws devicefarm` commands are used.

  python testbed/devicefarm/df.py run --package <zip> --spec <yml> --device-arn <arn> --name <run> --timeout 30 --out <dir>
  python testbed/devicefarm/df.py stop --run-arn <arn>
  python testbed/devicefarm/df.py minutes

`run` uploads the K-9 APK as the app, the package and the spec, schedules one run on one device with a job timeout,
waits for it to finish (stopping it if it outlives the timeout plus a margin), downloads every FILE artifact into
--out, and appends the device minutes and the account's remaining trial minutes to --out/minutes.json.

The AWS profile and project come from DF_PROFILE and DF_PROJECT (defaults: the 18-19/11 runs). Runs from 24/11 use
DF_PROFILE=devicefarm-credit-run and the P03-ghosteffect project ARN; that profile's login is
`aws login --profile devicefarm-credit --region ap-southeast-2`.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

PROFILE = os.environ.get('DF_PROFILE', 'devicefarm')
AWS = ['aws', 'devicefarm', '--profile', PROFILE, '--region', 'us-west-2', '--output', 'json']
PROJECT = os.environ.get('DF_PROJECT',
                         'arn:aws:devicefarm:us-west-2:478825889366:project:83e7e695-4f56-4afc-bca4-cb04dea963ec')
ROOT = Path(__file__).resolve().parents[2]


def aws(*args):
    result = subprocess.run(AWS + list(args), capture_output=True, text=True)
    if result.returncode:
        if 'expired' in result.stderr.lower() or 'login' in result.stderr.lower():
            raise SystemExit(f'AWS login expired for profile {PROFILE}: run aws login (see the docstring)')
        raise SystemExit(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else {}


def upload(path, kind):
    up = aws('create-upload', '--project-arn', PROJECT, '--name', Path(path).name, '--type', kind)['upload']
    request = urllib.request.Request(up['url'], data=Path(path).read_bytes(), method='PUT',
                                     headers={'Content-Type': 'application/octet-stream'})
    urllib.request.urlopen(request).read()
    while True:
        up = aws('get-upload', '--arn', up['arn'])['upload']
        if up['status'] in ('SUCCEEDED', 'FAILED'):
            break
        time.sleep(5)
    if up['status'] != 'SUCCEEDED':
        raise SystemExit(f"{kind} upload failed: {up.get('metadata') or up.get('message')}")
    print('uploaded', kind, Path(path).name)
    return up['arn']


def minutes():
    return aws('get-account-settings')['accountSettings']['trialMinutes']


def download(run_arn, out):
    out.mkdir(parents=True, exist_ok=True)
    for job in aws('list-jobs', '--arn', run_arn)['jobs']:
        for artifact in aws('list-artifacts', '--arn', job['arn'], '--type', 'FILE')['artifacts']:
            name = f"{artifact['name']}.{artifact['extension']}".replace(' ', '_')
            urllib.request.urlretrieve(artifact['url'], out / name)
            print('artifact', name)


def run(args):
    before = minutes()
    app = upload(ROOT / 'runtime/assets/com.fsck.k9_39046.apk', 'ANDROID_APP')
    package = upload(args.package, 'APPIUM_PYTHON_TEST_PACKAGE')
    spec = upload(args.spec, 'APPIUM_PYTHON_TEST_SPEC')
    selection = json.dumps(dict(filters=[dict(attribute='ARN', operator='IN', values=[args.device_arn])], maxDevices=1))
    scheduled = aws('schedule-run', '--project-arn', PROJECT, '--app-arn', app, '--name', args.name,
                    '--device-selection-configuration', selection,
                    '--test', json.dumps(dict(type='APPIUM_PYTHON', testPackageArn=package, testSpecArn=spec)),
                    '--execution-configuration', json.dumps(dict(jobTimeoutMinutes=args.timeout)))['run']
    print('scheduled', scheduled['arn'])
    start = time.monotonic()
    while True:
        state = aws('get-run', '--arn', scheduled['arn'])['run']
        if state['status'] == 'COMPLETED':
            break
        if time.monotonic() - start > (args.timeout + 20) * 60:   # a stuck run is stopped, never left billing
            aws('stop-run', '--arn', scheduled['arn'])
            print('stopped after the timeout')
        print(time.strftime('%H:%M:%S'), state['status'], flush=True)
        time.sleep(30)
    download(scheduled['arn'], args.out)
    after = minutes()
    record = dict(name=args.name, run_arn=scheduled['arn'], result=state.get('result'),
                  device_minutes=state.get('deviceMinutes'), trial_remaining_before=before['remaining'],
                  trial_remaining_after=after['remaining'], utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    ledger = args.out / 'minutes.json'
    ledger.write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))


def schedule_batch(args):
    """Upload the app and package once, schedule one run per --job name:spec:timeout, and return without waiting: the
    runs go on in Device Farm with the laptop off, bounded by their job timeouts. `fetch` collects them later."""
    args.out.mkdir(parents=True, exist_ok=True)
    before = minutes()
    app = upload(ROOT / 'runtime/assets/com.fsck.k9_39046.apk', 'ANDROID_APP')
    package = upload(args.package, 'APPIUM_PYTHON_TEST_PACKAGE')
    selection = json.dumps(dict(filters=[dict(attribute='ARN', operator='IN', values=[args.device_arn])], maxDevices=1))
    runs = []
    for job in args.job:
        name, spec_path, timeout = job.split(':')
        spec = upload(ROOT / spec_path, 'APPIUM_PYTHON_TEST_SPEC')
        r = aws('schedule-run', '--project-arn', PROJECT, '--app-arn', app, '--name', name,
                '--device-selection-configuration', selection,
                '--test', json.dumps(dict(type='APPIUM_PYTHON', testPackageArn=package, testSpecArn=spec)),
                '--execution-configuration', json.dumps(dict(jobTimeoutMinutes=int(timeout))))['run']
        runs.append(dict(name=name, spec=spec_path, timeout_min=int(timeout), run_arn=r['arn'], status=r['status']))
        print('scheduled', name, r['status'], flush=True)
    record = dict(profile=PROFILE, project=PROJECT, device_arn=args.device_arn, trial_remaining_before=before['remaining'],
                  utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), runs=runs)
    (args.out / 'scheduled.json').write_text(json.dumps(record, indent=2))


def fetch(args):
    """For each run in --out/scheduled.json: status, and for a finished run its artifacts and device minutes."""
    record = json.loads((args.out / 'scheduled.json').read_text())
    for r in record['runs']:
        state = aws('get-run', '--arn', r['run_arn'])['run']
        r.update(status=state['status'], result=state.get('result'), device_minutes=state.get('deviceMinutes'))
        if state['status'] == 'COMPLETED' and not (args.out / r['name'] / 'fetched.json').exists():
            download(r['run_arn'], args.out / r['name'])
            (args.out / r['name'] / 'fetched.json').write_text(json.dumps(r, indent=2))
        print(r['name'], r['status'], r.get('result'), r.get('device_minutes'), flush=True)
    record['trial_remaining_now'] = minutes()['remaining']
    (args.out / 'scheduled.json').write_text(json.dumps(record, indent=2))
    print('trial minutes remaining', record['trial_remaining_now'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--package', type=Path, required=True)
    r.add_argument('--spec', type=Path, required=True)
    r.add_argument('--device-arn', required=True)
    r.add_argument('--name', required=True)
    r.add_argument('--timeout', type=int, required=True)
    r.add_argument('--out', type=Path, required=True)
    b = sub.add_parser('schedule')
    b.add_argument('--package', type=Path, required=True)
    b.add_argument('--device-arn', required=True)
    b.add_argument('--job', action='append', required=True, help='name:spec path (repo-relative):timeout minutes')
    b.add_argument('--out', type=Path, required=True)
    f = sub.add_parser('fetch')
    f.add_argument('--out', type=Path, required=True)
    s = sub.add_parser('stop')
    s.add_argument('--run-arn', required=True)
    sub.add_parser('minutes')
    args = parser.parse_args()
    if args.cmd == 'run':
        run(args)
    elif args.cmd == 'schedule':
        schedule_batch(args)
    elif args.cmd == 'fetch':
        fetch(args)
    elif args.cmd == 'stop':
        print(aws('stop-run', '--arn', args.run_arn)['run']['status'])
    else:
        print(minutes())
