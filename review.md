# MobiSys 2027 Review Packet: GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents

**Paper folder:** `/Users/xuanbachle/Workstation/MobiSys2027/papers/P03-ghosteffect/`
**Date:** 2026-11-07
**PDF:** `manuscript/main.pdf`, 20 pages (`main.log`: "Output written on main.pdf (20 pages)").
**Body length vs. 12-page limit:** within the limit, no slack. From `main.aux`: Section 10 (Conclusion) is on page 12, References start on page 13, Appendix A (Proofs) on page 15, Appendix B (Additional results) on pages 17-20. Body is exactly 12 pages; references (2 pages) and appendix (6 pages) are excluded. Three overfull boxes, largest 7.9 pt.

**What was read (fully):** `manuscript/main.tex`; every file in `manuscript/sections/` (abstract, introduction, background-motivation, model, theory, design, implementation, evaluation, 07-real, discussion, related work, conclusion, appendix-proofs, tab-apps, tab-position); `manuscript/generated/macros.tex` (459 macros; every macro quoted below is resolved to its value) and all 18 generated tables and figures; `manuscript/figures/` (fig1.tex, fig-arch.tex, icons/); `STATUS.md`; `others/notes.md`; `others/citation-audit.md` (123 entries, all marked verified). `reviews/round1..4` and `reviews/self-review.md` were skimmed for history only; the reviews below are fresh.

**Is 07-real.tex included?** Yes. `07-evaluation.tex` inputs `generated/real_section.tex`, which inputs `sections/07-real`. The inclusion is conditional on `artifact/results/real/SUMMARY.md` existing at render time; it exists, so RQ7 (Section 7.7) is in the PDF.

**State of the manuscript.** `STATUS.md` describes a finished round-3 revision. The artifact has moved further: `artifact/scripts/planner_sim.py` contains later code (clock origin, lag-table size, vetted rules; `REAL4` table at lines 1870-1900) and `artifact/results/planner_real4_*.csv` hold its outputs. `render_real.py` does not read them and no section mentions them. The manuscript is reviewed as it stands; the reviews flag where it is narrower than its own artifact.

**Artifact spot-checks (by reading CSVs, not rerunning):**

| # | Claim in paper (macros resolved) | Artifact source | Result |
|---|---|---|---|
| 1 | Scripted GUI redo duplicated 20/20 K-9 sends | `campaign2/c2_k9_nosent_trials.csv` (12 rows `recompose_server_copies=2`) + `c2_k9_sent_trials.csv` (8 rows) | Match |
| 2 | CalDAV 8/8 exactly once; redo 3/3 duplicates | `campaign2/c2_caldav_trials.csv`: 9 trials, 8 dropped replies, `server_copies_window=1` in 9/9, `recompose_server_copies=2` in 3/3 | Match |
| 3 | Element 83/83 exactly once; 65 same txnId, 18 via /sync | `c2_element_outcomes.csv` row `ALL_interrupted(respdrop)` | Match |
| 4 | Lag p50/p90/max: kill -9 4.0/8.0/13.6; force-stop 11.9/12.3/12.7; net 2.4/2.7/2.9; none 2.5/2.9/3.8; 0 censored | `c2_element_lag.csv` | Match |
| 5 | Late reads 0/99 wrong; no two families wrong together 0/101 (CI 0-3.7%); first read bottom 33/101; first observed wrong 3/68 | `c2_element_families.csv`, `c2_element_cofailure.csv` | Match |
| 6 | Table 4 Element: product 3.0% asks, joint 72.9%, Thm-only 37.2%, rules 9.0%/3.1%, joint 12.7% at 5,000 labels, passive product P_v 14.59, tail product 2.77 | `planner_real.csv` | Match |
| 7 | Table 4 K-9: rules P_v 65.85 (no Sent), 28.91 (Sent); passive joint 9.85; trust-app 27.67 | `planner_real.csv` | Match |
| 8 | Table 2: product 0.05/24.9, joint 0.05/66.7, rules 0.52/23.9, Thm-only 73.0, redo 63.3 | `planner_sim.csv` | Match |
| 9 | Synapse: other device duplicates; row aged past 24 h duplicates | `c2_synapse_txn.csv` | Match |
| 10 | Ledger under qemu SIGKILL: FULL 0 lost (3 trials), OFF lost 15-158 in 3/3 | `ledger_powerloss.csv` via SUMMARY.md | Match |
| 11 | Table 4 label budget "2,000 / 5,000 per class" | `planner_sim.py` `N_LAG = 20000`; `planner_real4_lag5k.csv` (joint 30.6% asks with 5,000 lags), `lag2k.csv` (100%) | **Omission:** lag tables hold 20,000 bootstrapped lags per class regardless of the quoted label count; not stated |
| 12 | Section 3 and Algorithm 1 wait from t0 (the tap); Table 3b lags are from relaunch | `real_params.py` line 69; `planner_real4_t0down5.csv` (P_v 18.8% product, 29.9% joint if waiting from the tap with 5 s downtime) | **Model/measurement inconsistency**, not discussed |
| 13 | "joint holds only because it asks 74.4%" under an unlogged tail (2,000 labels) | `planner_real4_tail5.csv`: at 5,000 labels joint P_v 2.01% (CP 2.32) | True at 2,000, false at the headline 5,000; paper silent |

Every printed number matches. Items 11-13 are places where the text is narrower than the artifact.

---

## Review 1 — Senior mobile-systems PC member (Android apps, accessibility, on-device agents)

**Paper summary.** The paper names a failure mode of mobile GUI agents: an interruption between a commit tap and its confirmation leaves a "ghost effect" whose outcome the agent cannot read back, and a redo through the GUI sends it again. On Android 13 emulators with self-hosted servers, K-9 Mail keeps an accepted mail in its Outbox as a permanent error, and a scripted redo duplicated 20/20 K-9 mails and 3/3 CalDAV events; Element and DAVx5 recovered by themselves through idempotent client retries. GhostEffect is a recovery layer: a write-ahead SQLite ledger in a controller outside the agent, a nonce typed into a free-text field, three accessibility-text evidence families (outbox, nonce, history digest) plus a VLM family, a certified wait for visibility lag, and a planner that retries, declares or asks under a duplicate/loss budget, with bounds calibrated by Clopper-Pearson on fault-injected effects. Evaluation: model-based simulation, a 149-run emulator campaign, and a simulation re-parameterized from the measurements.

**Overall merit:** 3 (Weak accept)
**Reviewer expertise:** 4 (Expert)
**Sub-scores (1-5):** Novelty 3, Technical soundness 3, Evaluation 2, Significance/impact 3, Presentation & writing 3

