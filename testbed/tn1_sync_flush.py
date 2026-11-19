"""TN1 rig hygiene (b-log 19/11): run DAVx5's pending upload jobs at once instead of after a delay or a backoff.

On the AVD the sync manager starts an upload about 55 s after the save, and every committed-effect trial of the
app-kill and force-stop classes kills DAVx5 in the middle of its upload, after which the sync manager and WorkManager
back off further. DAVx5's next upload then missed the trial's 90 s barrier more and more often (c0121, c0143, c0160,
c0164, c0171). This helper, run beside the collector, polls DAVx5's scheduled jobs every second and force-runs
(`cmd jobscheduler run -f`) each account sync job (uid 1000) and each WorkManager job whose minimum latency is under
10 min, once per job id. Jobs with a longer latency (periodic and maintenance work) are left alone.
It only moves when DAVx5 uploads. The interruption point (after the server commit, before the reply) is the same, no
event or Etar state is touched, caldav_planner.py is unchanged, and hop-1 reads are Etar's local store.
"""
import argparse
import re
import subprocess
import time
from pathlib import Path


def latency_seconds(block):
    m = re.search(r'Minimum latency: \+(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', block)
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', default='emulator-5580')
    a = p.parse_args()
    adb = [a.adb, '-P', '5038', '-s', a.serial, 'shell']
    forced = set()
    with open(a.run / 'sync_flush.log', 'a', encoding='utf-8') as log:
        while True:
            try:
                dump = subprocess.run(adb + ['dumpsys jobscheduler at.bitfire.davdroid'], capture_output=True,
                                      text=True, encoding='utf-8', errors='replace', timeout=30).stdout
                section = dump.split('Pending queue')[0]
                for block in re.split(r'\n(?=  JOB #)', section)[1:]:
                    m = re.match(r'  JOB #(\w+)/(\d+): ', block)
                    if not m or (m.group(1), m.group(2)) in forced:
                        continue
                    uid, job = m.groups()
                    if uid != '1000' and latency_seconds(block) >= 600:
                        continue
                    package = 'android' if uid == '1000' else 'at.bitfire.davdroid'
                    out = subprocess.run(adb + ['cmd jobscheduler run -f %s %s' % (package, job)], capture_output=True,
                                         text=True, encoding='utf-8', errors='replace', timeout=30).stdout.strip()
                    forced.add((uid, job))
                    log.write('%s forced %s/%s (latency %ss): %s\n' % (time.strftime('%H:%M:%S'), package, job,
                                                                      latency_seconds(block), out[:40]))
                    log.flush()
            except Exception as exc:   # a failed poll is logged and retried, never fatal
                log.write('%s poll error %s\n' % (time.strftime('%H:%M:%S'), type(exc).__name__))
                log.flush()
            time.sleep(1)


if __name__ == '__main__':
    main()
