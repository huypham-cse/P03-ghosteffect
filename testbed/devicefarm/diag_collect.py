"""Diagnosis only (b-log 24/11, diag3): element_planner.collect exactly as the campaign runs it, with every screen read
recorded. The module is imported unchanged (same file, so the same reader hash and store check); only its `tree`
function is wrapped to save each dump, its duration and what to_room's checks see. Trials of this run never count.

  python3 testbed/devicefarm/diag_collect.py --schedule <json> --store <store> --adb <adb> --serial <s> --out <dir>
"""
import argparse
import itertools
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import element_planner as ep   # noqa: E402


def main():
    p = argparse.ArgumentParser()
    for name in ('--schedule', '--out', '--store'):
        p.add_argument(name, type=Path, required=True)
    p.add_argument('--adb', required=True)
    p.add_argument('--serial', required=True)
    a = p.parse_args()
    dumps = a.out.parent / (a.out.name + '-dumps')
    dumps.mkdir(parents=True, exist_ok=True)
    counter, original = itertools.count(), ep.tree

    def tree(phone):
        t0 = time.monotonic()
        xml, root = original(phone)
        i = next(counter)
        (dumps / ('%04d.xml' % i)).write_text(xml, encoding='utf-8')
        first = root.find('.//node') if root is not None else None
        with open(dumps / 'reads.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(dict(i=i, seconds=round(time.monotonic() - t0, 2), parsed=root is not None,
                                    head=xml[:160] if root is None else '', first_package=first.get('package') if first is not None else '',
                                    room_row=ep.room_row(root)[0] is not None, in_room=ep.in_room(root),
                                    element_nodes=sum(n.get('package') == ep.ELEMENT for n in root.iter('node')) if root is not None else 0)) + '\n')
        return xml, root

    ep.tree = tree
    ep.collect(argparse.Namespace(schedule=a.schedule, out=a.out, store=a.store, adb=a.adb, serial=a.serial))


if __name__ == '__main__':
    main()
