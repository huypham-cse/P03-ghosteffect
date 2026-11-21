"""TN1 rig hygiene (b-log 20/11): reset DAVx5's sync-worker backoff between trials (AVD only, root).

Every committed-effect trial of the app-kill and force-stop classes kills DAVx5 while its OneTimeSyncWorker uploads,
and WorkManager raises that worker's run_attempt_count (exponential backoff from 30 s). After a few such trials in a row
the next upload waits longer than the trial's 90 s barrier, and the count keeps rising until uploads stop for an hour
(20/11 03:28: count 8). This helper, run beside the collector, waits for each new line in batch.log (a trial ended; the
next one saves its event at least 5 s later) and then: force-stops DAVx5 (already dead after a kill-class trial), and
in one sqlite3 session sets run_attempt_count = 0 and last_enqueue_time = now for the ENQUEUED OneTimeSyncWorker. sqlite
checkpoints and removes its -wal and -shm on close, so the database file keeps DAVx5's owner and SELinux label (checked
20/11 03:31). It only changes when DAVx5 next uploads; no event, Etar state or label is touched.
"""
import argparse
import subprocess
import time
from pathlib import Path

DB = '/data/data/at.bitfire.davdroid/no_backup/androidx.work.workdb'
SQL = ("update WorkSpec set run_attempt_count=0, last_enqueue_time=strftime('%s','now')*1000-1000 "
       "where state=0 and run_attempt_count>=1 and worker_class_name like '%OneTimeSyncWorker'; select changes();")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', default='emulator-5580')
    a = p.parse_args()
    adb = [a.adb, '-P', '5038', '-s', a.serial, 'shell']
    batch = a.run / 'batch.log'
    seen = len(batch.read_text(encoding='utf-8').splitlines()) if batch.exists() else 0
    with open(a.run / 'worker_reset.log', 'a', encoding='utf-8') as log:
        while True:
            n = len(batch.read_text(encoding='utf-8').splitlines()) if batch.exists() else 0
            if n > seen:
                seen = n
                try:
                    subprocess.run(adb + ['am force-stop at.bitfire.davdroid'], capture_output=True, timeout=20)
                    out = subprocess.run(adb + ['sqlite3 %s "%s"' % (DB, SQL)], capture_output=True, text=True,
                                         encoding='utf-8', errors='replace', timeout=20)
                    log.write('%s after line %d: reset %s %s\n' % (time.strftime('%H:%M:%S'), n, out.stdout.strip(),
                                                                  out.stderr.strip()[:80]))
                except Exception as exc:   # logged, retried after the next trial
                    log.write('%s after line %d: error %s\n' % (time.strftime('%H:%M:%S'), n, type(exc).__name__))
                log.flush()
            time.sleep(.3)


if __name__ == '__main__':
    main()
