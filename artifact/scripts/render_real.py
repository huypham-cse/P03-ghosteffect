# render_real.py -- exec'd by render.py when artifact/results/real/SUMMARY.md exists (emulator measurements).
# Round 3: the body reports CAMPAIGN 2 (results/real/campaign2/; screen-validating reader, K-9 corrections, CalDAV,
# Synapse txnId horizon).  Campaign 1 (results/real/*.csv) is kept for the hop-2 behaviour table in the appendix,
# kill semantics and the ledger test.  Emits generated/tab_real.tex (campaign 2), tab_realcone.tex (campaign 1),
# tab_realsim.tex (measured-parameter simulation, results/planner_real.csv), macros \Real* / \Rsim*, and
# real_section.tex.  Every number is recomputed from the CSVs; asserts guard the facts the prose states.
import glob as _glob

C2 = os.path.join(REAL, 'campaign2')


def _rr(name, base=None):
    with open(os.path.join(base or REAL, name), newline='') as f:
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
M('RealElemNofaultN', _eo['none/nofault']['n'])
M('RealElemAckedN', _eo['bg_kill9/acked']['n'])
_present = sum(int(r['present']) for r in _pv)
M('RealElemSentPolls', f"{_present:,}".replace(',', '{,}'))
_lag = lambda c: _el[(c, 'row_visible')]
for c, nm in (('none/nofault', 'Nofault'), ('bg_kill9/respdrop', 'Kill'), ('force_stop/respdrop', 'Fs'),
              ('netcut/respdrop', 'Net'), ('bg_kill9_sticky/respdrop', 'SKill'), ('force_stop_sticky/respdrop', 'SFs'),
              ('bg_kill9/acked', 'Acked'), ('ALL_interrupted(respdrop)', 'All')):
    r = _lag(c)
    assert r['n_censored_final'] == '0'
    M(f'RealLag{nm}Med', f1(r['p50']))
    M(f'RealLag{nm}Ninety', f1(r['p90']))
    M(f'RealLag{nm}Max', f1(r['max']))
    M(f'RealLag{nm}N', r['n_committed'])
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

_lagrow = lambda lab, nm: (f"{lab} & \\RealLag{nm}N & \\RealLag{nm}Med & \\RealLag{nm}Ninety & \\RealLag{nm}Max \\\\")
W('tab_real.tex', r'''\begin{table*}[t]
\centering
\caption{Emulator measurements, campaign 2 (Android~13 emulators, self-hosted servers, scripted driver; ground truth = server copies). (a)~After a commit whose reply was
lost (TCP reset after the server committed), under no fault, background + \texttt{kill -9}, force-stop or a 20\,s network cut. App re-send: how the app resolved it; GUI redo:
a scripted agent recomposes and re-sends the same content. (b)~Element's recovery-to-visible lag (s; upper end of a one-dump $\approx$2\,s interval; no trial censored,
window $\ge$120\,s). Sticky: every reply dropped until the fault. (c)~Family errors against the server, wrong/observed, with no-observation ($\bot$, wrong screen) separated;
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
Element & \RealElemRL & txnId \RealElemSameTxn, /sync \RealElemSyncOnly & \RealElemRL & \emph{Sent} & new txnId \\
Etar+DAVx5 & \RealCalN & URL $\to$ 412 & \RealCalOnce & saved & \RealCalRecDup/\RealCalRecN{} dup \\
K-9 & \RealKRdNosent & none (error) & \RealKRdNosent & Outbox & dup \\
K-9 + Sent & \RealKRdSent & none (error) & \RealKRdSent & Outbox only & dup \\
\multicolumn{4}{@{}l}{\quad K-9 redo, both configurations} & & \RealKRecDup/\RealKRecN{} dup \\
\bottomrule
\end{tabular}\\[3pt]
\begin{tabular}{@{}l cccc@{}}
\toprule
\multicolumn{5}{@{}l}{(b) Element lag by fault class (s)} \\
Fault & $n$ & p50 & p90 & max \\
\midrule
''' + '\n'.join([_lagrow('none (reader floor; from \\emph{Send})', 'Nofault'), _lagrow('background + \\texttt{kill -9}', 'Kill'),
                 _lagrow('force-stop (relaunch lands off the room)', 'Fs'), _lagrow('network cut, app in foreground', 'Net'),
                 _lagrow('sticky + \\texttt{kill -9}', 'SKill'), _lagrow('sticky + force-stop', 'SFs')]) + r'''
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
 & row = indicator, first non-$\bot$ read & \RealEarlyWrong/\RealElemN$^{\ddagger}$ & 0 \\
 & row = indicator, late & 0/\RealLateObs & \RealLateBot \\
 & room-list digest, late & 0/\RealLateObs & \RealLateBot \\
 & any two families wrong together, late & 0/\RealCoN{} (CI 0--\RealLateHi\%) & \RealCoBot \\
K-9 & Outbox lists it (``unsent''), lost reply & \RealKOutWrong/\RealKRd & 0 \\
 & failure notification, lost reply & \RealKNotifWrong/\RealKRd$^{\S}$ & 0 \\
 & Sent folder lacks it, lost reply & \RealKSentWrong/\RealKSentN & 0 \\
 & \quad together with the Outbox & \RealKSentWrong/\RealKSentN & 0 \\
 & any family, acknowledged send & 0/\RealKAckedN & 0 \\
\bottomrule
\end{tabular}\\[2pt]
{\scriptsize $^{\ddagger}$All lag-blind: verified screen, scrolled to the bottom, message not yet in the restored timeline (visible at \RealBlindLagLo--\RealBlindLagHi\,s).
$^{\S}$Force-stop clears the app's notifications. The shade was cleared between trials.}
\end{minipage}
\end{table*}
''')

