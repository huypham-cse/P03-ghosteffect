# GhostEffect (P03): real Android-emulator measurements (2026-11-06)

All results below come from a real Android 13 emulator, real F-Droid app builds, and self-hosted backends running
natively on the host. No LLM and no paid API were used: the "agent" is a scripted UI driver. Ground truth always comes
from the **backend** (the server-side copy count). Tables are generated from the CSVs in this folder
(`shared-android/scripts/analyze_p03.py`, then `render_summary.py` with `shared-android/templates/p03_summary.tpl`).
How to rebuild the rig: `papers/shared-android/README.md`.

## Setup
* Device: AVD `GhostAvd` (Pixel 6, `android-33;google_apis;arm64-v8a` r17, 3 GB, persistent) on emulator 37.2.13,
  console 5570. K-9 ran on a second fresh AVD `MailAvd` (same image, console 5580). The host was heavily loaded
  (load average 16–38 on 18 cores, shared with other agents' VMs), so every UI timing is upper-biased.
* Apps (F-Droid, sha256 in `shared-android/apks/SHA256SUMS`): **Element Classic 1.6.62** (`im.vector.app_40106622`,
  arm64) and **K-9 Mail 24.0** (`com.fsck.k9_39046`).
* Backends (host, reached from the emulator at 10.0.2.2), not in Docker. Colima was left untouched.
  * Matrix: **Synapse 1.164.2** (SQLite, `server_name ghost.local`) on :8018. A fault proxy listens on :8008, and
    Element's homeserver URL is `http://10.0.2.2:8008`. The users are `alice` (device) and `bob` (observer). The room
    `#ghostroom` is unencrypted, so the server-side body is the ground truth, read by bob through `/messages`.
  * Mail: **GreenMail standalone 2.1.2**: SMTP :3025 behind the fault proxy on :3026, IMAP :3143. Ground truth = IMAP
    `SEARCH SUBJECT <nonce>` in bob's INBOX.
* **Fault proxy** (`scripts/faultproxy.py`): in `arm` mode it forwards the matching request, so the server **commits**,
  then discards the server's reply and resets the client connection. This is the "response lost after commit" case
  that decides G2. For Matrix it matches `PUT …/send/m.room.message/<txnId>`, for SMTP the end-of-DATA `\r\n.\r\n`.
  Every send request, with its txnId, is logged.
* **Faults** (as instructed): `bg_kill` = HOME (background the app), then `am kill <pkg>`; if the pid is still alive,
  `kill -9 <pid>`. `force_stop` = `am force-stop` (cancels WorkManager/alarms). `net_pre` = `svc wifi disable; svc
  data disable` **before** the send, then the fault while offline, then the network is restored. `fg_kill9` =
  SIGKILL of the foreground process 300 ms after tapping Send (no proxy). `acked` = the fault is applied only after
  the server has the copy. After every fault the app is brought back to the foreground (launcher intent), as an agent
  would do when it resumes.
* **Timings**: `net_pre` (request never left), `respdrop` (server committed, client saw a reset), `acked` (server
  committed, client got the 200), `inflight_fg_kill9` (kill races the request).
* Nonce = a unique token in the message body / mail subject (`gx<time>k<trial>`, `mx…`).
* UI reads use **uiautomator dumps** (`scripts/ui.py`). Each read took about 1–4 s on the loaded host, which sets the
  time resolution of the lag numbers. AndroidWorld's a11y forwarder was tried first. It was **observed to return a
  stale tree** (a room timeline from minutes earlier while the screen showed the room list) after the network toggles
  on this AVD. Those runs were discarded (`shared-android/logs/test/e4_run*`).
* Observation window after relaunch: 45 s. K-9 then gets one benign user-level action ("Sync account" in the drawer)
  and 20 s more.

## E4 — hop-2 behaviour (outcome per app × fault × timing)
`requests_ge2` = trials in which the client sent the effect request at least twice.
`retries_same_idempotency_key` = how many of those used a single idempotency key (the Matrix txnId) for all copies.

| app | fault | timing | n | exactly_once | duplicate | lost | requests_ge2 | retries_same_idempotency_key | failed_state_shown | pending_at_end | eventual_exactly_once | eventual_duplicate | eventual_lost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| element | bg_kill | acked | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| element | bg_kill | net_pre | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| element | bg_kill | respdrop | 5 | 5 | 0 | 0 | 5 | 5 | 0 | 0 | 5 | 0 | 0 |
| element | fg_kill9 | inflight_fg_kill9 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| element | force_stop | net_pre | 6 | 5 | 0 | 1 | 0 | 0 | 0 | 0 | 6 | 0 | 0 |
| element | force_stop | respdrop | 4 | 4 | 0 | 0 | 4 | 4 | 0 | 0 | 4 | 0 | 0 |
| element | none | net_pre | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| element | none | respdrop | 5 | 5 | 0 | 0 | 5 | 5 | 0 | 0 | 5 | 0 | 0 |
| k9 | bg_kill | acked | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| k9 | bg_kill | net_pre | 5 | 1 | 0 | 4 | 0 | 0 | 0 | 4 | 5 | 0 | 0 |
| k9 | bg_kill | respdrop | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 5 | 0 | 0 |
| k9 | force_stop | net_pre | 5 | 1 | 0 | 4 | 0 | 0 | 0 | 4 | 5 | 0 | 0 |
| k9 | force_stop | respdrop | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 5 | 0 | 0 |
| k9 | none | net_pre | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 5 | 0 | 0 |
| k9 | none | respdrop | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 5 | 0 | 0 |

K-9: copies at the end of the 45 s window, then after the benign "Sync account" (+20 s), and SMTP DATA attempts seen
by the proxy:

| app | fault | timing | n | copies_at_window_end_to_after_sync | smtp_DATA_attempts | still_in_outbox_after_sync | failure_notification |
|---|---|---|---|---|---|---|---|
| k9 | bg_kill | acked | 5 | 1->1: 5 | 1|1|1|1|1 | 0 | 5 |
| k9 | bg_kill | net_pre | 5 | 0->1: 4; 1->1: 1 | 1|1|1|1|1 | 0 | 5 |
| k9 | bg_kill | respdrop | 5 | 1->1: 5 | 1|1|1|1|1 | 0 | 5 |
| k9 | force_stop | net_pre | 5 | 0->1: 4; 1->1: 1 | 1|1|1|1|1 | 0 | 1 |
| k9 | force_stop | respdrop | 5 | 1->1: 5 | 1|1|1|1|1 | 0 | 0 |
| k9 | none | net_pre | 5 | 0->1: 5 | 1|1|1|1|1 | 0 | 5 |
| k9 | none | respdrop | 5 | 1->1: 5 | 1|1|1|1|1 | 0 | 5 |

Whether `am kill` worked after backgrounding, or the harness had to fall back to `kill -9`:

| app | kill_method | n |
|---|---|---|
| element | am_kill_noop+kill9 | 13 |
| element | fg_kill9 | 5 |
| element | force_stop | 10 |
| k9 | am_kill | 15 |
| k9 | force_stop | 10 |

## E5 — visibility lag and evidence families
Effect-visibility lag after the app is relaunched: seconds from the launcher intent until the nonce message is
present in the a11y tree (`visible`), and until its send-state icon reads "Sent" (`sent_state`). Resolution is one
uiautomator read, about 1–4 s.

| app | timing | measure | n_observed | n_not_within_window | p50 | p90 | max |
|---|---|---|---|---|---|---|---|
| element | acked | visible | 4 | 0 | 8.29 | 9.82 | 10.42 |
| element | inflight_fg_kill9 | visible | 5 | 0 | 8.73 | 11.3 | 12.78 |
| element | net_pre | visible | 12 | 2 | 6.72 | 11.71 | 12.6 |
| element | respdrop | visible | 12 | 2 | 5.87 | 13.92 | 14.55 |
| element | acked | sent_state | 4 | 0 | 8.29 | 9.82 | 10.42 |
| element | inflight_fg_kill9 | sent_state | 5 | 0 | 8.73 | 11.3 | 12.78 |
| element | net_pre | sent_state | 12 | 2 | 6.72 | 11.71 | 12.6 |
| element | respdrop | sent_state | 12 | 2 | 5.87 | 13.92 | 14.55 |

Evidence families, read from the UI only and scored against backend truth (committed = at least 1 server copy).
Element: (a) the send-state indicator (`messageSendStateImageView` content-desc: Sent / Sending), (b) the nonce text
present in the timeline (`b_copycount` = the number of visible copies equals the number of server copies), (c) the
room-list last-message digest. K-9: (a) the nonce listed in the Outbox folder (taken as "not committed"), (b) a
failure notification in the shade. "early" = the first read after relaunch, "late" = the end of the window.
`cofail:` rows count trials in which two families were wrong together (`ci95_lo`/`ci95_hi` hold the marginal error
counts in those rows).

| app | family | n | errors | error_rate | ci95_lo | ci95_hi |
|---|---|---|---|---|---|---|
| element | a_indicator_early | 33 | 0 | 0.0 | 0 | 0.104 |
| element | a_indicator_late | 37 | 5 | 0.135 | 0.059 | 0.28 |
| element | b_copycount_late | 37 | 5 | 0.135 | 0.059 | 0.28 |
| element | b_nonce_early | 33 | 0 | 0.0 | 0 | 0.104 |
| element | b_nonce_late | 37 | 5 | 0.135 | 0.059 | 0.28 |
| element | c_listdigest_late | 37 | 1 | 0.027 | 0.005 | 0.138 |
| element | cofail:a_indicator_late&b_nonce_late | 37 | 5 | 0.135 | marg_i=5 | marg_j=5 |
| element | cofail:a_indicator_late&c_listdigest_late | 37 | 1 | 0.027 | marg_i=5 | marg_j=1 |
| element | cofail:b_nonce_late&c_listdigest_late | 37 | 1 | 0.027 | marg_i=5 | marg_j=1 |
| element | cofail:all_late_families | 37 | 1 | 0.027 |  |  |
| k9 | a_outbox_early | 35 | 17 | 0.486 | 0.33 | 0.644 |
| k9 | a_outbox_late | 35 | 15 | 0.429 | 0.28 | 0.591 |
| k9 | b_notification_late | 35 | 21 | 0.6 | 0.436 | 0.744 |
| k9 | cofail:a_outbox_late&b_notification_late | 35 | 10 | 0.286 | marg_i=15 | marg_j=21 |
| k9 | cofail:all_late_families | 35 | 10 | 0.286 |  |  |

Per-trial family errors: `e5_per_trial_family_errors.csv`.

## SQLite WAL ledger under power-loss-like kill (`ledger_powerloss.csv`)
`scripts/ledger_powerloss.py`. On GhostAvd (root), `sqlite3` 3.32.2 appends ISSUED rows in WAL mode, one transaction
per row, and prints `ACK i` after each COMMIT returns. The host SIGKILLs the emulator's qemu process mid-stream, so
the guest page cache is lost and the guest never shuts down. Then the host cold-boots and runs `PRAGMA
integrity_check` and `max(seq)`. A write-ahead violation is an acknowledged row that is missing after boot. Note:
qemu's writes that already reached the host page cache survive a qemu SIGKILL, so this approximates guest power loss,
not host power loss.

| synchronous | n | integrity_ok | write_ahead_violations | acked_minus_persisted | median_boot_s |
|---|---|---|---|---|---|
| FULL | 3 | 3 | 0 | 0|0|0 | 20.3 |
| NORMAL | 3 | 3 | 0 | 0|0|0 | 18.2 |
| OFF | 3 | 3 | 3 | 61|15|158 | 18.4 |

## Parameter table (measured; for the paper's free parameters)
| Parameter (paper) | Element 1.6.62 + Synapse | K-9 24.0 + GreenMail (SMTP) | Source |
|---|---|---|---|
| Hop-2 retry-until-ack after response loss (G2) | **Yes.** In all 14 `respdrop` trials the client re-sent `PUT …/send/<txnId>` with the **same txnId** (2 requests, 1 txnId), and Synapse deduplicated: exactly one copy, including when the app was killed (`bg_kill`, 5 trials) or force-stopped (4 trials) right after the drop. | **No retry.** In all 15 `respdrop` trials there was exactly 1 DATA attempt, and the message stayed in the Outbox flagged as failed. "Sync account" and an explicit Outbox → "Send messages" (manual check after the runs) made **no** new SMTP connection. No duplicates arose, but the UI kept saying "not sent" for a committed effect. | `e4_outcomes.csv`, `e4_k9_after_sync.csv`, proxy logs |
| Pending effect after kill/force-stop while offline (`net_pre`) | Delivered after relaunch in every trial by the end of the analysis (eventual exactly-once 14/14). One force-stop trial was not yet delivered at the end of the 45 s window. | Not delivered within 45 s after relaunch and network restore in 13/15 trials. Delivered (exactly once) after the benign "Sync account" in all of them. Retry needs a trigger: a sync, or the 15-min poll. | `e4_outcomes.csv` (`eventual_*`), `e4_k9_after_sync.csv` |
| Marks item "failed" instead of retrying | Never observed (the state goes Sending → Sent). | Yes: "Failed to send some messages / Unable to send message" notification, and the message stays in the Outbox (`respdrop`). | `late_banner`, `shade_text` |
| force-stop breaks G2 (H3) | Not observed when the app is relaunched: force-stop during `net_pre` or `respdrop` gave exactly one copy in 10/10 trials eventually (9/10 within the 45 s window). Element's queue is persisted and re-sent on the next start. | Force-stop is no different from bg_kill: in both cases delivery waits for a sync. | `e4_outcomes.csv` |
| Effect-visibility lag after relaunch (UI) | Time to the nonce being visible with state "Sent": p50 8.5 s, max 14.6 s over 24 trials with a real process restart. The harness floor (relaunch with no kill) is 4.2–6.3 s (n = 9), so the app-attributable lag is roughly 2–10 s. See `e4_visibility_lag.csv`. | n/a (no Sent folder; the effect is not visible in K-9's UI) | `e4_visibility_lag.csv` |
| Evidence family (a): pending/outbox indicator | Early read 0/33 wrong. Late read 5/37 wrong. | Outbox membership: 17/35 wrong early (15 `respdrop` + 2 `net_pre` already delivered), 15/35 late (all 15 `respdrop`: listed as pending although committed). | `e5_evidence_families.csv` |
| Evidence family (b): nonce in UI text | Early 0/33, late 5/37 wrong. In all 5 the timeline was not on screen, or the nonce row left the tree, while the server had the copy. | Failure notification: 21/35 wrong (10 `respdrop`, 6 `net_pre`, 5 `acked`). The notification persists across trials, i.e. a stale cache. | same |
| Evidence family (c): list digest | Room-list last-message snippet: 1/37 wrong. | not available | same |
| Co-failure | (a) and (b) failed together in **5/5** of their errors, because both are read from the same timeline view. (c) failed with them in 1. | Outbox and notification failed together in 10/35. | same |
| `am kill` after HOME | No-op for Element in 13/13 (the process survived, so `kill -9` was needed). Android sometimes re-spawned Element in the background. | Killed K-9 in 15/15 | `e4_kill_methods.csv` |
| Nonce-capable benign field | Message body (visible; this is what the experiment used) | Subject/body (visible) | design |
| `accessibilityDataSensitive` | Not applicable on API 33: the flag exists from API 34, and nothing was hidden from uiautomator in these apps. The dex of all three apps references `setAccessibilityDataSensitive` (androidx wrapper), so it may matter on API 34+ devices. | same | static scan |
| SQLite WAL ledger, power-loss-like kill | `synchronous=FULL` and `NORMAL`: 0 acknowledged-but-lost rows in 3+3 trials, `integrity_check` ok. `OFF`: lost 61, 15 and 158 acknowledged rows (3/3 trials), integrity still ok. Each transaction ran in its own `sqlite3` process, so NORMAL also synced at close. Do not generalise NORMAL to a long-lived connection. | | `ledger_powerloss*.csv` |

## Failures and caveats
* **Small n.** Element: 37 trials (4 of them from a pilot run with the same method and a 40 s window, `e4_element_pilot_trials.csv`), K-9: 35. Two to six per cell. These are behaviour characterisations, not
  rate estimates; CIs are in the CSVs.
* **Discarded runs** (kept in `shared-android/logs/test/` for audit, not analysed): (i) runs whose UI reads came from
  the stale AndroidWorld forwarder; (ii) 4 Element `bg_kill` trials in which the harness did not relaunch the app,
  because Android had already re-spawned the process in the background. In 2 of these, a message queued while offline
  was not sent within 45 s while the app stayed in the background. That is n=2 and it is reported only here.
  (iii) A gRPC fork deadlock hung one run.
* **GhostAvd crashed once** (qemu exited around 03:56 during Element part C), so the `fg_kill9` cells of part C were
  lost. They were re-run in part D after the ledger test had re-booted the AVD.
* **Not done:** CalDAV (Radicale + Tasks.org: the "Sign in" button produced no request in 4 attempts; DAVx5/Etar not
  tried), Doze, LMK under real memory pressure, VLM-based reads (excluded by the no-LLM rule), and commit-classifier
  recall.
* The lag numbers include app cold start **and** harness navigation through slow uiautomator reads on an overloaded
  host. They are upper bounds on app behaviour.
* The `respdrop` fault reaches the app as a TCP reset after the server committed. A real network loss after commit can
  also surface as a timeout, which may trigger different client code paths.


## Campaign 2 (2026-11-06, 05:45–08:10 +07): screen-validated re-measurement, K-9 corrections, Synapse txnId horizon, CalDAV

Everything in this section comes from campaign-2 runs (folder `campaign2/`). Same rig, apps, backends and fault proxy as above
(`papers/shared-android/README.md`). No LLM and no paid API were used. The scripts are `shared-android/scripts/c2_element.py`,
`c2_k9.py`, `c2_caldav.py`, `c2_synapse_txn.py`, and the aggregation `analyze_c2.py`. Logs are in `campaign2/logs/`.

### Setup differences from campaign 1
* Emulators ran with `-cores 2`: GhostAvd (console 5570, Element), MailAvd (5580, K-9) and a third, read-only
  `AndroidWorldAvd` instance (5590, DAVx5 + Etar; nothing persisted). The host load average was 3–11 on 18 cores, lower than
  in campaign 1. Fresh backend processes: Synapse 1.164.2 (same SQLite DB), GreenMail 2.1.2 (in-memory, so empty at start),
  Radicale 3.9.0, plus the fault proxies (`shared-android/logs/c2/proxy_*.log`).
* **Screen-validating reader (Element).** Each poll is one uiautomator dump. It returns:
  * **⊥ `wrong_screen`** unless the foreground package is `im.vector.app`, `roomToolbarTitleView` == `ghostroom` and
    `timelineRecyclerView` is present. The observer then navigates back to the room, as an agent would.
  * **`present`** if a `messageTextView` contains the nonce. If the row is not found and `jumpToBottomView` is shown,
    the reader taps it and re-dumps once. The hop-1 indicator is the `messageSendStateImageView` content-desc on that row.
  * **`absent`** only on a verified screen that is scrolled to the bottom and shows the *anchor* row (the newest server
    message before the trial) with no nonce row.
  * **⊥ `row_not_found`** otherwise: timeline empty, anchor not visible, or not at the bottom.

  The room-list digest has its own screen check (`All Chats` + the `ghostroom` row). Per-poll records
  `[t_start, t_end, screen_ok, row_found, verdict, reason, indicator, copies, pkg|title]` are in the `polls` column.
* **Observation window:** the observer polls until 20 s after the first "Sent" read. If there is no "Sent" read, it
  polls for 120 s and then extends to 300 s, so a lag up to 300 s would have been observed rather than censored. Lags are
  interval data, `(lo, hi]`, where `hi` is the end of the first dump that saw the row. The resolution is one dump, about
  2 s.
* **Faults (Element):** `bg_kill9` = HOME, then `kill -9 <pid>`, then relaunch. `force_stop` = `am force-stop`, then
  relaunch. `netcut` = `svc wifi/data disable` for 20 s with the app left in the foreground, then restore. Every interrupted
  cell is `respdrop`: the proxy forwards `PUT …/send`, Synapse commits, the reply is dropped and the client gets a RST.
  `nofault` = an uninterrupted send (t0 = the Send tap). `bg_kill9/acked` = restart with no pending effect.
  `*_sticky` = the proxy keeps dropping the replies to Element's immediate retries until the process is killed, so the
  fault lands before any ack reaches the app (v2 uses the proxy's `armsticky` mode). `hold` = the reply is withheld with
  no RST, so the client sees a timeout (C2-1c).

### C2-1. Element re-measured with the screen-validating reader (`c2_element_trials.csv`, 101 trials)
**Recorded trials.** 101 trials in all:
* 12 `nofault`;
* 20 each of `bg_kill9`, `force_stop` and `netcut` (all `respdrop`);
* 23 sticky (`bg_kill9_sticky` 10+2, `force_stop_sticky` 10+1). Trials 300–302 are "v1", which re-armed from a harness
  thread; in 300–301 Element's retry escaped the drop, so they are reported separately. v2 uses the proxy's
  `armsticky` mode;
* 6 `bg_kill9/acked`.

That makes **83 committed response-loss trials**: 60 standard plus 23 sticky.

**Not recorded.** Trials 11–16 failed at trial start ("room not opened"). A system ANR dialog for AndroidWorld's
`accessibility_forwarder` (installed on GhostAvd, unused here) covered the screen, as the retry diagnostics later showed.
Trial 17 was killed mid-trial by the operator while the harness was being patched. Pilot trials (3) are in
`pilot_element.csv` and are not analysed.

**Outcomes.** 101/101 exactly-once: no duplicate and no loss. Every `respdrop` trial sent ≥2 `PUT …/send` with a single
txnId (83/83). How the committed send became acknowledged inside the app (`ack_mechanism` in
`c2_element_first_visible.csv`):

| cell | n | t0 | row/indicator lag p50 (s) | p90 | max | not visible by 45 s | censored | ack path: retry acked before fault / same-txnId re-send after relaunch / no re-send (sync echo) |
|---|---|---|---|---|---|---|---|---|
| none/nofault | 12 | Send tap | 2.51 | 2.87 | 3.78 | 0 | 0 | – |
| bg_kill9/respdrop | 20 | relaunch intent | 4.04 | 7.98 | 13.56 | 0 | 0 | 20 / 0 / 0 |
| force_stop/respdrop | 20 | relaunch intent | 11.95 | 12.28 | 12.69 | 0 | 0 | 20 / 0 / 0 |
| netcut/respdrop | 20 | network restore | 2.39 | 2.69 | 2.94 | 0 | 0 | 20 / 0 / 0 |
| bg_kill9_sticky/respdrop (v2) | 10 | relaunch intent | 4.12 | 4.41 | 4.58 | 0 | 0 | 0 / 0 / 10 |
| force_stop_sticky/respdrop (v2) | 10 | relaunch intent | 11.05 | 12.32 | 12.44 | 0 | 0 | 0 / 2 / 8 |
| bg_kill9_sticky_v1 / force_stop_sticky_v1 | 2 / 1 | relaunch intent | 4.01 / 11.47 | – | 4.28 / 11.47 | 0 | 0 | 2/0/0 and 0/1/0 |
| bg_kill9/acked (restart floor) | 6 | relaunch intent | 3.59 | 3.87 | 3.90 | 0 | 0 | – |
| **all respdrop** | **83** | – | **4.30** | **12.18** | **13.56** | **0** | **0** | **62 / 3 / 18** |

**Reading the table.**
* Lags are the upper ends `hi` of the interval `(lo, hi]` (end of the first dump that saw the row). The lower end is the
  previous negative or ⊥ read, which was 0 in almost every trial. The resolution is one dump, ≈2–2.5 s: the `nofault`
  row (2.5 s) is the reader floor.
* **Censoring: 0/101.** No trial needed more than 13.6 s. The observer would have kept polling to 120 s (300 s if
  still unseen) but never had to. **None of the 83 committed response-loss trials was invisible at 45 s.** Campaign 1's
  "not visible within 45 s" trials therefore do not reproduce under a screen-validating reader (see C2-1b).
* **Lag by fault class.**
  * `force_stop` is navigation-dominated. After `am force-stop` the relaunch lands on the room list (or the splash) in
    20/20 + 10/10 + 1/1 trials, so the first read is ⊥ `wrong_screen`. The reader navigates back and finds the row
    already "Sent" at ≈11–12.7 s.
  * `bg_kill9`: Android restores the room activity, giving 4.0 s p50. The 13.6 s maximum comes from the three lag-blind
    trials described below.
  * `netcut`: the app stayed in the foreground and the row was already Sent at the first read after restore.
* **Hop-1 indicator = row.** The send-state indicator (`messageSendStateImageView`, Element's hop-1 view) first
  appeared **in the same dump as the row in 101/101 trials**. It read "Sent" on all 1,036 polls that saw the row: "Sending"
  was never observed after a restart. On Element the indicator therefore carries no information beyond the row. It is
  drawn by the same lagged timeline, so it is **not a lag-free hop-1 view**. Per-trial first-visible intervals for the row
  and the indicator are in `c2_element_first_visible.csv` (one row per trial).
* **Mechanism (new).**
  * In all 60 standard response-loss trials, Element re-sent the same txnId **≈20–100 ms after the RST**, and that retry's
    200 reached the app **before** the fault. So the standard cells (and campaign 1's) test "retry then kill", not
    "kill before any ack".
  * The sticky cells drop every reply until the kill. There, after relaunch, Element re-sent the same txnId in 3/23
    trials (Synapse deduplicated it).
  * In 18/23 it sent **no further PUT at all** and still showed the message as "Sent", exactly once. It reconciled the
    local echo with the server event that `/sync` returned with `unsigned.transaction_id` (delivered only to the sending
    device).
  * Both recovery paths rest on the device-scoped txnId; see C2-3 for its horizon.
* In 3 `bg_kill9_sticky` trials Android had already re-spawned Element before the relaunch (`restarted=0`).

**Reader verdicts.** Of 1,076 polls, 36 were ⊥ `wrong_screen` (31 of them the first read after a force-stop), 1 was ⊥
`timeline_empty`, 3 were verified `absent` and 1,036 were `present`.

**Per-family error, with ⊥ kept separate** (truth = committed, server copies ≥ 1; all 101 trials were committed;
`c2_element_families.csv`, per trial in `c2_element_per_trial_families.csv`):

| family / read | n | ⊥ (no observation) | observed | wrong | wrong rate among observed [95% CI] |
|---|---|---|---|---|---|
| (a) hop-1 indicator, first read | 101 | 33 | 68 | 3 | 0.044 [0.015, 0.122] |
| (a) hop-1 indicator, first non-⊥ read | 101 | 0 | 101 | 3 | 0.030 [0.010, 0.084] |
| (a) hop-1 indicator, late read | 101 | 2 | 99 | 0 | 0.000 [0, 0.037] |
| (b) nonce row, first read | 101 | 33 | 68 | 3 | 0.044 [0.015, 0.122] |
| (b) nonce row, first non-⊥ read | 101 | 0 | 101 | 3 | 0.030 [0.010, 0.084] |
| (b) nonce row, late read | 101 | 2 | 99 | 0 | 0.000 [0, 0.037] |
| (c) room-list digest, late | 101 | 2 | 99 | 0 | 0.000 [0, 0.037] |

* **The 3 wrong readings are genuine lag-blind reads, not reader failures.** In trials 122, 132 and 161 (all
  `bg_kill9/respdrop`) the first read came at 0.2–3.0 s after relaunch, on the verified room screen, scrolled to the
  bottom, with the anchor row visible. The committed message was not yet in the restored timeline. It became visible at
  12.6, 13.6 and 4.6 s. These are visibility lag observed as "absent" and belong in the lag law, not in a persistent-error
  model.
* The 2 late ⊥ (trials 10 and 108) were wrong screens: the second was a system dialog (`android|`, the ANR).
* **Co-failure.**
  * Late reads: (a)&(b), (a)&(c) and (b)&(c) were **never wrong together (0/101, 95% CI [0, 0.037])**. All three were ⊥
    together in 2/101, from the same wrong screen.
  * Early reads: (a) and (b) were wrong together in 3/3 of their errors. They are the same dump of the same lagged view.
    This is a lag co-failure, not an independent reading error.
* Pilot only (not in the 101): in 1 of 3 pilot trials (netcut), the room-list digest showed an older message on a
  verified screen. That is a stale digest, a real wrong reading. It was not seen again in 101 trials.

**C2-1b. Campaign-1 re-score of the 5 "co-failures"** (`c1_rescored_cofailures.csv`). The campaign-1 logs keep only
`(t, copies, states)` per poll; screen identity was **not logged**. So ⊥ versus wrong cannot be decided directly from them.
What the logs do show:
* **0/5 rendered a contradicting state.** No "Sending" or "Failed" appeared for a committed message.
* **2/5** rendered the row as "Sent" and then lost it from the tree until the window ended: partC `none/respdrop` at
  4.6–35.4 s, partD `fg_kill9` at 8.7–11.2 s.
* **3/5** never showed the row in any timeline poll: pilot `bg_kill`, partC `force_stop`, partD `force_stop/net_pre`.
* In **4/5** the room-list digest read after the window shows this trial's nonce. The app had rendered the committed
  message, and the timeline reader just did not see it.
* In the 5th (pilot) the digest reader found no snippet at all.

Under the campaign-2 rule, all five are **⊥ for families (a) and (b), not wrong readings**. Family (c) is correct in 4
and ⊥ in 1. The mechanism campaign 2 observed directly is consistent with this: force-stop relaunch lands off the room
(first read ⊥ in 31/31 force-stop trials), and the old reader, which had no screen check, would have scored that as
"absent".

**C2-1c. Extra cell: response loss as a *timeout* instead of a RST** (`c2_element_timeout_trials.csv`, 6 trials;
the proxy's new `armhold` mode forwards the PUT, Synapse commits, and the reply is withheld with the client socket left
open). The trials ran back-to-back, which makes them pair up:
* **400, 402, 404 (clean, n = 3).** One PUT, reply withheld. Element nevertheless showed the message as "Sent" **2.9–3.5 s
  after the tap**, while the PUT was still outstanding: the `/sync` echo reconciled it. The hung request **timed out after
  70.0 s (3/3)**, and Element then re-PUT the same txnId, which Synapse deduplicated. Exactly one copy in every trial.
* **401, 403, 405 (queued behind the previous hung PUT).** Element's send queue is serial, so the new message waited until
  the previous trial's request timed out. Its indicator read **"Sending" for 12–20 s**, correctly, since it was not yet
  committed. It was committed 14–21 s after its tap and was "Sent" 3 s later, exactly once.
  Consequence: a hung (not reset) request delays every later send from the same client by up to the 70 s timeout.

### C2-2. K-9 Mail 24.0: what happens after response loss (`c2_k9_nosent_trials.csv`, 15 trials, no Sent folder)
Protocol: every trial starts from a clean slate. K-9 is force-stopped, the Outbox rows and `outbox_state` are deleted from
K-9's local DB, and the notification shade is cleared with "Clear all". The clearing was verified as successful in 15/15
(`shade_cleared_before`). The app's own state is read from its SQLite store (root), next to the UI. Cells:
`respdrop` × {none, bg_kill9, force_stop, netcut} × 3, and `acked` × 3.

**Source mechanism** (K-9 24.0 = thunderbird-android tag `K9MAIL_24_0`, commit `73dd96a4`; excerpts and sha256 in
`campaign2/logs/source_excerpts_synapse_k9.txt`):
* `SmtpTransport.sendMessage` sets `entireMessageSent = true` once the final `\r\n.` has been written. Any later exception
  is rethrown as `MessagingException("Unable to send message", permanentFailure = entireMessageSent)`.
* `MessagingController.sendPendingMessagesSynchronous` then records `setSendAttemptError` (`outbox_state.send_state =
  error`) and sets `X_SEND_FAILED`.
* On **every** later send pass ("Sync account", "Send messages", the 15-min poll), Outbox messages whose `send_state !=
  READY` are **skipped** ("Skipping sending message"). Their stored error is re-raised as the "Failed to send some
  messages" notification.
* K-9 thus deliberately refuses to auto-retry a message that may already have been delivered: the RFC 1047 duplicate
  window, handled client-side as at-most-once plus a user-visible failure.

**Measured (12 respdrop trials, all committed exactly once on the server):**
* **Failed state.** One second after the drop, before any fault, the local store held the message in **Outbox with
  `X_SEND_FAILED` and `send_state = error`, 1 attempt, "Unable to send message"** (12/12). The fault class does not
  matter: the state is already final before the fault.
  * The Outbox list shows the mail with **no** failure text in the accessibility tree.
  * Opening it gives a plain message view with no failure marker.
  * The failure notification was shown in 9/12. The 3 exceptions were the force-stop trials: force-stop removes the
    app's notifications, and the notification came back at the next send pass ("Send messages": `failed_shown` in 3/3).
* **"Sync account" (+20 s): no new SMTP DATA (0 in 12/12), no new server copy, and the mail is still in the Outbox**,
  both in the DB (`send_state = error`, 12/12) and in the UI (`still_in_outbox_after_sync_ui = present`, 12/12). This
  **corrects campaign 1**: its `still_in_outbox_after_sync = 0` came from an empty, never-recorded field. Direct evidence:
  all 18 campaign-1 mails left in K-9's local Outbox were still there with `send_state = error` at the start of
  campaign 2 (`campaign2/logs/k9_localstore_snapshot_before_c2.txt`).
* **Outbox → "Send messages" (+20 s): no new DATA (0/12), no new copy, still in the Outbox (DB 12/12).** The UI re-read
  after this step was ⊥ (navigation) in the no-Sent batch, and `present` 5/5 in the Sent batch after a navigation fix.
* **Agent recompose (scripted GUI retry: new compose with the same subject and body, Send): 12/12 produced a second
  server copy** (1 new DATA each). Every pair had **two distinct Message-IDs** (12/12), so no Message-ID-based receiver
  dedup could merge them. This is the GUI-retry duplicate: K-9's own resend paths never duplicate, but an agent that
  redoes the step does.
* **acked (3):** Outbox absent, no notification (0/3) after clearing between trials. Campaign 1's 5 `acked`
  "notification" errors were carry-over. The persistent error-state mails re-raise the notification on every send pass,
  which the source confirms.

Family error vs truth (`c2_k9_families.csv`; ⊥ = 0 in these reads):

| family / read | subset | n | wrong | rate [95% CI] |
|---|---|---|---|---|
| (a) Outbox membership ("listed ⇒ not sent"), early and late | respdrop | 12 | 12 | 1.00 [0.76, 1] |
| (a) Outbox membership | acked | 3 | 0 | 0 [0, 0.56] |
| (b) failure notification, early and late | respdrop | 12 | 9 | 0.75 [0.47, 0.91] |
| (b) failure notification | acked | 3 | 0 | 0 [0, 0.56] |

### C2-5. K-9 with an IMAP Sent folder (`c2_k9_sent_trials.csv`, 18 trials)
Configuration: the mailbox `Sent` was created for alice on GreenMail. In K-9's own Settings UI (Account → Folders → Sent
folder) "Sent" was selected; "Upload sent messages" was already on (prefs: `sentFolderId=3`, `uploadSentMessages=true`).
Cells: `acked` × 4, `bg_kill9/acked` × 3, `respdrop` × {none 3, bg_kill9 3, force_stop 2}, `bg_kill9/net_pre` × 3. The
shade was cleared before every trial (18/18). A background IMAP poller (0.5 s) records when the nonce appears in alice's
server-side `Sent`. The Sent list in the UI was read with a screen check (`toolbarTitle == Sent`) after the Outbox and
shade reads, so its first-seen time (~40 s) reflects read order, not app lag.

| cell | n | committed in window | original in server Sent (end, before recompose) | Sent APPEND after Send (s) | Sent list (UI), late | Outbox after Sync / Send-messages | new DATA on Sync / Send-messages | recompose copies |
|---|---|---|---|---|---|---|---|---|
| acked (none + bg_kill9) | 7 | 7 | 7/7 | 3.3, 5.2, 5.2, 5.2, 5.2, 5.3, 5.3 | present 7/7 | absent / absent | 0 / 0 | – |
| respdrop (none 3, bg_kill9 3, force_stop 2) | 8 | 8 | **0/8** | **never** (the only Sent copy that ever appeared, at ~195–209 s, is the recomposed one) | **absent 8/8** | present 8/8 / present 8/8 | 0 / 0 | **2 in 8/8** (distinct Message-IDs 8/8) |
| net_pre + bg_kill9 | 3 | 0 (sent on Sync) | 3/3 | 117.7, 122.8, 122.9 (after the Sync re-send) | absent at window end (correct: not yet sent) | absent / absent | 1 / 0 | – |

* **Does the Sent-folder evidence reveal the committed message after a restart? No for response loss (0/8, including
  5/5 with bg_kill9 or force_stop), yes for acked sends (7/7).** K-9 moves a message to Sent and queues the IMAP APPEND
  only in `moveOrDeleteSentMessage`, after `backend.sendMessage` returns successfully (source excerpt). The Sent folder
  is therefore **client-written evidence**: it inherits the client's (wrong) belief and is not an independent
  server-rendered history. The server copy in bob's INBOX is the only evidence of the commit, and the sender cannot see it.
* **Lag of the Sent evidence when it does appear:** APPEND 3.3–5.3 s after Send (n = 7). For net_pre it came only after
  the Sync-triggered re-send, 118–123 s after the original Send.
* **Family error, Sent mode** (`c2_k9_families.csv`; no ⊥):
  * (c) Sent folder, late: wrong **8/8** respdrop [0.68, 1], 0/7 acked, 0/3 net_pre;
  * (a) Outbox: 8/8 respdrop wrong;
  * (b) failure notification: 6/8 respdrop wrong (the 2 force-stop trials show none, as before).
* **Co-failure:** (a) Outbox & (c) Sent wrong together in **8/8** respdrop trials; all three families in 6/8. Both views are
  written by the same client decision, so for K-9 a "Sent folder" family is **not** independent of the Outbox family.
* The `net_pre` mails were marked failed at first (`X_SEND_FAILED`, `send_state=ready`), because the network-unreachable
  error is not permanent. The benign "Sync account" re-sent them (1 DATA each) and they left the Outbox: the same
  difference from respdrop's `error` state as in campaign 1.

### C2-3. Synapse 1.164.2 transaction-id horizon and scope (`c2_synapse_txn.csv`, source excerpts in `logs/source_excerpts_synapse_k9.txt`)
**Source** (installed package, sha256 recorded in the excerpts file):
* **Layer 1, in-memory cache.** `rest/client/transactions.py` `HttpTransactionCache` keys on `(path, "user", user_id,
  device_id)`: the access-token id is used only for tokens without a device. `CLEANUP_PERIOD = 30 min`, and a looping
  cleanup drops entries older than 30 min, so an entry lives 30–60 min. It is lost on restart.
* **Layer 2, persistent mapping.** `handlers/message.py` looks up `event_txn_id_device_id` by `(room_id, user_id,
  device_id, txn_id)`: "transactions are scoped to a user's device ID". `storage/databases/main/events_worker.py` runs
  `_cleanup_old_transaction_ids` **every 5 min** and deletes rows with `inserted_ts` older than **24 h**.

**Empirical check** (user bob, dedicated room, two devices; one run, 07:39–07:44):

| step | what | result |
|---|---|---|
| S0/S1 | same device, immediate retry | same event_id (1 copy) |
| S2 | same user, **other device**, same txnId | **new event** (2 copies): device-scoped |
| S3 | same device_id, new access token (re-login) | same event: scope is the device, not the token |
| S4 | retry after a Synapse restart (cache gone) | same event: persistent DB row |
| S5 | txnA's rows aged by 25 h (`inserted_ts` shifted while Synapse was stopped), restart, the 5-min cleanup deleted them (observed within 300 s), retry | **new event (duplicate, 3rd copy)** |
| S6 | txnB sent after the restart, its row aged 25 h and deleted by the cleanup while the in-memory entry (<30 min) was alive, retry | same event: the cache alone still deduplicates |

So the dedup horizon is **max(24 h persistent row, 30–60 min in-memory entry)**, scoped to one device (and room). The
24 h ageing was simulated by editing `inserted_ts`; we did not wait 24 h. An agent's GUI redo mints a new txnId and is
never deduplicated, which C2-1 and the K-9 recompose show. The partial runs (`logs/c2_synapse_txn_run1_partial.log`,
`run2_partial.log`) stopped at the restart step because no pid file existed. Their S0–S3 results are identical.

### C2-4 (optional item). A third app: Etar 1.0.57 + DAVx5 4.5.21-ose + Radicale 3.9.0 (CalDAV) (`c2_caldav_trials.csv`)
Setup: DAVx5 account "alice" on `http://10.0.2.2:5233/alice/` (fault proxy → Radicale :5232), calendar `alice/cal`
synced, on a read-only AndroidWorldAvd instance (console 5590). The event is created in Etar through its editor (INSERT
intent with title = nonce, then DONE). The calendar provider marks it dirty, and DAVx5 uploads `PUT
/alice/cal/<uuid>.ics`. The proxy arms on the nonce in the PUT body: Radicale commits (201) and the reply is dropped with a
RST. Faults on the DAVx5 process: none / `kill -9` / `am force-stop`. The kill and force-stop cells re-arm "sticky" for
4 s, so that DAVx5's immediate retry is also unanswered before the fault. Window 120 s, then DAVx5 "Synchronize now" +
25 s, then (every 3rd trial) an agent recompose.

* 9 trials. **8 were valid response losses**. In trial 15 the upload came >120 s after the save, after the arm window,
  so it had no drop.
* Save → upload took ≈53 s: Android's content-triggered sync delay.
* **Outcome: 8/8 exactly one server copy.**
* Mechanism: DAVx5 re-sends to the **same UID-derived href** with `If-None-Match: *`. Radicale answers **412
  Precondition Failed** (`logs/c2/` Radicale log: "creation requested but item found"), and DAVx5 then reconciles.
  * no fault: retry 0.3–0.4 s after the RST;
  * kill -9 / force-stop: both replies unanswered, then the restarted sync re-PUT the same href 53–124 s later → 412.
* So DAVx5 + Radicale **meets G2** through a stable, client-chosen resource name and a conditional create. This is an
  idempotency key in the URL. The provider row ended `dirty=0` with `_sync_id` = that href in every trial except one: in
  trial 16 (force-stop) the row was still dirty with `_sync_id=NULL` at the window end, and it was resolved by the next
  sync without a duplicate.
* **Agent recompose (3/3): a second server copy (new UID).** The GUI-retry duplicate again.
* Etar shows the event locally from the moment of DONE, whatever the server state. Its UI is a hop-1 (local-store) view
  only. Neither Etar nor DAVx5 showed any error in these trials.
* A superseded first launch without sticky re-arming was stopped before any trial finished (`logs/c2_caldav_v1_nonsticky.log`, empty; no rows). In the pilots
  (`pilot_caldav.csv`) a drop hit a leftover event; it showed the same same-href re-PUT.

### C2-6. Parameter table update (campaign 2; it supersedes the corresponding campaign-1 rows above where they conflict)
| Parameter | Element 1.6.62 + Synapse 1.164.2 | K-9 24.0 + GreenMail (no Sent folder / IMAP Sent folder) | Etar + DAVx5 + Radicale | Source |
|---|---|---|---|---|
| G2 after response loss | **Yes, 83/83** exactly once (60 standard + 23 sticky). Paths: immediate same-txnId retry acked before the fault (62), same-txnId re-send after relaunch (3), no re-send with reconciliation through the `/sync` echo (18). | **No retry, by design**: post-"." failure ⇒ `send_state=error` (permanent), skipped by every later send pass. 0 new DATA after Sync or Send-messages (12/12 no-Sent + 8/8 Sent-folder trials). | **Yes, 8/8**: same-href conditional re-PUT → 412, including after kill -9 / force-stop (re-PUT 53–124 s later). | `c2_element_outcomes.csv`, `c2_k9_summary.csv`, `c2_caldav_trials.csv` |
| GUI-retry (agent recompose) duplicates | Not run on Element (a new message gets a new txnId, and S2/S5 show that a new key is never deduplicated) | **Yes, 20/20** (12 no-Sent + 8 Sent-folder): 2 server copies, distinct Message-IDs | **Yes, 3/3**: 2 copies (new UID) | same |
| App-retry dedup horizon / scope | max(24 h DB row, 30–60 min cache), per (user, device, room); beyond it the same txnId ⇒ new event (S5) | n/a (no app retry) | as long as the href exists on the server; per resource | `c2_synapse_txn.csv`, source excerpts |
| Visibility lag after restart (row = hop-1 indicator), censoring | **0/101 censored** (window ≥120 s; max 13.6 s). p50/p90/max s: nofault 2.5/2.9/3.8 (reader floor); bg_kill9 4.0/8.0/13.6; force_stop 12.0/12.3/12.7 (navigation after the relaunch lands off the room); netcut 2.4/2.7/2.9; sticky bg_kill9 4.1/4.4/4.6; sticky force_stop 11.1/12.3/12.4; restart floor 3.6/3.9/3.9 | Sent-folder copy (server APPEND): 3.3–5.3 s after Send for acked (n = 7); **never** for respdrop (0/8) | n/a (Etar renders locally at once) | `c2_element_lag.csv`, `c2_element_first_visible.csv` |
| Hop-1 view lag-free? | **No**: the indicator appeared in the same dump as the row in 101/101 and was "Sent" in 1,036/1,036 row sightings | Outbox is a local store (lag-free) but wrong by design for respdrop | Etar = local store | same |
| Family error, ⊥ separated (late read) | (a) 0/99 (⊥ 2), (b) 0/99 (⊥ 2), (c) 0/99 (⊥ 2). First non-⊥ read: (a) 3/101 and (b) 3/101, all lag-blind "absent" at 0.2–3.0 s after relaunch | Outbox: 12/12 wrong (respdrop), 0/3 (acked). Failure notification: 9/12 wrong (respdrop; force-stop clears it), 0/3 (acked, no carry-over). **Sent folder: 8/8 wrong (respdrop), 0/7 (acked), 0/3 (net_pre)** | – | `c2_element_families.csv`, `c2_k9_families.csv` |
| Co-failure | Late: **0/101** for every pair [0, 0.037]; ⊥ together 2/101 (same wrong screen). Early: (a)&(b) 3/3 of their errors (the same lagged dump) | Outbox & notification wrong together in 9/12 respdrop (no Sent). Sent mode: Outbox & Sent folder 8/8, all three 6/8 | – | `c2_element_cofailure.csv` |
| First read is ⊥ | 33/101: 32 wrong screen (31 = force-stop relaunch lands off the room), 1 empty timeline | 0/15 | – | `c2_element_poll_verdicts.csv` |
| Campaign-1 "co-failures" (5) | 0/5 contradicting state rendered; 2 rendered then left the tree, 3 never in the timeline polls; the digest showed the nonce in 4/5 ⇒ re-scored ⊥ (a, b) | – | – | `c1_rescored_cofailures.csv` |
| Response loss as timeout (no RST) | 3/3 clean: "Sent" via the sync echo 2.9–3.5 s after the tap while the PUT hung; the hung PUT timed out at **70.0 s**, then a same-txnId re-PUT (deduplicated); later sends queued behind it ("Sending" for 12–20 s). Exactly once 6/6 | not run | not run | `c2_element_timeout_trials.csv` |

### C2-7. Caveats, failures and what was not done (campaign 2)
* **Resolution.** One uiautomator dump takes ≈2–2.5 s. The `nofault` lag (2.5 s) is the reader floor, and the lower end
  of each lag interval is usually 0. Lags are upper bounds on app behaviour.
* **What the standard Element cells test.** In the 60 standard response-loss cells (and in campaign 1), Element's own
  immediate retry was acknowledged before the kill, force-stop or network cut. Only the 20 sticky-v2 cells test "process
  death before any ack". In 3 of the 10 `bg_kill9_sticky` trials Android had already re-spawned Element before the
  relaunch.
* **Small n outside Element.**
  * K-9: 3 per cell (no-Sent) and 2–4 per cell (Sent). The K-9 outcome is fixed before the fault (`send_state=error` 1 s
    after the drop), so per-fault cells are replications.
  * CalDAV: 8 valid trials, 3 recomposes.
  * Timeout: 3 clean trials.
* **Simulated ageing.** The Synapse 24 h ageing was simulated by shifting `inserted_ts`, and one sequence was run. The
  cleanup period (≤5 min), the device scoping and the cache layer were observed directly.
* **Lost trials.** Element trials 11–16 were lost to a system ANR dialog for AndroidWorld's accessibility forwarder,
  which is installed on GhostAvd but unused by this reader. Trial 17 was killed by the operator. None of them is in the
  CSV. The K-9 harness hung once in its first launch (no row was written). It was restarted with step logging and did
  not hang again.
* **Rig changes.** `faultproxy.py` gained two modes, `armsticky` and `armhold`; `arm` is unchanged. The Matrix proxy was
  restarted between batches to load them. Synapse was restarted only for C2-3, after all Element trials.
* **Not done.**
  * K-9's unattended 15-min poll lag for `net_pre` (R1 m7);
  * E2EE rooms;
  * a physical device;
  * an agent or planner on the device;
  * VLM reads (excluded by the no-LLM rule);
  * any change to the manuscript.
* This section was written by hand from the `campaign2/` CSVs (`analyze_c2.py` prints every table). It is **not**
  produced by `render_summary.py`, so re-rendering the template would drop it.

### C2-8. Files (`campaign2/`)
* Per-trial data:
  * `c2_element_trials.csv` (101 trials; `polls` = per-poll reader records);
  * `c2_element_timeout_trials.csv` (6);
  * `c2_k9_nosent_trials.csv` (15);
  * `c2_k9_sent_trials.csv` (18);
  * `c2_caldav_trials.csv` (9);
  * `c2_synapse_txn.csv` (8 steps);
  * `pilot_*.csv` (pilots, not analysed).
* Derived, from `analyze_c2.py`:
  * `c2_element_outcomes.csv`, `c2_element_lag.csv`;
  * `c2_element_first_visible.csv` (simulator input: per-trial first-visible intervals for row and indicator, censoring
    flag, ack mechanism);
  * `c2_element_families.csv`, `c2_element_per_trial_families.csv`;
  * `c2_element_cofailure.csv`, `c2_element_poll_verdicts.csv`;
  * `c2_k9_summary.csv`, `c2_k9_families.csv`;
  * `c1_rescored_cofailures.csv`.
* Logs (`logs/`):
  * harness logs;
  * `rig_c2/` (proxy request logs with every `PUT`/`DATA` and every drop, plus the Radicale, GreenMail and emulator logs);
  * `source_excerpts_synapse_k9.txt`, `versions_hashes.txt`;
  * `k9_localstore_snapshot_before_c2.txt`.
* End state (≈08:10 +07): emulators 5570, 5580 and 5590 were stopped, along with Synapse, GreenMail, Radicale and all
  three fault proxies. Two other emulators (5584, 5586) belong to another agent and were not touched. Colima was not
  touched.
