"""Boot our AVD, install verified APKs and capture first-run GUI screens.

Isolated adb server/explicit AVD only. No accounts, agent, calibration or fault
study. Closes only the emulator/server started by this invocation.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
import xml.etree.ElementTree as ET

from setup_android import hash_file
from setup_avd import NAME


def free_port(port):
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',port))


def sms_role_action(xml):
    """Setup-only choice from the actual API33 role dialog, not an agent vote."""
    from ui import select
    tree=ET.fromstring(xml)
    targets=select(tree,{'resource-id':'com.android.permissioncontroller:id/title','text':'SMS Messenger'})
    if len(targets)!=1:raise RuntimeError('SMS role target is missing or ambiguous')
    parents={child:parent for parent in tree.iter() for child in parent}
    row=parents.get(targets[0])
    radios=[n for n in row.iter('node') if n.get('class')=='android.widget.RadioButton'] if row is not None else []
    if len(radios)!=1 or radios[0].get('enabled')!='true':raise RuntimeError('SMS role radio is missing/disabled')
    current=any(n.get('text')=='Current default' for n in row.iter('node'))
    if radios[0].get('checked')=='false':
        if current:raise RuntimeError('inconsistent default role dialog')
        return 'select-radio',radios[0]
    if radios[0].get('checked')!='true':raise RuntimeError('SMS role selection unknown')
    # An already-default app can leave the old request dialog behind. The
    # disabled confirmation is not another request to assign the role.
    selector=({'resource-id':'android:id/button2','text':'Cancel'} if current else
              {'resource-id':'android:id/button1','text':'Set as default'})
    buttons=select(tree,selector)
    if len(buttons)!=1 or buttons[0].get('enabled')!='true':raise RuntimeError('SMS role button missing/disabled')
    return ('close-already-default-dialog' if current else 'confirm-default'),buttons[0]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verification',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--only',nargs='+',help='selected verified catalogue APK filenames; default four measured-stack apps')
    parser.add_argument('--prepare-sms-role',action='store_true',help='set Simple SMS as default only inside this test AVD; no SMS is sent')
    parser.add_argument('--native-env-capture',action='store_true',help='also take one native AndroidWorld observation; installs the locked test-AVD forwarder')
    parser.add_argument('--scripted-agent-wire',action='store_true',help='SYNTHETIC transport responses for native BACK/reflection wiring only; requires native-env-capture')
    parser.add_argument('--gpu',choices=('swiftshader','host'),default='swiftshader',help='explicit development renderer; freeze and record it before study, never a silent fallback')
    args=parser.parse_args()
    if os.name!='nt':parser.error('local Windows development smoke only')
    if args.scripted_agent_wire and not args.native_env_capture:parser.error('scripted wiring requires native-env-capture')
    if args.output.exists():parser.error('fresh output required')
    root=Path(__file__).resolve().parents[1];sdk=root/'runtime/android-sdk'
    verification=json.loads(args.verification.read_text(encoding='utf-8'))
    if verification['status']!='PASS':parser.error('APK verification must pass first')
    assets={item['file']:item for item in verification['apks']}
    known={'im.vector.app_40106624.apk':'im.vector.app','com.fsck.k9_39046.apk':'com.fsck.k9',
           'at.bitfire.davdroid_405210002.apk':'at.bitfire.davdroid','ws.xsoh.etar_57.apk':'ws.xsoh.etar',
           'com.arduia.expense_11.apk':'com.arduia.expense','net.gsantner.markor_146.apk':'net.gsantner.markor',
           'org.tasks_130605.apk':'org.tasks','com.simplemobiletools.smsmessenger_85.apk':'com.simplemobiletools.smsmessenger',
           'net.cozic.joplin_2097740.apk':'net.cozic.joplin'}
    chosen=args.only or list(known)[:4]
    if set(chosen)-set(known) or len(set(chosen))!=len(chosen):parser.error('unknown or repeated catalogue APK')
    files={name:known[name] for name in chosen}
    required=list(files)
    if args.native_env_capture:
        if len(files)!=1:parser.error('native observation smoke uses exactly one selected app')
        agent_python=root/'runtime/agent-venv/Scripts/python.exe'
        if not agent_python.is_file():parser.error('pinned agent Python environment is missing')
        forwarder=json.loads((Path(__file__).with_name('agent-assets.lock.json')).read_text())['assets'][0]
        required.append(forwarder['file'])
        item=assets.get(forwarder['file'],{})
        if item.get('sha256')!=forwarder['sha256'] or not item.get('package','').startswith("package: name='"+forwarder['package']+"'"):
            parser.error('forwarder verification differs from its lock/package')
    for filename in required:
        item=assets.get(filename,{})
        if not item.get('signature_verified') or item['sha256']!=hash_file(root/'runtime/assets'/filename):
            parser.error('APK missing, changed or unverified: '+filename)
    if 'Pkg.Revision=37.2.13' not in (sdk/'emulator/source.properties').read_text():parser.error('emulator pin differs')
    for port in ((5038,5580,5581,8554) if args.native_env_capture else (5038,5580,5581)):free_port(port)
    args.output.mkdir(parents=True)
    env=os.environ.copy()
    env.update(ANDROID_HOME=str(sdk),ANDROID_SDK_ROOT=str(sdk),
               ANDROID_USER_HOME=str(root/'runtime/android-home'),
               ANDROID_EMULATOR_HOME=str(root/'runtime/android-home'),
               ANDROID_AVD_HOME=str(root/'runtime/android-avd'),
               ANDROID_ADB_SERVER_PORT='5038',ADB_SERVER_SOCKET='tcp:127.0.0.1:5038')
    adb=sdk/'platform-tools/adb.exe'
    result=dict(kind='actual Android boot/install/first-run UI smoke',status='RUNNING',
                study_result=False,abi_stratum='Windows x86_64 API33/r17',
                graphics_renderer_requested=args.gpu,
                source_sha256=hash_file(Path(__file__)),apks=[],
                capture_source_sha256=hash_file(Path(__file__).with_name('ui.py')),
                verification_sha256=hash_file(args.verification),started_utc_ns=time.time_ns())
    process=None;server_owned=False
    def call(*command,timeout=30,check=True):
        reply=subprocess.run([str(adb),'-P','5038',*command],capture_output=True,text=True,
                             encoding='utf-8',errors='replace',timeout=timeout,env=env)
        if check and reply.returncode:
            raise RuntimeError('adb '+repr(command)+' exit '+str(reply.returncode)+': '+(reply.stdout+reply.stderr)[:400])
        return reply
    def device(*command,**kwargs):return call('-s','emulator-5580',*command,**kwargs)
    log=(args.output/'emulator.log').open('w',encoding='utf-8')
    try:
        call('start-server');server_owned=True
        accel=subprocess.run([str(sdk/'emulator/emulator.exe'),'-accel-check'],capture_output=True,
                             text=True,encoding='utf-8',errors='replace',timeout=30,env=env)
        if accel.returncode:raise RuntimeError('accelerated VM unavailable; no software CPU fallback')
        result['acceleration']=accel.stdout
        command=[str(sdk/'emulator/emulator.exe'),'-avd',NAME,'-port','5580','-no-window',
                 '-no-audio','-no-snapshot','-no-boot-anim','-accel','on','-gpu',args.gpu]
        if args.native_env_capture:command+=['-grpc','8554']
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        result['owned_emulator_pid']=process.pid;start=time.monotonic();deadline=start+240
        print('BOOT AVD with WHPX, isolated adb5038, serial emulator-5580',flush=True)
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('owned emulator exited; inspect emulator.log')
            reply=device('shell','getprop','sys.boot_completed',timeout=10,check=False)
            if reply.returncode==0 and reply.stdout.strip()=='1':break
            time.sleep(2)
        else:raise RuntimeError('AVD boot timeout')
        result['boot_seconds']=time.monotonic()-start
        result['properties']={key:device('shell','getprop',key).stdout.strip() for key in (
            'ro.build.fingerprint','ro.build.version.sdk','ro.product.cpu.abi',
            'persist.sys.locale','persist.sys.timezone')}
        if result['properties']['ro.build.version.sdk']!='33' or result['properties']['ro.product.cpu.abi']!='x86_64':
            raise ValueError('actual API/ABI differs')
        for key in ('window_animation_scale','transition_animation_scale','animator_duration_scale'):
            device('shell','settings','put','global',key,'0')
        device('shell','input','keyevent','KEYCODE_WAKEUP');device('shell','input','keyevent','KEYCODE_MENU')
        # The GUI capture module inherits only this process-scoped adb endpoint.
        from ui import ADB
        previous={key:os.environ.get(key) for key in ('ANDROID_ADB_SERVER_PORT','ADB_SERVER_SOCKET')}
        os.environ.update({key:env[key] for key in previous})
        try:
            screen=ADB(adb,'emulator-5580')
            for filename,package in files.items():
                print('INSTALL/LAUNCH',filename,flush=True)
                def installed_hash():
                    paths_reply=device('shell','pm','path',package,check=False)
                    if paths_reply.returncode==1 and not (paths_reply.stdout.strip() or paths_reply.stderr.strip()):return None
                    if paths_reply.returncode:raise RuntimeError('package path lookup failed: '+paths_reply.stderr[:200])
                    paths=paths_reply.stdout.strip().splitlines()
                    base=next((p[len('package:'):] for p in paths if p.startswith('package:') and p.endswith('/base.apk')),None)
                    if base is None:return None
                    if not re.fullmatch(r'/[A-Za-z0-9_./~+=-]+/base\.apk',base):raise ValueError('unexpected installed APK path')
                    return device('shell','sha256sum',base).stdout.split()[0]
                before_hash=installed_hash()
                if before_hash!=assets[filename]['sha256']:
                    # Streaming reinstall can stall on this Windows/AVD path.
                    # The adb-supported push+install path preserves the APK.
                    installed=device('install','--no-streaming','-r','-g',str(root/'runtime/assets'/filename),timeout=240)
                    (args.output/(package+'.install.txt')).write_text(installed.stdout+installed.stderr,encoding='utf-8')
                    if 'Success' not in installed.stdout:raise RuntimeError('install did not confirm Success')
                actual_hash=installed_hash()
                if actual_hash!=assets[filename]['sha256']:raise ValueError('installed APK hash does not match verification')
                info=device('shell','dumpsys','package',package).stdout
                (args.output/(package+'.package.txt')).write_text(info,encoding='utf-8')
                component=device('shell','cmd','package','resolve-activity','--brief',
                    '-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER',package).stdout.strip().splitlines()[-1]
                if not re.fullmatch(re.escape(package)+r'/[A-Za-z0-9_.$]+',component):raise ValueError('launcher activity unresolved')
                launched=device('shell','am','start','-W','-n',component)
                (args.output/(package+'.launch.txt')).write_text(launched.stdout,encoding='utf-8')
                if package=='com.simplemobiletools.smsmessenger' and args.prepare_sms_role:
                    chooser='com.google.android.permissioncontroller/com.android.permissioncontroller.role.ui.RequestRoleActivity'
                    if screen.foreground()==chooser:
                        actions=[]
                        for index in range(3):
                            current=screen.foreground()
                            if current.startswith(package+'/'):break
                            if current!=chooser:raise RuntimeError('SMS role dialog identity changed')
                            tree=screen.tree(args.output/('sms-role-'+str(index)))
                            name,node=sms_role_action(tree)
                            bounds=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.get('bounds',''))
                            if not bounds:raise RuntimeError('SMS role selector lacks bounds')
                            if screen.foreground()!=chooser:raise RuntimeError('SMS role input changed before setup tap')
                            x0,y0,x1,y1=map(int,bounds.groups());screen.tap((x0+x1)//2,(y0+y1)//2)
                            actions.append(name)
                            time.sleep(2)
                        result['sms_role_setup']=dict(method='observed GUI chooser selection',actions=actions,
                            target=package,scope='this AVD only; no SMS sent')
                    else:
                        result['sms_role_setup']=dict(method='no role chooser shown',scope='inspect subsequent foreground; no role/SMS claim')
                    roles=device('shell','dumpsys','role').stdout
                    (args.output/'roles.txt').write_text(roles,encoding='utf-8')
                # Startup polling is development readiness, not extra votes in
                # a calibrated recovery family. Keep raw focus diagnostics.
                for attempt in range(15):
                    text=device('shell','dumpsys','window','displays').stdout
                    (args.output/(package+'.window.txt')).write_text(text,encoding='utf-8')
                    if re.search(r'mCurrentFocus=Window\{[^\n]*\bu\d+\s+'+re.escape(package)+'/',text):break
                    time.sleep(2)
                # Native M3A/T3A use the a11y forwarder, not UI Automator.
                # In this mode the child verifies focus and captures that
                # native observation; do not add a second sensor as its gate.
                capture=(dict(foreground_after=None,stable_tree=None) if args.native_env_capture
                         else screen.capture(args.output/package))
                result['apks'].append(dict(file=filename,sha256=assets[filename]['sha256'],
                    installed=True,launcher=component,foreground=capture['foreground_after'],
                    installed_apk_sha256=actual_hash,reused_exact_installed_apk=before_hash==actual_hash,
                    expected_foreground=(None if args.native_env_capture else capture['foreground_after'].startswith(package+'/')),
                    stable_tree=capture['stable_tree'],account_configured=False,
                    capture_scope='native observation follows' if args.native_env_capture else 'UI Automator capture'))
                crash=device('logcat','-b','crash','-d',check=False)
                (args.output/(package+'.crash.txt')).write_text(crash.stdout+crash.stderr,encoding='utf-8')
            if args.native_env_capture:
                print('INSTALL locked native accessibility forwarder, then capture once',flush=True)
                installed=device('install','--no-streaming','-r','-g',str(root/'runtime/assets'/forwarder['file']),timeout=120)
                (args.output/'forwarder-install.txt').write_text(installed.stdout+installed.stderr,encoding='utf-8')
                if 'Success' not in installed.stdout:raise RuntimeError('forwarder installation did not confirm Success')
                paths=device('shell','pm','path',forwarder['package']).stdout.strip().splitlines()
                if len(paths)!=1 or not paths[0].startswith('package:'):raise RuntimeError('unexpected forwarder package path')
                installed_path=paths[0][len('package:'):]
                if not re.fullmatch(r'/[A-Za-z0-9_./~+=-]+/base\.apk',installed_path):raise RuntimeError('unexpected forwarder APK path')
                if device('shell','sha256sum',installed_path).stdout.split()[0]!=forwarder['sha256']:
                    raise RuntimeError('installed forwarder differs from lock')
                # Do not pass backend/model-provider credentials to native
                # dependencies, some of which log their process environment.
                names=('SYSTEMROOT','WINDIR','TEMP','TMP','USERPROFILE','APPDATA','LOCALAPPDATA',
                       'PROGRAMDATA','PATHEXT','COMSPEC','NUMBER_OF_PROCESSORS','PROCESSOR_ARCHITECTURE')
                child_env={key:value for key,value in os.environ.items() if key.upper() in names}
                git_executable=shutil.which('git')
                if not git_executable:raise RuntimeError('git required to verify the pinned native source')
                child_env['PATH']=os.pathsep.join((str(Path(os.environ['SYSTEMROOT'])/'System32'),str(Path(git_executable).parent)))
                native_output=args.output/'native-env'
                extra=['--scripted-agent-wire'] if args.scripted_agent_wire else []
                with (args.output/'native-env.log').open('wb') as stream:
                    child=subprocess.run([str(agent_python),'-B',str(Path(__file__).with_name('capture_androidworld.py')),
                        '--adb',str(adb),'--console-port','5580','--adb-server-port','5038','--grpc-port','8554',
                        '--expected-package',package,'--output',str(native_output),*extra],
                        stdout=stream,stderr=subprocess.STDOUT,env=child_env,timeout=180)
                result['native_env_exit_code']=child.returncode
                if child.returncode:raise RuntimeError('native environment observation failed; inspect native-env.log')
                native_receipt=json.loads((native_output/'RESULT.json').read_text())
                if native_receipt['status']!='PASS':raise RuntimeError('native observation is not ready')
                result['apks'][-1]['foreground']=native_receipt['window_after']['component']
                result['apks'][-1]['expected_foreground']=native_receipt['window_after']['component'].startswith(package+'/')
                result['native_env_capture']=dict(status='PASS',receipt=str(native_output/'RESULT.json'),
                    source_sha256=native_receipt['source_sha256'],forwarder_sha256=forwarder['sha256'])
        finally:
            for key,value in previous.items():
                if value is None:os.environ.pop(key,None)
                else:os.environ[key]=value
        status='PASS' if all(a['expected_foreground'] for a in result['apks']) else 'NOT_READY'
        result.update(status=status,scope='boot and install/launch/capture only; app profiles/accounts/faults/agents not qualified')
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc))
        if process is not None and process.poll() is None:
            # Apparatus diagnostics only; never an observation supplied to the
            # agent/controller. Preserve ANRs instead of auto-dismissing them.
            for name,command in (('last-anr',('shell','dumpsys','activity','lastanr')),
                                 ('logcat',('logcat','-d','-t','600'))):
                try:
                    reply=device(*command,timeout=15,check=False)
                    (args.output/(name+'.txt')).write_text(reply.stdout+reply.stderr,encoding='utf-8')
                except (OSError,subprocess.TimeoutExpired):pass
        raise
    finally:
        if process is not None and process.poll() is None:
            try:device('emu','kill',timeout=15,check=False);process.wait(timeout=20)
            except (subprocess.TimeoutExpired,OSError):process.terminate();process.wait(timeout=20)
        log.close()
        if server_owned:call('kill-server',check=False)
        result['owned_emulator_stopped']=process is None or process.poll() is not None
        (args.output/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],output=str(args.output))))


if __name__=='__main__':main()
