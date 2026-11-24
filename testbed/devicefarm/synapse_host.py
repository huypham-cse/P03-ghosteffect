"""Synapse on the Device Farm test host for the Element runs (b-log 24/11): the same server as the emulator testbed
(Synapse 1.164.2, server name ghost.test, client listener on 127.0.0.1 only, no registration, no federation, the
testbed's rate limits), fresh test accounts alice and bob with random passwords, and alice's room "gx test" with bob
joined. Writes the accounts file element_planner.py reads (GX_ELEMENT_ACCOUNTS); passwords are never printed.

  python3 testbed/devicefarm/synapse_host.py --dir <state dir> --accounts <file> [--port 8008]

Run with PYTHONPATH pointing at the pip --target directory that holds matrix-synapse (the host Python has no venv).
"""
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request

SERVER = 'ghost.test'
ROOM = 'gx test'


def call(base, method, path, body=None, token=None):
    request = urllib.request.Request(base + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json',
                                              **({'Authorization': 'Bearer ' + token} if token else {})})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read() or b'{}')


def configure(state, port):
    import yaml   # a Synapse dependency, importable from the same --target directory
    config = state / 'homeserver.yaml'
    subprocess.run([sys.executable, '-m', 'synapse.app.homeserver', '--server-name', SERVER, '--config-path',
                    str(config), '--generate-config', '--report-stats', 'no'], cwd=state, check=True,
                   stdout=subprocess.DEVNULL)
    d = yaml.safe_load(config.read_text())
    d['listeners'] = [{'port': port, 'tls': False, 'type': 'http', 'bind_addresses': ['127.0.0.1'],
                       'resources': [{'names': ['client'], 'compress': False}]}]
    d.update(enable_registration=False, registration_shared_secret=secrets.token_hex(32), federation_domain_whitelist=[],
             url_preview_enabled=False, trusted_key_servers=[], suppress_key_server_warning=True,
             rc_message={'per_second': 50, 'burst_count': 100},
             rc_login={k: {'per_second': 10, 'burst_count': 50} for k in ('address', 'account', 'failed_attempts')})
    config.write_text(yaml.safe_dump(d, sort_keys=False))
    os.chmod(config, 0o600)
    return config, d['registration_shared_secret']


def register(base, secret, user, password):
    nonce = call(base, 'GET', '/_synapse/admin/v1/register')['nonce']
    mac = hmac.new(secret.encode(), b'\x00'.join([nonce.encode(), user.encode(), password.encode(), b'notadmin']),
                   hashlib.sha1).hexdigest()
    call(base, 'POST', '/_synapse/admin/v1/register', dict(nonce=nonce, username=user, password=password, mac=mac,
                                                         admin=False))


def login(base, user, password, device):
    return call(base, 'POST', '/_matrix/client/v3/login', dict(type='m.login.password', device_id=device,
                identifier=dict(type='m.id.user', user=user), password=password))['access_token']


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dir', type=Path, required=True)
    p.add_argument('--accounts', type=Path, required=True)
    p.add_argument('--port', type=int, default=8008)
    a = p.parse_args()
    a.dir.mkdir(parents=True, exist_ok=True)
    config, secret = configure(a.dir, a.port)
    subprocess.run([sys.executable, '-m', 'synapse.app.homeserver', '-c', str(config), '--daemonize'], cwd=a.dir,
                   check=True)
    base = 'http://127.0.0.1:%d' % a.port
    for _ in range(90):
        try:
            call(base, 'GET', '/_matrix/client/versions')
            break
        except (urllib.error.URLError, OSError):
            time.sleep(1)
    else:
        raise SystemExit('Synapse did not answer on ' + base)
    users = {name: dict(user=name, password=secrets.token_urlsafe(18)) for name in ('alice', 'bob')}
    for u in users.values():
        register(base, secret, u['user'], u['password'])
    alice = login(base, 'alice', users['alice']['password'], 'GXSETUP')
    room = call(base, 'POST', '/_matrix/client/v3/createRoom', dict(name=ROOM, preset='private_chat',
                invite=['@bob:' + SERVER]), alice)['room_id']
    bob = login(base, 'bob', users['bob']['password'], 'GXSETUPB')
    call(base, 'POST', '/_matrix/client/v3/join/' + urllib.request.quote(room), {}, bob)
    a.accounts.write_text(json.dumps(dict(homeserver=base, server_name=SERVER, room_id=room, **users), indent=2))
    os.chmod(a.accounts, 0o600)
    print(json.dumps(dict(status='READY', homeserver=base, room_id=room, users=sorted(users))))


if __name__ == '__main__':
    main()
