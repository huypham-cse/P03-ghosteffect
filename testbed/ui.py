"""ADB capture and conservative GUI-only reader for a NEW replication stratum.

No server, database, logcat, proxy receipt or true-outcome input is accepted.
Resource IDs/account anchors must be frozen from actual pinned-app dev screens.
An unfrozen/missing profile produces BOT, never a guessed absence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET


def digest(data):
    return hashlib.sha256(data).hexdigest()


def focused_window(display_dump,input_dump):
    """Match the live display's app window to the actual input recipient.

    API33 can expose an app tree/currentFocus underneath a system ANR modal.
    This check rejects that mismatch; it does not certify arbitrary overlays.
    Only the single default display used by our screenshot path is supported.
    """
    # Native Windows adb emits CRLF; text files/tests often normalize to LF.
    # Normalize here so the same live focus is not rejected on Windows.
    input_dump='\n'.join(input_dump.splitlines())+'\n'
    lines=[x for x in display_dump.splitlines() if re.match(r'\s*mCurrentFocus=',x)]
    line=lines[0] if len(lines)==1 else ''
    match=re.search(r'Window\{([0-9a-f]+)\s+u(\d+)\s+([A-Za-z0-9_.]+/[A-Za-z0-9_.$]+)\}',line)
    if not match:raise RuntimeError('focused application window cannot be verified')
    if (not re.search(r'^\s*DispatchEnabled:\s*true\s*$',input_dump,re.M)
            or not re.search(r'^\s*DispatchFrozen:\s*false\s*$',input_dump,re.M)
            or not re.search(r'^\s*FocusedDisplayId:\s*0\s*$',input_dump,re.M)):
        raise RuntimeError('default-display input dispatch is not ready')
    section=re.search(r'^\s*FocusedWindows:[ \t]*\n(.*?)(?=^\s*FocusRequests:)',input_dump,re.M|re.S)
    recipients=re.findall(r"displayId=(\d+), name='([^'\n]+)'",section[1]) if section else []
    token,user,component=match.groups()
    if recipients!=[('0',token+' '+component)]:
        raise RuntimeError('input focus differs from the observed application window')
    return dict(component=component,token=token,user=int(user),display_id=0)


class ADB:
    def __init__(self, executable, serial):
        if not re.fullmatch(r'emulator-\d+', serial):
            raise ValueError('this reconstruction runner only targets explicit AVD serials')
        self.executable, self.serial = str(executable), serial

    def run(self, *args, timeout=40, check=True):
        result = subprocess.run([self.executable, '-s', self.serial, *map(str, args)],
                                capture_output=True, timeout=timeout, check=check)
        return result.stdout

    def shell(self, *args):
        # adb shell invokes a device shell. All command arguments in this module
        # are fixed or validated; never interpolate arbitrary user effect text.
        return self.run('shell', *args).decode('utf-8', errors='strict').strip()

    def foreground_window(self, diagnostics=None):
        # API33 `windows` can omit focus, whereas an unrestricted dump can
        # prepend stale focus from "Last ANR" (observed on the real local AVD).
        # The displays section contains current focus. Multiple display foci
        # are unsupported: do not guess which one corresponds to our capture.
        display=self.shell('dumpsys','window','displays')
        inputs=self.shell('dumpsys','input')
        if diagnostics is not None:
            directory=Path(diagnostics);directory.mkdir(parents=True,exist_ok=False)
            (directory/'window-displays.txt').write_text(display,encoding='utf-8')
            (directory/'input.txt').write_text(inputs,encoding='utf-8')
        return focused_window(display,inputs)

    def foreground(self):
        return self.foreground_window()['component']

    def tree(self, diagnostics=None):
        """One dump only; retain malformed output rather than repairing/retrying it."""
        directory = Path(diagnostics) if diagnostics is not None else None
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=False)
        target = '/sdcard/window-' + uuid.uuid4().hex + '.xml'
        failed = False
        try:
            dumped = self.run('shell', 'uiautomator', 'dump', '--compressed', target)
            if directory is not None:
                (directory / 'dump-output.bin').write_bytes(dumped)
            data = self.run('exec-out', 'cat', target)
            if directory is not None:
                (directory / 'tree.raw.xml').write_bytes(data)
            # Keep raw bytes unchanged. Empty/error text or another XML document
            # is not a GUI tree, even when adb itself returned exit code zero.
            root = ET.fromstring(data)
            if root.tag != 'hierarchy':
                raise ValueError('uiautomator output is not a hierarchy')
            return data
        except BaseException as exc:
            failed = True
            if directory is not None and isinstance(exc, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
                for name, value in (('stdout', exc.stdout), ('stderr', exc.stderr)):
                    if value is not None:
                        (directory / ('command-error-' + name + '.bin')).write_bytes(
                            value.encode('utf-8') if isinstance(value, str) else value)
            raise
        finally:
            try:
                self.shell('rm', '-f', target)
            except Exception as exc:
                if directory is not None:
                    (directory / 'cleanup-error.json').write_text(json.dumps(dict(
                        error_type=type(exc).__name__, reason=str(exc))), encoding='utf-8')
                # A cleanup failure must not hide the original capture failure.
                if not failed:
                    raise

    def capture(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=False)
        started = time.monotonic_ns()
        stage = 'window_before'
        try:
            window_before = self.foreground_window(directory / 'window-before')
            before=window_before['component']
            stage = 'first_tree'
            first = self.tree(directory / 'first')
            stage = 'screenshot'
            screenshot = self.run('exec-out', 'screencap', '-p')
            (directory / 'screen.raw.png').write_bytes(screenshot)
            if not screenshot.startswith(b'\x89PNG\r\n\x1a\n'):
                raise RuntimeError('invalid PNG screenshot')
            stage = 'second_tree'
            second = self.tree(directory / 'second')
            stage = 'window_after'
            window_after = self.foreground_window(directory / 'window-after')
        except Exception as exc:
            (directory / 'capture-error.json').write_text(json.dumps(dict(
                status='FAILED', stage=stage, mono_start_ns=started,
                mono_end_ns=time.monotonic_ns(), error_type=type(exc).__name__,
                reason=str(exc), scope='capture failure; not a GUI verdict'), indent=2), encoding='utf-8')
            raise
        after=window_after['component']
        ended = time.monotonic_ns()
        (directory / 'screen.png').write_bytes(screenshot)
        (directory / 'tree.xml').write_bytes(second)
        meta = dict(kind='adb-sequential-bracketed-capture', serial=self.serial,
                    mono_start_ns=started, mono_end_ns=ended, utc_ns=time.time_ns(),
                    foreground_before=before, foreground_after=after,
                    stable_tree=first == second, same_foreground=window_before==window_after,
                    window_before=window_before,window_after=window_after,
                    tree_sha256=digest(second), png_sha256=digest(screenshot))
        (directory / 'capture.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
        return meta

    def tap(self, x, y):
        if not all(isinstance(v, int) and 0 <= v <= 10000 for v in (x, y)):
            raise ValueError('invalid tap coordinates')
        self.shell('input', 'tap', str(x), str(y))

    def force_stop(self, package):
        validate_package(package)
        before = self.pids(package)
        if not before:
            raise RuntimeError('target has no live PID before fault; not an app-death trial')
        self.shell('am', 'force-stop', package)
        after = self.pids(package)
        if after:
            raise RuntimeError('force-stop failed to stop target processes')
        return dict(observed_class='app-force-stop', package=package,
                    pids_before=before.split(), pids_after=after.split())

    def pids(self, package):
        validate_package(package)
        result = subprocess.run([self.executable, '-s', self.serial, 'shell', 'pidof', package],
                                capture_output=True, timeout=20, check=False)
        text = result.stdout.decode().strip()
        if result.returncode not in (0, 1) or result.stderr.strip() or (text and not re.fullmatch(r'\d+(?:\s+\d+)*', text)):
            raise RuntimeError('PID lookup failed; device error is not an app-death receipt')
        if not text and result.returncode == 0:
            raise RuntimeError('invalid empty successful pidof result')
        return text

    def type_ascii_fixture(self, text):
        if not text or not re.fullmatch(r'[A-Za-z0-9 _.,:@+\-]+', text):
            raise ValueError('this driver types only safe ASCII test fixture content')
        self.shell('input', 'text', text.replace(' ', '%s'))

    def launch(self, component):
        if not re.fullmatch(r'[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+', component):
            raise ValueError('explicit package/activity component required')
        self.shell('am', 'start', '-W', '-n', component)
        return dict(recovery_origin_mono_ns=time.monotonic_ns(), foreground=self.foreground())


def validate_package(package):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+', package):
        raise ValueError('invalid Android package')


def select(root, selector):
    if not selector or not isinstance(selector, dict):
        return []
    allowed = {'resource-id', 'text', 'content-desc', 'class', 'package'}
    if set(selector) - allowed:
        raise ValueError('selector has unsupported attributes')
    return [node for node in root.iter('node') if all(node.get(k) == v for k, v in selector.items())]


def read_nonce(xml, capture, profile, nonce, bottom_receipt=None):
    """Return a calibrated-family INPUT, not a backend-commit declaration.

    Explicit positive/outgoing/status selectors prevent drafts/Outbox/failed
    rows from being treated as delivered. An optimistic app can still be wrong;
    such errors belong in real interrupted-effect calibration.
    """
    def bot(reason):
        return dict(verdict='BOT', reason=reason)
    if not profile.get('frozen') or not profile.get('profile_id'):
        return bot('profile_not_frozen_from_actual_dev_screens')
    if not re.fullmatch(r'gx:[0-9ABCDEFGHJKMNPQRSTVWXYZ]{6}', nonce):
        return bot('invalid_nonce')
    if not capture.get('stable_tree') or not capture.get('same_foreground'):
        return bot('unstable_capture')
    age = (capture['mono_end_ns'] - capture['mono_start_ns']) / 1e9
    if age < 0 or age > profile.get('max_capture_seconds', 15):
        return bot('capture_duration_out_of_domain')
    component = capture.get('foreground_after', '')
    if not component.startswith(profile['package'] + '/'):
        return bot('wrong_foreground')
    if profile.get('activity') and component != profile['activity']:
        return bot('wrong_activity')
    if digest(xml) != capture.get('tree_sha256'):
        return bot('capture_hash_mismatch')
    root = ET.fromstring(xml)
    # Fail closed when account/title/previous-message/timeline identity is missing.
    for name in ('account', 'title', 'anchor', 'timeline'):
        if not select(root, profile.get(name)):
            return bot('missing_' + name)
    timelines = select(root, profile['timeline'])
    if len(timelines) != 1:
        return bot('ambiguous_timeline')
    rows = select(timelines[0], profile.get('row'))
    eligible = []
    for row in rows:
        if not select(row, profile.get('outgoing')) or not select(row, profile.get('acknowledged')):
            continue
        if any(select(row, selector) for selector in profile.get('exclude', [])):
            continue
        eligible.append(row)
    # Use the artifact's exact edit-distance predicate, not substring similarity.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'artifact' / 'scripts'))
    from sim_nonce import within_edit_distance
    matches = []
    visible_tokens = 0
    for row in eligible:
        text = ' '.join(n.get('text', '') + ' ' + n.get('content-desc', '') for n in row.iter('node'))
        tokens = re.findall(r'gx:([0-9A-Za-z]{5,7})\b', text)
        visible_tokens += len(tokens)
        if any(within_edit_distance(nonce[3:], token.upper(), 1) for token in tokens):
            matches.append(row)
    if visible_tokens > 40:
        return bot('nonce_token_count_exceeds_analytic_domain')
    if len(matches) > 1:
        return dict(verdict='duplicate_candidate', matches=len(matches), profile_id=profile['profile_id'])
    if matches:
        return dict(verdict='com', matches=1, profile_id=profile['profile_id'],
                    scope='GUI family observation; requires calibration')
    if not bottom_receipt or bottom_receipt.get('tree_sha256') != capture['tree_sha256']:
        return bot('absence_needs_verified_bottom_scroll')
    if bottom_receipt.get('direction') != 'latest' or bottom_receipt.get('unchanged_swipes', 0) < 2:
        return bot('bottom_not_verified')
    return dict(verdict='abs', matches=0, profile_id=profile['profile_id'],
                scope='GUI family observation; not proof of non-commit')


def scroll_latest(adb, profile, directory, max_swipes=12):
    """Profile specifies actual-device swipe geometry/direction from dev screens.

    Two unchanged swipes plus the reader's anchors are conservative evidence of
    reaching the end, not an inference from a single XML attribute.
    """
    swipe = profile.get('latest_swipe')
    if not isinstance(swipe, list) or len(swipe) != 4 or not all(type(v) is int and 0 <= v <= 10000 for v in swipe):
        raise ValueError('freeze a four-coordinate latest-direction swipe from dev screens')
    prior, unchanged = None, 0
    directory = Path(directory)
    for i in range(max_swipes):
        if not adb.foreground().startswith(profile['package'] + '/'):
            raise RuntimeError('foreground changed during navigation')
        adb.shell('input', 'swipe', *map(str, swipe), '400')
        meta = adb.capture(directory / str(i))
        data = (directory / str(i) / 'tree.xml').read_bytes()
        root = ET.fromstring(data)
        timelines = select(root, profile.get('timeline'))
        if len(timelines) != 1 or not meta['stable_tree']:
            unchanged, prior = 0, None
            continue
        signature = digest(ET.tostring(timelines[0]))
        unchanged = unchanged + 1 if signature == prior else 0
        prior = signature
        if unchanged >= 2:
            receipt = dict(direction='latest', unchanged_swipes=unchanged,
                           tree_sha256=meta['tree_sha256'], capture_path=str(directory / str(i)))
            (directory / 'bottom.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
            return data, meta, receipt
    raise RuntimeError('bottom could not be verified within navigation limit')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', required=True)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(ADB(args.adb, args.serial).capture(args.output), indent=2))


if __name__ == '__main__':
    main()
