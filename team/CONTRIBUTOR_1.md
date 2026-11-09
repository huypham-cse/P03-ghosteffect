# Contributor 1: Manuscript Owner

> **Project:** GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents (MobiSys 2027)
> **Your role:** You own `manuscript/`. You turn the current draft into the submission version. That means fixing every blocking issue in the internal review, restructuring the paper, and writing in the new results that Contributors 2 and 3 produce.
> **Hard deadlines:** abstract registration **Fri Nov 27, 2026**, full paper **Fri Dec 4, 2026** (MobiSys 2027 dates from `STATUS.md`; confirm the exact time and time zone on the CFP page on day 1).
> **Team lead decisions are final unless you raise a blocker in the weekly sync.**

---

## 0. Read this first (about 3 hours, day 1)

Read these in order. Do not skip any of them; everything below assumes you have.

| # | File | Why |
|---|---|---|
| 1 | `manuscript/main.pdf` | The current draft (20 pages, body ends p. 12). Read it end to end once. |
| 2 | `STATUS.md` | Round-3 state, key numbers, known weaknesses. The "Previous state" section is superseded where it conflicts. |
| 3 | `review.md` | **Internal mock review packet** (Vietnamese) with 4 reviewers, a meta-review and an author checklist. This is your main to-do source. It is not a real MobiSys review; the paper is a **fresh submission**, so there is no response letter. |
| 4 | `resolve.md` §1 and R01–R14 | The decisions already taken for each review point (clock origin, lag table size, composed bound, delta, nonce, recommended mode). Follow them unless this file says otherwise. |
| 5 | `others/notes.md` | Number ledger: which macro/CSV backs each claim. |
| 6 | `manuscript/generated/macros.tex` | Every number in the paper is a macro produced by `artifact/scripts/render.py` / `render_real.py`. |

The `codex/*.md` files describe a long-term 1,090-episode, 5-framework, H100 study. **That study is out of scope for this submission** (see §2). Do not promise it in the paper. At most, mention it in one sentence of future work.

---

## 1. Setup on your machine

```bash
git clone https://github.com/huypham-cse/P03-ghosteffect.git
cd P03-ghosteffect
git checkout -b c1/manuscript
```

You need a LaTeX distribution with `acmart`, `pgfplots`, `tikz` and `algorithmicx`:
- Linux/WSL: `sudo apt install texlive-full` (simplest), or TeX Live 2023+.
- macOS: MacTeX.
- Windows: TeX Live or MiKTeX. Run `build.sh` from Git Bash or WSL.
- Python 3.10+ (stdlib only) is needed because `build.sh` runs `render.py` first.

Build:

```bash
cd manuscript
sh build.sh          # render generated/*.tex from artifact/results, then pdflatex/bibtex/pdflatex x2
```

The build fails on any LaTeX error or undefined reference/citation. That is intended; keep it green.

**Rules for numbers (strict):**
1. Never type a result number into a `.tex` file by hand. Use the macro. If a number you need has no macro, ask Contributor 2 to add it to `render.py` / `render_real.py`.
2. Never edit `manuscript/generated/*` by hand. Contributor 2 owns those files; they are regenerated.
3. Every number in prose says what kind it is in the same sentence: *measured on the emulator*, *model-based simulation*, *simulation with measured parameters*, *exact computation*, or *LLM-agent run*. (Review style checklist item 3.)

---

## 2. Scope decision for this submission (team lead)

We fix what the review marks as **blocking** and most of what it marks as **strongly recommended**. We do **not** run the P01–P40 / 5-framework / C-guard study from `codex/`.

The paper's new evidence for this submission:
- **New measurement:** one LLM agent (M3A from AndroidWorld) on ≥10 valid interrupted K-9 sends. Contributor 3 runs it. This resolves the "no agent was run" weakness, which all reviewers raised.
- **New simulation rows:** clock origin, lag tables tied to the label budget, tail at 5k labels, vetted rules on the same labels, composed dup/loss bound, seed variance. Contributor 2 produces them; most already exist as `planner_real4_*.csv`.
- **Measured label cost:** wall-clock time per fault-injected trial, from Contributor 3's runs.

If the agent experiment fails (for example, the agent never re-sends), we report that honestly and reframe §2.3 as the review asks. The section must not depend on a particular outcome.

---

## 3. Task list

IDs are referenced in commits and PR titles (`[C1-07] ...`). "Dep" means you need input from another contributor first.

### A. Blocking fixes (from review.md, "Bắt buộc")

