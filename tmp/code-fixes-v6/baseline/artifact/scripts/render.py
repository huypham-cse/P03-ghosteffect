#!/usr/bin/env python3
"""render.py -- paper == artifact.  CSV (artifact/results) -> manuscript/generated/.

Emits booktabs tables (tab_*.tex), pgfplots figures with inline coordinates (fig_*.tex) and macros.tex
(one \\newcommand per inline number).  Nothing here is hand-typed data: every number comes from a CSV
written by a seeded script (or, for the ledger benchmark, a host measurement).
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
OUT = os.path.join(HERE, '..', '..', 'manuscript', 'generated')
os.makedirs(OUT, exist_ok=True)
for fn in os.listdir(OUT):                     # stale fragments must not survive a regeneration
    if fn.endswith('.tex'):
        os.remove(os.path.join(OUT, fn))
MACROS = {}


def rd(name):
    with open(os.path.join(RES, name), newline='') as f:
        return list(csv.DictReader(f))


def W(name, text):
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(text)


def M(name, val):
    MACROS[name] = val


def sci(x, d=1):
    x = float(x)
    if x == 0:
        return '\\ensuremath{0}'
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    if round(m, d) >= 10:
        m /= 10
        e += 1
    if -2 <= e <= 0 and x >= 0.01:
        return f'\\ensuremath{{{x:.{max(d + 1, 2)}f}}}' if x < 0.1 else f'\\ensuremath{{{x:.2f}}}'
    return f'\\ensuremath{{{m:.{d}f}{{\\times}}10^{{{e}}}}}'


def _half_up(x, d):
    """Round half up on the decimal text of x (R1 round-4 m2: one rounding rule, e.g. 11.95 -> 12.0)."""
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))


def f1(x):
    return _half_up(x, 1)


def f2(x):
    return _half_up(x, 2)


def alpha_tex(a):
    return f'$10^{{{int(round(math.log10(float(a))))}}}$'


def dur(s):
    s = float(s)
    if s == float('inf') or s != s:
        return '--'
    if s < 120:
        return f'{s:.0f}\\,s'
    if s < 7200:
        return f'{s / 60:.0f}\\,min'
    return f'{s / 3600:.1f}\\,h'


# ===================================================================== Thm 4.1 sanity checks (SPRT)
sp = rd('sprt_validation.csv')
lines = []
for r in sp:
    lines.append(' & '.join([f"{float(r['eps']):.2f}", alpha_tex(r['alpha']), sci(r['exact_dup']), sci(r['mc_dup_hi']),
                             f2(r['exact_EN']), f2(r['mc_EN']), f2(r['lb_EN']), f2(r['ub_EN'])]) + r' \\')
W('tab_sprt.tex', r'''\begin{table}[!htbp]
\centering
\caption{Implementation sanity check of Theorem~\ref{thm:main}(a,c) for an i.i.d.\ binary probe ($\epsilon_0{=}\epsilon_1{=}\epsilon$, $\beta{=}\alpha$), all 24 cells.
Exact DTMC values; ``MC hi'': one-sided 95\% Clopper--Pearson upper bound on $P(\mathrm{dup}\mid X{=}1)$ from 40{,}000 committed-world episodes;
$\bar N$: mean reads at $\pi{=}\tfrac12$, exact and MC; LB/UB: bounds~\eqref{eq:lb}/\eqref{eq:ub} averaged over the two outcomes.
At $\alpha{=}10^{-4}$, 40{,}000 episodes cannot confirm the budget by MC (zero events give an upper bound of $9.2{\times}10^{-5}$); the exact column does.}
\label{tab:sprt}
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}cc cc cccc@{}}
\toprule
$\epsilon$ & $\alpha$ & $P(\mathrm{dup})$ & MC hi & $\bar N$ & $\bar N_{\mathrm{MC}}$ & LB & UB \\
\midrule
''' + '\n'.join(lines) + r'''
\bottomrule
\end{tabular}
\end{table}
''')
ok = all(float(r['exact_dup']) <= float(r['alpha']) and float(r['exact_loss']) <= float(r['beta']) for r in sp)
M('SprtCells', str(len(sp)))
M('SprtAllWithin', 'all' if ok else 'NOT all')
M('SprtRatioMax', f"{max(float(r['exact_EN']) / float(r['lb_EN']) for r in sp if float(r['alpha']) <= 1e-3):.2f}")
M('SprtGapMax', f"{max(float(r['exact_EN']) - float(r['lb_EN']) for r in sp):.1f}")
M('SprtMCN', f"{int(sp[0]['n_mc']):,}".replace(',', '{,}'))
g = lambda e, a: [r for r in sp if float(r['eps']) == e and float(r['alpha']) == a][0]
M('SprtENfive', f1(g(0.05, 1e-3)['exact_EN']))
M('SprtENthirty', f1(g(0.30, 1e-3)['exact_EN']))
M('SprtMCdev', f"{max(abs(float(r['mc_EN']) - float(r['exact_EN'])) for r in sp):.2f}")
slack = sorted(float(r['alpha']) / max(float(r['exact_dup']), 1e-300) for r in sp)
M('SprtSlackMax', f"{slack[-1]:.0f}")
M('SprtSlackMed', f"{slack[len(slack) // 2]:.1f}")

cols = {0.05: 'blue!70!black', 0.15: 'orange!85!black', 0.30: 'red!70!black'}
plots = []
for e, c in cols.items():
    pts = ' '.join(f"({-math.log10(float(r['alpha'])):.0f},{float(r['exact_EN']):.3f})" for r in sp if float(r['eps']) == e)
    lb = ' '.join(f"({-math.log10(float(r['alpha'])):.0f},{float(r['lb_EN']):.3f})" for r in sp if float(r['eps']) == e)
    plots.append(f"\\addplot[color={c},mark=*,mark size=1.6pt,thick] coordinates {{{pts}}};\n\\addlegendentry{{$\\epsilon{{=}}{e:.2f}$}}\n"
                 f"\\addplot[color={c},dashed,thick,forget plot] coordinates {{{lb}}};")
W('fig_sprt.tex', r'''\begin{figure}[!htbp]
\centering
\begin{tikzpicture}
\begin{axis}[width=\linewidth,height=3.9cm,xlabel={$\log_{10}(1/\alpha)$ \ ($\beta{=}\alpha$)},
  ylabel={mean reads $\bar N$},xtick={1,2,3,4},ymin=0,
  legend style={at={(0.02,0.98)},anchor=north west,font=\footnotesize,draw=none,fill=none},
  ymajorgrids,grid style={dashed,gray!30},tick label style={font=\footnotesize},label style={font=\footnotesize}]
''' + '\n'.join(plots) + r'''
\end{axis}
\end{tikzpicture}
\caption{The price of a duplicate budget for an i.i.d.\ probe (exact). Solid: SPRT; dashed: lower bound~\eqref{eq:lb}.
Cost grows as $\log(1/\alpha)/\mathrm{KL}$; the gap is at most ''' + MACROS['SprtGapMax'] + r''' reads over all 24 cells (Table~\ref{tab:sprt}).}
\label{fig:sprt}
\end{figure}
''')

# ===================================================================== calibration (Lemma 4.6(i))
cal = rd('calibration.csv')
lines = []
for n in ['25', '50', '100', '200', '400']:
    rr = {r['mode']: r for r in cal if r['n_cal'] == n}
    lines.append(f"{n} & " + ' & '.join(f"{100 * float(rr[m]['viol']):.1f} & {float(rr[m]['EN']):.1f}"
                                        for m in ['plugin', 'cp-upper', 'cp-strict']) + r' \\')
W('tab_calib.tex', r'''\begin{table}[!htbp]
\centering
\caption{Calibration of an i.i.d.\ binary probe (Lemma~\ref{lem:calib}(i)): share of probe types (\%) whose exact $P(\mathrm{dup}\mid X{=}1)$ or
$P(\mathrm{loss}\mid X{=}0)$ exceeds $\alpha{=}\beta{=}0.01$, and mean reads, over 200 probe types $\times$ 5 seeds, $\epsilon_0{\in}[0.06,0.26]$,
$\epsilon_1{\in}[0.04,0.20]$. CP: one-sided Clopper--Pearson upper bounds at confidence $1{-}\delta$.}
\label{tab:calib}
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\begin{tabular}{@{}r cc cc cc@{}}
\toprule
 & \multicolumn{2}{c}{Plug-in} & \multicolumn{2}{c}{CP, $\delta{=}0.05$} & \multicolumn{2}{c}{CP, $\delta{=}\alpha/20$} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(l){6-7}
$n_{\mathrm{cal}}$ & viol. & $\bar N$ & viol. & $\bar N$ & viol. & $\bar N$ \\
\midrule
''' + '\n'.join(lines) + r'''
\bottomrule
\end{tabular}
\end{table}
''')
gc = lambda n, m, k: float([r for r in cal if r['n_cal'] == n and r['mode'] == m][0][k])
M('CalNomViol', f"{100 * gc('100', 'nominal', 'viol'):.0f}")
M('CalPlugViolLo', f"{100 * gc('400', 'plugin', 'viol'):.0f}")
M('CalPlugViolHi', f"{100 * gc('25', 'plugin', 'viol'):.0f}")
M('CalCPViolMax', f"{max(100 * float(r['viol']) for r in cal if r['mode'] == 'cp-upper'):.1f}")
M('CalStrictViolMax', f"{max(100 * float(r['viol']) for r in cal if r['mode'] == 'cp-strict'):.1f}")
M('CalCPWorst', f"{100 * gc('100', 'cp-upper', 'worst'):.2f}")
M('CalStrictWorst', f"{max(100 * float(r['worst']) for r in cal if r['mode'] == 'cp-strict'):.2f}")
M('CalCPENhundred', f1(gc('100', 'cp-upper', 'EN')))
M('CalStrictENhundred', f1(gc('100', 'cp-strict', 'EN')))
M('CalPlugENhundred', f1(gc('100', 'plugin', 'EN')))

# ===================================================================== correlated reads
cor = rd('correlation.csv')
C = {(r['scenario'], float(r['rho'])): r for r in cor}
lines = []
for rho in [0.0, 0.2, 0.6, 1.0]:
    a, b = C[('within', rho)], C[('cross', rho)]
    p = lambda r, k: f"{100 * float(r[k]):.2f}"
    lines.append(f"{rho:.1f} & {p(a, 'v1-naive_dup')} & {p(a, 'v1_dup')} & {p(a, 'v2-view_dup')} & "
                 f"{p(b, 'v1_dup')} & {p(b, 'v2-view_dup')} & {p(b, 'v2-cert_dup')} ({100 * float(b['v2-cert_ask']):.0f}) & "
                 f"{100 * float(b['bound_all_wrong']):.1f}" + r' \\')
W('tab_corr.tex', r'''\begin{table}[!htbp]
\centering
\caption{Correlated reads (model-based simulation; VLM family with 3 views, $\epsilon{=}0.10$, $\alpha{=}1\%$, 30{,}000 committed effects per cell):
$P(\mathrm{dup}\mid X{=}1)$ in \%. \emph{Within-view}: re-reads of a view share one error with probability $\rho$.
\emph{Cross-view}: views share a latent error rate with intraclass correlation $\rho$. naive: SPRT re-reading one view; re-read: our earlier design
(re-reads of rotated views, AR(1) shrinkage); view: one read per view, SPRT over views (assumes independent views); certified: family verdict with calibrated bound (Prop.~\ref{prop:family}),
escalations (\%) in parentheses; bound: Lemma~\ref{lem:floor}, worst case of all 3 views wrong.}
\label{tab:corr}
\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}c ccc cccc@{}}
\toprule
 & \multicolumn{3}{c}{Within-view $\rho$} & \multicolumn{4}{c}{Cross-view $\rho$} \\
\cmidrule(lr){2-4}\cmidrule(l){5-8}
$\rho$ & naive & re-read & view & re-read & view & certified & bound \\
\midrule
''' + '\n'.join(lines) + r'''
\bottomrule
\end{tabular}
\end{table}
''')
M('CorrNaiveOne', f1(100 * float(C[('within', 1.0)]['v1-naive_dup'])))
M('CorrVoneSix', f2(100 * float(C[('within', 0.6)]['v1_dup'])))
M('CorrVoneEight', f2(100 * float(C[('within', 0.8)]['v1_dup'])))
M('CorrVoneOne', f2(100 * float(C[('within', 1.0)]['v1_dup'])))
M('CorrViewWithinMax', f2(max(100 * float(C[('within', r)]['v2-view_dup_hi']) for r in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])))
M('CorrViewAsk', f"{100 * float(C[('within', 0.0)]['v2-view_ask']):.0f}")
M('CorrViewCrossTwo', f2(100 * float(C[('cross', 0.2)]['v2-view_dup'])))
M('CorrViewCrossOne', f1(100 * float(C[('cross', 1.0)]['v2-view_dup'])))
M('CorrCertMaxHi', f2(max(100 * float(r['v2-cert_dup_hi']) for r in cor)))

# ===================================================================== floor (appendix figure) and lag waits
imp, bf = rd('impossibility.csv'), rd('bayes_floor.csv')
plots = []
styles = {'n0': ('black', 'very thick', '$n{=}0$'), 'n1': ('red!70!black', 'thick', '$n{=}1$'),
          'n3': ('orange!85!black', 'thick', '$n{=}3$'), 'n9': ('blue!70!black', 'thick', '$n{=}9$')}
for key, (c, th, lab) in styles.items():
    pts = ' '.join(f"({float(r['pi']):.2f},{float(r[key]):.4f})" for r in bf)
    plots.append(f"\\addplot[color={c},{th}] coordinates {{{pts}}};\n\\addlegendentry{{{lab}}}")
for pol, mk in [('single-read', 'triangle*'), ('majority-of-5', 'square*'), ('fooled-SPRT', 'diamond*')]:
    pts = ' '.join(f"({float(r['pi']):.2f},{float(r[pol]):.4f})" for r in imp)
    plots.append(f"\\addplot[only marks,mark={mk},mark size=1.6pt,gray!70!black] coordinates {{{pts}}};\n\\addlegendentry{{{pol} (MC)}}")
W('fig_floor.tex', r'''\begin{figure}[!htbp]
\centering
\begin{tikzpicture}
\begin{axis}[width=\linewidth,height=4.5cm,xlabel={prior $\pi=P(\text{committed})$},ylabel={min $P(\mathrm{dup}){+}P(\mathrm{loss})$},
  ymin=0,ymax=0.9,xmin=0.05,xmax=0.95,legend columns=2,
  legend style={at={(0.5,1.02)},anchor=south,font=\footnotesize,draw=none,fill=none},
  ymajorgrids,grid style={dashed,gray!30},tick label style={font=\footnotesize},label style={font=\footnotesize}]
''' + '\n'.join(plots) + r'''
\end{axis}
\end{tikzpicture}
\caption{Sanity check of Theorem~\ref{thm:main}(d). Lines: exact Bayes floor $\mathbb{E}[\min(\pi_n,1{-}\pi_n)]$ after $n$ reads of an
informative probe ($\epsilon{=}0.3$). Markers: policies against an \emph{uninformative} probe (20{,}000 episodes each); none goes below $n{=}0$.}
\label{fig:floor}
\end{figure}
''')
viol = sum(1 for r in imp for p in ['always-retry', 'never-retry', 'coin(0.5)', 'single-read', 'majority-of-5', 'fooled-SPRT']
           if float(r[p]) < float(r['floor']) - 0.012)
M('ImpViol', str(viol))

lw = rd('lag_wait.csv')
tails = []
for r in lw:
    if r['tail'] not in tails:
        tails.append(r['tail'])
lines = []
short = {'lognormal, median 1.5 s, sigma 0.6': 'lognormal, 1.5\\,s, $\\sigma{=}0.6$',
         'lognormal, median 3 s, sigma 1.2': 'lognormal, 3\\,s, $\\sigma{=}1.2$',
         'Pareto, x_m 1 s, shape 3': 'Pareto, 1\\,s, $\\kappa{=}3$', 'Pareto, x_m 2 s, shape 1.1': 'Pareto, 2\\,s, $\\kappa{=}1.1$'}
L = {(r['tail'], float(r['alpha_lag'])): r for r in lw}
for t in tails:
    lines.append(short[t] + ' & ' + ' & '.join(f"{dur(L[(t, a)]['exact_wait'])} & {dur(L[(t, a)]['certified_wait'])}"
                                                for a in [1e-2, 1e-3]) + r' \\')
W('tab_lag.tex', r'''\begin{table}[!htbp]
\centering
\caption{Wait needed so that the lag tail uses at most $\alpha_{\mathrm{lag}}$ of the duplicate budget (Theorem~\ref{thm:main}(a,b)):
exact quantile $G^{-1}(\alpha_{\mathrm{lag}})$ and the wait certified from 20{,}000 logged commit-to-visibility times
(one-sided CP, $\delta{=}10^{-4}$). Median and shape of $T$ given per row; ``--'': not certifiable with 20{,}000 samples ($\alpha_{\mathrm{lag}}{=}10^{-4}$ never is).}
\label{tab:lag}
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}l cc cc@{}}
\toprule
 & \multicolumn{2}{c}{$\alpha_{\mathrm{lag}}{=}10^{-2}$} & \multicolumn{2}{c}{$\alpha_{\mathrm{lag}}{=}10^{-3}$} \\
\cmidrule(lr){2-3}\cmidrule(l){4-5}
Lag $T$ & exact & certified & exact & certified \\
\midrule
''' + '\n'.join(lines) + r'''
\bottomrule
\end{tabular}
\end{table}
''')
par = 'Pareto, x_m 2 s, shape 1.1'
M('LagParetoTwo', dur(L[(par, 1e-2)]['certified_wait']))
M('LagParetoThree', dur(L[(par, 1e-3)]['certified_wait']))
M('LagLogThree', dur(L[('lognormal, median 1.5 s, sigma 0.6', 1e-3)]['certified_wait']))

# ===================================================================== saga (appendix table + macros)
sg, mx = rd('saga_alloc.csv'), rd('saga_mixed.csv')
lines = [f"{r['k']} & {f1(r['obs_uni'])} & {f1(r['obs_opt'])} & {f2(r['saving_pct'])} & {f2(r['pred_saving_pct'])} & "
         f"{100 * float(r['frac_worse']):.0f} & {100 * float(r['max_e2e_dup']):.2f} & {100 * float(r['naive_e2e_dup_max']):.1f}" + r' \\'
         for r in sg]
W('tab_saga.tex', r'''\begin{table}[!htbp]
\centering
\caption{Saga budget allocation (Proposition~\ref{prop:saga}), $\alpha{=}\beta{=}0.01$, 200 random i.i.d.-probe workflows per $k$ (exact DP).
Mean reads under uniform and KKT splits, mean saving (\%) measured and predicted, share of workflows (\%) where KKT is \emph{worse} than uniform in
exact cost, worst end-to-end $P(\mathrm{dup})$ (\%) with KKT, and with every step given the full $\alpha$.}
\label{tab:saga}
\footnotesize
\setlength{\tabcolsep}{2.6pt}
\begin{tabular}{@{}r cc cc c cc@{}}
\toprule
$k$ & uniform & KKT & saving & pred. & worse & e2e dup & full-$\alpha$ \\
\midrule
''' + '\n'.join(lines) + r'''
\bottomrule
\end{tabular}
\end{table}
''')
S8 = [r for r in sg if r['k'] == '8'][0]
S16 = [r for r in sg if r['k'] == '16'][0]
S2 = [r for r in sg if r['k'] == '2'][0]
M('SagaSaveEight', f1(S8['saving_pct']))
M('SagaPredEight', f1(S8['pred_saving_pct']))
M('SagaNaiveSixteen', f1(100 * float(S16['naive_e2e_dup_max'])))
M('SagaMaxDup', f2(max(100 * float(r['max_e2e_dup']) for r in sg)))
M('SagaWorseTwo', f"{100 * float(S2['frac_worse']):.0f}")
M('SagaWorseSixteen', f"{100 * float(S16['frac_worse']):.0f}")
M('SagaMixSave', f1([r for r in mx if r['k'] == '8'][0]['saving_pct']))
M('SagaMixMaxFour', f"{float([r for r in mx if r['k'] == '4'][0]['saving_max']):.0f}")
M('SagaMixMaxEight', f"{float([r for r in mx if r['k'] == '8'][0]['saving_max']):.0f}")

# ===================================================================== nonce
nc, nb = rd('nonce.csv'), rd('nonce_before.csv')[0]
lines = [r"VLM, no look-alike & -- & 0.12 & 0.08 & " + f2(nb['vlm_D0']) + f" & {f1(nb['vlm_EN'])}" + r' \\',
         r"VLM, look-alike & -- & \multicolumn{2}{c}{uninformative} & 0 & $\infty$ \\", r'\midrule']
for r in nc:
    if r['ec'] in ('0.02', '0.05'):
        lines.append(f"nonce $k{{=}}{r['k']}$, $t{{=}}{r['t']}$ & {float(r['ec']) * 100:.0f}\\% & {sci(r['eps0_analytic'])} & "
                     f"{float(r['eps1_analytic']):.3f} ({float(r['eps1_mc']):.3f}) & {f2(r['D0'])} & {f1(r['EN'])}" + r' \\')
W('tab_nonce.tex', r'''\begin{table}[!htbp]
\centering
\caption{Content-carried nonce (Lemma~\ref{lem:nonce}; simulated OCR with substitutions, insertions and deletions; edit-distance matching).
OCR symbol error $e_c$; false-match bound $\epsilon_0$; miss rate $\epsilon_1$ analytic bound (MC, 40{,}000 screens), of which $\eta{=}1\%$
is a \emph{persistent} hidden field; $\mathrm{KL}(p_0\|p_1)$; mean reads at $\alpha{=}\beta{=}10^{-3}$ \emph{if} re-reads were independent.
With persistent misses no number of nonce reads certifies ``absent'' below $\eta$ (Lemma~\ref{lem:floor}).}
\label{tab:nonce}
\footnotesize
\setlength{\tabcolsep}{2.4pt}
\begin{tabular}{@{}l c c c c c@{}}
\toprule
Probe & $e_c$ & $\epsilon_0$ & $\epsilon_1$ & KL$_0$ & $\bar N$ \\
\midrule
''' + '\n'.join(lines) + r'''
\bottomrule
\end{tabular}
\end{table}
''')
n61 = [r for r in nc if r['k'] == '6' and r['t'] == '1' and r['ec'] == '0.02'][0]
M('NonceEpsOne', f"{float(n61['eps1_analytic']):.3f}")
M('NonceEpsZero', sci(n61['eps0_analytic']))
M('NonceEN', f1(n61['EN']))
M('VlmEN', f1(nb['vlm_EN']))

# ===================================================================== planner simulation
ps = rd('planner_sim.csv')
P = {r['policy']: r for r in ps}
names = {'redo': 'Redo (AgentProg-style)', 'ckpt': 'Checkpoint-resume', 'atomix': 'Atomix-style, in-memory',
         'atomix-durable': 'Atomix-style, durable log', 'verify': 'Verify-before-retry', 'key': 'Ledger + key',
         'key-ask': 'Ledger + key + ask (look-alike)', 'always-ask': 'Ledger + always ask', 'nonce-ask': 'Ledger + nonce + ask',
         'maj3-ask': 'Ledger + 3 VLM views + ask', 'rules': 'Same evidence, rules (all agree)',
         'rules-lenient': 'Same evidence, rules (lenient)', 'ghost-v1': 'Re-read SPRT (earlier design)',
         'ghost': r'\textbf{GhostEffect} (product, A2)', 'ghost-src': r'\textbf{GhostEffect} (source families)',
         'ghost-joint': r'\textbf{GhostEffect} (joint, no A2)',
         'ghost-nononce': '\\quad $-$ nonce', 'ghost-nohop1': '\\quad $-$ hop-1 probe',
         'ghost-nodigest': '\\quad $-$ digest probe', 'ghost-nocal': '\\quad $-$ calibration (nominal i.i.d.)',
         'ghost-uniform': '\\quad uniform $\\alpha$ split', 'ghost-noask': '\\quad declare when uncertified (no ask)',
         'ghost-visible': '\\quad $+$ visible-nonce opt-in', 'g2-only': 'Ledger + Thm.~\\ref{thm:twohop} only'}


def prow(r):
    return (f"{names[r['policy']]} & {f2(r['dup'])} & {f2(r['loss'])} & {f1(r['ask'])} & {f2(r['cdup'])} & {float(r['secs']):.0f}" + r' \\')


order_b = ['redo', 'ckpt', 'atomix', 'atomix-durable', 'verify', 'key', 'key-ask', 'nonce-ask', 'maj3-ask', 'always-ask', 'g2-only', 'ghost-v1',
           'rules', 'rules-lenient', 'ghost', 'ghost-src', 'ghost-joint']
order_a = ['ghost-nononce', 'ghost-nohop1', 'ghost-nodigest', 'ghost-nocal', 'ghost-uniform', 'ghost-noask', 'ghost-visible']
hw = max(max(float(P[p]['dup_hi']) - float(P[p]['dup']), float(P[p]['dup']) - float(P[p]['dup_lo'])) for p in P)
M('SimHalfWidth', f1(hw))
W('tab_planner.tex', r"""\begin{table}[t]
\centering
\caption{Model-based simulation: 12{,}000 paired interrupted workflows (5 seeds $\times$ 2{,}400), $\alpha{=}\beta{=}1\%$ per workflow, default
world (persistent nonce misses, within-view VLM correlation 0.6, cross-view 0.1, fallible Monitor, user wrong on 5\% of asks, 10\% with a look-alike), 2{,}000
calibration effects per app and outcome. dup/loss: \% of workflows with a duplicate/loss from any cause, including wrong user answers; ask: \% of workflows escalated;
$P_{\mathrm{v}}$: \% of committed effects retried by the planner's own decision (the guaranteed quantity, budget 1\%); s: blocking recovery
seconds per workflow (60\,s per ask). All 95\% Clopper--Pearson half-widths $\le$""" + MACROS['SimHalfWidth'] + r""" points.}
\label{tab:planner}
\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{tabular}{@{}l ccccc@{}}
\toprule
Policy & dup & loss & ask & $P_{\mathrm{v}}$ & s \\
\midrule
""" + '\n'.join(prow(P[p]) for p in order_b[:12]) + '\n\\midrule\n' + '\n'.join(prow(P[p]) for p in order_b[12:]) +
  '\n\\midrule\n' + '\n'.join(prow(P[p]) for p in order_a) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
mm = lambda k, p, fmt=f2: fmt(P[p][k])
for key, pol in [('Redo', 'redo'), ('Ckpt', 'ckpt'), ('Atomix', 'atomix'), ('AtomixDur', 'atomix-durable'), ('Verify', 'verify'),
                 ('Key', 'key'), ('KeyAsk', 'key-ask'), ('AskAll', 'always-ask'), ('NonceAsk', 'nonce-ask'), ('Maj', 'maj3-ask'),
                 ('Rules', 'rules'), ('RulesLen', 'rules-lenient'), ('Src', 'ghost-src'), ('Joint', 'ghost-joint'),
                 ('Vone', 'ghost-v1'), ('Ghost', 'ghost'), ('NoNonce', 'ghost-nononce'), ('NoHop', 'ghost-nohop1'),
                 ('NoDigest', 'ghost-nodigest'), ('NoCal', 'ghost-nocal'), ('Uni', 'ghost-uniform'), ('NoAsk', 'ghost-noask'),
                 ('Vis', 'ghost-visible'), ('Gtwo', 'g2-only')]:
    M(f'Sim{key}Dup', mm('dup', pol, f1) if float(P[pol]['dup']) >= 1 else mm('dup', pol))
    M(f'Sim{key}Loss', mm('loss', pol, f1) if float(P[pol]['loss']) >= 1 else mm('loss', pol))
    M(f'Sim{key}Ask', mm('ask', pol, f1))
    M(f'Sim{key}Pv', mm('cdup', pol, f1) if float(P[pol]['cdup']) >= 1 else mm('cdup', pol))
    M(f'Sim{key}PvHi', mm('cdup_hi', pol))
    M(f'Sim{key}Lv', mm('closs', pol, f1) if float(P[pol]['closs']) >= 1 else mm('closs', pol))
    M(f'Sim{key}Secs', f"{float(P[pol]['secs']):.0f}")
    M(f'Sim{key}P', f"{float(P[pol]['p_dup']):.2f}" if P[pol].get('p_dup') not in ('', 'nan', None) else '--')
M('SimN', '12{,}000')
M('SimGhostReads', f1(P['ghost']['obs']))
M('SimGhostBg', f1(P['ghost']['bg']))
M('SimGhostCloss', f2(P['ghost']['closs']))
M('SimAltered', f"{float(P['key']['altered']):.0f}")
M('SimGhostVsAskAll', f"{float(P['always-ask']['ask']) / float(P['ghost']['ask']):.1f}")
M('SimPUni', f2(P['ghost-uniform']['p_dup']))
M('SimNoCalRatio', f"{float(P['ghost-nocal']['cdup']) / max(1e-9, float(P['ghost']['cdup'])):.0f}")
M('SimRulesRatio', f"{float(P['rules']['cdup']) / max(1e-9, float(P['ghost']['cdup'])):.0f}")
M('SimBudgetRatio', f"{1.0 / max(1e-9, float(P['ghost']['cdup'])):.0f}")
g = P['ghost']
for k, nm in (('wait', 'Wait'), ('contra', 'Contra'), ('struct', 'Struct'), ('uncert', 'Uncert')):
    M(f'Why{nm}', f1(g['why_' + k]))
M('WhyTotal', f1(sum(float(g['why_' + k]) for k in ('wait', 'contra', 'struct', 'uncert'))))

cl = rd('planner_class.csv')
CL = {(r['policy'], r['cls']): r for r in cl}
for k, c in [('Gtwo', 'G2'), ('NonGtwo', 'non-G2'), ('Local', 'local'), ('Vlm', 'VLM-only')]:
    M(f'Class{k}Ask', f1(CL[('ghost', c)]['ask']))
    M(f'Class{k}Secs', f"{float(CL[('ghost', c)]['secs']):.0f}")
    M(f'ClassSrc{k}Ask', f1(CL[('ghost-src', c)]['ask']))
M('ClassKeyGtwoPv', f1(CL[('key', 'G2')]['cdup']))

sh = rd('planner_share.csv')
SH = {(r['policy'], r['family']): r for r in sh}
for fam, nm in (('hop1', 'Hop'), ('nonce', 'Nonce'), ('digest', 'Digest'), ('vlm', 'Vlm')):
    M(f'Share{nm}', f"{float(SH[('ghost', fam)]['share']):.0f}")
    M(f'ShareSrc{nm}', f"{float(SH[('ghost-src', fam)]['share']):.0f}")

# ---- stress (merge chunked parts)
st = []
for fn in sorted(os.listdir(RES)):
    if fn.startswith('planner_stress') and fn.endswith('.csv'):
        if fn == 'planner_stress.csv' and any(x.startswith('planner_stress.part') for x in os.listdir(RES)):
            continue
        st += rd(fn)
ST = {(r['scenario'], r['policy']): r for r in st}
scn = [('r1', 'independent re-reads'), ('r1+persist', '\\quad + persistent nonce misses'),
       ('default', 'default world (Table~\\ref{tab:planner})'), ('cross0.3', 'cross-view VLM correlation 0.3'),
       ('lagtail', 'heavy lag tail, \\emph{not} in calibration'), ('lagtail-cal', 'heavy lag tail, in calibration'),
       ('g2break', 'G2 broken (retry cap / force-stop)'), ('g2nodedup', 'classified G2, server without dedup'),
       ('doze-unaware', 'delayed recovery in Doze, not detected'),
       ('doze-aware', 'delayed recovery in Doze, detected'), ('common0.5', 'stale history, 0.5\\% common mode'),
       ('mon0.05', 'Monitor misreads 5\\% of terminal states'),
       ('user0.2', 'user wrong on 20\\% of asks'), ('combined', 'combined')]
lines = []
for s_, lab in scn:
    a, b, rr = ST[(s_, 'ghost-v1')], ST[(s_, 'ghost')], ST[(s_, 'rules')]
    lines.append(f"{lab} & {f2(a['cdup'])} & {f2(rr['cdup'])} & {f2(b['cdup'])} ({f2(b['cdup_hi'])}) & {f2(b['closs'])} & {f1(b['ask'])}" + r' \\')
W('tab_stress.tex', r"""\begin{table}[t]
\centering
\caption{Misspecification and stress (model-based simulation, 12{,}000 paired workflows per row; the generative model departs from
the planner's assumptions as listed). $P_{\mathrm{v}}$: \% of committed effects retried by the planner (budget 1\%; CP 95\% upper bound in
parentheses); $L_{\mathrm{v}}$: \% of absent effects the planner declared done; ask: \% of workflows. Rules: the same-evidence rule baseline.}
\label{tab:stress}
\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}l cc ccc@{}}
\toprule
 & Re-read & Rules & \multicolumn{3}{c}{\alg (product)} \\
