"""Verify this turn's authorized changes and preserve honest readiness scope."""
import hashlib,json,re,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((root/'tmp/resolve-v7/before.json').read_text(encoding='utf-8'))
publication=json.loads((out/'draft-refresh/PUBLICATION.json').read_text(encoding='utf-8'))
pdf=json.loads((out/'draft-refresh/PDF-PUBLICATION.json').read_text(encoding='utf-8'))
restoration=json.loads((out/'draft-refresh/PAPER-RESTORED.json').read_text(encoding='utf-8'))
if restoration['status']!='PASS':raise RuntimeError('paper restoration failed')
for entry in restoration['restored']:
 path=root/entry['file'];expected=entry['restored_sha256']
 if (path.exists() if expected is None else (not path.is_file() or sha(path)!=expected)):
  raise RuntimeError('restored manuscript no longer matches its pre-turn state: '+entry['file'])
allowed={x['file']:x['after_sha256'] for x in publication['outputs'] if not x['file'].startswith('manuscript/')}
changed=[p for p,h in baseline.items() if not (root/p).is_file() or sha(root/p)!=h]
protected=[p for p in changed if p.startswith(('artifact/','manuscript/')) or p in ('review.md','STATUS.md')]
unexpected=[p for p in protected if p not in allowed or sha(root/p)!=allowed[p]]
missing_published=[p for p,h in allowed.items() if not (root/p).is_file() or sha(root/p)!=h]
integrity=dict(status='PASS' if not unexpected and not missing_published else 'FAILED',
               basis='v7 baseline; derived experiment CSVs retained; manuscript edits restored per latest user request',
               unexpected_protected_changes=unexpected,published_hash_mismatches=missing_published,
               authorized_derived_changes=protected,
               raw_measurements_modified=any(p.startswith('artifact/results/real/') for p in protected),
               numerical_source_modified=any(p.startswith('artifact/scripts/') for p in protected),
               paper_prose_modified=any(p.startswith('manuscript/sections/') or p=='manuscript/main.tex' for p in protected))
(out/'INTEGRITY.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
if integrity['status']!='PASS':raise RuntimeError('unexpected protected changes')
tests={}
for host in ('windows','linux','agent-env'):
 path=out/('tests-'+host+'.json');test=json.loads(path.read_text(encoding='utf-8'))
 if test['exit_code'] or test['tests']!=66:raise RuntimeError('component tests did not pass: '+host)
 for rel,expected in test['source_sha256'].items():
  if sha(root/rel)!=expected:raise RuntimeError('testbed code changed after test run: '+rel)
 tests[host]=dict(tests=test['tests'],skipped=test['skipped'],executed=test['tests']-test['skipped'],
                  receipt=path.relative_to(root).as_posix(),sha256=sha(path))
smoke=json.loads((out/'sms-startup-diagnostics/RESULT.json').read_text(encoding='utf-8'))
if smoke['status']!='PASS' or not smoke['owned_emulator_stopped']:raise RuntimeError('startup smoke failed or owned AVD not stopped')
status=dict(status='PARTIAL',utc_ns=time.time_ns(),tests=tests,
            android_startup_status=smoke['status'],android_reader_qualified=False,
            android_stable_tree=smoke['apks'][0]['stable_tree'],owned_emulator_stopped=True,
            fresh_simulation=dict(policy_rows=24,workflows_per_cell=12000,
                                  source_ask_percent=publication['fresh_source_family_row']['ask']),
            draft_numeric_publication='RESTORED_PAPER_DEFERRED',draft_pdf_publication='RESTORED_PAPER_DEFERRED',
            manuscript_restored_files=len(restoration['restored']),manuscript_restoration='PASS',
            draft_numbers_are_illustrative=True,archive_numeric_match_is_a_gate=False,
            native_source_binding_tests_executed=True,native_grpc_avd_verified=False,
            models_loaded=False,native_agent_episodes=0,measured_calibration_effects=0,
            paper_campaign_episodes=0,paid_model_api_calls=0,h100_connected=False,
            remaining=['native forwarder/gRPC/episode harness and frameworkA3-A5 bindings',
                       'accounts/task fixtures/reset/grader for P40',
                       'collector fate/probe/clock joins and measured calibration',
                       'actual H100 serving/fit/throughput','native/protected paper campaigns'])
artifact_tests=json.loads((out/'artifact-tests.json').read_text(encoding='utf-8'))
schema=json.loads((out/'CSV-SCHEMA.json').read_text(encoding='utf-8'))
if artifact_tests['exit_code'] or schema['malformed']:raise RuntimeError('artifact regression/schema checks failed')
status['artifact_regression']=dict(tests=32,skipped=1,exit_code=artifact_tests['exit_code'],
                                    log_sha256=artifact_tests['log_sha256'])
status['published_csv_schema']=dict(files=len(schema['rows']),malformed=[])
(out/'VALIDATION.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
broken=[];count=0
for file in [root/'report.md',root/'resolve.md',root/'testbed/README.md',
             root/'codex/resolve-progress.md',root/'codex/plan.md',root/'codex/checklist.md',
             root/'codex/experiments.md',root/'codex/code-fixes.md',root/'codex/paper-alignment.md']:
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
  if target.startswith(('http:','https:','#','mailto:')):continue
  target=target.split('#',1)[0]
  if not target:continue
  count+=1
  if not (file.parent/target).exists():broken.append(dict(file=file.relative_to(root).as_posix(),target=target))
(out/'LINKS.json').write_text(json.dumps(dict(local_links=count,broken=broken),indent=2),encoding='utf-8')
print(json.dumps(dict(status='PARTIAL',integrity=integrity['status'],tests=tests,
                      paper_episodes=0,local_links=count,broken_links=broken)))
if broken:raise RuntimeError('broken local documentation links')
