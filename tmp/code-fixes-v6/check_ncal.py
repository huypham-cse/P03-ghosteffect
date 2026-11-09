from pathlib import Path
import sys,json,csv
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'tmp/code-fixes-v6/baseline/artifact/scripts'))
import planner_sim as old
a,e=old.run(['ghost'],overrides={'ncal_scale':.1})
row=old.summarize(a,e,['ghost'])[0]
full=list(csv.DictReader((root/'tmp/code-fixes-v6/full-artifact/artifact/results/planner_ncal.csv').open()))
new=next(x for x in full if x['policy']=='ghost' and x['ncal']=='200')
archived=list(csv.DictReader((root/'artifact/results/planner_ncal.csv').open()))
archive=next(x for x in archived if x['policy']=='ghost' and x['ncal']=='200')
result=dict(kind='unmodified baseline ncal200, 5x2400',old_source_ask=row['ask'],latest_source_ask=float(new['ask']),archived_ask=float(archive['ask']),old_matches_latest=row['ask']==float(new['ask']))
(Path(__file__).parent/'baseline-ncal200.json').write_text(json.dumps(result,indent=2));print(result)
