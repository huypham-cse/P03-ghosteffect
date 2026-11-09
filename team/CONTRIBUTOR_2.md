# Contributor 2: Artifact, Simulation and Numbers Owner

> **Project:** GhostEffect (MobiSys 2027)
> **Your role:** You own `artifact/` and everything in `manuscript/generated/`. You make every number in the paper reproducible from one command. You produce the new simulation rows the review requires and render them as tables and macros for Contributor 1. At the end you ship the **anonymized artifact**.
> **Hard deadlines:** abstract **Nov 27**, paper **Dec 4, 2026**. **Numbers freeze: Tue Dec 1.** No new runs after that.

---

## 0. Read this first (about 3 hours, day 1)

| # | File | Why |
|---|---|---|
| 1 | `artifact/README.md` | What each script produces and which table it feeds. |
| 2 | `STATUS.md` | Key results and which CSV backs them. |
| 3 | `review.md`, the table at the top (13 checks) + reviewers R2 and R3 + "Checklist dành cho tác giả" | The numerical issues you must close (Vietnamese; ask the team lead if anything is unclear). |
| 4 | `resolve.md` R03, R04, R05, R07, R10, R11, R23, R25, R26 | Decisions on clock origin, label/lag accounting, tails, equal-data rules, composed bound, δ, reproducibility, seeds. |
| 5 | `codex/code-fixes.md`, `codex/checklist.md` §1 | What was already fixed in the runner/ledger/renderer, and which CSV families exist. |
| 6 | `artifact/scripts/planner_sim.py` (top ~150 lines, `part_real`, `part_real4`), `render.py`, `render_real.py` | The code you will change. |

**Important convention (agreed with the previous owner on 2026-11-08):** numbers in the old draft are *illustrative*. A fresh run from source with recorded config and hashes is canonical. Do **not** tweak RNG or seeds to reproduce old values. Known example: `ghost-src` asks 47.01% fresh vs 47.35% archived; this is not a blocker. Report differences; do not hide them.

---

## 1. Setup

The artifact is stdlib-only Python and needs POSIX: the SIGKILL ledger test rejects native Windows. Use **Linux or WSL2 Ubuntu**.

```bash
git clone https://github.com/huypham-cse/P03-ghosteffect.git
cd P03-ghosteffect
git checkout -b c2/artifact
python3 --version                       # 3.10+; record the exact version
python3 -m unittest discover -s artifact/tests -v
python3 -m unittest discover -s testbed/tests -v   # some tests skip without Android/native env; that is expected
```

Full fresh run (about 20 min with 2 jobs; more jobs are faster if you have the cores):

```bash
python3 artifact/run_all.py --output-dir "$PWD/../ge-run-$(date +%Y%m%d-%H%M)" --jobs 4
```

The runner copies scripts and inputs into the output directory and writes a hash/exit manifest. It does not overwrite `artifact/results/` or `manuscript/`. You promote results into the repo deliberately (see §4).

Install SciPy only for the optional independent test reference: `pip install scipy`.

---

## 2. Task list

### A. Baseline (week 1)

| ID | Task | Done when |
|---|---|---|
| C2-01 | Fresh full run on Linux/WSL. Keep the run directory and its manifest. | 25 jobs exit 0; manifest saved under `artifact/runs/<date>/MANIFEST.json` (small files only, no huge logs). |
| C2-02 | **Diff report** between the fresh run and the committed `artifact/results/*.csv` + `manuscript/generated/macros.tex`. List every macro whose rendered value changes. | `team/diff-<date>.md` merged; C1 notified of every changed macro used in the body. |
| C2-03 | Promote the fresh results: copy CSVs into `artifact/results/`, run `python3 artifact/scripts/render.py` to regenerate `manuscript/generated/`, and make sure `manuscript/build.sh` still compiles. | One PR titled `[C2-03] fresh canonical run <date>` with the manifest hash in the description. |

### B. New rows and tables the review requires (weeks 1–2)

Most inputs already exist as `artifact/results/planner_real4_*.csv` (16 REAL4 tags). Your job is to (i) make sure they come from the fresh run, (ii) render them into **body tables and macros**, and (iii) add what is missing.

