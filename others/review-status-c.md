# Review status for C PRs

Checked against the integrated `main` and PR #75 on 19 November 2026. PRs
#55--#64, #72 and #74 are merged; this matrix records their integrated status.

| PR | Addressed by current head | Still missing / dependency |
|---|---|---|
| #55 | Merged. Agent numbers, conditional recommendation, device scope and `AgentRules` macros are present in `main`. | Recheck common gates on the final freeze. |
| #56 | Merged. Bundle README, clean-tree guard, host-dependent ledger note and extracted scrub/pipeline evidence are present. | Recreate from the final freeze commit. |
| #57 | Merged. Caption counts and late-family consistency checks are integrated. | Recheck renderer and page gate on freeze. |
| #58 | Merged. Seed metadata, renderer contract and Element outlier explanation are integrated. | Recheck on freeze. |
| #59 | Merged. Vetted baseline, appendix references, device anchor and main-table row are integrated. | Recheck page gate on freeze. |
| #60 | Merged. Related-work comparisons and citation audit are integrated; C-13 further shortened C-owned prose while retaining required comparisons. | Recheck citations on freeze. |
| #63 | Merged. Final integrated manifest at `artifact/runs/2026-11-19/MANIFEST.json` reports 27 jobs PASS, 0 errors and 107/108 comparable CSV hashes matching; only `ledger_bench.csv` is host-dependent. | Repeat from final freeze commit. |

## Evidence recorded separately

- C-10/#74: merged; readability pseudocode regression test passes.
- C-11/#64: merged after the lead's readability redo; C-13 reports 5/10/0/0 and the page gate now places Conclusion on page 12.
- C-20/#72: merged; physical-phone and emulator macros are integrated.
- C-13/#75: open as `[C] Nghiệm thu`; independent reviewer requested, HotCRP receipt pending, and final freeze waits for A/B/C acceptance.
