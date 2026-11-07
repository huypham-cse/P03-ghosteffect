# GhostEffect artifact

Everything here is **stdlib-only Python 3** (sqlite3 included) and **seeded**. `./run_all.sh` regenerates every result and every
table/figure/macro the paper inputs (`../manuscript/generated/`); `../manuscript/build.sh` compiles. Nothing in the paper is hand-typed data.
An anonymized copy of this artifact will be provided to reviewers (paper §8, "Data and artifact availability").

| Script | Paper element | Kind |
|---|---|---|
| `scripts/ge_core.py` | oracle, SPRT, exact DTMC DP, bounds, Clopper–Pearson, McNemar, Holm | library |
| `scripts/ledger.py` | write-ahead effect ledger (SQLite WAL, `synchronous=FULL`) | system component |
| `scripts/bench_ledger.py` | §6 ledger latency, bytes/effect, SIGKILL write-ordering test | **host measurement** (timings vary by machine/run) |
| `scripts/sim_sprt.py` | App. Fig. `fig:sprt`, Tables `tab:sprt`, `tab:calib`, `tab:corr` | exact computation + model-based simulation |
| `scripts/sim_impossibility.py` | App. Fig. `fig:floor`, Table `tab:lag` (certified waits) | exact computation + simulation |
| `scripts/sim_saga.py` | App. Table `tab:saga`, saga macros (Prop. 4.9) | exact computation |
| `scripts/sim_nonce.py` | App. Table `tab:nonce` (Lemma 4.7; edit-distance matching; OCR with sub/ins/del) | analytic + simulation |
| `scripts/planner_sim.py` | Tables `tab:planner`, `tab:stress`, `tab:pop`, `tab:sens`; Fig. `fig:pareto`; class/share/reason/decomposition/drift macros | **model-based simulation** (not device data) |
| `scripts/sample_size.py` | Table `tab:nsize` (calibration sizes; exact CP) | exact computation |
| `scripts/markov_planner.py` | earlier (re-read) planner, exact DTMC vs MC; writes `prism/*.pm` | sanity check only; not in the paper |
| `scripts/render.py` | all `generated/*.tex` and `macros.tex` | generator |

## The simulator (`planner_sim.py`)
- App profiles (`APPS`), faults, interruption points, lags: top of the file. Generative scenarios (`SCEN`): `default` is the main world (persistent nonce misses,
  within-view VLM correlation 0.6, cross-view 0.1, persistent hop-1/digest failures, Monitor misreads 1% of terminal states, user wrong on 5% of asks).
  Stress scenarios: `r1`, `r1+persist`, `cross0.3`, `lagtail`, `lagtail-cal`, `g2break`, `g2nodedup`, `doze-unaware`, `doze-aware`, `common0.5`, `mon0.05`, `user0.2`,
  `combined`; calibration-population scenarios: `iworld-passive`, `iworld-fault` (interrupted world: stale history, optimistic entries, heavy lags) and `cm*-fault`
  (common-mode stale history, fault-injected labels).
