#!/bin/sh
# C-12: build a deterministic anonymous ZIP from tracked artifact/testbed files.
set -eu
if [ "$#" -ne 1 ]; then
  echo 'Usage: sh team/make_bundle.sh OUTPUT.zip' >&2
  exit 2
fi
case "$1" in
  *.zip) ;;
  *) echo 'output must end in .zip' >&2; exit 2 ;;
esac
if [ -e "$1" ]; then
  echo 'output already exists' >&2
  exit 2
fi
repo=$(git rev-parse --show-toplevel)
script="$repo/team/scrub_check.sh"
output=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
python3 - "$repo" "$script" "$output" <<'PY'
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

repo, scrub, output = map(Path, sys.argv[1:])
excluded_prefixes = ('artifact/runs/', 'testbed/runs/')
excluded_parts = {'runtime', 'tmp', 'codex', 'team', '.git'}
excluded_names = {'review.md', 'resolve.md', '.env', 'README.vi.md', 'RUNBOOK_B.md'}
tracked = subprocess.check_output(
    ['git', '-C', str(repo), 'ls-files', '-z', 'artifact', 'testbed', 'manuscript']
).decode().split('\0')
selected = []
for name in tracked:
    if not name or name.startswith(excluded_prefixes):
        continue
    path = Path(name)
    if excluded_parts.intersection(path.parts) or path.name in excluded_names:
        continue
    if path.name.endswith('.local.json'):
        continue
    source = repo / path
    if source.is_file():
        selected.append((name, source))

with tempfile.TemporaryDirectory(prefix='ghosteffect-bundle-') as temporary:
    stage = Path(temporary) / 'ghosteffect-artifact'
    records = []
    for name, source in sorted(selected):
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        records.append({'path': name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    readme = stage / 'README.md'
    readme.write_text(
        '# GhostEffect anonymous artifact\n\n'
        'Reproduce on Linux/WSL with Python 3.12: '
        '`python3 artifact/run_all.py --output-dir /absolute/path/to/fresh-run --jobs 2`.\n\n'
        'Simulation outputs are seeded. `results/ledger_bench.csv` and floating-point tail values are host-dependent. '
        'Run time depends on the host and selected worker count. '
        'Android experiments require the separately documented emulator, apps, and local test backends.\n',
        encoding='utf-8')
    manifest = {
        'source_commit': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(),
        'included_tracked_files': len(records),
        'excluded': ['artifact/runs/', 'testbed/runs/', 'runtime/', 'tmp/', 'codex/', 'team/',
                     'review.md', 'resolve.md', '.git/', '*.local.json', '.env', 'README.vi.md', 'RUNBOOK_B.md'],
        'files': records,
    }
    (stage / 'BUNDLE-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    check = subprocess.run(['sh', str(scrub), str(stage)], text=True)
    if check.returncode:
        raise SystemExit(check.returncode)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(stage.rglob('*')):
            if not source.is_file():
                continue
            relative = source.relative_to(stage.parent).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
print(output)
PY
