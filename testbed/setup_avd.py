"""Install/check the isolated Windows API33/r17 x86_64 development AVD.

New host/ABI stratum, not historical arm64 timing. Project-local SDK, HOME and
AVD; no system PATH or hypervisor changes. No model or study runs here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET

from setup_android import archive_info,hash_file

IMAGE='system-images;android-33;google_apis;x86_64'
NAME='ghosteffect_api33_x86_local'


def run_java(java,sdk,main,args,env,stdin=None,timeout=900):
    classes={'sdkmanager':('sdkmanager-classpath.jar','com.android.sdklib.tool.sdkmanager.SdkManagerCli'),
             'avdmanager':('avdmanager-classpath.jar','com.android.sdklib.tool.AvdManagerCli')}
    jar,entry=classes[main]
    property_name='com.android.sdkmanager.toolsdir' if main=='avdmanager' else 'com.android.sdklib.toolsdir'
    command=[str(java),'-D'+property_name+'='+str(sdk/'cmdline-tools/19.0'),
             '-classpath',str(sdk/'cmdline-tools/19.0/lib'/jar),entry,*args]
    return subprocess.run(command,input=stdin,capture_output=True,text=True,encoding='utf-8',
                          errors='replace',env=env,timeout=timeout)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java',type=Path,required=True)
    parser.add_argument('--install',action='store_true')
    parser.add_argument('--create',action='store_true')
    parser.add_argument('--verify-apks',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if os.name!='nt':parser.error('Windows development setup only')
    if not any((args.install,args.create,args.verify_apks)):parser.error('choose setup operation')
    if args.output.exists():parser.error('fresh output directory required')
    root=Path(__file__).resolve().parents[1];sdk=root/'runtime/android-sdk'
    env=os.environ.copy()
    env.update(ANDROID_HOME=str(sdk),ANDROID_SDK_ROOT=str(sdk),
               ANDROID_USER_HOME=str(root/'runtime/android-home'),
               ANDROID_AVD_HOME=str(root/'runtime/android-avd'))
    for name in ('ANDROID_USER_HOME','ANDROID_AVD_HOME'):Path(env[name]).mkdir(parents=True,exist_ok=True)
    args.output.mkdir(parents=True)
    result=dict(kind='local Windows/x86_64 Android setup, not a study result',status='RUNNING',
                image=IMAGE,expected_image_revision='17',operations=[],started_utc_ns=time.time_ns(),
                script_sha256=hash_file(Path(__file__)))
    def command(label,call):
        reply=call()
        (args.output/(label+'.stdout.log')).write_text(reply.stdout,encoding='utf-8')
        (args.output/(label+'.stderr.log')).write_text(reply.stderr,encoding='utf-8')
        result['operations'].append(dict(operation=label,exit_code=reply.returncode))
        if reply.returncode:raise RuntimeError(label+' failed; inspect saved logs')
        return reply
    try:
        if args.install:
            # Freeze the currently published exact image revision BEFORE install.
            # setup_android's bootstrap registers emulator37.2.13 so dependency
            # resolution must not upgrade it. Re-check its revision afterwards.
            metadata=root/'runtime/android-downloads/sys-img-google-apis.xml'
            if not metadata.exists():
                with urllib.request.urlopen('https://dl.google.com/android/repository/sys-img/google_apis/sys-img2-3.xml',timeout=60) as source:
                    metadata.write_bytes(source.read())
            info=archive_info(metadata.read_bytes(),IMAGE,'17.0.0')
            result['image_archive']=info
            result['image_metadata_sha256']=hash_file(metadata)
            print('INSTALL exact API33/r17 image, platform33 and build-tools33.0.2',flush=True)
            command('sdk-install',lambda:run_java(args.java,sdk,'sdkmanager',[
                '--sdk_root='+str(sdk),'build-tools;33.0.2','platforms;android-33',IMAGE],env,'y\n'*10,1200))
            props=(sdk/'system-images/android-33/google_apis/x86_64/source.properties').read_text()
            if not any(line.strip()=='Pkg.Revision=17' for line in props.splitlines()):
                raise ValueError('installed image revision differs from frozen r17')
            if 'Pkg.Revision=37.2.13' not in (sdk/'emulator/source.properties').read_text():
                raise ValueError('emulator pin changed during SDK dependency resolution')
            package=sdk/'system-images/android-33/google_apis/x86_64/package.xml'
            result['installed_image_package_sha256']=hash_file(package)
        if args.create:
            avd=root/'runtime/android-avd'/(NAME+'.avd')
            if avd.exists():raise ValueError('existing AVD kept; choose a fresh setup or reuse it explicitly')
            print('CREATE project-local AVD (2048MB RAM, two vCPUs)',flush=True)
            command('avd-create',lambda:run_java(args.java,sdk,'avdmanager',[
                'create','avd','--name',NAME,'--package',IMAGE,'--path',str(avd),
                '--device','pixel_6'],env,'no\n',120))
            config=avd/'config.ini'
            lines=config.read_text(encoding='utf-8').splitlines()
            values=dict(line.split('=',1) for line in lines if '=' in line)
            values.update({'hw.ramSize':'2048','hw.cpu.ncore':'2','disk.dataPartition.size':'4G',
                           'hw.lcd.width':'1080','hw.lcd.height':'2400','hw.lcd.density':'420',
                           'hw.keyboard':'yes','showDeviceFrame':'no'})
            config.write_text(''.join(k+'='+v+'\n' for k,v in values.items()),encoding='utf-8')
            result['avd_config_sha256']=hash_file(config)
            result['avd']=str(avd)
        if args.verify_apks:
            tools=sdk/'build-tools/33.0.2';result['apks']=[]
            for apk in sorted((root/'runtime/assets').glob('*.apk')):
                print('VERIFY',apk.name,flush=True)
                signed=command(apk.name+'.signature',lambda:subprocess.run([
                    str(args.java),'-jar',str(tools/'lib/apksigner.jar'),'verify','--verbose',
                    '--print-certs',str(apk)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60))
                manifest=command(apk.name+'.manifest',lambda:subprocess.run([
                    str(tools/'aapt.exe'),'dump','badging',str(apk)],capture_output=True,text=True,
                    encoding='utf-8',errors='replace',timeout=60))
                result['apks'].append(dict(file=apk.name,sha256=hash_file(apk),
                    signature_verified=True,
                    certificates=[line for line in signed.stdout.splitlines() if 'certificate SHA-256 digest' in line],
                    package=next((line for line in manifest.stdout.splitlines() if line.startswith('package:')),None),
                    native=next((line for line in manifest.stdout.splitlines() if line.startswith('native-code:')),None)))
        result['status']='PASS'
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc));raise
    finally:
        (args.output/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],output=str(args.output))))


if __name__=='__main__':main()