**Strengths**
- The K-9 finding (Section 7.7, Table 3a, Figure 1) is a concrete, reproducible systems observation: after a lost SMTP reply, K-9 24.0 records `send_state=error`, skips the message on later syncs, keeps it in the Outbox, and never writes it to the IMAP Sent folder (0/8). It is the first measured GUI-agent ghost duplicate I have seen.
- The two-hop framing (Section 4.4) turns "is retry safe?" into a per-app, testable property (G2) with a measured dedup horizon (Synapse: same device, 24 h; an aged row duplicated).
- The reader discipline in Section 6 (bottom unless package, room title and timeline are verified; "absent" only on a scrolled, anchored screen) is what an accessibility-tree reader needs and is rarely stated.
- The ledger is placed correctly (outside the agent, write-ahead, WAL with `synchronous=FULL`) and tested under a qemu SIGKILL.
- Honest scoping: "We ran no LLM agent and no phone" (Section 1).

**Weaknesses (ordered by severity)**
1. **No agent was run (Sections 6, 7.7, 7.8).** The duplicate comes from a scripted driver that "recomposes and re-sends the same content, as an agent that trusts the screen would". Whether M3A, UI-TARS or AgentProg do that on K-9's error state decides significance, and the rig exists. One LLM agent on 20 K-9 trials would settle it.
2. **The on-device topology, the MobiSys case, is design only (Section 5.1).** "We have built the host topology's decision core and ledger; the on-device service is design only." Nothing is measured about a foreground-service controller under LMK, accessibility-service read cost, or ISSUED-before-tap latency on a device. Host timings (0.04 ms append on a macOS laptop) are not phone numbers, as the paper says.
3. **App coverage is three open-source clients with self-hosted servers (Table 8).** G2 classification needs an observable server. For Gmail, WhatsApp, Signal or a bank, the dedup horizon is unobservable, FLAG_SECURE blocks screenshots and accessibilityDataSensitive hides views (Section 8). State plainly what survives on a closed app: ledger yes, nonce only with a user-only field, G2 unknown, so every interrupted effect is asked about.
4. **Nonce placement conflicts across the paper.** Section 5.2: "By default GhostEffect uses only fields that the counterparty cannot see." Figure 1(b): "Nonce gx:7K2Q9F typed into the subject". Table 8: K-9 field is "mail body (visible)". The experiment used the subject (artifact SUMMARY.md). A subject tag is counterparty-visible and changes the mail the user asked for. The default or Figure 1 must change.
5. **The measured lag is not the modeled lag (Section 3 vs. Table 3b).** T runs "from t0 until the effect becomes visible", t0 the ISSUED time before the tap, and Algorithm 1 waits from t0. Table 3b measures "recovery-to-visible lag" from the relaunch intent. On a phone, tap-to-relaunch can be minutes (Doze, user returns later). A planner waiting from t0 against a relaunch-based table under-waits. The paper does not say which clock the planner uses.
6. **Emulator kill semantics differ from a phone (Sections 6, 7.7).** `am kill` was a no-op for Element (13/13); the force-stop lag (12 s) is "mostly navigation" of the harness, not the app; no LMK under memory pressure, no Doze, no OEM battery manager.
7. **No VLM was measured** ("the VLM family is removed rather than modelled", `params.csv`). "The VLM is a weak tie-breaker" (Section 7.4) is a simulation statement.

**Detailed comments for authors**
1. Section 2.1 says the foreground app "is essentially never reaped". The emulator shows `am kill` spared Element because its sync component keeps it perceptible. Say what this means for the fault mix: for G2 apps with a foreground sync service, app death may be rare and agent death common.
2. Section 5.3: "Hop 1 reads the app's local database." Without root the controller cannot read another app's database; it reads the Outbox screen through the accessibility tree. Make the text match what was built (uiautomator dumps).
3. Section 5.3: a label costs "about 15 s". Campaign-2 trials ran a 120-300 s window plus relaunch. Reconcile, then redo the arithmetic for 5,000 labels per class and outcome times four classes.
4. Section 7.7: "Seven Element trials were lost before writing a row (six to a system ANR dialog)". An ANR is itself an interruption an agent faces. If those sends committed, they belong in the lag table as censored, not as discards.
5. Section 7.7, withheld reply: Element showed Sent via the /sync echo before its 70 s client timeout, so a "committed" reading can precede the app's own acknowledgement. Say whether A1 and the hop-1 qualification cover this path.
6. Figure 1's G2 branch says "after a certified wait the row reads Sent, committed, no ask". Table 4 says the recommended joint mode asks on 72.9% (2,000 labels) or 12.7% (5,000) of interrupted Element sends. The figure shows the product mode; label it.
7. Table 8 lists MockBank, Pro Expense, Markor, Joplin, Tasks.org and Simple SMS; only three stacks were measured. Mark each row measured or planned in the table, not only in the caption.
8. Section 6: uiautomator dumps take about 2 s on a loaded host (load average 16-38 per SUMMARY.md). The 2.5 s no-fault "lag" is the reader's dump time. State the host load; it bounds every lag number.

**Questions for the authors' response**
1. Run one LLM agent (M3A, T3A or UI-TARS) on 20 interrupted K-9 sends with your rig. How many recompose and resend?
2. Which clock does the planner's certified wait use, ISSUED or relaunch? If ISSUED, how do you reconcile it with lag tables logged from relaunch?
3. Where does GhostEffect type the nonce for mail, and is that the default or opt-in?
4. For a closed app (Gmail) whose server you cannot observe, what does GhostEffect do on an interrupted send?
5. What is the per-label wall-clock cost on the emulator, and how many device-hours are 5,000 labels per class and outcome for one app version?

**Ethical / anonymity concerns.** None. Self-hosted servers, test accounts, open-source apps; nonce opt-in discussed; user-prompt study noted as needing IRB approval.

**Confidence and what would change my score.** High on the Android side, medium on statistics. A measured LLM-agent redo rate on K-9 (even n = 20) and a resolved lag clock would move me to 4. An on-device controller measured under LMK would make me champion the paper.

---

## Review 2 — Distributed-systems / theory reviewer

**Paper summary.** Recovery of a GUI effect after an interruption is modeled as a sequential decision under a hidden binary outcome X, a visibility lag T, and noisy, possibly correlated binary reads. The guarantee is conditional: P(retry | committed) at most alpha, P(declare | absent) at most beta. Theorem 4.1 restates Wald's SPRT bound with a lag share, a lag converse, a KL lower bound on reads and a Bayes-risk floor. Proposition 4.3 certifies family-level verdicts under independence across families (A2); Proposition 4.4 certifies the planner's whole stopping region without A2 by a fixed-sequence Clopper-Pearson test. Lemma 4.5 gives a persistent-error floor; Lemma 4.6 handles conservative calibration and union bounds; Lemma 4.7 bounds nonce false matches; Theorem 4.8 (two-hop) shows a local outbox plus idempotent retransmission within a dedup horizon D yields exactly one copy. A KKT split allocates budget across a saga.

**Overall merit:** 3 (Weak accept)
**Reviewer expertise:** 4 (Expert)
**Sub-scores (1-5):** Novelty 3, Technical soundness 4, Evaluation 3, Significance/impact 3, Presentation & writing 2

