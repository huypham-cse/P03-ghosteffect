"""Evidence handoff only; no installation, inference or study execution."""
import hashlib
import json
from pathlib import Path
import time

root = Path(__file__).resolve().parents[2]
out = Path(__file__).parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
baseline = json.loads((root / 'tmp/resolve-v7/before.json').read_text(encoding='utf-8'))
changed = [p for p, value in baseline.items() if not (root / p).is_file() or digest(root / p) != value]
protected = [p for p in changed if p.startswith(('artifact/', 'manuscript/')) or p in ('review.md', 'STATUS.md')]
source_hashes = {p.relative_to(root).as_posix(): digest(p) for p in (root / 'testbed').rglob('*')
                 if p.is_file() and p.suffix in ('.py', '.json', '.md') and '__pycache__' not in p.parts}
integrity = dict(status='PASS' if not protected else 'FAILED', baseline_files=len(baseline),
                 protected_changed=protected, changed=changed, source_sha256=source_hashes)
(out / 'INTEGRITY.json').write_text(json.dumps(integrity, indent=2), encoding='utf-8')
tests = {}
for host in ('windows', 'linux'):
    path = out / ('testbed-tests-' + host + '.json')
    receipt = json.loads(path.read_text(encoding='utf-8'))
    if receipt['exit_code'] != 0:
        raise RuntimeError('component tests failed: ' + host)
    tests[host] = dict(receipt=path.relative_to(root).as_posix(), receipt_sha256=digest(path),
                       log_sha256=receipt['log_sha256'], tests=60, skipped=1 if host == 'windows' else 0)
validation = dict(status='PARTIAL', utc_ns=time.time_ns(), tests=tests,
                  agent_runtime_receipt='runtime/agents/SETUP.json',
                  agent_runtime_receipt_sha256=digest(root / 'runtime/agents/SETUP.json'),
                  latest_android_smoke='tmp/resolve-v8/sms-startup-01/RESULT.json',
                  latest_android_smoke_status='FAILED_XML_PARSE_ERROR_CAUSE_UNVERIFIED',
                  sms_role_diagnostic='tmp/resolve-v8/sms-live-02/RESULT.json',
                  sms_role_diagnostic_status='NOT_READY',
                  models_loaded=False, native_agent_episodes=0, measured_calibration_effects=0,
                  paper_campaign_episodes=0, h100_connected=False, paid_model_api_calls=0,
                  protected_integrity_status=integrity['status'],
                  missing=['Android capture/startup qualification', 'accounts/P40 fixtures/reset/grader',
                           'official framework environment/action wiring', 'collector/fate/probe/clock joins',
                           'measured calibration and coverage', 'H100 serving/fit/throughput',
                           'historical archived source/output discrepancy'])
(out / 'VALIDATION.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')
print(json.dumps(dict(status=validation['status'], protected_changed=protected,
                     test_hosts=list(tests), paper_episodes=0)))
if protected:
    raise RuntimeError('protected artifact/source changed since v7 baseline')
