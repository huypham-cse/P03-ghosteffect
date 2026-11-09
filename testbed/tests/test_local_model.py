"""Local inference wire-contract fixtures, not real model quality measurements."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from local_model import LocalModel,TextOnlyModel


class Response(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*args):self.close()


def completion(model='Qwen/Qwen2.5-VL-7B-Instruct',finish='stop'):
    return dict(model=model,choices=[dict(finish_reason=finish,message=dict(content='Reason: test\nAction: {}'))],usage=dict(total_tokens=100))


class LocalModelTests(unittest.TestCase):
    def test_m3a_all_images_and_prompt_are_preserved_and_t3a_is_text_only(self):
        payloads=[]
        def send(request,timeout):
            payloads.append(json.loads(request.data));return Response(json.dumps(completion()).encode())
        prompt='upstream reflection/history unchanged';png=b'\x89PNG\r\n\x1a\nSYNTHETIC_WIRE_FIXTURE'
        with patch('local_model.urllib.request.urlopen',side_effect=send):
            model=LocalModel('http://127.0.0.1:8000/v1','Qwen/Qwen2.5-VL-7B-Instruct')
            text,safe,raw=model.predict_mm(prompt,[png,png,png])
            self.assertIsNone(safe)
            self.assertEqual(payloads[0]['messages'][0]['content'][0]['text'],prompt)
            self.assertEqual(len(payloads[0]['messages'][0]['content']),4)
            text_model=TextOnlyModel('http://127.0.0.1:8000/v1',model.model_id)
            text_model.predict(prompt)
            self.assertEqual(len(payloads[1]['messages'][0]['content']),1)
            with self.assertRaises(ValueError):text_model.predict_mm(prompt,[png])

    def test_external_fallback_wrong_model_truncation_and_transport_errors_propagate(self):
        with self.assertRaises(ValueError):LocalModel('https://external.invalid/v1','model')
        model=LocalModel('http://127.0.0.1:8000/v1','Qwen/Qwen2.5-VL-7B-Instruct')
        for raw in [completion(model='wrong'),completion(finish='length')]:
            with patch('local_model.urllib.request.urlopen',return_value=Response(json.dumps(raw).encode())):
                with self.assertRaises((ValueError,RuntimeError)):model.predict('test')
        with patch('local_model.urllib.request.urlopen',side_effect=TimeoutError) as request:
            with self.assertRaises(TimeoutError):model.predict('test')
            self.assertEqual(request.call_count,1)


if __name__=='__main__':unittest.main()