| ID | Task | Source / code | Output for C1 |
|---|---|---|---|
| C2-04 | **Lag table size and tied budgets.** Table 4 must state `N_LAG = 20,000` bootstrap draws. Add rows where lag samples per class = labels (2,000; 5,000) for product and joint on Element. | `planner_real4_lag2k.csv`, `lag5k.csv` (+ `lag10k`, `lag20k`, `boot10k` for the appendix) | New rows in Table 4 (`tab_real.tex` or a new `tab_real_lag.tex`), macros `\RsimLagTwoK...`, `\RsimLagFiveK...` |
| C2-05 | **Unlogged lag tail at 5k labels.** Joint `P_v` and CP upper bound at 5,000 labels with the 2.9225% tail (the review quotes 2.01% / CP 2.32 / 13.73% asks; confirm from the fresh run). Also the tied variant. | `tail5.csv`, `tail5tied.csv` | Row + macros |
| C2-06 | **Vetted rules, equal data.** Vetted rule chosen from the predefined family with the same fault-injected labels and lag information as joint; frozen before evaluation. Element, K-9, K-9+Sent. | `vet.csv`, `vetk9.csv`, `vetk9sent.csv`; check `part_real4` uses the same label budget as joint | Rows in Table 4 + macros |
| C2-07 | **Composed dup/loss bound.** `planner_sim.py` does not output conditional asks today (`resolve.md` R10). Add per-row `q1 = P(ask | X=1)`, `q0 = P(ask | X=0)` and final `dup`, `loss`, `unresolved` to the `real` part. Compute `min(1, α + q1·ε_u)` and `min(1, β + q0·ε_u)` with `ε_u = 0.05` (default user error) and `r1 = r0 = 0` inside the simulator. Zero denominator → `N/A`, never 0. | `planner_sim.py` `part_real`, new columns; renderer | Two columns (or a small table) for the product/joint/vetted rows + macros |
| C2-08 | **δ and unknown class.** Check `planner_sim.py` around the keyed/unknown fallback (~L1465–1471) and `testbed/calibration.py`. Does δ divide by K_total including classes? If the unknown-class path uses 4K bounds with δ = min(α,β)/(10K), fix the code, re-run the affected tags (`unknown`, `mixkeyed`, `main`) and tell C1 the exact formula. | code + rerun | One-paragraph note to C1 + changed macros |
| C2-09 | **Stale-screen counts.** From `artifact/results/real/SUMMARY.md`, `campaign2/pilot_*.csv` and the logs, count (a) forwarder stale-tree events and (b) stale-digest wrong reads on a validated screen. Read-only on raw data. | raw logs | Macros `\RealStaleTree`, `\RealStaleDigest` + a 3-line note on the denominator |
| C2-10 | **Agent experiment rendering.** When C3 delivers `artifact/results/real/agent/*.csv` + `SUMMARY.md`, write `render_agent.py` (or extend `render_real.py`): one small table (trials scheduled / valid / reached commit / agent re-sent / duplicates at backend / asked or abandoned / median wall-clock) and macros. Wilson 95% CIs for proportions. | C3 schema (see CONTRIBUTOR_3.md §4) | `generated/tab_agent.tex` + `\Agent*` macros |
| C2-11 | **Element lag dot plot.** All Element lag points by fault class (none / kill -9 / force-stop / net cut), with min/median/max marked. pgfplots or a PDF via matplotlib, kept small (one column, ≤ 4 cm high). | `campaign2/c2_element_lag.csv` | `generated/fig_lag_dots.tex` + Table 3b min/med/max macros |
| C2-13 | **Clock-origin rows** for the body: wrong origin (wait from `ISSUED` while the table is recovery-to-visible) vs correct origin (`r_e + w`), 5 s and 15 s downtime, product and joint. | `down5`, `down15`, `t0down5`, `t0down15` | Small table or 4 macros for §7 |
| C2-14 | **Seed variance** (nice to have): 5 seeds for the headline rows of Table 2 (product, joint, rules, Thm-4.8-only) and Table 4 (Element product/joint/vetted). Report mean ± sd or range. | rerun with seeds | Macros / footnote |
| C2-15 | **Stress count:** number of stress rows where product exceeds the budget (CP upper > α), to sit next to "rules over in 3/14". | `planner_stress.part*.csv` | One macro |

### C. Artifact for reviewers (weeks 3–4)