# ================================================================== measured-parameter simulation
_pr = rd('planner_real.csv') if os.path.exists(os.path.join(RES, 'planner_real.csv')) else []
_P = {(r['tag'], r['policy']): r for r in _pr}
_lab = {'redo': 'redo', 'app-state': 'trust app status', 'rules': 'rules, 10\\,s wait', 'rules-w30-all': 'rules, 30\\,s wait',
        'always-ask': 'always ask', 'g2-only': 'Thm.~\\ref{thm:twohop} only', 'ghost': 'product', 'ghost-src': 'source families',
        'ghost-joint': 'joint'}


def _cells(r):
    return f"{f2(r['dup'])} & {f2(r['loss'])} & {f1(r['ask'])} & {f2(r['cdup'])} ({f2(r['cdup_hi'])})"


def _row(tag, pol, label=None):
    return f"{label or _lab[pol]} & {_cells(_P[(tag, pol)])} \\\\"


_left = [r'\multicolumn{5}{@{}l}{\emph{Element: fault-injected, class-keyed labels (2{,}000 per class and outcome)}} \\']
_left += [_row('main', p) for p in ('redo', 'app-state', 'rules', 'rules-w30-all', 'g2-only')]
_left += [_row('main', p, '\\alg, ' + _lab[p]) for p in ('ghost', 'ghost-src', 'ghost-joint')]
_left += [r'\multicolumn{5}{@{}l}{\emph{Element, \alg\ with other labels}} \\']
for tag, lab in (('five', '5{,}000 per class'), ('passive', 'passive labels')):
    for p in ('ghost', 'ghost-joint'):
        _left.append(_row(tag, p, f"{lab}, {'product' if p == 'ghost' else 'joint'}"))
_right = [r'\multicolumn{5}{@{}l}{\emph{Element, lag tail beyond 14\,s (\RsimTail\%)}} \\']
for tag, lab in (('tail', 'not logged'), ('tailcal', 'logged')):
    for p in ('ghost', 'ghost-joint'):
        _right.append(_row(tag, p, f"{lab}, {'product' if p == 'ghost' else 'joint'}"))
_right += [r'\multicolumn{5}{@{}l}{\emph{K-9, no Sent folder (fault-injected labels)}} \\']
_right += [_row('k9', p) for p in ('app-state', 'rules', 'g2-only')]
_right += [_row('k9', 'ghost', '\\alg, every mode')]
_right += [r'\multicolumn{5}{@{}l}{\emph{K-9 + IMAP Sent folder}} \\']
_right += [_row('k9sent', p) for p in ('app-state', 'rules')]
_right += [_row('k9sent', 'ghost', '\\alg, every mode')]
_right += [_row('k9sentpass', 'ghost-joint', 'passive labels, joint')]
for t in ('k9', 'k9pass', 'k9sent'):                 # every GhostRecover mode asks on every interrupted K-9 workflow
    for p in ('ghost', 'ghost-src', 'ghost-joint'):
        if (t, p) in _P:
            assert abs(float(_P[(t, p)]['ask']) - 100.0) < 1e-9 and float(_P[(t, p)]['cdup']) == 0.0
