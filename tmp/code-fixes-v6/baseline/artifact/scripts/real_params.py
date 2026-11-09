#!/usr/bin/env python3
"""Derive the simulator's MEASURED parameters from the emulator measurements in artifact/results/real/ and write
results/real/params.csv (name,value,provenance), which `planner_sim.py real` reads.

Round 3: the parameters come from CAMPAIGN 2 (results/real/campaign2/, screen-validating reader; SUMMARY.md section
"Campaign 2"), which supersedes campaign 1 for Element's lag and family errors (campaign 1's five "co-failures" are
re-scored as no-observation, c1_rescored_cofailures.csv).  Campaign 1 still supplies K-9's queued-mail behaviour.

Nothing is typed in by hand except the parameters marked 'assumption' in their provenance.  Every measured value is
recomputed from the per-trial CSVs, and the script asserts the structural facts the mapping relies on.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.join(HERE, '..', 'results', 'real')
C2 = os.path.join(REAL, 'campaign2')


def rd(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


# measured cell(s) -> the simulator's lag cell (planner_sim.ELEM_CELL maps fault classes onto these)
CELLS = {
    'floor': ['none/nofault'],                                            # agent killed, app alive: reader floor
    'appdeath': ['bg_kill9/respdrop', 'bg_kill9_sticky/respdrop', 'bg_kill9_sticky_v1/respdrop',
                 'force_stop/respdrop', 'force_stop_sticky/respdrop', 'force_stop_sticky_v1/respdrop'],
    'net': ['netcut/respdrop'],
    'acked': ['bg_kill9/acked'],                                           # acknowledged send, then app death
}


def main():
    if not os.path.exists(os.path.join(C2, 'c2_element_first_visible.csv')):
        print('no campaign-2 measurements; no measured parameters')
        return
    rows = []

    def P(name, value, prov):
        rows.append(dict(name=name, value=value, provenance=prov))

    # ------------------------------------------------------------ Element: G2, outcomes
    fv = rd(os.path.join(C2, 'c2_element_first_visible.csv'))
    out = {r['cell']: r for r in rd(os.path.join(C2, 'c2_element_outcomes.csv'))}
    n_all = len(fv)
    assert n_all == 101
    assert all(int(r['server_copies']) == 1 for r in fv), 'every Element trial must end with exactly one copy'
    allrd = out['ALL_interrupted(respdrop)']
    assert int(allrd['n']) == int(allrd['exactly_once']) == int(allrd['put_ge2_single_txn']) == 83
    P('g2_break', 0.0, f'Element: {n_all}/{n_all} trials exactly once; 83/83 response-loss trials re-sent a single txnId '
      f'or reconciled via /sync (c2_element_outcomes.csv)')
    P('g2_nodedup', 0.0, 'Element: 0 duplicates in 101 trials (c2_element_outcomes.csv)')

    # ------------------------------------------------------------ Element: lag per cell (row = indicator), lag-blind reads
    fam = {r['trial']: r for r in rd(os.path.join(C2, 'c2_element_per_trial_families.csv'))}
    assert all(r['censored_final'] == '0' for r in fv), 'campaign 2 has no censored trial'
    assert all(r['row_first_visible_hi_s'] == r['indicator_first_visible_hi_s'] for r in fv), \
        'the indicator must appear in the same dump as the row (not a lag-free hop-1 view)'
    for cell, cells in CELLS.items():
        tr = [r for r in fv if r['cell'] in cells]
        smp = []
        for r in tr:
            blind = 1 if fam[r['trial']]['a_indicator_early'] == 'wrong' else 0
            assert (fam[r['trial']]['a_indicator_early'] == 'wrong') == (fam[r['trial']]['b_row_early'] == 'wrong')
            smp.append(f"{float(r['row_first_visible_hi_s']):.2f}:{blind}")
        P(f'elem_lag_{cell}', '|'.join(smp),
          f'Element {"+".join(cells)}: {len(tr)} trials; recovery-to-visible lag (upper end of the interval, s; t0 = relaunch '
          f'intent / network restore / Send tap) : first verified read was lag-blind "absent" (1) or not (0) '
          f'(c2_element_first_visible.csv, c2_element_per_trial_families.csv)')
    # ------------------------------------------------------------ Element: late reads
    late_wrong = sum(1 for r in fam.values() for k in ('a_indicator_late', 'b_row_late', 'c_digest_late')
                     if r[k] == 'wrong')
    assert late_wrong == 0, 'campaign 2: no late read was wrong'
    bot_all = sum(1 for r in fam.values() if r['a_indicator_late'] == r['b_row_late'] == r['c_digest_late'] == 'BOT')
    bot_any = sum(1 for r in fam.values() if 'BOT' in (r['a_indicator_late'], r['b_row_late'], r['c_digest_late']))
    assert bot_all == bot_any
    P('bot_late', bot_all / n_all, f'Element: all three families bot (no observation, wrong screen) together at the late '
      f'read in {bot_all}/{n_all}; never one alone (c2_element_per_trial_families.csv)')
    for name in ('hop1_persist1', 'hop1_view1', 'nonce_persist', 'nonce_view', 'digest_persist', 'digest_view'):
        P(name, 0.0, f'Element committed side: 0 wrong late reads among 99 observed (c2_element_families.csv); '
          'bounds still come from CP on simulated labels')
    tail = 1 - 0.05 ** (1 / n_all)
    P('elem_tail_ub', tail, f'one-sided 95% CP upper bound on P(not visible within the window) from 0/{n_all} censored '
      '(used only for the lag-tail sensitivity rows; not a measurement)')

    # ------------------------------------------------------------ K-9: failed state (campaign 2), queued delivery (campaign 1)
    ks = rd(os.path.join(C2, 'c2_k9_summary.csv'))
    rdk = [r for r in ks if r['cell'].endswith('/respdrop')]
    n_rdk = sum(int(r['n']) for r in rdk)
    assert all(r['app_state_late'] == 'Outbox:error' and r['app_state_after_sync'] == 'Outbox:error'
               and r['sync_new_DATA'] == '0' and r['sendmsgs_new_DATA'] == '0' for r in rdk)
    P('k9_failed_commit', 1.0, f'K-9 (campaign 2): after a lost SMTP reply the mail stays in the Outbox with '
      f'send_state=error, 0 new DATA on Sync or Send-messages, in {n_rdk}/{n_rdk} (c2_k9_summary.csv)')
    out1 = rd(os.path.join(REAL, 'e4_outcomes.csv'))
    np_k = [r for r in out1 if r['app'] == 'k9' and r['timing'] == 'net_pre']
    n_nk = sum(int(r['n']) for r in np_k)
    evk = sum(int(r['eventual_exactly_once']) for r in np_k)
    assert evk == n_nk
    P('k9_queued_delivered', 1.0, f'K-9 (campaign 1): queued (offline) mail delivered exactly once after a sync in '
      f'{evk}/{n_nk} (e4_outcomes.csv); campaign 2 net_pre 3/3 after Sync')
    P('k9_lag_lo', 45.0, 'K-9 queued-mail delivery lag, lower end: the 45 s window (campaign 1, measured)')
    P('k9_lag_hi', 900.0, "K-9 queued-mail delivery lag, upper end: K-9's 15-min poll interval (assumption: uniform law; "
      'the unattended poll was not measured)')
    snt = [r for r in ks if r['mode'] == 'sent' and r['cell'].endswith('acked')]
    app = [float(x) for r in snt for x in r['sent_server_append_after_send_s'].split('|')]
    P('k9_sent_lo', min(app), f'K-9 + IMAP Sent: APPEND of an acknowledged mail after Send, min of {len(app)} (c2_k9_summary.csv)')
    P('k9_sent_hi', max(app), f'K-9 + IMAP Sent: APPEND of an acknowledged mail after Send, max of {len(app)}')
    srd = [r for r in ks if r['mode'] == 'sent' and r['cell'].endswith('/respdrop')]
    assert all(set(r['sent_server_end'].split('|')) == {'0'} for r in srd), 'failed mail never reaches Sent'

    # ------------------------------------------------------------ run configuration
    P('nonce_policy', 'visible', 'Element: the experiment typed the nonce into the message body (counterparty-visible)')
    P('no_vlm', 1, 'no VLM was measured (no-LLM rule); the VLM family is removed rather than modelled')
    with open(os.path.join(REAL, 'params.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['name', 'value', 'provenance'])
        w.writeheader()
        w.writerows(rows)
    print(f'wrote {len(rows)} measured parameters to results/real/params.csv')


if __name__ == '__main__':
    main()
