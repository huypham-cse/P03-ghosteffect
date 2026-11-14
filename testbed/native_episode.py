"""Native M3A/T3A development episode against a verified local/forwarded engine.

Delegates the loop to pinned AndroidWorld.run_episode. Backend/reset/fault/grader
stay outside the agent. Prepare the isolated test AVD before this command; this
does not claim a P40 fixture or full benchmark implementation. There is no
synthetic-response switch or fallback in this runner.
"""
import argparse
from dataclasses import asdict,is_dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit

from setup_models import ROOT,LOCK,project_path
from serve_model import get_json,QWEN_IMAGE_POLICY


def serving_contract(file,endpoint):
    receipt=json.loads(Path(file).read_text(encoding='utf-8'))
    model=json.loads(LOCK.read_text())['models']['qwen']
    parsed=urlsplit(endpoint)
    if (parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost','::1')
            or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path!='/v1'):
        raise ValueError('explicit loopback/SSH-forwarded v1 endpoint required')
    if (receipt.get('status')!='MODEL_SERVING_READY' or receipt.get('repo_id')!=model['repo_id']
            or receipt.get('revision')!=model['revision'] or receipt.get('dtype')!='bfloat16'
            or receipt.get('max_model_len')!=32768 or receipt.get('engine_version')!='0.11.0'
            or not receipt.get('checkpoint_files_verified') or not receipt.get('models_loaded')
            or receipt.get('image_policy')!=QWEN_IMAGE_POLICY or receipt.get('history_policy')!='upstream_recipe'):
        raise ValueError('serving receipt is not a ready pinned Qwen BF16 engine')
    # A copied server receipt may name its original port. Endpoint may instead
    # be an SSH forward; live card/root/version must still match that server.
    version=get_json(endpoint[:-3]+'/version')
    cards=get_json(endpoint+'/models')['data']
    selected=[c for c in cards if c['id']==model['repo_id']]
    if (version.get('version')!='0.11.0' or len(selected)!=1 or selected[0].get('root')!=receipt['snapshot']
            or selected[0].get('max_model_len')!=32768):raise ValueError('live server differs from receipt')
    return receipt


