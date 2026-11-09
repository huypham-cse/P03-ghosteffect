#!/usr/bin/env python3
"""GhostEffect core: noisy outcome oracle, SPRT recovery policy, exact DP, bounds.

Stdlib only. All randomness goes through explicitly seeded random.Random objects.

Conventions (match the paper, Sec. 3-4):
  X = 1  effect committed, X = 0 effect absent.
  A binary probe returns Y in {0,1}.  eps0 = P(Y=1 | X=0) (false "committed"),
  eps1 = P(Y=0 | X=1) (false "absent").
  L_n = sum_i log p1(Y_i)/p0(Y_i).  Stop with "committed" (do NOT retry) when L_n >= a,
  stop with "absent" (retry) when L_n <= -b.
  dup  = retry while X=1      -> controlled by b = log(1/alpha)
  loss = no retry while X=0   -> controlled by a = log(1/beta)
"""
import math
import random

LN = math.log


# ---------------------------------------------------------------- information quantities
def kl_bern(p, q):
    """KL(Bern(p) || Bern(q)) in nats."""
    out = 0.0
    if p > 0:
        out += p * LN(p / q)
    if p < 1:
        out += (1 - p) * LN((1 - p) / (1 - q))
    return out


def d_bin(x, y):
    """binary KL d(x||y)."""
    return kl_bern(x, y)


def kl_pair(eps0, eps1):
    """Return (D1, D0) = (KL(p1||p0), KL(p0||p1)) for the binary oracle."""
    p1 = 1 - eps1  # P(Y=1|X=1)
    p0 = eps0      # P(Y=1|X=0)
    return kl_bern(p1, p0), kl_bern(p0, p1)


def steps(eps0, eps1):
    """LLR increments: Y=1 -> +u, Y=0 -> -v."""
    u = LN((1 - eps1) / eps0)
    v = LN((1 - eps0) / eps1)
    return u, v


def thresholds(alpha, beta):
    """Strict (non-asymptotic) thresholds: P(loss)<=beta, P(dup)<=alpha (Thm 4.1(a))."""
    return LN(1 / beta), LN(1 / alpha)


def lower_bound(alpha, beta, eps0, eps1):
    """Wald-Wolfowitz / data-processing lower bounds on E1[N], E0[N] (Thm 4.1(c))."""
    D1, D0 = kl_pair(eps0, eps1)
    lb1 = d_bin(1 - alpha, beta) / D1
    lb0 = d_bin(1 - beta, alpha) / D0
    return lb1, lb0


def wald_approx(alpha, beta, eps0, eps1):
    """Wald's ASN approximation (no overshoot) for the strict thresholds."""
    D1, D0 = kl_pair(eps0, eps1)
    a, b = thresholds(alpha, beta)
    w1 = ((1 - alpha) * a - alpha * b) / D1
    w0 = ((1 - beta) * b - beta * a) / D0
    return w1, w0


def upper_bound(alpha, beta, eps0, eps1):
    """Rigorous overshoot-inclusive upper bound: E1[N] <= (a+u)/D1, E0[N] <= (b+v)/D0."""
    D1, D0 = kl_pair(eps0, eps1)
    a, b = thresholds(alpha, beta)
    u, v = steps(eps0, eps1)
    return (a + u) / D1, (b + v) / D0


