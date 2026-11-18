# C acceptance checklist (C-13)

Status: **draft — integration pending** (18 November 2026).

This checklist records the evidence collected by Bá Nguyên. It is not a final
freeze or a claim that the whole paper has passed acceptance. The acceptance run
must be repeated from the integrated `main` after the content PRs below are merged.

## Evidence already collected

| Gate | Evidence | Status |
|---|---|---|
| YC-C1 / C-18 | `artifact/runs/2026-11-18/MANIFEST.json`; independent run from `c2b8b541` reports `source_tree_clean=true`, PASS, 25 completed jobs, 0 errors; 104 comparable CSV hashes match and only `ledger_bench.csv` differs as a host measurement | Ready for reviewer re-run |
| YC-C2 | Renderer regression suite and generated-fragment preservation tests pass on the C-04/C-06 branches | Re-run after integration |
| YC-C4 / C-05/C-06 | Matched-input renderer checks and vetted baseline checks pass on their PR branches | Re-run after integration |
| YC-C5 | Caption macros are generated from CSV; hard-coded count captions removed on #57/#58 | Review pending |
| YC-C10 / C-07 | Related-work citation audit and C-log entry pushed on #60 | Review pending |
| YC-C11 / C-11 | `readability_count.py --strict` passes C-owned sections after `2d47788`: 0 long sentences, 0 multi-semicolon paragraphs, 5 `\para{}`, 4 `\emph{}`; before/after report in `others/readability-c11.md` | Re-run after integration |
| YC-C12 / C-12 | Bundle `c12-current-1818.zip` created, extracted, scrub PASS, extracted pipeline PASS with 25/25 jobs and 0 errors; all comparable CSV hashes match and only `ledger_bench.csv` differs | Review pending |
| YC-C13 / C-14–C-20 | Abstract, introduction Results, evaluation, Discussion and conclusion use agent/device macros; #55 and #72 remain open for review | Blocked on merge/review |

## Required final run

1. Merge/rebase the content PRs #55–#60, #63, #64, #72 and #74 as approved;
   do not freeze from this draft branch.
2. From a clean integrated `main`, run `artifact/run_all.py --jobs 4`, compare
   CSV hashes, rebuild the manuscript, run all artifact tests, strict readability,
   scrub, and `make_bundle.sh`.
3. Check YC-F3: conclusion at page 12 or earlier, References at page 13 or
   earlier, no `??`, no identifying PDF metadata, and no acknowledgements.
4. Only after the reviewer signs off, mark this PR ready for review and record
   the freeze commit and artifact link.

## Current blockers / owners

- A and B owners must complete their pending readability and review fixes in
  their own files.
- The team lead must merge the accepted content PRs and assign the C reviewer;
  C-13 cannot be accepted while those PRs are separate.
- The final 22-page build still fails YC-F3's 12-page conclusion/13-page
  References gate, so this draft does not claim final acceptance.
