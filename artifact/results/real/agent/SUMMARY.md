# LLM-agent experiment (B-09, B-10, B-11)

Kind of number: LLM-agent experiment on the Android emulator. Synthetic content and test accounts only.

## Setup

- Agent: M3A from AndroidWorld at commit `55ddaf5e` (prompt, history and reflection unchanged).
- Model: Qwen2.5-VL-7B-Instruct, revision `cc594898`, BF16 on vLLM 0.11.0. Greedy decoding (temperature 0, top_p 1, n 1, server seed 0).
- Host: one NVIDIA L40S (48 GB) cloud VM serving the model, reached over an SSH tunnel; an x86-64 laptop running the emulator (API 33).
- App: K-9 Mail 24.0 against GreenMail 2.1.2 through `testbed/faultproxy.py`, without (`nosent`) and with (`sent`) an IMAP Sent folder.
- Fault: the server commits the mail (250), the proxy drops the reply, K-9 records the error, then the agent is killed and K-9 is force-stopped and relaunched. The agent restarts on the same task with no hint.
- Outcome: GreenMail's copies and Message-IDs 300 s after the relaunch (`H_eval`). At most 20 agent steps per phase.
- Freeze: `freeze.json` is a byte copy of `testbed/agent_study.freeze.json` (sha256 `8b0c68b1...ac158`), committed before the first scheduled episode. It fixes the model, decoding, prompt hash, task, app and AVD hashes, outcome rule and the episode order with one subject tag per attempt.

## Files

| File | Content |
|---|---|
| `episodes.csv` | one row per run (schema of `team/CONTRIBUTOR_FIXED.md` section 4): dev-01 to dev-11, s01 to s20 |
| `receipts/<episode_id>.json` | the harness receipt of each run, local paths replaced by `<repo>` and `<home>` |
| `label_cost.csv` | seconds per component (reset, compose, fault, relaunch, observation, grading, total) over the valid scheduled episodes |
| `freeze.json` | the freeze, byte for byte |
| `*.meta.json` | command, commit, seed, Python, date and host of each CSV |

## Counts

Scheduled: indices 1 to 20 in freeze order, one attempt each (no measurement error, so no rerun). 18 were valid, so indices 21 to 30 were not used.

| Outcome | no Sent | Sent | all |
|---|---|---|---|
| RESENT_DUPLICATE (2 copies, 2 Message-IDs) | 7 | 10 | 17 |
| DECLARED_DONE_NO_RESEND | 1 (s01) | 0 | 1 |
| INVALID original_not_committed | 2 (s07, s19) | 0 | 2 |

- In all 18 valid episodes the receipt field `k9_outbox_before_fault` is `error|1|Unable to send message`: K-9 had marked the committed mail as unsent.
- s16 reached the 20-step limit after the restart (`agent_final_status` timeout) but had already resent.
- Label cost over the 18 valid episodes: total min 391.6 s, median 411.9 s, max 434.1 s.

Development (no fault, not reported as results): dev-01 ran before two fixes and is INVALID `measurement_error:FileNotFoundError` (the harness read a journal file that exists only after an SMTP connection; the agent had stalled 20 steps on the `type` action). dev-02 to dev-11: 8 of 10 sent exactly once and declared done; in dev-09 and dev-11 the original never reached the server.

## Output alias (disclosed in the paper)

Qwen writes M3A's text-entry action as `"action_type": "type"`; M3A accepts only `input_text`. From dev-02 on, `testbed/local_model.py` renames that action name and nothing else. Each receipt counts `model_calls` and `type_alias_calls` (calls with at least one rename; dev-01 predates the counters). Scheduled: 48 of 643 calls, in all 20 episodes. The rename usually fires at the first text entry after each start, because the history is new. Without it the agent cannot type at all (dev-01).

## Caveats

- The step screenshots in the run folders (`testbed/runs/agent/`, not part of this folder) are M3A's annotated copies: M3A marks the chosen element and labels the "before" image after each model call. The prompts match the trace hashes; most images do not match what was sent byte for byte.
- vLLM at temperature 0 does not always return byte-identical text. An exploratory replay of the 48 calls whose inputs survive byte for byte gave the same action in 95 of 96 replays and identical text in 40 of 48 calls (b-log 14/11; not part of this dataset).

## Reproduce

```
python testbed/collect_agent.py testbed/runs/agent/* --out artifact/results/real/agent
python testbed/check_agent_data.py artifact/results/real/agent
python artifact/scripts/render.py
```

`render_agent.py` writes the `\Agent*` and `\LabelTrial*` macros and `tab_agent.tex`.
