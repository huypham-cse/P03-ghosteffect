# C acceptance checklist (C-13)

Status: **Part C accepted by the team lead on 19 November 2026; pre-freeze integration evidence retained**.

This checklist records the integrated `main` after PRs #55--#64, #72, #74 and
#75 were merged. The run below is pre-freeze evidence; YC-F1--YC-F4 still require
the final freeze, anonymous bundle check, PDF gate and HotCRP submission.

## Evidence already collected

| Gate | Evidence | Status |
|---|---|---|
| YC-C1 / C-18 | `artifact/runs/2026-11-19/MANIFEST.json` from source `bffa2f1e`: PASS, source tree clean, 27 completed jobs, 0 failed, 0 errors; 108 CSVs compared, 107 hashes match and only host-dependent `ledger_bench.csv` differs | Pass; repeat on the final freeze commit |
| YC-C2 | Artifact renderer and generated-fragment tests pass in the integrated tree; generated fragments rebuilt by `manuscript/build.sh` | Pass; reviewer rerun required |
| YC-C4 / C-05/C-06 | Artifact suite PASS (68/68), including matched-input and vetted-baseline regression checks | Pass; reviewer rerun required |
| YC-C5 | Table captions and inline result values come from generated macros; no hard-coded renderer count captions remain | Pass by integrated source/PDF review |
| YC-C10 / C-07 | Related-work comparisons and citation audit are present; #60 is merged | Pass |
| YC-C11 / C-11 | C-owned readability: 5 `\para{}`, 10 `\emph{}`, 0 long sentences, 0 multi-semicolon paragraphs; whole paper totals 14/28/0/0 within 15/30/0/0. Report in `others/readability-c13.md` | Pass |
| YC-C12 / C-12 | Bundle instructions document the one-line command, Python 3.12, runtime and host-dependent ledger; bundle scrub/pipeline evidence from #56 is retained | Pass; final bundle must be made from freeze commit |
| YC-C13 / C-14–C-20 | Abstract, introduction, evaluation, Discussion and conclusion use agent/device macros; stale agent wording is absent and `tab_agent_arms` is input | Pass by source/PDF/manifest checks |

## Required final run

1. The integrated run and build recorded below are pre-freeze evidence. After
   approval, repeat them from a clean clone at `main`.
2. Freeze on 21/11 only after A, B and C are accepted. Repeat the pipeline from
   the final freeze commit and record its manifest separately from this run.
3. Create the anonymous bundle from that freeze, scrub it, extract it and rerun
   the pipeline. Add the artifact link to §8 and rerun the PDF gate.

## Latest integrated-main diagnostic

The integrated build exits 0 and produces a 23-page PDF. `pdftotext` finds no
`??`, `pdfinfo` exposes no author name, and scrub passes on manuscript and
testbed. The artifact suite is **68/68 PASS** and the testbed suite is **119 PASS,
3 skipped**. The largest overfull box is 1.53427pt. Conclusion is entirely on
page 12 and References starts on page 13. Whole-paper readability is 14/28/0/0,
within the 15/30/0/0 limits; C-owned readability is 5/10/0/0.

## Current blockers / owners

- HotCRP abstract registration is evidenced in #75 by submission **#3**; the
  screenshot and confirmation are attached in the [registration comment with image](https://github.com/huypham-cse/P03-ghosteffect/pull/75#issuecomment-6999044362).
- The team lead recorded acceptance of A, B and C in `team/CONTRIBUTOR_FIXED.md`.
- A/B remain owners of their files and must review any new changes that affect
  their evidence before the final freeze.
