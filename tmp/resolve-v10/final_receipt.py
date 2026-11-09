"""Read-only closure evidence for this local setup turn; goal remains partial."""
import hashlib,json,re,time
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((out/'before.json').read_text(encoding='utf-8'))
changed=[p for p,h in baseline.items() if not (root/p).is_file() or sha(root/p)!=h]
paper=[p for p in changed if p.startswith('manuscript/')]
if paper:raise RuntimeError('paper changed: '+str(paper))
integrity=dict(status='PASS',manuscript_changes=paper,changed=changed,
               source_sha256={p.relative_to(root).as_posix():sha(p) for p in (root/'testbed').rglob('*')
                              if p.is_file() and p.suffix in ('.py','.json','.md')})
(out/'INTEGRITY.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
tests={}
for host in ('windows','linux','agent-env'):
 p=out/('tests-'+host+'.json');t=json.loads(p.read_text(encoding='utf-8'))
 if t['exit_code'] or t['tests']!=67:raise RuntimeError('test execution failed: '+host)
 for rel,h in t['source_sha256'].items():
  if sha(root/rel)!=h:raise RuntimeError('code changed after test: '+rel)
 tests[host]=dict(tests=67,executed=67-t['skipped'],skipped=t['skipped'],receipt=p.relative_to(root).as_posix(),sha256=sha(p))
native=json.loads((out/'native-smoke-01/native-env/RESULT.json').read_text(encoding='utf-8'))
wire_parent=json.loads((out/'native-wire-host-02/RESULT.json').read_text(encoding='utf-8'))
if native['status']!='PASS' or wire_parent['status']!='PASS' or not wire_parent['owned_emulator_stopped']:
 raise RuntimeError('native observation/wire smoke did not pass or owned AVD is live')
wire={}
for framework in ('m3a','t3a'):
 directory=out/'native-wire-host-02/native-env'/('scripted-wire-'+framework)
 result=json.loads((directory/'RESULT.json').read_text(encoding='utf-8'))
 if result['status']!='PASS' or not result['kind'].startswith('SYNTHETIC_RESPONSE') or result['models_loaded']:
  raise RuntimeError('bad synthetic/native scope')
 expected=2 if framework=='m3a' else 0
 if len(result['requests'])!=2 or any(r['images']!=expected for r in result['requests']):raise RuntimeError('native image/request fidelity differs')
 for png in directory.glob('request-*-image-*.png'):
  with Image.open(png) as im:
   if im.size!=(1080,2400):raise RuntimeError('image dimensions changed')
 wire[framework]=dict(status='PASS',native_scripted_steps=1,scientific_episodes=0,
                      model_driven_steps=0,requests=2,images_per_request=expected,
                      receipt_sha256=sha(directory/'RESULT.json'))
failed={}
for name in ('native-wire-01','native-wire-02','native-wire-host-01'):
 p=out/name/'RESULT.json';r=json.loads(p.read_text(encoding='utf-8'))
 if r['status']!='FAILED' or not r['owned_emulator_stopped']:raise RuntimeError('failed attempts not preserved/cleaned')
 failed[name]=dict(status='FAILED',error_type=r['error_type'],reason=r['reason'],sha256=sha(p))
verification=json.loads((out/'apk-verification/RESULT.json').read_text(encoding='utf-8'))
if verification['status']!='PASS' or len(verification['apks'])!=11:raise RuntimeError('APK verification incomplete')
validation=dict(status='PARTIAL',utc_ns=time.time_ns(),tests=tests,
                native_observation='PASS',synthetic_native_wire=wire,preserved_failed_attempts=failed,
                graphics_recipe='host renderer in successful scripted-wire attempt; not a frozen/optimal profile',
                apks_verified=11,core_requires_physical_phone=False,models_loaded=False,
                model_driven_agent_steps=0,scientific_episodes=0,measured_calibration_effects=0,
                paid_model_api_calls=0,h100_connected=False,manuscript_unchanged=True,
                remaining=['real-model serving/episode harness/full actions',
                           'AgentProg/UI-TARS/MobileAgent adapters',
                           'P40 accounts/fixtures/reset/grader, MockBank/Postfix',
                           'fault injector/semantic fate-clock-probe joins',
                           'classifier labels/calibration coverage',
                           'H100 fit/load/throughput and full scientific campaigns'])
(out/'VALIDATION.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
broken=[];count=0
for file in [root/'report.md',root/'codex/resolve-progress.md',root/'codex/plan.md',root/'codex/checklist.md',
             root/'codex/setup-server.md',root/'codex/setup-local.md',root/'codex/execution-placement.md',root/'testbed/README.md']:
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
  if target.startswith(('http:','https:','#','mailto:')):continue
  target=target.split('#',1)[0]
  if target:
   count+=1
   if not (file.parent/target).exists():broken.append(dict(file=file.relative_to(root).as_posix(),target=target))
(out/'LINKS.json').write_text(json.dumps(dict(local_links=count,broken=broken),indent=2),encoding='utf-8')
print(json.dumps(dict(status='PARTIAL',paper_changes=paper,tests=tests,
                     scripted_wire={k:v['status'] for k,v in wire.items()},failed_attempts_preserved=len(failed),
                     scientific_episodes=0,broken_links=broken)))
if broken:raise RuntimeError('broken local links')
