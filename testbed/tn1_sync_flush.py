"""TN1 rig hygiene (b-log 19/11): flush DAVx5's job backoff between trials.

Each committed-effect trial of the app-kill and force-stop classes kills DAVx5 in the middle of its upload, and the
sync manager and WorkManager back off further after every killed sync. On the AVD this pushed DAVx5's next upload
past the trial's 90 s barrier more and more often (barrier timeouts after 22, 17 and 4 trials). This helper, run beside
the collector, waits for each new line in batch.log (one trial just ended) and force-runs every scheduled DAVx5 job
(`cmd jobscheduler run -f`), so the next trial starts without an accumulated backoff. It acts before the next trial
arms the proxy and saves its event, touches no event and no Etar state, and does not change caldav_planner.py.
Hop-1 reads are Etar's local store and do not depend on when DAVx5 uploads.
"""
import argparse
import re
import subprocess
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', default='emulator-5580')
    a = p.parse_args()
    adb = [a.adb, '-P', '5038', '-s', a.serial, 'shell']
    batch = a.run / 'batch.log'
    seen = len(batch.read_text(encoding='utf-8').splitlines()) if batch.exists() else 0
    with open(a.run / 'sync_flush.log', 'a', encoding='utf-8') as log:
        while True:
            n = len(batch.read_text(encoding='utf-8').splitlines()) if batch.exists() else 0
            if n > seen:
                seen = n
                jobs = subprocess.run(adb + ['dumpsys jobscheduler at.bitfire.davdroid'], capture_output=True,
                                      text=True, encoding='utf-8', errors='replace', timeout=30).stdout
                ran = []
                for uid, job in sorted(set(re.findall(r'JOB #(\w+)/(\d+): [0-9a-f]+ ', jobs))):
                    package = 'android' if uid == '1000' else 'at.bitfire.davdroid'
                    out = subprocess.run(adb + ['cmd jobscheduler run -f %s %s' % (package, job)], capture_output=True,
                                         text=True, encoding='utf-8', errors='replace', timeout=30).stdout.strip()
                    ran.append('%s/%s:%s' % (package, job, out.split('\n')[0][:40]))
                log.write(time.strftime('%H:%M:%S') + ' after line %d: %s\n' % (n, '; '.join(ran) or 'no jobs'))
                log.flush()
            time.sleep(.5)


if __name__ == '__main__':
    main()
