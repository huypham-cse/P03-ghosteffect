# C-01: measured-parameter simulation renderer, invoked by render.py.
# Shared context: RES, OUT, rd, W, M, f1, f2, os.
import glob as _glob

# ================================================================== measured-parameter simulation
_pr = rd('planner_real.csv') if os.path.exists(os.path.join(RES, 'planner_real.csv')) else []
_P = {(r['tag'], r['policy']): r for r in _pr}


def _report_count(tag, column):
    """Read a table-wide count from its rows, rejecting mixed inputs."""
    values = {int(r[column]) for r in _pr if r['tag'] == tag}
    if len(values) != 1:
        raise ValueError('inconsistent reporting count: ' + tag + '/' + column)
    return f'{values.pop():,}'.replace(',', '{,}')


for _tag in {r['tag'] for r in _pr}:
    for _column in ('n', 'ncal'):
        _values = {int(r[_column]) for r in _pr if r['tag'] == _tag}
        if len(_values) > 1:
            raise ValueError('inconsistent reporting count: ' + _tag + '/' + _column)


M('RsimWorkflowN', _report_count('main', 'n'))
M('RsimBaseLabelN', _report_count('main', 'ncal'))
M('RsimFiveLabelN', _report_count('five', 'ncal'))
_fit = {r['family_read']: r for r in rd('real/campaign2/c2_element_families.csv') if r['cell'] == 'ALL'}
_late_names = {'a_indicator_late', 'b_row_late', 'c_digest_late'}
if set(_fit) & _late_names != _late_names:
    raise ValueError('missing measured late family rows')
_late_counts = {(int(_fit[name]['n_reads']), int(_fit[name]['observed']), int(_fit[name]['wrong'])) for name in _late_names}
if len(_late_counts) != 1:
    raise ValueError('inconsistent measured late family counts')
_co = rd('real/campaign2/c2_element_cofailure.csv')
(_late_n, _late_obs, _late_wrong), = _late_counts   # every late family has the same counts: report one family's
M('RsimFitLateWrong', _late_wrong)
M('RsimFitLateObs', _late_obs)
if len({(r['n'], r['both_wrong']) for r in _co}) != 1:
    raise ValueError('inconsistent late cofailure counts')
M('RsimFitCoWrong', _co[0]['both_wrong'])
M('RsimFitCoN', int(_co[0]['n']) - int(_co[0]['both_bot']))   # trials where both late reads were observed
_lab = {'redo': 'redo', 'app-state': 'trust app status', 'rules': 'rules, 10\\,s wait', 'rules-w30-all': 'rules, 30\\,s wait',
        'always-ask': 'always ask', 'g2-only': 'Thm.~\\ref{thm:twohop} only', 'ghost': 'product', 'ghost-src': 'source families',
        'ghost-joint': 'joint'}


def _cells(r):
    return f"{f2(r['dup'])} & {f2(r['loss'])} & {f1(r['ask'])} & {f2(r['cdup'])} ({f2(r['cdup_hi'])})"


def _row(tag, pol, label=None):
    return f"{label or _lab[pol]} & {_cells(_P[(tag, pol)])} \\\\"


