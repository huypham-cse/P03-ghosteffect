"""Collect B-12 K-9 action-audit receipts (k9_fault_case.py --action) into one CSV.

One row per trial directory with RESULT.json; trials are listed in run order.
Columns name the action (sync, send_messages, none, recompose), the UI receipt of
every tap, and what reached GreenMail after the action. Raw receipts stay in the
trial directories; this CSV is the data file the paper cites.
"""
import argparse
import csv
import json
from pathlib import Path

COLUMNS = ('trial', 'config', 'action', 'nonce', 'request_id', 'fault_reproduced', 'k9_state_before_fault',
           'server_copies_before_action', 'taps', 'window_s', 'smtp_data_after_action',
           'server_copies_after_action', 'distinct_message_ids_after_action', 'k9_outbox_after_action',
           'still_in_outbox_error', 'action_start_utc_ns')


def row(trial, result):
    a = result['audit']
    return dict(trial=trial, config=result['config'], action=a['action'], nonce=result['nonce'],
                request_id=result['request_id'], fault_reproduced=int(result['verdict'] == 'REPRODUCED'),
                k9_state_before_fault=result['k9_outbox_before_fault'],
                server_copies_before_action=result['server']['copies'],
                taps='|'.join(t['label'] for t in a['taps']), window_s=a['window_s'],
                smtp_data_after_action=a['smtp_data_after_action'],
                server_copies_after_action=a['server_copies_after_action'],
                distinct_message_ids_after_action=a['distinct_message_ids_after_action'],
                k9_outbox_after_action=a['k9_outbox_after_action'],
                still_in_outbox_error=int(a['k9_outbox_after_action'].startswith('error|')),
                action_start_utc_ns=a['action_start_utc_ns'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path, help='directory holding one sub-directory per trial')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = []
    for path in sorted(args.runs.glob('*/RESULT.json')):
        result = json.loads(path.read_text(encoding='utf-8'))
        if 'audit' in result:
            results.append((path.parent.name, result))
    results.sort(key=lambda item: item[1]['audit']['action_start_utc_ns'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, COLUMNS)
        writer.writeheader()
        writer.writerows(row(trial, result) for trial, result in results)
    print(f'wrote {len(results)} trials to {args.output}')


if __name__ == '__main__':
    main()
