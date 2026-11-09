"""Local SDK package selection/extraction checks; no SDK network calls here."""
import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from setup_android import archive_info,extract
from smoke_android import sms_role_action


class AndroidSetupTests(unittest.TestCase):
    def test_sms_setup_taps_the_radio_then_confirms_or_closes_an_already_default_dialog(self):
        # Synthetic selector fixture based on the observed API33 role dialog.
        def dialog(checked,summary='',enabled='true'):
            return ('<hierarchy><node><node resource-id="com.android.permissioncontroller:id/title" text="SMS Messenger"/>'
                    '<node class="android.widget.RadioButton" enabled="true" checked="'+checked+'"/>'
                    '<node text="'+summary+'"/></node><node resource-id="android:id/button1" text="Set as default" enabled="'+enabled+'"/>'
                    '<node resource-id="android:id/button2" text="Cancel" enabled="true"/></hierarchy>')
        action,node=sms_role_action(dialog('false'))
        self.assertEqual(action,'select-radio')
        self.assertEqual(node.get('class'),'android.widget.RadioButton')
        self.assertEqual(sms_role_action(dialog('true'))[0],'confirm-default')
        self.assertEqual(sms_role_action(dialog('true','Current default','false'))[0],'close-already-default-dialog')
        with self.assertRaises(RuntimeError):sms_role_action(dialog('true','','false'))
        with self.assertRaises(RuntimeError):sms_role_action(dialog('false','Current default'))
        with self.assertRaises(RuntimeError):sms_role_action('<hierarchy/>')

    def test_exact_emulator_revision_is_selected_not_newer_release(self):
        xml=b'''<repository><remotePackage path="emulator"><revision><major>37</major><minor>2</minor><micro>13</micro></revision>
<archives><archive><host-os>windows</host-os><complete><size>10</size><checksum type="sha1">test</checksum><url>exact.zip</url></complete></archive></archives></remotePackage>
<remotePackage path="emulator"><revision><major>37</major><minor>3</minor><micro>8</micro></revision><archives/></remotePackage></repository>'''
        self.assertEqual(archive_info(xml,'emulator','37.2.13')['url'],'exact.zip')
        with self.assertRaises(ValueError):archive_info(xml,'emulator','UNAVAILABLE')

    def test_sdk_zip_cannot_escape_or_overwrite_an_edited_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);archive=directory/'input.zip';target=directory/'sdk'
            with zipfile.ZipFile(archive,'w') as zipped:zipped.writestr('../escape','bad')
            with self.assertRaises(ValueError):extract(archive,target)
            self.assertFalse((directory/'escape').exists())
            with zipfile.ZipFile(archive,'w') as zipped:zipped.writestr('cmdline-tools/bin/sdkmanager.bat','original')
            extract(archive,target,'cmdline-tools')
            existing=target/'bin/sdkmanager.bat';self.assertEqual(existing.read_text(),'original')
            existing.write_text('local edit')
            with self.assertRaises(ValueError):extract(archive,target,'cmdline-tools')
            self.assertEqual(existing.read_text(),'local edit')


if __name__=='__main__':unittest.main()
