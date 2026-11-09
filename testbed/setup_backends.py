"""Install historical backend pins into a project-local venv, recording pip hashes.

Linux/WSL target. Generates local test configs, does not start services or import
old server state. Missing pinned versions FAIL instead of upgrading silently.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import venv
import hashlib
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', required=True)
    parser.add_argument('--resume', action='store_true', help='resume this project-local partial setup without deleting it')
    args = parser.parse_args()
    if os.name != 'posix':
        parser.error('run backend setup on Linux/WSL')
    root = Path(__file__).resolve().parents[1]
    destination = root / 'runtime' / 'backends'
    environment = root / 'runtime' / 'backend-venv'
    if (environment.exists() or destination.exists()) and not args.resume:
        parser.error('fresh project-local backend-venv and backends directories required')
    if (destination/'SETUP.json').exists():
        parser.error('setup already completed; preserve the installed environment')
    destination.mkdir(parents=True, exist_ok=True)
    if args.resume and environment.exists() and not (environment/'pyvenv.cfg').is_file():
        parser.error('existing directory is not a recognized project-local venv')
    # Debian/Ubuntu may omit ensurepip. Bootstrap pip only inside our venv,
    # following the PyPA-supported installer, without changing system Python.
    venv.create(environment, with_pip=False)
    python = environment / 'bin' / 'python'
    available = subprocess.run([str(python),'-m','pip','--version'],capture_output=True).returncode == 0
    if not available:
        bootstrap = destination/'get-pip.py'
        if not bootstrap.exists():
            with urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py',timeout=45) as source:
                bootstrap.write_bytes(source.read())
        (destination/'pip-bootstrap.json').write_text(json.dumps(dict(
            source_url='https://bootstrap.pypa.io/get-pip.py',sha256=hashlib.sha256(bootstrap.read_bytes()).hexdigest(),
            retrieved_utc_ns=time.time_ns(),target_venv=str(environment),pip_version='26.3'),indent=2))
        with (destination/'pip-bootstrap.log').open('w') as log:
            subprocess.run([str(python),str(bootstrap),'pip==26.3'],stdout=log,stderr=subprocess.STDOUT,check=True)
    requirements = Path(__file__).parent / 'requirements-backends.txt'
    with (destination / 'install.log').open('w') as log:
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(requirements),
                        '--report', str(destination / 'pip-install-report.json')],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    frozen = subprocess.check_output([str(python), '-m', 'pip', 'freeze'])
    (destination / 'requirements-resolved.txt').write_bytes(frozen)
    synapse = destination / 'synapse'
    synapse.mkdir(exist_ok=True)
    subprocess.run([str(python), '-m', 'synapse.app.homeserver', '--server-name', 'ghost.test',
                    '--config-path', str(synapse / 'homeserver.yaml'), '--generate-config', '--report-stats', 'no'],
                   cwd=synapse, check=True)
    # PyYAML is installed as a Synapse dependency. Edit structured config in that
    # venv; no shell interpolation, no public federation listener/registration.
    config_script = '''import pathlib,sys,yaml,secrets,os
p=pathlib.Path(sys.argv[1]);d=yaml.safe_load(p.read_text())
d['listeners']=[{'port':8008,'tls':False,'type':'http','bind_addresses':['127.0.0.1'],'resources':[{'names':['client'],'compress':False}]}]
d['enable_registration']=False
d['registration_shared_secret']=secrets.token_hex(32)
d['federation_domain_whitelist']=[]
d['url_preview_enabled']=False
p.write_text(yaml.safe_dump(d,sort_keys=False))
os.chmod(p,0o600)
'''
    subprocess.run([str(python), '-c', config_script, str(synapse / 'homeserver.yaml')], check=True)
    radicale = destination / 'radicale'
    radicale.mkdir(exist_ok=True)
    # A generated test password remains in a project-local file. Never use user
    # credentials or external accounts; this file is not emitted to stdout.
    import secrets
    (radicale / 'users').write_text('gx_test:' + secrets.token_hex(16) + '\n')
    (radicale / 'users').chmod(0o600)
    (radicale / 'config').write_text('[server]\nhosts = 127.0.0.1:5232\n[auth]\ntype = htpasswd\n'
                                    'htpasswd_filename = ' + str(radicale / 'users') + '\nhtpasswd_encryption = plain\n'
                                    '[storage]\nfilesystem_folder = ' + str(radicale / 'collections') + '\n')
    result = dict(status='INSTALLED_NOT_CAMPAIGN_READY', kind='new local backend installation',
                  utc_ns=time.time_ns(), venv=str(environment),
                  next=['create isolated Synapse users/room with generated registration shared secret',
                        'create Radicale test calendar and configure DAVx5 account',
                        'start pinned GreenMail, configure K9 receiver/Sent/no-Sent mapping',
                        'freeze APK/ABI/profile/reset receipts; run actual nofault/fault Android cases'])
    (destination / 'SETUP.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
