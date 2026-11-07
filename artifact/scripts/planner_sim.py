#!/usr/bin/env python3
"""Model-based simulation (paper Sec. 7): GhostRecover vs baselines under 12,000 paired interrupted workflows,
plus misspecification / stress experiments, calibration-population and sample-size studies.

This is a MODEL-BASED SIMULATION of the recovery decision problem, not a device measurement.
The generative model (apps, faults, outcomes, probe errors, lags, user answers) is stated below and
in the paper.  It deliberately differs from the planner's assumptions: persistent nonce misses, within-view
correlated VLM errors, cross-view correlation, persistent hop-1/digest failures, lags beyond the wait,
retry-capped / force-stopped clients, Doze, common-mode stale history after a restart, optimistic list
entries for tapped-but-uncommitted effects, a fallible Monitor, and an imperfect, slow user.

If artifact/results/real/params.csv exists (written from emulator measurements), `real_overrides()` maps its
rows onto the generative parameters and the 'measured' scenario uses them; see paper Sec. 7.

Policies
  redo, ckpt                     AgentProg-style redo / LangGraph-style checkpoint replay
  atomix, atomix-durable         Atomix-style port with in-memory / durable dedup + one read-back
  verify                         one VLM read at 5 s taken as truth
  key                            ledger + nonce, one exact read (GUI analogue of Li's keys)
  key-ask                        key, but ask when a look-alike is present and there is no nonce
  always-ask                     ledger + ask the user about every ambiguous effect
  nonce-ask                      ledger + nonce family verdict; ask when the app has no nonce field
  maj3-ask                       ledger + 3 VLM views; act on unanimity, ask on disagreement
  rules, rules-lenient           SAME evidence as GhostEffect (ledger, hop-1 + fallible Monitor, nonce, digest,
                                 VLM, fixed 10 s wait, ask) with deterministic rules instead of certification:
                                 'rules' acts only when every available family agrees (R1's rule set);
                                 'rules-lenient' acts on the first unanimous family unless another contradicts
  ghost-v1                       round-1 GhostRecover (re-reads, view rotation + AR(1) shrinkage)
  ghost                          GhostRecover, per-family calibration, product certification (Prop. 4.3; A2)
  ghost-joint                    GhostRecover, JOINT calibration of the cascade's retry/declare regions on whole
                                 effects (Prop. 4.4; no cross-family independence assumption)
  ghost-*                        ablations of the product planner
"""
import csv
import math
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from ge_core import kl_pair, cp_upper_one_sided, clopper_pearson, mcnemar, holm, binom_cdf

RES = os.path.join(os.path.dirname(__file__), '..', 'results')
SEEDS = [101, 202, 303, 404, 505]
N_PER_SEED = 2400
N_MAX_V1 = 14
T_VLM, T_OCR, T_HOP1, T_WAIT_BASE, T_ASK, T_RETRY = 2.5, 1.2, 1.5, 5.0, 60.0, 12.0
T_RULES_WAIT = 10.0          # fixed wait of the same-evidence rule baselines
W_MAX = 120.0                # longest additional blocking wait the planner accepts before asking instead
MON_STUCK = 120.0            # a hop-1 entry pending longer than this is handed to the end-to-end path
NCAL = 2000                  # calibration EFFECTS per (app, outcome); every family is read on each effect
N_LAG = 20000
V = dict(hop1=2, nonce=2, digest=2, vlm=3)       # distinct views per probe family
NONCE_EPS0_VIEW = 40 * 6 * 32 / 32 ** 6         # Lemma 4.7, edit distance t=1: M k m / m^k, k=6, M=40
# K = number of Clopper-Pearson bounds one effect's decision can use (Lemma 4.6(ii)); delta = alpha / (10 K).
#   product (Prop. 4.3): abs levels hop1 1 + nonce 1 + digest 1 + VLM 2, com levels hop1 1 + digest 1 + VLM 2
#   (the nonce's com bound is analytic), plus the two certified waits w1, w0             -> K = 11
#   joint (Prop. 4.4): retry region 1 + declare region 1 + q_h 1 + waits 2             -> K = 5
#   source families (hop-1 x jointly calibrated history): history regions 2 per side + hop-1 2 + waits 2  -> K = 8
K_PRODUCT, K_JOINT, K_SRC = 11, 5, 8

# app catalogue.  G2 = retry-until-ack + server dedup; hop1 = local outbox/status observable;
# nfield = kind of free-text field for the nonce; digest = history list enumerable via a11y;
# look = P(look-alike visible); local = no server; durable = outbox survives app kill.
APPS = {
    'sms':      dict(G2=False, hop1=True,  nfield='visible', digest=True,  look=0.15, local=False, durable=True),
    'mail':     dict(G2=False, hop1=True,  nfield='visible', digest=True,  look=0.10, local=False, durable=True),
    'calendar': dict(G2=True,  hop1=True,  nfield='private', digest=True,  look=0.25, local=False, durable=True),
    'chat':     dict(G2=True,  hop1=True,  nfield='visible', digest=True,  look=0.20, local=False, durable=False),
    'bank':     dict(G2=False, hop1=False, nfield='private', digest=True,  look=0.60, local=False, durable=True),
    'expense':  dict(G2=True,  hop1=True,  nfield='private', digest=True,  look=0.30, local=True,  durable=True),
    'contacts': dict(G2=True,  hop1=True,  nfield='private', digest=True,  look=0.05, local=True,  durable=True),
    'shop':     dict(G2=False, hop1=False, nfield='none',    digest=False, look=0.30, local=False, durable=True),
}
# MEASURED profiles (paper Sec. 7.8; artifact/results/real/, campaign 2): only used when S['catalog'] == 'measured'.
#   element: Element 1.6.62 + Synapse.  Measured (campaign 2, screen-validating reader): G2 (same-txnId re-send or
#            /sync reconciliation, 83/83 exactly once); the send-state indicator is drawn on the timeline row in the same
#            dump as the row (101/101), so it is NOT a lag-free hop-1 view: the planner has no hop-1 family and the
#            indicator is merged into the row (nonce) family; digest = room-list snippet.  Visibility lag after recovery
#            is drawn per fault class from the measured per-trial intervals (upper ends), with the measured lag-blind
#            first reads; late reads are never wrong (0/99) but all families are bot (no observation) together in 2/101.
#   k9:      K-9 Mail 24.0 + GreenMail (SMTP), no Sent folder.  Measured: a post-'.' failure sets a permanent error
#            state; the mail stays in the Outbox and is never re-sent by the app; queued mail goes out at the next sync.
#            hop-1 = Outbox listing; no end-to-end family in the UI.
#   k9sent:  the same with an IMAP Sent folder.  The Sent list is CLIENT-written: an acknowledged mail appears 3.3-5.3 s
#            after Send, a committed mail whose reply was lost never appears (0/8), so it errs together with the Outbox.
APPS_MEASURED = {
    'element': dict(G2=True,  hop1=False, nfield='visible', digest=True,  look=0.20, local=False, durable=True,
                    profile='element', entry_e2e=True),
    'k9':      dict(G2=False, hop1=True, nfield='none',    digest=False, look=0.10, local=False, durable=True,
                    profile='k9'),
    'k9sent':  dict(G2=False, hop1=True, nfield='none',    digest=True,  look=0.10, local=False, durable=True,
                    profile='k9', sent=True),
}
ALL_APPS = dict(APPS, **APPS_MEASURED)


def catalog(S):
    return APPS_MEASURED if S.get('catalog') == 'measured' else APPS


FAULTS = [('agent-kill', 0.30), ('app-kill', 0.25), ('net-blackout', 0.30), ('kill+net', 0.15)]
CLASSES = [f for f, _ in FAULTS]          # observable fault classes (agent restart, app pid change, connectivity event)
# Element: which measured cell supplies the lag of a committed effect, by fault class (point 'post' = acknowledged)
ELEM_CELL = {'agent-kill': 'floor', 'app-kill': 'appdeath', 'net-blackout': 'net', 'kill+net': 'appdeath'}
POINTS = [('pre', 0.20), ('mid', 0.25), ('inflight', 0.35), ('post', 0.20)]

# generative-model scenarios.  'default' is the main evaluation world; 'r1' reproduces the round-1
# assumptions (i.i.d. re-reads, AR(1) VLM correlation 0.2, no persistent failures).
# cal_pop: 'passive' = calibration labels from uninterrupted effects (confirmation seen / form abandoned) and
# passively logged lags; 'fault' = fault-injected calibration on test accounts, i.e. drawn from the interrupted
# population (stale history after restart, optimistic entries, interrupted-effect lag law).
BASE = dict(nonce_persist=0.01, nonce_view=0.006, nonce_iid=None, vlm_rho_w=0.6, vlm_rho_x=0.1,
            hop1_persist=0.005, digest_persist=0.02, digest_view=0.03, digest_false=0.01,
            iid_rereads=False, lag_heavy=0.0, g2_break=0.0, doze=0.0, doze_aware=True,
            common_mode=0.0, optimistic=0.0, user_err=0.05, nonce_policy='private', look_scale=1.0, g2_all=None,
            nfield_none=False, mon_err=0.01, cal_pop='passive', ncal_scale=1.0, kappa=1.0, shift_test=0,
            g2_nodedup=0.0, g2_sigma=0.6,
            # measured-profile parameters (defaults leave every model-based experiment unchanged)
            catalog='default', only_app=None, no_vlm=False, g2_lag_emp=None, blind=0.0, blind_digest=0.0,
            hop1_persist1=None, hop1_view1=None, k9_failed_commit=0.0, k9_queued_delivered=0.0,
            k9_lag_lo=45.0, k9_lag_hi=900.0,
            # campaign-2 measured-profile parameters and calibration options
            elem_lag=None, bot_late=0.0, lag_tail=0.0, lag_tail_cal=False, lag_tail_lo=14.0, lag_tail_hi=300.0,
            keyed=None, cal_faults=None, class_known=1.0, k9_sent_lo=3.3, k9_sent_hi=5.3,
            # round 4 (R2 R4-1, R4-2): downtime (s) between ISSUED and the class's observable clock origin (relaunch for app
            # death, connectivity restore for network loss; for agent death the origin is t0 itself), which clock the
            # planner waits on ('origin' = per-class observable origin r_e, the design; 't0' = ISSUED for every class,
            # the round-3 text), and the number of logged lags per class (None = N_LAG, a bootstrap of the measured trials)
            downtime=0.0, clock='origin', nlag=None)
IWORLD = dict(common_mode=0.02, optimistic=0.03, lag_heavy=0.2)     # 'interrupted-population' world
SCEN = {
    'default': {},
    'r1': dict(nonce_persist=0.0, nonce_view=0.0, nonce_iid=0.0156, vlm_rho_w=0.2, vlm_rho_x=0.0,
               hop1_persist=0.0, digest_persist=0.0, digest_view=0.03, digest_false=0.01, iid_rereads=True,
               user_err=0.0, mon_err=0.0),
    'r1+persist': dict(nonce_persist=0.01, nonce_view=0.006, nonce_iid=None, vlm_rho_w=0.2, vlm_rho_x=0.0,
                       hop1_persist=0.0, digest_persist=0.0, iid_rereads=True, user_err=0.0, mon_err=0.0),
    'cross0.3': dict(vlm_rho_x=0.3),
    'lagtail': dict(lag_heavy=0.5),
    'lagtail-cal': dict(lag_heavy=0.5, cal_pop='fault'),
    'g2break': dict(g2_break=0.3),
    'g2nodedup': dict(g2_nodedup=0.3),
    'doze-unaware': dict(doze=0.5, doze_aware=False),
    'doze-aware': dict(doze=0.5, doze_aware=True),
    'common0.5': dict(common_mode=0.005),
    'user0.2': dict(user_err=0.2),
    'mon0.05': dict(mon_err=0.05),
    'combined': dict(vlm_rho_x=0.3, lag_heavy=0.5, g2_break=0.3, doze=0.5, doze_aware=True, user_err=0.1),
    'iworld-passive': dict(IWORLD, cal_pop='passive'),
    'iworld-fault': dict(IWORLD, cal_pop='fault'),
}
for _cm in (0.005, 0.02, 0.05):
    SCEN[f'cm{_cm}-fault'] = dict(common_mode=_cm, cal_pop='fault')
