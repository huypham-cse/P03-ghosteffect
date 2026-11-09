"""Scripted transport fixture exercising native agent code on a test AVD.

Responses are SYNTHETIC, deliberately not an LLM baseline or a scientific
episode. Native M3A/T3A, prompts, reflection, image encoding and adb action run
unchanged. Only BACK is scripted. The server is loopback and lives for one step.
"""
import base64
from dataclasses import asdict,is_dataclass
import hashlib
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
from pathlib import Path
import threading
import time
from unittest.mock import patch


def run(env,framework,directory):
    from android_env.proto import adb_pb2
    from androidworld_env import make_agent
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    model_id='Qwen/Qwen2.5-VL-7B-Instruct'
    requests=[];actions=[];adb_calls=[]
    result=dict(status='RUNNING',kind='SYNTHETIC_RESPONSE_NATIVE_AGENT_WIRING_ONLY',
                framework=framework,models_loaded=False,scientific_episode=False,
                scripted_action='navigate_back',started_utc_ns=time.time_ns())
    def save_value(value,label):
        import numpy as np
        if isinstance(value,np.ndarray):
            from PIL import Image
            file=label+'.png';Image.fromarray(value).save(directory/file)
            return dict(file=file,shape=list(value.shape),sha256=hashlib.sha256((directory/file).read_bytes()).hexdigest())
        if is_dataclass(value):return save_value(asdict(value),label)
        if isinstance(value,dict):return {k:save_value(v,label+'-'+k) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [save_value(v,label+'-'+str(i)) for i,v in enumerate(value)]
        if value is None or isinstance(value,(str,int,float,bool)):return value
        raise TypeError('unsupported native step data type: '+type(value).__name__)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            try:
                if self.path!='/v1/chat/completions':raise ValueError('unexpected wire endpoint')
                payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                content=payload['messages'][0]['content']
                index=len(requests)
                if index>=2:raise ValueError('unexpected extra model request; fixture does not retry')
                images=[part['image_url']['url'] for part in content if part['type']=='image_url']
                expected=2 if framework=='m3a' else 0
                if len(images)!=expected:raise ValueError('native image count changed')
                if payload['temperature']!=0 or payload['top_p']!=1 or payload['max_tokens']!=2048:
                    raise ValueError('decode/budget differs from frozen recipe')
                for i,url in enumerate(images):
                    if not url.startswith('data:image/png;base64,'):raise ValueError('non-PNG transport')
                    (directory/('request-%d-image-%d.png'%(index,i))).write_bytes(base64.b64decode(url.split(',',1)[1],validate=True))
                (directory/('request-%d-prompt.txt'%index)).write_text(content[0]['text'],encoding='utf-8')
                requests.append(dict(index=index,images=len(images),body_sha256=hashlib.sha256(json.dumps(payload).encode()).hexdigest()))
                text=('Reason: Scripted BACK wiring fixture; no model inference.\nAction: {"action_type":"navigate_back"}'
                      if index==0 else 'Synthetic fixture summary after BACK; not an evaluated model judgment.')
                data=json.dumps(dict(model=model_id,choices=[dict(finish_reason='stop',message=dict(content=text))])).encode()
                self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            except Exception as exc:
                data=json.dumps(dict(error_type=type(exc).__name__,reason=str(exc))).encode()
                self.send_response(400);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':.05},daemon=True);thread.start()
    execute=env.execute_action;adb=env.controller.execute_adb_call
    def action_call(action):
        actions.append(asdict(action));return execute(action)
    def adb_call(request,*args,**kwargs):
        reply=adb(request,*args,**kwargs)
        adb_calls.append(dict(request=str(request),response_status=reply.status))
        return reply
    try:
        agent=make_agent(framework,env,'http://127.0.0.1:'+str(server.server_port)+'/v1',model_id)
        agent.reset()
        with patch.object(env,'execute_action',side_effect=action_call),patch.object(env.controller,'execute_adb_call',side_effect=adb_call):
            step=agent.step('Development wiring fixture: press Back once; no content creation or send.')
        data=save_value(step.data,'step')
        (directory/'step.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        if len(requests)!=2 or len(actions)!=1 or len(agent.history)!=1:
            raise RuntimeError('native action/reflection/history did not complete as expected')
        back='button: BACK'
        if not any(back in call['request'] and call['response_status']==adb_pb2.AdbResponse.OK for call in adb_calls):
            raise RuntimeError('no successful actual native BACK adb receipt')
        result.update(status='PASS',requests=requests,actions=actions,adb_calls=adb_calls,
                      native_history_entries=len(agent.history),agent_done=step.done,
                      scope='one native step with two scripted transport responses; not model quality or task success')
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc),requests=requests,actions=actions,adb_calls=adb_calls)
        raise
    finally:
        server.shutdown();server.server_close();thread.join(2)
        result['finished_utc_ns']=time.time_ns()
        (directory/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