**Strengths**
- The guarantee (Eq. 1) is conditional on X and prior-free; Corollary 4.2 shows alpha = 0 forces beta = 1, so the budget is the honest object.
- Proposition 4.4 is the right fix for correlated evidence: calibrate the stopping region, not the parts. The fixed-sequence argument (Appendix A.3) is correct and the sample-size consequence is priced (Table 1).
- Lemma 4.5's two-point extremal law checks out (mean epsilon, variance rho epsilon(1-epsilon)); the exchangeable case is handled separately.
- Theorem 4.8 is folklore and says so; the horizon D and device scope are new and measured (Section 7.7).
- The paper separates proved from assumed ("We claim none of these inequalities") and labels every number's kind.

**Weaknesses (ordered by severity)**
1. **The certified quantity excludes the dominant error source (Eq. 1; Table 4).** P_v is the planner's own retry rate; wrong user answers are "outside (1)". On Element, joint has P_v 0.00% but dup 3.17% and loss 2.04% because it asks 72.9% of the time with a 5%-wrong user; product has P_v 0.00%, dup 0.15%, loss 0.09%. The guarantee ranks modes opposite to their end-to-end error. State the composed bound, e.g. P(dup) at most pi(alpha + P(ask) epsilon_u), and say which quantity a deployer should use.
2. **The lag clock in the theory does not match the calibrated lag law (Section 3, Eq. 2, Algorithm 1 vs. Table 3b).** T runs from t0; the emulator lags run from relaunch or network restore (`real_params.py`: "t0 = relaunch intent / network restore / Send tap"). With positive downtime, a planner waiting w from t0 has waited less than w on the table's clock, and the lag share is not certified. The artifact quantifies it (`planner_real4_t0down5.csv`: P_v 18.8% product, 29.9% joint at 5 s downtime) but the paper is silent. Redefine T per class from an observable origin r_e and prove Eq. 2 for it, or add downtime to the wait.
3. **The headline label count hides the lag-table size (Section 7.7, Table 4).** "2,000 / 5,000 labels per class" are verdict labels; lag tables hold 20,000 bootstrapped lags per class (`N_LAG = 20000`). Table 1 says one wait at 0.2 alpha with zero exceedances needs 4,649 lags at alpha = 0.01, times four by class. The 12.7% figure rests on lag samples the quoted budget does not pay for; `planner_real4_lag5k.csv` gives joint 30.6% and product 60.3% asks when lags equal labels, `lag2k.csv` 100%.
4. **"Joint survives an unlogged tail" is label-count specific (Section 7.7).** At 2,000 labels joint holds "only because it asks 74.4%"; at 5,000, `planner_real4_tail5.csv` gives joint P_v 2.01% (CP 2.32), over budget. The abstract implies joint is immune to the tail. It is not.
5. **Proposition 4.3's R(tau) is under-specified for the hand-over path.** Algorithm 1 line 9 resets P to 1 after a failed/stuck hop-1 entry and re-enters the cascade. The proof of Eq. 2 covers it under Pi_0, but the proposition should say P is reset exactly once and that R(tau) includes assignments that begin after a hand-over.
6. **Lemma 4.6(ii) under keyed calibration.** For an unknown-class effect the fallback uses the bounds of all four classes, so the union is over 4K bounds; with delta = min(alpha, beta)/(10K) the marginal slack is 0.4 alpha, exceeding alpha_cal = 0.1 alpha. Either delta is also divided by the class count (say so) or the unknown-class path is over budget by the calibration share.
7. **Theorem 4.1(c,d) need T independent of reads given X.** Appendix A assumes it at the top; Section 3's A1 does not state it. Add it.

**Detailed comments for authors**
1. Corollary 4.2's "alpha = 0 forces beta = 1" is the right headline and justifies the title; put it in words in Section 1.
2. Proposition 4.4: the pilot split that fixes the score is never sized. Say it is disjoint from the n fresh effects and how large it was in the simulator.
3. Theorem 4.8, H3: the "positive window" between creation and first transmission is an app property; for Element it is shorter than one read (20-100 ms vs. a 2 s dump), which is why Element has no hop-1 family. Say so next to H3.
4. Proposition A.1: KKT is "sometimes worse than uniform" (38% at k = 2) and the body reports uniform "changes nothing significant (p = 0.57)". The saga layer's value is the union-bound safety, not the optimization. Shorten.
5. Notation: D is both the dedup horizon (Theorem 4.8) and KL divergences D0, D1. Rename the horizon.
6. "Whatever the dependence across families" (Prop. 4.4) is right, but the guarantee still needs the calibration population to match deployment (Lemma 4.6(ii)). The abstract's "assumes no independence" should not read as assumption-free.

**Questions for the authors' response**
1. Define the clock origin of T per fault class and restate Eq. 2 for it. What is P_v when the planner waits from ISSUED and the table is logged from relaunch, with 5 s and 15 s downtime?
2. How many logged lags per class does Table 4 use, and what are the escalations when the lag table equals the quoted label count?
3. At 5,000 labels, what is joint P_v under the unlogged 2.9% tail?
4. Give P(dup) in terms of alpha, P(ask) and epsilon_u, evaluated for the joint and product rows of Table 4.
5. For an unknown-class effect, is delta divided by the number of classes as well as by K?

**Ethical / anonymity concerns.** None.

**Confidence and what would change my score.** High; I checked every statement and the Appendix A proofs are correct as far as I can see. My 3 reflects the gap between the proved object (P_v) and the quantity that matters (dup + loss), and the clock-origin and lag-table issues, which are fixable in text plus one rerun. Fixed and with the composed bound stated, 4.

---

## Review 3 — Empirical / measurement and reproducibility reviewer

**Paper summary.** GhostEffect targets duplicated or lost GUI effects after interruption. Three evaluation layers: (i) a model-based simulation of 12,000 interrupted workflows over 8 synthetic app profiles, comparing redo, checkpoint-resume, Atomix-style, verify-before-retry, ledger plus key, asking baselines, a same-evidence rule cascade and three certification modes (product, source families, joint), with stress, population and sample-size studies; (ii) a 149-run emulator campaign on Element, K-9 and Etar/DAVx5 measuring hop-2 behaviour after a lost reply, GUI-redo duplicates, lag by fault class and family error rates; (iii) a "measured-parameter simulation" rerunning every mode on profiles built from (ii). Headline: joint certification holds the budget on Element at 12.7% escalations with 5,000 labels per class and asks on every K-9 send, where rules duplicate.

**Overall merit:** 2 (Weak reject)
**Reviewer expertise:** 4 (Expert)
**Sub-scores (1-5):** Novelty 3, Technical soundness 3, Evaluation 2, Significance/impact 3, Presentation & writing 2