# ---------------------------------------------------------------- exact DP (DTMC) for the SPRT
def sprt_exact(eps0, eps1, alpha, beta, x, n_max=None, cap=20000, model=None):
    """Exact exit probabilities of the binary SPRT random walk given X=x.

    Returns dict(top=P(decide committed), bot=P(decide absent), ask=P(hit n_max),
                 EN=E[N]).  This is the stdlib stand-in for the PRISM/Storm check.
    """
    a, b = thresholds(alpha, beta)
    u, v = steps(*(model if model is not None else (eps0, eps1)))  # policy's (possibly wrong) model
    q = (1 - eps1) if x == 1 else eps0  # P(Y=1) under the TRUE oracle
    # mass[k1] over continuing paths at level n
    mass = {0: 1.0}
    top = bot = 0.0
    EN = 0.0
    n = 0
    lim = n_max if n_max is not None else cap
    while mass and n < lim:
        n += 1
        new = {}
        for k1, m in mass.items():
            for y, py in ((1, q), (0, 1 - q)):
                if py == 0:
                    continue
                k = k1 + y
                L = k * u - (n - k) * v
                pm = m * py
                if L >= a - 1e-12:
                    top += pm
                    EN += pm * n
                elif L <= -b + 1e-12:
                    bot += pm
                    EN += pm * n
                else:
                    new[k] = new.get(k, 0.0) + pm
        mass = new
        if n_max is None and sum(mass.values()) < 1e-14:
            break  # remaining mass negligible (it never reaches exactly 0)
    rest = sum(mass.values())
    EN += rest * n
    return dict(top=top, bot=bot, ask=rest, EN=EN)


# ---------------------------------------------------------------- Monte Carlo SPRT
def sprt_run(rng, eps0_true, eps1_true, x, alpha, beta, eps0_model=None, eps1_model=None,
             n_max=10 ** 6, rho=0.0, lag_reads=0):
    """Run one SPRT episode.  Model params may differ from true ones (calibration study).

    rho: probability that a read repeats the previous read's *error status* (correlated
         VLM errors on re-reads of a similar screen).
    lag_reads: number of initial reads taken before the outcome is visible (they behave as
         if X=0), modelling an under-estimated lag Delta.
    Returns (decision, n) with decision in {'committed','absent','ask'}.
    """
    e0m = eps0_true if eps0_model is None else eps0_model
    e1m = eps1_true if eps1_model is None else eps1_model
    a, b = thresholds(alpha, beta)
    u, v = steps(e0m, e1m)
    L = 0.0
    n = 0
    prev_err = None
    while n < n_max:
        n += 1
        xv = 0 if n <= lag_reads else x
        perr = eps1_true if xv == 1 else eps0_true
        if prev_err is not None and rng.random() < rho:
            err = prev_err
        else:
            err = rng.random() < perr
        prev_err = err
        y = (1 - xv) if err else xv
        L += u if y == 1 else -v
        if L >= a:
            return 'committed', n
        if L <= -b:
            return 'absent', n
    return 'ask', n


# ---------------------------------------------------------------- statistics helpers
def binom_cdf(k, n, p):
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0 if k < n else 1.0
    s = 0.0
    lp, lq = LN(p), LN(1 - p)
    for i in range(0, k + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq)
    return min(1.0, s)


def clopper_pearson(k, n, conf=0.95):
    """Two-sided Clopper-Pearson interval via bisection on the binomial CDF."""
    lo_t = (1 - conf) / 2
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) >= lo_t)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) <= lo_t)
    return lower, upper


def cp_upper_one_sided(k, n, delta=0.05):
    """One-sided (1-delta) Clopper-Pearson upper bound on a Bernoulli rate."""
    if k == n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_cdf(k, n, mid) <= delta:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def mean_ci(xs, z=1.96):
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    # t critical for small n (two-sided 95%)
    tcrit = {2: 12.71, 3: 4.30, 4: 3.18, 5: 2.78, 6: 2.57, 7: 2.45, 8: 2.36, 9: 2.31, 10: 2.26}.get(n, z)
    return m, tcrit * math.sqrt(var / n)


def two_prop_z(k1, n1, k2, n2):
    """Two-proportion z test, two-sided p-value."""
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else 1e-12
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def mcnemar(b, c):
    """Exact two-sided McNemar test on discordant counts b, c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * binom_cdf(k, n, 0.5))


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (same order as input)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvals[i])
        run = max(run, val)
        adj[i] = run
    return adj
