"""Bounded local AVD diagnostic session; no study or physical-device access."""
import json,os,subprocess,time,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'testbed'))
from smoke_android import free_port
from setup_avd import NAME
directory=Path(__file__).parent/'live-01';directory.mkdir(exist_ok=False)
sdk=root/'runtime/android-sdk';adb=sdk/'platform-tools/adb.exe'
env=os.environ.copy();env.update(ANDROID_HOME=str(sdk),ANDROID_SDK_ROOT=str(sdk),ANDROID_USER_HOME=str(root/'runtime/android-home'),ANDROID_EMULATOR_HOME=str(root/'runtime/android-home'),ANDROID_AVD_HOME=str(root/'runtime/android-avd'),ANDROID_ADB_SERVER_PORT='5038',ADB_SERVER_SOCKET='tcp:127.0.0.1:5038')
def call(*args,check=True,timeout=30):
 return subprocess.run([str(adb),'-P','5038',*args],env=env,check=check,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
for p in (5038,5580,5581):free_port(p)
process=None;owned=False
with (directory/'emulator.log').open('w',encoding='utf-8') as log:
 try:
  call('start-server');owned=True
  process=subprocess.Popen([str(sdk/'emulator/emulator.exe'),'-avd',NAME,'-port','5580','-no-window','-no-audio','-no-snapshot','-no-boot-anim','-accel','on','-gpu','swiftshader'],stdout=log,stderr=subprocess.STDOUT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
  deadline=time.monotonic()+240
  while time.monotonic()<deadline:
   if process.poll() is not None:raise RuntimeError('owned emulator exited')
   r=call('-s','emulator-5580','shell','getprop','sys.boot_completed',check=False,timeout=10)
   if r.returncode==0 and r.stdout.strip()=='1':break
   time.sleep(2)
  else:raise RuntimeError('boot timeout')
  call('-s','emulator-5580','shell','input','keyevent','KEYCODE_WAKEUP')
  call('-s','emulator-5580','shell','input','keyevent','KEYCODE_MENU')
  launch=call('-s','emulator-5580','shell','am','start','-W','-n','com.simplemobiletools.smsmessenger/.activities.SplashActivity.Orange')
  (directory/'launch.txt').write_text(launch.stdout,encoding='utf-8')
  (directory/'READY.json').write_text(json.dumps(dict(kind='development diagnostic only',owned_pid=process.pid,serial='emulator-5580',adb_port=5038,deadline_seconds=900)))
  print('READY development session; stop via tmp/resolve-v8/live-01/STOP',flush=True)
  deadline=time.monotonic()+900
  while process.poll() is None and time.monotonic()<deadline and not (directory/'STOP').exists():time.sleep(1)
 finally:
  if process is not None and process.poll() is None:
   try:call('-s','emulator-5580','emu','kill',check=False,timeout=15);process.wait(20)
   except subprocess.TimeoutExpired:process.terminate();process.wait(20)
  if owned:call('kill-server',check=False)
  (directory/'STOPPED.json').write_text(json.dumps(dict(stopped=process is None or process.poll() is not None)))