**Strengths**
- Paper equals artifact. Every number is a macro generated from CSVs (`others/notes.md` is the ledger). I checked 13 headline figures; all match.
- The emulator campaign is careful where it counts: server ground truth, a proxy that commits then drops the reply, a screen-validating reader, no censoring (0/101 beyond 120 s), fault-class-conditioned lags.
- Lost and discarded trials are disclosed (seven ANR losses; four respawn discards).
- GUI-redo duplicates are shown with distinct Message-IDs (K-9) and a new server resource (CalDAV), ruling out receiver dedup.
- Negative results are kept: on Element, rules with a 30 s wait match the product mode (3.1% vs 3.0% asks); joint asks 72.9% at 2,000 labels; tuned rules match product at P_v about 0.1% in the default world.

**Weaknesses (ordered by severity)**
1. **The headline result is a simulation the measurements make nearly trivial (Section 7.7, Table 4).** Element's late family errors were 0/99, so the measured profile sets every committed-side error to zero (`params.csv`: `hop1_view1 = 0`, `nonce_view = 0`, `digest_view = 0`). The lag law that generates test effects is the same bootstrap the planner is calibrated on. "Every certified mode stays within budget" is then expected by construction; it tests the CP machinery, not the apps. Say what Table 4 can and cannot show.
2. **Sample sizes outside Element are characterizations, yet the strongest comparative claim rests on them (Table 3a, Table 4).** K-9 cells have n = 2-4 (12 and 8 trials); CalDAV n = 8 plus 3 redo. The K-9 lag "U(45 s, 15 min) is an assumption" (Table 4 caption). The rules' 28.91-65.85% P_v on K-9, quoted in abstract, intro and conclusion with two decimals, is a simulation output from an assumed lag law and a 15-trial behavioural observation.
3. **Lag-table size is unstated and 4-10x the quoted label budget** (`N_LAG = 20000`; Table 1 needs 4,649 lags per wait at alpha = 0.01, times four by class). The artifact's tied-budget runs give 100% (2,000 lags) and 30.6% joint / 60.3% product (5,000). The 12.7% headline is not reproducible from "5,000 labels per class".
4. **Label cost is understated (Section 5.3).** "About 15 s" per label vs. 120-300 s trials. Four classes times two outcomes times 5,000 is 40,000 effects per app version: 670 device-hours at 60 s, 167 at 15 s. The region-level shift test needed for pooling "we have not built".
5. **The rule baseline is denied the data GhostEffect gets (Sections 7.1, 7.7).** Rules use a fixed 10 s or 30 s wait and trust the Sent folder; GhostEffect gets 2,000-5,000 fault-injected labels per class. A rule designer with those labels would see K-9's Outbox and Sent folder wrong in 20/20 and 8/8 trials. The artifact already has vetted rules (`planner_real4_vet.csv`: Element 5.3% / 3.1% asks, P_v 0); they are not in the paper.
6. **"Passive labels break every certified mode" is a precondition violation shown as a result (Section 7.7, abstract).** The method already requires fault-injected labels (Lemma 4.6(ii)). It is a useful warning, not a finding on par with the measurements.
7. **Fault coverage is narrow (Section 6).** One network fault form (TCP reset after commit) in 83 of 101 Element trials, a withheld reply in 6; agent death not injected on the emulator; no LMK under memory pressure (`am kill` was a no-op); no Doze. Per-class calibration generalizes only to injected classes.
8. **No artifact link.** "An anonymized copy will be provided to reviewers" (Section 8, `artifact/README.md`). For generated-number claims the artifact is needed at submission.

**Detailed comments for authors**
1. Table 4 caption: state that calibration and test draw from the same measured law, so there is no shift unless a row injects one (passive, tail).
2. Table 3b: p90 from n = 20 is the second-largest observation. Report min/median/max or plot the 20 points.
3. Table 3c, "any two families wrong together 0/101": Element's families read one rendered timeline ("one evidence source", Section 5.3), so this row does not test A2 between sources. Say so.
4. Section 7.7: "first observed reads were wrong in 3/68, all lag-blind". The wait is certified from the same trials that produced these; a held-out lag campaign (another day, another host load) would make the wait credible.
5. Section 7.5: count the stress rows in which the product mode exceeds the budget (Table 6: unlogged tail 0.98, undetected Doze 5.83) next to "rules exceed in 3 of 14".
6. `SUMMARY.md` reports that the AndroidWorld accessibility forwarder "was observed to return a stale tree (a room timeline from minutes earlier while the screen showed the room list)" and that one pilot trial showed "a stale digest, a real wrong reading" on a verified screen. These are the only measured stale-screen events you have and direct evidence for the failure mode of Section 5.3. Put them in the paper with counts.
7. Reproducibility: state the Python version, that `run_all.sh` takes about 20 minutes, and that the host ledger benchmark is non-deterministic. Scrub host paths (`/Users/...` in `run_all.log`).

**Questions for the authors' response**
1. How many logged lags per class does Table 4 use? Report Element joint and product escalations with 2,000 and 5,000 lags per class.
2. Report rules vetted on the same fault-injected labels for Element, K-9 and K-9+Sent.
3. What is the measured wall-clock cost of one fault-injected label, and the device-hours for the 5,000-per-class headline?
4. Did any trial produce a wrong family reading on a verified screen after visibility? If only the pilot stale digest did, how does a zero-error profile test the certification machinery?
5. Can the anonymized artifact, including the emulator rig, be provided during the response period?

**Ethical / anonymity concerns.** None beyond host paths in logs.

**Confidence and what would change my score.** High. The measurements are honest and match the artifact; my concern is what is built on them. A 3 needs (a) lag-table size disclosed with tied-budget rows, (b) a vetted-rules baseline, (c) K-9 simulation numbers out of the abstract or labelled by provenance, (d) an artifact link. A 4 needs an LLM-agent run and a held-out lag campaign.

---

## Review 4 — Generalist senior PC member (LLM-agent relevance, MobiSys fit, positioning, clarity)

**Paper summary.** When a mobile GUI agent taps Send and is interrupted before it sees the result, it cannot know whether the message went out, and redoing the step sends it twice. The paper calls this a ghost effect, measures it on an emulator (a scripted redo duplicated every K-9 mail and CalDAV event tried; Element and DAVx5 recovered because their clients retry with an idempotent id), and proposes GhostEffect: log the effect before the tap in a ledger the agent cannot lose, tag it with a nonce, read the app's screens for evidence after restart, wait a calibrated time, retry only when calibrated bounds say a duplicate is improbable, else ask the user. The budget is (alpha, beta). Theory ties this to sequential testing; evaluation is mostly simulation plus one emulator campaign.

**Overall merit:** 3 (Weak accept)
**Reviewer expertise:** 3 (Knowledgeable)
**Sub-scores (1-5):** Novelty 3, Technical soundness 3, Evaluation 2, Significance/impact 3, Presentation & writing 2

