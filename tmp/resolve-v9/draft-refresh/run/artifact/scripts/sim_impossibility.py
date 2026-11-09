#!/usr/bin/env python3
"""E2 (REAL): Theorem 1(iii) -- the min(pi, 1-pi) floor and the cost-threshold rule.

A. No distinguishing read (p0 = p1): Monte Carlo of six recovery policies over a prior grid;
   every policy satisfies P(dup)+P(loss) >= min(pi, 1-pi); deterministic rules attain it.
B. Bayes floor E[min(post, 1-post)] with an informative oracle (eps=0.3) after n reads:
   the continuum between case (iii) (n=0) and case (ii).
C. Cost-threshold rule vs fixed policies across c_dup/c_loss (with ask-user option).
D. Unbounded lag (late commits, Pareto in-flight time): residual floor vs waiting time.
"""
import csv
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import sprt_run, clopper_pearson

RES = os.path.join(os.path.dirname(__file__), '..', 'results')
PIS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
N_EP = 20000


def run_policy(rng, name, pi):
    x = 1 if rng.random() < pi else 0
    # uninformative oracle: Y ~ Bern(0.3) regardless of X (e.g. last month's identical
    # $1,200 rent transfer is on screen whether or not this month's one went through)
    def read():
        return 1 if rng.random() < 0.3 else 0
    if name == 'always-retry':
        retry = True
    elif name == 'never-retry':
        retry = False
    elif name == 'coin(0.5)':
        retry = rng.random() < 0.5
    elif name == 'single-read':
        retry = read() == 0
    elif name == 'majority-of-5':
        retry = sum(read() for _ in range(5)) < 3
    elif name == 'fooled-SPRT':
        # an SPRT that believes the read is informative (eps=0.15) but it is not
        a = b = math.log(100)
        u = math.log(0.85 / 0.15)
        L = 0.0
        while -b < L < a:
            L += u if read() == 1 else -u
        retry = L <= -b
    else:
        raise ValueError(name)
    dup = retry and x == 1
    loss = (not retry) and x == 0
    return dup, loss


