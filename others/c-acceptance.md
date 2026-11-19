# C acceptance checklist (C-13)

Status: **integration evidence updated 19 November 2026; reviewer acceptance pending**.

This checklist records a fresh run from the integrated `main` after PRs #55--#64,
#72 and #74 were merged. It is not a final freeze or a claim of team acceptance;
the assigned reviewer must repeat the checks on a clean clone.

## Evidence already collected

| Gate | Evidence | Status |
|---|---|---|
| YC-C1 / C-18 | Fresh run `tmp/c13-main-20261119/RUN.json`: PASS, source tree clean, 27 completed jobs, 0 failed, 0 errors; 108 CSVs compared, 107 hashes match and only host-dependent `ledger_bench.csv` differs | Pass; archive manifest after final commit |
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
2. Freeze on 21/11 only after A, B and C are accepted. Copy the final manifest
   into `artifact/runs/2026-11-19/MANIFEST.json` and record its commit.
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

- HotCRP abstract-registration evidence is still missing from #75.
- The team lead must name the independent C reviewer. The reviewer must rerun the
  checklist on a clean clone and record the result.
- A/B still own their files and must remain available for reviewer-requested
  changes; C cannot mark team acceptance or freeze the final artifact alone.
