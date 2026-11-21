# C-13 final freeze and submission checklist

This file is the handoff sheet for the final `main` freeze. PR #81 is merged.
The 20 November run below is tied to the clean freeze-candidate commit that
adds reproducible line-ending rules; the lead must merge that candidate and
confirm the resulting `main` commit before its bundle is published.

## Freeze record (YC-F1)

- Freeze-candidate source commit: `29c29905599d0701a9669cfd89952c940c274097`
  (`PENDING` lead merge/final `main` confirmation)
- Manifest: `artifact/runs/2026-11-20/MANIFEST.json`
- Command: `python3 artifact/run_all.py --output-dir <fresh-output> --jobs 4`
- Exit code: `0`
- Completed jobs / failed jobs / errors: `27 / 0 / 0`; manifest status `PASS`,
  clean source tree `true`.
- CSV comparison: 108 committed and 108 reproduced; no missing or extra file;
  107 SHA-256 hashes match. Only `ledger_bench.csv` differs, as documented in
  the artifact README, because it is host-dependent.
- Macro and `others/notes.md` checks: 31 generated files were compared. Only
  `macros_real.tex` differs through the four host-dependent `\Ledger*` values;
  every non-ledger row of regenerated `others/notes.md` is identical.
- Reproducibility precondition: `.gitattributes` keeps POSIX source files LF
  and preserves the CSV bytes emitted by Python. A fresh clone then passes 68
  artifact tests and 119 testbed tests (3 Android-environment skips).
- After this commit, only the anonymous artifact link may be added to §8.

Preparation evidence from commit `15ccc64`:

- Extracted bundle pipeline: 27/27 jobs passed, 0 failed, 0 errors.
- 56 CSV outputs were produced; 55 hashes matched and only
  `artifact/results/ledger_bench.csv` differed because it is host-dependent.

## Anonymous artifact (YC-F2)

- Proposed hosting service: `anonymous.4open.science` (pending lead
  confirmation).
- The source for the final snapshot must be an artifact-only repository or
  equivalent frozen bundle view containing the files selected by
  `team/make_bundle.sh`; do not expose the full team repository, its history,
  or this checklist with author/contact data.
- 4open snapshot URL: `PENDING lead confirmation`
- Candidate ZIP name: `ghost-effect-c13-freeze-29c2990.zip` (must be recreated
  if the lead-confirmed `main` commit differs)
- Candidate ZIP SHA-256:
  `049d9ede19ab205b5c51445eab7e8c49eb7960790eed9af34538b8443c664503`
- Candidate bundle manifest: source `29c29905599d0701a9669cfd89952c940c274097`,
  583 tracked files.
- Anonymous download URL: `PENDING`
- Incognito or signed-out download check: `PENDING`
- Candidate extracted-directory scrub: `PASS`
- Candidate extracted pipeline exit code and manifest: `0`; `PASS`, 27/27
  jobs, 0 failed, 0 errors.
- Candidate extracted CSV comparison: 108/108 present; 107 hashes match;
  only `ledger_bench.csv` differs.
- Downloaded-from-anonymous-link rerun: `PENDING` publication and signed-out
  download.
- Allowed host-dependent differences: `artifact/results/ledger_bench.csv`.

### Drive staging upload (pre-freeze; historical test only)

The following upload only verified a temporary Drive destination and hash
procedure. It must not be cited as the final YC-F2 artifact because it
predates the freeze commit and is not an anonymous public link.

- Drive folder: <https://drive.google.com/drive/folders/1jp7xPlvLgLbaCk7ii5mZvw7oRWy5nLOJ>
- ZIP: `ghost-effect-c13-pre-freeze-15ccc64.zip`
- ZIP URL: <https://drive.google.com/file/d/1FX__khUXHwlnqINXI90CYPZNzVuM6pqE/view?usp=drivesdk>
- SHA-256: `5A6D9C8C26C808CCCF55A2D7AD42C27BD63F6FB87F226640AA6E3E16FDECF927`
- Upload result: verified by the connected Drive account on 19 Nov 2026.
- Public-link check: `NOT PASS` (a signed-out HTTP request redirected to
  `accounts.google.com`, so the file is still private). This staging result is
  retained only for audit; it is not the proposed final host.

Do not replace the `PENDING` final fields with this staging URL or checksum.

### 4open preparation

- GitHub account authorization for the selected private artifact repository:
  `PENDING`
- Terms to redact: repository owner/organization, team names, author names,
  author emails, local-user paths, and any non-synthetic host identifiers.
- Snapshot expiry: `PENDING conference/lead confirmation`
- Signed-out mirror browse check: `PENDING`
- Mirror ZIP download and extracted-directory scrub: `PENDING`
- Mirror ZIP pipeline and CSV comparison: `PENDING`

Hash commands:

