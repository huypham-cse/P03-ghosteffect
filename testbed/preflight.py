"""Read-only readiness inventory. Missing Android assets are explicit, not PASS."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import time


def inspect(adb=None, serial=None):
    root = Path(__file__).resolve().parents[1]
    sdk = root / 'runtime' / 'android-sdk'
    executable = adb or (sdk / 'platform-tools' / ('adb.exe' if os.name == 'nt' else 'adb'))
    result = dict(utc_ns=time.time_ns(), kind='reconstruction preflight', python=sys.version,
                  sqlite=sqlite3.sqlite_version, platform=platform.platform(),
                  machine=platform.machine(), cpus=os.cpu_count(),
                  linux_kvm_exists=Path('/dev/kvm').exists(),
                  linux_kvm_access=os.access('/dev/kvm', os.R_OK | os.W_OK),
                  adb_exists=Path(executable).is_file(), java_available=shutil.which('java') is not None,
                  sdk_root=str(sdk), assets=[], backends={})
    lock = json.loads((Path(__file__).parent / 'assets.lock.json').read_text())
    from setup_assets import sha
    for asset in lock['assets']:
        path = root / 'runtime' / 'assets' / asset['file']
        result['assets'].append(dict(file=asset['file'], present=path.is_file(),
                                     hash_matches=sha(path) == asset['sha256'] if path.is_file() else False))
    for name, expected in lock['python_backends'].items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        result['backends'][name] = dict(expected=expected, installed_here=actual, matches=actual == expected)
    result['android_connected'] = False
    if result['adb_exists'] and serial:
        from ui import ADB
        device = ADB(executable, serial)
        result['android'] = {key: device.shell('getprop', prop) for key, prop in
                             [('api', 'ro.build.version.sdk'), ('abi', 'ro.product.cpu.abi'),
                              ('fingerprint', 'ro.build.fingerprint')]}
        result['android_connected'] = result['android']['api'] == '33'
    result['status'] = 'READY_FOR_MANUAL_STACK_SETUP' if result['android_connected'] else 'ANDROID_NOT_READY'
    result['not_verified'] = ['backend accounts/reset/snapshots', 'APK signatures and installed versions',
                              'actual GUI reader profiles', 'models and five framework adapters',
                              'calibration/certificates', 'scientific campaign results']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb')
    parser.add_argument('--serial')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('fresh output required')
    result = inspect(args.adb, args.serial)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
