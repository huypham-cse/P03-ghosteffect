# LLM-agent experiment, kill-only arm (only the agent restarts; K-9 keeps running)

Kind of number: LLM-agent experiment on the Android emulator. Synthetic content and test accounts only. Compare with `../agent/` (M3A, force-stop).

## Setup

Same agent (M3A), model, decoding, task, apps, `H_eval`, outcome rule, configs and host as the baseline. Only the fault changes: the proxy drops the reply after the server commits, K-9 records the error, and then only the agent is killed and restarted on the same task. K-9 is not force-stopped or relaunched, so its screen and Outbox stay as they were. `H_eval` runs from the agent's restart. No recovery layer. `freeze.json` is a byte copy of `testbed/agent_study_killagent.freeze.json` (sha256 `6c766d3d...cfa69`), merged before the first scheduled episode.

## Counts

Scheduled indices 1 to 20; 19 valid, so indices 21 to 30 were not used.

| Outcome | count |
|---|---|
| RESENT_DUPLICATE | 19 |
| INVALID original_not_committed (k17: the agent declared done before the mail reached the server) | 1 |

- Duplicate rate: 19/19 (100.0%, Wilson 95% interval from 83.2 to 100.0%). Against the force-stop baseline (17 of 18) the exact two-sided Fisher p is 0.486: keeping K-9 alive does not change the outcome.
- In 5 episodes (k08, k12, k14, k18, k20) the restarted agent sent twice more, leaving three tagged copies with three Message-IDs.
- Alias: 54 of 644 model calls renamed `type` to `input_text` (`local_model.py`, as in the baseline).
- Label cost over the 19 valid episodes: total min 391.7 s, median 407.0 s, max 417.6 s.
- No emulator incident: the 4 GB guest raised no ANR and the watchdog never tapped during this arm.

## Reproduce

```
python testbed/collect_agent.py testbed/runs/agent-killagent/* --out artifact/results/real/agent_killagent --freeze testbed/agent_study_killagent.freeze.json
python testbed/check_agent_data.py artifact/results/real/agent_killagent --freeze testbed/agent_study_killagent.freeze.json
python artifact/scripts/render.py
```
