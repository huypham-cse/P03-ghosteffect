"""Launch one pinned, locally verified BF16 checkpoint with vLLM0.11.0.

One engine per checkpoint, not per agent role. This does not create a global
multi-engine scheduler, qualify task competence or collect calibration labels.
--plan writes a reviewable command/readiness receipt without loading a model.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

from setup_models import ROOT,LOCK,local_config,project_path,relative_name


def command_for(model,snapshot,port,allocation,python=sys.executable):
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('explicit unprivileged server port required')
    fractions={'singleton':.85,'dual':.45}
    if allocation not in fractions:raise ValueError('explicit singleton/dual allocation required')
    command=[str(python),'-m','vllm.entrypoints.openai.api_server','--model',str(snapshot),
             '--served-model-name',model['repo_id'],'--host','127.0.0.1','--port',str(port),
             '--dtype','bfloat16','--tensor-parallel-size','1','--max-model-len','32768',
             '--load-format','safetensors',
             '--max-num-seqs','2','--gpu-memory-utilization',str(fractions[allocation]),
             '--limit-mm-per-prompt',json.dumps({'image':5}), '--generation-config','vllm','--seed','0']
    if model['env_prefix']=='GUIOWL':
        command+=['--mm-processor-kwargs',json.dumps(dict(min_pixels=3136,max_pixels=3211264))]
    return command


def verify_snapshot(snapshot,model):
    """Verify bytes once before engine load; never trust only a directory name."""
    manifest=json.loads((snapshot/'SNAPSHOT.json').read_text(encoding='utf-8'))
    if (manifest.get('status')!='FILES_VERIFIED_NOT_INFERENCE' or manifest.get('repo_id')!=model['repo_id']
            or manifest.get('revision')!=model['revision']):raise ValueError('snapshot manifest identity differs')
    files=manifest.get('files',[])
    names=[f['file'] for f in files]
    if (len(set(names))!=len(names) or 'config.json' not in names or 'tokenizer_config.json' not in names
            or not any(n in names for n in ('preprocessor_config.json','processor_config.json'))
            or not any(n.endswith('.safetensors') for n in names)):
        raise ValueError('snapshot manifest is incomplete/ambiguous')
    for item in files:
        relative_name(item['file']);path=(snapshot/item['file']).resolve()
        if snapshot.resolve() not in path.parents:raise ValueError('snapshot file resolves outside the selected snapshot')
        if path.stat().st_size!=item['bytes']:raise ValueError('snapshot file size changed: '+item['file'])
        with path.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=item['sha256']:raise ValueError('snapshot file changed: '+item['file'])
    return hashlib.sha256((snapshot/'SNAPSHOT.json').read_bytes()).hexdigest()


def get_json(url):
    with urllib.request.urlopen(url,timeout=3) as reply:return json.load(reply)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=('qwen','uitars','guiowl'),required=True)
    parser.add_argument('--allocation',choices=('singleton','dual'),required=True)
    parser.add_argument('--port',type=int)
    parser.add_argument('--plan',action='store_true',help='write launch plan only; no GPU/model process')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=project_path(str(args.output))
    if output.exists():parser.error('fresh project-local output required')
    _,paths=local_config()
    model=json.loads(LOCK.read_text())['models'][args.model]
    snapshot=paths['MODEL_ROOT']/args.model/model['revision']
    port=args.port or dict(qwen=8101,uitars=8102,guiowl=8103)[args.model]
    command=command_for(model,snapshot,port,args.allocation)
    output.mkdir(parents=True)
    receipt=dict(status='PLAN_ONLY' if args.plan else 'STARTING',kind='local pinned model serving',
                 repo_id=model['repo_id'],revision=model['revision'],model_key=args.model,
                 endpoint='http://127.0.0.1:'+str(port)+'/v1',snapshot=str(snapshot),command=command,
                 dtype='bfloat16',max_model_len=32768,max_num_seqs=2,max_images_per_request=5,
                 allocation=args.allocation,gpu_memory_utilization=.85 if args.allocation=='singleton' else .45,
                 engine_version='0.11.0',image_policy='upstream_recipe',history_policy='upstream_recipe',
                 global_inflight_limit_implemented_here=False,started_utc_ns=time.time_ns(),models_loaded=False,
                 checkpoint_files_verified=False,task_quality_verified=False,api_provider_fallback=False)
    manifest=output/'SERVING.json'
    def save():manifest.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    save()
    if args.plan:
        print(json.dumps(dict(status='PLAN_ONLY',command=command,weights_present=(snapshot/'SNAPSHOT.json').is_file())))
        return
    process=None
    try:
        if os.name!='posix' or importlib.metadata.version('vllm')!='0.11.0':
            raise RuntimeError('Linux with pinned vLLM0.11.0 required; no runtime fallback')
        hardware=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total','--format=csv,noheader,nounits'],
                                check=True,capture_output=True,text=True,timeout=15).stdout.strip().splitlines()
        if len(hardware)!=1 or 'H100' not in hardware[0] or int(hardware[0].rsplit(',',1)[1].strip())<75000:
            raise RuntimeError('the selected recipe targets one full H10080GB; actual hardware differs')
        receipt['hardware']=hardware
        receipt['snapshot_manifest_sha256']=verify_snapshot(snapshot,model)
        receipt['checkpoint_files_verified']=True
        with socket.socket() as probe:probe.bind(('127.0.0.1',port))
        # Serving is offline after a full snapshot verification; no credentials
        # or network downloads are needed in the engine process.
        allowed=('PATH','HOME','USER','LANG','LC_ALL','LD_LIBRARY_PATH','CUDA_HOME','CUDA_PATH',
                 'TMPDIR','NVIDIA_VISIBLE_DEVICES','NVIDIA_DRIVER_CAPABILITIES')
        env={k:v for k,v in os.environ.items() if k in allowed}
        env.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HOME=str(paths['HF_HOME']),
                   HF_HUB_CACHE=str(paths['HF_HUB_CACHE']),TORCH_HOME=str(paths['TORCH_HOME']),
                   CUDA_VISIBLE_DEVICES='0',VLLM_NO_USAGE_STATS='1',DO_NOT_TRACK='1')
        with (output/'server.log').open('wb') as log:
            process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env)
            receipt['owned_pid']=process.pid;save();deadline=time.monotonic()+1200
            while time.monotonic()<deadline:
                if process.poll() is not None:raise RuntimeError('model engine exited; inspect the retained server log')
                try:
                    version=get_json(receipt['endpoint'][:-3]+'/version')
                    models=get_json(receipt['endpoint']+'/models')
                except OSError:
                    time.sleep(1);continue
                cards=[m for m in models['data'] if m['id']==model['repo_id']]
                if version.get('version')!='0.11.0':raise ValueError('server version differs')
                if len(cards)!=1 or cards[0].get('root')!=str(snapshot) or cards[0].get('max_model_len')!=32768:
                    raise ValueError('live model/card/context differs from the launch recipe')
                break
            else:raise TimeoutError('model startup exceeded hard timeout')
            receipt.update(status='MODEL_SERVING_READY',models_loaded=True,ready_utc_ns=time.time_ns(),
                           server_version=version,model_card=cards[0]);save()
            print('MODEL_SERVING_READY '+str(manifest),flush=True)
            # Foreground lifetime: caller stops this process to close only the
            # engine it owns. No daemon registry or automatic engine swapping.
            process.wait()
            receipt.update(status='STOPPED' if process.returncode==0 else 'FAILED',exit_code=process.returncode)
    except KeyboardInterrupt:
        receipt['status']='STOPPED'
    except Exception as exc:
        receipt.update(status='FAILED',error_type=type(exc).__name__)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:process.wait(30)
            except subprocess.TimeoutExpired:process.kill();process.wait(10)
        receipt['finished_utc_ns']=time.time_ns();save()
    if receipt['status']=='FAILED':raise SystemExit(1)


if __name__=='__main__':main()