\cmidrule(l){4-6}
Generative model & $P_{\mathrm{v}}$ & $P_{\mathrm{v}}$ & $P_{\mathrm{v}}$ (hi) & $L_{\mathrm{v}}$ & ask \\
\midrule
""" + '\n'.join(lines) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
sv = lambda s_, p, k, fmt=f2: fmt(ST[(s_, p)][k])
M('StressRoneVone', sv('r1', 'ghost-v1', 'cdup'))
M('StressPersistVone', sv('r1+persist', 'ghost-v1', 'cdup'))
M('StressLag', sv('lagtail', 'ghost', 'cdup'))
M('StressLagHi', sv('lagtail', 'ghost', 'cdup_hi'))
M('StressLagRules', sv('lagtail', 'rules', 'cdup'))
M('StressLagCalAsk', sv('lagtail-cal', 'ghost', 'ask', f1))
M('StressDoze', sv('doze-unaware', 'ghost', 'cdup', f1))
M('StressDozeVone', sv('doze-unaware', 'ghost-v1', 'cdup', f1))
M('StressDozeAsk', sv('doze-aware', 'ghost', 'ask', f1))
M('StressGbreakVoneLoss', sv('g2break', 'ghost-v1', 'closs', f1))
M('StressGbreakLoss', sv('g2break', 'ghost', 'closs'))
M('StressNodedupDup', sv('g2nodedup', 'ghost', 'dup', f1))
M('StressNodedupPv', sv('g2nodedup', 'ghost', 'cdup'))
M('StressCommon', sv('common0.5', 'ghost', 'cdup'))
M('StressMon', sv('mon0.05', 'ghost', 'cdup'))
M('StressMonLv', sv('mon0.05', 'ghost', 'closs'))
M('StressMonAsk', sv('mon0.05', 'ghost', 'ask', f1))
M('StressCombined', sv('combined', 'ghost', 'cdup'))
M('StressCombinedAsk', sv('combined', 'ghost', 'ask', f1))
M('StressCrossAsk', sv('cross0.3', 'ghost', 'ask', f1))
over = [s_ for s_, _ in scn if float(ST[(s_, 'ghost')]['cdup_hi']) > 1.0]
M('StressMaxHi', f2(max(float(ST[(s_, 'ghost')]['cdup_hi']) for s_, _ in scn if s_ not in over)))
M('StressNover', str(len(over)))
M('StressRulesOver', str(sum(1 for s_, _ in scn if float(ST[(s_, 'rules')]['cdup']) > 1.0)))

# ---- calibration population, common mode, calibration size (Table tab:pop)
pop = [('default', 'default world, passive labels'), ('iworld-passive', 'interrupted world, passive labels'),
       ('iworld-fault', 'interrupted world, fault-injected labels'), ('cm0.005-fault', 'stale history 0.5\\%, fault-injected'),
       ('cm0.02-fault', 'stale history 2\\%, fault-injected'), ('cm0.05-fault', 'stale history 5\\%, fault-injected')]
nc = rd('planner_ncal.csv')
NC = {(r['study'], r.get('ncal') or '', r.get('kappa') or '', r.get('shift_test') or '', r['policy']): r for r in nc}
cell = lambda r: f"{f2(r['cdup'])} / {float(r['ask']):.0f}"
lines = []
for s_, lab in pop:
    lines.append(lab + ' & ' + ' & '.join(cell(ST[(s_, p)]) for p in ('ghost', 'ghost-src', 'ghost-joint')) +
                 f" & {f2(ST[(s_, 'rules')]['cdup'])}" + r' \\')
lines.append(r'\midrule')
ncs = sorted(set(int(r['ncal']) for r in nc if r['study'] == 'ncal'))
for n_ in ncs:
    lines.append(f"$n_{{\\mathrm{{cal}}}}{{=}}{n_:,}".replace(',', '{,}') + '$ (default world) & ' +
                 ' & '.join(cell(NC[('ncal', str(n_), '', '', p)]) for p in ('ghost', 'ghost-src', 'ghost-joint')) + r' & -- \\')
W('tab_pop.tex', r"""\begin{table}[t]
\centering
\caption{Calibration population, common mode and calibration size (model-based simulation, 12{,}000 paired workflows per row). Cells: $P_{\mathrm{v}}$ (\%, budget 1\%) /
escalations (\%). Interrupted world: 2\% stale history after a restart, 3\% optimistic ``sending'' entries for tapped-but-uncommitted effects, 20\% heavy-tailed lags.
Passive labels come from uninterrupted effects; fault-injected labels from the interrupted population. Rules: $P_{\mathrm{v}}$ of the same-evidence rule baseline.}
\label{tab:pop}
\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}l ccc c@{}}
\toprule
 & product & source & joint & rules \\
