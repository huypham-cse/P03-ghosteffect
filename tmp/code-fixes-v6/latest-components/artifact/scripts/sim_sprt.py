#!/usr/bin/env python3
"""E1 (REAL): validate Theorem 1(ii) -- SPRT error guarantees and sample-size bounds.

For eps in {0.05..0.30} (symmetric oracle eps0=eps1=eps) and alpha=beta in {1e-1..1e-4}:
  * exact DP exit probabilities and E[N] (DTMC computation, stand-in for PRISM/Storm),
  * Monte Carlo over 5 seeds (empirical P(dup), P(loss), E[N]) with Clopper-Pearson CIs,
  * Wald approximation, rigorous upper bound, and the lower bound of Thm 4.1(c).
Also an asymmetric-oracle check and the calibration/correlation robustness study (Lemma 4.6(i), Prop. 4.3, Lemma 4.5).
Outputs CSVs in artifact/results/.
"""
import csv
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import (sprt_exact, sprt_run, lower_bound, wald_approx, upper_bound,
                     clopper_pearson, cp_upper_one_sided, kl_pair, mean_ci)

RES = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RES, exist_ok=True)
SEEDS = [11, 23, 37, 41, 53]
N_PER_SEED = 8000
EPS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
ALPHAS = [1e-1, 1e-2, 1e-3, 1e-4]


