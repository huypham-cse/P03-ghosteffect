# DAVx5 + Etar + Radicale on a rented Pixel 9 (Android 15, AWS Device Farm, no root): lost PUT reply, then a fault

Rows: trials.csv. Delay = seconds from the fault to the next PUT of the same href (proxy journal).

| Fault | Scheduled | Valid | Exactly once | Delay to next PUT, median [min, max] s |
|---|---|---|---|---|
| none | 3 | 3 | 3 | 0.0 [0.0, 0.0] |
| stop-app | 3 | 3 | 3 | 52.7 [42.0, 52.7] |
| stop-app-doze | 3 | 3 | 3 | 27.4 [27.2, 27.4] |

Process samples (every 10 s from the barrier): 9 trials, 0 with a frozen sample; procstates seen: 6 8 19.
Doze trials with a retry: 3; retry while still in deep idle (before the forced exit): 3.
