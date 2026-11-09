"""Native-source binding checks, with no device, weights or model API calls.

Run with runtime/agent-venv/Scripts/python.exe. Stdlib-only host test discovery
skips this module's native checks explicitly when AndroidWorld is not installed.
"""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from androidworld_env import connection_config,load_env,make_agent,verify_source


@unittest.skipUnless(importlib.util.find_spec('android_world'),'pinned AndroidWorld agent environment required')
class NativeBindingTests(unittest.TestCase):
    def test_imported_agent_and_environment_match_the_frozen_checkout(self):
        root=Path(__file__).resolve().parents[2]
        result=verify_source(root/'runtime/vendor/android_world_full')
        self.assertTrue(result['tracked_source_clean'])
        self.assertEqual(len(result['imported_module_sha256']),8)

    def test_real_native_config_and_reconnect_keep_the_isolated_adb_server(self):
        from android_env import loader
        from android_world.env import android_world_controller as native
        from android_world.env import env_launcher
        root=Path(__file__).resolve().parents[2]
        adb=root/'runtime/android-sdk/platform-tools/adb.exe'
        class Raw:
            def reset(self):return None
            def close(self):pass
        seen=[]
        def loaded(config):
            seen.append(config)
            return Raw()
        with patch.object(loader,'load',side_effect=loaded), \
             patch.object(native,'apply_a11y_forwarder_app_wrapper',side_effect=lambda raw,flag:raw), \
             patch.object(env_launcher,'setup_env') as setup:
            env=load_env(adb,5580,5038,8554,freeze_datetime=False)
            first=env.controller.env
            env.controller.refresh_env()
            self.assertIsNot(first,env.controller.env)
            setup.assert_called_once_with(env,emulator_setup=False,freeze_datetime=False)
            env.close()
        self.assertEqual(len(seen),2)
        for config in seen:
            self.assertEqual(config.simulator.adb_controller.adb_server_port,5038)
            self.assertEqual(config.simulator.adb_controller.device_name,'emulator-5580')
            self.assertEqual(config.simulator.emulator_launcher.grpc_port,8554)
            self.assertEqual(config.simulator.emulator_launcher.adb_port,5581)
        for ports in ((5581,5038,8554),(5580,5581,8554),(5580,5038,5038)):
            with self.assertRaises(ValueError):connection_config(adb,*ports,'unused')

    def test_factory_returns_native_agents_without_changing_native_defaults(self):
        from android_world.agents.m3a import M3A
        from android_world.agents.t3a import T3A
        from local_model import TextOnlyModel
        env=object()
        a=make_agent('m3a',env,'http://127.0.0.1:8000/v1','Qwen/Qwen2.5-VL-7B-Instruct')
        b=make_agent('t3a',env,'http://127.0.0.1:8000/v1','Qwen/Qwen2.5-VL-7B-Instruct')
        self.assertIs(type(a),M3A)
        self.assertIs(type(b),T3A)
        self.assertIs(a.env,env)
        self.assertIs(b.env,env)
        self.assertEqual(a.wait_after_action_seconds,2.0)
        self.assertEqual(a.transition_pause,1.0)
        self.assertEqual(b.transition_pause,1.0)
        self.assertIsInstance(b.llm,TextOnlyModel)
        with self.assertRaises(ValueError):b.llm.predict_mm('unused',[b'not sent'])
        with self.assertRaises(ValueError):make_agent('agentprog',env,'http://127.0.0.1:8000/v1','unused')


if __name__=='__main__':unittest.main()
