#!/bin/sh
# Regenerates every result and all LaTeX fragments the paper inputs (paper == artifact).
# Stdlib-only Python 3; seeded.  ~15 min on a laptop (planner parts run in parallel).  bench_ledger.py measures
# host timings, so its latency columns differ run to run; everything else is byte-reproducible.
# If results/real/*.csv exist (emulator measurements; see results/real/SUMMARY.md), render.py reports them and
# planner_sim.py 'real' re-runs the simulator on measured profiles (results/real/params.csv, written by real_params.py).
set -e
cd "$(dirname "$0")/scripts"
python3 -u sim_sprt.py          > ../results/sim_sprt.log          # Thm 4.1 sanity checks, Lemma 4.6(i) calibration, correlated reads
python3 -u sim_impossibility.py > ../results/sim_impossibility.log # Thm 4.1(b,d) floors, certified lag waits
python3 -u sim_saga.py          > ../results/sim_saga.log          # Prop. 4.9 KKT allocation
python3 -u sim_nonce.py         > ../results/sim_nonce.log         # Lemma 4.7 nonce error model (edit distance)
python3 -u markov_planner.py    > ../results/markov_planner.log    # round-1 planner exact DTMC (sanity check; not in paper)
python3 -u real_params.py       > ../results/real_params.log       # results/real/campaign2/*.csv -> results/real/params.csv (campaign-2 measured parameters)
for part in main rulesweep stress0/6 stress1/6 stress2/6 stress3/6 stress4/6 stress5/6 sweep user sens ncal decomp share real; do                # model-based simulation (Sec. 7)
  python3 -u planner_sim.py $part > ../results/planner_sim_$(echo $part | tr '/' '_').log &
done
wait
python3 -u sample_size.py       > ../results/sample_size.log       # required calibration sizes (exact CP)
python3 -u bench_ledger.py      > ../results/bench_ledger.log      # host ledger latency + SIGKILL invariant test
python3 render.py                                                  # CSV -> ../../manuscript/generated/
echo "done; now run ../manuscript/build.sh"