ALL_POLICIES = ['redo', 'ckpt', 'atomix', 'atomix-durable', 'verify', 'key', 'key-ask', 'always-ask',
                'nonce-ask', 'maj3-ask', 'rules', 'rules-lenient', 'ghost-v1', 'ghost', 'ghost-src', 'ghost-joint',
                'ghost-nononce', 'ghost-nohop1', 'ghost-nodigest', 'ghost-nocal', 'ghost-uniform', 'ghost-noask',
                'ghost-visible']
# parameterised same-evidence rule family (R2 m8): fixed wait (s) x quorum ('all' = every available family agrees,
# 'novlm' = every family except the VLM, 'two' = any two families agree and none contradicts)
RULE_FAMILY = [f'rules-w{w}-{q}' for w in (5, 10, 30, 60) for q in ('all', 'novlm', 'two')]
# 'app-state': trust the app's own status view (measured profiles); 'g2-only': Theorem 4.8 alone (R1 M3): classify the
# app's G2 status offline, never retry; declare when a G2 app's hop-1 entry exists (and is not failed), else ask.
EXTRA_POLICIES = ['app-state', 'g2-only'] + RULE_FAMILY + ['rules-vetted', 'rules-vetted-small']


def pick(rng, table):
    r, acc = rng.random(), 0.0
    for name, p in table:
        acc += p
        if r < acc:
            return name
    return table[-1][0]


def scen(name):
    s = dict(BASE)
    s.update(SCEN[name])
    return s


def app_cfg(app, S):
    A = dict(ALL_APPS[app])
    if S['g2_all'] is not None:
        A['G2'] = (S['g2_all'] and A['hop1']) or A['local']
    if S.get('nfield_none'):
        A['nfield'] = 'none'
    return A


def g2_lag(rng, S):
    if S.get('g2_lag_emp'):
        return rng.choice(S['g2_lag_emp'])            # measured: Element restart-to-'Sent' lags (bootstrap)
    return rng.uniform(0, 30) + rng.lognormvariate(math.log(20), S['g2_sigma'])


# ------------------------------------------------------------------ world generation
def make_world(rng, S):
    k = pick(rng, [(1, 0.4), (2, 0.3), (3, 0.2), (4, 0.1)])
    if S.get('only_app'):
        apps = [S['only_app']] * k
    else:
        apps = [rng.choice(list(catalog(S))) for _ in range(k)]
    n_int = 2 if (k >= 2 and rng.random() < 0.25) else 1
    ints = sorted(rng.sample(range(k), n_int))
    return [_effect(rng, S, app, i, i in ints) for i, app in enumerate(apps)]


def _effect(rng, S, app, i, interrupted, cal=False, force_fault=None):
    """cal=True: a calibration (lab) effect, whose fault class follows S['cal_faults'] if set (lab mix != deployment
    mix) and which carries the unlogged lag tail only if S['lag_tail_cal'].  force_fault: draw within one class."""
    A = app_cfg(app, S)
    e = dict(app=app, interrupted=interrupted, X=1, X1=1, lag=0.0,
             look=rng.random() < min(1.0, A['look'] * S['look_scale']),
             node_first=(i % 2 == 0), idx=i, fault=None, point=None, status='sent', doze=False,
             stale=False, optim=False, appdup=False, u=rng.random(), heavy=False,
             first_abs=False, bot=False, never=False)
    if e['interrupted']:
        e['doze'] = rng.random() < S['doze']              # device idle during a delayed recovery
        f, p = pick(rng, (S.get('cal_faults') if cal and S.get('cal_faults') else FAULTS)), pick(rng, POINTS)
        if force_fault is not None:
            f = force_fault
        e['fault'], e['point'] = f, p
        if S.get('class_known', 1.0) < 1.0:
            e['cls_known'] = rng.random() < S['class_known']
        if p == 'pre':
            X1, X = 0, 0
        elif p == 'mid':
            X1 = 1 if rng.random() < 0.5 else 0
            X = X1
        else:
            X1, X = 1, 1
        if X1 == 1 and f in ('app-kill', 'kill+net') and p in ('mid', 'inflight') \
                and not A['durable'] and rng.random() < 0.5:
            X1, X = 0, 0                                   # in-memory outbox lost
        lag, status = 0.0, ('sent' if X1 else 'none')
        if A['local']:
            X = X1
        elif p == 'inflight' and X1 == 1:
            if f in ('net-blackout', 'kill+net'):
                if A['G2']:
                    X, status = 1, 'pending'
                    lag = g2_lag(rng, S)
                else:
                    X = 1 if rng.random() < 0.4 else 0
                    lag = rng.uniform(0.5, 3.0)
                    status = 'sent' if X else 'failed'
            elif f == 'app-kill':
                if rng.random() < 0.5:
                    X, lag = 1, rng.uniform(0.5, 3.0)
                elif A['G2']:
                    X, lag, status = 1, (g2_lag(rng, S) if S.get('g2_lag_emp') else rng.uniform(5, 40)), 'pending'
                else:
                    X, status = 0, 'failed'
            else:
                X, lag = 1, rng.uniform(0.5, 3.0)
            # stress: heavy-tailed non-G2 visibility lag (deployment differs from passive logs)
            if not A['G2'] and X == 1 and rng.random() < S['lag_heavy']:
                lag, e['heavy'] = 2.0 * rng.paretovariate(1.1), True
            # stress: delayed recovery while the device dozes defers hop-2 to a maintenance window
            if X == 1 and e['doze']:
                lag += rng.uniform(60, 900)
            # stress: G2 violated (retry cap reached / force-stop cancels the WorkManager job)
            if A['G2'] and status == 'pending' and rng.random() < S['g2_break']:
                applied = rng.random() < 0.3              # a transmission landed, ack lost, client gave up
                X = 1 if applied else 0
                status = 'failed' if rng.random() < 0.7 else 'stuck'
                if not applied:
                    lag = 0.0
            # stress: app classified G2 but its server does not deduplicate -> app-induced duplicate
            if A['G2'] and status == 'pending' and rng.random() < S['g2_nodedup']:
                e['appdup'] = True
        elif X == 1:
            lag = rng.uniform(0.2, 2.0)
        if A.get('profile') == 'k9' and X1 == 1:
            # measured (K-9): a transmission whose response was lost after the server committed is shown as
            # unsent (Outbox + failure notification) and never re-sent; a queued, untransmitted message stays in
            # the Outbox and is delivered once, at the next sync (lag law: assumption, see params.csv)
            if p == 'inflight' and f in ('net-blackout', 'kill+net') and X == 1 \
                    and rng.random() < S['k9_failed_commit']:
                status = 'failed'
            elif X == 0 and rng.random() < S['k9_queued_delivered']:
                X, lag, status = 1, rng.uniform(S['k9_lag_lo'], S['k9_lag_hi']), 'pending'
        if A.get('sent') and X == 1:
            # measured (K-9 + IMAP Sent): the Sent copy is written by the client after a successful send (APPEND 3.3-5.3 s
            # after Send); a committed mail in the failed state never appears there (0/8)
            if status == 'failed':
                e['never'] = True
            elif status == 'sent':
                lag = rng.uniform(S['k9_sent_lo'], S['k9_sent_hi'])
        if A.get('profile') == 'element' and S.get('elem_lag') and X == 1:
            # measured (Element, campaign 2): recovery-to-visible lag (row = indicator) of a measured trial of the same
            # fault class, with its first verified read (lag-blind 'absent' or not); acknowledged sends use the restart floor
            cell = ('acked' if f in ('app-kill', 'kill+net') else 'floor') if p == 'post' else ELEM_CELL[f]
            lag, fl = rng.choice(S['elem_lag'][cell])
            e['first_abs'] = bool(fl)
            if S['lag_tail'] > 0 and rng.random() < S['lag_tail'] and (not cal or S['lag_tail_cal']):
                lag, e['first_abs'], e['heavy'] = rng.uniform(S['lag_tail_lo'], S['lag_tail_hi']), True, True
        e['X'], e['X1'], e['lag'], e['status'] = X, X1, lag, status
        if S['downtime'] > 0:
            # R4-1: the class's clock origin r_e is t0 + downtime for app death / connectivity (the measured lag runs from
            # r_e), t0 itself for agent death (the measured lag runs from the tap; recovery starts downtime later)
            e['down'] = S['downtime']
        # common mode: after a restart the app renders a stale (cached) history to every end-to-end family
        e['stale'] = X == 1 and rng.random() < S['common_mode']
        # optimistic entry: a tapped-but-uncommitted effect shows a 'sending' list item to digest and VLM
        e['optim'] = X == 0 and p != 'pre' and rng.random() < S['optimistic']
        if S.get('catalog') == 'measured':
            # what the app's own status view shows (hop-1 reading): K-9 lists only unsent mail in its Outbox
            # (no Sent folder in our configuration); Element shows every message with its send state
            e['h1'] = (1 if (X1 == 1 and status in ('failed', 'pending', 'stuck')) else 0) \
                if A.get('profile') == 'k9' else X1
            # measured co-failure (Element): indicator and nonce text read from the same timeline view are
            # missing together on a committed effect; the room-list digest misses in a fraction of these
            e['blind'] = X == 1 and A.get('profile') == 'element' and S['blind'] > 0 and rng.random() < S['blind']
            e['blind_dig'] = e['blind'] and rng.random() < S['blind_digest']
            # measured (Element, campaign 2): at the late read every end-to-end family returned bot (no observation:
            # wrong screen, e.g. a system dialog) together in 2/101 trials
            e['bot'] = A.get('profile') == 'element' and S['bot_late'] > 0 and rng.random() < S['bot_late']
    return e


# ------------------------------------------------------------------ probe families
def _theta(rng, eps, rho_x):
    if rho_x <= 0:
        return eps
    if rho_x >= 1:
        return 1.0 if rng.random() < eps else 0.0
    kk = 1 / rho_x - 1
    return rng.betavariate(max(eps * kk, 1e-9), max((1 - eps) * kk, 1e-9))


class Family:
    """One effect's probe family.  read(v, s) returns the reading of view v when the true state is s."""
    def __init__(self, rng, V_, persist, view, rho_w=1.0, rho_x=0.0, iid=False, uninformative=None):
        self.rng, self.iid, self.unif = rng, iid, uninformative
        self.pers = [rng.random() < min(1.0, persist[0]), rng.random() < min(1.0, persist[1])]
        self.th = [_theta(rng, view[0], rho_x), _theta(rng, view[1], rho_x)]
        self.sticky = [rng.random() < rho_w for _ in range(V_)]
        self.shared = [[rng.random() < self.th[s] for _ in range(V_)] for s in (0, 1)]
        self.prev = {}
        self.force0 = False                              # optimistic entry: reads 'committed' when absent
        self.force10 = False                             # measured co-failure: reads 'absent' when committed
        self.bot = False                                 # no observation (wrong screen): read returns None
        self.memo = None                                 # set to {} to make repeated reads of a view consistent

    def read(self, v, s):
        if self.memo is not None:
            if (v, s) not in self.memo:
                self.memo[(v, s)] = self._read(v, s)
            return self.memo[(v, s)]
        return self._read(v, s)

    def _read(self, v, s):
        if self.bot:
            return None
        if self.force0 and s == 0:
            return 1
        if self.force10 and s == 1:
            return 0
        if self.unif is not None:                       # look-alike: reading independent of s
            return 1 if self.rng.random() < self.unif else 0
        if self.pers[s]:
            err = True
        elif self.iid:
            err = self.rng.random() < self.th[s]
        elif self.sticky[v % len(self.sticky)]:
            err = self.shared[s][v % len(self.sticky)]
        else:
            err = self.rng.random() < self.th[s]
        return (1 - s) if err else s

    def read_ar(self, v, s, rho):
        """Round-1 i.i.d.-with-AR(1) re-read model (scenario r1)."""
        th = self.th[s]
        key = (v, s)
        if key in self.prev and self.rng.random() < rho:
            err = self.prev[key]
        else:
            err = self.rng.random() < th
        self.prev[key] = err
        return (1 - s) if err else s


