# DAVx5 + Etar + Radicale on the AVD: lost PUT reply, then a fault

Rows: trials.csv. Delay = seconds from the fault to the next PUT of the same href (proxy journal).

| Fault | Scheduled | Valid | Exactly once | Delay to next PUT, median [min, max] s |
|---|---|---|---|---|
| kill9 | 3 | 3 | 3 | 52.5 [52.4, 54.1] |
| kill9-doze | 3 | 3 | 3 | 50.9 [50.9, 50.9] |
| lmk | 3 | 3 | 3 | 39.6 [39.5, 40.6] |
| none | 3 | 2 | 2 | 0.0 [0.0, 0.0] |