\midrule
""" + '\n'.join(lines) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
M('PopRulesOver', str(sum(1 for s_, _ in pop[1:] if float(ST[(s_, 'rules')]['cdup']) > 1.0)))
M('PopRows', str(len(pop) - 1))
for s_, nm in (('iworld-passive', 'IwP'), ('iworld-fault', 'IwF'), ('cm0.005-fault', 'CmA'), ('cm0.02-fault', 'CmB'), ('cm0.05-fault', 'CmC')):
    for p, pn in (('ghost', 'Prod'), ('ghost-src', 'Src'), ('ghost-joint', 'Joint'), ('rules', 'Rules')):
        M(f'Pop{nm}{pn}', f2(ST[(s_, p)]['cdup']))
        M(f'Pop{nm}{pn}Hi', f2(ST[(s_, p)]['cdup_hi']))
        M(f'Pop{nm}{pn}Ask', f1(ST[(s_, p)]['ask']))
for n_ in ncs:
    for p, pn in (('ghost', 'Prod'), ('ghost-src', 'Src'), ('ghost-joint', 'Joint')):
        r = NC[('ncal', str(n_), '', '', p)]
        tag = {100: 'A', 200: 'B', 500: 'C', 1000: 'D', 2000: 'E', 5000: 'F', 10000: 'G'}[n_]
        M(f'Ncal{tag}{pn}Ask', f1(r['ask']))
        M(f'Ncal{tag}{pn}Pv', f2(r['cdup']))
for r in nc:
    if r['study'] == 'drift':
        tag = f"{int(float(r['kappa']))}"
        tag = {'1': 'One', '3': 'Three', '5': 'Five', '10': 'Ten'}[tag] + ('Test' if r['shift_test'] not in ('0', '') else '')
        M(f'Drift{tag}Pv', f2(r['cdup']))
        M(f'Drift{tag}PvHi', f2(r['cdup_hi']))
        M(f'Drift{tag}Ask', f1(r['ask']))

# ---- over-delivery decomposition
dc = rd('planner_decomp.csv')
dcu = [r for r in dc if float(r['tau']) > 0]
mean = lambda xs: sum(xs) / max(1, len(xs))
M('DecompBcp', f"{100 * mean([float(r['B_cp']) for r in dcu]):.2f}")
M('DecompBtrue', f"{100 * mean([float(r['B_true']) for r in dcu]):.3f}")
M('DecompRealized', f"{100 * mean([float(r['realized']) for r in dcu]):.3f}")
M('DecompCPratio', f"{mean([float(r['B_cp']) for r in dcu]) / max(1e-12, mean([float(r['B_true']) for r in dcu])):.1f}")

# ---- sample sizes (exact)
ss = rd('sample_size.csv')
lines = []
for r in ss:
    nn = lambda x: '--' if x in ('inf', '') else f"{int(float(x)):,}".replace(',', '{,}')
    lines.append(f"{alpha_tex(r['alpha'])} & {float(r['p']) * 100:.1f}\\% & {nn(r['prod_n'])} & {nn(r['prod_n0'])} & {nn(r['joint_n'])} & {nn(r['joint_n_q'])} & {nn(r['joint_n_k'])} & {nn(r['lag_n'])}" + r' \\')
W('tab_nsize.tex', r"""\begin{table}[t]
\centering
\caption{Calibration sizes that make certification possible (exact one-sided Clopper--Pearson, $\delta{=}\min(\alpha,\beta)/(10K)$, $\alpha{=}\beta$), per stratum. Keying by the four
observable fault classes multiplies every entry by \NsizeKeyLo--\NsizeKeyHi{} (each class needs its own labels and is certified at $\delta/4$). Product (A2): effects so that two families, each with true wrong-verdict rate $p$, multiply to
$\alpha_{\mathrm{test}}{=}\alpha/2$; \emph{med.}: observed at the expected count $\lceil pn\rceil$ (about half of such sets fail), \emph{0}: zero wrong verdicts (minimum for any $p$).
Joint: whole effects for a jointly calibrated region to certify $\alpha_{\mathrm{test}}$ with zero events (\emph{0}), at a true region rate $\alpha_{\mathrm{test}}/4$ (\emph{med.}), and with zero events for one
step of a 3-effect workflow. Lag: logged times for one wait at $0.2\alpha$ with zero exceedances.}
\label{tab:nsize}
\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{tabular}{@{}cc cc ccc c@{}}
\toprule
 & & \multicolumn{2}{c}{product} & \multicolumn{3}{c}{joint} & lag \\
