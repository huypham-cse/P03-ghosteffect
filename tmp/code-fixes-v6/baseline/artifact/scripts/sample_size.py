#!/usr/bin/env python3
"""Required calibration sizes (exact one-sided Clopper-Pearson; paper Sec. 5.3 / Table 'tab:nsize').

For a budget alpha, the planner's shares are alpha_test = 0.5 alpha, alpha_lag = 0.4 alpha (split into two
certified waits of 0.2 alpha each when the app has a hop-1 family), and K delta = 0.1 alpha with
K = 11 (product certification, Prop. 4.3) or K = 5 (joint certification, Prop. 4.4).

Columns (smallest n such that the bound certifies its target):
  prod_n      MEDIAN-CASE: effects per (app version, outcome) so that each of TWO families with true wrong-verdict
              rate p, observed at its expected count ceil(p n), gets a CP bound <= sqrt(alpha_test) (A2); about half
              of calibration sets of this size fail to certify
  prod_n0     ZERO-EVENT minimum for the same (no wrong verdict observed; a lower bound for any p)
  joint_n     ZERO-EVENT minimum: whole effects so that the joint retry region certifies alpha_test (no A2)
  joint_n_q   MEDIAN-CASE at a true region rate alpha_test/4 (expected count ceil(alpha_test n / 4))
  joint_n_k   the same for a single-effect step of a 3-effect workflow (alpha_test / 3)
  lag_n       logged commit-to-visibility times so that a wait certifies 0.2 alpha with zero exceedances
  *_key       the same per fault class when keyed by the 4 observable classes (delta / 4); total = 4 x *_key
  lag_n_full  one wait at the whole lag share 0.4 alpha (an app without a hop-1 family, e.g. Element)
"""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import cp_upper_one_sided

RES = os.path.join(os.path.dirname(__file__), '..', 'results')


def n_zero(target, delta):
    """smallest n with CP(0, n, delta) = 1 - delta^(1/n) <= target."""
    return math.ceil(math.log(delta) / math.log(1 - target))


def n_rate(target, delta, p, lo=10, hi=10 ** 7):
    """smallest n with CP(ceil(p n), n, delta) <= target (bisection; CP decreases in n for fixed rate)."""
    if p >= target:
        return float('inf')
    ok = lambda n: cp_upper_one_sided(math.ceil(p * n), n, delta) <= target
    while not ok(hi):
        return float('inf')
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    rows = []
    for alpha in (1e-2, 1e-3):
        a_test, a_wait = 0.5 * alpha, 0.2 * alpha
        dp, dj = alpha / 110, alpha / 50
        for p in (0.005, 0.01):
            rows.append(dict(alpha=alpha, p=p, delta_prod=dp, delta_joint=dj,
                             prod_n=n_rate(math.sqrt(a_test), dp, p), prod_n0=n_zero(math.sqrt(a_test), dp),
                             joint_n=n_zero(a_test, dj), joint_n_q=n_rate(a_test, dj, a_test / 4),
                             joint_n_k=n_zero(a_test / 3, dj),
                             lag_n=n_zero(a_wait, dp)))
            # keyed by the 4 observable fault classes: each class needs its own labels, certified at delta/4 (the
            # unknown-class fallback uses every class's bounds), so the total is 4 x (per-class size at delta/4)
            dk, djk = dp / 4, dj / 4
            rows[-1].update(prod_n_key=n_rate(math.sqrt(a_test), dk, p), prod_n0_key=n_zero(math.sqrt(a_test), dk),
                            joint_n_key=n_zero(a_test, djk), joint_n_q_key=n_rate(a_test, djk, a_test / 4),
                            joint_n_k_key=n_zero(a_test / 3, djk), lag_n_key=n_zero(a_wait, dk),
                            lag_n_full=n_zero(0.4 * alpha, dp), lag_n_full_key=n_zero(0.4 * alpha, dk))
            print(rows[-1])
    with open(os.path.join(RES, 'sample_size.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    main()
