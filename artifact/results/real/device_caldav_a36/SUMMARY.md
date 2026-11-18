# DAVx5 + Etar + Radicale on a rented Galaxy A36 (Android 15, AWS Device Farm, no root): lost PUT reply, then a fault

Rows: trials.csv. Delay = seconds from the fault to the next PUT of the same href (proxy journal).

| Fault | Scheduled | Valid | Exactly once | Delay to next PUT, median [min, max] s |
|---|---|---|---|---|
| none | 3 | 3 | 3 | 0.0 [0.0, 0.0] |
| stop-app | 3 | 3 | 3 | 30.0 [29.9, 39.0] |
| stop-app-doze | 3 | 1 | 1 | N/A |

Process samples (every 10 s from the barrier): 7 trials, 0 with a frozen sample; procstates seen: 6 8 19.
