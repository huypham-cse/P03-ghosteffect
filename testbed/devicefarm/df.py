"""Laptop-side driver for the AWS Device Farm runs (b-log 18/11). Only `aws devicefarm` commands are used.

  python testbed/devicefarm/df.py run --package <zip> --spec <yml> --device-arn <arn> --name <run> --timeout 30 --out <dir>
  python testbed/devicefarm/df.py stop --run-arn <arn>
  python testbed/devicefarm/df.py minutes

`run` uploads the K-9 APK as the app, the package and the spec, schedules one run on one device with a job timeout,
waits for it to finish (stopping it if it outlives the timeout plus a margin), downloads every FILE artifact into
--out, and appends the device minutes and the account's remaining trial minutes to --out/minutes.json.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time
import urllib.request

AWS = ['aws', 'devicefarm', '--profile', 'devicefarm', '--region', 'us-west-2', '--output', 'json']
PROJECT = 'arn:aws:devicefarm:us-west-2:478825889366:project:83e7e695-4f56-4afc-bca4-cb04dea963ec'
ROOT = Path(__file__).resolve().parents[2]


def aws(*args):
    result = subprocess.run(AWS + list(args), capture_output=True, text=True)
    if result.returncode:
        if 'expired' in result.stderr.lower() or 'login' in result.stderr.lower():
            raise SystemExit('AWS login expired: run  aws login --profile devicefarm --region us-west-2')
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
    s = sub.add_parser('stop')
    s.add_argument('--run-arn', required=True)
    sub.add_parser('minutes')
    args = parser.parse_args()
    if args.cmd == 'run':
        run(args)
    elif args.cmd == 'stop':
        print(aws('stop-run', '--arn', args.run_arn)['run']['status'])
    else:
        print(minutes())