def make_family(name, rng, app, look, S, app_eps, kap=1.0):
    """kap multiplies the persistent-failure rates (deployment drift relative to calibration)."""
    if name == 'hop1':
        hp = S['hop1_persist'] * kap
        if S.get('hop1_persist1') is not None:          # measured committed-side rates
            h0 = app_eps[app]['hop1'][0]
            return Family(rng, V['hop1'], (hp, S['hop1_persist1']), (h0, S['hop1_view1']), iid=S['iid_rereads'])
        return Family(rng, V['hop1'], (hp, hp), app_eps[app]['hop1'], iid=S['iid_rereads'])
    if name == 'nonce':
        nv = S['nonce_iid'] if S['nonce_iid'] is not None else S['nonce_view']
        return Family(rng, V['nonce'], (0.0, S['nonce_persist'] * kap), (NONCE_EPS0_VIEW, nv), iid=S['iid_rereads'])
    if name == 'digest':
        return Family(rng, V['digest'], (0.005 * kap, S['digest_persist'] * kap), (S['digest_false'], S['digest_view']),
                      iid=S['iid_rereads'])
    e1v = app_eps[app]['vlm']
    if look:
        return Family(rng, V['vlm'], (0, 0), e1v, uninformative=1 - e1v[1])
    return Family(rng, V['vlm'], (0, 0), e1v, rho_w=S['vlm_rho_w'], rho_x=S['vlm_rho_x'])


def families(rng, e, A, S, app_eps, nonce_ok):
    names = (['hop1'] if A['hop1'] else []) + (['nonce'] if nonce_ok else []) + \
            (['digest'] if A['digest'] else []) + ([] if S.get('no_vlm') else ['vlm'])
    F = {n: make_family(n, rng, e['app'], e['look'], S, app_eps, kap=S['kappa']) for n in names}
    if e.get('optim'):
        for n in ('digest', 'vlm'):
            if n in F:
                F[n].force0 = True
    if e.get('blind'):
        for n in ('hop1', 'nonce') + (('digest',) if e.get('blind_dig') else ()):
            if n in F:
                F[n].force10 = True
    if e.get('bot'):
        for n in ('nonce', 'digest', 'vlm'):
            if n in F:
                F[n].bot = True
    if e.get('never') and 'digest' in F:
        F['digest'].force10 = True                     # K-9 Sent folder: a failed (but committed) mail never appears
    return F


def e2e_state(e, t):
    """t: seconds since the planner's recovery start.  e['lag'] runs from the class's clock origin, which is the recovery
    start except for agent death, whose origin t0 lies e['down'] earlier (round 4; e['down'] = 0 unless S['downtime'])."""
    if e.get('down') and e.get('fault') == 'agent-kill':
        t = t + e['down']
    return 1 if (e['X'] == 1 and t >= e['lag'] and not e['stale']) else 0


def verdict(fam, name, s_fn, V_):
    """Read each distinct view once.  nonce: 'com' if any view matches; others: unanimity."""
    ys = [fam.read(v, s_fn(v)) for v in range(V_)]
    if any(y is None for y in ys):
        return 'bot', V_
    if name == 'nonce':
        return ('com' if any(ys) else 'abs'), V_
    if all(y == 0 for y in ys):
        return 'abs', V_
    if all(y == 1 for y in ys):
        return 'com', V_
    return 'mixed', V_


def verdict_of(name, ys):
    """Graded family verdict from one read per view: (side, r) with r = views on the majority side
    (nonce: any match = committed).  Ties and no-observation (bot) reads return (None, 0)."""
    if any(y is None for y in ys):
        return None, 0
    nc = sum(ys)
    na = len(ys) - nc
    if name == 'nonce':
        return ('com', nc) if nc else ('abs', len(ys))
    if na > nc:
        return 'abs', na
    if nc > na:
        return 'com', nc
    return None, 0


def readout(fam, name, s_fn, V_):
    return verdict_of(name, [fam.read(v, s_fn(v)) for v in range(V_)])


def levels(name):
    Vf = V[name]
    if name == 'nonce':
        return dict(abs=[Vf], com=list(range(1, Vf + 1)))
    lo = Vf // 2 + 1
    return dict(abs=list(range(lo, Vf + 1)), com=list(range(lo, Vf + 1)))


# ------------------------------------------------------------------ calibration
_CAL_CACHE = {}


def cal_families(A, S):
    names = (['hop1'] if A['hop1'] else []) + (['nonce'] if A['nfield'] != 'none' else []) + \
            (['digest'] if A['digest'] else []) + ([] if S.get('no_vlm') else ['vlm'])
    return names


def cal_effects(wrng, app, A, S, app_eps, x, n, kap=1.0, pop=None, cls=None):
    """n calibration effects with outcome x; every family is read once per view on each effect.
    pop='passive': confirmation seen (x=1) or form abandoned (x=0): no stale history, no optimistic entry.
    pop='fault': fault-injected calibration on test accounts: the interrupted population."""
    pop = pop or S['cal_pop']
    names = cal_families(A, S)
    if S.get('catalog') == 'measured':
        return cal_effects_measured(wrng, app, A, S, app_eps, x, n, kap, pop, names, cls)
    out = []
    for _ in range(n):
        stale = x == 1 and pop == 'fault' and wrng.random() < S['common_mode']
        optim = x == 0 and pop == 'fault' and wrng.random() < S['optimistic']
        rec = {}
        for name in names:
            fam = make_family(name, wrng, app, False, S, app_eps, kap=kap)
            if optim and name in ('digest', 'vlm'):
                fam.force0 = True
            s = x if (name == 'hop1' or not stale) else 0
            rec[name] = [fam.read(v, s) for v in range(V[name])]
        out.append(rec)
    return out


def cal_effects_measured(wrng, app, A, S, app_eps, x, n, kap, pop, names, cls=None):
    """Measured profiles.  'fault': labels are interrupted effects of this app from the lab's fault-injection
    generator (fault mix S['cal_faults'] if set, else the deployment mix; one class if cls is given), rejection on the
    outcome, read once per view after visibility (bot reads stay bot).  'passive': uninterrupted effects (x=1:
    confirmation seen, so K-9 has already moved the mail out of its Outbox; x=0: form abandoned)."""
    out = []
    for _ in range(n):
        bot = never = False
        if pop == 'fault':
            while True:
                e = _effect(wrng, S, app, 0, True, cal=True, force_fault=cls)
                if e['X'] == x:
                    break
            h1, blind, bdig = e['h1'], e['blind'], e['blind_dig']
            bot, never = e['bot'], e['never']
        else:
            h1 = (0 if A.get('profile') == 'k9' else 1) if x == 1 else 0
            blind = bdig = False
        rec = {}
        for name in names:
            fam = make_family(name, wrng, app, False, S, app_eps, kap=kap)
            if blind and (name in ('hop1', 'nonce') or (name == 'digest' and bdig)):
                fam.force10 = True
            if bot and name in ('nonce', 'digest', 'vlm'):
                fam.bot = True
            if never and name == 'digest':
                fam.force10 = True
            s = h1 if name == 'hop1' else x
            rec[name] = [fam.read(v, s) for v in range(V[name])]
        out.append(rec)
    return out


def marginal_bounds(eff1, eff0, names, delta):
    """Per (family, side, level r): one-sided CP upper bound on P(>= r views on the wrong side), from whole
    calibration effects.  Absorbs within-family correlation and persistent misses."""
    q = {}
    n1, n0 = len(eff1), len(eff0)
    for name in names:
        L = levels(name)
        ge1 = Counter()
        ge0 = Counter()
        for rec in eff1:
            w = sum(1 for y in rec[name] if y == 0)
            for r in range(1, w + 1):
                ge1[r] += 1
        for rec in eff0:
            w = sum(1 for y in rec[name] if y == 1)
            for r in range(1, w + 1):
                ge0[r] += 1
        qa = {r: cpu(ge1[r], n1, delta) for r in L['abs']}
        if name == 'nonce':
            qc = {r: V['nonce'] * NONCE_EPS0_VIEW for r in L['com']}       # analytic (Lemma 4.7)
        else:
            qc = {r: cpu(ge0[r], n0, delta) for r in L['com']}
        q[name] = dict(abs=qa, com=qc, ge1=dict(ge1), ge0=dict(ge0), n1=n1, n0=n0)
    return q


def binom_sf(k, n, p):
    return 1.0 if k <= 0 else 1.0 - binom_cdf(k - 1, n, p)


def calibrate(wrng, app_eps, S, delta, mode, key=None):
    if key is not None and key in _CAL_CACHE:
        return _CAL_CACHE[key]
    Q = _calibrate(wrng, app_eps, S, delta, mode)
    if key is not None:
        _CAL_CACHE[key] = Q
    return Q


def _calibrate(wrng, app_eps, S, delta, mode):
    n = max(50, int(round(NCAL * S['ncal_scale'])))
    Q = {}
    for app in catalog(S):
        A = app_cfg(app, S)
        names = cal_families(A, S)
        if S.get('keyed') == 'all':
            # fault-class-keyed bounds (R2 m4): n labels per outcome IN EACH observable class; the planner uses the
            # class of the effect, or a fallback that is valid for every class when the class is unknown
            per = {}
            for c in CLASSES:
                e1 = cal_effects(wrng, app, A, S, app_eps, 1, n, cls=c)
                e0 = cal_effects(wrng, app, A, S, app_eps, 0, n, cls=c)
                per[c] = (marginal_bounds(e1, e0, names, delta) if mode == 'product' else
                          src_calibration(app, A, e1, e0, names, delta) if mode == 'src' else
                          joint_calibration(app, A, e1, e0, names, delta))
            Q[app] = dict(keyed=per)
            continue
        e1 = cal_effects(wrng, app, A, S, app_eps, 1, n)
        e0 = cal_effects(wrng, app, A, S, app_eps, 0, n)
        if mode == 'product':
            q = marginal_bounds(e1, e0, names, delta)
            if S['shift_test']:
                q = shift_tested(wrng, app, A, S, app_eps, q, names, delta)
            Q[app] = q
        elif mode == 'src':
            Q[app] = src_calibration(app, A, e1, e0, names, delta)
        else:
            Q[app] = joint_calibration(app, A, e1, e0, names, delta)
    return Q


def shift_tested(wrng, app, A, S, app_eps, q, names, delta, level=0.05):
    """Pooled calibration across app versions with a shift test: the pooled bounds (from the previous version)
    are kept for a family unless S['shift_test'] new-version effects reject 'no increase' at `level`; then that
    family falls back to bounds from the new-version effects alone (conservative fallback)."""
    m = S['shift_test']
    k = S['kappa']
    n1 = cal_effects(wrng, app, A, S, app_eps, 1, m, kap=k)
    n0 = cal_effects(wrng, app, A, S, app_eps, 0, m, kap=k)
    newq = marginal_bounds(n1, n0, names, delta)
    out = {}
    for name in names:
        rej = False
        for side, ge, nn, gen in (('abs', 'ge1', 'n1', newq[name]['ge1']), ('com', 'ge0', 'n0', newq[name]['ge0'])):
            for r in levels(name)[side]:
                if name == 'nonce' and side == 'com':
                    continue
                p_hat = max(q[name][ge].get(r, 0) / q[name][nn], 0.5 / q[name][nn])
                if binom_sf(gen.get(r, 0), m, p_hat) < level:
                    rej = True
        out[name] = newq[name] if rej else q[name]
        out[name]['shifted'] = rej
    return out


def enum_assignments(lv):
    """All ordered assignments over the families of lv (each skipped or at a level): list of (prod, prod_before)."""
    asg = []

    def rec(i, p, pre):
        if i == len(lv):
            if pre is not None:
                asg.append((p, pre))
            return
        rec(i + 1, p, pre)
        for r, qv in lv[i].items():
            rec(i + 1, p * qv, p)
    rec(0, 1.0, None)
    return asg


def stop_product(rec, seq, q, side, hop1_com):
    """Product of bound factors at which the cascade (families in `seq`) would stop with `side`, given the full
    verdict tuple `rec` (family -> verdict).  inf if it never stops with that side (contradiction first, or the
    first informative verdict is on the other side).  The cascade stops at the first prefix whose product is
    <= tau, so it stops with `side` at threshold tau iff this product is <= tau."""
    P, d0 = 1.0, None
    best = float('inf')
    for f in seq:
        d, r = rec[f]
        if f == 'hop1' and d == 'com' and not hop1_com:
            continue                                   # non-G2 entry: says nothing about the end-to-end outcome
        if d is None:
            continue
        if d0 not in (None, d):
            break
        d0 = d
        if d != side:
            return float('inf')
        P *= q[f][d][r]
        best = P
    return best


