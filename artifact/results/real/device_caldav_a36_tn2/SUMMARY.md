# DAVx5 + Etar + Radicale on the AVD: lost PUT reply, then a fault

Rows: trials.csv. Delay = seconds from the fault to the next PUT of the same href (proxy journal).

| Fault | Scheduled | Valid | Exactly once | Delay to next PUT, median [min, max] s |
|---|---|---|---|---|
| stop-app-doze | 2 | 2 | 2 | 27.7 [27.6, 27.7] |

Process samples (every 10 s from the barrier): 2 trials, 0 with a frozen sample; procstates seen: 19.
Doze trials with a retry: 2; retry while still in deep idle (before the forced exit): 2.
