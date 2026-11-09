"""One native AndroidWorld observation on an already-owned test AVD.

No agent step, model, task grader, backend access or calibration output. Parent
owns boot/shutdown and hard timeout; a failed observation is retained as failed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb',type=Path,required=True)
    parser.add_argument('--console-port',type=int,required=True)
    parser.add_argument('--adb-server-port',type=int,required=True)
    parser.add_argument('--grpc-port',type=int,required=True)
    parser.add_argument('--expected-package',required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--scripted-agent-wire',action='store_true',help='explicit SYNTHETIC responses to test native M3A/T3A BACK/reflection wiring; no LLM inference')
    args=parser.parse_args()
    if args.output.exists():parser.error('fresh output required')
    from ui import ADB,validate_package
    validate_package(args.expected_package)
    args.output.mkdir(parents=True)
    root=Path(__file__).resolve().parents[1]
    os.environ.update(ANDROID_ADB_SERVER_PORT=str(args.adb_server_port),
                      ADB_SERVER_SOCKET='tcp:127.0.0.1:'+str(args.adb_server_port))
    screen=ADB(args.adb,'emulator-'+str(args.console_port))
    from androidworld_env import verify_source,load_env
    result=dict(status='RUNNING',kind='native AndroidWorld observation smoke',study_result=False,
                models_loaded=False,model_driven_agent_steps=0,scripted_native_steps=0,paid_model_api_calls=0,
                started_utc_ns=time.time_ns(),freeze_datetime=False,
                console_port=args.console_port,adb_server_port=args.adb_server_port,grpc_port=args.grpc_port,
                source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (
                    Path(__file__),Path(__file__).with_name('androidworld_env.py'),Path(__file__).with_name('ui.py'))})
    env=None
    try:
        result['native_source']=verify_source(root/'runtime/vendor/android_world_full')
        print('CONNECT native AndroidWorld to existing owned AVD',flush=True)
        env=load_env(args.adb,args.console_port,args.adb_server_port,args.grpc_port,freeze_datetime=False)
        # Mirror native runner initialization: reset/home first, then initialize
        # the target app. Starting the forwarder under an already-static screen
        # can yield an empty initial forest. This is setup, not extra votes.
        initial=env.reset(go_home=True)
        component=screen.shell('cmd','package','resolve-activity','--brief',
            '-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER',args.expected_package).splitlines()[-1]
        if not component.startswith(args.expected_package+'/'):raise RuntimeError('target launcher unresolved')
        screen.launch(component)
        env.hide_automation_ui()
        result['setup_sequence']=['load_env','native reset(go_home=True)','launch target app','hide automation pointer UI']
        result['initial_reset_elements']=len(initial.ui_elements)
        print('CAPTURE one native screenshot/accessibility forest',flush=True)
        before=screen.foreground_window(args.output/'window-before')
        started=time.monotonic_ns()
        state=env.get_state(wait_to_stabilize=False)
        ended=time.monotonic_ns()
        after=screen.foreground_window(args.output/'window-after')
        from PIL import Image
        pixels=state.pixels
        if str(pixels.dtype)!='uint8' or len(pixels.shape)!=3 or pixels.shape[2]!=3:
            raise ValueError('invalid native RGB observation')
        Image.fromarray(pixels).save(args.output/'screen.png')
        forest=state.forest.SerializeToString(deterministic=True)
        (args.output/'forest.pb').write_bytes(forest)
        # Debug representation comes from the same single native observation,
        # not another GUI read or a second calibrated view.
        (args.output/'forest.txt').write_text(str(state.forest),encoding='utf-8')
        from dataclasses import asdict
        elements=[asdict(element) for element in state.ui_elements]
        (args.output/'ui-elements.json').write_text(json.dumps(elements,indent=2),encoding='utf-8')
        if not forest or not elements:raise RuntimeError('empty native accessibility observation')
        result.update(status='PASS' if before==after and after['component'].startswith(args.expected_package+'/') else 'NOT_READY',
                      mono_start_ns=started,mono_end_ns=ended,window_before=before,window_after=after,
                      image_shape=list(pixels.shape),forest_sha256=hashlib.sha256(forest).hexdigest(),
                      ui_elements=len(elements),same_window=before==after,
                      scope='single native observation; not reader calibration, stable-screen proof or agent episode')
        if args.scripted_agent_wire:
            from smoke_agent_wire import run
            result['scripted_agent_wiring']={}
            for framework in ('m3a','t3a'):
                print('SYNTHETIC transport fixture, native '+framework+' BACK/reflection step',flush=True)
                wire=run(env,framework,args.output/('scripted-wire-'+framework))
                result['scripted_agent_wiring'][framework]=wire['status']
                result['scripted_native_steps']+=1
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc))
        raise
    finally:
        if env is not None:env.close()
        result['finished_utc_ns']=time.time_ns()
        (args.output/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],output=str(args.output))),flush=True)
    if result['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
