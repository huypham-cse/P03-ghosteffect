"""Thin local-vLLM binding for the pinned AndroidWorld M3A/T3A interfaces.

Preserves upstream prompt/history and all supplied images at full resolution.
No paid provider, checkpoint substitution, retry, cropping or silent truncation.
One documented output change: Qwen2.5-VL writes the text action as "type", which the pinned
M3A rejects, so the name "type" becomes "input_text" (decided by the team lead on 14/11/2026;
counted per call in the trace and the episode receipt, disclosed in the paper).
This is a backbone binding, not a reimplementation of M3A/T3A agent algorithms.
"""
import base64
import hashlib
import io
import json
import re
import time
from urllib.parse import urlsplit
import urllib.request


TYPE_ACTION = re.compile(r'("action_type"\s*:\s*")type(")')


def alias_action_type(text):
    """("type" -> "input_text") on action JSON only; returns (text, number of replacements)."""
    return TYPE_ACTION.subn(r'\1input_text\2', text)


def png_bytes(image):
    if isinstance(image,bytes):
        if not image.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('expected PNG bytes')
        return image
    # AndroidWorld passes uint8 numpy arrays. Import image dependency lazily so
    # stdlib-only numerical/protocol work does not require an ML environment.
    from PIL import Image
    if str(getattr(image,'dtype',None))!='uint8' or len(image.shape)!=3 or image.shape[2] not in (3,4):
        raise ValueError('expected full-resolution RGB/RGBA uint8 screenshot')
    output=io.BytesIO();Image.fromarray(image).save(output,format='PNG')
    return output.getvalue()


class LocalModel:
    def __init__(self,endpoint,model_id,max_output_tokens=2048,timeout=180,journal=None):
        parsed=urlsplit(endpoint)
        if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost','::1') or parsed.username or parsed.query:
            raise ValueError('use explicit local inference or SSH-forwarded endpoint; no external provider fallback')
        if type(max_output_tokens) is not int or max_output_tokens<1:
            raise ValueError('explicit positive generation budget required')
        self.endpoint=endpoint.rstrip('/');self.model_id=model_id
        self.max_output_tokens,self.timeout,self.journal=max_output_tokens,timeout,journal

    def predict(self,text_prompt):
        return self.predict_mm(text_prompt,[])

    def predict_mm(self,text_prompt,images):
        if not isinstance(text_prompt,str) or not text_prompt:
            raise ValueError('upstream text prompt required')
        content=[dict(type='text',text=text_prompt)]
        image_hashes=[]
        for image in images:
            data=png_bytes(image);image_hashes.append(hashlib.sha256(data).hexdigest())
            content.append(dict(type='image_url',image_url=dict(url='data:image/png;base64,'+base64.b64encode(data).decode())))
        payload=dict(model=self.model_id,messages=[dict(role='user',content=content)],
                     temperature=0,top_p=1,n=1,max_tokens=self.max_output_tokens)
        request=urllib.request.Request(self.endpoint+'/chat/completions',json.dumps(payload).encode(),
                                       {'Content-Type':'application/json'})
        started=time.monotonic()
        # Errors/timeouts/context overflow propagate. Never alter prompt/images
        # or retry a scientific model failure to obtain a favorable completion.
        with urllib.request.urlopen(request,timeout=self.timeout) as response:
            raw=json.load(response)
        if raw.get('model')!=self.model_id:
            raise ValueError('inference response model identity mismatch')
        choices=raw.get('choices')
        if not isinstance(choices,list) or len(choices)!=1:
            raise ValueError('expected exactly one model completion')
        if choices[0].get('finish_reason')!='stop':
            raise RuntimeError('incomplete/truncated/refused model completion')
        text=choices[0].get('message',{}).get('content')
        if not isinstance(text,str) or not text.strip():
            raise ValueError('empty/non-text completion')
        text,aliased=alias_action_type(text)
        raw['action_alias']=aliased
        if self.journal:
            self.journal.emit('LOCAL_INFERENCE',model=self.model_id,
                              prompt_sha256=hashlib.sha256(text_prompt.encode()).hexdigest(),
                              image_sha256=image_hashes,usage=raw.get('usage'),seconds=time.monotonic()-started,
                              finish_reason=choices[0]['finish_reason'],weights_revision_verified=False,
                              action_alias=aliased)
        # Upstream explicitly accepts None for unknown safety-classifier status.
        # A local model without that classifier must not claim safety=True.
        return text,None,raw


class TextOnlyModel(LocalModel):
    """T3A's predict() remains text-only even when shared Qwen supports vision."""
    def predict_mm(self,text_prompt,images):
        if images:raise ValueError('T3A must not receive images')
        return super().predict_mm(text_prompt,[])