**Strengths**
- The problem is real and under-studied. Benchmarks reward state change, frameworks redo or replay on resume, and nobody has measured what happens to the message when the agent dies after Send. The K-9 permanent-error observation is small but memorable, and its 1988 ancestor (RFC 1047) is a nice touch.
- The two-hop idea is the most transferable contribution: the app's outbox is a key-carrying retry layer the agent did not build, and "is the app G2?" is a question harness builders can answer per app.
- Positioning is thorough and fair. Table 5 separates key, read-back model, asking, crash durability and GUI across 12 systems; idempotency keys, sagas, at-most-once RPC, Kafka idempotent producers, durable execution and the recent agent-recovery papers (LIMBO, UndoBench, RetryBench, Atomix, Agent libOS, Cordon) are placed correctly as far as I can judge.
- Candid: "We ran no LLM agent and no phone"; "On Element simpler mechanisms also hold".

**Weaknesses (ordered by severity)**
1. **Significance is argued, not measured (Sections 1, 2.3, 7.8).** The motivating claim is that deployed agents create ghost duplicates; the paper measures that a scripted redo does. Whether an LLM agent, seeing K-9's "Unable to send message", resends is left to a planned study. The rig exists. Without a small agent run, the first sentence is a hypothesis.
2. **The recommended mode is not the mode that works (abstract, Section 7.7, Table 4).** The abstract recommends joint certification. On Element, joint asks 72.9% at 2,000 labels and 12.7% at 5,000; the product mode asks 3.0% and a 30 s rule 3.1%, all within budget. On K-9 every mode asks 100%. Section 7.7 concedes "the decisive pieces are G2 classification, fault-injected labels, and asking", but the abstract and conclusion lead with joint.
3. **MobiSys fit is thin in the body.** Two of twelve pages are theory, four are a simulation of a world the authors defined, one is the mobile measurement (7.7). The content a MobiSys audience will read (G2 per app, K-9 state, lag by fault class, ledger under power loss, `am kill` semantics) arrives last.
4. **Too many modes, RQs and tables (Section 7).** Seven RQs, three certification modes, two rule variants plus a 12-member rule family, an "earlier design", 15 tables and 5 figures. The reader needs one decision: which mode is GhostEffect? The abstract says joint, Figure 1 and Table 2's bold row say product, K-9 says "every mode asks".
5. **Title vs. content.** Corollary 4.2 says exactly-once by verification is impossible; the title promises it. "Budgeted exactly-once" is explained in Section 4.1, which a MobiSys reader may not reach.
6. **Density.** The abstract has 287 words and 18 numbers. Average sentence 23 words, 31 sentences over 45 words, 151 semicolons, 43 bold lead-ins, 373 parentheses. See the readability report.

**Detailed comments for authors**
1. Intro, "Why existing fixes do not transfer": the first sentence packs three results from three papers into one citation group. Split and attribute.
2. Intro, "Approach" (187 words) introduces about sixteen named concepts before any is defined. Give the one-sentence version first (readability report, 3d).
3. Section 2.3's heading "How often do agents create ghost effects?" is answered with "No published study measures" and a scripted redo. Retitle to what you answer: "Do apps show the trap?"
4. Section 5.4: Algorithm 1 is 29 lines with inline comments like "bkgd., fallible". Add a 5-line prose walk-through of one K-9 and one Element case before the listing.
5. Section 7.4: "Theorem 4.8 alone retries nothing but escalates 73.0%". This baseline and always-ask bracket the design space; lead the comparison with them and the recommended mode, and move the other eleven baselines to table-only treatment.
6. Table 5 (positioning) belongs in the body; Table 1 (sample sizes) in the appendix.
7. "G2" is a label from a proof. Call it "idempotent-retry app" in prose.
8. The conclusion repeats the abstract with the same numbers. Use it for lessons: on apps that retry idempotently the agent should not retry; on apps that do not, the GUI cannot tell you and you must ask; calibration is the price of knowing which is which.
9. Missing citation candidates (verify): Gray and Reuter, "Transaction Processing: Concepts and Techniques" (1992) for the exactly-once/at-least-once discussion; Bailis et al., "Coordination Avoidance in Database Systems" (VLDB 2015). Not insisted upon.

**Questions for the authors' response**
1. If you had to ship one mode today, which is it, and why does the abstract recommend a different one?
2. What fraction of an LLM agent's interrupted K-9 sends end in a resend on your rig? Ten trials with one agent would answer this.
3. Is there any app in Table 8 where certification, as opposed to G2 classification plus asking, changed an outcome in your measurements?
4. Is "classify G2, read the outbox, otherwise ask" the practical takeaway for a harness author without the calibration pipeline?

**Ethical / anonymity concerns.** None; scrub host paths in the artifact.

**Confidence and what would change my score.** Medium-high. The paper is sound and honest; what a MobiSys audience needs is small and arrives last, under an apparatus whose recommended output the measurements do not support. A short agent run, a reordered paper that leads with measurements, and an abstract that recommends what works would make this a clear accept.

---

## Meta-review

### Score table

| Reviewer | Overall | Expertise | Novelty | Soundness | Evaluation | Significance | Presentation |
|---|---|---|---|---|---|---|---|
| R1 (mobile systems) | 3 Weak accept | 4 | 3 | 3 | 2 | 3 | 3 |
| R2 (theory) | 3 Weak accept | 4 | 3 | 4 | 3 | 3 | 2 |
| R3 (empirical) | 2 Weak reject | 4 | 3 | 3 | 2 | 3 | 2 |
| R4 (generalist) | 3 Weak accept | 3 | 3 | 3 | 2 | 3 | 2 |

### Decision: Major revision (one-shot)

The committee agrees that the problem is real, the K-9 and two-hop measurements are genuine systems contributions, the theory is correct and clearly scoped, and the paper equals its artifact (13 of 13 checked numbers match). It also agrees the evaluation does not yet support the framing. The headline mode (joint) is the most expensive and buys nothing on the apps measured; the headline label count omits a 20,000-entry lag table the artifact shows is load-bearing (12.7% becomes 30.6% escalations when lags are tied to labels); the modeled lag clock (from the tap) does not match the measured one (from relaunch), and the artifact shows the mismatch is not benign; no LLM agent was run although the rig exists; and the rule baseline is denied the labels GhostEffect gets. None of these is a flaw in what was measured. All are fixable with text, reruns already in the artifact, and one small agent experiment. A one-shot revision is preferred over shepherding because the abstract, headline and recommended mode would change, and over rejection because the measurement core is sound and the fixes are known.

### Points of consensus
- The ghost-effect framing and the K-9 permanent-error finding are new and well measured (all four).
- The two-hop decomposition with a measured dedup horizon is the most reusable idea (R1, R2, R4).
- The theory is correct and honest about what is classical (R2; R4 on honesty).
- Paper equals artifact; disclosure of discarded trials is good (R1, R3).
- No LLM agent was run; the significance claim is unmeasured (R1, R3, R4).
- The recommended joint mode is not supported by the measured apps (R2, R3, R4).
- The writing is too dense and number-heavy (R2, R3, R4).