| ID | Task | Done when |
|---|---|---|
| C2-12 | **Anonymized artifact.** Build `ghosteffect-artifact.zip` containing `artifact/` (scripts, tests, results incl. `real/`), `testbed/` (code + tests + `*.example.json`, **no** `runs/`, no `*.local.json`), a top-level README (English) with the one-command reproduction, Python version, expected runtime (~20 min), and which outputs are host-dependent (ledger timings). **Exclude** `tmp/`, `codex/`, `review.md`, `resolve.md`, `report.md`, `runtime/`, `.git`. | Scrub check passes (below); uploaded to an anonymous host (anonymous.4open.science from a repo you create for this, or an anonymous Zenodo/OSF link); link given to C1 by **Dec 1**. |
| C2-16 | **Scrub check** script `team/scrub_check.sh`: grep the bundle for `/Users/`, `xuanbach`, `lexuanbach`, `huypham`, `phamhuynh`, `bachdylan`, `gmail.com`, `Gia Huy`, `D:\\`, `C:\\Users`, Vietnamese-only docs. Fail if any hit. Also run it on `manuscript/` for C1. | Script in repo; output pasted in the C2-12 PR. |
| C2-17 | Make `artifact/README.md` English and accurate: the runner, Python version, time, what is simulation vs measurement, and the "illustrative vs canonical" note rephrased neutrally ("numbers are regenerated; host timings vary"). | Merged |

---

## 3. Timeline

| Week | Dates | Focus | Milestone |
|---|---|---|---|
| W1 | Nov 9–15 | C2-01, C2-02, C2-03. Start C2-07 (code change) and C2-08 (check). | **Sun Nov 15:** fresh canonical run merged; diff report sent to C1 |
| W2 | Nov 16–22 | C2-04, C2-05, C2-06, C2-07, C2-08, C2-11, C2-13, C2-15 rendered as tables/macros C1 can `\input`. | **Sun Nov 22:** all simulation tables/macros for the new §7 in `main` |
| W3 | Nov 23–29 | C2-09, C2-10 (as soon as C3 delivers, target Nov 26), C2-14, start C2-12/16/17. | **Fri Nov 27:** agent table rendered |
| W4 | Nov 30–Dec 4 | Final clean run from `main` (C2-01 again) → **numbers freeze Tue Dec 1**. Artifact upload, scrub. | **Tue Dec 1:** frozen; anonymized link delivered |

---

## 4. Rules

- **Branch** `c2/artifact`; PRs to `main` with `[C2-xx]` titles. Keep PRs small: one table or feature each.
- **You own:** `artifact/**`, `manuscript/generated/**`, `manuscript/build.sh`, `team/diff-*.md`, `team/scrub_check.sh`. Do not edit `manuscript/sections/*` (C1) or `testbed/*` (C3). If a renderer change needs a new `\input` in a section, tell C1.
- **Raw data is read-only:** never modify `artifact/results/real/**` except to *add* `real/agent/` content delivered by C3.
- **Provenance:** every new CSV has a header comment or sidecar `*.meta.json` with command, git commit, seed, python version and date. Every macro name says what it is (prefix `\Rsim` = measured-parameter simulation, `\Sim` = model-based, `\Real` = emulator measurement, `\Agent` = LLM-agent run).
- **No outcome-driven tuning.** Do not change a seed, a rule family or a label budget after seeing a result to make GhostEffect look better. If a row comes out unfavourable, it goes in the paper; tell C1.
- **Macro requests from C1** arrive as GitHub issues `[macro] ...`. Answer within 24 h (deliver or explain why not).
- Weekly sync Sunday evening.

---

## 5. Tracker

Status: `todo` / `doing` / `review` / `done` / `blocked(<reason>)`.

| ID | Short name | Due | Status | Notes / PR |
|---|---|---|---|---|
| C2-01 | Fresh full run + manifest | Nov 12 | todo | |
| C2-02 | Diff report vs committed results | Nov 14 | todo | |
| C2-03 | Promote fresh results, rebuild PDF | Nov 15 | todo | |
| C2-04 | Lag table size + tied 2k/5k rows | Nov 19 | todo | |
| C2-05 | Joint tail at 5k | Nov 19 | todo | |
| C2-06 | Vetted rules equal-data rows | Nov 20 | todo | |
| C2-07 | q1/q0 + composed bound | Nov 21 | todo | code change in planner_sim |
| C2-08 | δ / unknown-class check (+ fix) | Nov 18 | todo | tell C1 |
| C2-09 | Stale-screen counts | Nov 25 | todo | |
| C2-10 | Agent table + macros | Nov 27 | todo | needs C3-10 |
| C2-11 | Element lag dot plot | Nov 22 | todo | |
| C2-12 | Anonymized artifact uploaded | Dec 1 | todo | |
| C2-13 | Clock-origin rows | Nov 20 | todo | |
| C2-14 | Seed variance (nice to have) | Nov 28 | todo | |
| C2-15 | Product stress-failure count | Nov 20 | todo | |
| C2-16 | Scrub check script | Nov 29 | todo | |
| C2-17 | English artifact README | Nov 30 | todo | |
| FREEZE | Final clean run from main | Dec 1 | todo | |
