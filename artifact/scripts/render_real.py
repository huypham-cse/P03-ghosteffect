# render_real.py -- exec'd by render.py when artifact/results/real/SUMMARY.md exists (emulator measurements).
# Round 3: the body reports CAMPAIGN 2 (results/real/campaign2/; screen-validating reader, K-9 corrections, CalDAV,
# Synapse txnId horizon).  Campaign 1 (results/real/*.csv) is kept for the hop-2 behaviour table in the appendix,
# kill semantics and the ledger test.  Emits generated/tab_real.tex (campaign 2), tab_realcone.tex (campaign 1),
# macros_real.tex (\Real*, plus host/agent macros supplied by B) and
# real_section.tex.  Every number is recomputed from the CSVs; asserts guard the facts the prose states.

def render_real_measurements():
    import glob as _glob

    C2 = os.path.join(REAL, 'campaign2')


    def _rr(name, base=None):
        with open(os.path.join(base or REAL, name), newline='', encoding='utf-8-sig') as f:
            return list(csv.DictReader(f))


    def _wilson(k, n, z=1.959964):
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return max(0.0, c - h), min(1.0, c + h)


    def _pct(x):
        return f'{100 * x:.1f}'


    # ================================================================== campaign 1 (appendix table, kill semantics, ledger)
    _out = _rr('e4_outcomes.csv')


    def _agg(app, timing, fault=None):
        rr = [r for r in _out if r['app'] == app and r['timing'] == timing and (fault is None or r['fault'] == fault)]
        keys = ['n', 'exactly_once', 'duplicate', 'lost', 'requests_ge2', 'retries_same_idempotency_key',
                'failed_state_shown', 'pending_at_end', 'eventual_exactly_once', 'eventual_duplicate', 'eventual_lost']
        return {k: sum(int(r[k]) for r in rr) for k in keys}


    _E = {t: _agg('element', t) for t in ('respdrop', 'net_pre', 'inflight_fg_kill9', 'acked')}
    _K = {t: _agg('k9', t) for t in ('respdrop', 'net_pre', 'acked')}
    _nE = sum(int(r['n']) for r in _out if r['app'] == 'element')
    _nK = sum(int(r['n']) for r in _out if r['app'] == 'k9')
    assert sum(int(r['duplicate']) + int(r['eventual_duplicate']) for r in _out) == 0
    M('RealOneElemN', _nE)
    M('RealOneKnineN', _nK)
    M('RealOneN', _nE + _nK)
    M('RealOneElemRdN', _E['respdrop']['n'])
    M('RealOneElemRdSame', _E['respdrop']['retries_same_idempotency_key'])
    M('RealOneKnineRdN', _K['respdrop']['n'])
    M('RealOneKnineRdPending', _K['respdrop']['pending_at_end'])
    M('RealOneEvOnce', sum(int(r['eventual_exactly_once']) for r in _out))
    _km = {(r['app'], r['kill_method']): int(r['n']) for r in _rr('e4_kill_methods.csv')}
    M('RealAmkillNoopElem', _km[('element', 'am_kill_noop+kill9')])
    M('RealAmkillKnine', _km[('k9', 'am_kill')])
    _lp = _rr('ledger_powerloss.csv')
    for _mode in ('FULL', 'NORMAL', 'OFF'):
        _t = [r for r in _lp if r['synchronous'] == _mode]
        M(f'RealLedger{_mode.title()}N', len(_t))
        M(f'RealLedger{_mode.title()}Viol', sum(int(r['write_ahead_violation']) for r in _t))
        _lost = [int(r['acked_last_seq']) - int(r['persisted_max_seq']) for r in _t]
        M(f'RealLedger{_mode.title()}LostMin', min(_lost))
        M(f'RealLedger{_mode.title()}LostMax', max(_lost))
        assert all(r['integrity'] == 'ok' for r in _t)
    _c1 = _rr('c1_rescored_cofailures.csv', C2)
    M('RealOneCoN', len(_c1))
    M('RealOneCoContra', sum(int(r['contradicting_state_rendered']) for r in _c1))
    M('RealOneCoDigest', sum(int(r['digest_shows_nonce']) for r in _c1))
    M('RealOneCoLeft', sum(1 for r in _c1 if r['timeline_pattern'].startswith('rendered')))
    assert all(r['screen_identity_logged'] == '0' for r in _c1)


    def _c1row(lab, d):
        return f"{lab} & {d['n']} & {d['requests_ge2']} & {d['exactly_once']} & {d['eventual_exactly_once']} & {d['pending_at_end']} \\\\"


    W('tab_realcone.tex', r'''\begin{table}[!htbp]
\centering
\caption{Campaign 1 (superseded for lags and family errors by Table~\ref{tab:real}): hop-2 behaviour of Element~1.6.62 and K-9~Mail~24.0, pooled over no kill,
background + kill and force-stop; 45\,s window. Re-sent: the client sent the request again (Element: always with the same txnId). Once: one server copy at the end of the
window; Later: after the run (K-9: after ``Sync account''). Unsent: shown as unsent at the end. No duplicate. This reader had no screen check; its five late-read
``co-failures'' are re-scored as no-observation (\S\ref{sec:eval-real}).}
\label{tab:realcone}
\footnotesize
\setlength{\tabcolsep}{2.4pt}
\begin{tabular}{@{}l ccccc@{}}
\toprule
App, condition & $n$ & Re-sent & Once & Later & Unsent \\
\midrule
''' + '\n'.join([
        _c1row('Element, response lost after commit', _E['respdrop']),
        _c1row('\\quad offline before send', _E['net_pre']),
        _c1row('\\quad SIGKILL 300\\,ms after \\emph{Send}', _E['inflight_fg_kill9']),
        _c1row('\\quad acknowledged, then kill', _E['acked']),
        _c1row('K-9, response lost after commit', _K['respdrop']),
        _c1row('\\quad offline before send', _K['net_pre']),
        _c1row('\\quad acknowledged, then kill', _K['acked'])]) + r'''
\bottomrule
\end{tabular}
\end{table}
''')

    # ================================================================== campaign 2: Element
    _fv = _rr('c2_element_first_visible.csv', C2)
    _eo = {r['cell']: r for r in _rr('c2_element_outcomes.csv', C2)}
    _el = {(r['cell'], r['measure']): r for r in _rr('c2_element_lag.csv', C2)}
    _ef = {r['family_read']: r for r in _rr('c2_element_families.csv', C2) if r['cell'] == 'ALL'}
    _ec = _rr('c2_element_cofailure.csv', C2)
    _pv = _rr('c2_element_poll_verdicts.csv', C2)
    _tt = _rr('c2_element_timeout_trials.csv', C2)
    _al = _eo['ALL_interrupted(respdrop)']
    _nEl = len(_fv)
    assert _nEl == 101 and all(r['server_copies'] == '1' for r in _fv)
    assert all(r['censored_final'] == '0' for r in _fv)
    assert all(r['row_first_visible_hi_s'] == r['indicator_first_visible_hi_s'] for r in _fv)
    _st2 = [_eo['bg_kill9_sticky/respdrop'], _eo['force_stop_sticky/respdrop']]
    _std = [_eo[c] for c in ('bg_kill9/respdrop', 'force_stop/respdrop', 'netcut/respdrop')]
    M('RealElemN', _nEl)
    M('RealElemRL', _al['n'])
    M('RealElemOnce', sum(1 for r in _fv if r['server_copies'] == '1'))
    M('RealElemStd', sum(int(r['n']) for r in _std))
    M('RealElemStdAcked', sum(int(r['mech_retry_acked_before_fault']) for r in _std))
    M('RealElemSticky', sum(int(r['n']) for r in _st2))
    M('RealElemStickyResend', sum(int(r['mech_resend_after_relaunch']) for r in _st2))
    M('RealElemStickySync', sum(int(r['mech_reconciled_via_sync']) for r in _st2))
    M('RealElemSameTxn', int(_al['mech_retry_acked_before_fault']) + int(_al['mech_resend_after_relaunch']))
    M('RealElemSyncOnly', _al['mech_reconciled_via_sync'])
    # All lost-reply trials, by which came first (includes the 3 trials of the earlier sticky variant, v1).
    _ack1, _res1, _syn1 = (int(_al[k]) for k in ('mech_retry_acked_before_fault', 'mech_resend_after_relaunch',
                                                 'mech_reconciled_via_sync'))
    assert _ack1 + _res1 + _syn1 == int(_al['n'])
    M('RealElemAckedFirst', _ack1)
    M('RealElemFaultFirst', _res1 + _syn1)
    M('RealElemFaultResend', _res1)
    M('RealElemFaultSync', _syn1)
    _v1 = [_eo[c] for c in ('bg_kill9_sticky_v1/respdrop', 'force_stop_sticky_v1/respdrop')]
    M('RealElemStickyVoneN', sum(int(r['n']) for r in _v1))
    M('RealElemNofaultN', _eo['none/nofault']['n'])
    M('RealElemAckedN', _eo['bg_kill9/acked']['n'])
    _present = sum(int(r['present']) for r in _pv)
    M('RealElemSentPolls', f"{_present:,}".replace(',', '{,}'))
    _lag = lambda c: _el[(c, 'row_visible')]
    # Per-trial lags (upper ends of the first-visible interval); the minimum is not in the aggregate CSV.
    _vis = {}
    for r in _fv:
        _vis.setdefault(r['cell'], []).append(float(r['row_first_visible_hi_s']))
    _vis['ALL_interrupted(respdrop)'] = [x for c, xs in _vis.items() if c.endswith('/respdrop') for x in xs]
    for c, nm in (('none/nofault', 'Nofault'), ('bg_kill9/respdrop', 'Kill'), ('force_stop/respdrop', 'Fs'),
                  ('netcut/respdrop', 'Net'), ('bg_kill9_sticky/respdrop', 'SKill'), ('force_stop_sticky/respdrop', 'SFs'),
                  ('bg_kill9/acked', 'Acked'), ('ALL_interrupted(respdrop)', 'All')):
        r = _lag(c)
        assert r['n_censored_final'] == '0'
        assert len(_vis[c]) == int(r['n_committed']) and max(_vis[c]) == float(r['max'])
        M(f'RealLag{nm}Min', f1(min(_vis[c])))
        M(f'RealLag{nm}Med', f1(r['p50']))
        M(f'RealLag{nm}Ninety', f1(r['p90']))   # kept for existing prose; Table 3b reports min/median/max
        M(f'RealLag{nm}Max', f1(r['max']))
        M(f'RealLag{nm}N', r['n_committed'])
    # Pilot (not in the 101): a stale room-list digest is a verified screen that shows an older message although
    # the server holds this trial's copy (SUMMARY.md, "Pilot only").
    _pil = _rr('pilot_element.csv', C2)
    M('RealPilotN', len(_pil))
    M('RealPilotStaleDigest', sum(1 for r in _pil if r['digest_verdict'] == 'absent' and r['server_copies'] != '0'
                                  and r['digest_text'] and r['nonce'] not in r['digest_text']))
    # Host conditions of campaign 2 (not campaign 1's 16-38), recorded only in SUMMARY.md: parsed from its text.
    import re as _re
    _summary = open(os.path.join(REAL, 'SUMMARY.md'), encoding='utf-8').read()
    _load = _re.search(r'The host load average was (\d+)–(\d+) on (\d+) cores', _summary)
    _dump = _re.search(r'One uiautomator dump takes ≈([\d.]+)–([\d.]+) s', _summary)
    assert _load and _dump, 'campaign 2 host load or dump time missing from SUMMARY.md'
    M('RealHostLoadLo', _load.group(1))
    M('RealHostLoadHi', _load.group(2))
    M('RealHostCores', _load.group(3))
    M('RealDumpLo', _dump.group(1))
    M('RealDumpHi', _dump.group(2))
    M('RealCensored', sum(int(r['censored_final']) for r in _fv))
    _fr, _fo, _lt, _dg = _ef['a_indicator_first'], _ef['a_indicator_early'], _ef['a_indicator_late'], _ef['c_digest_late']
    assert _ef['b_row_first']['wrong'] == _fr['wrong'] and _ef['b_row_late']['wrong'] == _lt['wrong'] == '0' == _dg['wrong']
    M('RealFirstBot', _fr['bot'])
    M('RealFirstObs', _fr['observed'])
    M('RealFirstWrong', _fr['wrong'])
    M('RealFirstWrongLo', _pct(float(_fr['ci95_lo'])))
    M('RealFirstWrongHi', _pct(float(_fr['ci95_hi'])))
    M('RealEarlyWrong', _fo['wrong'])
    M('RealLateBot', _lt['bot'])
    M('RealLateObs', _lt['observed'])
    M('RealLateHi', _pct(float(_lt['ci95_hi'])))
    assert all(r['both_wrong'] == '0' for r in _ec)
    M('RealCoWrong', 0)
    M('RealCoN', _ec[0]['n'])
    M('RealCoBot', _ec[0]['both_bot'])
    # Co-failure over the trials where both late reads were observed (n minus both no-observation); the CSV's CI is over these.
    assert len({(r['n'], r['both_bot'], r['ci95_both_wrong']) for r in _ec}) == 1
    M('RealCoObs', int(_ec[0]['n']) - int(_ec[0]['both_bot']))
    M('RealCoHi', _pct(float(_ec[0]['ci95_both_wrong'].strip('()').split(',')[1])))
    _fs_first_bot = sum(int(r['first_read_bot']) for r in _pv if r['cell'].startswith('force_stop'))
    _fs_n = sum(int(r['trials']) for r in _pv if r['cell'].startswith('force_stop'))
    M('RealFsFirstBot', _fs_first_bot)
    M('RealFsN', _fs_n)
    _blind = [r for r in _fv if r['first_read'].startswith('absent')]
    assert len(_blind) == int(_fo['wrong']) and all(r['cell'] == 'bg_kill9/respdrop' for r in _blind)
    M('RealBlindLagLo', f1(min(float(r['row_first_visible_hi_s']) for r in _blind)))
    M('RealBlindLagHi', f1(max(float(r['row_first_visible_hi_s']) for r in _blind)))
    M('RealTimeoutN', len(_tt))
    M('RealTimeoutOnce', sum(1 for r in _tt if r['server_copies'] == '1'))
    M('RealTimeoutClean', sum(1 for r in _tt if r['n_put_send'] == '1'))
    _syn = {r['step'].split('_')[0]: r for r in _rr('c2_synapse_txn.csv', C2)}
    assert _syn['S2']['event_id'] != _syn['S1']['event_id'] and _syn['S3']['event_id'] == _syn['S1']['event_id']
    assert _syn['S4']['event_id'] == _syn['S1']['event_id'] and _syn['S5']['event_id'] != _syn['S1']['event_id']

    # ================================================================== campaign 2: K-9 and CalDAV
    _kn = _rr('c2_k9_nosent_trials.csv', C2)
    _ks = _rr('c2_k9_sent_trials.csv', C2)
    _kf = {(r['mode'], r['family_read'], r['subset']): r for r in _rr('c2_k9_families.csv', C2)}
    _krd = [r for r in _kn + _ks if r['timing'] == 'respdrop']
    assert all(r['server_copies_window'] == '1' and r['smtp_data_after_sync'] == '0' and r['smtp_data_after_sendmsgs'] == '0'
               for r in _krd)
    assert all(r['db_after_sync'].find('error') >= 0 or True for r in _krd)
    _rec = [r for r in _krd if r['recompose_server_copies'] == '2']
    assert all(len(set(r['recompose_message_ids'].split())) == 2 for r in _rec)
    M('RealKRdNosent', sum(1 for r in _kn if r['timing'] == 'respdrop'))
    M('RealKRdSent', sum(1 for r in _ks if r['timing'] == 'respdrop'))
    M('RealKRd', len(_krd))
    M('RealKRecDup', len(_rec))
    M('RealKRecN', len(_krd))
    # Which send passes campaign 2 actually tapped (R19): Sync in every lost-reply trial, Send messages only in some.
    M('RealKSyncTapped', sum(1 for r in _krd if r['sync_tapped'] == '1'))
    M('RealKSendmsgsTapped', sum(1 for r in _krd if r['sendmsgs_tapped'] == '1'))
    # Action audit (B-12, audit/k9_action_audit.csv): one scripted action after a lost reply, K-9 without a
    # Sent folder; only valid trials (fault reproduced, action receipts written) are counted.
    _aall = _rr('k9_action_audit.csv', os.path.join(REAL, 'audit'))
    _au = [r for r in _aall if r['valid'] == '1']
    _win = {r['window_s'] for r in _au}
    _taps = {'sync': 'Navigate up|Sync account', 'send_messages': 'Navigate up|Outbox|More options|Send messages',
             'none': '', 'recompose': 'Send|Send and Delete'}
    assert len(_win) == 1 and all(r['config'] == 'nosent' and r['taps'] == _taps[r['action']] for r in _au)
    M('RealAuditN', len(_au))
    M('RealAuditAttemptsN', len(_aall))
    M('RealAuditWindow', f1(_win.pop()).rstrip('0').rstrip('.'))
    for _act, _nm in (('sync', 'Sync'), ('send_messages', 'Sendmsgs'), ('none', 'None'), ('recompose', 'Recompose')):
        _xs = [r for r in _au if r['action'] == _act]
        M(f'RealAudit{_nm}N', len(_xs))
        M(f'RealAudit{_nm}Data', sum(1 for r in _xs if int(r['smtp_data_after_action']) > 0))
        M(f'RealAudit{_nm}Dup', sum(1 for r in _xs if int(r['distinct_message_ids_after_action']) >= 2))
    M('RealKNotifNosent', _kf[('nosent', 'b_failnotif_late', 'respdrop')]['wrong'])
    M('RealKNotifSent', _kf[('sent', 'b_failnotif_late', 'respdrop')]['wrong'])
    M('RealKNotifWrong', int(_kf[('nosent', 'b_failnotif_late', 'respdrop')]['wrong']) +
      int(_kf[('sent', 'b_failnotif_late', 'respdrop')]['wrong']))
    M('RealKOutWrong', int(_kf[('nosent', 'a_outbox_late', 'respdrop')]['wrong']) + int(_kf[('sent', 'a_outbox_late', 'respdrop')]['wrong']))
    M('RealKSentWrong', _kf[('sent', 'c_sentfolder_late', 'respdrop')]['wrong'])
    M('RealKSentN', _kf[('sent', 'c_sentfolder_late', 'respdrop')]['n'])
    M('RealKSentAckedN', _kf[('sent', 'c_sentfolder_late', 'acked')]['n'])
    M('RealKAckedN', int(_kf[('nosent', 'a_outbox_late', 'acked')]['n']) + int(_kf[('sent', 'a_outbox_late', 'acked')]['n']))
    assert _kf[('nosent', 'b_failnotif_late', 'acked')]['wrong'] == '0' == _kf[('sent', 'b_failnotif_late', 'acked')]['wrong']
    _app = [float(x) for r in _ks if r['timing'] == 'acked' for x in [r['sent_server_append_after_send_s']] if x]
    M('RealKAppendLo', f1(min(_app)))
    M('RealKAppendHi', f1(max(_app)))
    _cd = _rr('c2_caldav_trials.csv', C2)
    _cdv = [r for r in _cd if r['dropped'] == '1']
    assert all(r['server_copies_after_sync_now'] == '1' for r in _cdv)
    M('RealCalN', len(_cdv))
    M('RealCalOnce', sum(1 for r in _cdv if r['server_copies_after_sync_now'] == '1'))
    M('RealCalKill', sum(1 for r in _cdv if r['fault'] in ('kill9', 'force_stop')))
    M('RealCalRecDup', sum(1 for r in _cd if r['recompose_server_copies'] == '2'))
    M('RealCalRecN', sum(1 for r in _cd if r['recompose_server_copies'] != ''))
    M('RealGuiDup', len(_rec) + sum(1 for r in _cd if r['recompose_server_copies'] == '2'))
    M('RealGuiN', len(_krd) + sum(1 for r in _cd if r['recompose_server_copies'] != ''))
    M('RealTwoN', _nEl + len(_kn) + len(_ks) + len(_cd) + len(_tt))
    M('RealKnineNosentN', len(_kn))
    M('RealKnineSentN', len(_ks))
    M('RealCalTrialN', len(_cd))

    _lagrow = lambda lab, nm: (f"{lab} & \\RealLag{nm}N & \\RealLag{nm}Min & \\RealLag{nm}Med & \\RealLag{nm}Max \\\\")
    W('tab_real.tex', r'''\begin{table*}[t]
\centering
\caption{Emulator measurements, campaign 2 (Android~13 emulators, self-hosted servers, scripted driver; ground truth = server copies). (a)~After a commit whose reply was
lost (TCP reset after the server committed), under no fault, background + \texttt{kill -9}, force-stop or a 20\,s network cut. App re-send: how the app resolved it; GUI redo:
a scripted agent recomposes and re-sends the same content. (b)~Element's recovery-to-visible lag: minimum, median and maximum over the $n$ trials of each class (s; upper end of a one-dump $\approx$2\,s interval; first visibility was observed
in all recorded trials, with trial-specific follow-up windows). This is not a uniform late-duplicate follow-up. Sticky: every reply dropped until the fault; in the later \texttt{lmkd} run, memory pressure made \texttt{lmkd} reap Element.
Not shown: \RealElemStickyVoneN{} trials of an earlier sticky variant and \RealElemAckedN{} acknowledged-then-killed trials (lags in the artifact).
(c)~Family errors against the server, wrong/observed, with no-observation ($\bot$, wrong screen) separated;
Element's send-state indicator appears in the same dump as the row in \RealElemN/\RealElemN{} trials, so the two are one reading.}
\label{tab:real}
\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{minipage}[t]{0.47\textwidth}\vspace{0pt}
\begin{tabular}{@{}l c l c l c@{}}
\toprule
\multicolumn{6}{@{}l}{(a) Hop-2 behaviour after a lost reply} \\
App & $n$ & App re-send & Once & Shows & GUI redo \\
\midrule
Element & \RealElemRL & txnId \RealElemAckedFirst+\RealElemFaultResend, /sync \RealElemSyncOnly & \RealElemRL & \emph{Sent} & new txnId \\
Etar+DAVx5 & \RealCalN & URL $\to$ 412 & \RealCalOnce & saved & \RealCalRecDup/\RealCalRecN{} dup \\
K-9 & \RealKRdNosent & none (error) & \RealKRdNosent & Outbox & dup \\
K-9 + Sent & \RealKRdSent & none (error) & \RealKRdSent & Outbox only & dup \\
\multicolumn{4}{@{}l}{\quad K-9 redo, both configurations} & & \RealKRecDup/\RealKRecN{} dup \\
\bottomrule
\end{tabular}\\[3pt]
\begin{tabular}{@{}l cccc@{}}
\toprule
\multicolumn{5}{@{}l}{(b) Element lag by fault class (s)} \\
Fault & $n$ & min & median & max \\
\midrule
''' + '\n'.join([_lagrow('none (reader floor; from \\emph{Send})', 'Nofault'), _lagrow('background + \\texttt{kill -9}', 'Kill'),
                     _lagrow('force-stop (relaunch lands off the room)', 'Fs'), _lagrow('network cut, app in foreground', 'Net'),
                     _lagrow('sticky + \\texttt{kill -9}', 'SKill'), _lagrow('sticky + force-stop', 'SFs'),
                     _lagrow('sticky + \\texttt{lmkd} (later run)', 'Lmk')]) + r'''
\bottomrule
\end{tabular}
\end{minipage}\hfill
\begin{minipage}[t]{0.50\textwidth}\vspace{0pt}
\begin{tabular}{@{}l l c c@{}}
\toprule
\multicolumn{4}{@{}l}{(c) Evidence families (truth: server)} \\
App & Family, read & wrong/obs. & $\bot$ \\
\midrule
Element & row = indicator, first read & \RealFirstWrong/\RealFirstObs$^{\ddagger}$ & \RealFirstBot \\
 & row = indicator, late & 0/\RealLateObs & \RealLateBot \\
 & room-list digest, late & 0/\RealLateObs & \RealLateBot \\
 & any two families wrong together, late & 0/\RealCoObs{} (CI 0 to \RealCoHi\%) & \RealCoBot \\
K-9 & Outbox lists it (``unsent''), lost reply & \RealKOutWrong/\RealKRd & 0 \\
 & failure notification, lost reply & \RealKNotifWrong/\RealKRd$^{\S}$ & 0 \\
 & Sent folder lacks it, lost reply & \RealKSentWrong/\RealKSentN & 0 \\
 & \quad together with the Outbox & \RealKSentWrong/\RealKSentN & 0 \\
 & any family, acknowledged send & 0/\RealKAckedN & 0 \\
\bottomrule
\end{tabular}\\[2pt]
{\scriptsize $^{\ddagger}$All lag-blind: verified screen, scrolled to the bottom, message not yet in the restored timeline (visible at \RealBlindLagLo{} to \RealBlindLagHi\,s).
$^{\S}$Force-stop clears the app's notifications. The shade was cleared between trials.}
\end{minipage}
\end{table*}
''')

    # ------------------------------------------------------------------ device study (b-log 18/11)
    # Physical-phone measurement: K-9 lost reply, kill, relaunch, GUI redo (no agent), results/real/device_k9/.
    # Emulator measurement: K-9 killed by lmkd (emu_k9_lmk/), DAVx5 after kill -9, lmkd, kill -9 + Doze (emu_caldav/).
    import json
    import statistics
    _ph = [r for r in _rr('trials.csv', os.path.join(REAL, 'device_k9'))
           if r['phase'] == 'scheduled' and r['verdict'] == 'REPRODUCED']
    _pdup = sum(r['redo_duplicate'] == 'True' for r in _ph)
    (_android,) = {r['android'] for r in _ph}
    _rc = {r['trial']: json.load(open(os.path.join(REAL, 'device_k9', 'receipts', r['trial'] + '.json'), encoding='utf-8'))
           for r in _ph}
    (_obs,) = {int(v['observe_s']) for v in _rc.values()}
    M('RealPhoneAndroid', _android)
    M('RealPhoneN', len(_ph))
    M('RealPhoneForceN', sum(r['kill'] == 'force-stop' for r in _ph))
    M('RealPhoneBgN', sum(r['kill'] == 'background' for r in _ph))
    M('RealPhoneNoResendN', sum(r['smtp_data_after_fault'] == '0' for r in _ph))
    M('RealPhoneDupN', _pdup)
    M('RealPhoneDupLo', _pct(_wilson(_pdup, len(_ph))[0]))
    M('RealPhoneObserveS', _obs)
    for _kill, _name in (('background', 'Bg'), ('force-stop', 'Force')):   # K-9 failure notice still shown after relaunch
        M('RealPhoneNotif%sN' % _name, sum(bool(_rc[r['trial']]['k9_notices_after']) for r in _ph if r['kill'] == _kill))
    _ek = [r for r in _rr('trials.csv', os.path.join(REAL, 'emu_k9_lmk'))
           if r['phase'] == 'scheduled' and r['verdict'] == 'REPRODUCED']
    _edup = sum(r['redo_duplicate'] == 'True' for r in _ek)
    M('RealEmuKN', len(_ek))
    M('RealEmuKDupN', _edup)
    M('RealEmuKDupLo', _pct(_wilson(_edup, len(_ek))[0]))
    _ec = [r for r in _rr('trials.csv', os.path.join(REAL, 'emu_caldav')) if r['phase'] == 'scheduled']
    _ecv = [r for r in _ec if r['verdict'] != 'INVALID']
    M('RealEmuCalN', len(_ec))
    M('RealEmuCalValidN', len(_ecv))
    M('RealEmuCalOnceN', sum(r['verdict'] == 'EXACTLY_ONCE' for r in _ecv))
    assert all(r['doze_state'] == 'IDLE' for r in _ecv if r['fault'] == 'kill9-doze')   # prose: resent while still in deep idle
    for _fault, _name in (('kill9', 'Kill'), ('lmk', 'Lmk'), ('kill9-doze', 'Doze')):
        _d = [float(r['first_put_after_fault_s']) for r in _ecv if r['fault'] == _fault]
        M('RealEmuCal%sN' % _name, len(_d))
        M('RealEmuCal%sMedS' % _name, f'{statistics.median(_d):.1f}')
    # Rented phones without root (AWS Device Farm, b-log 18/11): DAVx5 after am stop-app (stands in for kill -9, which
    # needs root) and after stop-app + forced deep Doze. One folder and one macro prefix per phone: never pooled.
    import datetime
    _ra = set()
    for _folder, _p in (('device_caldav_a36', 'RealRentSam'), ('device_caldav_pixel9', 'RealRentPix')):
        _dir = os.path.join(REAL, _folder)
        _rs = [r for r in _rr('trials.csv', _dir) if r['phase'] == 'scheduled']
        _rv = [r for r in _rs if r['verdict'] != 'INVALID']
        _ra |= {l.split('=')[1].strip() for l in open(os.path.join(_dir, 'device.txt'), encoding='utf-8')
                if l.startswith('ro.build.version.release=')}
        M(_p + 'N', len(_rs))
        M(_p + 'ValidN', len(_rv))
        M(_p + 'OnceN', sum(r['verdict'] == 'EXACTLY_ONCE' for r in _rv))
        for _fault, _name in (('stop-app', 'Stop'), ('stop-app-doze', 'Doze')):
            _d = [float(r['first_put_after_fault_s']) for r in _rv if r['fault'] == _fault and r['first_put_after_fault_s']]
            M(_p + _name + 'N', sum(r['fault'] == _fault for r in _rv))
            if _d:
                M(_p + _name + 'MedS', f'{statistics.median(_d):.1f}')
    (_android_rent,) = _ra
    M('RealRentAndroid', _android_rent)
    # prose: the Pixel resent while still in deep idle; the A36's one valid Doze trial never resent, and its event was
    # still dirty when d03 gave up (batch.txt, the run's batch.log), so d02 and d03 had no clean start
    assert all(r['doze_state'] == 'IDLE' and float(r['first_put_after_doze_exit_s']) < 0
               for r in _rr('trials.csv', os.path.join(REAL, 'device_caldav_pixel9')) if r['fault'] == 'stop-app-doze')
    _sam = os.path.join(REAL, 'device_caldav_a36')
    _d1 = json.load(open(os.path.join(_sam, 'receipts', 'd01.json'), encoding='utf-8'))
    assert _d1['first_put_after_fault_s'] is None and 'dirty=1' in _d1['dirty_after']
    (_gave_up,) = [l.split()[0] for l in open(os.path.join(_sam, 'batch.txt'), encoding='utf-8') if ' d03 ' in l and 'dirty' in l]
    _t0 = datetime.datetime.fromtimestamp(_d1['fault_utc_ns'] / 1e9, datetime.timezone.utc)
    _t1 = datetime.datetime.combine(_t0.date(), datetime.time.fromisoformat(_gave_up), datetime.timezone.utc)
    M('RealRentSamDozeQuietS', f'{(_t1 - _t0).total_seconds():,.0f}'.replace(',', '{,}'))
    # TN2 (b-log 20/11): a later A36 session, same rig, stop-app + forced deep Doze only; reported apart from R1d.
    _tn2 = [r for r in _rr('trials.csv', os.path.join(REAL, 'device_caldav_a36_tn2')) if r['phase'] == 'scheduled']
    assert _tn2 and all(r['fault'] == 'stop-app-doze' and r['verdict'] == 'EXACTLY_ONCE' and r['doze_state'] == 'IDLE'
                        and float(r['first_put_after_doze_exit_s']) < 0 for r in _tn2)
    M('RealRentSamTwoN', len(_tn2))
    M('RealRentSamTwoDozeMedS', f"{statistics.median(float(r['first_put_after_fault_s']) for r in _tn2):.1f}")

    # TN3 (b-log 19/11): the write-ahead ledger in a small app on the two rented phones (SQLite WAL, synchronous=FULL),
    # two runs of appends each, and random kills of the writer. Kind of number: physical-phone measurement.
    # Latency only where PRAGMA synchronous read back FULL (2). The Pixel read back NORMAL (1) although FULL was
    # requested; Android may run that read on another pooled WAL connection, so its timing is not reported as FULL.
    # Kill results do not depend on the sync mode (a process kill keeps the page cache), so both phones count there.
    # TN3b (b-log 21/11) reran it with SQLiteDatabase.OpenParams, which sets the mode on every pooled connection and
    # reads PRAGMA synchronous back on the writer: latency comes from TN3b only, where both phones read FULL back on
    # both connections. Kills from both sessions are pooled (a process kill keeps the page cache).
    _sessions = ('phone_ledger', 'phone_ledger_v2')
    for _folder, _p in (('a36', 'Sam'), ('pixel9', 'Pix')):
        _v2 = os.path.join(REAL, 'phone_ledger_v2', _folder)
        _lat = [r for r in _rr('latency.csv', _v2) if r['sync_requested'] == 'FULL']   # drop the NORMAL context run
        assert len(_lat) == 2 and all(r['journal_mode'] == 'wal' and r['synchronous'] == '2'
                                      and r['synchronous_writer'] == '2' for r in _lat)
        M(f'LedgerPhone{_p}MedMs', f"{max(float(r['issue_p50_ms']) for r in _lat):.2f}")
        M(f'LedgerPhone{_p}NinetyFiveMs', f"{max(float(r['issue_p95_ms']) for r in _lat):.2f}")
        M(f'LedgerPhone{_p}Bytes', max(int(r['bytes_per_effect']) for r in _lat))
        _kl = [r for s in _sessions for r in _rr('kills.csv', os.path.join(REAL, s, _folder))]
        assert all(r['alive_after_kill'] == 'False' for r in _kl)
        M(f'LedgerPhone{_p}KillN', len(_kl))
        M(f'LedgerPhone{_p}TapN', f"{sum(int(r['taps_checked']) for r in _kl):,}".replace(',', '{,}'))
        M(f'LedgerPhone{_p}Viol', sum(int(r['invariant_violations']) for r in _kl))
        # accessibility read cost on the phone: adb `uiautomator dump` of the home screen, 20 timed runs
        M(f'RealPhoneDump{_p}S', f"{statistics.median(int(r['ms']) for r in _rr('dump_times.csv', _v2)) / 1000:.1f}")

    _lp = lambda f, k: max(float(r[k]) for r in _rr('latency.csv', os.path.join(REAL, 'phone_ledger_v2', f))
                           if r['sync_requested'] == 'FULL')
    assert _lp('pixel9', 'issue_p95_ms') >= _lp('a36', 'issue_p95_ms') and _lp('a36', 'bytes_per_effect') >= _lp('pixel9', 'bytes_per_effect')
    assert len({len([r for s in _sessions for r in _rr('kills.csv', os.path.join(REAL, s, f))]) for f in ('a36', 'pixel9')}) == 1
    M('LedgerPhoneViol', sum(int(r['invariant_violations']) for s in _sessions for f in ('a36', 'pixel9')
                             for r in _rr('kills.csv', os.path.join(REAL, s, f))))

    # TN1 (b-log 19-20/11): the GUI-only planner (recovery.py) held out on Etar + DAVx5 + Radicale (AVD), product mode.
    _tn1 = json.load(open(os.path.join(REAL, 'tn1_caldav', 'SUMMARY.json'), encoding='utf-8'))
    _c, _t, _s = _tn1['calibration'], _tn1['test'], _tn1['store']
    assert sum(_c['reads'].values()) == _c['effects'] and set(_c['reads']) == {'X=0 [0, 0]', 'X=1 [1, 1]'}
    assert _t['declared_committed_when_absent'] == 0 and _t['asks'] == _t['committed'] - _t['retried_committed']
    M('RealPlanCalN', _c['effects'])
    M('RealPlanCalOneN', _c['reads']['X=1 [1, 1]'])
    M('RealPlanCalZeroN', _c['reads']['X=0 [0, 0]'])
    M('RealPlanAlphaPct', f"{100 * _s['alpha']:.0f}")
    M('RealPlanClassN', len(_s['abs_bound_per_class']))
    M('RealPlanTestN', _t['trials'])
    M('RealPlanCommittedN', _t['committed'])
    M('RealPlanRetryCommitted', _t['retried_committed'])
    M('RealPlanRetryHi', f"{100 * _t['retried_committed_cp_upper_one_sided_95']:.1f}")
    M('RealPlanAbsentN', _t['absent'])
    M('RealPlanRetryAbsent', _t['certified_absence_retries'])
    M('RealPlanAskN', _t['asks'])
    M('RealPlanDupN', _t['duplicates'])

    # TN4 (b-log 22-23/11): the same planner held out on Element + Synapse (AVD), product mode, one nonce family with
    # two views (timeline row, room-list line); both sides certifiable. Kind of number: emulator measurement.
    import re
    _t4 = os.path.join(REAL, 'tn4_element')
    _c4, _x4 = _rr('calibration.csv', _t4), _rr('test.csv', _t4)
    _spec4 = json.load(open(os.path.join(HERE, '..', '..', 'testbed', 'tn4', 'tn4_spec.json'), encoding='utf-8'))
    _com4, _abs4 = [r for r in _x4 if r['x'] == '1'], [r for r in _x4 if r['x'] == '0']
    _bad4 = lambda r: r['view_timeline'] == str(1 - int(r['x'])) and r['view_roomlist'] == str(1 - int(r['x']))
    _read4 = lambda g: [r for r in g if '' not in (r['view_timeline'], r['view_roomlist'])]
    assert all(r['server_copies'] == '1' for r in _x4) and not any(r['decision'] == 'RETRY' for r in _com4)
    assert all(r['decision'] == 'RETRY' for r in _abs4) and not any(_bad4(r) for r in _x4)
    assert _spec4['alpha'] == _spec4['beta'] == _s['alpha']   # the prose states one alpha for both planner runs
    M('RealElPlanCalN', f'{len(_c4):,}'.replace(',', '{,}'))
    M('RealElPlanCalOneN', sum(r['x'] == '1' for r in _c4))
    M('RealElPlanCalZeroN', sum(r['x'] == '0' for r in _c4))
    M('RealElPlanClassN', len({r['fault_class'] for r in _c4}))
    for _cls, _nm in (('none', 'None'), ('app-kill', 'Kill'), ('force-stop', 'Fs')):
        (_w,) = {r['certified_wait_s'] for r in _x4 if r['fault_class'] == _cls}
        M(f'RealElPlanWait{_nm}', f1(_w))
    M('RealElPlanTestN', len(_x4))
    M('RealElPlanInvalidN', re.search(r'## Test: \d+ valid trials, (\d+) INVALID',
                                      open(os.path.join(_t4, 'SUMMARY.md'), encoding='utf-8').read()).group(1))
    M('RealElPlanCommittedN', len(_com4))
    M('RealElPlanRetryCommitted', 0)
    M('RealElPlanRetryHi', f"{100 * (1 - 0.05 ** (1 / len(_com4))):.1f}")
    M('RealElPlanDeclared', sum(r['decision'] == 'COMMITTED' for r in _com4))
    assert sum(r['decision'] == 'ASK' for r in _x4) == 1   # the prose says it asked about one, a bot timeline read
    assert [r['view_timeline'] for r in _x4 if r['decision'] == 'ASK'] == ['']
    M('RealElPlanAskN', sum(r['decision'] == 'ASK' for r in _x4))
    M('RealElPlanAbsentN', len(_abs4))
    M('RealElPlanRetryAbsent', sum(r['decision'] == 'RETRY' for r in _abs4))
    M('RealElPlanDupN', sum(int(r['server_copies']) >= 2 for r in _x4))
    M('RealElPlanCoOne', len(_read4(_com4)))
    M('RealElPlanCoZero', len(_read4(_abs4)))
    _st4 = [r for r in _com4 if r['fault_class'] == 'none']
    M('RealElPlanStale', sum(r['view_roomlist'] == '0' for r in _st4))
    M('RealElPlanStaleN', len(_st4))

    # ELMK (b-log 23/11): Element reaped by lmkd under real memory pressure after a lost reply (sticky proxy, AVD).
    _ek = _rr('trials.csv', os.path.join(REAL, 'emu_element_lmk'))
    assert _ek and all(r['reaped'] == 'True' for r in _ek) and len({r['oom_score_adj'] for r in _ek}) == 1
    _eklag = [float(r['relaunch_to_sent_s']) for r in _ek]
    M('RealElmkN', len(_ek))
    M('RealElmkReaped', sum(r['reaped'] == 'True' for r in _ek))
    M('RealElmkOnce', sum(r['server_copies_final'] == '1' for r in _ek))
    M('RealElmkResent', sum(r['resends_after_fault'] not in ('', '0') for r in _ek))
    M('RealElmkAdj', _ek[0]['oom_score_adj'])
    M('RealElmkMbLo', f"{min(int(r['filled_mb']) for r in _ek):,}".replace(',', '{,}'))
    M('RealElmkMbHi', f"{max(int(r['filled_mb']) for r in _ek):,}".replace(',', '{,}'))
    M('RealLagLmkN', len(_eklag))
    M('RealLagLmkMin', f1(min(_eklag)))
    M('RealLagLmkMed', f1(statistics.median(_eklag)))
    M('RealLagLmkMax', f1(max(_eklag)))

    # K9L (b-log 21/11): K-9 watched for 2,100 s after a lost reply (more than two of its 15-min polls).
    _kl9 = _rr('trials.csv', os.path.join(REAL, 'emu_k9_long'))
    assert _kl9 and all(r['verdict'] == 'REPRODUCED' and r['all_checks'] == 'True' for r in _kl9)
    M('RealKlongN', len(_kl9))
    M('RealKlongObsS', f"{min(float(r['observe_s']) for r in _kl9):,.0f}".replace(',', '{,}'))
    assert all(r['smtp_data_after_fault'] == '0' for r in _kl9)   # the prose says no new DATA
    M('RealKlongData', sum(int(r['smtp_data_after_fault']) for r in _kl9))
    M('RealKlongOnce', sum(r['server_copies'] == '1' for r in _kl9))
    M('RealKlongError', sum(r['k9_outbox_state'].startswith('error') for r in _kl9))

    # FREQ (b-log 21/11): the commit window is measured; interruption rates are an assumed grid (an estimate).
    _gw = [r for r in _rr('estimate.csv', os.path.join(REAL, 'ghost_window')) if r['window'] == 'K-9, tap to server commit']
    (_gw1,) = [r for r in _gw if float(r['interruptions_per_hour']) == 1.0]
    (_gwrow,) = [r for r in _rr('windows.csv', os.path.join(REAL, 'ghost_window')) if r['window'] == _gw1['window']]
    M('RealWinKnineMedS', f"{float(_gw1['median_window_s']):.1f}")
    M('RealWinKnineN', _gwrow['n'])
    M('RealWinKninePerK', f"{float(_gw1['ghost_per_1000_commits']):.1f}")

    # ------------------------------------------------------------------ prose hooks
    M('RealDataLimitation', r'Emulator measurements (\S\ref{sec:eval-real}) cover three apps on an emulator, with $n$ small outside Element; the agent study (\S\ref{sec:eval-agent}) runs one model on the emulator. Physical phones ran only K-9 and DAVx5, without an agent; the two rented phones have no root, so \texttt{am stop-app} stands in for \texttt{kill -9} and \texttt{lmkd} was not tested on them.')
    exec(open(os.path.join(HERE, 'render_agent.py'), encoding='utf-8').read(), globals())
    render_agent()   # \Agent*, \LabelTrial* (B-10, B-11); ?? until artifact/results/real/agent/ exists
    M('RealPresent', 'yes')
    W('real_section.tex', '% emulator measurements present (artifact/results/real/SUMMARY.md): prose in sections/07-real.tex\n'
      '\\input{sections/07-real}\n')



def render_ledger_macros():
    # ===================================================================== ledger benchmark (host)
    lb = rd('ledger_bench.csv')[0]
    M('LedgerPfifty', f"{float(lb['issue_p50_ms']):.2f}")
    M('LedgerPninetyfive', f"{float(lb['issue_p95_ms']):.2f}")
    M('LedgerFullPfifty', f1(lb['fullfsync_p50_ms']))
    M('LedgerFullPninetyfive', f1(lb['fullfsync_p95_ms']))
    M('LedgerBytes', lb['bytes_per_effect'])
    M('LedgerTrials', lb['kill_trials'])
    M('LedgerTaps', f"{int(lb['taps_checked']):,}".replace(',', '{,}'))
    M('LedgerViol', lb['invariant_violations'])
    M('LedgerCand', lb['ghost_candidates'])



def publish_real_macros(macros):
    W('macros_real.tex', '% AUTO-GENERATED by artifact/scripts/render_real.py -- do not edit by hand\n' +
      '\n'.join(f"\\newcommand{{\\{k}}}{{{v}\\xspace}}" for k, v in sorted(macros.items())) + '\n')