### Points of disagreement and resolution
- **R3 (2) vs. others (3) on the evaluation.** R3 holds Table 4 is near-tautological on Element (zero committed-side error; calibration and test share one law). R2 accepts the simulation as a test of the certification machinery but wants the composed bound. R1 and R4 weight the measurement core more. The meta-reviewer sides with R3 on the specific point (the paper must say what Table 4 can show) and with the majority on merit: the measurements stand on their own once the framing matches them.
- **Is the clock-origin issue blocking?** R2 and R1 say a literal Algorithm 1 under-waits; R4 does not raise it. Blocking, because the artifact's own rows show P_v of 18.8-46.4% under modest downtime.
- **Is an LLM-agent run required?** R1 and R4 ask for 10-20 trials; R3 treats it as a path to 4. Required, because the rig exists, the cost is hours, and the first claim depends on it.

### Checklist for the authors

**Required (blocking)**
- [ ] Define the clock origin of T per fault class (tap for agent death, relaunch for app death, restore for connectivity); restate Eq. 2 and CertifiedWait for it; report measured-parameter rows with 5 s and 15 s downtime (Sections 3, 4.2, 5.4, 7.7).
- [ ] State the lag-table size in Table 4 and add rows with logged lags per class equal to the quoted label count (2,000; 5,000); revise "12.7% escalations (5,000 labels per class)" accordingly (Table 4, abstract, Sections 1, 10).
- [ ] Report joint P_v under the unlogged 2.9% tail at 5,000 labels; correct "joint holds" to "joint holds only while it asks" (Section 7.7, abstract).
- [ ] Add rules vetted on the same fault-injected labels to Table 4 for Element, K-9, K-9+Sent; rewrite the "rules retry 28.91-65.85%" claims (Sections 7.1, 7.7, abstract, 1, 10).
- [ ] Run at least one LLM-based agent on at least 10 interrupted K-9 sends on the existing rig and report resends; if none, say so and reframe Section 2.3 (Sections 2.3, 7.7, 7.8).
- [ ] Make the recommended mode consistent across abstract, Figure 1, Table 2's bold row, Section 7.7 and the conclusion; if it is "product where A2 is checked, joint otherwise, ask when neither certifies", say so in the abstract.
- [ ] Reconcile the mail nonce field: Section 5.2 default vs. Figure 1 (subject) vs. Table 8 (body); state that measured runs used counterparty-visible fields under opt-in.
- [ ] State in Table 4's caption that the Element profile has zero committed-side family error by measurement, that calibration and test share one law, and what the table therefore tests (Section 7.7).
- [ ] Add the composed bound P(dup) in alpha, P(ask), epsilon_u and evaluate it for Table 4 (Section 3 or 4.1, Section 7.7).
- [ ] Provide the anonymized artifact including the emulator rig at revision time (Section 8).

**Strongly recommended**
- [ ] Reorder Section 7 so the emulator measurements come first; cut the simulation to baselines that bracket the design (redo, Thm-4.8-only, always-ask, rules, vetted rules, product, joint).
- [ ] Abstract at most 200 words and 4 numbers; no two-decimal K-9 simulation numbers.
- [ ] Shorten Section 4 in the body (Theorem 4.1 in three lines; Lemma 4.5 and Prop. A.1 to the appendix); spend the space on a worked K-9/Element walk-through of Algorithm 1 (Sections 4, 5.4).
- [ ] Correct the label-cost estimate (15 s) to the measured trial duration and give device-hours for 5,000 labels per class and outcome (Section 5.3).
- [ ] Fix the unknown-class union bound: is delta divided by the class count? (Section 4.3, Lemma 4.6).
- [ ] Add the two measured stale-screen events from the artifact (forwarder stale tree; pilot stale digest) with counts (Section 7.7).
- [ ] Replace p90 from n = 20 with min/median/max or a dot plot (Table 3b).
- [ ] Rename the dedup horizon symbol D (Section 4.4).
- [ ] Swap Table 5 into the body and Table 1 into the appendix (Sections 2.2, 5.3).
- [ ] Count the stress rows where the product mode exceeds the budget (Section 7.5, Table 6).

**Nice to have**
- [ ] Measure the on-device controller (foreground service) ISSUED-before-tap latency and survival under `am kill`/LMK on the emulator (Sections 5.1, 6).
- [ ] Per-seed variance for headline rows of Tables 2 and 4 (Section 7.1).
- [ ] A held-out lag campaign (another day or host load) for Element (Section 7.7).
- [ ] One E2EE Element room to confirm the txnId path and nonce probe (Section 8).
- [ ] Gray and Reuter (1992), Bailis et al. (VLDB 2015) if they fit (Section 9; verify).

### Shepherding notes
If the PC converts this to accept with shepherding, the shepherd should hold the authors to the first six required items (clock origin, lag-table size, tail at 5,000, vetted rules, one agent run, consistent recommended mode) and the abstract rewrite. The rest are text changes the authors can make unsupervised.

---

## Readability, clarity, and "less AI" report

### 1. Diagnosis

**(a) The abstract is a results table in prose.** 287 words, 18 numeric tokens plus the symbol pair (alpha, beta); 14 numbers are macros; four carry two decimals (28.91, 65.85, 0.05, 12.7). The reader learns what GhostEffect does in sentence 6 of 11, after 118 words of measurements.

**(b) Sentences assert before they explain.** The intro's "Approach" paragraph (187 words) uses budget, floors, hop 1, nonce, digest, calibration over whole effects, family, product, joint, lag share, two-hop decomposition, dedup horizon, ledger, controller, planner and the fallible user before any is defined:

> "What makes the budget reachable is evidence, read as accessibility text: the app's local outbox (hop 1), a content-carried nonce that turns look-alikes into text matches (Lemma 4.7), and a digest of the history list."

> "What makes it certifiable is calibration over whole effects: per family, which survives any dependence among a family's views (Proposition 4.3), or jointly over the cascade's stopping region, which needs no independence across families (Proposition 4.4)."

**(c) Too many named concepts.** Body occurrences: family 79, certif- 70, hop 66, joint 63, G2 57, nonce 53, escalat- 39, ledger 38, budget 37, product 32, digest 20, ghost 18, look-alike 11, fault class 10, passive label 8, dedup horizon 7, lag tail 7, two-hop 6, certified wait 4. At least 19 named concepts, three of them (product, source families, joint) alternatives to each other. Notation: alpha, beta, alpha_test, alpha_lag, alpha_cal, G(w), T, X, t0, w0, w1, q, q_h, tau, B(tau), R(tau), Q(t), K, delta, kappa, eta, epsilon_0, epsilon_1, epsilon_u, D0, D1, D (horizon), u*, v*, P_v, L_v, W_max, n1, C_e, G2, G2-prime.

**(d) Sentence length and punctuation.** 427 body sentences average 22.9 words; 31 exceed 45 words; 151 semicolons (one per 2.8 sentences); 66 colon-led clauses; 373 opening parentheses. Example (Section 4.4):

> "The planner therefore counts hop-1 entries created after t0 (two entries mean a duplicate), treats 'absent' as absent from both outbox and sent list, and monitors a pending entry until it is acknowledged, escalating it before its age approaches D."

