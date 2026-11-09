import os,sys,time,json,re
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'testbed'))
os.environ['ADB_SERVER_SOCKET']='tcp:127.0.0.1:5038';os.environ['ANDROID_ADB_SERVER_PORT']='5038'
from ui import ADB,select
p=ADB(root/'runtime/android-sdk/platform-tools/adb.exe','emulator-5580')
out=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'sms-live-01'
out.mkdir(exist_ok=False)
events=[]
def event(name,**fields):
 events.append(dict(name=name,mono_ns=time.monotonic_ns(),**fields))
 (out/'events.json').write_text(json.dumps(events,indent=2))
def tap(node):
 bounds=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.get('bounds',''))
 if not bounds:raise RuntimeError('missing bounds')
 x0,y0,x1,y1=map(int,bounds.groups());p.tap((x0+x1)//2,(y0+y1)//2)
chooser='com.google.android.permissioncontroller/com.android.permissioncontroller.role.ui.RequestRoleActivity'
try:
 dismissed=False;deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  try:current=p.foreground()
  except RuntimeError:
   inp=p.shell('dumpsys','input');(out/'blocked-input.txt').write_text(inp)
   focus=inp.split('  FocusedWindows:',1)[1].split('  FocusRequests:',1)[0]
   if not dismissed and 'Application Not Responding: com.android.systemui' in focus:
    (out/'anr-before.png').write_bytes(p.run('exec-out','screencap','-p'))
    # Actual screenshot in live-01/before.png locates this named OS ANR's
    # Close app row. This apparatus-only action is never a recovery probe.
    p.tap(500,1235);event('close_observed_systemui_anr');dismissed=True
   time.sleep(1);continue
  if current!=chooser:raise RuntimeError('unexpected foreground before role selection: '+current)
  event('verified_chooser_focus')
  xml=p.tree();(out/'before-select.xml').write_bytes(xml);tree=ET.fromstring(xml)
  nodes=select(tree,{'resource-id':'com.android.permissioncontroller:id/title','text':'SMS Messenger'})
  if len(nodes)!=1:raise RuntimeError('target row missing')
  parents={child:parent for parent in tree.iter() for child in parent}
  radios=[x for x in parents[nodes[0]].iter('node') if x.get('class')=='android.widget.RadioButton']
  if len(radios)!=1:raise RuntimeError('target row radio missing')
  if p.foreground()!=chooser:raise RuntimeError('chooser changed before selection')
  tap(radios[0]);event('select_sms_radio')
  time.sleep(2)
  xml=p.tree();(out/'after-select.xml').write_bytes(xml)
  buttons=select(ET.fromstring(xml),{'resource-id':'android:id/button1','text':'Set as default'})
  if len(buttons)!=1 or buttons[0].get('enabled')!='true':raise RuntimeError('confirmation still disabled')
  if p.foreground()!=chooser:raise RuntimeError('chooser changed before confirm')
  tap(buttons[0]);event('confirm_default_sms')
  break
 else:raise RuntimeError('no unblocked chooser within development deadline')
 time.sleep(2)
 (out/'roles.txt').write_text(p.shell('dumpsys','role'))
 capture=p.capture(out/'after')
 r=dict(status='PASS' if capture['foreground_after'].startswith('com.simplemobiletools.smsmessenger/') else 'NOT_READY',
        kind='local setup diagnostic only, not an SMS send or paper trial',capture=capture,events=events)
except Exception as e:
 r=dict(status='FAILED',kind='local setup diagnostic only',error_type=type(e).__name__,reason=str(e),events=events)
 (out/'RESULT.json').write_text(json.dumps(r,indent=2));raise
(out/'RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(status=r['status'],output=str(out))),flush=True)
