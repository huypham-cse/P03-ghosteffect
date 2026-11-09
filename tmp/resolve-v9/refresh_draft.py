"""Refresh derived numbers from verified runs, retaining the previous draft.

User authorized numerical draft refresh; raw Android data and paper prose are
not modified. This command does not run an agent, load weights or call an API.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

raise SystemExit('DISABLED: user requested no manuscript edits; use isolated experiment outputs only.')

root=Path(__file__).resolve().parents[2]
out=Path(__file__).parent/'draft-refresh'
latest=root/'tmp/code-fixes-v6/latest-components'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

sources=json.loads((latest/'SOURCE.json').read_text(encoding='utf-8'))
for name,expected in sources.items():
    if sha(root/'artifact/scripts'/name)!=expected:
        raise RuntimeError('component snapshot source differs: '+name)
resume=sys.argv[1:]==['--resume-interrupted']
if sys.argv[1:] and not resume:raise ValueError('unknown argument')
if not resume:out.mkdir(exist_ok=False)
run=out/'run'
if not resume:
    shutil.copytree(root/'artifact/scripts',run/'artifact/scripts',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(latest/'artifact/results',run/'artifact/results')
    shutil.copytree(root/'manuscript',run/'manuscript',ignore=shutil.ignore_patterns(
        'generated','main.pdf','*.aux','*.log','*.bbl','*.blg','*.out','*.fdb_latexmk','*.fls','*.synctex.gz'))
receipt=dict(status='RUNNING',kind='draft numerical refresh from actual simulation/host runs',
             agent_trials=0,source_sha256=sources,started_utc_ns=time.time_ns(),commands=[])
manifest=out/'PUBLICATION.json'
if resume:
    previous=json.loads(manifest.read_text(encoding='utf-8'))
    if previous['status']!='RUNNING' or previous['commands']:
        raise RuntimeError('only the interrupted pre-output invocation can resume')
    if any((run/'artifact/results'/n).exists() for n in ('planner_sim.csv','planner_class.csv')):
        raise RuntimeError('partial output exists; inspect before resuming')
    receipt['interrupted_invocation']=dict(started_utc_ns=previous['started_utc_ns'],
        reason='tool handle missing; Windows and WSL processes verified absent; no main CSVs',
        log_sha256=sha(out/'planner-main.log'))
def save():manifest.write_text(json.dumps(receipt,indent=2),encoding='utf-8')

def execute(command,cwd,log,timeout):
    start=time.monotonic()
    with log.open('wb') as stream:
        process=subprocess.run(command,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
    receipt['commands'].append(dict(command=command,exit_code=process.returncode,
                                    seconds=time.monotonic()-start,log_sha256=sha(log)))
    save()
    if process.returncode:raise RuntimeError('failed command; inspect '+str(log))

save()
try:
    # Remove only these two copied scratch outputs, so success cannot read a
    # stale main CSV from the previous component snapshot.
    for name in ('planner_sim.csv','planner_class.csv'):
        path=run/'artifact/results'/name
        if path.exists():path.unlink()
    if os.name=='nt' and not resume:
        work='/mnt/'+str(run.resolve())[0].lower()+'/'+str(run.resolve())[3:].replace('\\','/')
        command=['wsl','-d','Ubuntu','--cd',work,'--','python3','-B','artifact/scripts/planner_sim.py','main']
    else:
        command=[sys.executable,'-B','artifact/scripts/planner_sim.py','main']
    print('RUN seeded main, unchanged 5 x 2400 workflows/cell',flush=True)
    execute(command,run,out/'planner-main.log',300)
    with (run/'artifact/results/planner_sim.csv').open(newline='',encoding='utf-8') as stream:
        rows=list(csv.DictReader(stream))
    selected=[row for row in rows if row['policy']=='ghost-src']
    if len(rows)!=24 or len(selected)!=1 or selected[0]['n']!='12000':
        raise RuntimeError('fresh main output has wrong schema/cell count')
    receipt['fresh_source_family_row']=selected[0]
    print('Fresh ASK percent:',selected[0]['ask'],flush=True)
    execute([sys.executable,'-B',str(run/'artifact/scripts/render.py'),
             '--results-dir',str(run/'artifact/results'),
             '--output-dir',str(run/'manuscript/generated')],run,out/'render.log',90)
    # Verify displayed rounding from the data, never an illustrative target.
    macro=(run/'manuscript/generated/macros.tex').read_text(encoding='utf-8')
    expected='\\newcommand{\\SimSrcAsk}{'+format(float(selected[0]['ask']),'.1f')+'\\xspace}'
    if expected not in macro:raise RuntimeError('source ASK macro does not match the fresh CSV')
    publication=[]
    for source in sorted((run/'artifact/results').glob('*.csv')):
        publication.append((source,root/'artifact/results'/source.name))
    for source in sorted((run/'manuscript/generated').glob('*.tex')):
        publication.append((source,root/'manuscript/generated'/source.name))
    before=out/'previous'
    receipt['outputs']=[]
    for source,target in publication:
        rel=target.relative_to(root)
        backup=before/rel
        backup.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():shutil.copy2(target,backup)
        receipt['outputs'].append(dict(file=rel.as_posix(),before_sha256=sha(target) if target.exists() else None,
                                       after_sha256=sha(source)))
    save()
    for source,target in publication:
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=target.with_name('.draft-refresh-'+target.name)
        shutil.copy2(source,temporary);os.replace(temporary,target)
    receipt.update(status='PASS',finished_utc_ns=time.time_ns(),
                   scope='derived CSVs and generated TeX only; raw measurements and prose unchanged',
                   base_run='tmp/code-fixes-v6/full-artifact/RUN.json',
                   component_snapshot='tmp/code-fixes-v6/latest-components/SOURCE.json')
    save()
    print(json.dumps(dict(status=receipt['status'],ask=selected[0]['ask'],
                          outputs=len(publication),manifest=str(manifest))),flush=True)
except BaseException as exc:
    receipt.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc))
    save();raise
