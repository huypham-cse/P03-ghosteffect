import unittest,json,pathlib,sys,time,os
sys.dont_write_bytecode=True
root=pathlib.Path(__file__).resolve().parents[3]
os.chdir(root)
for name,folder in [('artifact','artifact/tests'),('testbed','testbed/tests')]:
 if len(sys.argv)>1 and name not in sys.argv[1:]: continue
 out=pathlib.Path(__file__).parent
 host='linux' if os.name=='posix' else 'windows'
 with (out/(name+'-'+host+'.log')).open('w',encoding='utf-8') as log:
  suite=unittest.TestLoader().discover(folder);start=time.monotonic();res=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 d=dict(status='PASS' if res.wasSuccessful() else 'FAIL',tests=res.testsRun,failures=len(res.failures),errors=len(res.errors),skipped=len(res.skipped),seconds=time.monotonic()-start)
 (out/(name+'-'+host+'.json')).write_text(json.dumps(d,indent=2));print(name,d,flush=True)
 if not res.wasSuccessful():print((out/(name+'-'+host+'.log')).read_text());sys.exit(1)