| ID | Task | Where | Dep | Done when |
|---|---|---|---|---|
| C1-01 | **Clock origin.** Define the observable recovery origin `r_e` per fault class: agent death → `ISSUED`; app death → confirmed relaunch intent; network cut → restore; combined → the later of the two. Define `T_c = max(0, t_visible − r_e)` and `G_c(w)`. Restate Eq. (2) and `CertifiedWait` so the deadline is `r_e + w_c` (equivalently `t0 + d_e + w_c`). Unknown origin or class → conservative max over classes, or ASK. Follow `resolve.md` R03 exactly. | §3 Model, §4.2, Alg. 1 (§5.4), App. A | — | Text, algorithm and proof are consistent. One sentence in §7 cites the wrong-origin rows (5 s / 15 s downtime) as macros. |
| C1-02 | **Lag table size.** State that the Table 4 lag tables use `N_LAG = 20,000` bootstrap draws from measured trials, not unique measurements. Add the tied rows (lag samples = label budget, 2k and 5k). Rewrite every "12.7% asks (5,000 labels per class)" so it is accurate. | Table 4, abstract, §1, §7, §10 | C2-04 | No sentence implies 5,000 labels alone give 12.7%. |
| C1-03 | **Joint under the unlogged lag tail at 5k labels.** Report joint `P_v` (it exceeds the budget). Replace "joint still meets the budget" with "joint meets the budget only while it asks enough". | §7 (Element measured-parameter text), abstract | C2-05 | The claim matches `planner_real4_tail5.csv`. |
| C1-04 | **Vetted rules baseline.** Add the vetted-rule rows (same fault-injected labels as GhostEffect) for Element, K-9 and K-9+Sent to Table 4. Rewrite the "rules retry 28.91–65.85%" claims; remove them from the abstract. | Table 4, §7.1, §7, abstract, §1, §10 | C2-06 | The rules comparison is equal-data. |
| C1-05 | **LLM agent section.** Write the agent experiment: setup, model, fault, n, resend count, duplicates, abandon/ask, and wall-clock. Replace the planned-harness paragraph (§7.8 / §6) with it. If 0 re-sends, say so and retitle §2.3. | New subsection in §7 (about 0.3 pages), §1 contributions, §2.3 | C3-10, C2-10 | All numbers are macros from `artifact/results/real/agent/`. |
| C1-06 | **One recommended mode** everywhere: *product when A2 is structurally justified; joint otherwise; ASK when nothing certifies; on G2 apps, do not retry.* Make the abstract, Fig. 1, the bold row in Table 2, §7 and §10 agree. Relabel the Fig. 1 G2 branch to the mode it actually depicts. | abstract, Fig. 1 (`figures/fig1.tex`), Table 2, §7, §10 | — | `grep -n "joint\|product" sections/*.tex` reads consistently. |
| C1-07 | **Nonce field.** The default is fields invisible to the counterparty. State that the K-9 measurements used the **subject** (visible to the recipient) on test accounts with explicit opt-in. Fix Fig. 1(b) and Table 8 (`tab-apps.tex`) to match. | §5.2, Fig. 1, `tab-apps.tex`, §8 ethics | — | No contradiction remains. |
| C1-08 | **Table 4 caption.** Say that calibration and test draw from the same measured distribution; that Element's committed-side family error rates are measured as 0 (0/99, 0/101); and therefore what Table 4 tests (the certification machinery and the price in asks) and what it does not (reader errors on real screens). | Table 4 caption + 2 sentences in §7 | — | Answers reviewer R3 weakness 1. |
| C1-09 | **Composed error bound.** Add `P(dup | X=1) ≤ min(1, α + q1·ε1 + r1)` and `P(loss | X=0) ≤ min(1, β + q0·ε0 + r0)` with definitions (`resolve.md` R10). Evaluate it for the product and joint rows of Table 4. Say which quantity a deployer should read. | §3 or §4.1, §7 | C2-07 | Values come from macros. Do not use the illustrative `0.05 × 72.9%`. |
| C1-10 | **Artifact availability** paragraph with the anonymized link. | §8 | C2-12 | The link works from a private browser window. |

### B. Strongly recommended ("Rất nên làm")

