"""First retrieval from the exact URL in installed android-env1.2.3 source."""
import hashlib,json,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[2]
url='https://storage.googleapis.com/android_env-tasks/2024.05.13-accessibility_forwarder.apk'
target=root/'runtime/assets/2024.05.13-accessibility_forwarder.apk'
if target.exists():raise RuntimeError('existing asset kept; inspect rather than overwrite')
with urllib.request.urlopen(url,timeout=60) as reply:
 data=reply.read()
 metadata=dict(url=reply.url,status=reply.status,etag=reply.headers.get('ETag'),
               last_modified=reply.headers.get('Last-Modified'))
if not data.startswith(b'PK'):raise RuntimeError('not an APK/ZIP payload')
target.write_bytes(data)
receipt=dict(file=target.name,source=metadata,retrieved_utc_ns=time.time_ns(),
             sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
             provenance='first retrieval from the URL embedded in installed android-env1.2.3; not historical paper hash',
             upstream_source_sha256=hashlib.sha256((root/'runtime/agent-venv/Lib/site-packages/android_env/wrappers/a11y_grpc_wrapper.py').read_bytes()).hexdigest(),
             signature_verified=False)
target.with_suffix('.apk.receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt))
