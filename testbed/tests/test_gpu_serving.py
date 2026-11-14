"""GPU profiles of serve_model.py and the SYNTHETIC fake_model.py rule. No GPU, model or AVD."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from serve_model import command_for, image_policy
from fake_model import reply

QWEN = dict(repo_id='Qwen/Qwen2.5-VL-7B-Instruct', env_prefix='QWEN')


def flag(command, name):
    return command[command.index(name) + 1]


def screen(*items, history=''):
    lines = ['UI element %d: %r' % (i, dict(index=i, **item)) for i, item in enumerate(items)]
    return ('The current user goal/request is: Send an email to bob@test.invalid with the subject "Lease gx:ABC123" '
            'and the text "Signed lease attached later."\n' + history + '\n'.join(lines) + '\nYour Answer:\n')


class GpuProfiles(unittest.TestCase):
    def test_only_memory_settings_differ_between_gpus(self):
        a10g, h100 = (command_for(QWEN, 'snap', 8101, 'singleton', g) for g in ('a10g', 'h100'))
        self.assertEqual((flag(a10g, '--gpu-memory-utilization'), flag(a10g, '--max-num-seqs')), ('0.9', '1'))
        self.assertEqual((flag(h100, '--gpu-memory-utilization'), flag(h100, '--max-num-seqs')), ('0.85', '2'))
        strip = lambda c: [x for i, x in enumerate(c) if c[i - 1] not in ('--gpu-memory-utilization', '--max-num-seqs')]
        self.assertEqual(strip(a10g), strip(h100))
        self.assertIn('"max_pixels": 3211264', flag(a10g, '--mm-processor-kwargs'))
        self.assertEqual(flag(a10g, '--max-model-len'), '32768')

    def test_screenshot_is_not_resized_by_the_cap(self):
        rounded = round(2400 / 28) * 28 * round(1080 / 28) * 28   # Qwen smart_resize before the max_pixels check
        self.assertLessEqual(rounded, 3211264)
        self.assertIn('not resized', image_policy(QWEN))

    def test_dual_and_unknown_gpu_are_refused(self):
        with self.assertRaises(ValueError):
            command_for(QWEN, 'snap', 8101, 'dual', 'a10g')
        with self.assertRaises(ValueError):
            command_for(QWEN, 'snap', 8101, 'singleton', 't4')


class FakeModel(unittest.TestCase):
    def test_compose_fill_send_then_done(self):
        listing = dict(content_description='Compose', is_clickable=True)
        compose = [dict(content_description='Send', is_clickable=True), dict(is_editable=True),
                   dict(hint_text='Subject', is_editable=True), dict(hint_text='Message', is_editable=True)]
        self.assertIn('"action_type": "click", "index": 0', reply(screen(listing)))
        steps, history = [], ''
        for _ in range(4):
            answer = reply(screen(*compose, history=history))
            marker = answer.split()[1]
            steps.append((marker, answer))
            history += 'Step - Summary: %s done\n' % marker
        self.assertEqual([m for m, _ in steps], ['fake:to', 'fake:subject', 'fake:body', 'fake:send'])
        self.assertIn('"text": "bob@test.invalid", "index": 1', steps[0][1])
        self.assertIn('"text": "Lease gx:ABC123", "index": 2', steps[1][1])
        dialog = reply(screen(dict(text='Cancel'), dict(text='Send and Delete'), history=history))
        self.assertIn('"index": 1', dialog)
        self.assertIn('"goal_status": "complete"', reply(screen(listing, history=history)))

    def test_summary_echoes_the_marker(self):
        self.assertEqual(reply('...Based on the reason: fake:subject\n...Summary of this step: '), 'fake:subject done')


class ActionAlias(unittest.TestCase):
    def test_only_the_type_action_name_changes(self):   # dev-01, 14/11: Qwen writes "type", M3A wants "input_text"
        from local_model import alias_action_type
        text = 'Reason: To field.\nAction: {"action_type": "type", "text": "type here", "index": 9}'
        self.assertEqual(alias_action_type(text),
                         ('Reason: To field.\nAction: {"action_type": "input_text", "text": "type here", "index": 9}', 1))
        for unchanged in ('{"action_type": "click", "index": 2}', '{"action_type": "typed"}', 'type the text'):
            self.assertEqual(alias_action_type(unchanged), (unchanged, 0))


if __name__ == '__main__':
    unittest.main()
