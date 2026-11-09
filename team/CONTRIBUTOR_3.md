# Contributor 3: Emulator Testbed and LLM-Agent Experiment Owner

> **Project:** GhostEffect (MobiSys 2027)
> **Your role:** You own `testbed/` and the **one new measurement** in this submission: run a real LLM GUI agent (M3A from AndroidWorld) on **interrupted K-9 Mail sends** and measure how often it re-sends (creating a duplicate). All four internal reviewers asked for this, and the paper's motivation depends on it. You also measure the **wall-clock cost of one fault-injected trial**, which the paper needs for its labeling-cost estimate.
> **Hard deadlines:** abstract **Nov 27**, paper **Dec 4, 2026**. **Your data delivery: Thu Nov 26.** Plan to finish the main runs by Nov 24.

---

## 0. Read this first (about 3 hours, day 1)

| # | File | Why |
|---|---|---|
| 1 | `manuscript/main.pdf` §2.3, §6, §7.7, Fig. 1 | What the K-9 ghost effect is and how campaign 2 measured it with a **scripted** redo. |
| 2 | `artifact/results/real/SUMMARY.md` | The original campaign protocol: fault proxy, commit-then-drop-response, GreenMail, reader rules. |
| 3 | `testbed/README.md` (Vietnamese) | The reconstructed rig: what works, the exact setup commands and their limits. |
| 4 | `review.md`, reviewer R1 question 1 and the author checklist item "Chạy tối thiểu một tác tử dựa trên LLM..." | What the experiment must answer. |
| 5 | `resolve.md` R08, R14, R16, R19 | Agent protocol decisions: native restart behaviour, nonce, ANR/missingness, K-9 audit. |
| 6 | `codex/resolve-progress.md` rounds 24–30 | What was actually run on the previous machine: AVD boot, APK hashes, native AndroidWorld observation, scripted M3A/T3A BACK wiring, known ANR/focus problems. |

The `codex/` plan describes a 1,090-episode, 5-framework, H100 study. **You are not doing that.** Your scope is the single **A-native** experiment described below, plus a small no-fault development run.

---

## 1. Scope (team-lead decision)

