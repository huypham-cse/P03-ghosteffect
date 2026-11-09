"""Small declarative GUI driver; actual per-app selectors come from dev captures.

Scripted study mechanics only, not a replacement M3A/UI-TARS baseline. No DB,
backend, proxy or model access. In a certified family each view is read once;
poll_history below is specifically for visibility characterization, not voting.
"""
import json
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET

from ui import select, read_nonce, scroll_latest


def navigate(adb, profile, actions, fixture_text=None):
    if not profile.get('frozen'):
        raise ValueError('actual app profile must be frozen before scripted navigation')
    for action in actions:
        if not adb.foreground().startswith(profile['package'] + '/'):
            raise RuntimeError('foreground changed during scripted navigation')
        kind = action['action']
        if kind == 'tap':
            matches = select(ET.fromstring(adb.tree()), action.get('selector'))
            if len(matches) != 1:
                raise RuntimeError('GUI selector is missing or ambiguous')
            bounds = re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', matches[0].get('bounds', ''))
            if not bounds:
                raise RuntimeError('GUI node has no verified bounds')
            x0, y0, x1, y1 = map(int, bounds.groups())
            adb.tap((x0+x1)//2, (y0+y1)//2)
        elif kind == 'type_fixture':
            if fixture_text is None:
                raise ValueError('fixture text required')
            adb.type_ascii_fixture(fixture_text)
        elif kind == 'back':
            adb.shell('input', 'keyevent', 'KEYCODE_BACK')
        elif kind == 'wait':
            seconds = float(action['seconds'])
            if not 0 <= seconds <= 10:
                raise ValueError('navigation wait must be between 0 and 10 seconds')
            time.sleep(seconds)
        else:
            raise ValueError('unsupported GUI action: ' + kind)


def poll_history(adb, profile, nonce, output, recovery_origin_ns, horizon=300, after_seen=20, interval=2):
    """Visibility interval (last verified abs, first GUI com], preserving BOT.

    This records GUI observations, not true outcome. Server grader must be
    joined separately to identify optimistic rows and committed-never-visible.
    """
    if not 0 < horizon <= 300 or not 0 < after_seen <= 300 or interval <= 0:
        raise ValueError('invalid observation window')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    deadline = recovery_origin_ns / 1e9 + horizon
    first, last_abs, polls = None, None, []
    while time.monotonic() < deadline:
        index = len(polls)
        started = time.monotonic_ns()
        try:
            data, meta, bottom = scroll_latest(adb, profile, output / str(index))
            result = read_nonce(data, meta, profile, nonce, bottom)
            observed_at = meta['mono_end_ns']
        except (RuntimeError, ValueError) as exc:
            result, observed_at = dict(verdict='BOT', reason=str(exc)), time.monotonic_ns()
        row = dict(index=index, mono_start_ns=started, mono_end_ns=observed_at,
                   seconds_since_recovery=(observed_at-recovery_origin_ns)/1e9,
                   within_horizon=observed_at <= recovery_origin_ns + horizon*1e9, **result)
        if row['within_horizon'] and result['verdict'] == 'abs' and first is None:
            last_abs = row['seconds_since_recovery']
        elif row['within_horizon'] and result['verdict'] == 'com' and first is None:
            first = row['seconds_since_recovery']
            deadline = min(deadline, observed_at/1e9 + after_seen)
        polls.append(row)
        with (output / 'polls.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
        time.sleep(min(interval, max(0, deadline-time.monotonic())))
    result = dict(kind='GUI visibility characterization, not calibration votes',
                  recovery_origin_mono_ns=recovery_origin_ns, first_gui_com_seconds=first,
                  last_verified_abs_seconds=last_abs, right_censored=first is None,
                  left_censored=first is not None and last_abs is None, polls=len(polls),
                  backend_truth_used=False)
    (output / 'VISIBILITY.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result
