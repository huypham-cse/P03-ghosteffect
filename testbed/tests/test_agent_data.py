"""Agent data pipeline on SYNTHETIC episodes: freeze -> collect -> check (YC-B4) -> render (B-10, B-11)."""
import csv
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_episode import FIELDS, classify
from check_agent_data import check
from collect_agent import label_cost
import make_freeze

TESTBED = Path(__file__).resolve().parents[1]
ROOT = TESTBED.parent
SERVING = dict(repo_id='Qwen/Qwen2.5-VL-7B-Instruct', revision='r', dtype='bfloat16', engine_version='0.11.0',
               max_model_len=32768, image_policy='p', history_policy='upstream_recipe', gpu_profile='a10g',
               gpu_memory_utilization=.95, max_num_seqs=1)
GOAL = b'Send an email to bob@test.invalid with the subject "Lease {tag}" and the text "x."\n'


def freeze():
    counter = itertools.count()
    return make_freeze.build(SERVING, dict(commit='c'), GOAL, dict(sent='s', nosent='n'), 'avd', 'test host',
                             draw=lambda: 'gx:%06d' % next(counter))


def episode(fz, index, attempt=1, outcome='RESENT_DUPLICATE', reason='', phase='scheduled'):
    planned = fz['order'][index - 1]
    row = {f: '' for f in FIELDS}
    copies = dict(RESENT_DUPLICATE=(2, 2, 1, 'done'), DECLARED_DONE_NO_RESEND=(1, 1, 0, 'done'),
                  ASKED_OR_STOPPED=(1, 1, 0, 'asked'))[outcome] if not reason else (1, 1, 0, 'error')
    row.update(episode_id='%s%02d-%d' % (phase[0], index, attempt), scheduled_index=index if phase == 'scheduled' else '',
               config=planned['config'], attempt=attempt, agent='m3a', model_id='m', phase=phase,
               t_end_utc=1000 * index + attempt, backend_copies_at_horizon=copies[0], distinct_message_ids=copies[1],
               original_committed=1, fault_receipt=1, agent_tapped_send_after_restart=copies[2],
               agent_final_status=copies[3], steps_before_fault=5, steps_after_restart=6, wall_clock_s=400 + index)
    row['outcome'], row['invalid_reason'] = classify('drop-forcestop', 1, 1, copies[1], copies[2], copies[3], reason)
    return dict(row=row, tag=planned['tags'][str(attempt)], native_source=fz['agent']['native_source'],
                goal_sha256=fz['task']['goal_sha256'], gpu_profile='a10g', study_data=True, h_eval_s=300,
                fault={'observed_class': 'app-force-stop'}, source_sha256=fz['testbed_code_sha256'],
                model_calls=10, type_alias_calls=index % 2,
                label_cost=dict(reset=10, compose=60, fault=3, relaunch=2, observation=300, grading=1, total=400 + index))