\cmidrule(lr){3-4}\cmidrule(lr){5-7}
$\alpha$ & $p$ & med. & 0 & 0 & med. & 0, $k{=}3$ & 0 \\
\midrule
""" + '\n'.join(lines) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
S1 = [r for r in ss if float(r['alpha']) == 0.01 and float(r['p']) == 0.01][0]
S3 = [r for r in ss if float(r['alpha']) == 0.001 and float(r['p']) == 0.01][0]
fmtn = lambda x: f"{int(float(x)):,}".replace(',', '{,}')
M('NsizeProdTwo', fmtn(S1['prod_n']))
M('NsizeJointTwo', fmtn(S1['joint_n']))
M('NsizeLagTwo', fmtn(S1['lag_n']))
M('NsizeProdThree', fmtn(S3['prod_n']))
M('NsizeJointThree', fmtn(S3['joint_n']))
M('NsizeJointQTwo', fmtn(S1['joint_n_q']))
M('NsizeProdZeroTwo', fmtn(S1['prod_n0']))
M('NsizeLagThree', fmtn(S3['lag_n']))
_kcols = ['prod_n', 'prod_n0', 'joint_n', 'joint_n_q', 'joint_n_k', 'lag_n']
_kmult = [4 * float(r[c + '_key']) / float(r[c]) for r in ss for c in _kcols]
M('NsizeKeyLo', f1(min(_kmult)))
M('NsizeKeyHi', f1(max(_kmult)))
M('NsizeKeyJointTwo', f"{4 * float(S1['joint_n_key']) / float(S1['joint_n']):.1f}")
M('NsizeLagFullKey', fmtn(S1['lag_n_full_key']))
M('NsizeLagFull', fmtn(S1['lag_n_full']))

# ---- Pareto figure: (a) P_v vs escalations along the alpha sweep; (b) dup+loss vs escalations
sw = rd('planner_alpha_sweep.csv')
SW = {}
for r in sw:
    SW.setdefault(r['policy'], []).append(r)
curves = [('ghost', 'blue!70!black', '*', 'product'), ('ghost-src', 'teal!70!black', 'square*', 'source'),
          ('ghost-joint', 'violet!80!black', 'triangle*', 'joint'), ('ghost-nocal', 'orange!85!black', 'diamond*', 'nominal i.i.d.')]
pa = []
for pol, col, mk, lab in curves:
    pts = ' '.join(f"({float(r['cdup']):.3f},{float(r['ask']):.2f})" for r in SW[pol])
    pa.append(f"\\addplot[color={col},mark={mk},thick,mark size=1.5pt] coordinates {{{pts}}};\n\\addlegendentry{{{lab}}}")
rsw = rd('planner_rules_sweep.csv') if os.path.exists(os.path.join(RES, 'planner_rules_sweep.csv')) else []
if rsw:
    pts = ' '.join(f"({float(r['cdup']):.3f},{float(r['ask']):.2f})" for r in rsw)
    pa.append(f"\\addplot[only marks,mark=x,mark size=2pt,gray!60!black] coordinates {{{pts}}};\n\\addlegendentry{{rule family}}")
    # Pareto frontier of the rule family (min escalations at P_v <= x), and the matched-P_v comparisons
    best = lambda cap, rows: min((float(r['ask']), r) for r in rows if float(r['cdup']) <= cap)
    pv10 = float(SW['ghost'][0]['cdup'])
    a_r, r_r = best(pv10, rsw)
    M('RuleBestTenAsk', f1(a_r))
    M('RuleBestTenPv', f2(r_r['cdup']))
    M('RuleBestTenName', r_r['policy'].replace('rules-w', 'wait ').replace('-all', ' s, all agree').replace('-novlm', ' s, all but VLM').replace('-two', ' s, any two'))
    g3 = [r for r in SW['ghost'] if abs(float(r['alpha']) - 0.03) < 1e-9][0]
    a3, r3_ = best(float(g3['cdup']) + 1e-9, rsw)
    M('RuleBestThreeAsk', f1(a3))
    M('RuleBestThreePv', f2(r3_['cdup']))
    M('RuleBestThreeName', r3_['policy'].replace('rules-w', 'wait ').replace('-all', ' s, all agree').replace('-novlm', ' s, all but VLM').replace('-two', ' s, any two'))
    M('RuleMinAsk', f1(min(float(r['ask']) for r in rsw)))
    M('RuleMinPv', f2(min(float(r['cdup']) for r in rsw)))
    M('RuleMinPvAsk', f1(min((float(r['cdup']), float(r['ask'])) for r in rsw)[1]))
    M('RuleN', len(rsw))
    M('RuleOver', sum(1 for r in rsw if float(r['cdup']) > 1.0))
    jt = SW['ghost-joint']
    M('SweepJointTenPv', f2(jt[0]['cdup']))
    M('SweepJointTenAsk', f1(jt[0]['ask']))
    j3 = [r for r in jt if abs(float(r['alpha']) - 0.03) < 1e-9][0]
    M('SweepJointThreePv', f2(j3['cdup']))
    M('SweepJointThreeAsk', f1(j3['ask']))
for pol, mk, lab, anc in (('rules', 'x', 'rules', 'west'), ('rules-lenient', '+', 'rules (lenient)', 'south west'),
                          ('nonce-ask', 'pentagon', 'nonce+ask', 'west')):
    r = P[pol]
    if float(r['cdup']) <= 2.0:
        pa.append(f"\\addplot[only marks,mark={mk},mark size=2.2pt,black,forget plot] coordinates {{({float(r['cdup']):.3f},{float(r['ask']):.2f})}};"
                  f"\\node[font=\\scriptsize,anchor={anc},inner sep=2pt] at (axis cs:{float(r['cdup']):.3f},{float(r['ask']):.2f}) {{{lab}}};")
gl = ' '.join(f"\\node[font=\\tiny,anchor=south east,inner sep=1pt,blue!60!black] at (axis cs:{float(r['cdup']):.3f},{float(r['ask']):.2f}) {{{float(r['alpha']):g}}};"
              for r in SW['ghost'])
mark = {'redo': 'x', 'atomix': 'triangle', 'atomix-durable': 'triangle*', 'verify': 'diamond', 'key': 'square',
        'key-ask': 'square*', 'nonce-ask': 'pentagon*', 'maj3-ask': 'diamond*', 'always-ask': 'otimes*', 'ghost-v1': 'o'}
short_n = {'redo': 'redo', 'atomix': 'Atomix', 'atomix-durable': 'Atomix-durable', 'verify': 'verify', 'key': 'key',
           'key-ask': 'key+ask', 'nonce-ask': 'nonce+ask', 'maj3-ask': '3 views+ask', 'always-ask': 'always ask', 'ghost-v1': 're-read SPRT',
           'rules': 'rules', 'rules-lenient': 'lenient'}
anch = {'key': 'south west', 'always-ask': 'south east', 'maj3-ask': 'south', 'nonce-ask': 'south west', 'key-ask': 'north west',
        'ghost-v1': 'north west', 'rules': 'north', 'rules-lenient': 'north west'}
pb = []
for p, mk in mark.items():
    r = P[p]
    y = float(r['dup']) + float(r['loss'])
    pb.append(f"\\addplot[only marks,mark={mk},mark size=1.8pt,gray!40!black] coordinates {{({float(r['ask']):.2f},{y:.3f})}};"
              f"\\node[font=\\scriptsize,anchor={anch.get(p, 'west')},inner sep=1.5pt] at (axis cs:{float(r['ask']):.2f},{y:.3f}) {{{short_n[p]}}};")
gpts = ' '.join(f"({float(r['ask']):.2f},{float(r['dup']) + float(r['loss']):.3f})" for r in SW['ghost'])
xmax = max(1.6, max(float(r['cdup']) for pol, *_ in curves for r in SW[pol]) * 1.1)
W('fig_pareto.tex', r"""\begin{figure}[t]
\centering
\begin{tikzpicture}
\begin{axis}[width=\linewidth,height=4.0cm,xlabel={$P_{\mathrm{v}}$ (\% of committed effects retried by the planner)},ylabel={escalations (\%)},
  xmin=-0.05,xmax=""" + f"{xmax:.2f}" + r""",ymin=0,ymax=100,
  legend style={at={(0.5,1.03)},anchor=south,font=\scriptsize,draw=none,fill=none},legend columns=5,legend cell align=left,
  tick label style={font=\footnotesize},label style={font=\footnotesize},ymajorgrids,grid style={dashed,gray!30}]
