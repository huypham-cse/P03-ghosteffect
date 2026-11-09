from pathlib import Path
import sys,importlib.util,json,time,csv
sys.dont_write_bytecode=True
base=Path(__file__).parent
for name in ['predicate','score_space']:
 sys.path.insert(0,str(base/name))
 spec=importlib.util.spec_from_file_location(name,base/name/'planner_sim.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 started=time.monotonic();out,eff=module.run(['ghost-src']);row=module.summarize(out,eff,['ghost-src'])[0]
 result=dict(kind='default 5x2400 workflows, source union-bound numerical boundary diagnosis',variant=name,seconds=time.monotonic()-started,summary=row)
 (base/(name+'.json')).write_text(json.dumps(result,indent=2));print(name,row,flush=True)