```text
sha256sum ghost-effect-c13-freeze-<commit>.zip
sha256sum artifact/results/*.csv
```

On Windows PowerShell, use:

```powershell
Get-FileHash .\ghost-effect-c13-freeze-<commit>.zip -Algorithm SHA256
```

## Final PDF gate (YC-F3)

- Candidate `sh manuscript/build.sh` exit code: `0`
- Candidate PDF pages: 23; Conclusion is on and ends on page 12; References
  starts on page 13.
- Candidate `pdftotext` count of `??`: `0`
- Candidate `pdfinfo` author field: absent; no Acknowledgments heading.
- Candidate overfull maximum: 1.53427 pt; boxes above 10 pt: `0`
- Candidate readability: `PASS` (`\para` 14/15, `\emph` 28/30, no long
  sentence or semicolon violation).
- YC-01–YC-12 core rerun on this same commit: build, tests, scrub and
  readability `PASS`; repeat after adding the final anonymous link.

## HotCRP submission (YC-F4)

- Abstract registration: submission #3, evidenced in PR #75.
- Final title: `GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents`
- Author order: `PENDING team confirmation`
- Each author's full name, email and affiliation: `PENDING team confirmation`
- ACM corresponding author: `PENDING team confirmation`
- Final PDF uploaded: `PENDING`
- Submission confirmation URL or screenshot: `PENDING`
- Text comparison between submitted PDF and the freeze build: `PENDING`

### Author and contact handoff

These values are for the HotCRP record only; keep the manuscript and artifact
double-blind. Names, emails and affiliations are entered in HotCRP and never
committed here (YC-09: this file must pass `team/scrub_check.sh`). The order and
every author's details must be confirmed by the team before YC-F4.

| Order | Full name | Email | Affiliation | Status |
|---|---|---|---|---|
| 1 | `PENDING A` | `PENDING A` | `PENDING A` | Team confirmation required |
| 2 | `PENDING B` | `PENDING B` | `PENDING B` | Team confirmation required |
| 3 | `PENDING C` | `PENDING C` | `PENDING C` | Team confirmation required |

- ACM corresponding author: `PENDING team confirmation`
- HotCRP contact account: the account that registered submission #3 (see PR #75)
- Do not guess missing A/B names, emails, affiliations, author order, or the
  corresponding author from Git commit metadata.

## Freeze rule

The freeze commit, manifest, ZIP checksum and final PDF comparison must all
refer to the same `main` commit. Do not reuse the pre-freeze ZIP after a code,
data, generated output or manuscript change.

## 21/11/2026: final freeze, anonymous artifact and link

- Freeze commit: `dd4b633` on `main` (#84 and #85 merged). Between the
  20/11 freeze run (`29c2990`, Python 3.12.3, 27/27 PASS, 107/108 CSV hashes
  match, only `ledger_bench.csv` differs) and `dd4b633`, `artifact/` and
  `testbed/` changed only in `artifact/README.md` and
  `artifact/tests/test_eval.py`; no script, CSV or raw data changed, so the
  20/11 manifest stands for this commit.
- Clean-clone check of the same artifact code on 21/11 (Python 3.14.4,
  WSL): 68 artifact tests and 119 testbed tests OK; bundle pipeline 27/27,
  106/108 CSV byte-identical; `ledger_bench.csv` is host-dependent and
  `lag_wait.csv` differs only in the last digit of two floats (Python 3.14
  versus 3.12), as the bundle README allows.
- Bundle: `ghost-effect-freeze-dd4b633.zip`, 585 files, SHA-256
  `c22277b90868f8e5b98b3cd88144482211380ce9287427fe24be5b71133bde6d`;
  extracted-directory scrub PASS.
- Anonymous artifact: <https://anonymous.4open.science/r/ghosteffect-artifact>.
  Signed-out file listing and ZIP download work (HTTP 200); the downloaded
  copy is byte-identical to the freeze bundle (585 files, `diff -r` empty)
  and passes scrub, so the bundle pipeline result above applies to it.
- Section 8 now gives the link. PDF gate after the link: build exit 0,
  23 pages, Conclusion on page 12, References start on page 13, `??` 0,
  no Author metadata, no Acknowledgments heading, largest overfull box
  1.53 pt, scrub of the tracked manuscript sources PASS.
- HotCRP upload of the final PDF and author details: done by the team
  member who holds the HotCRP account (YC-F4 evidence pending).

## 21/11/2026 (afternoon): language polish after the freeze

At the team's request the manuscript text was polished once more before
upload (no number, macro, script or data change; details in
`team/a-log.md`). The artifact code and data are unchanged from `dd4b633`;
only `manuscript/` in the anonymous bundle is refreshed. PDF gate: build
exit 0, 23 pages, Conclusion and References on page 12, `??` 0, no overfull
box, abstract 199 words.