_left = [r'\multicolumn{5}{@{}l}{\emph{Element: fault-injected, class-keyed labels (\RsimBaseLabelN{} per class and outcome)}} \\']
_left += [_row('main', p) for p in ('redo', 'app-state', 'rules', 'rules-w30-all', 'g2-only')]
_left += [_row('main', p, '\\alg, ' + _lab[p]) for p in ('ghost', 'ghost-src', 'ghost-joint')]
_left += [r'\multicolumn{5}{@{}l}{\emph{Element, \alg\ with other labels}} \\']
for tag, lab in (('five', r'\RsimFiveLabelN{} per class'), ('passive', 'passive labels')):
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
\caption{\emph{Measured-parameter simulation}: \RsimWorkflowN{} paired workflows per row, calibration and test drawn from one law fitted to Table~\ref{tab:real}. K-9's queued-mail lag $U$(45\,s, 15\,min) is assumed. Tail: \RsimTail\% of committed effects beyond the measured maximum. Always ask on Element: dup/loss \RsimElemAskAllDup/\RsimElemAskAllLoss.}
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
M('RsimTail', f1(100 * float([x for x in rd('real/params.csv') if x['name'] == 'elem_tail_ub'][0]['value'])))

# C-03: retain the adverse results when the two policies see identical inputs.
_matched_lines = []
for _tag, _prefix, _app_label in (
        ('match2k', 'RsimMatchElemTwo', 'Element'),
        ('match5k', 'RsimMatchElemFive', 'Element'),
        ('matchk9', 'RsimMatchKnine', 'K-9'),
        ('matchk9sent', 'RsimMatchKsent', 'K-9 + Sent')):
    _matched = rd('planner_real4_' + _tag + '.csv')
    if len(_matched) != 2 or {r['policy'] for r in _matched} != {'rules-vetted', 'ghost-joint'}:
        raise ValueError('missing or duplicate matched policies: ' + _tag)
    _budgets = {(r['ncal'], r['nlag'], r['keyed'], r['n']) for r in _matched}
    if len(_budgets) != 1 or any(r['tag'] != _tag for r in _matched):
        raise ValueError('matched input metadata disagree: ' + _tag)
    _ncal, _nlag, _, _n = next(iter(_budgets))
    _inttex = lambda x: f'{int(x):,}'.replace(',', '{,}')
    M(_prefix + 'LabelN', _inttex(_ncal))
    M(_prefix + 'LagN', _inttex(_nlag))
    M(_prefix + 'WorkflowN', _inttex(_n))
    for _r in _matched:
        _policy_name = 'Vetted' if _r['policy'] == 'rules-vetted' else 'Joint'
        _pv = 'N/A' if int(_r['n1']) == 0 else f2(_r['cdup'])
        _hi = 'N/A' if int(_r['n1']) == 0 else f2(_r['cdup_hi'])
        M(_prefix + _policy_name + 'Pv', _pv)
        M(_prefix + _policy_name + 'PvHi', _hi)
        M(_prefix + _policy_name + 'Ask', f1(_r['ask']))
        _matched_lines.append(' & '.join([
            _app_label, 'vetted rules' if _policy_name == 'Vetted' else 'joint',
            _inttex(_ncal), _inttex(_nlag), _pv, _hi, f1(_r['ask'])]) + r' \\')
W('tab_matched.tex', r'''\begin{table*}[t]
\centering
\caption{Matched-input, measured-parameter simulation: joint certification and vetted rules use identical records and lag tables per seed (labels per outcome, and per class for Element; lags per class for Element, pooled for K-9). Zero observed errors do not certify vetted rules. Values in \%.}
\label{tab:matched}
\small
\begin{tabular}{@{}llrrrrr@{}}
\toprule
Profile & Policy & Labels & Lags & $P_{\mathrm v}$ & CP hi & Ask \\
\midrule
''' + '\n'.join(_matched_lines) + r'''
\bottomrule
\end{tabular}
\end{table*}
''')


# REAL4 stays separate: this renders the review evidence without rewriting the
# draft to include it. These remain measured-parameter simulations, not new
# emulator/agent measurements.
_four_lines = []
for _path in sorted(_glob.glob(os.path.join(RES, 'planner_real4_*.csv'))):
    _tag = os.path.basename(_path)[len('planner_real4_'):-4]
    _rows = rd(os.path.basename(_path))
    if not _rows:
        raise ValueError('empty REAL4 output: ' + _path)
    for _r in _rows:
        if _r['tag'] != _tag:
            raise ValueError('REAL4 tag/filename mismatch: ' + _path)
        _four_lines.append(' & '.join([
            _tag, _r['app'], _r['policy'], _r['ncal'], _r['nlag'],
            _r['clock'] + '/' + _r['downtime'], f2(_r['cdup']),
            f2(_r['cdup_hi']), f1(_r['ask'])]) + r' \\')
if _four_lines:
    W('tab_real4.tex', r'''\begin{table*}[!htbp]
\centering
\caption{REAL4 sensitivities: measured-parameter simulations, not fresh device or agent runs.
Calibration labels and lag entries are generated; clock/downtime are explicit.
$P_{\mathrm v}$, its CP upper bound and ASK are percentages.}
\label{tab:real4}
\scriptsize
\begin{tabular}{@{}llllllrrr@{}}
\toprule
Case & App & Policy & Labels & Lags & Clock/down(s) & $P_{\mathrm v}$ & CP hi & ASK \\
\midrule
''' + '\n'.join(_four_lines) + r'''
\bottomrule
\end{tabular}
\end{table*}
''')
