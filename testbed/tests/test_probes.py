"""Synthetic GUI fixtures verify semantic digest/classifier failure boundaries."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from probes import history_snapshot, read_digest
from classifier import classify, commit_slot_id

XML=b'''<hierarchy><node text="alice" resource-id="account"/><node text="room" resource-id="title"/>
<node resource-id="timeline"><node resource-id="anchor"/><node resource-id="row">
<node resource-id="outgoing"/><node resource-id="ack"/><node resource-id="recipient" text="bob"/>
<node resource-id="message" text="same content"/></node></node></hierarchy>'''


class DigestTests(unittest.TestCase):
    def setUp(self):
        self.profile=dict(frozen=True,profile_id='synthetic',package='test.app',
                          account={'resource-id':'account','text':'alice'},title={'resource-id':'title','text':'room'},
                          timeline={'resource-id':'timeline'},anchor={'resource-id':'anchor'},row={'resource-id':'row'},
                          outgoing={'resource-id':'outgoing'},acknowledged={'resource-id':'ack'},exclude=[{'resource-id':'failed'}],
                          history_fields=dict(recipient={'resource-id':'recipient'},body={'resource-id':'message'}))

    def snapshot(self,xml=XML):
        checksum=hashlib.sha256(xml).hexdigest()
        return history_snapshot(xml,dict(stable_tree=True,same_foreground=True,tree_sha256=checksum,
                                         foreground_after='test.app/.Main'),self.profile,
                                dict(recipient='bob',body='same content'),
                                dict(direction='latest',unchanged_swipes=2,tree_sha256=checksum))

    def test_layout_change_does_not_become_a_new_history_item(self):
        before=self.snapshot();after=self.snapshot(XML.replace(b'text="same content"',b'text="same content" bounds="[0,0][5,5]"'))
        self.assertEqual(before['snapshot']['semantic_sha256'],after['snapshot']['semantic_sha256'])
        self.assertEqual(read_digest(before,after)['verdict'],'abs')

    def test_old_lookalike_is_not_new_but_second_matching_item_is(self):
        start=XML.index(b'<node resource-id="row">');end=XML.index(b'</node></node></hierarchy>')+len(b'</node>')
        row=XML[start:end]
        before=self.snapshot();after=self.snapshot(XML[:end]+row+XML[end:])
        self.assertEqual(read_digest(before,after)['verdict'],'com')
        self.assertEqual(read_digest(before,after)['added'],1)
        self.assertTrue(read_digest(before,after)['lookalike'])
        self.assertEqual(read_digest(after,before)['verdict'],'BOT')

    def test_wrong_account_failed_or_missing_field_never_positive(self):
        self.assertEqual(self.snapshot(XML.replace(b'alice',b'other'))['verdict'],'BOT')
        failed=self.snapshot(XML.replace(b'"ack"',b'"failed"'))
        self.assertEqual(failed['snapshot']['matches'],0)
        missing=self.snapshot(XML.replace(b'"message"',b'"missing"'))
        self.assertEqual(missing['verdict'],'BOT')


class ClassifierTests(unittest.TestCase):
    def test_target_lexicon_and_structured_effect_not_other_screen_text(self):
        xml=b'<hierarchy><node resource-id="test:id/btnSend" bounds="[0,0][50,50]"/><node text="delete" bounds="[80,0][100,20]"/></hierarchy>'
        self.assertTrue(classify(dict(action_type='tap',x=25,y=25),xml)['commit_candidate'])
        self.assertIsNone(classify(dict(action_type='tap',x=60,y=25),xml)['commit_candidate'])
        self.assertTrue(classify({},b'',structured_effect=True)['commit_candidate'])
        self.assertIsNone(classify(dict(action_type='tap',x=25,y=25),xml,locale='unconfigured')['commit_candidate'])

    def test_slot_id_survives_wording_and_is_separate_for_new_logical_effect(self):
        self.assertEqual(commit_slot_id('r','task','send'),commit_slot_id('r','task','send'))
        self.assertNotEqual(commit_slot_id('r','task','send'),commit_slot_id('r','task','other-send'))


if __name__=='__main__':unittest.main()
