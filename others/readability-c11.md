# C-11 readability report

Scope: the C-owned manuscript sections listed in `team/CONTRIBUTOR_FIXED.md`:
`00-abstract.tex`, `01-introduction.tex`, `07-evaluation.tex`,
`07-realsim.tex`, `08-discussion.tex`, `09-related-work.tex`,
`10-conclusion.tex`, and `appendix-results.tex`.

The counts below are source-level estimates from `team/readability_count.py`.
They do not replace a final PDF reading pass.

| Run | `\para{` | `\emph{` | sentences over 45 words | paragraphs with over one semicolon |
|---|---:|---:|---:|---:|
| Before this C-11 pass | 18 | 34 | 19 | 17 |
| After this C-11 pass | 0 | 4 | 0 | 0 |
| C contributor limit | 5 | 10 | 0 | 0 |

Validation command:

```sh
python3 team/readability_count.py --strict \
  manuscript/sections/00-abstract.tex \
  manuscript/sections/01-introduction.tex \
  manuscript/sections/07-evaluation.tex \
  manuscript/sections/07-realsim.tex \
  manuscript/sections/08-discussion.tex \
  manuscript/sections/09-related-work.tex \
  manuscript/sections/10-conclusion.tex \
  manuscript/sections/appendix-results.tex
```

The command passed after the edits. `bash manuscript/build.sh` also produced a
22-page PDF successfully. Generated fragments and the PDF were not committed by
this readability pass.

## Out of scope

No A- or B-owned source file was edited. Their owners still need to run the same
check and make any required fixes in their own files:

- A: `03-model.tex`, `04-theory.tex`, `05-design.tex`, and
  `appendix-proofs.tex`.
- B: `02-background-motivation.tex`, `06-implementation.tex`, `07-real.tex`,
  `07-agent.tex`, `tab-apps.tex`, `tab-position.tex`, and `fig1.tex`.

The full-paper gate remains a team acceptance task after A and B complete their
own readability passes.
