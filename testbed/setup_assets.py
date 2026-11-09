"""Fetch explicit locked assets into this project, verifying known SHA256.

No model downloads or APK installation. A missing/mismatching release FAILS;
there is no latest-version fallback. Signature checks still precede installation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(asset, directory):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / asset['file']
    if target.exists():
        if sha(target) != asset['sha256']:
            raise ValueError('existing asset hash mismatch: ' + target.name)
        return dict(file=target.name, sha256=asset['sha256'], status='EXISTING_VERIFIED')
    errors = []
    temporary = target.with_suffix(target.suffix + '.part')
    for url in asset['urls']:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'GhostEffect-reconstruction/1.0'})
            with urllib.request.urlopen(req, timeout=45) as source, temporary.open('wb') as out:
                while data := source.read(1024 * 1024):
                    out.write(data)
            actual = sha(temporary)
            if actual != asset['sha256']:
                raise ValueError('download SHA256 does not match the selected lock')
            temporary.replace(target)
            receipt = dict(file=target.name, source_url=url, retrieved_utc_ns=time.time_ns(),
                           version=asset['version'], sha256=actual, bytes=target.stat().st_size,
                           license=asset['license'], signature_verified=False,
                           purpose='isolated Android replication; no personal accounts', status='DOWNLOADED_VERIFIED')
            (directory / (target.name + '.receipt.json')).write_text(json.dumps(receipt, indent=2), encoding='utf-8')
            return receipt
        except (OSError, ValueError) as exc:
            errors.append(dict(url=url, error_type=type(exc).__name__, reason=str(exc)))
            if temporary.exists():
                temporary.unlink()  # this downloader's exact, project-local temporary file
    raise RuntimeError(json.dumps(dict(file=asset['file'], status='UNAVAILABLE', attempts=errors)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock',type=Path,default=Path(__file__).parent/'assets.lock.json',
                        help='historical lock by default; choose assets-windows.lock.json explicitly for the port')
    parser.add_argument('--only', nargs='+', required=True, help='explicit filenames from assets.lock.json')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    lock = json.loads(args.lock.read_text(encoding='utf-8'))
    assets = {a['file']: a for a in lock['assets']}
    if set(args.only) - set(assets):
        parser.error('unknown asset filename')
    receipts = [download(assets[name], root / 'runtime' / 'assets') for name in args.only]
    print(json.dumps(receipts, indent=2))


if __name__ == '__main__':
    main()
