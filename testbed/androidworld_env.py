"""Thin pinned AndroidWorld connection/agent factory; no replacement agent loop.

Connects an already-owned API33 AVD with explicit adb/gRPC ports. Install the
upstream accessibility forwarder during setup, not during measured episodes.
Neither backend truth nor calibration outcomes are accepted by this module.
"""
import hashlib
import importlib
from pathlib import Path
import subprocess


ANDROID_WORLD_COMMIT='55ddaf5edc6f6c25673aed343907d5b9dca66f84'
QWEN_REVISION='cc594898137f460bfe9f0759e9844b3ce807cfb5'


def verify_source(repository):
    """Compare imported native code to the clean pinned checkout before use."""
    repository=Path(repository).resolve()
    head=subprocess.run(['git','-C',str(repository),'rev-parse','HEAD'],
                        check=True,capture_output=True,text=True).stdout.strip()
    if head!=ANDROID_WORLD_COMMIT:raise ValueError('AndroidWorld source pin differs')
    dirty=subprocess.run(['git','-C',str(repository),'status','--porcelain','--untracked-files=no'],
                         check=True,capture_output=True,text=True).stdout
    if dirty.strip():raise ValueError('AndroidWorld tracked source has local changes')
    result={}
    for name in ('agents.m3a','agents.t3a','agents.base_agent','agents.infer',
                 'env.android_world_controller','env.interface','env.env_launcher','env.actuation'):
        module=importlib.import_module('android_world.'+name)
        installed=Path(module.__file__).read_bytes()
        original=(repository/'android_world'/Path(*name.split('.'))).with_suffix('.py').read_bytes()
        if installed!=original:raise ValueError('imported module differs from pinned source: '+name)
        result[name]=hashlib.sha256(installed).hexdigest()
    return dict(commit=head,imported_module_sha256=result,tracked_source_clean=True)


def connection_config(adb_path,console_port,adb_server_port,grpc_port,task_path):
    """Same native loader config, with the adb server explicitly preserved."""
    ports=(console_port,console_port+1,adb_server_port,grpc_port)
    if any(type(p) is not int or not 1024<=p<=65535 for p in ports) or len(set(ports))!=4:
        raise ValueError('distinct explicit unprivileged console/adb/server/gRPC ports required')
    if console_port%2:raise ValueError('AVD console port must be even')
    adb_path=Path(adb_path).resolve()
    if not adb_path.is_file():raise ValueError('explicit existing adb executable required')
    from android_env.components import config_classes as config
    return config.AndroidEnvConfig(
        task=config.FilesystemTaskConfig(path=str(task_path)),
        simulator=config.EmulatorConfig(
            emulator_launcher=config.EmulatorLauncherConfig(
                emulator_console_port=console_port,adb_port=console_port+1,grpc_port=grpc_port),
            adb_controller=config.AdbControllerConfig(adb_path=str(adb_path),
                adb_server_port=adb_server_port,device_name='emulator-'+str(console_port))))


def load_env(adb_path,console_port,adb_server_port,grpc_port,*,freeze_datetime):
    """Use native observation/action implementations; bind reconnect to our rig.

    This function can install/start instrumentation services and change guest UI
    settings through native AndroidEnv initialization. Freeze GUI reader profiles
    after that initialization. Caller owns emulator lifecycle and hard timeout.
    The upstream accessibility-forwarder APK must already be installed.
    """
    if type(freeze_datetime) is not bool:raise ValueError('explicit datetime policy required')
    from absl import logging
    from android_env import loader
    from android_world.env import android_world_controller as native
    from android_world.env import env_launcher,interface
    # Upstream adb_controller logs its inherited environment at INFO. Keep it
    # below WARNING here; callers should additionally launch with a minimal env.
    logging.set_verbosity(logging.WARNING)
    task_path=native._write_default_task_proto()
    def connect():
        raw=loader.load(connection_config(adb_path,console_port,adb_server_port,grpc_port,task_path))
        try:return IsolatedController(raw,install_a11y_forwarding_app=False)
        except BaseException:
            raw.close()
            raise
    class IsolatedController(native.AndroidWorldController):
        # Native refresh_env calls get_controller(), whose server defaults5037.
        # Only the connection factory changes; native a11y/actions stay intact.
        def refresh_env(self):
            self._env=connect().env
    controller=connect()
    env=interface.AsyncAndroidEnv(controller)
    try:
        env_launcher.setup_env(env,emulator_setup=False,freeze_datetime=freeze_datetime)
    except BaseException:
        env.close()
        raise
    return env


def make_agent(framework,env,endpoint,model_id,journal=None):
    """Construct native M3A/T3A; preserve defaults, prompt, history and parsers."""
    from local_model import LocalModel,TextOnlyModel
    if framework=='m3a':
        from android_world.agents.m3a import M3A
        return M3A(env,LocalModel(endpoint,model_id,2048,journal=journal))
    if framework=='t3a':
        from android_world.agents.t3a import T3A
        return T3A(env,TextOnlyModel(endpoint,model_id,2048,journal=journal))
    raise ValueError('this factory binds only M3A/T3A; other frameworks need their native bindings')


class EpochStop(BaseException):
    """Host-controlled stop that native broad `except Exception` cannot swallow.

    The outer harness must catch this explicitly and record ASK/PENDING/fault
    fate. This marker alone does not implement protected dispatch or recovery.
    """
