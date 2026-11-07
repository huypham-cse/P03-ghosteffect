# STATUS — P03 GhostEffect (MobiSys 2027, rank 3)

**Last updated 2026-11-07: round-3 revision done** (round-3 reviews 3/3/3; response in `reviews/round3/response.md`). Emulator campaign 2 integrated; measured-parameter
simulation re-run; title changed to "GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents".
Deadlines: abstract Nov 27, paper Dec 4, 2026.

## State (round 3)
**Compiles cleanly. Body ends on page 12** (references start p. 13; 20 pages total). Errors / undefined refs / undefined cites: **0 / 0 / 0**; largest overfull box 7.9 pt.
**123** bib entries, all cited, all verified (`others/citation-audit.md`; 10 added this round, GreenMail year fixed).

### Round-3 changes
- **Campaign 2** (raw data `artifact/results/real/campaign2/`, read-only): screen-validating reader, ≥120 s window. Element 101 trials (83 lost-reply, all exactly once; 0 censored;
  lag by fault class: none 2.5/2.9/3.8 s, kill -9 4.0/8.0/13.6, force-stop 12.0/12.3/12.7, net cut 2.4/2.7/2.9); indicator = row (not lag-free hop-1); late family errors 0/99,
  co-failure 0/101; campaign-1 co-failures re-scored ⊥. Mechanism: standard cells retry-acked-before-fault 60/60; sticky 20 = 2 re-send + 18 /sync reconcile; timeout 6/6 once.
  Synapse txnId horizon 24 h + device scope (aged row → duplicate). K-9: permanent error state, stays in Outbox (campaign-1 "left Outbox" was an unrecorded field), Sent folder
  never shows committed-but-dropped mail (0/8); **scripted GUI redo duplicated K-9 20/20 and CalDAV 3/3**. DAVx5 + Radicale 8/8 exactly once (G2 by server dedup).
- **Simulator** (`planner_sim.py`): campaign-2 profiles `element` (no hop-1 family), `k9`, `k9sent`; fault-class-keyed calibration with unknown-class fallback; lab fault mix
  option; no-observation (⊥) reads; `g2-only` (Thm 4.8 only) and a 12-variant rule family (`rulesweep`); source-family Q(t)=1 fix (changed every ghost-src row slightly,
  conservatively; all other model-based rows byte-identical to round 2). `real_params.py` rewritten for campaign 2; `render_real.py` rewritten; `sample_size.py` extended.
- **Theory/text**: Thm 4.8 dedup horizon D + device scope (+ necessity in App. A); A1 hop-1 qualification; source-family premise + Q convention; Lemma 4.5 exchangeable condition;
  Lemma 4.6 fault-class keying, δ = min(α,β)/(10K); Alg. 1 defines q_h; Table 1 median-case/zero-event columns; RQ4–RQ5 merged into the body with numbers; NORMAL caveat; ANR /
  discarded trials disclosed; related work (AndroidReality, Coati, LegacyWorld, KedgeFlow, CUA-Recovery, ReTrace, VeriCUA-2, budget conservation, RFC 1047, Synapse source).
- **Headline mode**: joint certification on fault-injected, class-keyed labels (named everywhere); product = the mode that assumes A2.

### Key results (generated; see `others/notes.md`)
- Measured-parameter (Table 4): Element: every certified mode P_v 0.00% (CP 0.04); product 3.0% asks; joint 72.9% (2,000/class) / **12.7% (5,000/class)**; Thm-4.8-only 37.2%;
  rules 10 s 9.0% / 30 s 3.1% (also within budget); trust app status 1.33% (over); passive labels product 14.59%, joint 5.21%; unlogged 2.9% tail product/rules 2.77% (joint
  holds at 74.4% asks); logged tail → 100% asks. K-9: every mode asks 100%; trust 27.67% (+34.34% loss); rules 65.85%. K-9+Sent: every mode asks (fault labels); rules 28.91%;
  passive joint 9.85%, passive product (5,000) 9.84%.
- Default world: product 0.05% at 24.9%; source 0.00% at 47.4%; joint 0.05% at 66.7% (33.8% at 5,000); rules 0.52% at 23.9%; Thm-4.8-only 0.00% at 73.0%. Rule family:
  best rule matches product at P_v≈0.1% (17.6% asks); at P_v≈0.5% product 10.4% vs best rule 16.3%.

