#!/usr/bin/env python3
"""E5 (REAL): exact DTMC computation of the two-hop GhostRecover planner (stand-in for PRISM).

Planner (Alg. 1 restricted to one effect):
  stage 1: SPRT on the hop-1 probe (outbox / "sending" indicator) with budgets (a1, b1);
           "absent at hop 1" -> retry;   "present" & app has hop-2 guarantee G2 -> committed.
  stage 2 (non-G2 apps only): SPRT on the end-to-end probe with budgets (a2, b2), capped at
           n_max observations -> ask the user (resolves correctly at cost c_ask).
Hidden states: X1 (in outbox), X2 (server committed), X2 <= X1.
Exact P(dup), P(loss), P(ask), E[N] computed by composing exact SPRT exit distributions, and
compared with a Monte Carlo run of the *same* policy code.  The PRISM model in
artifact/prism/ghosteffect.pm encodes the symmetric-oracle instance for a Storm/PRISM re-check.
"""
import csv
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import sprt_exact, sprt_run, clopper_pearson

RES = os.path.join(os.path.dirname(__file__), '..', 'results')


def exact(cfg):
    h0, h1 = cfg['hop1_eps']
    e0, e1 = cfg['e2e_eps']
    a1, b1, a2, b2 = cfg['a1'], cfg['b1'], cfg['a2'], cfg['b2']
    nmax = cfg['n_max']
    out = {}
    # worst-case hidden states for each error type
    # dup: X2=1 (so X1=1).  retry happens if stage1 says absent, or stage2 says absent.
    s1 = sprt_exact(h0, h1, a1, b1, 1)
    if cfg['G2']:
        out['dup'] = s1['bot']
        out['EN_committed'] = s1['EN']
        out['ask_committed'] = 0.0
    else:
        s2 = sprt_exact(e0, e1, a2, b2, 1, n_max=nmax)
        out['dup'] = s1['bot'] + s1['top'] * s2['bot']
        out['EN_committed'] = s1['EN'] + s1['top'] * s2['EN']
        out['ask_committed'] = s1['top'] * s2['ask']
    # loss: worst case X1=1, X2=0 for non-G2 (stage-1 correctly passes, stage-2 must catch);
    #       X1=0 for G2 (stage 1 must catch).
    if cfg['G2']:
        s1x = sprt_exact(h0, h1, a1, b1, 0)
        out['loss'] = s1x['top']
        out['EN_absent'] = s1x['EN']
        out['ask_absent'] = 0.0
    else:
        s2x = sprt_exact(e0, e1, a2, b2, 0, n_max=nmax)
        out['loss'] = s1['top'] * s2x['top']
        out['EN_absent'] = s1['EN'] + s1['top'] * s2x['EN']
        out['ask_absent'] = s1['top'] * s2x['ask']
    return out


def mc(cfg, seed, n=200000):
    rng = random.Random(seed)
    h0, h1 = cfg['hop1_eps']
    e0, e1 = cfg['e2e_eps']
    dup = loss = ask = 0
    for _ in range(n):
        # committed world
        d, _ = sprt_run(rng, h0, h1, 1, cfg['a1'], cfg['b1'])
        if d == 'absent':
            dup += 1
        elif not cfg['G2']:
            d2, _ = sprt_run(rng, e0, e1, 1, cfg['a2'], cfg['b2'], n_max=cfg['n_max'] or 10 ** 6)
            dup += d2 == 'absent'
            ask += d2 == 'ask'
        # absent world (worst case as in exact())
        if cfg['G2']:
            d, _ = sprt_run(rng, h0, h1, 0, cfg['a1'], cfg['b1'])
            loss += d == 'committed'
        else:
            d, _ = sprt_run(rng, h0, h1, 1, cfg['a1'], cfg['b1'])
            if d == 'committed':
                d2, _ = sprt_run(rng, e0, e1, 0, cfg['a2'], cfg['b2'], n_max=cfg['n_max'] or 10 ** 6)
                loss += d2 == 'committed'
    return dup, loss, ask, n