| ID | Task | Where | Dep |
|---|---|---|---|
| C1-11 | **Restructure §7.** Order: 7.1 emulator measurements (Table 3) → 7.2 agent experiment → 7.3 measured-parameter simulation (Table 4) → 7.4 model-based simulation (Table 2 cut to redo, Thm-4.8-only, always-ask, rules, vetted rules, product, joint) → 7.5 stress + population (one paragraph; Tables 6–7 stay in the appendix) → 7.6 mechanisms (one paragraph). Move RQ1–RQ2 to the appendix with a one-sentence pointer. Explain simulation vs. measurement once, early, in 3 sentences. | §7 | C2 tables |
| C1-12 | **Abstract ≤ 200 words, ≤ 4 numbers.** Start from the 197-word draft in review.md §3(a), translated back to English and updated with the agent result. No two-decimal simulation numbers. | `00-abstract.tex` | C1-05 |
| C1-13 | **Shorten §4 to about 1.5 pages.** Thm 4.1 in 3 lines plus a "classical parts" note. Keep Prop 4.4 and Thm 4.8 in full. Move Prop 4.3, Lemma 4.5, Lemma 4.6(iii), Lemma 4.7 and the saga allocation to App. A with pointers. Use the space for a step-by-step Algorithm 1 walk-through (one K-9 send and one Element send) in §5.4. | §4, §5.4, App. A | — |
| C1-14 | **Label cost.** Replace "about 15 s per label" with the measured trial wall-clock, and report device-hours for 5,000 labels × class × outcome on one app version. | §5.3 | C3-11 |
| C1-15 | **Unknown-class union bound.** With 4 classes the union has 4K bounds. State that `δ` is divided by the class count (or show the code does this) and keep it consistent with `planner_sim.py`. Coordinate with C2-08. | §4.3, Lemma 4.6 | C2-08 |
| C1-16 | **Stale-screen events.** Add the two measured stale-screen events (forwarder returned a stale tree; stale digest in a pilot), with counts. | §7.1 | C2-09 |
| C1-17 | **Table 3b.** Replace p90 (n = 20) with min/median/max, or reference the dot plot of all Element lags by class. | Table 3b | C2-11 |
| C1-18 | Rename the dedup horizon `D` (it clashes with the KL terms `D0`/`D1`); for example `H_dedup`. | §4.4, everywhere | — |
| C1-19 | Move Table 5 (positioning) into the body (§2), and Table 1 (sample sizes) to the appendix. | §2, §5.3 | — |
| C1-20 | Count the stress rows where product exceeds the budget, next to "rules exceed in 3/14". | §7.5 | C2 macro |

### C. Correctness and clarity details (from the reviewers' detailed comments)

| ID | Task |
|---|---|
| C1-21 | §5.3: hop 1 reads the Outbox **screen via the accessibility tree** (uiautomator dumps), not the app's local DB. |
| C1-22 | §2.1: qualify "foreground apps are almost never killed". Element survives `am kill` 13/13 because of its sync service; app death may be rare for G2 apps with foreground sync while agent death is common. |
| C1-23 | §7: ANR-lost Element trials. If they had committed, say they are censored observations; say how they were treated. |
| C1-24 | §7 / A1: the Element withhold case shows "Sent" via the `/sync` echo before the client's 70 s timeout. State whether A1 and the hop-1 conditions cover this path. |
| C1-25 | Table 8 (`tab-apps.tex`): mark each row **measured** or **planned** in a column, not only in the caption. |
| C1-26 | §6: report host load average (16–38) and dump time (~2 s) as a lower bound on all measured lags. |
| C1-27 | Theory: A1 must state `T` is independent of reads given `X` (used by Thm 4.1(c,d)). Prop 4.3: `P` is reset exactly once at hand-over, and `R(τ)` includes the post-hand-over allocation. |
| C1-28 | Prop A.1 / saga: say that the value is safety via the union bound, not optimality (KKT is sometimes worse than uniform). |
| C1-29 | Thm 4.8 / H3: Element's positive window (20–100 ms) is shorter than one read (2 s dump), so Element has no hop-1 family. Say this next to H3. |
| C1-30 | Prop 4.4: state the pilot size used to fix the score function, that it is separate from the `n` holdout, and the size used in the simulator (500 pilot + 4,500 holdout at "5,000", per `resolve.md` R04). |
| C1-31 | §1 "why existing solutions don't apply": split the three-results-in-one-citation sentence. |
| C1-32 | §9: one contrast sentence each for LIMBO, Agent libOS and VeriGUI. Optionally cite Gray & Reuter 1992 and Bailis et al. VLDB 2015. **Verify each reference against the real source before adding it to `references.bib`.** |
| C1-33 | §10: three sentences of lessons, no numbers (review §4 "Mục 10"). |
| C1-34 | Prose: G2 → "apps that retry idempotently" in prose (keep G2 in theorems); hop 1 → "Outbox evidence" in prose; choose one of "ask"/"escalate" and use it everywhere. |

### D. Readability pass (do it last, after the numbers freeze)

Apply review.md §5's 15-point style checklist. Measurable targets:
- 0 sentences over 45 words (today 31); aim for no sentence over 35.
- At most 1 semicolon per paragraph (today 151 in total).
- `\para{}` lead-ins ≤ 15 (today 43); `\emph{}` ≤ 30 (today 94).
- Each term is defined before first use in its section.
- Intro opens with the K-9 story (review §3(b)) and the one-sentence description (§3(d)).

Re-run the counting commands from review.md §2 and paste the before/after counts into your PR description.

### E. Final gates (owned by C1)

