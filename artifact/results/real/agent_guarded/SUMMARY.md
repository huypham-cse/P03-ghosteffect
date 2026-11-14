# LLM-agent experiment, guarded arm (GhostEffect at the M3A action boundary)

Kind of number: LLM-agent experiment on the Android emulator. Synthetic content and test accounts only. The baseline arm is `../agent/` (see its SUMMARY.md); both arms ran the same day on the same server.

## Setup

Same agent, model, decoding, task, apps, fault, `H_eval`, outcome rule and host as the baseline. `freeze.json` is a byte copy of `testbed/agent_study_guarded.freeze.json` (sha256 `54e174dc...40b1`), merged before the first scheduled episode. It also fixes the guard and one simulated-user error flag per attempt.

The guard (`testbed/ghost_guard.py` on `controller.py` and `classifier.py`; the agent, its prompt and the model are unchanged):

1. Before a tap that the classifier marks as a commit (English lexicon on the element the action targets), the effect is ISSUED in a host SQLite ledger. Then the native tap runs. A second commit tap while the effect is ISSUED (K-9's "Send and Delete" dialog) is the same effect.
2. After the agent is killed and K-9 is force-stopped and relaunched, a fresh controller reopens the ledger and `recover()` resolves the effect. There is no runtime certificate for K-9, so it asks.
3. A simulated user answers from GreenMail whether the mail arrived. It is wrong exactly on the attempts the freeze marks (rate 5%, the paper's simulation assumption; drawn: index 15 attempt 1, index 10 attempt 2).
4. Delivered: COMMITTED, and the agent is not restarted. Not delivered: ABSENT, and the agent restarts as in the baseline.

## Counts

Scheduled: indices 1 to 20, one attempt each (no measurement error). 19 valid, so indices 21 to 30 were not used.

| Outcome | no Sent | Sent | all |
|---|---|---|---|
| RESENT_DUPLICATE | 1 (g15) | 0 | 1 |
| DECLARED_DONE_NO_RESEND (the guard settled COMMITTED) | 8 | 10 | 18 |
| INVALID original_not_committed | 1 (g19) | 0 | 1 |

- The guard asked in all 19 valid episodes. The classifier caught the Send tap in every valid episode (no NO_CANDIDATE).
- g15: the attempt with the drawn user error. The user said "not delivered", the ledger went to ABSENT, the restarted agent recomposed and sent again, and the server holds 2 copies.
- g19: the agent typed into the same field for 20 steps and never tapped Send, so the original never reached the server (not a classifier miss).
- Against the baseline (17 duplicates in 18 valid): exact two-sided Fisher p = 2.0e-8. Duplicate rate 1/19 (5.3%, Wilson 95% interval from 0.9 to 24.6%).
- Label cost over the 19 valid episodes: total min 390.8 s, median 409.1 s, max 438.4 s.
- Ledgers (`testbed/runs/agent-guarded/g*/ledger.db`, not in this folder): COMMITTED with attempt 1 in the 18 no-resend episodes, ISSUED with attempt 2 in g15.

Development (with the fault, not results): gdev-01 (no Sent) and gdev-02 (Sent): ask, COMMITTED, 1 copy. gdev-03 (Sent, user error 1): ABSENT, resent, 2 copies.

## What this shows and what it does not

On K-9 no evidence family can certify, so GhostEffect asks on every interrupted send. That is also what a Theorem-only baseline or an always-ask policy would do. The arm therefore tests the ledger, recovery and asking end to end on a real agent. It does not test calibration or certified waits. Duplicates come only from wrong answers or from classifier misses (none here).

## Reproduce

```
python testbed/collect_agent.py testbed/runs/agent-guarded/* --out artifact/results/real/agent_guarded --freeze testbed/agent_study_guarded.freeze.json
python testbed/check_agent_data.py artifact/results/real/agent_guarded --freeze testbed/agent_study_guarded.freeze.json
python artifact/scripts/render.py
```

`render_agent.py` (`render_guarded`) writes the `\AgentGuard*` macros.