def joint_calibration(app, A, e1, e0, names, delta):
    """Prop. 4.4: calibrate the cascade's whole stopping region on whole effects.  A pilot tenth of the
    calibration effects fixes the score (products of per-family bounds) that orders verdict tuples; the other
    nine tenths test the nested regions {score <= tau} in increasing tau (fixed-sequence testing), so the
    chosen tau has P(retry | X=1, visible) <= alpha_test with probability >= 1 - delta, with NO assumption about
    dependence across families.  The region is the union over the configurations the planner may run
    (hop-1 used or not -- failed/stuck/non-G2 paths -- and VLM used or skipped on look-alikes)."""
    n_p = len(e1) // 10
    qp = marginal_bounds(e1[:n_p], e0[:n_p], names, delta)
    t1, t0 = e1[n_p:], e0[n_p:]
    hop1_com = A['G2'] or A['local']
    cfgs = []
    for uh in ([True, False] if 'hop1' in names else [False]):
        for uv in (True, False):
            cfgs.append([f for f in names if (f != 'hop1' or uh) and (f != 'vlm' or uv)])

    def region(test, side):
        pats = Counter(tuple(verdict_of(f, rec[f]) for f in names) for rec in test)
        stops = Counter()
        for pat, c in pats.items():
            rec = dict(zip(names, pat))
            sp = min(stop_product(rec, [f for f in cfg], qp, side, hop1_com) for cfg in cfgs)
            stops[sp] += c
        lv = [qp[f][side] for f in names if not (f == 'hop1' and side == 'com' and not hop1_com)]
        taus = sorted(set(p for p, _ in enum_assignments(lv)))
        n = len(test)
        out, k, runmax = [], 0, 0.0
        srt = sorted(stops.items())
        j = 0
        for t in taus:
            while j < len(srt) and srt[j][0] <= t:
                k += srt[j][1]
                j += 1
            runmax = max(runmax, cpu(k, n, delta))
            out.append((runmax, t))
        return out
    qh = None
    if 'hop1' in names:
        k = sum(1 for rec in t1 if sum(1 for y in rec['hop1'] if y == 0) >= V['hop1'])
        qh = cpu(k, len(t1), delta)
    return dict(q=qp, abs_tab=region(t1, 'abs'), com_tab=region(t0, 'com'), qh=qh)


def src_calibration(app, A, e1, e0, names, delta):
    """Evidence-source families: the app's local outbox (hop-1) is one source; every reader of the server-rendered
    history (nonce, digest, VLM) is merged into ONE family whose verdict is calibrated jointly on whole effects, so
    A2 is needed only between the two data sources.  With q_h the hop-1 bound and Q(t) a CP bound on
    P(history stop-product <= t | wrong outcome), B(tau) = q_h Q(tau/q_h) + Q(tau); thresholds are tested in
    increasing order (fixed sequence; two CP bounds per side)."""
    n_p = len(e1) // 10
    qp = marginal_bounds(e1[:n_p], e0[:n_p], names, delta)
    t1, t0 = e1[n_p:], e0[n_p:]
    hist = [f for f in names if f != 'hop1']
    cfgs = [hist, [f for f in hist if f != 'vlm']]
    hop1_com = A['G2'] or A['local']

    def stops(test, side):
        out = []
        for rec in test:
            vt = {f: verdict_of(f, rec[f]) for f in hist}
            out.append(min(stop_product(vt, cfg, qp, side, hop1_com) for cfg in cfgs))
        return sorted(out)

    s1, s0 = stops(t1, 'abs'), stops(t0, 'com')
    q = {f: qp[f] for f in hist}
    qh = qhc = None
    if 'hop1' in names:
        k = sum(1 for rec in t1 if sum(1 for y in rec['hop1'] if y == 0) >= V['hop1'])
        qh = cpu(k, len(t1), delta)
        k = sum(1 for rec in t0 if sum(1 for y in rec['hop1'] if y == 1) >= V['hop1'])
        qhc = cpu(k, len(t0), delta)
        q['hop1'] = dict(abs={V['hop1']: qh}, com={V['hop1']: qhc})

    def table(sl, side, qhs, use_h):
        import bisect
        n = len(sl)
        cand = sorted(set(p for p, _ in enum_assignments([qp[f][side] for f in hist])))
        m_min = cand[0] if cand else float('inf')    # below this no history verdict can reach t: region empty
        taus = sorted(set(cand + ([c * qhs for c in cand] + [qhs] if use_h else [])))
        out, runmax = [], 0.0
        for t in taus:
            b = cpu(bisect.bisect_right(sl, t), n, delta) if t >= m_min else 0.0
            if use_h and t >= qhs:
                b += qhs                                 # Q(t/q_h) = 1 for t >= q_h: hop-1 'absent' alone retries
            elif use_h and t / qhs >= m_min:
                b += qhs * cpu(bisect.bisect_right(sl, t / qhs), n, delta)
            runmax = max(runmax, b)
            out.append((runmax, t))
        return out
    return dict(q=q, abs_tab=table(s1, 'abs', qh, qh is not None),
                com_tab=table(s0, 'com', qhc, qhc is not None and hop1_com), qh=qh)


def tau_from(tab, budget):
    tau = 0.0
    for B, t in tab:
        if B <= budget:
            tau = t
        else:
            break
    return tau


_TAB_CACHE = {}


def cert_table(lv):
    """lv: cascade-ordered list of {r: q} for one side.  The cascade stops at the first prefix whose product is
    <= tau, so the stopping event is contained in the union over 'minimal' assignments A (prod(A) <= tau <
    prod(A minus its last family)), and P(stop with this side | wrong hypothesis) <= B(tau) = sum_A prod(A)
    under A2.  Returns sorted (B, tau) pairs with a running max of tau."""
    key = tuple(tuple(sorted(d.items())) for d in lv)
    if key in _TAB_CACHE:
        return _TAB_CACHE[key]
    asg = enum_assignments(lv)
    taus = sorted(set(p for p, _ in asg))
    pairs = []
    for t in taus:
        B = sum(p for p, pre in asg if p <= t < pre)
        pairs.append((B, t))
    pairs.sort()
    best, out = 0.0, []
    for B, t in pairs:
        best = max(best, t)
        out.append((B, best))
    _TAB_CACHE[key] = out
    return out


def B_of(lv, tau, lv_eval=None):
    """Union bound B(tau) of Prop. 4.3 over the assignment set defined by lv, evaluated with lv_eval's factors."""
    lv_eval = lv_eval or lv
    tot = 0.0

    def rec(i, p, pre, pe):
        nonlocal tot
        if i == len(lv):
            if pre is not None and p <= tau < pre:
                tot += pe
            return
        rec(i + 1, p, pre, pe)
        for r, qv in lv[i].items():
            rec(i + 1, p * qv, p, pe * lv_eval[i][r])
    rec(0, 1.0, None, 1.0)
    return tot


def tau_for(table, budget):
    """Largest stopping threshold tau whose union bound B(tau) is within budget (0 if none)."""
    tau = 0.0
    for B, t in table:
        if B <= budget:
            tau = t
        else:
            break
    return tau


def ng2_lag_sample(rng, S, pop):
    if pop == 'fault' and rng.random() < S['lag_heavy']:
        return 2.0 * rng.paretovariate(1.1)
    return rng.uniform(0.5, 3.0)


def lag_tables(wrng, S):
    """Logged commit-to-visibility times (sorted).  passive: uninterrupted effects; fault: interrupted ones."""
    if S.get('catalog') == 'measured':
        return lag_tables_measured(wrng, S)
    pop = S['cal_pop']
    ng2 = sorted(ng2_lag_sample(wrng, S, pop) for _ in range(N_LAG))
    g2 = sorted(g2_lag(wrng, S) for _ in range(N_LAG))
    return dict(ng2=ng2, g2=g2)


def lag_tables_measured(wrng, S):
    """Measured profiles: logged recovery-to-visible times of the lab's committed interrupted effects (fault mix
    S['cal_faults'] or the deployment mix), inf for a committed effect no end-to-end view ever shows (K-9 Sent folder,
    failed state).  keyed: one table per observable fault class.  passive: uninterrupted sends."""
    app = S['only_app']
    A = app_cfg(app, S)
    N_LAG_ = S.get('nlag') or N_LAG

    def draw(cls=None):
        return _lag_draw(wrng, S, app, cls)
    if S['cal_pop'] == 'passive':
        if A.get('profile') == 'element' and S.get('elem_lag'):
            xs = sorted(wrng.choice(S['elem_lag']['floor'])[0] for _ in range(N_LAG_))
        elif A.get('sent'):
            xs = sorted(wrng.uniform(S['k9_sent_lo'], S['k9_sent_hi']) for _ in range(N_LAG_))
        else:
            xs = sorted(wrng.uniform(0.5, 3.0) for _ in range(N_LAG_))
        return dict(g2=xs, ng2=xs, cls=None)
    pooled = sorted(draw() for _ in range(N_LAG_))
    cls = {c: sorted(draw(c) for _ in range(N_LAG_)) for c in CLASSES} if S.get('keyed') else None
    return dict(g2=pooled, ng2=pooled, cls=cls)


def _lag_draw(wrng, S, app, cls=None):
    """One logged lag of a committed fault-injected lab effect (measured profiles), inf if no end-to-end view ever shows it."""
    while True:
        e = _effect(wrng, S, app, 0, True, cal=True, force_fault=cls)
        if e['X'] == 1:
            return math.inf if e['never'] else e['lag']


def vetting(wrng, app_eps, S, policy):
    """R1 M1: rules vetted on fault-injected labels.  For each observable class (or pooled), keep only the families that
    were NEVER wrong on that class's labels (an 'absent' verdict on a committed label or 'committed' on an absent one),
    and set the wait to the longest logged lag of the class (at least 30 s); if a logged lag exceeds W_MAX or never
    became visible, the rule never retries on end-to-end absence.  'rules-vetted' uses as many labels as GhostEffect,
    'rules-vetted-small' 30 per class and outcome (the size of an emulator campaign cell).  No guarantee is computed."""
    assert S.get('catalog') == 'measured'
    n = 30 if policy.endswith('-small') else max(50, int(round(NCAL * S['ncal_scale'])))
    out = {}
    for app in catalog(S):
        A = app_cfg(app, S)
        names = cal_families(A, S)
        per = {}
        for c in (CLASSES if S.get('keyed') == 'all' else [None]):
            e1 = cal_effects(wrng, app, A, S, app_eps, 1, n, cls=c)
            e0 = cal_effects(wrng, app, A, S, app_eps, 0, n, cls=c)
            ok = {f for f in names
                  if not any(verdict_of(f, rec[f])[0] == 'abs' for rec in e1)
                  and not any(verdict_of(f, rec[f])[0] == 'com' for rec in e0)}
            mx = max(_lag_draw(wrng, S, app, c) for _ in range(n))
            per[c] = (ok, max(30.0, mx) if mx <= W_MAX else 30.0, mx <= W_MAX)
        out[app] = per
    return out


def lag_wait(lagx, A, e, share, delta):
    """Certified wait from the lag table of the effect's fault class (keyed), the maximum over classes when the class
    is unknown, or the pooled table."""
    if lagx.get('cls'):
        if e.get('cls_known', True):
            return certified_wait(lagx['cls'][e['fault']], share, delta)
        return max(certified_wait(t, share, delta) for t in lagx['cls'].values())
    return certified_wait(lagx['g2' if A['G2'] else 'ng2'], share, delta)


def qmax(per):
    """Elementwise maximum of per-class product bounds (fallback when the fault class is unknown)."""
    out = {}
    for c, q in per.items():
        for f, d in q.items():
            o = out.setdefault(f, dict(abs={}, com={}))
            for side in ('abs', 'com'):
                for r, v in d[side].items():
                    o[side][r] = max(o[side].get(r, 0.0), v)
    return out


_CPU = {}


def _betacf(a, b, x):
    """Continued fraction for the regularized incomplete beta (Numerical Recipes, betacf)."""
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return h