### Remaining weaknesses
No LLM agent (redo is scripted), no VLM, no physical phone, no E2EE; n small outside Element; measured-parameter labels are simulated draws (a ≤2.9% unseen lag tail is
not excluded); on Element simpler mechanisms also hold the budget; joint needs ~5,000 labels/class; tuned rules match the product mode in the default world; no anonymized
artifact link yet; region-level shift test for joint pooling not built.

## Previous state (round 2.5, superseded where it conflicts)

**Revised draft with real emulator measurements (two apps). Compiles cleanly. Quantitative claims are exact computation, model-based simulation, host measurement, emulator measurement (RQ7, §7.8), or measured-parameter simulation (Table 4). No agent, VLM or physical-phone measurement.**

| Item | Value |
|---|---|
| Class | `\documentclass[sigconf,review,anonymous]{acmart}` |
| Build | `artifact/run_all.sh` (~20 min; now also `real_params.py` → `results/real/params.csv`, and `planner_sim.py real` → `planner_real.csv`) then `manuscript/build.sh` (render [+ `render_real.py`] → pdflatex → bibtex → pdflatex ×2) |
| Pages | 19 total. **Body ends on page 12** (conclusion ends at the bottom of p. 12; references start on p. 13; no slack). Moved to the appendix this round: Table 1 position (now Table 5), stress (Table 6), population/common-mode (Table 7), Prop. saga statement (Prop. A.1). Appendix: proofs + additional results (Tables 5–15, Figs. 4–5) |
| Errors / undefined refs / undefined cites | **0 / 0 / 0** |
| Overfull boxes > 10 pt | **0** (largest 7.9 pt) |
| Citations | **113** bib entries, **113 cited**, **113/113 verified** (`others/citation-audit.md`; 4 software artifacts added: Element, Synapse, K-9 Mail, GreenMail) |
| Body floats | Tables 1 sample sizes, 2 main comparison, **3 emulator measurements (hop-2 behaviour + evidence families, Wilson CIs)**, **4 measured-parameter simulation**; Figs. 1 scenario (**redrawn: K-9 mail accepted but shown unsent → GUI-trusting resend; GhostEffect asks; Element G2 branch; measured steps marked; re-rendered and checked visually**), 2 architecture, 3 P_v-vs-escalation; Algorithm 1 |
| Theory | Thm 4.1 (b corrected), Cor 4.2 (absolute continuity), Prop 4.3 + Eq. (2) lag split, **Prop 4.4 joint certification (new)**, Lemma 4.5 (+ exchangeable sup), Lemma 4.6 (interrupted population, β side, robustness margin), Lemma 4.7, Thm 4.8 (+ implicit assumptions), Prop 4.9 |
| Artifact | `planner_sim.py` parts: main, stress0..5/6, sweep, user, sens, ncal, decomp, share, **real (measured profiles `element`, `k9`; new `app-state` baseline)**; `real_params.py`, `render_real.py` new. Model-based outputs byte-identical to round 2 (checked: planner_sim.csv, planner_stress.part0.csv, planner_class.csv md5). Deterministic except ledger timings |
| Availability | §8 "Data and artifact availability": anonymized artifact will be provided for review (no external link created) |

