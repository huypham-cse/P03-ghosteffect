from pathlib import Path
import unittest,json,sys,os,time,contextlib,hashlib
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2];os.chdir(root)
base=Path(__file__).parent
host='linux' if os.name=='posix' else 'windows'
results={}
for name,folder in [('artifact','artifact/tests'),('testbed','testbed/tests')]:
 with (base/(name+'-'+host+'.log')).open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
  start=time.monotonic();suite=unittest.TestLoader().discover(folder);r=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 d=dict(status='PASS' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped),seconds=time.monotonic()-start)
 results[name]=d;print(name,d,flush=True)
 if not r.wasSuccessful():print((base/(name+'-'+host+'.log')).read_text());sys.exit(1)
(base/('tests-'+host+'.json')).write_text(json.dumps(results,indent=2))