def _betai(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def _binom_cdf_fast(k, n, p):
    """P(Bin(n, p) <= k) = I_{1-p}(n-k, k+1)."""
    if k >= n:
        return 1.0
    return _betai(n - k, k + 1, 1.0 - p)


def cpu(k, n, delta):
    """One-sided (1-delta) Clopper-Pearson upper bound (bisection on the binomial CDF, evaluated through the
    regularized incomplete beta; agrees with ge_core.cp_upper_one_sided to ~1e-12)."""
    key = (k, n, delta)
    if key not in _CPU:
        if k >= n:
            _CPU[key] = 1.0
        else:
            lo, hi = 0.0, 1.0
            for _ in range(60):
                mid = (lo + hi) / 2
                if _binom_cdf_fast(k, n, mid) <= delta:
                    hi = mid
                else:
                    lo = mid
            _CPU[key] = (lo + hi) / 2
    return _CPU[key]


_CW = {}


def certified_wait(xs, a_lag, delta):
    """Smallest logged lag w whose CP upper bound on P(T > w) is <= a_lag (inf if none): the largest exceedance
    count k with CP(k, n) <= a_lag (CP is increasing in k), and w = the (n-k)-th order statistic."""
    n = len(xs)
    key = (n, delta, a_lag)
    if key not in _CW:
        if cpu(0, n, delta) > a_lag:
            _CW[key] = -1
        else:
            lo, hi = 0, n - 1                       # cpu(lo) <= a_lag < cpu(hi+1)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if cpu(mid, n, delta) <= a_lag:
                    lo = mid
                else:
                    hi = mid - 1
            _CW[key] = lo
    kbest = _CW[key]
    return xs[n - 1 - kbest] if kbest >= 0 else float('inf')


# ------------------------------------------------------------------ user and Monitor
def ask_user(rng, e, S):
    err = S['user_err'] * (2 if e['look'] else 1)
    ans = e['X'] if rng.random() >= err else 1 - e['X']
    return ans == 0                                    # retry iff the user says "not done"


def monitor(rng, e, S):
    """Background re-reads of a hop-1 entry until a terminal state.  Returns (observation, seconds).
    Fallible: a terminal state is misread (acknowledged <-> failed) with probability S['mon_err']."""
    st = e['status']
    if st in ('sent', 'pending'):
        if st == 'pending' and e['lag'] > MON_STUCK:
            return 'stuck', MON_STUCK
        obs, t = 'acked', max(1.0, e['lag'])
    elif st == 'stuck':
        return 'stuck', MON_STUCK
    else:                                              # failed, or no entry at all (false hop-1 'com' reading)
        obs, t = 'failed', 10.0
    if rng.random() < S['mon_err']:
        obs = 'failed' if obs == 'acked' else 'acked'
    return obs, t


# ------------------------------------------------------------------ round-1 planner (for comparison)
def sprt_reads(read, e0m, e1m, al, be, n_max, cost, shrink=1.0):
    a, b = math.log(1 / be), math.log(1 / al)
    u = math.log((1 - e1m) / e0m) * shrink
    v = math.log((1 - e0m) / e1m) * shrink
    L, n = 0.0, 0
    while n < n_max:
        n += 1
        L += u if read(n) == 1 else -v
        if L >= a:
            return 'committed', n, n * cost
        if L <= -b:
            return 'absent', n, n * cost
    return 'ask', n, n * cost


def resolve_v1(e, A, F, S, est_v1, alloc, rng):
    al, be = alloc
    nobs, secs = 0, 0.0
    rr = lambda f, v, s: f.read(v, s)
    if 'hop1' in F:
        h0m, h1m = est_v1[e['app']]['hop1']
        d, n, s = sprt_reads(lambda i: rr(F['hop1'], 0, e['X1']), h0m, h1m, 0.2 * al, 0.2 * be, N_MAX_V1, T_HOP1)
        nobs += n
        secs += s
        if d == 'absent':
            return True, nobs, secs
        if d == 'committed' and (A['G2'] or A['local']):
            return False, nobs, secs
        al, be = 0.8 * al, 0.8 * be
    wait = 10.0 if not A['G2'] else 75.0 if 'hop1' not in F else 10.0
    secs += wait
    if 'nonce' in F:
        d, n, s = sprt_reads(lambda i: rr(F['nonce'], 0, e2e_state(e, wait + i * T_OCR)), 1e-5, 0.03, al, be,
                             N_MAX_V1, T_OCR)
    elif e['look']:
        return None, nobs, secs
    else:
        e0m, e1m = est_v1[e['app']]['vlm']
        r_eff = 0.2 / 3
        shrink = (1 - r_eff) / (1 + r_eff)
        if S['iid_rereads']:
            rd = lambda i: F['vlm'].read_ar(i % 3, e2e_state(e, wait + i * T_VLM), 0.2)
        else:
            rd = lambda i: F['vlm'].read(i % 3, e2e_state(e, wait + i * T_VLM))
        d, n, s = sprt_reads(rd, e0m, e1m, al, be, N_MAX_V1, T_VLM, shrink=shrink)
    nobs += n
    secs += s
    if d == 'ask':
        return None, nobs, secs
    return d == 'absent', nobs, secs


# ------------------------------------------------------------------ revised planner
COST = dict(hop1=T_HOP1, nonce=T_OCR, digest=T_OCR, vlm=T_VLM)
USED = Counter()                 # (side, families in the certifying product) -> count, for the family-share study
NOMINAL = dict(hop1=0.02, nonce=0.006, digest=0.03, vlm=0.08)


def nominal_q(q):
    def tail(k, r, p):
        return sum(math.comb(k, j) * p ** j * (1 - p) ** (k - j) for j in range(r, k + 1))
    return {k: dict(abs={r: tail(V[k], r, NOMINAL[k]) for r in d['abs']},
                    com={r: (V[k] * NONCE_EPS0_VIEW if k == 'nonce' else tail(V[k], r, NOMINAL[k])) for r in d['com']})
            for k, d in q.items()}


def resolve_v2(policy, e, A, F, S, Q, lagx, alloc, delta, rng):
    """Revised GhostRecover (Algorithm 1).  Returns (retry: True/False/None=ask, reads, blocking s, background s,
    reason).  reason for asks: 'wait' (certified wait > W_max, Doze), 'contra' (families disagree), 'struct' (even
    full agreement of the available families cannot certify), 'uncert' (evidence agreed but did not reach tau)."""
    joint = policy in ('ghost-joint', 'ghost-src')
    Qa = Q[e['app']]
    if 'keyed' in Qa:                                   # fault-class-keyed bounds
        per = Qa['keyed']
        if e.get('cls_known', True):
            return resolve_v2(policy, e, A, F, S, {e['app']: per[e['fault']]}, lagx, alloc, delta, rng)
        if not joint:                                   # unknown class: per-family max over classes
            return resolve_v2(policy, e, A, F, S, {e['app']: qmax(per)}, lagx, alloc, delta, rng)
        # unknown class, joint/source: act only if the action is certified in EVERY class (intersection of regions)
        for fam in F.values():
            fam.memo = {}
        outs = [resolve_v2(policy, e, A, F, S, {e['app']: per[c]}, lagx, alloc, delta, rng) for c in CLASSES]
        for fam in F.values():
            fam.memo = None
        rets = [o[0] for o in outs]
        n_, s_, b_ = max(o[1] for o in outs), max(o[2] for o in outs), max(o[3] for o in outs)
        if all(r is True for r in rets):
            return True, n_, s_, b_, None
        if all(r is False for r in rets):
            return False, n_, s_, b_, None
        return None, n_, s_, b_, next((o[4] for o in outs if o[4]), 'contra')
    al, be = alloc
    a_test = (0.9 if A['local'] else 0.5) * al          # lag share 0.4 al (non-local), calibration 0.1 al
    a_lag, b_test = 0.4 * al, 0.9 * be
    if joint:
        J = Q[e['app']]
        q = J['q']
    else:
        q = Q[e['app']]
        if policy == 'ghost-nocal':
            q = nominal_q(q)
    nobs, secs, bg = 0, 0.0, 0.0
    use_hop1 = 'hop1' in F and policy != 'ghost-nohop1'
    hop1_com = A['G2'] or A['local']
    order = [f for f in ('nonce', 'digest', 'vlm') if f in F]
    if policy == 'ghost-nononce':
        order = [f for f in order if f != 'nonce']
    if policy == 'ghost-nodigest':
        order = [f for f in order if f != 'digest']
    if e['look']:
        order = [f for f in order if f != 'vlm']        # the pre-tap digest reveals the look-alike
    lv_a = ([q['hop1']['abs']] if use_hop1 else []) + [q[f]['abs'] for f in order]
    lv_c = ([q['hop1']['com']] if use_hop1 and hop1_com else []) + [q[f]['com'] for f in order]
    if joint:
        tau_a, tau_c = tau_from(J['abs_tab'], a_test), tau_from(J['com_tab'], b_test)
        qh = J['qh'] if use_hop1 else 0.0
    else:
        tau_a = tau_for(cert_table(lv_a), a_test) if lv_a else 0.0
        tau_c = tau_for(cert_table(lv_c), b_test) if lv_c else 0.0
        qh = max(q['hop1']['abs'].values()) if use_hop1 else 0.0
    # lag shares (corrected composition): P(retry, not visible | X=1) <= q_h G(w1) + G(w0).  With a hop-1 family
    # the planner certifies q_h G(w1) <= a_lag/2 and G(w0) <= a_lag/2; without one, G(w0) <= a_lag.
    s1, s0 = (a_lag / 2, a_lag / 2) if (use_hop1 and not A['local']) else (0.0, a_lag)
    P, direction, elapsed, background = 1.0, None, 0.0, False
    path = 'main'
    used = []
    if use_hop1:
        d, r = readout(F['hop1'], 'hop1', lambda vv: e.get('h1', e['X1']), V['hop1'])
        nobs += V['hop1']
        secs += V['hop1'] * T_HOP1
        if d == 'com' and hop1_com:
            P, direction = q['hop1']['com'][r], 'com'
            used.append('hop1')
            if A['local']:
                if P <= tau_c:
                    USED[('com',) + tuple(used)] += 1
                    return False, nobs, secs, bg, None
            else:
                obs, tm = monitor(rng, e, S)
                bg += tm
                nobs += 1 + int(tm // 10)
                if obs == 'acked':
                    if P <= tau_c:
                        USED[('com',) + tuple(used)] += 1
                        return False, nobs, secs, bg, None
                    elapsed, background, path = tm, True, 'corroborate'   # acknowledged: visible end to end
                else:                                   # failed / stuck: end-to-end path, wait counted from t0
                    P, direction, elapsed, path = 1.0, None, tm, 'handover'
                    used = []
        elif d == 'abs':
            P, direction, path = q['hop1']['abs'][r], 'abs', 'h1abs'
            used.append('hop1')
            if P <= tau_a:
                USED[('abs',) + tuple(used)] += 1
                return True, nobs, secs, bg, None
    if order and path != 'corroborate':
        if A['local']:
            wait = 0.0
        else:
            share = min(1.0, s1 / qh) if path == 'h1abs' else s0
            w = lag_wait(lagx, A, e, share, delta)
            if e['doze'] and S['doze_aware']:
                w = float('inf')                        # delayed recovery while idle: no lag table for this state
            # reads happen no earlier than r_e + w, with r_e the class's observable clock origin (R4-1): for agent death
            # r_e = t0, which lies e['down'] before recovery; S['clock'] == 't0' waits from ISSUED for every class (wrong
            # for app death / connectivity, whose lag law is logged from relaunch / restore)
            pre = e.get('down', 0.0) if (e.get('fault') == 'agent-kill' or S['clock'] == 't0') else 0.0
            wait = max(0.0, w - pre - max(elapsed, secs))
        if wait > W_MAX:
            return None, nobs, secs, bg, 'wait'
        secs += wait
        elapsed = max(elapsed, secs)
    t_read = elapsed if path in ('corroborate', 'handover') else secs
    reason = 'uncert'
    for f in order:
        t0 = t_read
        d, r = readout(F[f], f, lambda vv: e2e_state(e, t0 + vv * COST[f]), V[f])
        nobs += V[f]
        if background:
            bg += V[f] * COST[f]
        else:
            secs += V[f] * COST[f]
        t_read += V[f] * COST[f]
        if d is None:
            continue                                    # tie: no evidence, try the next family
        if direction not in (None, d):
            reason = 'contra'
            break                                       # contradiction -> ask
        P, direction = P * q[f][d][r], d
        used.append(f)
        if d == 'abs' and P <= tau_a:
            USED[('abs',) + tuple(used)] += 1
            return True, nobs, secs, bg, None
        if d == 'com' and P <= tau_c:
            USED[('com',) + tuple(used)] += 1
            return False, nobs, secs, bg, None
    if reason == 'uncert':
        # could ANY verdict of the available families have certified?  (structural escalation)
        best_a = math.prod(min(x.values()) for x in lv_a) if lv_a else 1.0
        best_c = math.prod(min(x.values()) for x in lv_c) if lv_c else 1.0
        if not joint and best_a > tau_a and best_c > tau_c:
            reason = 'struct'
        if joint and tau_a == 0.0 and tau_c == 0.0:
            reason = 'struct'
        if joint and policy == 'ghost-src' and lv_a and lv_c:
            if math.prod(min(x.values()) for x in lv_a) > tau_a and math.prod(min(x.values()) for x in lv_c) > tau_c:
                reason = 'struct'
    if policy == 'ghost-noask':                         # declare whenever uncertified (no ask)
        return False, nobs, secs, bg, None
    return None, nobs, secs, bg, reason


def resolve_rules(policy, e, A, F, S, rng):
    """Same evidence as GhostRecover (hop-1 + fallible Monitor, nonce, digest, VLM, one read per view, a fixed wait,
    ask) decided by deterministic rules rather than calibrated certification.  'rules' = 10 s wait, every family agrees;
    'rules-lenient' acts on the first unanimous family unless another contradicts; 'rules-w<W>-<Q>' is the
    parameterised family (wait W s; quorum Q = all / novlm / two).  A nonce match in any view always means done."""
    wait_s, quorum = T_RULES_WAIT, 'all'
    trusted, retry_ok = None, True
    if policy.startswith('rules-vetted'):
        tab = S['_vet'][e['app']]
        if None in tab:
            trusted, wait_s, retry_ok = tab[None]
        elif e.get('cls_known', True):
            trusted, wait_s, retry_ok = tab[e['fault']]
        else:                                           # unknown class: families trusted in every class, longest wait
            trusted = set.intersection(*(v[0] for v in tab.values()))
            wait_s = max(v[1] for v in tab.values())
            retry_ok = all(v[2] for v in tab.values())
        F = {f: F[f] for f in F if f in trusted}
        if not F:
            return None, 0, 0.0, 0.0
    elif policy.startswith('rules-w'):
        w_, quorum = policy[len('rules-w'):].split('-')
        wait_s = float(w_)
    nobs, secs, bg = 0, 0.0, 0.0
    hop1_vote = None
    elapsed = 0.0
    if 'hop1' in F:
        d, r = readout(F['hop1'], 'hop1', lambda vv: e.get('h1', e['X1']), V['hop1'])
        nobs += V['hop1']
        secs += V['hop1'] * T_HOP1
        if d == 'com' and (A['G2'] or A['local']):
            if A['local']:
                return False, nobs, secs, bg
            obs, tm = monitor(rng, e, S)
            bg += tm
            if obs == 'acked':
                return False, nobs, secs, bg        # rule: acknowledged entry -> done
            elapsed = tm                            # failed/stuck: decide end to end
        elif d == 'abs':
            hop1_vote = 'abs'
    order = [f for f in ('nonce', 'digest', 'vlm') if f in F and not (f == 'vlm' and e['look'])]
    if quorum == 'novlm':
        order = [f for f in order if f != 'vlm']
    wait = 0.0 if A['local'] else max(0.0, wait_s - max(elapsed, secs))
    secs += wait
    t = max(elapsed, secs)
    votes = []
    for f in order:
        t0 = t
        v, n = verdict(F[f], f, lambda vv: e2e_state(e, t0 + vv * COST[f]), V[f])
        nobs += n
        secs += n * COST[f]
        t += n * COST[f]
        if f == 'nonce' and v == 'com':
            return False, nobs, secs, bg            # rule: nonce found in any view -> committed
        if v == 'bot':
            continue                                # no observation: no vote
        votes.append(v)
        if policy == 'rules-lenient' and v in ('abs', 'com'):
            if hop1_vote is not None and v != hop1_vote:
                return None, nobs, secs, bg
            return v == 'abs', nobs, secs, bg
    allv = votes + ([hop1_vote] if hop1_vote else [])
    if quorum == 'two':
        na, nc = sum(v == 'abs' for v in allv), sum(v == 'com' for v in allv)
        need = min(2, len(order) + (1 if 'hop1' in F else 0))
        if need and na >= need and nc == 0:
            return True, nobs, secs, bg
        if need and nc >= need and na == 0:
            return False, nobs, secs, bg
        return None, nobs, secs, bg
    if allv and all(v == 'abs' for v in allv) and len(votes) == len(order):
        return (True if retry_ok else None), nobs, secs, bg
    if votes and all(v == 'com' for v in votes) and hop1_vote is None and len(votes) == len(order):
        return False, nobs, secs, bg
    return None, nobs, secs, bg


# ------------------------------------------------------------------ baselines
def resolve_baseline(policy, e, A, F, S, rng):
    if policy in ('redo', 'ckpt'):
        return True, 0, 0.0
    if policy == 'always-ask':
        return None, 0, 0.0
    if policy == 'g2-only':
        # Theorem 4.8 alone: never retry.  A G2 (or local) app's hop-1 entry, if present and not failed, means done.
        if A['local'] and 'hop1' in F:
            d, _ = readout(F['hop1'], 'hop1', lambda vv: e.get('h1', e['X1']), V['hop1'])
            return (False if d == 'com' else None), V['hop1'], V['hop1'] * T_HOP1
        if not A['G2']:
            return None, 0, 0.0
        if 'hop1' in F:
            d, _ = readout(F['hop1'], 'hop1', lambda vv: e.get('h1', e['X1']), V['hop1'])
            if d == 'com':
                obs, _tm = monitor(rng, e, S)           # background; a failed/stuck entry is asked about
                return (False if obs == 'acked' else None), V['hop1'] + 1, V['hop1'] * T_HOP1
            return None, V['hop1'], V['hop1'] * T_HOP1
        if A.get('entry_e2e'):
            # Element: the entry is the timeline row, drawn only once visible; the first verified read decides
            if e['bot']:
                return None, 1, T_OCR
            seen = e['X'] == 1 and not e['first_abs']
            return (False if seen else None), 1, (max(T_OCR, e['lag']) if seen else T_OCR)
        return None, 0, 0.0
    if policy == 'app-state' and 'hop1' not in F and A.get('entry_e2e'):
        # trust the app's status view read right after recovery: no row shown -> 'not sent' -> resend
        if e['X'] == 0:
            return True, 1, T_OCR
        return e['first_abs'], 1, T_OCR
    if policy == 'app-state' and 'hop1' in F:
        # GUI-only verification that trusts the app's own status view as designed.  No entry shown: K-9's Outbox
        # lists only unsent mail, so 'not listed' reads as sent; Element shows every message, so 'not shown' reads
        # as not sent.  An entry shown: wait for a terminal state (fallible Monitor), retry unless acknowledged.
        if F['hop1'].read(0, e.get('h1', e['X1'])) == 0:
            return A.get('profile') != 'k9', 1, T_HOP1
        obs, tm = monitor(rng, e, S)
        return obs != 'acked', 1, T_HOP1 + tm
    vlm1 = lambda t: F['vlm'].read(0, e2e_state(e, t))
    if policy in ('atomix', 'atomix-durable'):
        if policy == 'atomix' and e['fault'] in ('agent-kill', 'kill+net'):
            return True, 0, 0.0                         # in-memory dedup table lost with the agent
        if A['G2'] and 'hop1' in F:
            return F['hop1'].read(0, e['X1']) == 0, 1, T_WAIT_BASE + T_HOP1
        return vlm1(T_WAIT_BASE) == 0, 1, T_WAIT_BASE + T_VLM
    if policy == 'verify':
        return vlm1(T_WAIT_BASE) == 0, 1, T_WAIT_BASE + T_VLM
    if policy in ('key', 'key-ask'):
        if 'nonce' in F:
            return F['nonce'].read(0, e2e_state(e, T_WAIT_BASE)) == 0, 1, T_WAIT_BASE + T_OCR
        if policy == 'key-ask' and e['look']:
            return None, 0, T_WAIT_BASE
        return vlm1(T_WAIT_BASE) == 0, 1, T_WAIT_BASE + T_VLM
    if policy == 'nonce-ask':
        if 'nonce' in F:
            v, n = verdict(F['nonce'], 'nonce', lambda vv: e2e_state(e, T_WAIT_BASE + vv * T_OCR), V['nonce'])
            return v == 'abs', n, T_WAIT_BASE + n * T_OCR
        return None, 0, 0.0
    if policy == 'maj3-ask':
        if e['look']:
            return None, 0, 0.0
        v, n = verdict(F['vlm'], 'vlm', lambda vv: e2e_state(e, T_WAIT_BASE + vv * T_VLM), V['vlm'])
        if v == 'mixed':
            return None, n, T_WAIT_BASE + n * T_VLM
        return v == 'abs', n, T_WAIT_BASE + n * T_VLM
    raise ValueError(policy)


# ------------------------------------------------------------------ budget allocation (Prop. 4.9)
def allocation(policy, effects, est, alpha, beta, Q=None):
    k = len(effects)
    if policy == 'ghost-uniform':
        return [(alpha / k, beta / k)] * k
    if Q is not None and policy.startswith('ghost') and policy != 'ghost-v1':
        # Prop. 4.9 with each step's strongest family as its probe: D ~ log(1/q), c = family read time
        w, v = [], []
        for e in effects:
            q = Q[e['app']]
            if 'keyed' in q:
                q = qmax({c: (v['q'] if 'abs_tab' in v else v) for c, v in q['keyed'].items()})
            if 'abs_tab' in q:
                q = q['q']
            if all(f == 'hop1' for f in q):              # measured K-9 profile: hop-1 is the only family
                w.append(1.0)
                v.append(1.0)
                continue
            best_a = min((min(d['abs'].values()), f) for f, d in q.items() if f != 'hop1')
            best_c = min((min(d['com'].values()), f) for f, d in q.items() if f != 'hop1')
            ca, cc = V[best_a[1]] * COST[best_a[1]], V[best_c[1]] * COST[best_c[1]]
            w.append(ca * 0.4 / math.log(1 / max(best_a[0], 1e-12)))
            v.append(cc * 0.6 / math.log(1 / max(best_c[0], 1e-12)))
        return [(alpha * wi / sum(w), beta * vi / sum(v)) for wi, vi in zip(w, v)]
    w, v = [], []
    for e in effects:
        e0, e1 = est[e['app']]['vlm']
        if ALL_APPS[e['app']]['nfield'] != 'none':
            e0, e1 = 1e-5, 0.03
        D1, D0 = kl_pair(e0, e1)
        c = T_OCR if ALL_APPS[e['app']]['nfield'] != 'none' else T_VLM
        w.append(c * 0.4 / D0)
        v.append(c * 0.6 / D1)
    return [(alpha * wi / sum(w), beta * vi / sum(v)) for wi, vi in zip(w, v)]


def app_class(A):
    if A['local']:
        return 'local'
    if A['G2']:
        return 'G2'
    if not A['hop1'] and A['nfield'] == 'none' and not A['digest']:
        return 'VLM-only'
    return 'non-G2'


# ------------------------------------------------------------------ driver
def app_errors(wrng, S=None):
    app_eps, est_v1 = {}, {}
    for app in (catalog(S) if S else APPS):
        e0, e1 = wrng.uniform(0.06, 0.26), wrng.uniform(0.04, 0.20)
        h0, h1 = wrng.uniform(0.01, 0.05), wrng.uniform(0.01, 0.05)
        app_eps[app] = dict(vlm=(e0, e1), hop1=(h0, h1))
        k0 = sum(wrng.random() < e0 for _ in range(100))
        k1 = sum(wrng.random() < e1 for _ in range(100))
        g0 = sum(wrng.random() < h0 for _ in range(100))
        g1 = sum(wrng.random() < h1 for _ in range(100))
        est_v1[app] = dict(vlm=(min(0.45, cp_upper_one_sided(k0, 100)), min(0.45, cp_upper_one_sided(k1, 100))),
                           hop1=(min(0.45, cp_upper_one_sided(g0, 100)), min(0.45, cp_upper_one_sided(g1, 100))))
    return app_eps, est_v1


def run(policies, scenario='default', seeds=SEEDS, n_per_seed=N_PER_SEED, alpha=0.01, beta=0.01, overrides=None):
    S = scen(scenario)
    if overrides:
        S.update(overrides)
    d_prod, d_joint, d_src = alpha / (10 * K_PRODUCT), alpha / (10 * K_JOINT), alpha / (10 * K_SRC)
    if S.get('keyed') == 'all':                        # the unknown-class fallback uses every class's bounds
        d_prod, d_joint, d_src = (d / len(CLASSES) for d in (d_prod, d_joint, d_src))
    out = {p: [] for p in policies}
    eff = {p: dict(d1=0, n1=0, l0=0, n0=0, altered=0, amb=0, all=0, cls={}, why=Counter(), dlag=0) for p in policies}
    for s in seeds:
        wrng = random.Random(s)
        app_eps, est_v1 = app_errors(wrng, S)
        worlds = [make_world(wrng, S) for _ in range(n_per_seed)]
        need_p = any(p.startswith('ghost') and p not in ('ghost-v1', 'ghost-joint', 'ghost-src') for p in policies)
        need_j = 'ghost-joint' in policies
        need_s = 'ghost-src' in policies
        crng = random.Random(s * 31 + 7)
        skey = tuple(sorted((k, str(v)) for k, v in S.items() if k not in ('user_err', 'nonce_policy', 'mon_err')))
        Qp = calibrate(random.Random(s * 31 + 7), app_eps, S, d_prod, 'product', key=(s, d_prod, 'p', skey)) \
            if need_p else None
        Qj = calibrate(random.Random(s * 31 + 7), app_eps, S, d_joint, 'joint', key=(s, d_joint, 'j', skey)) \
            if need_j else None
        Qs = calibrate(random.Random(s * 31 + 7), app_eps, S, d_src, 'src', key=(s, d_src, 's', skey)) \
            if need_s else None
        lagx = lag_tables(random.Random(s * 31 + 11), S) if (need_p or need_j or need_s) else None
        VET = {p: vetting(random.Random(s * 31 + 13), app_eps, S, p) for p in policies if p.startswith('rules-vetted')}
        for p in policies:
            prng = random.Random(s * 7919 + (ALL_POLICIES + EXTRA_POLICIES).index(p))
            Sp = dict(S)
            if p == 'ghost-visible':
                Sp['nonce_policy'] = 'visible'
            if p in VET:
                Sp['_vet'] = VET[p]
            Q = Qj if p == 'ghost-joint' else Qs if p == 'ghost-src' else Qp
            delta = d_joint if p == 'ghost-joint' else d_src if p == 'ghost-src' else d_prod
            for effects in worlds:
                alloc = allocation(p, effects, est_v1, alpha, beta, Q)
                dup = loss = ask = uerr = 0
                nobs, secs, bg = 0, 0.0, 0.0
                for j, e in enumerate(effects):
                    A = app_cfg(e['app'], S)
                    nonce_ok = A['nfield'] == 'private' or (A['nfield'] == 'visible' and Sp['nonce_policy'] == 'visible')
                    if p in ('key', 'key-ask', 'nonce-ask', 'ghost-v1'):
                        nonce_ok = A['nfield'] != 'none'      # round-1 behaviour: any free-text field
                    uses_nonce = p not in ('redo', 'ckpt', 'atomix', 'atomix-durable', 'verify', 'always-ask',
                                           'maj3-ask', 'ghost-nononce')
                    eff[p]['all'] += 1
                    if uses_nonce and nonce_ok and A['nfield'] == 'visible':
                        eff[p]['altered'] += 1
                    if not e['interrupted']:
                        continue
                    eff[p]['amb'] += 1
                    if p == 'ckpt' and not e['node_first'] and e['fault'] in ('agent-kill', 'kill+net'):
                        dup = 1
                    if e['appdup'] and p not in ('redo', 'ckpt'):
                        dup = 1                                # server without dedup retransmitted twice
                    F = families(prng, e, A, Sp, app_eps, nonce_ok)
                    why = None
                    if p == 'ghost-v1':
                        retry, n, sec = resolve_v1(e, A, F, Sp, est_v1, alloc[j], prng)
                    elif p.startswith('ghost'):
                        retry, n, sec, b, why = resolve_v2(p, e, A, F, Sp, Q, lagx, alloc[j], delta, prng)
                        bg += b
                    elif p.startswith('rules'):
                        retry, n, sec, b = resolve_rules(p, e, A, F, Sp, prng)
                        bg += b
                    else:
                        retry, n, sec = resolve_baseline(p, e, A, F, Sp, prng)
                    nobs += n
                    secs += sec
                    asked = retry is None
                    if asked and why:
                        eff[p]['why'][why] += 1
                    c = app_class(A)
                    C = eff[p]['cls'].setdefault(c, dict(n=0, ask=0, secs=0.0, d1=0, n1=0))
                    C['n'] += 1
                    C['ask'] += asked
                    C['secs'] += sec + (T_ASK if asked else 0.0)
                    if asked:
                        ask = 1
                        secs += T_ASK
                        retry = ask_user(prng, e, Sp)
                        if (retry and e['X'] == 1) or (not retry and e['X'] == 0):
                            uerr = 1
                    if retry:
                        secs += T_RETRY
                    if e['X'] == 1:
                        eff[p]['n1'] += 1
                        C['n1'] += 1
                        if retry:
                            dup = 1
                            if not asked:
                                eff[p]['d1'] += 1
                                C['d1'] += 1
                    else:
                        eff[p]['n0'] += 1
                        if not retry:
                            loss = 1
                            if not asked:
                                eff[p]['l0'] += 1
                out[p].append((dup, loss, ask, nobs, secs, bg, uerr))
    return out, eff


def summarize(out, eff, policies):
    rows = []
    for p in policies:
        ep = out[p]
        N = len(ep)
        r = dict(policy=p, n=N)
        for key, idx in (('dup', 0), ('loss', 1), ('ask', 2), ('uerr', 6)):
            k = sum(x[idx] for x in ep)
            lo, hi = clopper_pearson(k, N)
            r[key], r[key + '_lo'], r[key + '_hi'] = 100 * k / N, 100 * lo, 100 * hi
        r['obs'] = sum(x[3] for x in ep) / N
        r['secs'] = sum(x[4] for x in ep) / N
        r['bg'] = sum(x[5] for x in ep) / N
        E = eff[p]
        r['cdup'] = 100 * E['d1'] / max(1, E['n1'])
        r['cdup_hi'] = 100 * clopper_pearson(E['d1'], max(1, E['n1']))[1]
        r['closs'] = 100 * E['l0'] / max(1, E['n0'])
        r['closs_hi'] = 100 * clopper_pearson(E['l0'], max(1, E['n0']))[1]
        r['altered'] = 100 * E['altered'] / max(1, E['all'])
        nw = sum(E['why'].values())
        for k in ('wait', 'contra', 'struct', 'uncert'):
            r['why_' + k] = 100 * E['why'][k] / max(1, E['amb'])        # % of interrupted EFFECTS
        r['amb'] = E['amb']
        rows.append(r)
    return rows


def write(name, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(RES, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def show(tag, r):
    print(tag, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)


# ------------------------------------------------------------------ experiments (run as separate parts)
def part_main():
    main_pols = ALL_POLICIES + ['g2-only']
    out, eff = run(main_pols)
    rows = summarize(out, eff, main_pols)
    base = out['ghost']
    comps = [p for p in ALL_POLICIES if p != 'ghost']     # Holm family as in round 2; g2-only reported unadjusted
    pv_d, pv_l = [], []
    for p in comps:
        b = sum(1 for g, x in zip(base, out[p]) if g[0] == 1 and x[0] == 0)
        c = sum(1 for g, x in zip(base, out[p]) if g[0] == 0 and x[0] == 1)
        pv_d.append(mcnemar(b, c))
        b = sum(1 for g, x in zip(base, out[p]) if (g[0] or g[1]) and not (x[0] or x[1]))
        c = sum(1 for g, x in zip(base, out[p]) if not (g[0] or g[1]) and (x[0] or x[1]))
        pv_l.append(mcnemar(b, c))
    ad, al_ = holm(pv_d), holm(pv_l)
    for r in rows:
        if r['policy'] in comps:
            r['p_dup'] = ad[comps.index(r['policy'])]
            r['p_err'] = al_[comps.index(r['policy'])]
        elif r['policy'] == 'g2-only':
            b = sum(1 for g, x in zip(base, out['g2-only']) if g[0] == 1 and x[0] == 0)
            c = sum(1 for g, x in zip(base, out['g2-only']) if g[0] == 0 and x[0] == 1)
            r['p_dup'] = mcnemar(b, c)
            r['p_err'] = float('nan')
        else:
            r['p_dup'] = r['p_err'] = float('nan')
        show('main', r)
    write('planner_sim.csv', rows)
    cl = []
    for p in ('ghost', 'ghost-src', 'ghost-joint', 'rules', 'always-ask', 'key', 'g2-only'):
        for c, C in sorted(eff[p]['cls'].items()):
            cl.append(dict(policy=p, cls=c, effects=C['n'], ask=100 * C['ask'] / C['n'], secs=C['secs'] / C['n'],
                           cdup=100 * C['d1'] / max(1, C['n1'])))
            show('class', cl[-1])
    write('planner_class.csv', cl)


STRESS = ['r1', 'r1+persist', 'default', 'cross0.3', 'lagtail', 'lagtail-cal', 'g2break', 'g2nodedup',
          'doze-unaware', 'doze-aware', 'common0.5', 'mon0.05', 'user0.2', 'combined']
POP = ['iworld-passive', 'iworld-fault', 'cm0.005-fault', 'cm0.02-fault', 'cm0.05-fault']


def part_stress(chunk=None):
    """chunk 'i/n' runs every n-th scenario starting at i and writes planner_stress.part<i>.csv (render.py merges)."""
    scs = STRESS + POP
    tag = ''
    if chunk:
        i, n = (int(x) for x in chunk.split('/'))
        scs, tag = scs[i::n], f'.part{i}'
    st = []
    for sc in scs:
        pols = ['ghost-v1', 'ghost', 'ghost-src', 'ghost-joint', 'rules']
        o, ef = run(pols, scenario=sc)
        for r in summarize(o, ef, pols):
            r['scenario'] = sc
            st.append(r)
            show('stress ' + sc, r)
    write(f'planner_stress{tag}.csv', st)


def part_sweep():
    sw = []
    for a in [0.1, 0.03, 0.01, 0.003, 0.001]:
        pols = ['ghost', 'ghost-src', 'ghost-joint', 'ghost-nocal']
        o, ef = run(pols, alpha=a, beta=a)
        for r in summarize(o, ef, pols):
            r['alpha'] = a
            sw.append(r)
            show(f'sweep {a}', r)
    write('planner_alpha_sweep.csv', sw)


def part_user():
    us = []
    for ue in [0.0, 0.05, 0.1, 0.2]:
        pols = ['always-ask', 'nonce-ask', 'maj3-ask', 'rules', 'ghost']
        o, ef = run(pols, overrides=dict(user_err=ue))
        for r in summarize(o, ef, pols):
            r['user_err'] = ue
            us.append(r)
            print('user', ue, r['policy'], round(r['dup'], 3), round(r['loss'], 3), round(r['ask'], 2), flush=True)
    write('planner_user.csv', us)


def part_sens():
    se = []
    variants = [('default', {}), ('look-alikes x0.5', dict(look_scale=0.5)), ('look-alikes x2', dict(look_scale=2.0)),
                ('no nonce fields', dict(nfield_none=True)), ('visible nonce opt-in', dict(nonce_policy='visible')),
                ('no G2 apps', dict(g2_all=False)), ('G2 wherever hop-1', dict(g2_all=True))]
    for name, ov in variants:
        pols = ['key', 'always-ask', 'nonce-ask', 'ghost']
        o, ef = run(pols, seeds=SEEDS[:2], overrides=ov)
        for r in summarize(o, ef, pols):
            r['variant'] = name
            se.append(r)
            print('sens', name, r['policy'], round(r['dup'], 3), round(r['loss'], 3), round(r['ask'], 2), flush=True)
    write('planner_sensitivity.csv', se)


def part_ncal():
    """Calibration budget: effects per (app version, outcome) from 100 to 5,000; and version drift (kappa) with
    pooled calibration, with and without a 200-effect shift test."""
    rows = []
    for sc in [0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]:
        pols = ['ghost', 'ghost-src', 'ghost-joint']
        o, ef = run(pols, overrides=dict(ncal_scale=sc))
        for r in summarize(o, ef, pols):
            r['ncal'] = int(round(NCAL * sc))
            r['study'] = 'ncal'
            rows.append(r)
            show(f'ncal {r["ncal"]}', r)
    for kap in [1.0, 3.0, 5.0, 10.0]:
        for st in (0, 200):
            o, ef = run(['ghost'], overrides=dict(kappa=kap, shift_test=st))
            r = summarize(o, ef, ['ghost'])[0]
            r['kappa'], r['shift_test'], r['study'] = kap, st, 'drift'
            rows.append(r)
            show(f'drift k={kap} st={st}', r)
    write('planner_ncal.csv', rows)


def part_decomp():
    """Where does the over-delivery come from?  For each seed and app (single-effect budget alpha = 1%), the
    certified union bound B_cp(tau_a) of the chosen threshold, the same union evaluated with the TRUE family rates
    (Monte Carlo, 50,000 committed effects per app), and the realized retry rate on visible committed effects."""
    S = scen('default')
    delta = 0.01 / (10 * K_PRODUCT)
    rows = []
    for s in SEEDS:
        wrng = random.Random(s)
        app_eps, _ = app_errors(wrng)
        Q = _calibrate(random.Random(s * 31 + 7), app_eps, S, delta, 'product')
        trng = random.Random(s * 977)
        for app in APPS:
            A = app_cfg(app, S)
            names = [f for f in cal_families(A, S) if f != 'nonce' or A['nfield'] == 'private']
            e1 = cal_effects(trng, app, A, S, app_eps, 1, 50000)
            qt = marginal_bounds(e1, e1[:10], names, 0.5)          # point estimates on the abs side
            for f in names:
                n1 = qt[f]['n1']
                qt[f]['abs'] = {r: qt[f]['ge1'].get(r, 0) / n1 for r in levels(f)['abs']}
            lv = [Q[app][f]['abs'] for f in names]
            lvt = [qt[f]['abs'] for f in names]
            tau = tau_for(cert_table(lv), 0.005)
            bcp = B_of(lv, tau)
            btrue = B_of(lv, tau, lvt)
            # realized: run the cascade on the 100k visible committed effects
            k = 0
            for rec in e1:
                vt = {f: verdict_of(f, rec[f]) for f in names}
                if stop_product(vt, names, Q[app], 'abs', A['G2'] or A['local']) <= tau:
                    k += 1
            rows.append(dict(seed=s, app=app, tau=tau, B_cp=bcp, B_true=btrue, realized=k / len(e1)))
            show('decomp', rows[-1])
    write('planner_decomp.csv', rows)


def real_overrides():
    """Map emulator measurements (artifact/results/real/params.csv: name,value,provenance, written by real_params.py
    from the per-trial CSVs) onto generative parameters.  Returns {} when no measurements exist."""
    path = os.path.join(RES, 'real', 'params.csv')
    if not os.path.exists(path):
        return {}
    ov = {}
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            v = row['value']
            if row['name'].startswith('elem_lag_'):       # per-cell trial samples "lag:lagblind|..."
                ov.setdefault('elem_lag', {})[row['name'][len('elem_lag_'):]] = \
                    [(float(x.split(':')[0]), int(x.split(':')[1])) for x in v.split('|')]
                continue
            if row['name'] == 'elem_tail_ub':
                ov['elem_tail_ub'] = float(v)
                continue
            if row['name'] not in BASE:
                continue
            if '|' in v:
                ov[row['name']] = [float(x) for x in v.split('|')]
                continue
            try:
                ov[row['name']] = float(v)
            except ValueError:
                ov[row['name']] = v
    if 'no_vlm' in ov:
        ov['no_vlm'] = bool(ov['no_vlm'])
    return ov


def part_rulesweep():
    """Parameterised same-evidence rule family (R2 m8): wait x quorum, default world, the paired workflows of Table 2."""
    o, ef = run(RULE_FAMILY)
    rows = summarize(o, ef, RULE_FAMILY)
    for r in rows:
        show('rulesweep', r)
    write('planner_rules_sweep.csv', rows)


REAL_POLICIES = ['redo', 'app-state', 'rules', 'rules-w30-all', 'always-ask', 'g2-only', 'ghost', 'ghost-src',
                 'ghost-joint']
GHOSTS = ['ghost', 'ghost-src', 'ghost-joint']
LAB_MIX = [('agent-kill', 0.10), ('app-kill', 0.10), ('net-blackout', 0.70), ('kill+net', 0.10)]   # easy-to-inject lab mix


def part_real():
    """MEASURED-PARAMETER simulation on the campaign-2 profiles (Element, K-9 without and with an IMAP Sent folder):
    measured G2 / failed-state behaviour, per-fault-class lag laws, bot rates and family errors; the fault mix, the
    absent-side error rates, the Monitor and the user stay as in the model.  Labels are simulated draws from the measured
    law (2,000 per outcome, per class when keyed).  Rows (tag):
      main      Element, fault-injected labels, fault-class-keyed bounds and lag tables (the recommended configuration)
      pooled    Element, fault-injected labels pooled over classes, lab mix = deployment mix
      mixlab    Element, pooled, lab fault mix != deployment (net-heavy)          [R2 m4]
      mixkeyed  Element, keyed, same mismatched lab mix
      unknown   Element, keyed, fault class never known (max-over-classes / intersection fallback)
      passive   Element, passive labels
      tail      Element, a lag tail beyond the window at the 95% upper bound of 0/101 censored, NOT in the lab logs
      tailcal   the same tail, present in the lab logs
      five      Element, keyed, 5,000 labels
      k9, k9sent (fault / passive)"""
    ov = real_overrides()
    if not ov:
        print('no artifact/results/real/params.csv; skipping measured-parameter run')
        return
    tail = ov.pop('elem_tail_ub', 0.0)
    rows = []
    E = 'element'
    runs = [('main', E, dict(cal_pop='fault', keyed='all'), REAL_POLICIES),
            ('pooled', E, dict(cal_pop='fault'), GHOSTS),
            ('mixlab', E, dict(cal_pop='fault', cal_faults=LAB_MIX), GHOSTS),
            ('mixkeyed', E, dict(cal_pop='fault', cal_faults=LAB_MIX, keyed='all'), GHOSTS),
            ('unknown', E, dict(cal_pop='fault', keyed='all', class_known=0.0), GHOSTS),
            ('passive', E, dict(cal_pop='passive'), GHOSTS),
            ('tail', E, dict(cal_pop='fault', keyed='all', lag_tail=tail, lag_tail_cal=False),
             ['rules', 'rules-w30-all', 'g2-only'] + GHOSTS),
            ('tailcal', E, dict(cal_pop='fault', keyed='all', lag_tail=tail, lag_tail_cal=True), GHOSTS),
            ('five', E, dict(cal_pop='fault', keyed='all', ncal_scale=2.5), GHOSTS),
            ('k9', 'k9', dict(cal_pop='fault'), ['app-state', 'rules', 'always-ask', 'g2-only'] + GHOSTS),
            ('k9pass', 'k9', dict(cal_pop='passive'), GHOSTS),
            ('k9sent', 'k9sent', dict(cal_pop='fault'), ['app-state', 'rules', 'always-ask', 'g2-only'] + GHOSTS),
            ('k9sentpass', 'k9sent', dict(cal_pop='passive'), GHOSTS),
            ('k9sentpass5', 'k9sent', dict(cal_pop='passive', ncal_scale=2.5), GHOSTS)]
    if len(sys.argv) > 2:
        runs = [r for r in runs if r[0] in sys.argv[2:]]
    for tag, app, extra, pols in runs:
        o, ef = run(pols, overrides=dict(ov, catalog='measured', only_app=app, **extra))
        for r in summarize(o, ef, pols):
            r['tag'], r['app'], r['cal_pop'] = tag, app, extra['cal_pop']
            r['ncal'] = int(round(NCAL * extra.get('ncal_scale', 1.0)))
            r['keyed'] = extra.get('keyed') or 'pooled'
            r['lag_tail'] = extra.get('lag_tail', 0.0)
            rows.append(r)
            show(f'real {tag}', r)
    write('planner_real.csv' if len(sys.argv) <= 2 else 'planner_real_partial.csv', rows)


GH2 = ['ghost', 'ghost-joint']
VETTED = ['rules-vetted', 'rules-vetted-small']
NET_LAB = [('agent-kill', 0.0), ('app-kill', 0.0), ('net-blackout', 1.0), ('kill+net', 0.0)]   # lab injects network cuts only
REAL4 = {
    # R1 M1: rules vetted on the same fault-injected labels (and on 30 per class), every measured profile
    'vet':       ('element', dict(cal_pop='fault', keyed='all'), VETTED + ['rules-w30-all']),
    'vetk9':     ('k9', dict(cal_pop='fault'), VETTED),
    'vetk9sent': ('k9sent', dict(cal_pop='fault'), VETTED),
    # R2 R4-2 / R1 M2: lag logs tied to the label budget (labels per class and outcome = logged lags per class)
    'lag2k':     ('element', dict(cal_pop='fault', keyed='all', nlag=2000), GH2),
    'lag5k':     ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, nlag=5000), GH2),
    'lag10k':    ('element', dict(cal_pop='fault', keyed='all', ncal_scale=5.0, nlag=10000), GH2),
    'lag20k':    ('element', dict(cal_pop='fault', keyed='all', ncal_scale=10.0, nlag=20000), GH2),
    'boot10k':   ('element', dict(cal_pop='fault', keyed='all', ncal_scale=5.0), GH2),
    # R2 R4-3: unlogged tail (95% bound) at 5,000 labels, with bootstrapped and with tied lag logs
    'tail5':     ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, lag_tail='ub', lag_tail_cal=False), GH2),
    'tail5tied': ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, nlag=5000, lag_tail='ub',
                                  lag_tail_cal=False), GH2),
    # R2 R4-1: nonzero downtime before the class's clock origin, waiting from that origin (design) or from t0 (wrong)
    'down5':     ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, downtime=5.0), GH2),
    'down15':    ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, downtime=15.0), GH2),
    't0down5':   ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, downtime=5.0, clock='t0'), GH2),
    't0down15':  ('element', dict(cal_pop='fault', keyed='all', ncal_scale=2.5, downtime=15.0, clock='t0'), GH2),
    # R2 m-a: the lab injects network cuts only (the easy fault): pooled vs keyed calibration
    'netlab':    ('element', dict(cal_pop='fault', cal_faults=NET_LAB), GH2),
    'netlabkey': ('element', dict(cal_pop='fault', cal_faults=NET_LAB, keyed='all'), GH2),
}


