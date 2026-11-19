# C-13 readability and page-gate report

Run date: 2026-11-19. The baseline is integrated `main` at `4d50067`, before
the C-13 prose compaction. Counts use `team/readability_count.py` and exclude
generated fragments.

| Scope | Baseline `4d50067` | C-13 result | Limit |
|---|---:|---:|---:|
| C-owned sections: `para` | 5 | 5 | 5 |
| C-owned sections: `emph` | 10 | 10 | 10 |
| C-owned sections: long sentences | 0 | 0 | 0 |
| C-owned sections: paragraphs with >1 semicolon | 0 | 0 | 0 |
| Whole paper: `para` | 14 | 14 | 15 |
| Whole paper: `emph` | 28 | 28 | 30 |
| Whole paper: long sentences | 0 | 0 | 0 |
| Whole paper: paragraphs with >1 semicolon | 0 | 0 | 0 |

The C-13 edit shortened `09-related-work.tex` and `10-conclusion.tex` while
retaining the LIMBO, Agent libOS and VeriGUI comparisons, citations, agent
macros and scientific claims. The integrated build changed from Conclusion
starting on page 13 to Conclusion ending on page 12; References starts on page
13. The final PDF has 23 pages, no `??`, and no author metadata. The largest
overfull box is 1.53427pt.
