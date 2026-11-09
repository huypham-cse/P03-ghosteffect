# Archive of `P03-ghosteffect`

- Created: 2026-11-07T16:28:44+07:00
- Source folder: `/Users/xuanbachle/Workstation/MobiSys2027/papers/P03-ghosteffect`
- Kept locally (not archived): nothing
- Format: zip (deflate), archives larger than 4.8 GB split into byte parts
- Every archive was tested with `unzip -t`; SHA-256 values below were taken before upload.

## Notes

MobiSys 2027 paper P03-ghosteffect: manuscript, artifact with real measurements, STATUS.md and review.md. Git repo pushed to github.com/lexuanbach/MobiSys-2027-P03-* before archiving. Archived 2026-11-07 after the review packet was written.

## Archives

| # | Archive file(s) | Original paths | Files | Original size | Archive size |
|---|---|---|---|---|---|
| 01 | `01_root__small-items.zip` | `.git`<br>`.gitignore`<br>`STATUS.md`<br>`artifact`<br>`manuscript`<br>`others`<br>`review.md` | 450 | 4.0 MB | 2.6 MB |

## Checksums (SHA-256)

```
9bbc4018eab8cdf7ab33d4e8ced360cf24b464e720883e8573fbcdfc4af3c390  01_root__small-items.zip
```

## Restore

Single archive: `unzip <label>.zip -d <restore-dir>` (paths are relative to the source folder).

Split archive: join the parts in order, check the hash, then unzip:

```sh
cat <label>.zip.part* > <label>.zip
shasum -a 256 <label>.zip   # compare with the value above
unzip <label>.zip -d <restore-dir>
```

To rebuild the original folder, unzip every archive into the same directory and put the kept paths back.
`MANIFEST.tsv.gz` lists every archived file (archive label, relative path, size in bytes).

## Git repositories in the archive

| Repository | Branch | HEAD | Remotes | Uncommitted entries |
|---|---|---|---|---|
| `.` | main | `c332358` | https://github.com/lexuanbach/MobiSys-2027-P03-GhostEffect.git | 0 |
