"""Record actual test exits/counts; fixtures are not paper trials."""
import hashlib,json,re,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=Path(__file__).parent
host=sys.argv[1]
commands={
 'windows':[sys.executable,'-B','-m','unittest','discover','-s','testbed/tests','-v'],
 'linux':['wsl','-d','Ubuntu','--cd','/mnt/d/NCKH/mobisys/P03-ghosteffect','--',
          'python3','-B','-m','unittest','discover','-s','testbed/tests','-v'],
 'agent-env':[str(root/'runtime/agent-venv/Scripts/python.exe'),'-B','-m','unittest',
              'discover','-s','testbed/tests','-v']}
command=commands[host];log=out/('tests-'+host+'.log');start=time.time_ns()
with log.open('wb') as stream:
 r=subprocess.run(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
text=log.read_text(encoding='utf-8',errors='replace')
count=re.search(r'Ran (\d+) tests? in ',text)
skip=re.search(r'^OK \(skipped=(\d+)\)',text,re.M)
result=dict(host=host,command=command,started_utc_ns=start,finished_utc_ns=time.time_ns(),
            exit_code=r.returncode,tests=int(count[1]) if count else None,
            skipped=int(skip[1]) if skip else 0,
            log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
            source_sha256={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (root/'testbed').rglob('*.py')},
            scope='component/synthetic fixtures and native-source wiring; not Android/model trials')
log.with_suffix('.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}))
print(text[-250:])
sys.exit(r.returncode or (1 if not count else 0))
