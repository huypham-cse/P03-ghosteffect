import pathlib,unittest,contextlib,json,sys,time,os,hashlib
sys.dont_write_bytecode=True
root=pathlib.Path(__file__).resolve().parents[2];os.chdir(root)
folder=root/'tmp/resolve-v7/component-final';folder.mkdir(exist_ok=True)
host='linux' if os.name=='posix' else 'windows'
files=list((root/'testbed').rglob('*.py'))
sources={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if '__pycache__' not in str(p)}
start=time.monotonic()
with (folder/(host+'.log')).open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
 result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.TestLoader().discover('testbed/tests'))
record=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),seconds=time.monotonic()-start,source_sha256=sources,scope='component fixtures and loopback; no measured calibration/agent trials')
(folder/(host+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='source_sha256'}))
if not result.wasSuccessful():sys.exit(1)
