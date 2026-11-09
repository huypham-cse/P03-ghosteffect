"""Pinned snapshot integrity checks; no model download, GPU or inference."""
import hashlib
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from setup_models import inventory,project_path,relative_name,verify_file


class ModelSetupTests(unittest.TestCase):
    def test_pinned_metadata_rejects_wrong_revision_or_incomplete_processor(self):
        model=dict(revision='a'*40)
        files=[SimpleNamespace(rfilename=name,size=3,blob_id='x',lfs=None) for name in
               ('config.json','tokenizer_config.json','preprocessor_config.json','model.safetensors')]
        info=SimpleNamespace(sha='a'*40,siblings=files)
        self.assertEqual(len(inventory(info,model)),4)
        info.sha='b'*40
        with self.assertRaises(ValueError):inventory(info,model)
        info.sha='a'*40;info.siblings=[f for f in files if f.rfilename!='preprocessor_config.json']
        with self.assertRaises(ValueError):inventory(info,model)

    def test_hub_paths_and_local_directories_cannot_escape_the_project(self):
        for name in ('../escape','/absolute','weights\\evil','C:drive'):
            with self.assertRaises(ValueError):relative_name(name)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve()
            self.assertEqual(project_path('runtime/models',root),root/'runtime/models')
            with self.assertRaises(ValueError):project_path('../outside',root)
            with self.assertRaises(ValueError):project_path('.',root)

    def test_lfs_and_git_blob_checks_detect_silent_same_size_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'tiny.bin';data=b'actual fixture bytes';path.write_bytes(data)
            record=dict(file=path.name,bytes=len(data),lfs_sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=None)
            self.assertEqual(verify_file(path,record)['sha256'],record['lfs_sha256'])
            path.write_bytes(b'X'+data[1:])
            with self.assertRaises(ValueError):verify_file(path,record)
            path.write_bytes(data)
            record.update(lfs_sha256=None,git_blob_sha1=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
            verify_file(path,record)
            path.write_bytes(b'X'+data[1:])
            with self.assertRaises(ValueError):verify_file(path,record)


if __name__=='__main__':unittest.main()
