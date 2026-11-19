# C-13 final freeze and submission checklist

This file is the handoff sheet for the final `main` freeze. It must be filled
from one clean freeze commit after PR #81 is merged. The current values marked
`pre-freeze` are preparation evidence only and must be replaced or reconfirmed
at freeze time.

## Freeze record (YC-F1)

- Freeze commit: `PENDING`
- Manifest: `artifact/runs/<date>/MANIFEST.json`
- Command: `python3 artifact/run_all.py --output-dir <fresh-output> --jobs 4`
- Exit code: `PENDING`
- Completed jobs / failed jobs / errors: `PENDING`
- CSV comparison: `PENDING`; document `ledger_bench.csv` separately if it is
  the only host-dependent output.
- Macro and `others/notes.md` spot checks: `PENDING`
- After this commit, only the anonymous artifact link may be added to §8.

Preparation evidence from commit `15ccc64`:

- Extracted bundle pipeline: 27/27 jobs passed, 0 failed, 0 errors.
- 56 CSV outputs were produced; 55 hashes matched and only
  `artifact/results/ledger_bench.csv` differed because it is host-dependent.

## Anonymous artifact (YC-F2)

- Hosting service: Google Drive shared link (the Drive connector must be
  connected before upload).
- Final ZIP name: `ghost-effect-c13-freeze-<commit>.zip`
- ZIP SHA-256: `PENDING`
- Anonymous download URL: `PENDING`
- Incognito or signed-out download check: `PENDING`
- Extracted-directory scrub: `PENDING`
- Extracted pipeline exit code and manifest: `PENDING`
- Downloaded CSV hash comparison: `PENDING`
- Allowed host-dependent differences: `PENDING`

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

- `sh manuscript/build.sh` exit code: `PENDING`
- PDF pages: `PENDING` (Conclusion must end by page 12; References must start by page 13)
- `pdftotext` count of `??`: `PENDING`
- `pdfinfo` author field: `PENDING` (must be empty or anonymous)
- Overfull boxes above 10 pt: `PENDING`
- YC-01–YC-12 rerun on this same commit: `PENDING`

## HotCRP submission (YC-F4)

- Abstract registration: submission #3, evidenced in PR #75.
- Final title: `GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents`
- Author order: `PENDING team confirmation`
- Each author's full name, email and affiliation: `PENDING team confirmation`
- ACM corresponding author: `PENDING team confirmation`
- Final PDF uploaded: `PENDING`
- Submission confirmation URL or screenshot: `PENDING`
- Text comparison between submitted PDF and the freeze build: `PENDING`

## Freeze rule

The freeze commit, manifest, ZIP checksum and final PDF comparison must all
refer to the same `main` commit. Do not reuse the pre-freeze ZIP after a code,
data, generated output or manuscript change.