**(e) Simulation vs. measurement is explained late.** Tables 1 and 2 (simulation) precede Table 3 (measurement); Table 4 is a third kind whose definition lives in its caption ("not an emulator run"). Section 7.7:

> "Table 4 reruns every mode on profiles built from these measurements (params.csv records each value's source), with per-class lags and bottom as no observation."

**(f) Paragraph length and emphasis.** Section 4 has paragraphs of 436, 268, 243 and 227 words; Section 7.7 of 275, 268 and 209. 43 bold `\para` lead-ins and 94 `\emph` spans, so emphasis stops carrying signal.

Further evidence, one sentence per section:

> Section 1: "For tool agents, idempotency keys cut duplicates from 28% to 4%, frontier models duplicate in 56-74% of episodes when a read-back cannot reveal the outcome, and no verification-only policy is exactly-once under late commits without a bound on in-flight time."

> Section 5.3: "Joint certification and the waits need about ln(1/delta)/alpha_test samples even with zero events, i.e. thousands at alpha = 1% and tens of thousands at 10^-3, about twice that if the region's true rate is a quarter of alpha_test, and four times that when keyed by fault class."

> Section 7.4: "At P_v about 0.1% the best of 12 variants (wait 60 s, any two) escalates 17.6%, as many as the product mode run at alpha = 0.03; at P_v about 0.5% the product mode, run at a nominal alpha = 0.1 (a 10% guarantee, not 0.5%), escalates 10.4% against 16.3% for the best rule, and joint certification 8.7% at P_v = 0.88%; no rule goes below 16.2% escalations."

### 2. AI-prose tells found

Commands, run from `manuscript/sections/` over the twelve body files with comment lines removed (`$FILES` = the twelve body `.tex` files):

```
for pat in "not only" "not merely" "not just" "rather than" "crucially" "notably" \
  "importantly" "in essence" "robust" "leverag" "delve" "landscape" "seamless" \
  "novel" "comprehensive" "---" "; " "We present" "We propose" "We recommend" \
  "What makes" "by design" "the price"; do
  printf "%-14s %s\n" "$pat" "$(cat $FILES | grep -v '^%' | grep -o -i -- "$pat" | wc -l)"; done
cat $FILES | grep -v '^%' | sed 's/\\[a-zA-Z]*//g; s/[{}$]//g' | tr '\n' ' ' | sed 's/\. /.\n/g' \
  | grep -cE "^ *(This|These|It) "          # sentences opening with a bare demonstrative
cat $FILES | grep -o "\\\\para{" | wc -l    # bold lead-ins
cat $FILES | grep -o "\\\\emph{" | wc -l    # italics
cat $FILES | grep -o "(" | wc -l            # parentheticals
```

Counts: "not only" 0; "not merely" 0; "not just" 0; "rather than" 1; "crucially" 0; "notably" 0; "importantly" 0; "in essence" 0; "robust" 3; "leverage" 0; "delve" 0; "landscape" 0; "seamless" 0; "novel" 0; "comprehensive" 0; em-dash `---` 0; semicolons 151; "We present/We propose" 0; "We recommend" 2; "What makes ..." 2; "by design" 4; "the price" 3; sentences opening with This/These/It 7; bold lead-ins 43; `\emph` 94; parentheses 373; sentences over 45 words 31 of 427.

Reading: the vocabulary tells of machine prose (crucially, leverage, landscape, em-dashes, "not X but Y") are absent, to the authors' credit. The structural tells are present: semicolon chains; parenthetical reference stacking; rule-of-three lists ("the agent, the app or the network"; "outbox, a content-carried nonce, a history digest"; "retries, declares or asks"); punchline closings on most paragraphs ("certification uses what the labels show"; "calibration adds a guarantee that follows the labels"; "the two-hop reduction is where phones differ"; "an agent's redo is not"); rhetorical "What makes X is Y" openers; over-precise numbers in the abstract. Hedging stacks are rare, which is good.

### 3. Rewrites

**(a) Abstract, at most 200 words and 4 numbers**

> A mobile GUI agent that taps Send and is then interrupted cannot tell whether the message went out. If it redoes the step, the app creates a new request, and the server has no key to deduplicate it. We call such an effect a ghost effect. On Android emulators with self-hosted servers we show the trap directly: after a lost SMTP reply, K-9 Mail keeps the accepted mail in its Outbox as a permanent error, and a scripted redo duplicated every one of 20 sends. Apps whose clients retry with their own idempotent id (Element on Matrix, DAVx5 on CalDAV) recovered by themselves, within the server's dedup window. GhostEffect is a recovery layer that records each effect in a write-ahead ledger before the tap, tags it with a nonce, reads the app's own screens for evidence after a restart, waits a calibrated time for the server to show the result, and retries only when calibrated error bounds keep the probability of a duplicate under a budget. When nothing certifies, it asks the user. On the measured apps, the decisive pieces are knowing whether the app retries idempotently, calibrating on interrupted rather than normal sends, and asking when the screen cannot reveal the outcome; on K-9 that means asking on every interrupted send.

(197 words, 2 numbers.)

**(b) First paragraph of the introduction**

> Ask a phone agent to email the signed lease to Alex. It opens K-9 Mail, writes the mail and taps Send. The SMTP server accepts the message; the reply is lost when the connection drops. K-9 records the send as failed, for good: the mail stays in the Outbox with an error, and later syncs skip it. The agent resumes, reads the screen, sees an unsent mail, writes it again and taps Send. Alex gets the lease twice, and the agent reports success. We ran this on an Android emulator against our own mail server; a scripted redo duplicated every K-9 send we tried. We call an effect whose outcome the agent cannot read back a ghost effect. This paper is about deciding what to do with one.

**(c) Ten before/after sentence rewrites**

