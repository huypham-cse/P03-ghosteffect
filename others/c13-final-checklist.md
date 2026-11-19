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

- Hosting service: Google Drive.
- Final ZIP name: `ghost-effect-c13-freeze-<commit>.zip`
- ZIP SHA-256: `PENDING`
- Anonymous download URL: `PENDING`
- Incognito or signed-out download check: `PENDING`
- Extracted-directory scrub: `PENDING`
- Extracted pipeline exit code and manifest: `PENDING`
- Downloaded CSV hash comparison: `PENDING`
- Allowed host-dependent differences: `PENDING`

### Staging upload (pre-freeze; not the submission artifact)

The following upload only verifies the Drive destination and hash procedure. It
must not be cited as the final YC-F2 artifact because it predates the freeze
commit.

- Drive folder: <https://drive.google.com/drive/folders/1jp7xPlvLgLbaCk7ii5mZvw7oRWy5nLOJ>
- ZIP: `ghost-effect-c13-pre-freeze-15ccc64.zip`
- ZIP URL: <https://drive.google.com/file/d/1FX__khUXHwlnqINXI90CYPZNzVuM6pqE/view?usp=drivesdk>
- SHA-256: `5A6D9C8C26C808CCCF55A2D7AD42C27BD63F6FB87F226640AA6E3E16FDECF927`
- Upload result: verified by the connected Drive account on 19 Nov 2026.
- Public-link check: `NOT PASS` (a signed-out HTTP request redirected to
  `accounts.google.com`, so the file is still private). The current connector
  can upload and share with a named account/domain, but cannot grant `anyone`
  access for this personal Gmail account. Before YC-F2, set **General access →
  Anyone with the link → Viewer** in Drive, then repeat the signed-out/incognito
  check and record the successful download status here.

Do not replace the `PENDING` final fields with this staging URL or checksum.

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

### Author and contact handoff

These values are for the HotCRP record only; keep the manuscript and artifact
double-blind. The order and the A/B details must be confirmed by the team
before YC-F4.

| Order | Full name | Email | Affiliation | Status |
|---|---|---|---|---|
| 1 | `PENDING A` | `PENDING A` | `PENDING A` | Team confirmation required |
| 2 | `PENDING B` | `PENDING B` | `PENDING B` | Team confirmation required |
| 3 | Lê Nguyễn Bá Nguyên | `lenguyenbanguyen20192020@gmail.com` | `PENDING C` | C; affiliation and order confirmation required |

- ACM corresponding author: `PENDING team confirmation`
- HotCRP contact account currently connected: Lê Nguyễn Bá Nguyên
- Do not guess missing A/B names, emails, affiliations, author order, or the
  corresponding author from Git commit metadata.

## Freeze rule

The freeze commit, manifest, ZIP checksum and final PDF comparison must all
refer to the same `main` commit. Do not reuse the pre-freeze ZIP after a code,
data, generated output or manuscript change.