| ID | Gate |
|---|---|
| C1-40 | Body ends on page 12. References and appendix are unlimited, but check the CFP. |
| C1-41 | 0 LaTeX errors, 0 undefined refs/cites; no overfull box > 10 pt. |
| C1-42 | Anonymity: no author names, no `/Users/...` paths, no GitHub user names, no acknowledgements; anonymous artifact link only. Check PDF metadata (`pdfinfo main.pdf`). |
| C1-43 | Every `\cite` resolves to a verified bib entry. Update `others/citation-audit.md` if it exists; otherwise create a short audit list. |
| C1-44 | Final PDF is uploaded to HotCRP **by Dec 3** (one day of buffer). |

---

## 4. Timeline

| Week | Dates | Your focus | Milestone |
|---|---|---|---|
| W1 | Nov 9–15 | Read everything (§0). Do the number-independent fixes: C1-06, C1-07, C1-13 (theory moves), C1-18, C1-19, C1-21–C1-34. Draft C1-01 text. Agree the §7 outline (C1-11) with the team. | **Sun Nov 15:** outline of the new §7 + list of every macro you need, sent to C2 |
| W2 | Nov 16–22 | C1-01, C1-08, C1-09 (theory), C1-15. Integrate C2's new tables (C1-02, C1-03, C1-04, C1-17, C1-20). Write the C1-05 skeleton with placeholder macros. | **Sun Nov 22:** full draft compiles with all new simulation rows |
| W3 | Nov 23–29 | Abstract (C1-12). Fill in the agent section once C3 delivers. C1-14, C1-16. | **Wed Nov 25:** abstract frozen. **Fri Nov 27:** abstract + title registered |
| W4 | Nov 30–Dec 4 | Numbers freeze **Tue Dec 1** (no new runs after this). Readability pass (D). Final gates (E). C1-10. | **Thu Dec 3:** submitted. Dec 4 is buffer only |

---

## 5. How we work together

- **Branch:** `c1/manuscript`. Open a PR to `main` at least twice a week. The team lead merges. Rebase on `main` before each PR, because C2 changes `manuscript/generated/`.
- **File ownership:** you own `manuscript/sections/*`, `manuscript/figures/*`, `manuscript/main.tex`, `manuscript/references.bib` and `STATUS.md`. Do not edit `artifact/`, `testbed/` or `manuscript/generated/`. Ask the owner instead.
- **Requesting a number:** open a GitHub issue titled `[macro] <name>` with the exact meaning, source CSV/row and format (for example `%.1f`). Assign it to Contributor 2.
- **Weekly sync:** Sunday evening, 30 minutes. Each person reports their tracker. Blockers are raised at sync or immediately in the team chat.
- **Commit messages:** `[C1-xx] short summary`.

---

## 6. Tracker

Update this table in every PR. Status values: `todo` / `doing` / `review` / `done` / `blocked(<reason>)`.

| ID | Short name | Due | Status | Notes / PR |
|---|---|---|---|---|
| C1-01 | Clock origin (model, Eq. 2, Alg. 1, proof) | Nov 20 | todo | |
| C1-02 | Lag table size + tied rows | Nov 22 | todo | needs C2-04 |
| C1-03 | Joint tail at 5k | Nov 22 | todo | needs C2-05 |
| C1-04 | Vetted rules in Table 4 | Nov 22 | todo | needs C2-06 |
| C1-05 | LLM agent subsection | Nov 29 | todo | needs C3-10, C2-10 |
| C1-06 | One recommended mode | Nov 15 | todo | |
| C1-07 | Nonce field consistency | Nov 15 | todo | |
| C1-08 | Table 4 caption: what it tests | Nov 20 | todo | |
| C1-09 | Composed dup/loss bound | Nov 22 | todo | needs C2-07 |
| C1-10 | Artifact link | Dec 2 | todo | needs C2-12 |
| C1-11 | Restructure §7 | Nov 22 | todo | outline by Nov 15 |
| C1-12 | Abstract ≤ 200 words | Nov 25 | todo | |
| C1-13 | Shorten §4, Alg. 1 walk-through | Nov 18 | todo | |
| C1-14 | Measured label cost | Nov 28 | todo | needs C3-11 |
| C1-15 | δ and class count | Nov 20 | todo | with C2-08 |
| C1-16 | Stale-screen events | Nov 26 | todo | needs C2-09 |
| C1-17 | Table 3b min/med/max or dot plot | Nov 22 | todo | needs C2-11 |
| C1-18 | Rename dedup horizon D | Nov 15 | todo | |
| C1-19 | Move Table 5 in, Table 1 out | Nov 15 | todo | |
| C1-20 | Count product stress failures | Nov 22 | todo | |
| C1-21–34 | Detailed correctness/clarity items | Nov 18 | todo | one PR per 3–4 items |
| D | Readability pass | Dec 2 | todo | paste before/after counts |
| C1-40–44 | Final gates + submission | Dec 3 | todo | |