def save_data(value,directory,label):
    """Lossless image payloads plus native dataclasses/raw responses for audit."""
    import numpy as np
    if isinstance(value,np.ndarray):
        if value.dtype!=np.uint8 or len(value.shape)!=3 or value.shape[2] not in (3,4):
            raise ValueError('unexpected native array; no silent truncation/conversion')
        from PIL import Image
        file=label+'.png';Image.fromarray(value).save(directory/file)
        return dict(file=file,shape=list(value.shape),sha256=hashlib.sha256((directory/file).read_bytes()).hexdigest())
    if is_dataclass(value):return save_data(asdict(value),directory,label)
    if isinstance(value,dict):return {k:save_data(v,directory,label+'-'+k) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [save_data(v,directory,label+'-'+str(i)) for i,v in enumerate(value)]
    if value is None or isinstance(value,(str,int,float,bool)):return value
    raise TypeError('unsupported native result payload: '+type(value).__name__)


def worker(args):
    from androidworld_env import verify_source,load_env,make_agent,EpochStop
    from faultproxy import Journal
    from android_world import episode_runner
    log=Journal(args.output/'agent-trace.jsonl')
    receipt=serving_contract(args.serving_receipt,args.endpoint)
    result=dict(status='RUNNING',kind='model-driven native development episode',framework=args.framework,
                task_success=None,backend_grade=None,scientific_cohort=None,
                goal_sha256=hashlib.sha256(args.goal_file.read_bytes()).hexdigest(),
                model_repo_id=receipt['repo_id'],model_revision=receipt['revision'],
                serving_receipt_sha256=hashlib.sha256(args.serving_receipt.read_bytes()).hexdigest(),
                max_steps=args.max_steps,started_utc_ns=time.time_ns(),steps_completed=0,
                source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in Path(__file__).parent.rglob('*.py')})
    env=None
    try:
        result['native_source']=verify_source(ROOT/'runtime/vendor/android_world_full')
        env=load_env(args.adb,args.console_port,args.adb_server_port,args.grpc_port,freeze_datetime=False)
        agent=make_agent(args.framework,env,args.endpoint,receipt['repo_id'],journal=log)
        native_step=agent.step
        def traced_step(goal):
            index=result['steps_completed']
            log.emit('STEP_BEGIN',index=index)
            try:step=native_step(goal)
            except BaseException:
                log.emit('STEP_INTERRUPTED',index=index)
                raise
            folder=args.output/('step-%04d'%index);folder.mkdir()
            data=save_data(step.data,folder,'native')
            (folder/'step.json').write_text(json.dumps(dict(agent_done=step.done,data=data),indent=2),encoding='utf-8')
            result['steps_completed']+=1
            log.emit('STEP_END',index=index,agent_done=step.done)
            return step
        agent.step=traced_step
        goal=args.goal_file.read_text(encoding='utf-8').strip()
        # Use upstream reset, max-step handling and done semantics unchanged.
        episode=episode_runner.run_episode(goal,agent,max_n_steps=args.max_steps,
            start_on_home_screen=False,termination_fn=None,print_fn=lambda s:log.emit('NATIVE_RUNNER',message=s))
        result.update(status='AGENT_STOPPED' if episode.done else 'STEP_LIMIT',agent_done=episode.done,
                      scope='agent belief/trace only; independent backend grader/reset/fault/follow-up still required')
    except EpochStop as exc:
        result.update(status='HOST_STOP',reason=str(exc))
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__)
        raise
    finally:
        if env is not None:env.close()
        result['finished_utc_ns']=time.time_ns()
        (args.output/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--framework',choices=('m3a','t3a'),required=True)
    parser.add_argument('--goal-file',type=Path,required=True)
    parser.add_argument('--max-steps',type=int,required=True)
    parser.add_argument('--timeout-seconds',type=float,required=True)
    parser.add_argument('--serving-receipt',type=Path,required=True)
    parser.add_argument('--endpoint',required=True)
    parser.add_argument('--adb',type=Path,required=True)
    parser.add_argument('--console-port',type=int,required=True)
    parser.add_argument('--adb-server-port',type=int,required=True)
    parser.add_argument('--grpc-port',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    args.output=project_path(str(args.output))
    if not args.goal_file.is_file() or not args.goal_file.read_text(encoding='utf-8').strip():parser.error('nonempty goal file required')
    if not 1<=args.max_steps<=1000 or not 0<args.timeout_seconds<=7200:parser.error('explicit bounded steps/deadline required')
    if args.worker:worker(args);return
    if args.output.exists():parser.error('fresh output directory required')
    # Verify the model before touching the AVD, then recheck in the worker.
    serving_contract(args.serving_receipt,args.endpoint)
    args.output.mkdir(parents=True)
    os_names=('SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA','PROGRAMDATA',
              'PATHEXT','COMSPEC','PATH','HOME','USER','LANG','LC_ALL','LD_LIBRARY_PATH','TMPDIR')
    env={k:v for k,v in os.environ.items() if k.upper() in os_names}
    command=[sys.executable,'-B',str(Path(__file__).resolve()),*sys.argv[1:],'--worker']
    with (args.output/'worker.log').open('wb') as stream:
        try:
            reply=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=env,timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            log=dict(status='TIMEOUT',kind='model-driven native development episode',
                     timeout_seconds=args.timeout_seconds,task_success=None,backend_grade=None,
                     scope='partial raw step data retained; no automatic retry or task-success inference')
            (args.output/'TIMEOUT.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
            raise SystemExit(124)
    if reply.returncode:raise SystemExit(reply.returncode)
    print('Native development trace: '+str(args.output/'RESULT.json'))


if __name__=='__main__':main()
