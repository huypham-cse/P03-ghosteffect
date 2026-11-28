"""Schedules for the TN4 transfer check on rented phones (pre-registered in team/b-log.md, 24/11).

The emulator calibration store (testbed/tn4/tn4_store.json) is applied unchanged on a rented Galaxy A36: 30 committed
(x=1) and 30 absent (x=0) effects, fault classes none and force-stop only (kill -9 is refused without root, b-log 18/11
p01), 15 per class and outcome. Each of the four cells is dealt alternately into halves A and B (8/7, so each half is
balanced on its own), and each half is shuffled with a fixed seed; one phone per half, run in parallel. The dev
schedule (P0) has one committed none trial and one absent force-stop trial; it is not counted.

  python testbed/devicefarm/make_transfer_schedules.py
"""
import json
from pathlib import Path
import random

OUT = Path(__file__).resolve().parent
SEED = 20261124


def write(name, trials, max_replacements):
    (OUT / name).write_text(json.dumps(dict(split='transfer', seed=SEED, classes=['none', 'force-stop'],
                                            max_replacements=max_replacements, trials=trials), indent=1) + '\n',
                            encoding='utf-8')
    print(name, len(trials), sum(t['x'] for t in trials), 'committed')


def main():
    rng = random.Random(SEED)
    halves = ([], [])
    for c in ('none', 'force-stop'):
        for x in (1, 0):
            for k in range(15):
                halves[k % 2 if (c, x) in (('none', 1), ('force-stop', 0)) else 1 - k % 2].append(dict(x=x, fault_class=c))
    for half, prefix in zip(halves, 'ab'):
        rng.shuffle(half)
        for i, item in enumerate(half):
            item.update(name='x%s%03d' % (prefix, i), split='transfer')
    write('tn4x_A.json', halves[0], 6)
    write('tn4x_B.json', halves[1], 6)
    write('tn4x_dev.json', [dict(name='dev0', split='transfer-dev', x=1, fault_class='none'),
                            dict(name='dev1', split='transfer-dev', x=0, fault_class='force-stop')], 1)


if __name__ == '__main__':
    main()
