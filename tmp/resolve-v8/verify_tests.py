"""Save component test receipts; never counted as paper trials."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[2]
host = sys.argv[1]
if host not in ('windows', 'linux'):
    raise ValueError('windows or linux required')
command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'testbed/tests', '-v']
if host == 'linux':
    command = ['wsl', '-d', 'Ubuntu', '--cd', '/mnt/d/NCKH/mobisys/P03-ghosteffect',
               '--', 'python3', '-B', '-m', 'unittest', 'discover', '-s', 'testbed/tests', '-v']
log = Path(__file__).parent / ('testbed-tests-' + host + '.log')
started = time.time_ns()
with log.open('wb') as stream:
    reply = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
result = dict(host=host, command=command, started_utc_ns=started,
              finished_utc_ns=time.time_ns(), exit_code=reply.returncode,
              scope='component/synthetic fixtures; not agent/Android/calibration trials',
              log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
log.with_suffix('.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
print(log.read_text(encoding='utf-8', errors='replace')[-500:])
sys.exit(reply.returncode)