""" + '\n'.join(pa) + '\n' + gl + r"""
\draw[dashed,red!60!black] (axis cs:1,0) -- (axis cs:1,100) node[pos=0.97,anchor=north west,font=\scriptsize,inner sep=2pt] {1\% budget};
\end{axis}
\end{tikzpicture}\\[-1pt]
\begin{tikzpicture}
\begin{axis}[width=\linewidth,height=3.7cm,xlabel={escalations (\% of interrupted workflows)},ylabel={dup + loss (\%)},
  ymode=log,xmin=-6,xmax=106,ymin=0.8,ymax=120,log basis y=10,
  tick label style={font=\footnotesize},label style={font=\footnotesize},ymajorgrids,grid style={dashed,gray!30}]
""" + '\n'.join(pb) + r"""
\addplot[color=blue!70!black,mark=*,thick,mark size=1.6pt] coordinates {""" + gpts + r"""};
\end{axis}
\end{tikzpicture}
\caption{Top: escalations against the guaranteed quantity $P_{\mathrm{v}}$ as $\alpha{=}\beta$ sweeps from $0.1$ to $10^{-3}$ (labels on the product curve), against
the same-evidence rule family (wait 5/10/30/60\,s $\times$ quorum all / all but VLM / any two; gray $\times$), which has no guarantee; neither does a planner run at nominal $\alpha{=}0.1$. Bottom: total errors (including wrong user answers) against escalations; gray: baselines at their single operating point, blue: product sweep. Model-based simulation, default world.}
\label{fig:pareto}
\end{figure}
""")
gs = SW['ghost']
M('SweepAskLo', f1(gs[0]['ask']))
M('SweepAskHi', f1(gs[-1]['ask']))
M('SweepPvLo', f2(gs[0]['cdup']))
M('SweepSecsLo', f"{float(gs[0]['secs']):.0f}")
M('SweepSecsHi', f"{float(gs[-1]['secs']):.0f}")
r3 = [r for r in gs if abs(float(r['alpha']) - 0.03) < 1e-9][0]
M('SweepThreeAsk', f1(r3['ask']))
M('SweepThreePv', f2(r3['cdup']))
M('SweepTenAsk', f1(gs[0]['ask']))
nb = SW['ghost-nocal']
M('SweepNocalLoPv', f2(nb[0]['cdup']))

us = rd('planner_user.csv')
U = {(r['policy'], float(r['user_err'])): r for r in us}
tot = lambda r: float(r['dup']) + float(r['loss'])
M('UserAskAllTwenty', f1(tot(U[('always-ask', 0.2)])))
M('UserGhostTwenty', f1(tot(U[('ghost', 0.2)])))
M('UserRulesTwenty', f1(tot(U[('rules', 0.2)])))
M('UserGhostZero', f2(tot(U[('ghost', 0.0)])))
M('UserNonceZero', f1(tot(U[('nonce-ask', 0.0)])))
M('UserMajTwenty', f1(tot(U[('maj3-ask', 0.2)])))

se = rd('planner_sensitivity.csv')
vars_ = []
for r in se:
    if r['variant'] not in vars_:
        vars_.append(r['variant'])
SE = {(r['variant'], r['policy']): r for r in se}
lines = []
for v in vars_:
    cells = []
    for p in ['key', 'nonce-ask', 'always-ask', 'ghost']:
        r = SE[(v, p)]
        cells.append(f"{tot(r):.1f} / {float(r['ask']):.0f}")
    lines.append(f"{v} & " + ' & '.join(cells) + f" & {f2(SE[(v, 'ghost')]['cdup'])} ({f2(SE[(v, 'ghost')]['cdup_hi'])})" + r' \\')
W('tab_sens.tex', r"""\begin{table}[!htbp]
\centering
\caption{Sensitivity to the simulator's free app-profile parameters (4{,}800 paired workflows per row). Cells: dup+loss (\% of workflows) /
escalations (\%); last column: GhostEffect's $P_{\mathrm{v}}$ (\%, budget 1\%) with its 95\% CP upper bound.}
\label{tab:sens}
\footnotesize
\setlength{\tabcolsep}{2.2pt}
\begin{tabular}{@{}l cccc c@{}}
\toprule
Variant & key & nonce+ask & always ask & GhostEffect & $P_{\mathrm{v}}$ (hi) \\
\midrule
""" + '\n'.join(lines) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
M('SensPvMax', f2(max(float(SE[(v, 'ghost')]['cdup']) for v in vars_)))
M('SensPvHiMax', f2(max(float(SE[(v, 'ghost')]['cdup_hi']) for v in vars_)))

# ===================================================================== emulator measurements (results/real/), if present
REAL = os.path.join(RES, 'real')
real_csvs = sorted(f for f in os.listdir(REAL) if f.endswith('.csv')) if os.path.isdir(REAL) else []
# measurements count as reportable only once the testbed agent has written its SUMMARY.md (provenance)
if real_csvs and os.path.exists(os.path.join(REAL, 'SUMMARY.md')):
    exec(open(os.path.join(HERE, 'render_real.py')).read())
else:
    M('RealDataLimitation', r'No simulator parameter is yet measured on a device or emulator.')
    M('RealPresent', 'no')
    M('RealAbstract', r'No agent, VLM or phone is measured; device experiments are planned.')
    M('RealIntro', r'none is a device measurement.')
    M('RealConclusion', r'Whether real agents, apps and VLMs match these models is what the device study will measure.')
    W('real_section.tex', '% no artifact/results/real/*.csv present: no emulator measurements reported\n')

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

# ===================================================================== macros
W('macros.tex', '% AUTO-GENERATED by artifact/scripts/render.py -- do not edit by hand\n' +
  '\n'.join(f"\\newcommand{{\\{k}}}{{{v}\\xspace}}" for k, v in sorted(MACROS.items())) + '\n')
print(f'wrote {len(MACROS)} macros and tables/figures to {OUT}')