## Real data (emulator testbed) — INTEGRATED (round 2.5)
Source: `artifact/results/real/` (SUMMARY.md + CSVs, written by the testbed in `papers/shared-android/`). Android 13 API 33 arm64 emulators; Element 1.6.62 + Synapse 1.164.2,
K-9 Mail 24.0 + GreenMail 2.1.2; commit-then-drop-response fault proxy; scripted driver (no LLM/agent); uiautomator reads on an overloaded host (latencies = upper bounds).
- **G2 (Table 3a):** Element re-sent with the same txnId in 14/14 response-loss trials (incl. 5 bg-kill, 4 force-stop), 1 server copy → G2. Force-stop + relaunch: 10/10 eventually exactly once (H3 not supported for Element). K-9: 0/15 re-sent (1 DATA each), 15/15 left in Outbox as unsent though committed (failure notification 10/15) → non-G2 with misleading failed state = failed-state case of Thm 4.8. K-9 offline mail: 2/15 within 45 s, 15/15 after "Sync account". 72/72 eventually exactly once, 0 duplicates.
- **Families (Table 3b, Wilson):** Element first read (once visible) 0/33 [0–10.4]; end of window indicator & nonce co-fail 5/37 [5.9–28.0] (3 never visible in 45 s), all three 1/37; K-9 Outbox 17/35 early, 15/35 late; notification 21/35; co-fail 10/35 [16.3–45.1].
- **Lag:** Element restart → "Sent" p50 8.5 s, p90 12.7, max 14.6 (n=24); harness floor 4.2–6.3 s (n=9). **Kills:** `am kill` no-op for Element 13/13, killed K-9 15/15. **Ledger** (qemu SIGKILL ≈ guest power loss): FULL/NORMAL 0 acked rows lost (3+3), OFF lost 15–158 in 3/3; plus host 300-SIGKILL write-ordering test.
- **Measured-parameter simulation (Table 4, `planner_real.csv`):** Element, fault-injected labels: product P_v 2.61% (CP 2.96) **over budget** (A2 violated by co-failure); source 0.00% / joint 0.00% (CP 0.04) at 44.9% / 76.3% asks (37.4% / 44.6% at 5,000 labels; source P_v 0.58% at 5,000). Passive labels: product 13.05%, joint 4.80%. K-9: every GhostRecover variant asks on 100% of interrupted workflows (= always-ask); trust-app-status P_v 27.69% (+34.09% loss), rules 65.81%.
- **Not measured / caveats:** n small (2–6/cell), two apps, emulator only, no agent/VLM, TCP-reset form of response loss, CalDAV (Tasks.org) failed, K-9 resend duplicate inferred (no agent run), K-9 queued-delivery lag law U(45 s, 15 min) assumed, K-9 config has no Sent folder.

## Key results (generated; see `others/notes.md`)
- Default world, 12,000 paired interrupted workflows: product planner P_v **0.05%** (CP upper 0.12%; budget 1%), **24.9%** escalations; same-evidence strict rules 0.52% at 23.9%; lenient rules 1.16% (over) at 8.1%.
- Matched P_v ≈ 0.5%: product at nominal α=0.1 escalates **10.4%** vs 23.9% for rules.
- Source-family / joint certification (A2-free): 47.0% / 66.7% escalations at 2,000 labels; 26.4% / 33.8% at 5,000.
- Interrupted world: passive labels → product 0.87% (CP 1.09%); fault-injected labels → 0.11%. Common-mode 5% (fault-injected): product 0.33%, source 0.02%, joint 0.00%, rules 2.16%.
- Stress: product over budget only with lag tails missing from calibration (CP upper 1.22%) and undetected Doze (5.8%); rules over in 3/14 rows.
- Drift κ=10: 0.79% (CP 1.00%) without, ≤0.04% with a 200-effect shift test.
- Certified decisions: hop-1 69%, nonce 63%, digest 44%, VLM needed 16%. Over-delivery 21×: CP slack 3.6×, union/independence slack, unused lag+cal shares.

## Claims changed in round 2.5
- Product certification: in measured-parameter simulation with Element's measured co-failure it exceeds the budget (2.61%) even with fault-injected labels; the paper now recommends joint/source certification on fault-injected labels and states the escalation price.
- On an app whose GUI cannot reveal the outcome (K-9 in our configuration), GhostEffect reduces to asking on every interrupted send.
- Figure 1 is no longer an illustrative payment on a planned app; it is the measured K-9 failed-state case (agent resend step inferred, marked as such).

## Claims weakened in round 2
- Escalations 23.5% → 24.9%; VLM-only "always escalates" now a configuration consequence (98.8%), not a theorem.
- Product certification depends on A2 and on interrupted-population labels; A2-free modes cost labels/escalations.
- Rules and certification have indistinguishable total workflow errors in the default world (p=0.84); certification wins on P_v, stress, and at matched P_v.
- "Reachable on phones" removed; MockBank labelled planned; SIGKILL test described as write-ordering only.

## Next steps (priority order)
1. Extend the emulator study: more apps (CalDAV via DAVx5/Etar; an app with a sent list), timeouts instead of TCP resets, Doze/LMK under real memory pressure, larger n per cell; an agent run that actually resends on K-9.
2. Device study (§7.8): agent runs, real-screen VLM calibration, commercial-app survey (R3 N1c), physical phone, power-loss ledger test.
3. LP-optimal certified policy / escalation lower bound (R2 n9); asynchronous asks and ask-latency sensitivity (R1 n8).
4. Build MockBank, the injector and the on-device controller; PRISM/Storm on `artifact/prism/ghosteffect.pm`.
