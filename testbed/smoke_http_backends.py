"""Actual pinned Synapse/Radicale + fault proxy; synthetic payloads, no Android/LLM.

Run with runtime/backend-venv/bin/python on Linux. Creates an isolated backend
state directory and private accounts; starts/stops only its own child process.
Backend oracle is used only in this injector-side integration, never recovery.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import hmac
import importlib.metadata
import json
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from faultproxy import Journal, Faults, http_proxy
from grader import matrix_count, caldav_count
from setup_assets import sha


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        return sock.getsockname()[1]


def request(url,method='GET',payload=None,headers=None):
    if isinstance(payload,dict):
        payload=json.dumps(payload).encode()
        headers=dict(headers or {},**{'Content-Type':'application/json'})
    req=urllib.request.Request(url,payload,headers or {},method=method)
    try:
        with urllib.request.urlopen(req,timeout=20) as response:
            return response.status,response.read()
    except urllib.error.HTTPError as exc:
        return exc.code,exc.read()


@contextmanager
def backend(command,directory,port):
    with (directory/'backend.log').open('w',encoding='utf-8') as stream:
        child=subprocess.Popen(command,cwd=directory,stdout=stream,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+180
            while time.monotonic()<deadline:
                if child.poll() is not None:
                    raise RuntimeError('backend exited early; inspect backend.log')
                try:
                    with socket.create_connection(('127.0.0.1',port),timeout=.3):break
                except OSError:time.sleep(.2)
            else:raise RuntimeError('backend startup timed out')
            yield
        finally:
            child.terminate()
            try:child.wait(15)
            except subprocess.TimeoutExpired:
                child.kill();child.wait()


@contextmanager
def proxy_server(origin,protocol,directory):
    faults=Faults(Journal(directory/'proxy.jsonl'),barrier_timeout=20)
    server=http_proxy(origin,protocol,faults)
    worker=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':.02},daemon=True)
    worker.start()
    try:yield 'http://%s:%s'%server.server_address,faults
    finally:
        server.shutdown();server.server_close();worker.join(2)


def run_matrix(directory):
    import yaml
    if importlib.metadata.version('matrix-synapse')!='1.164.2':raise ValueError('wrong Synapse version')
    port=free_port();origin='http://127.0.0.1:'+str(port)
    config=directory/'homeserver.yaml'
    subprocess.run([sys.executable,'-m','synapse.app.homeserver','--server-name','ghost.test',
                    '--config-path',str(config),'--generate-config','--report-stats','no'],
                   cwd=directory,stdout=subprocess.DEVNULL,check=True)
    data=yaml.safe_load(config.read_text());secret=secrets.token_hex(32)
    data.update(listeners=[dict(port=port,tls=False,type='http',bind_addresses=['127.0.0.1'],
                                resources=[dict(names=['client'],compress=False)])],
                registration_shared_secret=secret,enable_registration=False,url_preview_enabled=False,
                federation_domain_whitelist=[],database=dict(name='sqlite3',args=dict(database=str(directory/'homeserver.db'))))
    config.write_text(yaml.safe_dump(data,sort_keys=False));config.chmod(0o600)
    with backend([sys.executable,'-m','synapse.app.homeserver','--config-path',str(config)],directory,port):
        code,body=request(origin+'/_synapse/admin/v1/register');assert code==200
        nonce=json.loads(body)['nonce'];password=secrets.token_hex(16);user='gx_smoke'
        mac=hmac.new(secret.encode(),b'\x00'.join(x.encode() for x in [nonce,user,password,'notadmin']),hashlib.sha1).hexdigest()
        code,body=request(origin+'/_synapse/admin/v1/register','POST',dict(nonce=nonce,username=user,password=password,admin=False,mac=mac))
        assert code==200,'failed isolated user registration'
        auth={'Authorization':'Bearer '+json.loads(body)['access_token']}
        code,body=request(origin+'/_matrix/client/v3/createRoom','POST',dict(visibility='private',name='GhostEffect synthetic smoke'),auth)
        assert code==200
        room=json.loads(body)['room_id'];path='/_matrix/client/v3/rooms/'+urllib.parse.quote(room,safe='')+'/send/m.room.message/'
        count=lambda tag:matrix_count(origin,room,tag,auth['Authorization'][7:])['copies']
        cases=[]
        with proxy_server(origin,'matrix',directory) as (proxy,faults):
            tag='GX_NOFAULT_'+uuid.uuid4().hex
            assert request(proxy+path+'nofault','PUT',dict(msgtype='m.text',body=tag),auth)[0]==200
            assert count(tag)==1;cases.append(dict(case='nofault',copies=1))
            tag='GX_LOSTACK_'+uuid.uuid4().hex;payload=dict(msgtype='m.text',body=tag)
            arm=faults.configure('drop','lost')
            with ThreadPoolExecutor(1) as pool:
                future=pool.submit(request,proxy+path+'lost','PUT',payload,auth)
                assert faults.arm['reached'].wait(20),'barrier not reached'
                assert count(tag)==1 and not future.done()
                faults.release(arm,dict(observed_class='none',purpose='protocol smoke, no app fault'))
                try:future.result()
                except (OSError,urllib.error.URLError):pass
                else:raise AssertionError('lost ACK reached the client')
            assert request(proxy+path+'lost','PUT',payload,auth)[0]==200
            assert count(tag)==1;cases.append(dict(case='lost_ack_same_txnid_retry',copies=1))
            assert request(proxy+path+'new-id','PUT',payload,auth)[0]==200
            assert count(tag)==2;cases.append(dict(case='new_txnid_same_content',copies=2))
            tag='GX_REJECT_'+uuid.uuid4().hex;payload=dict(msgtype='m.text',body=tag)
            arm=faults.configure('reject','rejected')
            assert request(proxy+path+'rejected','PUT',payload,auth)[0]==403
            faults.release(arm,dict(observed_class='none'))
            assert request(proxy+path+'rejected','PUT',payload,auth)[0]==403
            assert count(tag)==0;cases.append(dict(case='preapply_reject_and_late_same_id',copies=0))
        return cases


def run_caldav(directory):
    if importlib.metadata.version('Radicale')!='3.9.0':raise ValueError('wrong Radicale version')
    port=free_port();origin='http://127.0.0.1:'+str(port)
    username,password='gx_smoke',secrets.token_hex(16)
    users=directory/'users';users.write_text(username+':'+password+'\n');users.chmod(0o600)
    config=directory/'config';config.write_text('[server]\nhosts = 127.0.0.1:'+str(port)+'\n[auth]\ntype = htpasswd\nhtpasswd_filename = '+str(users)+'\nhtpasswd_encryption = plain\n[storage]\nfilesystem_folder = '+str(directory/'collections')+'\n')
    auth={'Authorization':'Basic '+base64.b64encode((username+':'+password).encode()).decode()}
    with backend([sys.executable,'-m','radicale','--config',str(config)],directory,port):
        collection='/'+username+'/calendar/'
        xml=b'<c:mkcalendar xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:set><d:prop><d:displayname>synthetic</d:displayname></d:prop></d:set></c:mkcalendar>'
        code,_=request(origin+collection,'MKCALENDAR',xml,dict(auth,**{'Content-Type':'application/xml'}));assert code==201
        count=lambda tag:caldav_count(origin+collection,tag,username,password)['copies']
        headers=dict(auth,**{'Content-Type':'text/calendar; charset=utf-8','If-None-Match':'*'})
        def body(uid,tag):
            return ('BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//GhostEffect//synthetic//EN\r\nBEGIN:VEVENT\r\nUID:'+uid+'\r\nDTSTAMP:20261108T000000Z\r\nDTSTART:20261110T100000Z\r\nDTEND:20261110T110000Z\r\nSUMMARY:synthetic\r\nDESCRIPTION:'+tag+'\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n').encode()
        cases=[]
        with proxy_server(origin,'caldav',directory) as (proxy,faults):
            tag='GX_NOFAULT_'+uuid.uuid4().hex
            assert request(proxy+collection+'nofault.ics','PUT',body('nofault',tag),headers)[0]==201
            assert count(tag)==1;cases.append(dict(case='nofault',copies=1))
            tag='GX_LOSTACK_'+uuid.uuid4().hex;payload=body('lost',tag)
            arm=faults.configure('drop',collection+'lost.ics')
            with ThreadPoolExecutor(1) as pool:
                future=pool.submit(request,proxy+collection+'lost.ics','PUT',payload,headers)
                assert faults.arm['reached'].wait(20)
                assert count(tag)==1 and not future.done()
                faults.release(arm,dict(observed_class='none',purpose='protocol smoke, no app fault'))
                try:future.result()
                except (OSError,urllib.error.URLError):pass
                else:raise AssertionError('lost ACK reached client')
            assert request(proxy+collection+'lost.ics','PUT',payload,headers)[0]==412
            assert count(tag)==1;cases.append(dict(case='lost_ack_same_href_conditional_retry',copies=1,retry_status=412))
            assert request(proxy+collection+'new.ics','PUT',body('new-logical-entry',tag),headers)[0]==201
            assert count(tag)==2;cases.append(dict(case='new_href_uid_same_content',copies=2))
            tag='GX_REJECT_'+uuid.uuid4().hex;payload=body('rejected',tag)
            arm=faults.configure('reject',collection+'rejected.ics')
            assert request(proxy+collection+'rejected.ics','PUT',payload,headers)[0]==403
            faults.release(arm,dict(observed_class='none'))
            assert request(proxy+collection+'rejected.ics','PUT',payload,headers)[0]==403
            assert count(tag)==0;cases.append(dict(case='preapply_reject_and_late_same_id',copies=0))
        return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',required=True,choices=['matrix','caldav'])
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if not __debug__:parser.error('verification needs Python without -O')
    if args.output.exists():parser.error('fresh output required')
    output=args.output.resolve();output.mkdir(parents=True)
    started=time.monotonic()
    try:
        cases=run_matrix(output) if args.protocol=='matrix' else run_caldav(output)
        result=dict(status='PASS',kind='real backend protocol integration with synthetic payloads',
                    protocol=args.protocol,android=False,llm=False,app_fault=False,cases=cases,
                    version=importlib.metadata.version('matrix-synapse' if args.protocol=='matrix' else 'Radicale'),
                    seconds=time.monotonic()-started,source_sha256={p.name:sha(p) for p in Path(__file__).parent.glob('*.py')})
    except Exception as exc:
        result=dict(status='FAIL',protocol=args.protocol,error_type=type(exc).__name__,reason=str(exc),seconds=time.monotonic()-started)
        (output/'RESULT.json').write_text(json.dumps(result,indent=2));raise
    (output/'RESULT.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