1. Section 1. Before: "We express exactly-once as a budget: the probability alpha of retrying a committed effect and beta of abandoning an absent one, conditional on the hidden outcome." After: "Exactly-once cannot be guaranteed from a screen. We ask for a budget instead: retry a committed effect with probability at most alpha, and abandon an absent one with probability at most beta."
2. Section 2.2. Before: "A GUI read-back is a perception that can be wrong, tends to repeat its error on a re-read, and is defeated by look-alikes; VeriGUI trains an action-effect verifier for this setting without an error guarantee." After: "Reading a screen is perception. It can be wrong, it repeats the error when read again, and a look-alike item makes the screen consistent with both outcomes. VeriGUI learns such a verifier but gives no error bound."
3. Section 3. Before: "Re-reading a view adds nothing in this model (a reader tends to repeat its answer)." After: "In this model a view is read once. Reading it again returns the same answer and adds no evidence."
4. Section 4.1. Before: "Exactly-once by verification is a limit, not a point, so GhostEffect exposes (alpha, beta) as a knob; reads cost about log(1/alpha)/D0, and the gap between (ub) and (lb) under X = 1 tends to u*/D1 as alpha, beta go to 0 provided alpha log(1/beta) goes to 0." After: "Verification can approach exactly-once but never reach it, so GhostEffect exposes the budget as a knob. Each factor of ten in alpha costs about 1/D0 more reads. In the limit the upper and lower bounds differ by one read's worth of evidence."
5. Section 4.2. Before: "A2 lets bounds multiply, and it is doubtful when families read the same screens: a stale history after a restart fools nonce, digest and VLM at once." After: "Multiplying bounds needs independence across families. That is doubtful when the families read the same screen: a stale history after a restart fools the nonce, the digest and the VLM together."
6. Section 5.3. Before: "Validity holds at any sample size; small samples only widen the bounds and raise escalations." After: "The guarantee holds at any sample size. With few labels the bounds are loose, so the planner asks more often; it never retries more often."
7. Section 5.4. Before: "A hop-1 verdict starts the product on either side, so the 'committed' side of a G2 or local app is certified like any other declaration (its bound enters B_com), and a hop-1 'absent' verdict relaxes its own wait w1, with half of the lag share (Eq. 2)." After: "The outbox read is the first factor in the product. If it says committed for an idempotent-retry app, that verdict is certified like any other. If it says absent, the planner may wait less, because the outbox does not lag; this uses half of the lag share (Eq. 2)."
8. Section 7.1. Before: "The default world departs from the planner's assumptions: nonce misses are persistent (eta = 1% hidden field, plus 0.6% per view); hop-1 views err at 1-5% each plus 0.5% persistently, and the Monitor misreads 1% of terminal states; digest views miss 3% each plus 2% persistently; VLM views err at epsilon_0 in U[0.06, 0.26], epsilon_1 in U[0.04, 0.20], with within-view correlation 0.6 and cross-view correlation 0.1." After: "The simulated world breaks the planner's assumptions on purpose. Some errors are persistent: a hidden nonce field (1%), a stuck outbox reading (0.5%), a stale digest (2%). VLM reads are noisy and correlated within and across views. Full parameters are in Table 2's caption."
9. Section 7.7. Before: "On real apps the decisive pieces are G2 classification, fault-injected labels, and asking when the GUI cannot reveal the outcome; calibration adds a guarantee that follows the labels." After: "On the apps we measured, three things decide the outcome: knowing whether the app retries idempotently, calibrating on interrupted sends, and asking when the screen cannot tell. Calibration does not change those outcomes; it tells you when you may trust them."
10. Section 8. Before: "The decision results come from simulation, model-based or with measured parameters; the generative model departs from the planner's assumptions on purpose, but it is ours." After: "Every decision result is a simulation. The world it simulates breaks our own assumptions on purpose, but we wrote it."

**(d) One-sentence statement the paper lacks**

> GhostEffect logs a GUI effect before the agent commits it and, after an interruption, decides from the app's own screens, a calibrated wait, and if needed the user whether to redo it, so that a committed effect is redone with probability at most alpha and an absent one abandoned with probability at most beta.

Place it as the last sentence of the first introduction paragraph.

### 4. Structural suggestions

- **Abstract.** Use the 197-word version. Keep K-9 20/20 and the Element/DAVx5 contrast. Drop simulation numbers.
- **Section 1.** Open with the K-9 story (3b). Cut "Why existing fixes do not transfer" to three sentences. Replace "Approach" and "Results" with one paragraph: the one-sentence statement (3d), the mechanisms (ledger, nonce, screen evidence with calibrated bounds, certified wait, ask), the two measured findings. Four contribution bullets, measurements first.
- **Section 2.** Merge 2.1 and 2.2 to one page. Rename 2.3 "Do apps show the trap?" and answer with Table 3a. Move Table 5 here from the appendix.
- **Section 3.** Keep. Add a 4-row table: symbol, meaning, where measured. Move the 0.5/0.4/0.1 split to Section 5.
- **Section 4.** Cut to 1.5 pages. Theorem 4.1 in three lines plus the "what is classical" note. Keep Proposition 4.4 and Theorem 4.8 in full. Move Proposition 4.3, Lemma 4.5, Lemma 4.6(iii), Lemma 4.7 and the saga allocation to the appendix with pointers. Rename D.
- **Section 5.** In 5.3, replace "How many labels" with Table 1 and two sentences; correct the label cost. In 5.4, add a worked example before Algorithm 1 (one K-9 send: hop 1 failed, nothing certifies, ask; one Element send: no hop 1, certified wait 13.6 s, row reads Sent). Figure 1 already tells it; point to it.
- **Section 6.** Keep. State host load and dump time. Move "Planned agent harness" to 7.8 or cut.
- **Section 7.** Reorder: 7.1 emulator measurements (Table 3), 7.2 measured-parameter rerun (Table 4 with lag-table size and vetted rules), 7.3 model-based simulation (Table 2 cut to redo, Thm-only, always-ask, rules, vetted rules, product, joint), 7.4 stress and population (one paragraph; Tables 6-7 in appendix), 7.5 mechanisms (one paragraph). Drop RQ1-RQ2 from the body (classical validation; one sentence plus pointer). Replace Table 3b's p90 column with a dot plot of the 83 lags by class.
- **Section 7.8.** Three sentences in Section 8, or replace with the agent run.
- **Section 8.** Keep Limitations and Android realism; fold Ethics into one paragraph; add the composed error bound here or in Section 3.
- **Section 9.** Add one sentence each for LIMBO, Agent libOS and VeriGUI stating the difference.
- **Section 10.** Three sentences of lessons. No numbers.
- **Page budget.** The body is exactly 12 pages. Cuts (Section 4 about 0.7 page; 7.2-7.6 about 1 page; 7.8 0.2; intro 0.3) free about 2 pages, paying for the agent run (0.3), worked example (0.3), lag dot plot (0.2), Table 5 in the body (0.3) and vetted-rules rows (0.1), with margin.

### 5. Style checklist for this paper

1. One claim per sentence; split every sentence over 35 words (31 are over 45).
2. At most one semicolon per paragraph; convert the rest to full stops.
3. No number without its kind in the same sentence: measured, simulated, or exact. Table 4 numbers are "simulated with measured parameters" every time.
4. Counts as fractions (20/20); percentages with one decimal; none in the abstract beyond the K-9 and Element counts.
5. Define a term before first use or do not use it in that section: hop 1, G2, family, verdict, product, joint.
6. One name per concept: "idempotent-retry app" in prose, G2 in theorems; "outbox evidence" in prose, hop 1 in theorems; either "escalation" or "ask".
7. Replace "What makes X Y is Z" with "Z makes X Y".
8. Move parenthetical cross-references to the end of the sentence or the next sentence.
9. Bold lead-ins only where a reader scans (setup, baselines, metrics), not for argument steps.
10. Italics only at a term's first definition; 94 `\emph` spans is too many.
11. End a paragraph with its result, not an aphorism; delete closings like "certification uses what the labels show" unless they add information.
12. State the simulation-measurement relationship once, early in Section 7, in three sentences.
13. Every table caption answers "a measurement of what, with what n" in its first sentence.
14. Lists of three only when there are three things; do not pad or cut to three.
15. Read the abstract aloud; over 60 seconds is too long.
