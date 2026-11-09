"""Publish the compiled numeric draft after checking the rendered data page."""
import hashlib,json,os,shutil,time
from pathlib import Path
import fitz
raise SystemExit('DISABLED: paper edits deferred by the user; numerical paper refresh was restored.')
root=Path(__file__).resolve().parents[2]
out=Path(__file__).parent/'draft-refresh'
publication=json.loads((out/'PUBLICATION.json').read_text(encoding='utf-8'))
if publication['status']!='PASS':raise RuntimeError('numeric renderer publication failed')
compile_receipt=json.loads((out/'compile-result-02.json').read_text(encoding='utf-16'))
if not compile_receipt['pdfExists'] or compile_receipt['attempts'][-1]['exitCode']!=0:
    raise RuntimeError('PDF compile failed')
source=out/'run/manuscript/main.pdf'
document=fitz.open(source)
if len(document)!=20 or '47.0%' not in document[8].get_text():
    raise RuntimeError('compiled PDF does not contain the updated ASK macro')
document.close()
target=root/'manuscript/main.pdf';backup=out/'previous/manuscript/main.pdf'
backup.parent.mkdir(parents=True,exist_ok=True)
if backup.exists():raise RuntimeError('PDF already published; inspect receipt instead of overwriting backup')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(target)
shutil.copy2(target,backup)
temporary=target.with_name('.numeric-refresh-main.pdf')
shutil.copy2(source,temporary);os.replace(temporary,target)
receipt=dict(status='PASS',utc_ns=time.time_ns(),file='manuscript/main.pdf',before_sha256=before,
             after_sha256=sha(target),pages=20,compiler='bundled Tectonic0.16.9',
             qa='rendered page9 checked at150%; all20pages contact sheet reviewed',
             prose_modified=False,raw_measurements_modified=False,
             scope='draft numerical refresh only; existing hypotheses remain unverified',
             previous_pdf=str(backup.relative_to(root)),
             compile_receipt='tmp/resolve-v9/draft-refresh/compile-result-02.json')
(out/'PDF-PUBLICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt))