- Policies: baselines (redo, ckpt, atomix, atomix-durable, verify, key, key-ask, always-ask, nonce-ask, maj3-ask), the **same-evidence rule cascades** (`rules`,
  `rules-lenient`), `ghost-v1` (earlier re-read SPRT), and three certification modes of the revised planner: `ghost` (per-family calibration, product
  certification, Prop. 4.3, assumes A2), `ghost-src` (evidence-source families: hop-1 × jointly calibrated history readers), `ghost-joint` (joint calibration
  of the cascade's stopping region by fixed-sequence testing, Prop. 4.4, no cross-family assumption); plus ablations.
- Lag composition (Eq. `eq:lagsplit`): `q_h G(w1) <= a_lag/2` and `G(w0) <= a_lag/2` (all of `a_lag` to `w0` without a hop-1 family). Stuck (pending > 120 s) and
  failed entries are handed to the end-to-end path with the wait measured from t0. The Monitor is fallible; a hop-1 "committed" verdict enters the declare-side bound
  and is corroborated end to end after acknowledgement unless it certifies alone.
- Calibration: 2,000 whole effects per app and outcome, every family read once per view on each; `cal_pop='passive'` (uninterrupted effects) or `'fault'`
  (fault-injected, interrupted population). δ = α/(10K) with K = 11 (product), 8 (source), 5 (joint). Lag tables: 20,000 samples.
- Parts (run in parallel by `run_all.sh`): `main`, `stress0/6`..`stress5/6`, `sweep`, `user`, `sens`, `ncal` (calibration size and version drift with/without a
  200-effect shift test), `decomp` (over-delivery decomposition), `share` (which families certify), `real` (re-run with measured parameters if present).

## Emulator measurements (`results/real/`)
`results/real/` (raw per-trial CSVs, logs, SUMMARY.md) is written by the separate emulator testbed (`papers/shared-android/`) and is **read-only** here.
Round 3 uses **campaign 2** (`results/real/campaign2/`: screen-validating reader, Element 101 trials + 6 timeout cells, K-9 with and without an IMAP Sent folder,
Etar+DAVx5+Radicale, Synapse txnId horizon). Campaign 1 (`results/real/*.csv`) supplies the appendix table, kill semantics and the ledger test.
* `real_params.py` recomputes the simulator's measured parameters from the campaign-2 CSVs (per-fault-class lag samples with lag-blind first reads, late
  no-observation rate, K-9 failed state and Sent-folder APPEND lag), asserts the facts the mapping relies on, and writes `results/real/params.csv`
  (`name,value,provenance`; assumptions are labelled).
* `planner_sim.py real [tags...]` runs the measured-parameter simulation (`results/planner_real.csv`): profiles `element` (no hop-1 family: its indicator is
  not lag-free), `k9`, `k9sent`; rows `main` (fault-injected, fault-class-keyed), `pooled`, `mixlab` (lab fault mix != deployment), `mixkeyed`, `unknown`
  (class never known: max-over-classes / intersection fallback), `passive`, `tail`/`tailcal` (lag tail at the 95% bound of 0/101 censored, unlogged/logged),
  `five` (5,000 labels per class), `k9*`.
* `render_real.py` (exec'd by `render.py`) renders Table 3 (campaign 2), the campaign-1 appendix table and Table 4, plus every `\Real*`/`\Rsim*` macro.

## Round-3 changes to the simulator
* `ghost-src`: fixed the source-family union bound, Q(t/q_h) = 1 for t >= q_h (hop-1 alone acts). The old table under-counted B(tau) on the **declare**
  side in the default world, so every `ghost-src` row changed slightly (e.g. default world asks 47.0% -> 47.4%, L_v 0.054% -> 0.018%); all other rows are
  byte-identical to round 2.
* New baselines: `g2-only` (Theorem 4.8 alone: never retry; G2 app with an acknowledged hop-1 entry = done, else ask) and the rule family
  `rules-w{5,10,30,60}-{all,novlm,two}` (part `rulesweep`, `results/planner_rules_sweep.csv`).
* Fault-class-keyed calibration (`keyed='all'`), lab fault mix (`cal_faults`), unknown-class fallback (`class_known`), no-observation reads (bot).
* `sample_size.py`: product zero-event column and joint median-case column at a true region rate alpha_test/4.

`retired/illustrative.py` and `retired/illustrative_results/` are the round-1 † projections (seeded draws around target rates). They are **not** measurements and are
**not** used by the paper. They are kept only so the change can be audited.

## Not done
- PRISM/Storm on `prism/ghosteffect.pm` (no install in the build environment).
- Device harness (AndroidWorld fault injector, on-device controller), power-loss ledger test on a device: see paper §6 and §7.

Reproducibility: `bench_ledger.py` timing columns change from run to run; every other CSV and every generated `.tex` file is byte-identical across runs.
