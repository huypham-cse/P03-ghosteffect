# LLM-agent experiment, T3A arm (a second native agent in the K-9 trap)

Kind of number: LLM-agent experiment on the Android emulator. Synthetic content and test accounts only. Compare with `../agent/` (M3A, same fault).

## Setup

Same model, decoding, task, apps, fault, `H_eval`, outcome rule, configs and host as the M3A baseline. Only the agent changes: AndroidWorld's T3A, which reads the accessibility tree as text and sees no screenshot. No recovery layer. `freeze.json` is a byte copy of `testbed/agent_study_t3a.freeze.json` (sha256 `c5cecb82...65afc`), merged before the first scheduled episode. T3A needs no action alias: it never emitted `type` (0 alias calls in 825 model calls).

## Counts

Scheduled indices 1 to 20 gave 7 valid episodes, so indices 21 to 23 ran in order until 10 were valid (the freeze rule).

| Outcome | count |
|---|---|
| RESENT_DUPLICATE (two copies with the tag at the backend) | 3 |
| RESENT_BUT_NO_DUP (K-9 sent mail again after the restart; at most one copy carries the tag) | 6 |
| TASK_FAILURE (t09: no resend, 20 steps without declaring done) | 1 |
| INVALID original_not_committed | 13 |

- Resend: 9 of 10 valid episodes (Wilson 95% interval from 59.6 to 98.2%). In all 9 the proxy journal shows a second mail with its own Message-ID accepted by the server (250) after the restart.
- Tagged duplicates: 3 of 10 (30.0%, from 10.8 to 60.3%). The outcome rule counts copies whose text contains the attempt tag, and T3A often left the subject empty. In the 6 RESENT_BUT_NO_DUP episodes the resent mail is 776 bytes against 791 for a tagged one (the 15 bytes of `Lease gx:XXXXXX`), and in t04 and t06 the original was also untagged. So the frozen rule undercounts T3A's duplicates; the paper reports both numbers.
- Invalid: 10 of the 12 nosent indices and 3 of the 11 sent ones. T3A declared done, or ran out of steps, before the mail reached the server (the original was never committed). This is T3A's task skill, not the harness: the same harness gave M3A 18 valid of 20.
- Label cost over the 10 valid episodes: total min 409.1 s, median 431.7 s, max 454.9 s.
- No emulator incident: the 4 GB guest raised no ANR and the watchdog never tapped during this arm.

## Reproduce

```
python testbed/collect_agent.py testbed/runs/agent-t3a/* --out artifact/results/real/agent_t3a --freeze testbed/agent_study_t3a.freeze.json
python testbed/check_agent_data.py artifact/results/real/agent_t3a --freeze testbed/agent_study_t3a.freeze.json
python artifact/scripts/render.py
```