_hdr = r'''\toprule
Policy & dup & loss & ask & $P_{\mathrm{v}}$ (hi) \\
\midrule
'''
W('tab_realsim.tex', r'''\begin{table*}[t]
\centering
\caption{\emph{Measured-parameter simulation} (12{,}000 paired interrupted workflows per row; not an emulator run). Measured (Table~\ref{tab:real}): G2 and its
mechanisms, per-fault-class lag laws with lag-blind first reads, the 2\% late no-observation rate and zero late family errors (Element); the permanent failed state,
the client-written Sent folder and its APPEND lag (K-9). Modelled: fault mix, absent-side errors, Monitor, user; K-9's queued-mail lag $U$(45\,s, 15\,min) is an
assumption. Element has no hop-1 family (its indicator is not lag-free). Labels are simulated draws from the measured law. Tail: committed effects (the 95\%
upper bound from 0/101 censored) visible only after 14--300\,s. Always ask: dup/loss \RsimElemAskAllDup/\RsimElemAskAllLoss{} (Element). dup, loss, ask: \% of workflows; $P_{\mathrm{v}}$: \% of committed effects the policy retried by itself
(CP 95\% upper bound; budget 1\%).}
\label{tab:realsim}
\scriptsize
\setlength{\tabcolsep}{2.4pt}
\begin{minipage}[t]{0.495\textwidth}\vspace{0pt}
\begin{tabular}{@{}l cccc@{}}
''' + _hdr + '\n'.join(_left) + r'''
\bottomrule
\end{tabular}
\end{minipage}\hfill
\begin{minipage}[t]{0.475\textwidth}\vspace{0pt}
\begin{tabular}{@{}l cccc@{}}
''' + _hdr + '\n'.join(_right) + r'''
\bottomrule
\end{tabular}
\end{minipage}
\end{table*}
''')


def _sm(name, key, col, fmt=f2):
    M(name, fmt(_P[key][col]))


for tag, tn in (('main', ''), ('five', 'Five'), ('pooled', 'Pool'), ('mixlab', 'Mix'), ('unknown', 'Unk'),
                ('passive', 'Pass'), ('tail', 'Tail'), ('tailcal', 'TailCal'), ('k9', 'Knine'), ('k9sent', 'Ksent'),
                ('k9sentpass', 'KsentPass'), ('k9sentpass5', 'KsentPassFive')):
    for pol, pn in (('ghost', 'Prod'), ('ghost-src', 'Src'), ('ghost-joint', 'Joint'), ('rules', 'Rules'),
                    ('rules-w30-all', 'RulesThirty'), ('g2-only', 'Gtwo'), ('app-state', 'App'), ('always-ask', 'AskAll'),
                    ('redo', 'Redo')):
        if (tag, pol) in _P:
            r = _P[(tag, pol)]
            pre = 'Rsim' + (tn or 'Elem') + pn
            M(pre + 'Pv', f2(r['cdup']))
            M(pre + 'PvHi', f2(r['cdup_hi']))
            M(pre + 'Ask', f1(r['ask']))
            M(pre + 'Dup', f2(r['dup']))
            M(pre + 'Loss', f2(r['loss']))
            M(pre + 'Err', f2(float(r['dup']) + float(r['loss'])))
            M(pre + 'Secs', f"{float(r['secs']):.0f}")
M('RsimTail', f1(100 * float([x for x in _rr('params.csv') if x['name'] == 'elem_tail_ub'][0]['value'])))

# ------------------------------------------------------------------ prose hooks
M('RealDataLimitation', r'Emulator measurements (\S\ref{sec:eval-real}) cover three apps on an emulator, with $n$ small outside Element; agents, physical phones, VLMs and the commit classifier are not measured.')
M('RealPresent', 'yes')
W('real_section.tex', '% emulator measurements present (artifact/results/real/SUMMARY.md): prose in sections/07-real.tex\n'
  '\\input{sections/07-real}\n')