def main():
    rows = []
    configs = []
    for G2 in [True, False]:
        for ee in [0.10, 0.20, 0.30]:
            for nmax in [None, 12]:
                if G2 and nmax is not None:
                    continue
                if G2 and ee != 0.20:
                    continue
                # round-1 split of alpha=beta=0.01 between hops (hop-1 is far more informative)
                configs.append(dict(G2=G2, hop1_eps=(0.03, 0.03), e2e_eps=(ee, ee),
                                    a1=0.002, b1=0.002,  # Alg. 1: hop 1 always gets 20% of the budget
                                    a2=0.008, b2=0.008, n_max=nmax))
    for i, c in enumerate(configs):
        ex = exact(c)
        d, l, a, n = mc(c, 777 + i)
        _, dhi = clopper_pearson(d, n)
        _, lhi = clopper_pearson(l, n)
        rows.append(dict(G2=int(c['G2']), e2e_eps=c['e2e_eps'][0], n_max=c['n_max'] or 0,
                         budget=0.01, exact_dup=ex['dup'], mc_dup=d / n, mc_dup_hi=dhi,
                         exact_loss=ex['loss'], mc_loss=l / n, mc_loss_hi=lhi,
                         exact_ask=ex['ask_committed'], mc_ask=a / n,
                         EN=0.5 * (ex['EN_committed'] + ex['EN_absent'])))
        print(rows[-1])
    with open(os.path.join(RES, 'markov_planner.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_prism()


def write_prism():
    """Symmetric-oracle instance; thresholds in LLR units of u = log((1-e)/e)."""
    e = 0.2
    al = 0.008
    u = math.log((1 - e) / e)
    A = math.ceil(math.log(1 / al) / u)
    path = os.path.join(os.path.dirname(__file__), '..', 'prism')
    os.makedirs(path, exist_ok=True)
    pm = f"""// GhostEffect stage-2 recovery planner as a DTMC (PRISM / Storm input).
// Generated by artifact/scripts/markov_planner.py.  Symmetric oracle eps={e}; budgets alpha=beta={al}.
// d = (#reads saying committed) - (#reads saying absent); stop at d>=A (committed) or d<=-A (absent);
// n counts reads; at n=NMAX without a decision the planner asks the user.
dtmc

const double pi;            // prior P(X=1); results are reported conditional on x via filters
const double eps = {e};
const int A = {A};          // ceil(log(1/alpha) / log((1-eps)/eps))
const int NMAX = 12;

module planner
  x : [0..1] init 0;        // hidden outcome, drawn in the first step
  init_done : bool init false;
  d : [-A..A] init 0;
  n : [0..NMAX] init 0;
  dec : [0..3] init 0;      // 0 none, 1 committed (no retry), 2 absent (retry), 3 ask

  [] !init_done -> pi : (x'=1)&(init_done'=true) + (1-pi) : (x'=0)&(init_done'=true);
  [] init_done & dec=0 & d<A & d>-A & n<NMAX & x=1 ->
        (1-eps) : (d'=min(d+1,A))&(n'=n+1) + eps : (d'=max(d-1,-A))&(n'=n+1);
  [] init_done & dec=0 & d<A & d>-A & n<NMAX & x=0 ->
        eps : (d'=min(d+1,A))&(n'=n+1) + (1-eps) : (d'=max(d-1,-A))&(n'=n+1);
  [] init_done & dec=0 & d>=A -> (dec'=1);
  [] init_done & dec=0 & d<=-A -> (dec'=2);
  [] init_done & dec=0 & d<A & d>-A & n=NMAX -> (dec'=3);
  [] dec>0 -> true;
endmodule

label "dup"  = dec=2 & x=1;
label "loss" = dec=1 & x=0;
label "ask"  = dec=3;
label "done" = dec>0;

rewards "obs"
  init_done & dec=0 & d<A & d>-A & n<NMAX : 1;
endrewards
"""
    props = """// P(dup | X=1) and P(loss | X=0): run with -const pi=1 and pi=0 respectively.
P=? [ F "dup" ]
P=? [ F "loss" ]
P=? [ F "ask" ]
R{"obs"}=? [ F "done" ]
"""
    open(os.path.join(path, 'ghosteffect.pm'), 'w').write(pm)
    open(os.path.join(path, 'ghosteffect.props'), 'w').write(props)
    # the same instance computed by our DP for cross-checking once PRISM/Storm is run
    r1 = sprt_exact(e, e, al, al, 1, n_max=12)
    r0 = sprt_exact(e, e, al, al, 0, n_max=12)
    with open(os.path.join(RES, 'prism_instance_dp.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['eps', 'alpha', 'A', 'NMAX', 'P_dup_given_x1', 'P_loss_given_x0', 'P_ask_x1', 'EN_x1'])
        w.writerow([e, al, A, 12, r1['bot'], r0['top'], r1['ask'], r1['EN']])
    print('PRISM instance DP:', r1, r0)


if __name__ == '__main__':
    main()
