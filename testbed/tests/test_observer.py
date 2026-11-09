"""Synthetic screen/model fixtures for the real GUI adapter's boundaries."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from observer import GUIObserver
import test_probes as probe_fixtures

XML=b'<hierarchy><node resource-id="account" text="alice"/><node resource-id="title" text="room"/><node resource-id="timeline"><node resource-id="anchor"/><node resource-id="row"><node resource-id="outgoing"/><node resource-id="ack"/><node text="gx:ABC123"/></node></node></hierarchy>'


class Device:
    def foreground(self):return 'test.app/.Main'
    def tree(self):return XML
    def capture(self,directory):
        directory.mkdir(parents=True)
        (directory/'tree.xml').write_bytes(XML)
        (directory/'screen.png').write_bytes(b'\x89PNG\r\n\x1a\nSYNTHETIC')
        return dict(stable_tree=True,same_foreground=True,foreground_after='test.app/.Main',
                    mono_start_ns=0,mono_end_ns=1,tree_sha256=hashlib.sha256(XML).hexdigest())


class ObserverTests(unittest.TestCase):
    def profile(self):
        return dict(frozen=True,profile_id='synthetic',package='test.app',
                    account={'resource-id':'account','text':'alice'},title={'resource-id':'title','text':'room'},
                    timeline={'resource-id':'timeline'},anchor={'resource-id':'anchor'},row={'resource-id':'row'},
                    outgoing={'resource-id':'outgoing'},acknowledged={'resource-id':'ack'},
                    views=dict(nonce={'sent':{}},vlm={'detail':{'actions':[]}}))

    def test_verifier_receives_one_image_description_and_no_agent_history(self):
        calls=[]
        class Verifier:
            def predict_mm(self,prompt,images):
                calls.append((prompt,images));return '{"verdict":"com"}',None,{}
        with tempfile.TemporaryDirectory() as temp:
            observer=GUIObserver(Device(),self.profile(),'send test item','gx:ABC123',{},Path(temp)/'views',Verifier())
            self.assertEqual(observer.read('vlm','detail'),1)
            self.assertEqual(len(calls[0][1]),1)
            self.assertIn('send test item',calls[0][0])
            self.assertNotIn('backend',calls[0][0])

    def test_unconfigured_view_or_unqualified_hop1_is_bot(self):
        with tempfile.TemporaryDirectory() as temp:
            observer=GUIObserver(Device(),self.profile(),'send test item','gx:ABC123',{},Path(temp)/'views')
            self.assertIsNone(observer.read('nonce','missing'))
            self.assertIsNone(observer.read('hop1','outbox'))
            self.assertEqual(observer.monitor()['state'],'stuck')

    def test_bad_verifier_answer_is_bot_without_extracting_prose_vote(self):
        class Verifier:
            def predict_mm(self,prompt,images):return 'Probably done',None,{}
        with tempfile.TemporaryDirectory() as temp:
            observer=GUIObserver(Device(),self.profile(),'send test item','gx:ABC123',{},Path(temp)/'views',Verifier())
            self.assertIsNone(observer.read('vlm','detail'))

    def test_nonce_off_hop1_counts_against_pre_tap_baseline_not_old_lookalike(self):
        fixtures=probe_fixtures.DigestTests();fixtures.setUp()
        HISTORY_XML=probe_fixtures.XML
        before=fixtures.snapshot()
        profile=fixtures.profile;profile['hop1_qualified']=True
        config=dict(verified_bottom=True,match_fields={'recipient':'bob','body':'same content'})
        profile['views']={'hop1':{'outbox':config}}
        start=HISTORY_XML.index(b'<node resource-id="row">');end=HISTORY_XML.index(b'</node></node></hierarchy>')+len(b'</node>')
        row=HISTORY_XML[start:end]
        class Captured(GUIObserver):
            xml=HISTORY_XML
            def capture_view(self,family,view):
                checksum=hashlib.sha256(self.xml).hexdigest()
                meta=dict(stable_tree=True,same_foreground=True,tree_sha256=checksum,foreground_after='test.app/.Main')
                directory=self.output/'one';directory.mkdir(exist_ok=True)
                return config,self.xml,meta,dict(direction='latest',unchanged_swipes=2,tree_sha256=checksum),directory,profile
            def verify_context(self):return True
        with tempfile.TemporaryDirectory() as temp:
            observer=Captured(Device(),profile,'send same content','',{'hop1':{'outbox':before}},Path(temp)/'views')
            self.assertEqual(observer.read('hop1','outbox'),0)
            observer.xml=HISTORY_XML[:end]+row+HISTORY_XML[end:]
            self.assertEqual(observer.read('hop1','outbox'),1)
            observer.xml=HISTORY_XML[:end]+row+row+HISTORY_XML[end:]
            self.assertIsNone(observer.read('hop1','outbox'))
            observer.pre_snapshots={}
            self.assertIsNone(observer.read('hop1','outbox'))

    def test_monitor_ignores_unrelated_status_and_nonce_prefix_collision(self):
        profile=self.profile();profile['hop1_qualified']=True
        profile['monitor']=dict(entry_selector={'resource-id':'row'},acked_selector={'resource-id':'ack'})
        with tempfile.TemporaryDirectory() as temp:
            observer=GUIObserver(Device(),profile,'send test item','gx:ABC124',{},Path(temp)/'views')
            self.assertEqual(observer.monitor()['state'],'stuck')
            observer.nonce='gx:ABC12'
            self.assertEqual(observer.monitor()['state'],'stuck')
            observer.nonce='gx:ABC123'
            self.assertEqual(observer.monitor()['state'],'acked')


if __name__=='__main__':unittest.main()