def part_real4(tags=None):
    """Round-4 measured-parameter rows (R1 M1/M2, R2 R4-1/R4-2/R4-3/m-a); one CSV per tag (planner_real4_<tag>.csv)."""
    ov = real_overrides()
    if not ov:
        print('no artifact/results/real/params.csv; skipping')
        return
    tail = ov.pop('elem_tail_ub', 0.0)
    for tag in (tags or list(REAL4)):
        app, extra, pols = REAL4[tag]
        extra = dict(extra)
        if extra.get('lag_tail') == 'ub':
            extra['lag_tail'] = tail
        o, ef = run(pols, overrides=dict(ov, catalog='measured', only_app=app, **extra))
        rows = []
        for r in summarize(o, ef, pols):
            r['tag'], r['app'], r['cal_pop'] = tag, app, extra['cal_pop']
            r['ncal'] = int(round(NCAL * extra.get('ncal_scale', 1.0)))
            r['nlag'] = extra.get('nlag') or N_LAG
            r['keyed'] = extra.get('keyed') or 'pooled'
            r['lag_tail'] = extra.get('lag_tail', 0.0)
            r['downtime'], r['clock'] = extra.get('downtime', 0.0), extra.get('clock', 'origin')
            rows.append(r)
            show(f'real4 {tag}', r)
        write(f'planner_real4_{tag}.csv', rows)