def main():
    rows = []
    for eps in EPS:
        for al in ALPHAS:
            be = al
            ex1 = sprt_exact(eps, eps, al, be, 1)
            ex0 = sprt_exact(eps, eps, al, be, 0)
            lb1, lb0 = lower_bound(al, be, eps, eps)
            w1, w0 = wald_approx(al, be, eps, eps)
            ub1, ub0 = upper_bound(al, be, eps, eps)
            dups = losses = 0
            n1s, n0s = [], []
            per_seed_en = []
            for s in SEEDS:
                rng = random.Random(s * 1000 + int(eps * 100) * 10 + ALPHAS.index(al))
                t1 = t0 = 0
                for _ in range(N_PER_SEED):
                    d, n = sprt_run(rng, eps, eps, 1, al, be)
                    dups += d == 'absent'
                    t1 += n
                    d, n = sprt_run(rng, eps, eps, 0, al, be)
                    losses += d == 'committed'
                    t0 += n
                n1s.append(t1 / N_PER_SEED)
                n0s.append(t0 / N_PER_SEED)
                per_seed_en.append(0.5 * (t1 + t0) / N_PER_SEED)
            N = N_PER_SEED * len(SEEDS)
            dlo, dhi = clopper_pearson(dups, N)
            llo, lhi = clopper_pearson(losses, N)
            en, enci = mean_ci(per_seed_en)
            rows.append(dict(
                eps=eps, alpha=al, beta=be,
                exact_dup=ex1['bot'], exact_loss=ex0['top'],
                exact_EN=0.5 * (ex1['EN'] + ex0['EN']),
                mc_dup=dups / N, mc_dup_hi=dhi, mc_loss=losses / N, mc_loss_hi=lhi,
                mc_EN=en, mc_EN_ci=enci,
                wald_EN=0.5 * (w1 + w0), lb_EN=0.5 * (lb1 + lb0), ub_EN=0.5 * (ub1 + ub0),
                ratio_to_lb=(0.5 * (ex1['EN'] + ex0['EN'])) / (0.5 * (lb1 + lb0)),
                n_mc=N))
            print(f"eps={eps:.2f} a={al:g}: exact dup={ex1['bot']:.2e} loss={ex0['top']:.2e} "
                  f"EN={0.5*(ex1['EN']+ex0['EN']):.2f} mcEN={en:.2f} LB={0.5*(lb1+lb0):.2f} "
                  f"W={0.5*(w1+w0):.2f} UB={0.5*(ub1+ub0):.2f} mc dup={dups}/{N} loss={losses}/{N}")
    with open(os.path.join(RES, 'sprt_validation.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- asymmetric oracles (VLM evaluators tend to over-claim success: eps0 > eps1)
    asym = []
    for e0, e1 in [(0.20, 0.05), (0.10, 0.25), (0.26, 0.07), (0.02, 0.15)]:
        for al, be in [(1e-3, 1e-2), (1e-2, 1e-3)]:
            ex1 = sprt_exact(e0, e1, al, be, 1)
            ex0 = sprt_exact(e0, e1, al, be, 0)
            lb1, lb0 = lower_bound(al, be, e0, e1)
            asym.append(dict(eps0=e0, eps1=e1, alpha=al, beta=be, exact_dup=ex1['bot'],
                             exact_loss=ex0['top'], EN1=ex1['EN'], EN0=ex0['EN'], LB1=lb1, LB0=lb0))
    with open(os.path.join(RES, 'sprt_asym.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(asym[0].keys()))
        w.writeheader()
        w.writerows(asym)

    # ---- calibration robustness (Lemma 3): nominal, plug-in, and Clopper-Pearson upper bounds at two
    # confidence levels.  delta=0.05 is the round-1 setting (marginal guarantee alpha + 2 delta = 0.11 at
    # alpha=0.01, vacuous); 'cp-strict' uses delta = alpha/20, so the marginal guarantee is 1.1 alpha.
    # 200 probe types per seed; exact per-probe error via DP.
    cal_rows = []
    al = be = 1e-2
    for n_cal in [25, 50, 100, 200, 400]:
        for mode in ['nominal', 'plugin', 'cp-upper', 'cp-strict']:
            dups, viols, ens, worst, margs = [], [], [], [], []
            for s in SEEDS:
                rng = random.Random(7000 + 13 * s + n_cal)
                dsum = vcount = esum = 0.0
                wmax = 0.0
                P = 200
                for probe in range(P):
                    e0 = rng.uniform(0.06, 0.26)
                    e1 = rng.uniform(0.04, 0.20)
                    k0 = sum(rng.random() < e0 for _ in range(n_cal))
                    k1 = sum(rng.random() < e1 for _ in range(n_cal))
                    if mode == 'nominal':      # vendor-style "92% accurate" claim
                        m0 = m1 = 0.08
                    elif mode == 'plugin':
                        m0 = max(k0, 0.5) / n_cal
                        m1 = max(k1, 0.5) / n_cal
                    elif mode == 'cp-upper':
                        m0 = cp_upper_one_sided(k0, n_cal, 0.05)
                        m1 = cp_upper_one_sided(k1, n_cal, 0.05)
                    else:
                        m0 = cp_upper_one_sided(k0, n_cal, al / 20)
                        m1 = cp_upper_one_sided(k1, n_cal, al / 20)
                    m0 = min(m0, 0.45)
                    m1 = min(m1, 0.45)
                    r1 = sprt_exact(e0, e1, al, be, 1, model=(m0, m1))
                    r0 = sprt_exact(e0, e1, al, be, 0, model=(m0, m1))
                    pd = r1['bot']
                    dsum += pd
                    vcount += (pd > al) or (r0['top'] > be)
                    wmax = max(wmax, pd)
                    esum += 0.5 * (r1['EN'] + r0['EN'])
                dups.append(dsum / P)
                viols.append(vcount / P)
                ens.append(esum / P)
                worst.append(wmax)
            dm, dci = mean_ci(dups)
            vm, vci = mean_ci(viols)
            em, eci = mean_ci(ens)
            cal_rows.append(dict(n_cal=n_cal, mode=mode, dup=dm, dup_ci=dci, viol=vm, viol_ci=vci,
                                 worst=max(worst), EN=em, EN_ci=eci, alpha=al))
            print(f"cal n={n_cal} {mode}: dup={dm:.4f} viol={vm:.3f}±{vci:.3f} worst={max(worst):.4f} EN={em:.2f}")
    with open(os.path.join(RES, 'calibration.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cal_rows[0].keys()))
        w.writeheader()
        w.writerows(cal_rows)
    correlation_study()


# ------------------------------------------------------------------ correlated reads (revised)
# Generative model (an *outcome* of the simulation, not an input to the planner):
#  * within-view: each of V=3 views is "sticky" with prob rho_w -- all its re-reads share one error
#    draw -- otherwise its re-reads are i.i.d.; pairwise correlation of two re-reads of a view = rho_w.
#  * cross-view: per effect a latent error rate theta ~ Beta(mean eps, ICC rho_x) shared by all views
#    (rho_x = 0: theta = eps).  Views are conditionally i.i.d. given theta.
# Policies:
#  v1-naive : SPRT re-reading one view (round-1 strawman), cap 14.
#  v1       : round-1 planner: rotate 3 views, shrink LLR by (1-r)/(1+r), r = rho_w/3, cap 14.
#  v2-view  : one read per distinct view (never re-reads), view-level CP-calibrated eps, SPRT capped
#             at V=3 views, then ask.  Guarantee assumes independence ACROSS views only (A2').
#  v2-cert  : family verdict = unanimity of the V views; acts only if the CP upper bound on the
#             probability of a wrong unanimous verdict (calibrated on whole effects, so it includes
#             cross-view and persistent errors) is within budget; otherwise asks.  Model-free.
V_VIEWS = 3
EPS_C = 0.10
ALPHA_C = 1e-2
NCAL_VIEW, NCAL_FAM = 1000, 2000
DELTA_C = ALPHA_C / 20


def _theta(rng, eps, rho_x):
    if rho_x <= 0:
        return eps
    if rho_x >= 1:
        return 1.0 if rng.random() < eps else 0.0
    k = 1 / rho_x - 1
    return rng.betavariate(eps * k, (1 - eps) * k)


class Views:
    """Error process for one effect under X (1 = committed)."""
    def __init__(self, rng, x, eps, rho_w, rho_x):
        self.rng, self.x = rng, x
        th = _theta(rng, eps, rho_x)
        self.sticky = [rng.random() < rho_w for _ in range(V_VIEWS)]
        self.shared = [rng.random() < th for _ in range(V_VIEWS)]
        self.th = th

    def read(self, v):
        err = self.shared[v] if self.sticky[v] else (self.rng.random() < self.th)
        return (1 - self.x) if err else self.x


def _sprt_reads(read, e0, e1, al, be, n_max, shrink=1.0):
    import math
    a, b = math.log(1 / be), math.log(1 / al)
    u = math.log((1 - e1) / e0) * shrink
    v = math.log((1 - e0) / e1) * shrink
    L, n = 0.0, 0
    while n < n_max:
        n += 1
        L += u if read(n - 1) == 1 else -v
        if L >= a:
            return 'committed', n
        if L <= -b:
            return 'absent', n
    return 'ask', n


def worst_all_wrong(eps, rho, V):
    """Lemma (exchangeable views): sup P(all V views wrong) given mean eps and ICC rho."""
    if rho <= 0:
        return eps ** V
    w = rho * eps / (1 - eps + rho * eps)
    a = eps * (1 - rho)
    return w + (1 - w) * a ** V


def beta_all_wrong(eps, rho, V):
    if rho <= 0:
        return eps ** V
    if rho >= 1:
        return eps
    k = 1 / rho - 1
    a, b = eps * k, (1 - eps) * k
    out = 1.0
    for j in range(V):
        out *= (a + j) / (a + b + j)
    return out


def correlation_study():
    rows = []
    for scen in ['within', 'cross']:
        for rho in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            rw, rx = (rho, 0.0) if scen == 'within' else (0.0, rho)
            crng = random.Random(4100 + int(rho * 10) + (0 if scen == 'within' else 50))
            # view-level calibration: one read of view 0 per calibration effect
            k1 = sum(Views(crng, 1, EPS_C, rw, rx).read(0) == 0 for _ in range(NCAL_VIEW))
            k0 = sum(Views(crng, 0, EPS_C, rw, rx).read(0) == 1 for _ in range(NCAL_VIEW))
            e1v = min(0.45, cp_upper_one_sided(k1, NCAL_VIEW, DELTA_C))
            e0v = min(0.45, cp_upper_one_sided(k0, NCAL_VIEW, DELTA_C))
            # family-verdict calibration on whole effects
            f1 = f0 = 0
            for _ in range(NCAL_FAM):
                vv = Views(crng, 1, EPS_C, rw, rx)
                f1 += all(vv.read(j) == 0 for j in range(V_VIEWS))
                vv = Views(crng, 0, EPS_C, rw, rx)
                f0 += all(vv.read(j) == 1 for j in range(V_VIEWS))
            q1 = cp_upper_one_sided(f1, NCAL_FAM, DELTA_C)
            q0 = cp_upper_one_sided(f0, NCAL_FAM, DELTA_C)
            r = dict(scenario=scen, rho=rho, eps=EPS_C, alpha=ALPHA_C, eps_view_cp=e1v, q1_cp=q1,
                     bound_all_wrong=worst_all_wrong(EPS_C, rho, V_VIEWS) if scen == 'cross' else EPS_C ** V_VIEWS,
                     true_all_wrong=beta_all_wrong(EPS_C, rho, V_VIEWS) if scen == 'cross' else EPS_C ** V_VIEWS)
            for pol in ['v1-naive', 'v1', 'v2-view', 'v2-cert']:
                dups = asks = tot = nsum = 0
                for s in SEEDS:
                    rng = random.Random(9100 + 17 * s + int(rho * 100) + (0 if scen == 'within' else 7)
                                        + ['v1-naive', 'v1', 'v2-view', 'v2-cert'].index(pol) * 3)
                    for _ in range(6000):
                        vv = Views(rng, 1, EPS_C, rw, rx)
                        if pol == 'v1-naive':
                            d, n = _sprt_reads(lambda i: vv.read(0), EPS_C, EPS_C, ALPHA_C, ALPHA_C, 14)
                        elif pol == 'v1':
                            reff = rw / 3
                            d, n = _sprt_reads(lambda i: vv.read(i % V_VIEWS), EPS_C, EPS_C, ALPHA_C, ALPHA_C, 14,
                                               shrink=(1 - reff) / (1 + reff))
                        elif pol == 'v2-view':
                            d, n = _sprt_reads(lambda i: vv.read(i), e0v, e1v, ALPHA_C, ALPHA_C, V_VIEWS)
                        else:
                            ys = [vv.read(j) for j in range(V_VIEWS)]
                            n = V_VIEWS
                            if all(y == 0 for y in ys) and q1 <= ALPHA_C:
                                d = 'absent'
                            elif all(y == 1 for y in ys) and q0 <= ALPHA_C:
                                d = 'committed'
                            else:
                                d = 'ask'
                        dups += d == 'absent'
                        asks += d == 'ask'
                        nsum += n
                        tot += 1
                lo, hi = clopper_pearson(dups, tot)
                r[pol + '_dup'] = dups / tot
                r[pol + '_dup_hi'] = hi
                r[pol + '_ask'] = asks / tot
                r[pol + '_EN'] = nsum / tot
            rows.append(r)
            print({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})
    with open(os.path.join(RES, 'correlation.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    main()
