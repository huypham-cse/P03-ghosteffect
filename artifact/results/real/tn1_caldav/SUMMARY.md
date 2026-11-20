# TN1: held-out validation of the GUI-only planner on a real app (Etar + DAVx5 + Radicale, AVD)

Collected 19 to 20 November 2026 with `testbed/caldav_planner.py` (spec, schedules and reader frozen in
`testbed/tn1/` before collection; the reader and `recovery.py` hashes are part of the store's domain).

**Effect.** Create a calendar event whose title is a fresh nonce in Etar; DAVx5 syncs it to Radicale. X=1: the save
commits at the server, the reply is lost, then the fault lands. X=0: the edit screen is open and the fault lands
before the save. Fault classes, applied to both apps: none, app-kill (kill -9), force-stop.

**Planner.** The real `recovery.py` (Algorithm 1) reads only Etar's GUI. Family hop1 (the app's local store) has two
views: Etar's search for the nonce and Etar's agenda. No GUI view shows DAVx5's hop-2 acknowledgement, so the stratum
declares G2 unusable: a committed effect cannot be certified and is asked; an absent one can be certified and retried.

## Calibration (product mode, alpha = beta = 0.1, keyed by fault class)

| | per class | total | read errors |
|---|---|---|---|
| committed effects (X=1), both views read the event | 133 | 399 | 0 |
| absent effects (X=0), both views read no event | 30 | 90 | 0 |

K = 9, delta = 1.11e-3. The one-sided bound on reading "absent" for a committed effect is 0.0499 in every class,
equal to the threshold alpha_test = 0.05, so the store certifies absence in all three classes. 86 trials were
INVALID (rig failures, mostly upload barrier timeouts) and were rerun; no valid label was dropped or changed.

## Held-out test (40 per class and outcome, 240 effects)

| fault class | committed: decision | absent: decision |
|---|---|---|
| none | ASK 40/40 | RETRY 40/40 |
| app-kill | ASK 40/40 | RETRY 40/40 |
| force-stop | ASK 40/40 | RETRY 40/40 |

- Retries of committed effects: **0/120** (one-sided 95% Clopper-Pearson upper bound 2.47%).
- Absent effects declared committed (loss): 0/120. Duplicates on the server: 0/240.
- Every absent effect was retried with reason `certified_hop1_absence`; asks were 120/240, all on committed effects.
- After the retry the agent recomposed the event through the GUI: 117/120 reached the server exactly once within
  the 90 s window. The other 3 (t0132, t0133, t0135) stayed in Etar's local store, unsent, during an AVD DNS outage
  (20 Nov 13:00 to 13:13) that blocked every DAVx5 sync; they are kept in the data and reported separately.
- 5 test trials were INVALID (rig) and rerun.

## Limits

One app pair on an emulator; hop1 is a local, easily read store, so the reads were perfect in this sample; the
committed side is never certified because no GUI view of the hop-2 acknowledgement exists for this app; the budget is
alpha = beta = 0.1, the loosest that 133 zero-error labels per class can certify. Rig interventions during collection
(stale proxy arms, DAVx5 WorkManager backoff resets between trials, the DNS outage fix) changed only when DAVx5
uploaded, never what the planner read; they are logged in `team/b-log.md`. Per-trial evidence (screen dumps, receipts,
proxy journal) is in the ignored `testbed/runs/tn1-calibration/` and `testbed/runs/tn1-test/`.
