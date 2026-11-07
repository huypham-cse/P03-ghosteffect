#!/usr/bin/env python3
"""Analytic bound + simulation: Lemma 4.7 -- the content-carried nonce turns a look-alike screen into a text match.

Error model (stated in the paper, Sec. 5.2):
  * nonce: k symbols from Crockford base32 (m=32), written into a benign free-text field;
  * screen: M other k-symbol tokens visible (worst case: uniformly random over the alphabet);
  * OCR: each symbol independently suffers an error w.p. e_c (80% substitution, 10% deletion,
    10% insertion); the field is hidden/truncated w.p. eta (a PERSISTENT miss: every view misses);
  * matcher: accept if some visible token is within edit (Levenshtein) distance t of the nonce.
Analytic: eps1 <= eta + P[Bin(k,e_c) > t];  eps0 <= M |B_t| / m^k, where |B_t| bounds the number of
length-k strings within edit distance t of any token (|B_0| = 1, |B_1| <= k m).
Monte Carlo over 5 seeds x 40k screens validates eps1 (eps0 is far below MC resolution;
we report the Clopper-Pearson upper bound of the 0 observed false matches).
Before the nonce: VLM semantic judgement (eps0, eps1) = (0.12, 0.08) when no look-alike
effect is on screen, and an uninformative read (KL = 0) when a look-alike exists.
"""
import csv
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import sprt_exact, kl_pair, clopper_pearson, mean_ci

RES = os.path.join(os.path.dirname(__file__), '..', 'results')
ALPH = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'  # Crockford base32
M_TOK = 40
ETA = 0.01
SEEDS = [3, 5, 7, 11, 13]


def ball(k, t, m=32):
    """Max number of length-k strings within edit distance t of any token (t in {0,1})."""
    assert t in (0, 1)
    return 1 if t == 0 else k * m


def analytic(k, t, ec, eta=ETA, M=M_TOK):
    p_bin = 1 - sum(math.comb(k, j) * ec ** j * (1 - ec) ** (k - j) for j in range(t + 1))
    eps1 = eta + (1 - eta) * p_bin
    eps0 = min(1.0, M * ball(k, t) / 32 ** k)
    return eps0, eps1


def ocr(rng, s, ec):
    out = []
    for ch in s:
        if rng.random() < ec:
            u = rng.random()
            if u < 0.8:
                out.append(rng.choice(ALPH))
            elif u < 0.9:
                pass                                   # deletion
            else:
                out.append(ch)
                out.append(rng.choice(ALPH))           # insertion
        else:
            out.append(ch)
    return ''.join(out)


def ham(a, b):
    """Levenshtein distance (name kept for history)."""
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def mc(k, t, ec, seed, n=40000):
    rng = random.Random(seed * 101 + k * 7 + int(ec * 1000))
    fn = fp = 0
    for _ in range(n):
        nonce = ''.join(rng.choice(ALPH) for _ in range(k))
        others = [''.join(rng.choice(ALPH) for _ in range(k)) for _ in range(M_TOK)]
        # committed screen: nonce present (unless hidden)
        shown = others + ([] if rng.random() < ETA else [nonce])
        read = [ocr(rng, s, ec) for s in shown]
        if not any(ham(r, nonce) <= t for r in read):
            fn += 1
        # absent screen
        read0 = [ocr(rng, s, ec) for s in others]
        if any(ham(r, nonce) <= t for r in read0):
            fp += 1
    return fn, fp, n


def main():
    rows = []
    for k, t in [(4, 0), (6, 1), (8, 1)]:
        for ec in [0.005, 0.02, 0.05]:
            e0, e1 = analytic(k, t, ec)
            fns, fps, ns, rates = 0, 0, 0, []
            for s in SEEDS:
                fn, fp, n = mc(k, t, ec, s, n=8000)
                fns += fn
                fps += fp
                ns += n
                rates.append(fn / n)
            m1, ci1 = mean_ci(rates)
            _, fp_hi = clopper_pearson(fps, ns)
            e0m = max(e0, 1e-9)
            D1, D0 = kl_pair(e0m, e1)
            r1 = sprt_exact(e0m, e1, 1e-3, 1e-3, 1)
            r0 = sprt_exact(e0m, e1, 1e-3, 1e-3, 0)
            rows.append(dict(k=k, t=t, ec=ec, eps0_analytic=e0, eps1_analytic=e1, eps1_mc=m1,
                             eps1_mc_ci=ci1, fp_mc=fps, n_mc=ns, eps0_mc_hi=fp_hi,
                             D1=D1, D0=D0, EN=0.5 * (r1['EN'] + r0['EN']),
                             p_dup=r1['bot'], p_loss=r0['top']))
            print(rows[-1])
    # before-nonce reference rows
    e0, e1 = 0.12, 0.08
    D1, D0 = kl_pair(e0, e1)
    r1 = sprt_exact(e0, e1, 1e-3, 1e-3, 1)
    r0 = sprt_exact(e0, e1, 1e-3, 1e-3, 0)
    before = dict(vlm_eps0=e0, vlm_eps1=e1, vlm_D1=D1, vlm_D0=D0, vlm_EN=0.5 * (r1['EN'] + r0['EN']),
                  vlm_dup=r1['bot'], lookalike_D=0.0)
    print('before', before)
    with open(os.path.join(RES, 'nonce.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(RES, 'nonce_before.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(before.keys()))
        w.writeheader()
        w.writerow(before)


if __name__ == '__main__':
    main()
