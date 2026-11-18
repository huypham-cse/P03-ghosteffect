# K-9 lost reply on the AVD, killed by lmkd under real memory pressure

Rows: trials.csv. Valid = every pre-redo check passed. Redo duplicate = 2 server copies, 2 Message-IDs.

| Kill | Config | Scheduled | Valid | No resend after relaunch | Redo duplicates | 95% Wilson |
|---|---|---|---|---|---|---|
| lmk | sent | 3 | 3 | 3 | 3/3 | [43.9, 100.0] |
| lmk | nosent | 3 | 3 | 3 | 3/3 | [43.9, 100.0] |
| all | all | 6 | 6 | 6 | 6/6 | [61.0, 100.0] |
