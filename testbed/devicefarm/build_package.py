"""Build the AWS Device Farm test package for the rented-phone runs (b-log 18/11).

  python testbed/devicefarm/build_package.py --out <dir>

Device Farm's APPIUM_PYTHON type wants requirements.txt, wheelhouse/ and tests/ at the zip root; the custom test
spec ignores Appium and runs the testbed scripts on the test host instead. The zip also carries the testbed code,
sim_nonce.py (lazily imported by ui.py), the locked APKs and GreenMail (hash-checked by setup_assets.sha), and any
wheels found in --wheels (Radicale for the CalDAV runs). Nothing from runtime/ besides those assets is packed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ('com.fsck.k9_39046.apk', 'at.bitfire.davdroid_405210002.apk', 'ws.xsoh.etar_57.apk', 'greenmail.jar',
          'im.vector.app_40106622.apk')   # Element 1.6.62 arm64 for the 24/11 runs
# Assets kept outside runtime/ (drive C is nearly full): GX_EXTRA_ASSETS names a second folder; every file is still
# hash-checked against testbed/assets.lock.json.
ASSET_DIRS = [ROOT / 'runtime/assets'] + ([Path(os.environ['GX_EXTRA_ASSETS'])] if 'GX_EXTRA_ASSETS' in os.environ else [])
# The TN4 transfer check (b-log 24/11) runs element_planner.py with the emulator store and its numeric dependencies.
EXTRA = ('testbed/tn4/tn4_store.json', 'artifact/scripts/planner_sim.py', 'artifact/scripts/ge_core.py')


def build(out, wheels=None):
    lock = {a['file']: a['sha256'] for a in json.loads((ROOT / 'testbed/assets.lock.json').read_text())['assets']}
    target = out / 'gx-devicefarm.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('requirements.txt', 'pytest\nradicale==3.9.0\n')   # Device Farm rejects an empty file
        z.writestr('wheelhouse/', '')
        for wheel in sorted(Path(wheels).glob('*.whl')) if wheels else ():
            z.write(wheel, 'wheelhouse/' + wheel.name)
        z.writestr('tests/test_placeholder.py', 'def test_placeholder():\n    pass\n')
        for path in sorted((ROOT / 'testbed').glob('*.py')) + [ROOT / 'testbed/assets.lock.json']:
            z.write(path, 'testbed/' + path.name)
        for path in sorted((ROOT / 'testbed/devicefarm').glob('*')):   # LF on the Linux host whatever git checked out
            z.writestr('testbed/devicefarm/' + path.name, path.read_bytes().replace(b'\r\n', b'\n'))
        z.write(ROOT / 'artifact/scripts/sim_nonce.py', 'artifact/scripts/sim_nonce.py')
        for rel in EXTRA:
            z.write(ROOT / rel, rel)
        # TN3 (b-log 19/11): the phone ledger benchmark, built by testbed/phone_ledger/build.sh; its hash is logged.
        apk = ROOT / 'testbed/phone_ledger/build/ledgerbench.apk'
        if apk.exists():
            z.write(ROOT / 'testbed/phone_ledger/harness.py', 'testbed/phone_ledger/harness.py')
            z.write(apk, 'testbed/phone_ledger/ledgerbench.apk')
            print('ledgerbench.apk sha256', hashlib.sha256(apk.read_bytes()).hexdigest())
        for name in ASSETS:
            path = next((d / name for d in ASSET_DIRS if (d / name).exists()), ROOT / 'runtime/assets' / name)
            if hashlib.sha256(path.read_bytes()).hexdigest() != lock[name]:
                raise SystemExit(name + ' does not match assets.lock.json')
            z.write(path, 'runtime/assets/' + name)
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--wheels', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    print(build(args.out, args.wheels))
