# K-9 lost reply on a physical phone

Rows: trials.csv. Valid = every pre-redo check passed. Redo duplicate = 2 server copies, 2 Message-IDs.

| Kill | Config | Scheduled | Valid | No resend after relaunch | Redo duplicates | 95% Wilson |
|---|---|---|---|---|---|---|
| background | sent | 5 | 5 | 5 | 5/5 | [56.6, 100.0] |
| background | nosent | 5 | 5 | 5 | 5/5 | [56.6, 100.0] |
| force-stop | sent | 10 | 10 | 10 | 10/10 | [72.2, 100.0] |
| force-stop | nosent | 10 | 10 | 10 | 10/10 | [72.2, 100.0] |
| all | all | 30 | 30 | 30 | 30/30 | [88.6, 100.0] |
