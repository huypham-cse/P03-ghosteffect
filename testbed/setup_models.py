"""Inspect/download exact HF snapshots into this project; never run inference.

Only public model Hub file APIs are used. No Inference Provider/fallback/paid
model calls. Cache setup occurs before importing huggingface_hub. Receipts never
include HF_TOKEN or the contents of .env.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path,PurePosixPath
import time

ROOT=Path(__file__).resolve().parents[1]
LOCK=Path(__file__).with_name('models.lock.json')


def project_path(value,root=ROOT):
    path=(root/value).resolve()
    if path==root.resolve() or root.resolve() not in path.parents:
        raise ValueError('model/cache files must stay in a project subdirectory')
    if path.relative_to(root.resolve()).parts[0] in ('manuscript','artifact','others'):
        raise ValueError('model/cache outputs cannot write to manuscript or research inputs')
    return path


def local_config(root=ROOT):
    config={}
    file=root/'.env'
    if file.is_file():
        for line in file.read_text(encoding='utf-8-sig').splitlines():
            line=line.strip()
            if not line or line.startswith('#'):continue
            key,separator,value=line.partition('=')
            if not separator:raise ValueError('invalid project .env syntax; contents are not logged')
            key,value=key.strip(),value.strip()
            if len(value)>1 and value[0]==value[-1] and value[0] in ('"',"'"):value=value[1:-1]
            config[key]=value
    # Explicit process config takes precedence over the template, without
    # exporting arbitrary credentials to subprocesses or receipts.
    for key in ('HF_TOKEN','HF_HOME','HF_HUB_CACHE','HF_XET_CACHE','TORCH_HOME','MODEL_ROOT',
                'QWEN_MODEL_ID','QWEN_MODEL_REVISION','UITARS_MODEL_ID','UITARS_MODEL_REVISION',
                'GUIOWL_MODEL_ID','GUIOWL_MODEL_REVISION'):
        if key in os.environ:config[key]=os.environ[key]
    defaults=dict(HF_HOME='runtime/cache/huggingface',HF_HUB_CACHE='runtime/cache/huggingface/hub',
                  HF_XET_CACHE='runtime/cache/huggingface/xet',TORCH_HOME='runtime/cache/torch',MODEL_ROOT='runtime/models')
    paths={key:project_path(config.get(key,default),root) for key,default in defaults.items()}
    for key,path in paths.items():
        path.mkdir(parents=True,exist_ok=True)
        if key!='MODEL_ROOT':os.environ[key]=str(path)
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
    return config,paths


def relative_name(name):
    path=PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in ('..','.') for part in path.parts) or '\\' in name or ':' in name:
        raise ValueError('invalid Hub file path')
    return path


def inventory(info,model):
    if info.sha!=model['revision']:raise ValueError('Hub resolved another model revision')
    files=[]
    for file in info.siblings:
        relative_name(file.rfilename)
        lfs=file.lfs
        files.append(dict(file=file.rfilename,bytes=file.size,git_blob_sha1=file.blob_id,
                          lfs_sha256=(lfs.sha256 if hasattr(lfs,'sha256') else lfs.get('sha256')) if lfs else None))
    if not files or any(type(f['bytes']) is not int or f['bytes']<0 for f in files):
        raise ValueError('incomplete Hub file size metadata')
    names={f['file'] for f in files}
    if 'config.json' not in names or 'tokenizer_config.json' not in names or not any(n.endswith('.safetensors') for n in names):
        raise ValueError('required native config/tokenizer/safetensors files missing')
    if not any(n in names for n in ('preprocessor_config.json','processor_config.json')):
        raise ValueError('native image processor config missing')
    return files


def verify_file(path,record):
    if path.stat().st_size!=record['bytes']:raise ValueError('model file size mismatch: '+record['file'])
    digest=hashlib.sha256();blob=hashlib.sha1()
    blob.update(b'blob '+str(record['bytes']).encode()+b'\0')
    with path.open('rb') as stream:
        while data:=stream.read(4*1024*1024):digest.update(data);blob.update(data)
    actual=digest.hexdigest()
    expected=record['lfs_sha256']
    if expected:
        if actual!=expected:raise ValueError('model LFS checksum mismatch: '+record['file'])
    elif not record['git_blob_sha1'] or blob.hexdigest()!=record['git_blob_sha1']:
        raise ValueError('model Git blob checksum mismatch: '+record['file'])
    return dict(file=record['file'],bytes=record['bytes'],sha256=actual)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',nargs='+',choices=('qwen','uitars','guiowl'),required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--inspect',action='store_true',help='metadata and byte requirements only; no weight download')
    mode.add_argument('--download',action='store_true',help='download full pinned repo and verify every file')
    parser.add_argument('--output',type=Path,required=True,help='fresh receipt directory inside this project')
    args=parser.parse_args()
    if len(set(args.only))!=len(args.only):parser.error('repeated model selection')
    output=project_path(str(args.output))
    if output.exists():parser.error('fresh project-local receipt directory required')
    config,paths=local_config()
    lock=json.loads(LOCK.read_text(encoding='utf-8'))
    for key in args.only:
        model=lock['models'][key];prefix=model['env_prefix']
        for name,expected in ((prefix+'_MODEL_ID',model['repo_id']),(prefix+'_MODEL_REVISION',model['revision'])):
            if config.get(name,expected)!=expected:parser.error(name+' differs from the selected plan lock')
    from huggingface_hub import HfApi,snapshot_download
    token=config.get('HF_TOKEN') or False
    api=HfApi(token=token)
    output.mkdir(parents=True)
    receipt=dict(status='RUNNING',mode='download' if args.download else 'metadata_only',
                 sdk_version=importlib.metadata.version('huggingface-hub'),models={},started_utc_ns=time.time_ns(),
                 inference_calls=0,weights_loaded=False,lock_sha256=hashlib.sha256(LOCK.read_bytes()).hexdigest())
    try:
        for key in args.only:
            model=lock['models'][key]
            print('INSPECT pinned snapshot',model['repo_id'],flush=True)
            info=api.model_info(model['repo_id'],revision=model['revision'],files_metadata=True,timeout=60)
            files=inventory(info,model)
            entry=dict(repo_id=model['repo_id'],revision=info.sha,files=files,bytes=sum(f['bytes'] for f in files),
                       weights_downloaded=False,hashes_verified=False,offline_reload_verified=False)
            receipt['models'][key]=entry
            if args.download:
                destination=paths['MODEL_ROOT']/key/model['revision']
                snapshot_download(repo_id=model['repo_id'],revision=model['revision'],token=token,
                                  local_dir=destination,cache_dir=paths['HF_HUB_CACHE'],max_workers=2)
                verified=[verify_file(destination/str(relative_name(f['file'])),f) for f in files]
                manifest=dict(status='FILES_VERIFIED_NOT_INFERENCE',repo_id=model['repo_id'],revision=model['revision'],
                              files=verified,offline_reload_verified=False,utc_ns=time.time_ns())
                (destination/'SNAPSHOT.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
                entry.update(local_dir=destination.relative_to(ROOT).as_posix(),weights_downloaded=True,hashes_verified=True)
            print(json.dumps(dict(model=key,files=len(files),bytes=entry['bytes'],weights_downloaded=entry['weights_downloaded'])),flush=True)
        receipt['status']='PASS'
    except Exception as exc:
        # Store exception type only: SDK error strings may include signed URLs.
        receipt.update(status='FAILED',error_type=type(exc).__name__)
        print('SETUP FAILED:',type(exc).__name__,'(details/credentials not logged)',flush=True)
    finally:
        receipt['finished_utc_ns']=time.time_ns()
        (output/'RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    if receipt['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
