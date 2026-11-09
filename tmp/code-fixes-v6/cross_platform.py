from pathlib import Path
import sys,importlib.util,json,time,os
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
old_scripts=root/'tmp/code-fixes-v6/baseline/artifact/scripts'
sys.path.insert(0,str(old_scripts))
import planner_sim as old
start=time.monotonic()
a,e=old.run(['ghost-src'])
r=old.summarize(a,e,['ghost-src'])[0]
result=dict(host=os.name,kind='unmodified pre-fix source, default 5x2400 workflows',seconds=time.monotonic()-start,summary=r)
out=Path(__file__).parent/('baseline-full-'+os.name+'.json');out.write_text(json.dumps(result,indent=2));print(result,flush=True)
