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


# Memory settings per GPU (b-log 14/11). They decide how much GPU memory vLLM takes and how many
# requests it batches; they do not change what the model sees or answers. An episode sends one
# request at a time, so max_num_seqs=1 on the 24 GB A10G loses nothing. 0.90 of 22.5 GiB leaves about
# 3 GiB of KV cache after the 15.6 GiB weights; 32768 tokens need 1.75 GiB (56 KiB per token).
GPUS={'h100':dict(name='H100',min_mib=75000,util=dict(singleton=.85,dual=.45),max_num_seqs=2),
      'l40s':dict(name='L40S',min_mib=44000,util=dict(singleton=.85),max_num_seqs=2),
      'a10g':dict(name='A10G',min_mib=22000,util=dict(singleton=.90),max_num_seqs=1)}
PIXELS=dict(min_pixels=3136,max_pixels=3211264)
# Qwen's processor default (12845056) makes vLLM reserve encoder memory for 16384-token images.
# The cap shrinks that reserve to 4096 tokens, and a 1080x2400 screenshot (2408x1092 after
# rounding to 28 px, 2629536 px) stays below it, so no study screenshot is resized.
QWEN_IMAGE_POLICY='max_pixels=3211264, 1080x2400 screenshots not resized'


def image_policy(model):
    return QWEN_IMAGE_POLICY if model['env_prefix']=='QWEN' else 'upstream_recipe'


def command_for(model,snapshot,port,allocation,gpu,python=sys.executable):
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('explicit unprivileged server port required')
    if gpu not in GPUS:raise ValueError('explicit GPU profile required: '+'/'.join(GPUS))
    if allocation not in GPUS[gpu]['util']:raise ValueError('allocation %r is not available on %s'%(allocation,gpu))
    command=[str(python),'-m','vllm.entrypoints.openai.api_server','--model',str(snapshot),
             '--served-model-name',model['repo_id'],'--host','127.0.0.1','--port',str(port),
             '--dtype','bfloat16','--tensor-parallel-size','1','--max-model-len','32768',
             '--load-format','safetensors',
             '--max-num-seqs',str(GPUS[gpu]['max_num_seqs']),'--gpu-memory-utilization',str(GPUS[gpu]['util'][allocation]),
             '--limit-mm-per-prompt',json.dumps({'image':5}), '--generation-config','vllm','--seed','0',
             '--mm-processor-cache-gb','1']   # host RAM only; M3A never resends an identical image
    if model['env_prefix'] in ('GUIOWL','QWEN'):
        command+=['--mm-processor-kwargs',json.dumps(PIXELS)]
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
    parser.add_argument('--gpu',choices=tuple(GPUS),required=True,help='GPU profile; checked against nvidia-smi')
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
    command=command_for(model,snapshot,port,args.allocation,args.gpu)
    profile=GPUS[args.gpu]
    output.mkdir(parents=True)
    receipt=dict(status='PLAN_ONLY' if args.plan else 'STARTING',kind='local pinned model serving',
                 repo_id=model['repo_id'],revision=model['revision'],model_key=args.model,
                 endpoint='http://127.0.0.1:'+str(port)+'/v1',snapshot=str(snapshot),command=command,
                 dtype='bfloat16',max_model_len=32768,max_num_seqs=profile['max_num_seqs'],max_images_per_request=5,
                 allocation=args.allocation,gpu_profile=args.gpu,gpu_memory_utilization=profile['util'][args.allocation],
                 engine_version='0.11.0',image_policy=image_policy(model),history_policy='upstream_recipe',
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
        if (len(hardware)!=1 or profile['name'] not in hardware[0]
                or int(hardware[0].rsplit(',',1)[1].strip())<profile['min_mib']):
            raise RuntimeError('GPU profile %s needs one %s with at least %d MiB; nvidia-smi: %s'
                               %(args.gpu,profile['name'],profile['min_mib'],hardware))
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
        receipt.update(status='FAILED',error_type=type(exc).__name__,error=str(exc)[:500])
        print('FAILED %s: %s'%(type(exc).__name__,exc),file=sys.stderr,flush=True)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:process.wait(30)
            except subprocess.TimeoutExpired:process.kill();process.wait(10)
        receipt['finished_utc_ns']=time.time_ns();save()
    if receipt['status']=='FAILED':raise SystemExit(1)


if __name__=='__main__':main()
