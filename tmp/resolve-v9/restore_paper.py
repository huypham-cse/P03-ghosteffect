"""Undo only this turn's numerical manuscript publication, per user request."""
import hashlib,json,os,shutil,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent/'draft-refresh'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
publication=json.loads((out/'PUBLICATION.json').read_text(encoding='utf-8'))
pdf=json.loads((out/'PDF-PUBLICATION.json').read_text(encoding='utf-8'))
entries=[e for e in publication['outputs'] if e['file'].startswith('manuscript/')]
entries.append({k:pdf[k] for k in ('file','before_sha256','after_sha256')})
targets=[]
for entry in entries:
 target=(root/entry['file']).resolve()
 if root/'manuscript' not in target.parents:raise RuntimeError('target outside manuscript')
 backup=out/'previous'/entry['file']
 if not target.is_file() or sha(target)!=entry['after_sha256']:
  raise RuntimeError('current manuscript differs from our published output; preserve it: '+entry['file'])
 if entry['before_sha256'] is not None and (not backup.is_file() or sha(backup)!=entry['before_sha256']):
  raise RuntimeError('missing or changed restoration backup: '+entry['file'])
 targets.append((entry,target,backup))
for entry,target,backup in targets:
 if entry['before_sha256'] is None:
  # Only this exact newly generated file, verified above, is removed.
  target.unlink()
 else:
  temporary=target.with_name('.restore-before-v9-'+target.name)
  shutil.copy2(backup,temporary);os.replace(temporary,target)
for entry,target,backup in targets:
 if entry['before_sha256'] is None:
  if target.exists():raise RuntimeError('new generated file was not removed')
 elif sha(target)!=entry['before_sha256']:raise RuntimeError('restoration hash differs')
receipt=dict(status='PASS',utc_ns=time.time_ns(),reason='user explicitly requested no paper edits; paper deferred',
             restored=[dict(file=e['file'],restored_sha256=e['before_sha256']) for e,_,_ in targets],
             experiment_csvs_retained=True,
             scope='only v9 generated TeX/PDF changes undone; prior worktree changes preserved')
(out/'PAPER-RESTORED.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(dict(status='PASS',restored_files=len(targets),experiment_csvs_retained=True)))
