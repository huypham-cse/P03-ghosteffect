#!/bin/sh
# C-10: scan text and filenames without printing matched secrets.
set -eu
if [ "$#" -eq 0 ]; then
  echo 'Usage: sh team/scrub_check.sh FILE_OR_DIRECTORY [...]' >&2
  exit 2
fi
if [ -n "${PYTHON:-}" ]; then
  interpreter=$PYTHON
elif command -v python3 >/dev/null 2>&1; then
  interpreter=python3
else
  interpreter=python
fi
exec "$interpreter" - "$@" <<'PY'
import re
import sys
from pathlib import Path
import unicodedata


def folded(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn').casefold()


patterns = [
    ('local-user-path', re.compile(r'/Users/|(?<![A-Za-z0-9])[A-Z]:[\\/](?!Program Files[\\/])', re.I)),
    ('api-key', re.compile(r'\b(?:sk-|AIza|hf_)[A-Za-z0-9_-]{16,}')),
    ('github-token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})')),
    ('private-key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('team-account', re.compile(r'nguyennguyen938-debug', re.I)),
    ('email', re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)),
]
names = re.compile(r'\b(?:gia huy|trung nguyen|ba nguyen)\b')
excluded = {'.git', '__pycache__'}
forbidden_dirs = {'runtime', 'tmp', 'codex', 'team', 'runs'}
failed = False
seen = set()


def report(label, line, rule):
    global failed
    # Deliberately omit the line contents, match and absolute host path.
    print(f'{label}:{line}: {rule}')
    failed = True


def scan(path, label):
    if path.is_symlink():
        report(label, 0, 'symlink-needs-review')
        return
    if path.is_dir():
        for child in sorted(path.iterdir()):
            child_label = label + '/' + child.name
            if child.name in forbidden_dirs or child.name == '.git':
                report(child_label, 0, 'internal-directory')
            if child.name not in excluded:
                scan(child, child_label)
        return
    resolved = path.resolve()
    if resolved in seen:
        return
    seen.add(resolved)
    if (path.name == '.env' or path.name.endswith(('.local.json', '.secrets.env', '.signing.key'))
            or path.name in {'review.md', 'resolve.md'}):
        report(label, 0, 'forbidden-file')
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        content = raw.decode('utf-16')
    elif b'\x00' in raw[:8192]:
        # PDF, archives and images need format-specific inspection separately.
        return
    else:
        content = raw.decode('utf-8-sig', errors='replace')
    for number, line in enumerate(content.splitlines(), 1):
        for rule, pattern in patterns:
            if pattern.search(line):
                report(label, number, rule)
        if names.search(folded(line)):
            report(label, number, 'team-name')


try:
    for argument in sys.argv[1:]:
        target = Path(argument)
        if not target.exists():
            raise FileNotFoundError(target.name)
        scan(target, target.name)
except (OSError, UnicodeError) as exc:
    print('scrub check could not read an input: ' + type(exc).__name__, file=sys.stderr)
    sys.exit(2)
print('scrub check: ' + ('FAIL' if failed else 'PASS') + ' (text/filesystem scan; inspect PDF metadata separately)')
sys.exit(1 if failed else 0)
PY
