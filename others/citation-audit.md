# Citation audit

## 2026-11-16 - C-07

| Key | Primary source | Claim checked |
|---|---|---|
| `li2026exactlyonce` | https://arxiv.org/abs/2609.29095 | LIMBO evaluates duplicate side effects, idempotency keys, read paths and late commits for API tools. |
| `zhang2026agentlibos` | https://arxiv.org/abs/2606.03895v3 | Agent libOS provides capability checks, checkpoints, events and audit records around agent runtime primitives. |
| `zhang2026verigui` | https://arxiv.org/abs/2604.05477 | VeriGUI verifies action effects and uses verification to guide correction under noisy GUI responses; the record retains its ACL 2026 venue. |

The comparisons describe differences in problem boundary and do not claim that these systems implement GhostEffect's calibrated GUI recovery.

Gray and Reuter (1992) and Bailis et al. (VLDB 2015) were considered for this
section but not added: the current comparisons already cover the closest
agent-runtime, GUI-verification and exactly-once boundaries, and adding them
would not support a distinct claim in the manuscript.

## 2026-11-25 - all cited keys

All 84 cited keys were looked up at their primary source (arXiv, DOI, publisher or official docs) and every citing
sentence was compared with the source. All 84 exist. Mismatches found and fixed:

| Key | Problem | Fix |
|---|---|---|
| `tian2025agentprog` | AgentProg was credited with redoing the step and labelling commit points; it does neither (it recovers from a global belief state). Bib was the arXiv preprint. | Intro and Sec. 5 reworded, Redo baseline no longer attributed to it, position table says "belief-state recovery"; bib now MobiSys '26, doi 10.1145/3745756.3809245. |
| `li2025agentgit` | Cited for "checkpoint restore can replay irreversible effects"; AgentGit only discusses rollback and branching. | Removed from that sentence. |
| `li2026phoneharness` | Cited for "benchmarks test robustness and recovery"; it checks observable side effects of task completion. | Removed from that sentence. |
| `sentosa2025cellreplay` | Cited for connectivity loss and lost acknowledgements; CellReplay emulates cellular performance. | Removed; Sec. 2 case (4) now cites `rfc1047` (lost final reply). |
| `chen2026cordon` | Credited with Agent libOS's phases (prepare, dispatch, settle). | Sentence now gives libOS its phases and Cordon its effect outbox. |
| `android_workmanager` | Cited for "a crash or force-stop cancels alarms and jobs"; the page does not say it, and no official page says a crash does. | Now cited only for persistent WorkManager jobs; new `android15_behavior` (force-stop cancels all pending intents since Android 15). |
| `android_lmkd` | Cited for "reaps the foreground app last"; the page says lmkd kills "the least essential processes". | Reworded to the page's statement. |
| `langgraph_durable` | URL now serves the Persistence page, which does not state re-execution. | Points to the Interrupts page ("the node restarts from the beginning"); dropped from the exactly-once group. |
