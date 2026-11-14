# GhostEffect testbed

Android emulator testbed for the paper's emulator measurements and its LLM-agent experiment. Real Android apps
talk to self-hosted test servers through a fault proxy that lets a request commit on the server and then drops
the reply. Ground truth (how many copies the server holds) comes from the servers only; the GUI reader and the
agent never see it.

This is a reconstruction of the original rig from the paper's description and campaign logs; it does not carry
the original rig's hashes. All content is synthetic and all accounts are test accounts on loopback servers.

## What is not in the package

- `runtime/`: SDK, emulator, AVD, APKs, model weights and virtual environments. The setup scripts below create it.
- `runs/`: receipts written by every run (`RESULT.json`, journals, screenshots).
- Local secrets: `.env` and `*.local.json` files.

## Requirements

- Windows 11 x86_64 with WHPX, or Linux with KVM. 8 CPU threads and 32 GB RAM were used.
- Python 3.11 or newer for the stdlib tools; the agent environment is pinned to Python 3.11.8 through `uv`.
- Java 17 or newer for GreenMail.
- For the LLM agent: one NVIDIA GPU running vLLM 0.11.0 (`serve_model.py`; profiles for A10G 24 GB, L40S 48 GB and
  H100 80 GB differ only in memory settings), reached through an SSH tunnel so the endpoint stays on loopback. No
  paid model API is used.

## Quick checks without a device

```bash
python -m unittest discover -s testbed/tests -v
python testbed/setup_assets.py --only greenmail.jar
python testbed/smoke_greenmail.py --output testbed/runs/mail-smoke-01
```

## Android setup

```bash
python testbed/setup_android.py --bootstrap
python testbed/setup_avd.py --java <path-to-java> --install --create --verify-apks --output testbed/runs/avd-01
python testbed/setup_assets.py --only com.fsck.k9_39046.apk
python testbed/smoke_android.py --verification testbed/runs/avd-01/RESULT.json --only com.fsck.k9_39046.apk --native-env-capture --gpu host --output testbed/runs/native-01
```

Only `-gpu host` was stable; the software renderer produced ANR dialogs. Right after a cold boot the AndroidWorld
accessibility forwarder sometimes returns no tree; wait a few minutes before the first episode. Do not restore
AVD snapshots with `-gpu host`: restored processes drew no text and the guest clock was off by 80 s.

## K-9 Mail profiles and reset

Two test accounts on GreenMail: `alice@test.invalid` sends, `bob@test.invalid` receives. K-9 Mail 24.0 uses IMAP
`127.0.0.1:3143` and SMTP `127.0.0.1:14025` (the fault proxy), reached from the AVD with `adb reverse`. Two clean
copies of K-9's data directory are kept on the AVD under `/data/local/tmp/ghosteffect/`: `k9-sent.tar` (Sent
folder assigned manually) and `k9-nosent.tar` (made from it by removing the Sent folder and its assignment).
Without a Sent folder, K-9 24.0 asks "Sent folder not found" on every send and sends only after "Send and Delete".

```bash
python testbed/k9_reset.py --config nosent --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/reset-01
python testbed/k9_fault_case.py --config sent --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/fault-01
```

`k9_reset.py` disables the AndroidWorld accessibility forwarder (its crash dialog otherwise covers K-9), restores
the clean copy, relabels it for SELinux, restarts GreenMail empty and checks nine conditions, including that K-9
holds the focus. `k9_fault_case.py` runs its own SMTP fault proxy and control server on ports 14025 and 19025,
so no other proxy may listen there; it drops the SMTP reply after GreenMail returned 250, waits until K-9 records
the error, force-stops and relaunches K-9, then grades from the server. With `--action` (`sync`, `send_messages`,
`none`, `recompose`) it also performs one user action, with a UI receipt per tap, and counts what reaches the
server in `--action-window` seconds; `k9_audit_table.py` collects those receipts into a CSV. A failed trial writes
`RESULT.json` with verdict `INVALID`. To send mail by hand through the proxy, run `faultproxy.py` yourself
(`--protocol smtp --upstream smtp://127.0.0.1:3025 --listen-port 14025 --control-port 19025`) and stop it before
running these scripts.