**Experiment E-AGENT (= codex "A-dev" + "A-native", reduced):**
- **Agent:** M3A from the pinned AndroidWorld commit `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, unmodified prompts, history and reflection. Instantiate it through `testbed/androidworld_env.py`. Optional second agent, only if time allows after the main runs: T3A (text-only).
- **App/backend:** K-9 Mail 24.0 + GreenMail 2.1.2 through `testbed/faultproxy.py` (SMTP), in two configs: **no-Sent** and **Sent** folder (IMAP Sent mapping on).
- **Fault:** the commit-then-drop-response fault from campaign 2. The proxy forwards DATA, the server returns 250 (committed), the proxy drops the reply, then the app is force-stopped and relaunched. Only the force-stop subtype is used; do not call it LMK.
- **Agent restart:** the agent process is killed at the fault and restarted with the **same user task and a fresh GUI**. It gets no hint about the truth, and nothing is injected into its memory (`resolve.md` R08).
- **Runs:** 10 no-fault development episodes (A-dev, to debug the wiring; not reported as results), then **20 scheduled interrupted episodes** (10 no-Sent + 10 Sent). The review gate is **≥ 10 valid** interrupted episodes. "Valid" means the backend confirms the original message committed *and* the fault receipt exists.
- **Truth:** only the backend grader (receiver IMAP count + distinct Message-IDs at GreenMail) decides duplicates. The agent and controller never see it.
- **Horizon:** observe for a fixed `H_eval = 300 s` after the agent restarts, then grade.
- **Pre-registered outcome categories** (one per episode, mutually exclusive): `RESENT_DUPLICATE` / `RESENT_BUT_NO_DUP` (should not happen with K-9; investigate if it does) / `DECLARED_DONE_NO_RESEND` / `ASKED_OR_STOPPED` / `TASK_FAILURE` (agent never reached Send, or crashed) / `INVALID` (fault not delivered, barrier timeout, ANR before commit; keep these, but they do not count toward the ≥ 10).
- **Freeze before the 20 scheduled runs:** model, decoding, prompt, AVD image, APK hashes, task text, horizon, outcome rules. Write them in `testbed/agent_study.freeze.json` and commit **before** the first scheduled run. No reruns to change an outcome; only instrumentation failures may be retried, once per episode.

**Model decision (gate G1, by Sat Nov 14):**
1. **Preferred:** `Qwen/Qwen2.5-VL-7B-Instruct` (BF16) served locally with vLLM 0.11.0 through `testbed/serve_model.py` and `testbed/local_model.py`. This needs an NVIDIA GPU with **≥ 24 GB** (A100/H100/RTX 4090/A6000) on Linux. If the lab gives us such a machine by Nov 14, use it.
2. **Fallback:** a hosted multimodal API model that M3A supports upstream (e.g. GPT-4o, or Gemini through the AndroidWorld `infer` wrappers). Estimated cost for 30 episodes is well under USD 50; get budget approval from the team lead first. Put the API key **only** in a git-ignored `.env`. Never commit it and never put it in a receipt.

Whichever you choose, record the exact model ID and version and the decoding parameters in the freeze file. The paper will name the model.

---

## 2. Setup

The previous owner ran everything on **Windows 11 + WHPX** with an x86_64 API 33 AVD. `runtime/` is git-ignored, so you must rebuild it. Linux with KVM also works and is faster. Pick one host and stay on it.

```bash
git clone https://github.com/huypham-cse/P03-ghosteffect.git
cd P03-ghosteffect
git checkout -b c3/testbed
python -m unittest discover -s testbed/tests -v      # host tests; Android/native tests skip until setup is done
python testbed/preflight.py --output testbed/runs/preflight-01.json
```

Then follow `testbed/README.md` "Setup Android/backend". In short:

| Step | Command (from repo root) | Check |
|---|---|---|
| Android SDK, emulator, API 33 r17 image | `python testbed/setup_android.py --bootstrap` | `BOOTSTRAP.json` written, `emulator -accel-check` exit 0 |
| AVD | `python testbed/setup_avd.py --java <path-to-java17> --install --create --verify-apks --output testbed/runs/avd-01` | AVD `ghosteffect_api33_x86_local` exists |
| K-9 APK + GreenMail | `python testbed/setup_assets.py --only com.fsck.k9_39046.apk greenmail.jar` | SHA matches the lock |
| AndroidWorld forwarder | `python testbed/setup_assets.py --lock testbed/agent-assets.lock.json --only 2024.05.13-accessibility_forwarder.apk` | SHA matches |
| Agent sources + Python 3.11.8 venv | Clone the 4 pinned repos into `runtime/vendor/` at the commits in `runtime/agents/SETUP.json` (see `codex/models.md`); create `runtime/agent-venv` with Python **3.11.8**; install AndroidWorld requirements | `python -c "import android_world.agents.m3a"` works in the venv |
| GreenMail smoke | `python testbed/smoke_greenmail.py --output testbed/runs/mail-smoke-01` | PASS |
| Native AndroidWorld observation | `python testbed/smoke_android.py --verification <apk-verification RESULT.json> --only <k9 apk> --native-env-capture --output testbed/runs/native-01` | screenshot + a11y tree, window/input identity match |

There is **no setup script for `runtime/vendor` and the agent venv**. Write one (`testbed/setup_agents.py`) that clones each repo, checks out the pinned commit, verifies a clean tree and records `SETUP.json`. This is task C3-02 and it is useful to the whole team.

Known problems from the previous machine (`codex/resolve-progress.md`): SystemUI ANR dialogs, empty accessibility forests, focus-guard failures and an unstable onboarding tree. **Do not disable the guards to get a PASS.** Keep failed attempts in `testbed/runs/` (git-ignored) and summarise them in your notes. `--gpu host` was what made the scripted wire smoke pass (`native-wire-host-02`).

Never run two smokes or experiments at the same time on one AVD/adb port (5038).

---

## 3. Task list

| ID | Task | Done when |
|---|---|---|
| C3-01 | Host chosen (Windows+WHPX or Linux+KVM); preflight + host tests pass; SDK/AVD/APKs installed with matching hashes. | preflight JSON + smoke receipts summarised in `team/c3-log.md` |
| C3-02 | `testbed/setup_agents.py`: reproducible vendor clone at pinned commits + Python 3.11.8 venv + import check. | Fresh clone → script → `import android_world.agents.m3a` OK |
| C3-03 | **K-9 profiles:** a test account on GreenMail through the SMTP proxy (port reverse via `adb reverse`); configs **no-Sent** and **Sent**; app snapshot/reset recipe (AVD snapshot or `pm clear` + scripted account setup). Reader profile (`reader-profile.example.json` → `k9.local.json`) for Outbox/Sent screens. | Reset → identical start state 3/3 times; proxy journal shows DATA → 250 |
| C3-04 | **Fault wiring with scripted driver first:** reproduce one campaign-2 K-9 trial with `testbed/run_case.py` (`--mode` commit-then-drop, force-stop, relaunch). Confirm the "permanent error in Outbox" state and that the backend has exactly 1 copy. | 3/3 trials reproduce the K-9 failed state; receipts saved |
| C3-05 | **Model gate G1:** serve the chosen model (vLLM or API). Run the scripted-wire smoke, then one real M3A step on the K-9 home screen. | Decision recorded in `team/c3-log.md` **by Nov 14** |
| C3-06 | **Episode harness** `testbed/agent_episode.py`: reset → start M3A with task text → watch for the Send tap (classifier or proxy DATA event) → let the commit happen, drop the response → kill the agent + force-stop K-9 → relaunch K-9 → restart M3A with the same task → run until the agent stops or `H_eval = 300 s` → grade from the backend → write one JSON receipt per episode. The agent stays unmodified. The harness only starts and stops it. | Dry-run on 2 episodes produces complete receipts |
| C3-07 | **A-dev:** 10 no-fault episodes (5 per config). Measure task success, steps, tokens and wall-clock. These are for debugging only; you may change the harness during A-dev. | 10 receipts; task success ≥ 6/10, or escalate to the team lead (the task text may need fixing **before** freeze) |
| C3-08 | **Freeze:** commit `testbed/agent_study.freeze.json` (model, decode, prompt hash, task text, APK/AVD hashes, horizon, outcome rules, seed, episode order). | Merged to `main` before C3-09 starts |
| C3-09 | **A-native:** 20 scheduled interrupted episodes (10 no-Sent, 10 Sent, interleaved order). At most one instrumentation retry per episode; keep every attempt. | ≥ 10 valid episodes. If fewer, run up to 10 more scheduled episodes with the *same* freeze and report all of them |
| C3-10 | **Deliver data** to `artifact/results/real/agent/` (schema §4) + `SUMMARY.md` (protocol, model, host, load, what was not measured). Open a PR, and C2 renders it. | Merged by **Nov 26** |
| C3-11 | **Label cost:** from the fault-injected episodes (and the C3-04 scripted trials), report the wall-clock of one trial broken into reset / compose / fault / relaunch / observation / grading. Give min/median/max. | Numbers in `SUMMARY.md`; C1 uses them in §5.3 |
| C3-12 | (Stretch, only if C3-09 is done by Nov 22) **T3A** on the same 20-episode schedule, or an **independent Element lag check** (20 trials, different day/host) for the review's "independent lag campaign" item. Ask the team lead before starting either. | — |
| C3-13 | Write the protocol paragraph (English, ~150 words) and the limitations list for C1: one agent, one model, emulator only, force-stop only, n small. | Sent to C1 by Nov 27 |

---

## 4. Data schema you deliver (`artifact/results/real/agent/`)

`episodes.csv`, one row per attempt (including invalid and retried ones):

```
episode_id, scheduled_index, config(nosent|sent), attempt(1|2), agent(m3a), model_id, phase(dev|scheduled),
t_issue_utc, t_data_250_utc, t_fault_utc, t_relaunch_utc, t_agent_restart_utc, t_end_utc,
backend_copies_at_horizon, distinct_message_ids, original_committed(0|1), fault_receipt(0|1),
agent_tapped_send_after_restart(0|1), agent_final_status(done|infeasible|asked|error|timeout),
outcome(RESENT_DUPLICATE|RESENT_BUT_NO_DUP|DECLARED_DONE_NO_RESEND|ASKED_OR_STOPPED|TASK_FAILURE|INVALID),
invalid_reason, steps_before_fault, steps_after_restart, prompt_tokens, completion_tokens,
wall_clock_s, reset_s, observation_s, notes
```

Also include:
- `freeze.json`: a copy of the frozen config.
- `receipts/<episode_id>.json`: a trimmed proxy journal, grader output and the agent action list (no screenshots in git; keep them locally and zip them for the artifact later if they are under 50 MB).
- `SUMMARY.md`: protocol, counts table, anything unexpected.

Use **synthetic content only** (made-up recipients on GreenMail, test subjects/bodies). No personal accounts, no real outbound mail.

---

## 5. Timeline

| Week | Dates | Focus | Milestone |
|---|---|---|---|
| W1 | Nov 9–15 | C3-01, C3-02, C3-03, C3-04, C3-05 | **Sat Nov 14:** model gate G1 decided. **Sun Nov 15:** scripted K-9 fault reproduces |
| W2 | Nov 16–22 | C3-06, C3-07, C3-08, start C3-09 | **Thu Nov 19:** freeze committed. **Sun Nov 22:** ≥ 10 scheduled episodes done |
| W3 | Nov 23–29 | Finish C3-09, C3-10, C3-11, C3-13 | **Tue Nov 24:** runs finished. **Thu Nov 26:** data merged |
| W4 | Nov 30–Dec 4 | Help C2 package `testbed/` for the anonymized artifact. Answer C1's questions. No new runs after **Dec 1** | — |

**Escalate immediately (team chat, not at the weekly sync) if:** the emulator cannot boot or stay stable by Nov 13; no model is available by Nov 14; A-dev task success is below 6/10 on Nov 19; fewer than 10 valid episodes by Nov 23. The fallback plan is decided by the team lead. Options include T3A instead of M3A, a simpler task text (fixed before freeze), or reporting fewer valid episodes honestly.

---

## 6. Rules

- **Branch** `c3/testbed`; PRs to `main` titled `[C3-xx]`.
- **You own:** `testbed/**`, `artifact/results/real/agent/**`, `team/c3-log.md`. Do not edit `manuscript/` or other `artifact/` files.
- **Never commit:** `runtime/`, `testbed/runs/`, `*.local.json`, `.env`, API keys, screenshots of anything personal. Check `git status` before every commit.
- **Do not modify upstream agent code** (prompts, history, parser, action space). If a binding fix is needed, it goes in `testbed/` with a comment and a test.
- **Outcome honesty:** if M3A never re-sends, that *is* the result. It changes the paper's framing (C1 handles that). Do not change the task text or the model after the freeze to get re-sends.
- Weekly sync Sunday evening. Keep `team/c3-log.md` as a dated daily log (what ran, what failed, receipt paths).

---

## 7. Tracker

Status: `todo` / `doing` / `review` / `done` / `blocked(<reason>)`.

| ID | Short name | Due | Status | Notes / PR |
|---|---|---|---|---|
| C3-01 | Host + SDK/AVD/APKs | Nov 12 | todo | |
| C3-02 | setup_agents.py | Nov 13 | todo | |
| C3-03 | K-9 profiles + reset | Nov 14 | todo | |
| C3-04 | Scripted K-9 fault reproduces | Nov 15 | todo | |
| C3-05 | Model gate G1 | Nov 14 | todo | Qwen local / API fallback |
| C3-06 | Episode harness | Nov 18 | todo | |
| C3-07 | A-dev 10 no-fault | Nov 19 | todo | |
| C3-08 | Freeze file merged | Nov 19 | todo | |
| C3-09 | A-native 20 scheduled (≥ 10 valid) | Nov 24 | todo | |
| C3-10 | Data + SUMMARY merged | Nov 26 | todo | |
| C3-11 | Label wall-clock cost | Nov 26 | todo | |
| C3-12 | Stretch: T3A or Element lag | Nov 28 | todo | ask lead first |
| C3-13 | Protocol paragraph + limitations for C1 | Nov 27 | todo | |