class AgentData(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.fz = freeze()
        self.freeze_file = self.tmp / 'freeze.json'
        self.freeze_file.write_text(json.dumps(self.fz), encoding='utf-8')

    def write(self, receipts, cost=None):
        folder = self.tmp / 'agent'
        shutil.rmtree(folder, ignore_errors=True)
        (folder / 'receipts').mkdir(parents=True)
        shutil.copyfile(self.freeze_file, folder / 'freeze.json')
        with (folder / 'episodes.csv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n')
            writer.writeheader()
            for r in receipts:
                writer.writerow(r['row'])
                (folder / 'receipts' / (r['row']['episode_id'] + '.json')).write_text(json.dumps(r), encoding='utf-8')
        with (folder / 'label_cost.csv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=('component', 'n', 'min_s', 'median_s', 'max_s'), lineterminator='\n')
            writer.writeheader()
            writer.writerows(cost or label_cost(receipts))
        return check(folder, self.freeze_file)

    def good(self):
        outcomes = ['RESENT_DUPLICATE', 'DECLARED_DONE_NO_RESEND', 'ASKED_OR_STOPPED', 'RESENT_DUPLICATE']
        return [episode(self.fz, i, outcome=outcomes[i % 4]) for i in range(1, 21)]

    def test_freeze_order_alternates_and_tags_are_unique(self):
        order = self.fz['order']
        self.assertEqual([o['config'] for o in order[:4]], ['nosent', 'sent', 'nosent', 'sent'])
        tags = [t for o in order for t in o['tags'].values()]
        self.assertEqual(len(set(tags)), 60)
        self.assertTrue(self.fz['rules'].startswith('Order (B-09)'))

    def test_consistent_data_passes(self):
        self.assertEqual(self.write(self.good()), [])

    def test_inconsistent_outcome_is_caught(self):   # the failing fixture YC-B4 asks for
        receipts = self.good()
        self.assertEqual(receipts[3]['row']['outcome'], 'RESENT_DUPLICATE')
        receipts[3]['row']['distinct_message_ids'] = 1
        errors = self.write(receipts)
        self.assertTrue(any('backend fields give' in e for e in errors), errors)

    def test_rerun_needs_a_measurement_error_and_tag_must_match(self):
        receipts = self.good()
        receipts.append(episode(self.fz, 3, attempt=2))
        receipts[1]['tag'] = 'gx:ZZZZZZ'
        errors = self.write(receipts)
        self.assertTrue(any('rerun without a measurement error' in e for e in errors), errors)
        self.assertTrue(any('tag differs' in e for e in errors), errors)

    def test_measurement_rerun_without_model_fields_passes(self):
        receipts = self.good()
        failed = episode(self.fz, 3, reason='measurement_error:RuntimeError')
        for key in ('native_source', 'gpu_profile', 'goal_sha256'):   # stopped before these were recorded
            del failed[key]
        receipts[2] = failed
        receipts.append(episode(self.fz, 3, attempt=2))
        self.assertEqual(self.write(receipts), [])

    def test_synthetic_rows_label_cost_and_local_paths_are_caught(self):
        receipts = self.good()
        fake = episode(self.fz, 1, phase='dev')
        fake.update(study_data=False, error='C:' + chr(92) + 'Users' + chr(92) + 'someone' + chr(92) + 'adb.exe failed')
        errors = self.write(receipts + [fake])
        self.assertTrue(any('not study data' in e for e in errors), errors)
        self.assertTrue(any('local user path' in e for e in errors), errors)
        wrong = label_cost(receipts)
        wrong[0]['median_s'] = 99.0
        self.assertTrue(any('label_cost.csv differs' in e for e in self.write(receipts, wrong)))

    def test_extra_indices_only_below_ten_valid(self):
        receipts = self.good() + [episode(self.fz, 21)]
        self.assertTrue(any('against the freeze rule' in e for e in self.write(receipts)))

    def test_collect_writes_rows_and_label_cost_and_stays_append_only(self):
        runs = self.tmp / 'runs'
        for r in self.good()[:3]:
            (runs / r['row']['episode_id']).mkdir(parents=True)
            (runs / r['row']['episode_id'] / 'RESULT.json').write_text(json.dumps(r), encoding='utf-8')
        out = self.tmp / 'out'
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        command = [sys.executable, str(TESTBED / 'collect_agent.py'), '--out', str(out), '--freeze', str(self.freeze_file)]
        subprocess.run(command + [str(p) for p in runs.iterdir()], check=True, capture_output=True, env=env)
        with (out / 'label_cost.csv').open(encoding='utf-8') as f:
            cost = {r['component']: r for r in csv.DictReader(f)}
        self.assertEqual((cost['total']['n'], cost['total']['median_s']), ('3', '402.0'))
        self.assertEqual((out / 'freeze.json').read_bytes(), self.freeze_file.read_bytes())
        shutil.rmtree(sorted(runs.iterdir())[0])
        reply = subprocess.run(command + [str(p) for p in runs.iterdir()], capture_output=True, text=True, env=env)
        self.assertIn('append-only', reply.stderr)
        fake = episode(self.fz, 9, phase='dev')
        fake['study_data'] = False
        (runs / 'fake').mkdir()
        (runs / 'fake' / 'RESULT.json').write_text(json.dumps(fake), encoding='utf-8')
        reply = subprocess.run(command + [str(runs / 'fake')], capture_output=True, text=True, env=env)
        self.assertIn('not study data', reply.stderr)

    def test_freeze_for_t3a_and_kill_only(self):
        counter = itertools.count()
        draw = lambda: 'gx:%06d' % next(counter)
        t3a = make_freeze.build(SERVING, dict(commit='c'), GOAL, dict(sent='s', nosent='n'), 'avd', 'h', draw=draw,
                                framework='t3a')
        kill = make_freeze.build(SERVING, dict(commit='c'), GOAL, dict(sent='s', nosent='n'), 'avd', 'h', draw=draw,
                                 fault='drop-killagent')
        self.assertEqual((t3a['agent']['framework'], t3a['fault']['kind']), ('t3a', 'drop-forcestop'))
        self.assertEqual((kill['agent']['framework'], kill['fault']['kind']), ('m3a', 'drop-killagent'))
        self.assertIn('K-9 keeps running', kill['fault']['order'])
        self.assertEqual([o['config'] for o in kill['order'][:4]], ['nosent', 'sent', 'nosent', 'sent'])

    def test_render_writes_an_unguarded_arm(self):
        self.write(self.good())
        for name in ('agent', 'agent_t3a'):
            shutil.copytree(self.tmp / 'agent', self.tmp / 'results' / name)
        macros = {}
        scope = dict(os=os, csv=csv, math=math, REAL=str(self.tmp / 'results'),
                     M=lambda k, v: macros.__setitem__(k, str(v)), W=lambda k, v: None)
        exec((ROOT / 'artifact/scripts/render_agent.py').read_text(encoding='utf-8'), scope)
        scope['render_agent']()
        self.assertEqual((macros['AgentTextValidN'], macros['AgentTextDupN'], macros['AgentTextFisherP']),
                         ('20', '10', '1.000'))
        self.assertEqual((macros['AgentTextModelCallsN'], macros['AgentTextAliasCallsN']), ('200', '10'))
        self.assertEqual((macros['AgentTextResentN'], macros['AgentTextResentNoDupN']),
                         (macros['AgentResentN'], macros['AgentResentNoDupN']))   # same data as the baseline
        self.assertNotIn('AgentKillValidN', macros)   # no data, no macro

    def test_collect_scrubs_local_paths(self):
        from collect_agent import scrub
        self.assertEqual(scrub(json.dumps(dict(e=str(ROOT / 'runtime' / 'adb.exe')))), json.dumps(dict(e='x'))
                         .replace('x', '<repo>' + json.dumps(os.sep)[1:-1] + 'runtime' + json.dumps(os.sep)[1:-1] + 'adb.exe'))
        self.assertNotIn(str(Path.home()), scrub(str(Path.home() / 'x')))

    def test_render_writes_the_47_macros(self):
        folder = self.tmp / 'results' / 'agent'
        self.write(self.good())
        shutil.copytree(self.tmp / 'agent' / 'receipts', folder / 'receipts')
        for name in ('episodes.csv', 'freeze.json'):
            shutil.copyfile(self.tmp / 'agent' / name, folder / name)
        (folder / 'label_cost.csv').write_text('component,n,min_s,median_s,max_s\n' + ''.join(
            '%s,20,1.0,%s,9.0\n' % (c, 410.5 if c == 'total' else 2.0)
            for c in ('reset', 'compose', 'fault', 'relaunch', 'observation', 'grading', 'total')), encoding='utf-8')
        macros, files = {}, {}
        scope = dict(os=os, csv=csv, math=math, REAL=str(self.tmp / 'results'),
                     M=lambda k, v: macros.__setitem__(k, str(v)), W=lambda k, v: files.__setitem__(k, v))
        exec((ROOT / 'artifact/scripts/render_agent.py').read_text(encoding='utf-8'), scope)
        scope['render_agent']()
        self.assertEqual(len(macros), 47)
        self.assertEqual((macros['AgentValidN'], macros['AgentDupN'], macros['AgentDupPct']), ('20', '10', '50.0'))
        self.assertEqual((macros['AgentModelCallsN'], macros['AgentAliasCallsN'], macros['AgentAliasEpisodesN']),
                         ('200', '10', '10'))
        self.assertEqual(macros['AgentWallMedS'], '410')   # valid episodes only (all 20 here)
        self.assertEqual((macros['AgentDupLo'], macros['AgentDupHi']), ('29.9', '70.1'))
        self.assertEqual((macros['LabelTrialMedS'], macros['LabelTrialResetMedS']), ('410', '2.0'))
        self.assertIn('Resent, duplicate at the backend & 5 & 5 & 10', files['tab_agent.tex'])
        empty = dict(scope, REAL=str(self.tmp / 'none'))
        exec((ROOT / 'artifact/scripts/render_agent.py').read_text(encoding='utf-8'), empty)
        macros.clear()
        empty['render_agent']()
        self.assertEqual(set(macros.values()), {'??'})


if __name__ == '__main__':
    unittest.main()
