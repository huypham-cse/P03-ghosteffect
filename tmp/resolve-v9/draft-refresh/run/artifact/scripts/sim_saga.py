#!/usr/bin/env python3
"""E3 (REAL): Proposition 4 -- KKT-optimal duplicate/loss budget allocation across a saga.

For k-step workflows with heterogeneous oracles (eps0_i, eps1_i ~ U[0.03, 0.30]) and priors
pi_i ~ U[0.3, 0.7], total budgets alpha = beta = 0.01:
  * closed-form allocation alpha_i = alpha * w_i / sum w,  w_i = (1-pi_i)/D0_i
                           beta_i  = beta  * v_i / sum v,  v_i = pi_i/D1_i
  * uniform split alpha_i = alpha/k, beta_i = beta/k
Expected observations are computed EXACTLY by DP for both allocations; the end-to-end
duplicate probability (worst case: every step committed) is computed exactly as
1 - prod(1 - P_i(dup)) and must be <= alpha.  Also reports the predicted saving
W * KL(w_hat || uniform) from Prop. 4.9.
"""
import csv
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import sprt_exact, kl_pair, mean_ci

RES = os.path.join(os.path.dirname(__file__), '..', 'results')
ALPHA = BETA = 0.01
WF_PER_K = 200


def total_obs(steps, alphas, betas):
    tot = 0.0
    e2e_dup = 1.0
    e2e_loss = 1.0
    for (e0, e1, pi), ai, bi in zip(steps, alphas, betas):
        r1 = sprt_exact(e0, e1, ai, bi, 1)
        r0 = sprt_exact(e0, e1, ai, bi, 0)
        tot += pi * r1['EN'] + (1 - pi) * r0['EN']
        e2e_dup *= (1 - r1['bot'])
        e2e_loss *= (1 - r0['top'])
    return tot, 1 - e2e_dup, 1 - e2e_loss


def main():
    rows, summ = [], []
    for k in [2, 4, 8, 16]:
        rng = random.Random(500 + k)
        sav, pred, dups, losses, opt_tot, uni_tot = [], [], [], [], [], []
        naive_dups = []
        for wf in range(WF_PER_K):
            steps = []
            for i in range(k):
                steps.append((rng.uniform(0.03, 0.30), rng.uniform(0.03, 0.30), rng.uniform(0.3, 0.7)))
            w = []
            v = []
            for e0, e1, pi in steps:
                D1, D0 = kl_pair(e0, e1)
                w.append((1 - pi) / D0)
                v.append(pi / D1)
            W, V = sum(w), sum(v)
            a_opt = [ALPHA * wi / W for wi in w]
            b_opt = [BETA * vi / V for vi in v]
            a_uni = [ALPHA / k] * k
            b_uni = [BETA / k] * k
            t_opt, d_opt, l_opt = total_obs(steps, a_opt, b_opt)
            t_uni, d_uni, l_uni = total_obs(steps, a_uni, b_uni)
            t_nai, d_nai, l_nai = total_obs(steps, [ALPHA] * k, [BETA] * k)
            naive_dups.append(d_nai)
            # predicted saving (Wald objective): W*KL(w_hat||u) + V*KL(v_hat||u)
            p = sum(wi * math.log(k * wi / W) for wi in w) + sum(vi * math.log(k * vi / V) for vi in v)
            sav.append(100 * (t_uni - t_opt) / t_uni)
            pred.append(100 * p / t_uni)
            dups.append(d_opt)
            losses.append(l_opt)
            opt_tot.append(t_opt)
            uni_tot.append(t_uni)
            if wf < 3:
                rows.append(dict(k=k, wf=wf, t_opt=t_opt, t_uni=t_uni, e2e_dup=d_opt, e2e_loss=l_opt))
        sm, sci = mean_ci(sav)
        pm, pci = mean_ci(pred)
        om, oci = mean_ci(opt_tot)
        um, uci = mean_ci(uni_tot)
        srt = sorted(sav)
        summ.append(dict(k=k, n_wf=WF_PER_K, obs_opt=om, obs_opt_ci=oci, obs_uni=um, obs_uni_ci=uci,
                         saving_pct=sm, saving_ci=sci, saving_p90=srt[int(0.9 * len(srt))],
                         pred_saving_pct=pm, max_e2e_dup=max(dups), max_e2e_loss=max(losses),
                         frac_worse=sum(s < 0 for s in sav) / len(sav),
                         naive_e2e_dup_mean=sum(naive_dups) / len(naive_dups),
                         naive_e2e_dup_max=max(naive_dups)))
        print(summ[-1])
    with open(os.path.join(RES, 'saga_alloc.csv'), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(summ[0].keys()))
        wr.writeheader()
        wr.writerows(summ)

    # mixed-probe workflows, objective in SECONDS (Prop. 4.9 with costs c_i):
    # probe types: nonce text match, hop-1 indicator, on-screen VLM read, deep VLM read
    # (navigate to a history screen).  w_i = c_i (1-pi_i)/D0_i,  v_i = c_i pi_i/D1_i.
    PT = {'nonce': (lambda r: (1e-6, 0.02), 1.2), 'hop1': (lambda r: (0.03, 0.03), 1.5),
          'vlm': (lambda r: (r.uniform(0.06, 0.26), r.uniform(0.04, 0.20)), 2.5),
          'vlm-deep': (lambda r: (r.uniform(0.06, 0.26), r.uniform(0.04, 0.20)), 8.0)}
    mix = []
    for k in [4, 8]:
        rng = random.Random(1300 + k)
        sv, so, su = [], [], []
        for wf in range(WF_PER_K):
            steps, cost = [], []
            for i in range(k):
                name = rng.choice(list(PT))
                e0, e1 = PT[name][0](rng)
                steps.append((e0, e1, rng.uniform(0.3, 0.7)))
                cost.append(PT[name][1])
            w, v = [], []
            for (e0, e1, pi), c in zip(steps, cost):
                D1, D0 = kl_pair(e0, e1)
                w.append(c * (1 - pi) / D0)
                v.append(c * pi / D1)
            a_opt = [ALPHA * x / sum(w) for x in w]
            b_opt = [BETA * x / sum(v) for x in v]
            def secs(al, be):
                t = 0.0
                for (e0, e1, pi), c, ai, bi in zip(steps, cost, al, be):
                    r1 = sprt_exact(e0, e1, ai, bi, 1)
                    r0 = sprt_exact(e0, e1, ai, bi, 0)
                    t += c * (pi * r1['EN'] + (1 - pi) * r0['EN'])
                return t
            t_o = secs(a_opt, b_opt)
            t_u = secs([ALPHA / k] * k, [BETA / k] * k)
            sv.append(100 * (t_u - t_o) / t_u)
            so.append(t_o)
            su.append(t_u)
        m, ci = mean_ci(sv)
        om, oci = mean_ci(so)
        um, uci = mean_ci(su)
        mix.append(dict(k=k, secs_opt=om, secs_opt_ci=oci, secs_uni=um, secs_uni_ci=uci,
                        saving_pct=m, saving_ci=ci, saving_max=max(sv)))
        print('mix', mix[-1])
    with open(os.path.join(RES, 'saga_mixed.csv'), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(mix[0].keys()))
        wr.writeheader()
        wr.writerows(mix)


if __name__ == '__main__':
    main()
