"""Paper-contract tests with explicitly SYNTHETIC calibration effects and clock.

Exercise certified decisions, class intersection, censoring and restart failure
boundaries. These fixtures are never exported as measured Android calibration.
"""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import signal
import subprocess
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from calibration import compile_store, load_store, canonical_sha, DOMAIN_KEYS, SCHEMA, bound_count
from recovery import Recovery
from controller import HostController
from faultproxy import Journal


def fixture(mode='joint',local=False,hop=False,classes=('app-kill',),n=3000):
    domain={key:'SYNTHETIC-'+key for key in DOMAIN_KEYS}
    domain.update(app_package='test.app',origin_kind='recovery')
    names=(['hop1'] if hop else [])+['nonce','digest','vlm']
    families={name:[name+'-'+str(i) for i in range(3 if name=='vlm' else 2)] for name in names}
    cap=dict(local=local,G2=hop,hop1_qualified=hop,nonce_analytic_qualified=False,
             family_independence_qualified=True,source_independence_qualified=True,
             hop1_lag_independent=False,backend_visibility_domain_qualified=True)
    item=dict(id='test',domain=domain,families=families,classes=list(classes),capabilities=cap,
              quota=dict(pilot0=20,pilot1=20,calibration0=n,calibration1=n,lag1=0))
    spec=dict(schema=SCHEMA,mode=mode,evidence_kind='synthetic_fixture',alpha=.01,beta=.01,strata=[item])
    rows=[]
    for cls in classes:
        for split in ('pilot','calibration'):
            for x in (0,1):
                for i in range(item['quota'][split+str(x)]):
                    rows.append(dict(effect_id=f'{cls}-{split}-{x}-{i}',stratum='test',domain=domain,
                                     fault_class=cls,X_backend=x,split=split,population='interrupted',
                                     evidence_kind='synthetic_fixture',probe_eligibility_verified=True,
                                     views={name:[x]*len(views) for name,views in families.items()},
                                     lag_upper_seconds=10 if x else None,origin_kind='recovery',origin_verified=True))
    return spec,rows


class Clock:
    def __init__(self,t=100):
        self.t=t
    def now(self):
        return self.t
    def sleep(self,t):
        self.t+=t


