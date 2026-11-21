"""TN1 label cost: wall time of each scripted calibration label trial (reset, compose, fault, relaunch, both reads,
grading), from the trial's clock.json start to its completion line in batch.log. Writes
artifact/results/real/tn1_caldav/label_cost.csv in the schema of results/real/agent/label_cost.csv.

batch.log stamps local time (UTC+7, the collection host) without a date; the date comes from clock.json."""
import csv
import datetime as dt
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'testbed/runs/tn1-calibration'
OUT = ROOT / 'artifact/results/real/tn1_caldav'
TZ = dt.timezone(dt.timedelta(hours=7))


def durations():
    cal = [json.loads(l) for l in (OUT / 'calibration_effects.jsonl').read_text(encoding='utf-8').splitlines()]
    done = {}
    for line in (RUN / 'batch.log').read_text(encoding='utf-8').splitlines():
        m = re.match(r'(\d\d):(\d\d):(\d\d) (c\d{4}) ok ', line)
        if m:
            done[m.group(4)] = tuple(map(int, m.group(1, 2, 3)))
    out = []
    for r in cal:
        name = r['evidence']['clock']['path'].split('/')[0]
        start = dt.datetime.fromtimestamp(json.loads((RUN / name / 'clock.json').read_text())['start_utc_ns'] / 1e9, TZ)
        h, mi, s = done[name]
        end = start.replace(hour=h, minute=mi, second=s, microsecond=0)
        if end < start:
            end += dt.timedelta(days=1)
        secs = (end - start).total_seconds()
        assert 0 < secs < 600, (name, secs)
        out.append((r['X_backend'], secs))
    return out


def main():
    d = durations()
    rows = []
    for comp, sel in (('committed', 1), ('absent', 0), ('total', None)):
        v = [s for x, s in d if sel is None or x == sel]
        rows.append(dict(component=comp, n=len(v), min_s=f'{min(v):.1f}', median_s=f'{statistics.median(v):.1f}',
                         max_s=f'{max(v):.1f}'))
    with open(OUT / 'label_cost.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == '__main__':
    sys.exit(main())
