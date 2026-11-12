"""Collect B-12 K-9 action-audit receipts (k9_fault_case.py --action) into one CSV.

One row per trial directory, in run order (directory names t01, t02, ...), including
trials that failed before the action: they get valid=0 and the error as the reason,
taken from RESULT.json or, for trials that died without one, from the trial's log.
Columns name the action (sync, send_messages, none, recompose), the UI receipt of
every tap, and what reached GreenMail after the action.
"""
import argparse
import csv
import json
from pathlib import Path

COLUMNS = ('trial', 'config', 'action', 'valid', 'invalid_reason', 'nonce', 'request_id', 'fault_reproduced',
           'k9_state_before_fault', 'server_copies_before_action', 'taps', 'window_s', 'smtp_data_after_action',
           'server_copies_after_action', 'distinct_message_ids_after_action', 'k9_outbox_after_action',
           'still_in_outbox_error', 'action_start_utc_ns')


def row(trial, result, log):
    action = trial.split('-', 1)[1]
    if not result or 'audit' not in result:
        reason = (result or {}).get('reason') or (log.strip().splitlines() or ['no receipt'])[-1]
        return dict(trial=trial, action=action, valid=0, invalid_reason=reason[:200],
                    config=(result or {}).get('config', ''), fault_reproduced=0)
    a = result['audit']
    assert a['action'] == action, trial
    return dict(trial=trial, config=result['config'], action=action, valid=int(result['verdict'] == 'REPRODUCED'),
                invalid_reason='' if result['verdict'] == 'REPRODUCED' else 'fault not reproduced',
                nonce=result['nonce'], request_id=result['request_id'],
                fault_reproduced=int(result['verdict'] == 'REPRODUCED'),
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
    rows = []
    for trial in sorted(p for p in args.runs.iterdir() if p.is_dir()):
        receipt, log = trial / 'RESULT.json', trial.with_suffix('.log')
        result = json.loads(receipt.read_text(encoding='utf-8')) if receipt.exists() else None
        rows.append(row(trial.name, result, log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'wrote {len(rows)} trials ({sum(r["valid"] for r in rows)} valid) to {args.output}')


if __name__ == '__main__':
    main()