## LLM-agent episodes

```bash
python testbed/setup_agents.py --output testbed/runs/agents-01
bash testbed/server_gpu.sh setup && bash testbed/server_gpu.sh serve      # on the GPU server
runtime/agent-venv/Scripts/python.exe testbed/agent_episode.py --framework m3a --config sent --fault drop-forcestop --phase scheduled --episode-id s01 --scheduled-index 1 --goal-file testbed/agent_goal.txt --tag gx:ABC123 --serving-receipt testbed/runs/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/s01
```

The study itself: `run_agent_study.py --phase dev` (A-dev), `make_freeze.py` (writes
`agent_study.freeze.json`: model, decoding, native source hashes, task, app hashes, outcome rule and the episode
order with its tags), `run_agent_study.py --phase scheduled` (follows the committed freeze), then
`collect_agent.py`, `check_agent_data.py` and `artifact/scripts/render.py` (`render_agent.py` writes the `\Agent*`
and `\LabelTrial*` macros). `fake_model.py` is a synthetic stand-in for the vLLM endpoint that rehearses the whole
path on the AVD without a GPU; its receipts are marked synthetic and are never study data.

`agent_episode.py` runs one episode: reset, native M3A from the pinned AndroidWorld commit, the agent blocked as
soon as the server committed the mail, the reply dropped, K-9 force-stopped and relaunched, a fresh M3A on the same
task, and grading at relaunch plus `H_eval` (300 s) from distinct Message-IDs on the server. Its `RESULT.json`
holds one row of `episodes.csv`. `--framework scripted-stop` and `scripted-redo` are synthetic tap fixtures for
dry runs without a model and are never study data. The SMTP proxy runs inside the harness on port 14025, so do not
run a separate proxy at the same time.

## Files

| File | Role |
|---|---|
| `faultproxy.py` | SMTP, Matrix and CalDAV fault proxy: pass, reject, drop, sticky, withhold; fsynced journal |
| `grader.py` | Server-side copy counts; used by the injector and grader only, never by an agent |
| `run_case.py` | Scripted trial with a post-accept, pre-ACK barrier and an optional app fault |
| `k9_reset.py`, `k9_fault_case.py`, `k9_audit_table.py` | K-9 reset, scripted lost-reply case, action audit table |
| `agent_episode.py` | LLM-agent fault-injection episode and outcome rule |
| `native_episode.py`, `androidworld_env.py`, `local_model.py` | Pinned AndroidWorld env, M3A/T3A factory, loopback vLLM binding |
| `serve_model.py`, `setup_models.py`, `server_gpu.sh` | Model download and serving on the GPU server |
| `run_agent_study.py`, `make_freeze.py`, `collect_agent.py`, `check_agent_data.py` | A-dev and A-native runs, freeze, data and its checks |
| `fake_model.py` | Synthetic vLLM stand-in for rehearsing the agent path without a GPU |
| `capture_androidworld.py`, `smoke_android.py`, `smoke_agent_wire.py` | AVD and agent wiring smoke tests |
| `smoke_greenmail.py`, `smoke_http_backends.py` | Backend plus proxy smoke tests without Android |
| `setup_android.py`, `setup_avd.py`, `setup_assets.py`, `setup_backends.py`, `setup_agents.py` | Pinned setup |
| `ui.py`, `app_driver.py`, `observer.py`, `probes.py`, `classifier.py` | GUI-only readers and evidence families |
| `controller.py`, `recovery.py`, `calibration.py` | Host-side ledger boundary, Algorithm 1 runtime, calibration compiler |
| `preflight.py` | Read-only readiness inventory |
| `*.lock.json`, `requirements-backends.txt` | Pinned assets, models and backend versions with SHA256 |

## Rules kept by the code

- Only the grader reads server state or app databases; readers and agents see the GUI only.
- Every receipt is written, including invalid runs; nothing retries a failed measurement silently.
- The agent code is the pinned upstream AndroidWorld, unchanged; prompts, history and reflection are not edited.
