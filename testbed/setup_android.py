"""Project-local Windows Android SDK bootstrap, with publisher checksums.

Downloads exact packages from Google's repository metadata, not an unpinned
latest fallback. Does not modify Windows hypervisor features or system PATH.
Historical emulator version is retained; Windows/x86_64 remains a new stratum.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import shutil
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

# platform-tools 37.0.2 is still listed by Google but its archive returns 404 (checked 09/11/2026);
# 37.0.1 is the nearest exact release with a publisher checksum.
PINS={'emulator':'37.2.13','platform-tools':'37.0.1','cmdline-tools;19.0':'19.0.0'}


def hash_file(path,algorithm='sha256'):
    with path.open('rb') as stream:return hashlib.file_digest(stream,algorithm).hexdigest()


def archive_info(data,package,revision):
    tree=ET.fromstring(data)
    matches=[]
    for node in tree.findall('remotePackage'):
        rev=node.find('revision')
        value='.'.join(rev.findtext(n,'0') for n in ('major','minor','micro'))
        if node.get('path')!=package or value!=revision:continue
        for archive in node.findall('archives/archive'):
            if archive.findtext('host-os') not in (None,'windows'):continue
            complete=archive.find('complete');checksum=complete.find('checksum')
            matches.append(dict(package=package,revision=revision,url=complete.findtext('url'),
                                bytes=int(complete.findtext('size')),checksum=checksum.text,
                                checksum_type=checksum.get('type')))
    if len(matches)!=1:raise ValueError('exact pinned Windows package unavailable: '+package+'/'+revision)
    return matches[0]


def download(info,folder):
    name=info['url']
    if '/' in name or '\\' in name or not name.endswith('.zip'):raise ValueError('unexpected SDK archive URL')
    target=folder/name
    if not target.exists():
        temporary=target.with_suffix('.zip.part')
        with urllib.request.urlopen('https://dl.google.com/android/repository/'+name,timeout=60) as source,temporary.open('wb') as stream:
            while block:=source.read(1024*1024):stream.write(block)
        if temporary.stat().st_size!=info['bytes'] or hash_file(temporary,info['checksum_type'])!=info['checksum']:
            raise ValueError('publisher checksum/size mismatch: '+name)
        temporary.replace(target)
    if target.stat().st_size!=info['bytes'] or hash_file(target,info['checksum_type'])!=info['checksum']:
        raise ValueError('cached SDK checksum mismatch: '+name)
    return target


def extract(archive,target,strip_root=None):
    target=target.resolve();target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        bad=zipped.testzip()
        if bad:raise ValueError('bad SDK zip member: '+bad)
        for item in zipped.infolist():
            path=PurePosixPath(item.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in item.filename:
                raise ValueError('unsafe SDK archive member')
            parts=path.parts
            if strip_root:
                if not parts or parts[0]!=strip_root:raise ValueError('unexpected SDK root')
                parts=parts[1:]
            if not parts:continue
            destination=target.joinpath(*parts).resolve()
            if target not in destination.parents:raise ValueError('SDK member escaped project destination')
            if item.is_dir():destination.mkdir(parents=True,exist_ok=True);continue
            destination.parent.mkdir(parents=True,exist_ok=True)
            # Never overwrite an existing edited/installed file during resume.
            data=zipped.read(item)
            if destination.exists() and destination.read_bytes()!=data:
                raise ValueError('existing SDK member differs: '+str(destination))
            if not destination.exists():destination.write_bytes(data)


def register_generic(sdk,package,revision):
    """Let sdkmanager see manually checksum-verified generic packages.

    This is local installation metadata, not a publisher signature or receipt.
    Registration avoids an image dependency silently fetching another emulator.
    """
    target=sdk.joinpath(*package.split(';'))/'package.xml'
    if target.exists():return
    common='http://schemas.android.com/repository/android/common/02'
    generic='http://schemas.android.com/repository/android/generic/02'
    xsi='http://www.w3.org/2001/XMLSchema-instance'
    root=ET.Element('repository',{'xmlns':common,'xmlns:g':generic,'xmlns:xsi':xsi})
    local=ET.SubElement(root,'localPackage',{'path':package,'obsolete':'false','xmlns':''})
    ET.SubElement(local,'type-details',{'xsi:type':'g:genericDetailsType'})
    rev=ET.SubElement(local,'revision')
    for name,value in zip(('major','minor','micro'),revision.split('.')):ET.SubElement(rev,name).text=value
    ET.SubElement(local,'display-name').text=package+' '+revision
    target.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bootstrap',action='store_true',required=True)
    args=parser.parse_args()
    if os.name!='nt':parser.error('this bootstrap is for the current Windows host; server setup remains Linux runbook')
    root=Path(__file__).resolve().parents[1];folder=root/'runtime/android-downloads';sdk=root/'runtime/android-sdk'
    folder.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(root).free<3*1024**3:raise RuntimeError('less than 3GiB free for SDK bootstrap')
    metadata=folder/'repository2-3.xml'
    if not metadata.exists():
        with urllib.request.urlopen('https://dl.google.com/android/repository/repository2-3.xml',timeout=60) as source:metadata.write_bytes(source.read())
    result=dict(status='RUNNING',kind='new Windows Android replication toolchain',
                historical_emulator_version='37.2.13',project_root=str(root),sdk_root=str(sdk),
                repository_url='https://dl.google.com/android/repository/repository2-3.xml',
                repository_sha256=hash_file(metadata),packages=[],started_utc_ns=time.time_ns())
    manifest=folder/'BOOTSTRAP.json'
    try:
        for package,revision in PINS.items():
            info=archive_info(metadata.read_bytes(),package,revision)
            print('DOWNLOAD/VERIFY',package,revision,flush=True)
            archive=download(info,folder)
            target=sdk/'cmdline-tools'/'19.0' if package.startswith('cmdline-tools;') else sdk
            extract(archive,target,'cmdline-tools' if package.startswith('cmdline-tools;') else None)
            register_generic(sdk,package,revision)
            result['packages'].append(dict(**info,sha256=hash_file(archive)))
            manifest.write_text(json.dumps(result,indent=2))
        check=subprocess.run([str(sdk/'emulator/emulator.exe'),'-accel-check'],capture_output=True,text=True,timeout=30)
        result.update(status='BOOTSTRAPPED',accel_check_exit=check.returncode,
                      accel_check_stdout=check.stdout,accel_check_stderr=check.stderr,
                      next='verify SDK licenses; install API33 image/build-tools; create isolated AVD; record new ABI stratum')
    except Exception as exc:
        result.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc));raise
    finally:
        manifest.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
