# LLM-agent experiment, rules arm (same-evidence rule cascade at the M3A action boundary)

Kind of number: LLM-agent experiment on the Android emulator. Synthetic content and test accounts only. Compare with `../agent/` (native), `../agent_guarded/` (GhostEffect).

## Setup

Same agent, model, decoding, task, apps, fault, `H_eval`, outcome rule and host as the baseline. Every index uses the configuration with an IMAP Sent folder. Without one, the only end-to-end family is the VLM, which has no real reader here. `freeze.json` is a byte copy of `testbed/agent_study_rules.freeze.json` (sha256 `dea3e1fe...afb0`), merged before the first scheduled episode.

The rules (`testbed/ghost_guard.py` `Rules`; the paper's same-evidence rules, RQ3 and `planner_sim.resolve_rules`) use the same ledger and boundary as GhostEffect:

1. Before a classified commit tap, the effect is ISSUED in the host ledger.
2. After the kill and relaunch, they read the K-9 folders that hold the mail. The Outbox is hop 1. K-9 is not G2, so hop 1 gives no vote.
3. After a fixed 10 s wait they read again:
   - mail in the Sent list: COMMITTED, and the agent is not restarted;
   - absent: every family reads absent, so ABSENT and the agent restarts (retry);
   - no reading: ask the simulated user.
4. Reads come from K-9's own database, an upper bound on a perception-based reader. This favours the rules.

## Counts

Scheduled indices 1 to 20; 15 valid, so indices 21 to 30 were not used.

| Outcome | count |
|---|---|
| RESENT_DUPLICATE (rules retried, the agent resent) | 14 |
| TASK_FAILURE (r11: rules retried, the restarted agent called open_app 20 times) | 1 |
| INVALID original_not_committed (r07, r08) | 2 |
| INVALID measurement_error, both attempts (indices 9, 10, 12) | 3 |

- The rules retried in all 15 valid episodes. K-9 writes its Sent list only after a successful send, so after the lost reply the Sent list never showed the mail. The rules never asked. The classifier caught the Send tap in every valid episode.
- Duplicate rate: 14/15 (93.3%, Wilson 95% interval from 70.2 to 98.8%). Against GhostEffect's Sent-configuration episodes (0 of 10), the exact two-sided Fisher p is 3.4e-6.
- Label cost over the 15 valid episodes: total min 398.7 s, median 413.1 s, max 506.4 s.

## Emulator incidents during this arm

- r09: the focus check at force-stop failed twice. r10 and r12: the reset failed twice, because K-9 was not the focused window.
- The cause was the emulator. After about ten hours with a 2 GB guest, System UI raised "isn't responding" dialogs. The dialog took the focus, and later Android's "LAST ANR" record in `dumpsys window` (whose first `mCurrentFocus` line is null) misled the reset's focus check. Indices 9, 10 and 12 stay INVALID: one rerun per index.
- Fixes, logged in `team/b-log.md`:
  - 02:43: the guest was rebooted.
  - 02:57 to 02:59: a watchdog tapped "Wait" on the System UI dialog 14 times. That was before r11's agent phases, and there were no taps after.
  - 03:08: the emulator restarted with 4 GB of guest RAM (`-memory 4096`; the hashed AVD config is unchanged). Indices 13 to 20 ran on it with no ANR.
  - The runner gained a rule: the same command resumes past an index that already has two recorded measurement errors.

## Reproduce

```
python testbed/collect_agent.py testbed/runs/agent-rules/* --out artifact/results/real/agent_rules --freeze testbed/agent_study_rules.freeze.json
python testbed/check_agent_data.py artifact/results/real/agent_rules --freeze testbed/agent_study_rules.freeze.json
python artifact/scripts/render.py
```