class Observer:
    def __init__(self,clock,values=None,monitor=None):
        self.clock,self.values,self.calls=clock,values or {},[]
        self.monitor_value=monitor or dict(state='acked',end_to_end_ready=True)
        self.valid=True
    def verify_context(self):
        return self.valid
    def read(self,family,view):
        self.calls.append((family,view,self.clock.now()))
        value=self.values.get(family,0)
        return value[int(view.rsplit('-',1)[1])] if isinstance(value,list) else value
    def monitor(self):
        return self.monitor_value


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec,cls.rows=fixture()
        cls.store=compile_store(cls.spec,cls.rows)

    def test_synthetic_store_cannot_authorize_production_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'store.json';path.write_text(json.dumps(self.store))
            with self.assertRaisesRegex(ValueError,'synthetic'):
                load_store(path)
            self.assertEqual(load_store(path,allow_synthetic=True)['effects'],len(self.rows))
            changed=copy.deepcopy(self.store);changed['alpha']=.2;path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError,'modified'):
                load_store(path,True)

    def test_effect_duplicates_passive_and_eval_cannot_be_labels(self):
        for changes in ({'population':'passive'},{'split':'eval'},{'probe_eligibility_verified':False},
                        {'origin_verified':False},{'X_backend':True}):
            rows=[dict(self.rows[0],**changes)]+self.rows[1:]
            with self.assertRaises(ValueError):
                compile_store(self.spec,rows)
        with self.assertRaisesRegex(ValueError,'once'):
            compile_store(self.spec,self.rows+[self.rows[0]])

    def test_rehashed_malformed_store_still_cannot_authorize_decisions(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'store.json'
            for change in ('bound','lags','counts','table','spec'):
                store=copy.deepcopy(self.store);record=store['strata'][0]['calibrated']['app-kill']
                if change=='bound':record['q']['nonce']['abs'][2]=-1
                elif change=='lags':record['lag_seconds']=[-1]*3000
                elif change=='counts':record['counts']['calibration0']=1
                elif change=='table':record['abs_tab']=[[0,-1]]
                else:store['spec']['alpha']=.1
                store.pop('content_sha256');store['content_sha256']=canonical_sha(store)
                path.write_text(json.dumps(store))
                with self.assertRaises(ValueError):load_store(path,True)

    def test_fixed_quota_and_independence_qualifications(self):
        with self.assertRaisesRegex(ValueError,'quota'):
            compile_store(self.spec,self.rows[:-1])
        spec=copy.deepcopy(self.spec);spec['mode']='product'
        spec['strata'][0]['capabilities']['family_independence_qualified']=False
        with self.assertRaisesRegex(ValueError,'A2'):
            compile_store(spec,self.rows)

    def test_pilot_cannot_be_reused_as_lag_holdout(self):
        spec=copy.deepcopy(self.spec);spec['strata'][0]['lag_splits']=['pilot']
        with self.assertRaisesRegex(ValueError,'pilot'):
            compile_store(spec,self.rows)

    def test_censored_lags_remain_exceedances_not_zero(self):
        rows=[dict(r,lag_upper_seconds=None) if r['X_backend']==1 else r for r in self.rows]
        store=compile_store(self.spec,rows)
        fitted=store['strata'][0]['calibrated']['app-kill']
        self.assertEqual(fitted['lag_censored'],3000)
        self.assertEqual(fitted['lag_seconds'],[])
        result,obs,clock=run_recovery(store)
        self.assertEqual(result['decision'],'ASK')
        self.assertEqual(obs.calls,[])

    def test_real_measurement_requires_hash_linked_evidence(self):
        spec=copy.deepcopy(self.spec);spec['evidence_kind']='interrupted_measurement'
        rows=[dict(r,evidence_kind='interrupted_measurement') for r in self.rows]
        with self.assertRaisesRegex(ValueError,'evidence'):
            compile_store(spec,rows)

    def test_actual_k_counts_modes_domains_classes_and_nonce_qualification(self):
        spec,rows=fixture(hop=True,classes=('agent-kill','app-kill'),n=5)
        item=spec['strata'][0]
        item['capabilities'].update(hop1_lag_independent=True,nonce_analytic_qualified=True)
        item['nonce_contract']=dict(symbols=6,alphabet='0123456789ABCDEFGHJKMNPQRSTVWXYZ',edit_distance=1,
                                    max_visible_tokens=40,no_uncommitted_nonce_visible=True)
        self.assertEqual(bound_count(item,'product'),11)
        self.assertEqual(bound_count(item,'joint'),5)
        self.assertEqual(bound_count(item,'source'),8)
        store=compile_store(spec,rows)
        self.assertEqual(store['K_total'],10)
        self.assertEqual(store['delta'],.01/100)

    def test_source_score_threshold_grid_is_pilot_only(self):
        spec,rows=fixture(mode='source',hop=True,n=200)
        first=compile_store(spec,rows)
        changed=[]
        for row in rows:
            r=copy.deepcopy(row)
            if r['split']=='calibration':
                r['views']['hop1']=[1-r['X_backend']]*2
            changed.append(r)
        second=compile_store(spec,changed)
        a=first['strata'][0]['calibrated']['app-kill']
        b=second['strata'][0]['calibrated']['app-kill']
        self.assertEqual([t for _,t in a['abs_tab']],[t for _,t in b['abs_tab']])
        self.assertNotEqual(a['qh'],b['qh'])


def run_recovery(store,values=None,context_changes=None,domain_changes=None,monitor=None):
    clock=Clock()
    obs=Observer(clock,values,monitor)
    domain=dict(store['strata'][0]['domain']);domain.update(domain_changes or {})
    context=dict(fault_class='app-kill',origin_kind='recovery',origin_mono_seconds=100,
                 origin_verified=True,g2_eligible=True,dedup_horizon_seconds=1000,issued_mono_seconds=95)
    context.update(context_changes or {})
    result=Recovery(store,obs,clock.now,clock.sleep).resolve(domain,context)
    return result,obs,clock


class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec,rows=fixture();cls.store=compile_store(spec,rows)

    def test_absence_waits_from_recovery_then_retries_and_checks_foreground(self):
        result,obs,clock=run_recovery(self.store)
        self.assertEqual(result['decision'],'RETRY')
        self.assertTrue(all(t>=110 for _,_,t in obs.calls))
        self.assertEqual(len(obs.calls),len(set((a,b) for a,b,_ in obs.calls)))

    def test_committed_and_small_calibration_ask_paths(self):
        result,_,_=run_recovery(self.store,dict(nonce=1,digest=1,vlm=1))
        self.assertEqual(result['decision'],'COMMITTED')
        spec,rows=fixture(n=4);store=compile_store(spec,rows)
        result,_,_=run_recovery(store)
        self.assertEqual(result['decision'],'ASK')

    def test_missing_origin_wrong_domain_idle_or_force_context_fail_closed(self):
        for changes in ({'origin_kind':'tap'},{'origin_verified':False},{'origin_mono_seconds':101},
                        {'fault_class':'UNSEEN'},{'new_fault_since_origin':True},{'idle_domain_changed':True}):
            result,obs,_=run_recovery(self.store,context_changes=changes)
            self.assertEqual(result['decision'],'ASK')
            self.assertEqual(obs.calls,[])
        result,_,_=run_recovery(self.store,domain_changes={'abi':'DIFFERENT'})
        self.assertEqual(result['reason'],'unsupported_domain')

    def test_bot_and_contradiction_do_not_become_absence(self):
        values=dict(nonce=None,digest=[0,1],vlm=[None,0,0])
        result,_,_=run_recovery(self.store,values)
        self.assertEqual(result['decision'],'ASK')
        # Disable early threshold crossing to reach a contradictory later family.
        spec,rows=fixture(local=True,n=10);store=compile_store(spec,rows)
        result,_,_=run_recovery(store,dict(nonce=0,digest=1,vlm=0))
        self.assertEqual(result['reason'],'family_disagreement')

    def test_local_returns_lag_budget_to_test_without_network_wait(self):
        spec,rows=fixture(local=True,n=1600);store=compile_store(spec,rows)
        result,obs,clock=run_recovery(store)
        self.assertEqual(result['decision'],'RETRY')
        self.assertEqual(clock.now(),100)
        budget=next(x for x in result['trace'] if x['event']=='BUDGET')
        self.assertEqual(budget['alpha_lag'],0)
        self.assertEqual(budget['alpha_test'],.009000000000000001)

    def test_unknown_class_intersection_can_only_reduce_actions(self):
        spec,rows=fixture(classes=('agent-kill','app-kill'))
        for row in rows:
            if row['fault_class']=='agent-kill' and row['X_backend']==1:
                row['views']={name:[0]*len(v) for name,v in row['views'].items()}
        store=compile_store(spec,rows)
        known,_,_=run_recovery(store)
        unknown,_,_=run_recovery(store,context_changes={'fault_class':None})
        self.assertEqual(known['decision'],'RETRY')
        self.assertEqual(unknown['decision'],'ASK')

    def test_unknown_class_uses_maximum_deadline_with_each_classes_own_clock(self):
        spec,rows=fixture(classes=('agent-kill','app-kill'))
        item=spec['strata'][0]
        item['domain']['origin_kind']='per_class'
        item['class_origins']={'agent-kill':'issued','app-kill':'recovery'}
        for row in rows:
            row['origin_kind']=item['class_origins'][row['fault_class']]
            if row['X_backend']==1:
                row['lag_upper_seconds']=50 if row['fault_class']=='agent-kill' else 10
        store=compile_store(spec,rows)
        clocks={'issued':dict(origin_kind='issued',origin_verified=True,origin_mono_seconds=80),
                'recovery':dict(origin_kind='recovery',origin_verified=True,origin_mono_seconds=100)}
        result,obs,clock=run_recovery(store,context_changes=dict(fault_class=None,origins=clocks))
        self.assertEqual(result['decision'],'RETRY')
        self.assertEqual(clock.now(),130)
        self.assertTrue(all(t>=130 for _,_,t in obs.calls))
        clocks.pop('issued')
        result,obs,_=run_recovery(store,context_changes=dict(fault_class=None,origins=clocks))
        self.assertEqual(result['reason'],'unknown_or_mismatched_origin')
        self.assertEqual(obs.calls,[])

    def test_monitor_cannot_reset_stuck_or_dedup_age_to_relaunch(self):
        spec,rows=fixture(hop=True,n=10);store=compile_store(spec,rows)
        for issue in (-100,None):
            result,_,_=run_recovery(store,dict(hop1=1),context_changes=dict(issued_mono_seconds=issue),monitor=dict(state='pending'))
            self.assertNotEqual(result['decision'],'PENDING')

    def test_g2_pending_then_terminal_failed_handover_and_force_stop_downgrade(self):
        spec,rows=fixture(hop=True,n=10);store=compile_store(spec,rows)
        result,obs,_=run_recovery(store,dict(hop1=1),monitor=dict(state='pending'))
        self.assertEqual(result['decision'],'PENDING')
        self.assertEqual(len(obs.calls),2)
        result,_,_=run_recovery(store,dict(hop1=1),monitor=dict(state='failed'))
        self.assertEqual(result['decision'],'ASK')
        result,_,_=run_recovery(store,dict(hop1=1),context_changes={'force_stopped':True},monitor=dict(state='pending'))
        self.assertNotEqual(result['decision'],'PENDING')
        self.assertFalse(next(x for x in result['trace'] if x['event']=='BUDGET')['g2'])


class ControllerRecoveryTests(unittest.TestCase):
    def test_production_commit_checks_identity_before_and_after_durable_issue(self):
        class Device:
            taps=0
            def foreground(self):return 'test.app/.Main'
            def tap(self,x,y):self.taps+=1
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);device=Device()
            controller=HostController(directory/'ledger.db',device,Journal(directory/'events.jsonl'))
            controller.prepare('e','wf',1,'test.app','send',b'old',app_version='1.0')
            with self.assertRaises(RuntimeError):controller.dispatch('e','test.app',1,1)
            self.assertEqual(controller.ledger.state('e'),'PLANNED')
            answers=iter((True,False))
            with self.assertRaises(RuntimeError):
                controller.dispatch('e','test.app',1,1,context_guard=lambda:next(answers))
            self.assertEqual(controller.ledger.state('e'),'ISSUED')
            self.assertEqual(device.taps,0)
            controller.close()

    def test_saved_lookalike_skips_vlm_even_when_caller_omits_flag(self):
        spec,rows=fixture(local=True,n=5);store=compile_store(spec,rows)
        class Device:
            def foreground(self):return 'test.app/.Main'
            def tap(self,x,y):pass
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);certificate=directory/'cert.json';certificate.write_text(json.dumps(store))
            controller=HostController(directory/'ledger.db',Device(),Journal(directory/'events.jsonl'))
            controller.prepare('e','wf',1,'test.app','send',b'old',semantic_snapshot={'verdict':'SNAPSHOT','snapshot':{'matches':1}})
            controller.dispatch('e','test.app',1,1)
            clock=Clock();obs=Observer(clock)
            context=dict(fault_class='app-kill',origin_kind='recovery',origin_mono_seconds=100,origin_verified=True)
            controller.recover('e',certificate,spec['strata'][0]['domain'],context,obs,True,clock.now,clock.sleep)
            self.assertFalse(any(family=='vlm' for family,_,_ in obs.calls))
            self.assertNotIn('lookalike',context)
            controller.close()

    @unittest.skipUnless(os.name=='posix','actual SIGKILL boundary requires POSIX')
    def test_sigkill_after_started_marker_prevents_new_vote_after_process_restart(self):
        spec,rows=fixture(local=True,n=20);store=compile_store(spec,rows)
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);certificate=directory/'cert.json';certificate.write_text(json.dumps(store))
            worker=directory/'worker.py'
            worker.write_text('''import sys,time,json,os
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from controller import HostController
from faultproxy import Journal
base=Path(sys.argv[2]);store=json.loads((base/'cert.json').read_text())
class Device:
 def foreground(self):return 'test.app/.Main'
 def tap(self,x,y):pass
class Observer:
 def verify_context(self):return True
 def read(self,family,view):
  with (base/'acquired').open('w') as f:f.write(family+'/'+view);f.flush();os.fsync(f.fileno())
  time.sleep(60)
c=HostController(base/'ledger.db',Device(),Journal(base/'events.jsonl'))
c.prepare('e','wf',1,'test.app','send',b'old');c.dispatch('e','test.app',1,1)
ctx=dict(fault_class='app-kill',origin_kind='recovery',origin_mono_seconds=100,origin_verified=True)
c.recover('e',base/'cert.json',store['strata'][0]['domain'],ctx,Observer(),True,lambda:100,lambda t:None)
''')
            process=subprocess.Popen([sys.executable,'-I',str(worker),str(Path(__file__).resolve().parents[1]),str(directory)],
                                     stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            try:
                deadline=time.monotonic()+15
                while not (directory/'acquired').exists():
                    if process.poll() is not None:self.fail(process.stderr.read().decode())
                    if time.monotonic()>deadline:self.fail('writer never acquired a view')
                    time.sleep(.01)
                process.send_signal(signal.SIGKILL)
                self.assertEqual(process.wait(5),-signal.SIGKILL)
                class Device:
                    def foreground(self):return 'test.app/.Main'
                    def tap(self,x,y):pass
                controller=HostController(directory/'ledger.db',Device(),Journal(directory/'events.jsonl'))
                observer=Observer(Clock());context=dict(fault_class='app-kill',origin_kind='recovery',origin_mono_seconds=100,origin_verified=True)
                result=controller.recover('e',certificate,spec['strata'][0]['domain'],context,observer,True,lambda:100,lambda t:None)
                self.assertNotIn(('nonce','nonce-0'),[(a,b) for a,b,_ in observer.calls])
                self.assertEqual(result['decision'],'ASK')
                controller.close()
            finally:
                if process.poll() is None:process.kill();process.wait()
                process.stderr.close()

    def test_certified_settlement_and_crash_mid_read_does_not_resample(self):
        spec,rows=fixture(local=True);store=compile_store(spec,rows)
        clock=Clock();owner=self
        class Device:
            def foreground(self):return 'test.app/.Main'
            def tap(self,x,y):pass
        class CrashObserver(Observer):
            def read(self,family,view):
                super().read(family,view)
                raise KeyboardInterrupt('synthetic controller death after starting read')
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);certificate=directory/'cert.json';certificate.write_text(json.dumps(store))
            db=directory/'ledger.db';journal=Journal(directory/'events.jsonl')
            controller=HostController(db,Device(),journal)
            controller.prepare('e','wf',1,'test.app','send',b'old')
            controller.dispatch('e','test.app',1,1)
            context=dict(fault_class='app-kill',origin_kind='recovery',origin_mono_seconds=100,origin_verified=True)
            crash=CrashObserver(clock)
            with self.assertRaises(KeyboardInterrupt):
                controller.recover('e',certificate,spec['strata'][0]['domain'],context,crash,True,clock.now,clock.sleep)
            controller.close()
            restarted=HostController(db,Device(),journal);obs=Observer(clock)
            result=restarted.recover('e',certificate,spec['strata'][0]['domain'],context,obs,True,clock.now,clock.sleep)
            self.assertNotIn(('nonce','nonce-0'),[(a,b) for a,b,_ in obs.calls])
            count=len(obs.calls)
            if result['decision']=='ASK':
                restarted.recover('e',certificate,spec['strata'][0]['domain'],context,obs,True,clock.now,clock.sleep)
                self.assertEqual(len(obs.calls),count)
            self.assertIn(restarted.ledger.state('e'),('ABSENT','ASKED'))
            restarted.close()

    def test_production_controller_rejects_fixture_and_never_auto_dispatches_retry(self):
        spec,rows=fixture(local=True);store=compile_store(spec,rows)
        class Device:
            taps=0
            def foreground(self):return 'test.app/.Main'
            def tap(self,x,y):self.taps+=1
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);certificate=directory/'cert.json';certificate.write_text(json.dumps(store))
            device=Device();controller=HostController(directory/'ledger.db',device,Journal(directory/'events.jsonl'))
            controller.prepare('e','wf',1,'test.app','send',b'old');controller.dispatch('e','test.app',1,1)
            clock=Clock();obs=Observer(clock)
            result=controller.recover('e',certificate,spec['strata'][0]['domain'],{},obs)
            self.assertEqual(result['decision'],'ASK')
            self.assertEqual(device.taps,1)
            self.assertEqual(obs.calls,[])
            controller.close()


if __name__=='__main__':
    unittest.main()