def main():
    pols = ['always-retry', 'never-retry', 'coin(0.5)', 'single-read', 'majority-of-5', 'fooled-SPRT']
    rows = []
    for pi in PIS:
        row = dict(pi=pi, floor=min(pi, 1 - pi))
        for p in pols:
            rng = random.Random(4242 + int(pi * 100) * 7 + pols.index(p))
            d = l = 0
            for _ in range(N_EP):
                dd, ll = run_policy(rng, p, pi)
                d += dd
                l += ll
            row[p] = (d + l) / N_EP
            lo, hi = clopper_pearson(d + l, N_EP)
            row[p + '_lo'] = lo
        rows.append(row)
        print(pi, {k: round(v, 4) for k, v in row.items()})
    with open(os.path.join(RES, 'impossibility.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    # minimum over policies of (estimate - floor), using the CP lower bound
    worst_gap = min(min(r[p + '_lo'] - r['floor'] for p in pols) for r in rows)
    print('min CP-lower minus floor (should be <= ~0 only for attaining policies):', worst_gap)

    # ---- B: Bayes floor with informative reads, eps=0.3, after n reads (exact)
    eps = 0.3
    brow = []
    for pi in [i / 20 for i in range(1, 20)]:
        r = dict(pi=pi)
        for n in [0, 1, 3, 9, 27]:
            tot = 0.0
            for k in range(n + 1):  # k reads say "committed"
                c = math.comb(n, k)
                l1 = c * (1 - eps) ** k * eps ** (n - k)
                l0 = c * eps ** k * (1 - eps) ** (n - k)
                tot += min(pi * l1, (1 - pi) * l0)
            r['n%d' % n] = tot
        brow.append(r)
    with open(os.path.join(RES, 'bayes_floor.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(brow[0].keys()))
        w.writeheader()
        w.writerows(brow)

    # ---- C: cost-threshold rule.  c_loss = 1, c_ask = 0.15, pi = posterior P(committed)
    crow = []
    for ratio in [0.1, 0.2, 0.5, 1, 2, 5, 10]:
        c_dup, c_loss, c_ask = ratio, 1.0, 0.15
        for pi in [0.3, 0.5, 0.7]:
            always = pi * c_dup
            never = (1 - pi) * c_loss
            bayes = min(always, never)
            with_ask = min(bayes, c_ask)
            act = 'retry' if (1 - pi) * c_loss > pi * c_dup else 'no-retry'
            if c_ask < bayes:
                act = 'ask'
            crow.append(dict(ratio=ratio, pi=pi, always=always, never=never, bayes=bayes,
                             with_ask=with_ask, action=act))
    with open(os.path.join(RES, 'cost_policy.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(crow[0].keys()))
        w.writeheader()
        w.writerows(crow)

    # ---- D: late commits with Pareto in-flight time T (x_m=2 s, shape k).
    # After waiting w with an "absent" read, q_w = P(T > w | in flight)*P(in flight)/P(absent seen).
    drow = []
    p_inflight = 0.3  # of interrupted requests still in flight at resume
    p_never = 0.4     # never reached server
    for k in [1.1, 1.5, 3.0]:
        for w in [2, 5, 10, 30, 60, 300, 900, 3600]:
            tail = 1.0 if w <= 2 else (2.0 / w) ** k
            late = p_inflight * tail
            absent_seen = p_never + late
            q = late / absent_seen
            floor = absent_seen * min(q, 1 - q)
            drow.append(dict(shape=k, wait=w, q=q, floor=floor))
    with open(os.path.join(RES, 'late_commit.csv'), 'w', newline='') as f:
        w_ = csv.DictWriter(f, fieldnames=list(drow[0].keys()))
        w_.writeheader()
        w_.writerows(drow)
    for r in drow:
        if r['wait'] in (60, 3600):
            print('late', r)
    lag_wait()


# ---- E: wait needed for the lag-tail share of the budget (Thm 4.1(a)/(b)).  T = time from the commit
# tap t0 to visibility.  Lower bound (Thm 4.1(b)): a verification-only policy deciding at t0+w from end-to-end reads has alpha >= (1-beta) G(w).
# Certified wait: smallest empirical quantile of n_lag passively logged commit-to-visibility times whose
# one-sided CP upper bound on the exceedance probability is <= alpha_lag (confidence 1-delta).
from ge_core import cp_upper_one_sided

TAILS = [
    ('lognormal, median 1.5 s, sigma 0.6', lambda r: r.lognormvariate(math.log(1.5), 0.6),
     lambda w: 0.5 * math.erfc((math.log(w) - math.log(1.5)) / (0.6 * math.sqrt(2))) if w > 0 else 1.0),
    ('lognormal, median 3 s, sigma 1.2', lambda r: r.lognormvariate(math.log(3.0), 1.2),
     lambda w: 0.5 * math.erfc((math.log(w) - math.log(3.0)) / (1.2 * math.sqrt(2))) if w > 0 else 1.0),
    ('Pareto, x_m 1 s, shape 3', lambda r: 1.0 * r.paretovariate(3.0), lambda w: 1.0 if w <= 1 else (1.0 / w) ** 3.0),
    ('Pareto, x_m 2 s, shape 1.1', lambda r: 2.0 * r.paretovariate(1.1), lambda w: 1.0 if w <= 2 else (2.0 / w) ** 1.1),
]
N_LAG, DELTA_LAG = 20000, 1e-4


def quantile_exact(G, a):
    lo, hi = 0.0, 1.0
    while G(hi) > a:
        hi *= 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if G(mid) > a:
            lo = mid
        else:
            hi = mid
    return hi


def lag_wait():
    rows = []
    for ti, (name, draw, G) in enumerate(TAILS):
        rng = random.Random(880 + ti)
        xs = sorted(draw(rng) for _ in range(N_LAG))
        for a in [1e-2, 1e-3, 1e-4]:
            exact = quantile_exact(G, a)
            cert = float('inf')
            for j in range(N_LAG - 1, -1, -1):        # wait = xs[j] leaves N_LAG-1-j exceedances
                exc = N_LAG - 1 - j
                if cp_upper_one_sided(exc, N_LAG, DELTA_LAG) <= a:
                    cert = xs[j]
                else:
                    break
            rows.append(dict(tail=name, alpha_lag=a, exact_wait=exact, certified_wait=cert,
                             n_lag=N_LAG, delta=DELTA_LAG, G_at_cert=G(cert) if cert < float('inf') else float('nan')))
            print(rows[-1])
    with open(os.path.join(RES, 'lag_wait.csv'), 'w', newline='') as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w_.writeheader()
        w_.writerows(rows)


if __name__ == '__main__':
    main()