def part_share():
    """Which families carry certified decisions (default world, product and joint planners)?"""
    rows = []
    for p in ('ghost', 'ghost-src', 'ghost-joint'):
        USED.clear()
        run([p])
        tot = sum(USED.values())
        for fam in ('hop1', 'nonce', 'digest', 'vlm'):
            k = sum(c for key, c in USED.items() if fam in key[1:])
            rows.append(dict(policy=p, family=fam, share=100 * k / max(1, tot), n=k, total=tot))
            show('share', rows[-1])
        k = sum(c for key, c in USED.items() if key[1:] == ('vlm',) or (len(key) > 1 and 'vlm' == key[-1]))
        rows.append(dict(policy=p, family='vlm-decisive', share=100 * k / max(1, tot), n=k, total=tot))
        show('share', rows[-1])
    write('planner_share.csv', rows)


PARTS = dict(share=part_share, main=part_main, rulesweep=part_rulesweep, stress=part_stress, sweep=part_sweep, user=part_user, sens=part_sens, ncal=part_ncal,
             decomp=part_decomp, real=part_real)

if __name__ == '__main__':
    todo = sys.argv[1:] or list(PARTS)
    if todo and todo[0] == 'real4':
        part_real4(todo[1:] or None)
        sys.exit(0)
    if todo and todo[0] == 'real':
        todo = ['real']                                 # extra arguments select rows of part 'real'
    for t in todo:
        if t.startswith('stress') and len(t) > 6:
            part_stress(t[6:])
        else:
            PARTS[t]()
