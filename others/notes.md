# Notes — GhostEffect (P03)

Last updated 2026-11-07 (round 3: emulator campaign 2 integrated; measured-parameter simulation re-run; Thm-4.8-only and rule-family baselines; source-family fix).

## 1. Number ledger (single source of truth)

Every inline number in the prose is a macro in `manuscript/generated/macros.tex`, written by `artifact/scripts/render.py` from CSVs in `artifact/results/`.
**Do not hand-edit numbers in the .tex files.** Tables and figures are generated (`generated/tab_*.tex`, `fig_*.tex`). Hand-written floats: `sections/tab-apps.tex`,
`sections/tab-position.tex` (descriptive, no data) and Figure 1 (`figures/fig1.tex`, counts are macros). A few literal facts in the RQ7 prose come from
`results/real/SUMMARY.md` text rather than a CSV column: the 70 s client timeout, the 20–100 ms retry delay, "six trials lost to an ANR dialog, one stopped by the
operator", the 24 h / 30–60 min Synapse retention (also in `campaign2/logs/source_excerpts_synapse_k9.txt` and the Synapse source, cited), and 14 s / 300 s as the
tail-sensitivity range (a modelling choice).
**Emulator measurements**: the body reports campaign 2 (`artifact/results/real/campaign2/`); campaign 1 (`results/real/*.csv`) feeds the appendix table
`tab_realcone.tex`, kill semantics and the ledger test. `render_real.py` writes `tab_real.tex`, `tab_realcone.tex`, `tab_realsim.tex` and the `\Real*`/`\Rsim*` macros.
`real_params.py` derives `results/real/params.csv` from the campaign-2 per-trial CSVs; `planner_sim.py real` → `planner_real.csv`.

Kinds: *exact*; *model-based simulation* (seeded, stated generative model, NOT device data); *EMULATOR measurement* (Android 13 emulator, small n outside Element);
*measured-parameter simulation* (simulator on measured profiles; NOT an emulator run); *HOST measurement* (ledger benchmark on the build laptop; changes per run).
"(unused)" macros are emitted for completeness. Generated from `macros.tex` (967 macros) by a scratch script.

| Macro | Value | Kind | Source | Used in |
|---|---|---|---|---|
| `\CalCPENhundred` | 5.7 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalCPViolMax` | 1.6 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalCPWorst` | 1.79 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalNomViol` | 94 | exact DP | calibration.csv (sim_sprt.py) | 07-evaluation.tex |
| `\CalPlugENhundred` | 4.3 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalPlugViolHi` | 56 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalPlugViolLo` | 12 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalStrictENhundred` | 8.2 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalStrictViolMax` | 0.0 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\CalStrictWorst` | 0.71 | exact DP | calibration.csv (sim_sprt.py) | (unused) |
| `\ClassGtwoAsk` | 8.9 | model-based simulation | planner_class.csv | 07-evaluation.tex |
| `\ClassGtwoSecs` | 33 | model-based simulation | planner_class.csv | (unused) |
| `\ClassKeyGtwoPv` | 27.8 | model-based simulation | planner_class.csv | 07-evaluation.tex |
| `\ClassLocalAsk` | 1.2 | model-based simulation | planner_class.csv | 07-evaluation.tex |
| `\ClassLocalSecs` | 6 | model-based simulation | planner_class.csv | (unused) |
| `\ClassNonGtwoAsk` | 20.2 | model-based simulation | planner_class.csv | 07-evaluation.tex |
| `\ClassNonGtwoSecs` | 21 | model-based simulation | planner_class.csv | (unused) |
| `\ClassSrcGtwoAsk` | 31.0 | model-based simulation | planner_class.csv | (unused) |
| `\ClassSrcLocalAsk` | 6.0 | model-based simulation | planner_class.csv | (unused) |
| `\ClassSrcNonGtwoAsk` | 64.3 | model-based simulation | planner_class.csv | (unused) |
| `\ClassSrcVlmAsk` | 99.0 | model-based simulation | planner_class.csv | (unused) |
| `\ClassVlmAsk` | 98.8 | model-based simulation | planner_class.csv | 07-evaluation.tex |
| `\ClassVlmSecs` | 67 | model-based simulation | planner_class.csv | (unused) |
| `\CorrCertMaxHi` | 0.19 | MC | correlation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\CorrNaiveOne` | 9.6 | MC | correlation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\CorrViewAsk` | 27 | MC | correlation.csv (sim_sprt.py) | (unused) |
| `\CorrViewCrossOne` | 10.4 | MC | correlation.csv (sim_sprt.py) | (unused) |
| `\CorrViewCrossTwo` | 1.13 | MC | correlation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\CorrViewWithinMax` | 0.20 | MC | correlation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\CorrVoneEight` | 1.76 | MC | correlation.csv (sim_sprt.py) | (unused) |
| `\CorrVoneOne` | 1.89 | MC | correlation.csv (sim_sprt.py) | (unused) |
| `\CorrVoneSix` | 0.99 | MC | correlation.csv (sim_sprt.py) | (unused) |
| `\DecompBcp` | 0.38 | model-based simulation | planner_decomp.csv | 07-evaluation.tex |
| `\DecompBtrue` | 0.104 | model-based simulation | planner_decomp.csv | 07-evaluation.tex |
| `\DecompCPratio` | 3.6 | model-based simulation | planner_decomp.csv | 07-evaluation.tex |
| `\DecompRealized` | 0.029 | model-based simulation | planner_decomp.csv | (unused) |
| `\DriftFiveAsk` | 29.6 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftFivePv` | 0.24 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftFivePvHi` | 0.37 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftFiveTestAsk` | 44.7 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftFiveTestPv` | 0.01 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftFiveTestPvHi` | 0.07 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftOneAsk` | 24.9 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftOnePv` | 0.05 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftOnePvHi` | 0.12 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftOneTestAsk` | 25.8 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftOneTestPv` | 0.05 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftOneTestPvHi` | 0.12 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftTenAsk` | 33.5 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftTenPv` | 0.79 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\DriftTenPvHi` | 1.00 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\DriftTenTestAsk` | 54.3 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftTenTestPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftTenTestPvHi` | 0.04 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\DriftThreeAsk` | 27.6 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftThreePv` | 0.16 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftThreePvHi` | 0.27 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftThreeTestAsk` | 37.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftThreeTestPv` | 0.04 | model-based simulation | planner_ncal.csv | (unused) |
| `\DriftThreeTestPvHi` | 0.11 | model-based simulation | planner_ncal.csv | (unused) |
| `\ImpViol` | 0 | MC | impossibility.csv (sim_impossibility.py) | appendix-proofs.tex |
| `\LagLogThree` | 12\,s | exact CP | lag_wait.csv (sim_impossibility.py) | 07-evaluation.tex |
| `\LagParetoThree` | 98\,min | exact CP | lag_wait.csv (sim_impossibility.py) | 07-evaluation.tex |
| `\LagParetoTwo` | 3\,min | exact CP | lag_wait.csv (sim_impossibility.py) | 07-evaluation.tex |
| `\LedgerBytes` | 205 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerCand` | 92 | HOST measurement | ledger_bench.csv (bench_ledger.py) | (unused) |
| `\LedgerFullPfifty` | 4.0 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerFullPninetyfive` | 4.2 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerPfifty` | 0.04 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerPninetyfive` | 0.09 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerTaps` | 228{,}793 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerTrials` | 300 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\LedgerViol` | 0 | HOST measurement | ledger_bench.csv (bench_ledger.py) | 06-implementation.tex |
| `\NcalAJointAsk` | 100.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalAJointPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalAProdAsk` | 51.6 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalAProdPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalASrcAsk` | 100.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalASrcPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalBJointAsk` | 100.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalBJointPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalBProdAsk` | 39.7 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalBProdPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalBSrcAsk` | 72.6 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalBSrcPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalCJointAsk` | 100.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalCJointPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalCProdAsk` | 31.1 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalCProdPv` | 0.04 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalCSrcAsk` | 62.1 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalCSrcPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalDJointAsk` | 100.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalDJointPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalDProdAsk` | 27.4 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalDProdPv` | 0.05 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalDSrcAsk` | 60.0 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalDSrcPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalEJointAsk` | 66.7 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\NcalEJointPv` | 0.05 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalEProdAsk` | 24.9 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\NcalEProdPv` | 0.05 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalESrcAsk` | 47.4 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\NcalESrcPv` | 0.00 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalFJointAsk` | 33.8 | model-based simulation | planner_ncal.csv | 01-introduction.tex, 07-evaluation.tex |
| `\NcalFJointPv` | 0.04 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalFProdAsk` | 23.4 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalFProdPv` | 0.02 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalFSrcAsk` | 27.2 | model-based simulation | planner_ncal.csv | 07-evaluation.tex |
| `\NcalFSrcPv` | 0.04 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalGJointAsk` | 26.4 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalGJointPv` | 0.07 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalGProdAsk` | 23.5 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalGProdPv` | 0.04 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalGSrcAsk` | 23.8 | model-based simulation | planner_ncal.csv | (unused) |
| `\NcalGSrcPv` | 0.05 | model-based simulation | planner_ncal.csv | (unused) |
| `\NonceEN` | 1.5 | exact / MC | nonce.csv (sim_nonce.py) | (unused) |
| `\NonceEpsOne` | 0.016 | exact / MC | nonce.csv (sim_nonce.py) | (unused) |
| `\NonceEpsZero` | \ensuremath{7.2{\times}10^{-6}} | exact / MC | nonce.csv (sim_nonce.py) | 05-design.tex, 07-evaluation.tex |
| `\NsizeJointQTwo` | 3{,}723 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeJointThree` | 21{,}635 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeJointTwo` | 1{,}700 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeLagThree` | 58{,}036 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeLagTwo` | 4{,}649 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeProdThree` | 2{,}268 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeProdTwo` | 221 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\NsizeProdZeroTwo` | 127 | exact CP | sample_size.csv (sample_size.py) | (unused) |
| `\PopCmAJoint` | 0.00 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmAJointAsk` | 73.8 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmAJointHi` | 0.04 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmAProd` | 0.16 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmAProdAsk` | 26.4 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmAProdHi` | 0.27 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmARules` | 0.73 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmARulesAsk` | 24.1 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmARulesHi` | 0.93 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmASrc` | 0.01 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmASrcAsk` | 49.4 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmASrcHi` | 0.07 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBJoint` | 0.01 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBJointAsk` | 74.2 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBJointHi` | 0.07 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBProd` | 0.31 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBProdAsk` | 29.3 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBProdHi` | 0.46 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBRules` | 1.10 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBRulesAsk` | 24.7 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBRulesHi` | 1.35 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBSrc` | 0.01 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBSrcAsk` | 49.8 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmBSrcHi` | 0.07 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCJoint` | 0.00 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopCmCJointAsk` | 74.5 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCJointHi` | 0.04 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCProd` | 0.33 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopCmCProdAsk` | 33.5 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCProdHi` | 0.47 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCRules` | 2.16 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCRulesAsk` | 24.4 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCRulesHi` | 2.50 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCSrc` | 0.01 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopCmCSrcAsk` | 50.5 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopCmCSrcHi` | 0.07 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFJoint` | 0.00 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopIwFJointAsk` | 79.6 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFJointHi` | 0.04 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFProd` | 0.11 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopIwFProdAsk` | 46.2 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFProdHi` | 0.21 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFRules` | 1.34 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopIwFRulesAsk` | 24.7 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFRulesHi` | 1.61 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFSrc` | 0.00 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFSrcAsk` | 55.6 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwFSrcHi` | 0.04 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPJoint` | 0.34 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopIwPJointAsk` | 67.4 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPJointHi` | 0.49 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPProd` | 0.87 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopIwPProdAsk` | 26.4 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPProdHi` | 1.09 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopIwPRules` | 1.34 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPRulesAsk` | 24.7 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPRulesHi` | 1.61 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPSrc` | 0.13 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPSrcAsk` | 47.9 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopIwPSrcHi` | 0.24 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\PopRows` | 5 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\PopRulesOver` | 4 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\RealAmkillKnine` | 15 | EMULATOR measurement (campaign 1) | results/real/e4_kill_methods.csv | 07-real.tex |
| `\RealAmkillNoopElem` | 13 | EMULATOR measurement (campaign 1) | results/real/e4_kill_methods.csv | 07-real.tex |
| `\RealBlindLagHi` | 13.6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealBlindLagLo` | 4.5 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealCalKill` | 5 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealCalN` | 8 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, tab_real.tex |
| `\RealCalOnce` | 8 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealCalRecDup` | 3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, tab_real.tex |
| `\RealCalRecN` | 3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, tab_real.tex |
| `\RealCensored` | 0 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealCoBot` | 2 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealCoN` | 101 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 01-introduction.tex, 07-real.tex, 08-discussion.tex, tab_real.tex |
| `\RealCoWrong` | 0 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealDataLimitation` | (prose) | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 08-discussion.tex |
| `\RealEarlyWrong` | 3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealElemAckedN` | 6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemN` | 101 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealElemNofaultN` | 12 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemOnce` | 101 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealElemRL` | 83 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, fig1.tex, tab_real.tex |
| `\RealElemSameTxn` | 65 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealElemSentPolls` | 1{,}036 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemStd` | 60 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemStdAcked` | 60 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealElemSticky` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemStickyResend` | 2 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemStickySync` | 18 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealElemSyncOnly` | 18 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealFirstBot` | 33 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealFirstObs` | 68 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealFirstWrong` | 3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealFirstWrongHi` | 12.2 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealFirstWrongLo` | 1.5 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealFsFirstBot` | 31 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealFsN` | 31 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealGuiDup` | 23 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 02-background-motivation.tex |
| `\RealGuiN` | 23 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 02-background-motivation.tex |
| `\RealKAckedN` | 10 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealKAppendHi` | 5.3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealKAppendLo` | 3.3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealKNotifNosent` | 9 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealKNotifSent` | 6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealKNotifWrong` | 15 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealKOutWrong` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealKRd` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | fig1.tex, tab_real.tex |
| `\RealKRdNosent` | 12 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealKRdSent` | 8 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealKRecDup` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, fig1.tex, tab_real.tex |
| `\RealKRecN` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, fig1.tex, tab_real.tex |
| `\RealKSentAckedN` | 7 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealKSentN` | 8 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealKSentWrong` | 8 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealLagAckedMax` | 3.9 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAckedMed` | 3.6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAckedN` | 6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAckedNinety` | 3.9 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAllMax` | 13.6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAllMed` | 4.3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAllN` | 83 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagAllNinety` | 12.2 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealLagFsMax` | 12.7 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagFsMed` | 11.9 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealLagFsN` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagFsNinety` | 12.3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 01-introduction.tex, tab_real.tex |
| `\RealLagKillMax` | 13.6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagKillMed` | 4.0 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagKillN` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagKillNinety` | 8.0 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealLagNetMax` | 2.9 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagNetMed` | 2.4 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagNetN` | 20 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagNetNinety` | 2.7 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 01-introduction.tex, tab_real.tex |
| `\RealLagNofaultMax` | 3.8 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagNofaultMed` | 2.5 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealLagNofaultN` | 12 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagNofaultNinety` | 2.9 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSFsMax` | 12.4 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSFsMed` | 11.1 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSFsN` | 10 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSFsNinety` | 12.3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSKillMax` | 4.6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSKillMed` | 4.1 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSKillN` | 10 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLagSKillNinety` | 4.4 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLateBot` | 2 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLateHi` | 3.7 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex, tab_real.tex |
| `\RealLateObs` | 99 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | tab_real.tex |
| `\RealLedgerFullLostMax` | 0 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerFullLostMin` | 0 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerFullN` | 3 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | 07-real.tex |
| `\RealLedgerFullViol` | 0 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerNormalLostMax` | 0 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerNormalLostMin` | 0 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerNormalN` | 3 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerNormalViol` | 0 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | (unused) |
| `\RealLedgerOffLostMax` | 158 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | 07-real.tex |
| `\RealLedgerOffLostMin` | 15 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | 07-real.tex |
| `\RealLedgerOffN` | 3 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | 07-real.tex |
| `\RealLedgerOffViol` | 3 | EMULATOR measurement (campaign 1) | results/real/ledger_powerloss.csv | 07-real.tex |
| `\RealOneCoContra` | 0 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | 07-real.tex |
| `\RealOneCoDigest` | 4 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | 07-real.tex |
| `\RealOneCoLeft` | 2 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneCoN` | 5 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | 07-real.tex |
| `\RealOneElemN` | 37 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneElemRdN` | 14 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneElemRdSame` | 14 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneEvOnce` | 72 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneKnineN` | 35 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneKnineRdN` | 15 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneKnineRdPending` | 15 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | (unused) |
| `\RealOneN` | 72 | EMULATOR measurement (campaign 1) | results/real/*.csv, campaign2/c1_rescored_cofailures.csv | 07-real.tex |
| `\RealPresent` | yes | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | (unused) |
| `\RealTimeoutClean` | 3 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 08-discussion.tex |
| `\RealTimeoutN` | 6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealTimeoutOnce` | 6 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 07-real.tex |
| `\RealTwoN` | 149 | EMULATOR measurement (campaign 2) | results/real/campaign2/*.csv (render_real.py) | 01-introduction.tex |
| `\RsimElemAppAsk` | 0.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAppDup` | 1.03 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAppErr` | 1.03 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAppLoss` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAppPv` | 1.33 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimElemAppPvHi` | 1.58 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAppSecs` | 6 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAskAllAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAskAllDup` | 4.76 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | tab_realsim.tex |
| `\RsimElemAskAllErr` | 6.95 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAskAllLoss` | 2.19 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | tab_realsim.tex |
| `\RsimElemAskAllPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAskAllPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemAskAllSecs` | 73 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemGtwoAsk` | 37.2 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 01-introduction.tex, 07-real.tex |
| `\RsimElemGtwoDup` | 0.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemGtwoErr` | 2.27 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemGtwoLoss` | 2.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemGtwoPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemGtwoPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemGtwoSecs` | 31 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemJointAsk` | 72.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimElemJointDup` | 3.17 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemJointErr` | 5.21 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemJointLoss` | 2.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimElemJointSecs` | 70 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemProdAsk` | 3.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimElemProdDup` | 0.15 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemProdErr` | 0.24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemProdLoss` | 0.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemProdSecs` | 19 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoAsk` | 0.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoDup` | 71.24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoErr` | 71.24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoLoss` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoPv` | 100.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoPvHi` | 100.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRedoSecs` | 14 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesAsk` | 9.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimElemRulesDup` | 0.42 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesErr` | 0.50 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesLoss` | 0.07 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesSecs` | 25 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesThirtyAsk` | 3.1 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimElemRulesThirtyDup` | 0.10 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesThirtyErr` | 0.16 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesThirtyLoss` | 0.06 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesThirtyPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesThirtyPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemRulesThirtySecs` | 44 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcAsk` | 72.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcDup` | 3.16 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcErr` | 5.30 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcLoss` | 2.14 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimElemSrcSecs` | 70 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveJointAsk` | 12.7 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 00-abstract.tex, 01-introduction.tex, 07-real.tex, 10-conclusion.tex |
| `\RsimFiveJointDup` | 0.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveJointErr` | 0.76 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveJointLoss` | 0.67 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 01-introduction.tex |
| `\RsimFiveJointSecs` | 24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdAsk` | 2.7 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdDup` | 0.05 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdErr` | 0.14 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdLoss` | 0.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveProdSecs` | 18 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcAsk` | 18.4 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcDup` | 0.49 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcErr` | 1.21 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcLoss` | 0.72 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimFiveSrcSecs` | 29 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAppAsk` | 0.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAppDup` | 21.07 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAppErr` | 55.42 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAppLoss` | 34.34 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimKnineAppPv` | 27.67 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimKnineAppPvHi` | 28.59 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAppSecs` | 24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllDup` | 4.55 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllErr` | 6.68 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllLoss` | 2.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineAskAllSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoDup` | 4.47 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoErr` | 6.55 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoLoss` | 2.08 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineGtwoSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointDup` | 4.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointErr` | 6.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointLoss` | 1.99 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineJointSecs` | 77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdDup` | 3.96 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdErr` | 6.01 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdLoss` | 2.05 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineProdSecs` | 77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineRulesAsk` | 28.1 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineRulesDup` | 49.91 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineRulesErr` | 49.98 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineRulesLoss` | 0.07 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineRulesPv` | 65.85 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 00-abstract.tex, 01-introduction.tex, 07-evaluation.tex, 07-real.tex |
| `\RsimKnineRulesPvHi` | 66.81 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineRulesSecs` | 40 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcDup` | 4.02 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcErr` | 6.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcLoss` | 2.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKnineSrcSecs` | 77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppAsk` | 0.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppDup` | 20.91 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppErr` | 55.45 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppLoss` | 34.54 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppPv` | 27.64 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppPvHi` | 28.56 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAppSecs` | 23 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllDup` | 4.33 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllErr` | 6.39 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllLoss` | 2.06 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentAskAllSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoDup` | 3.86 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoErr` | 5.79 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoLoss` | 1.93 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentGtwoSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointDup` | 4.07 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointErr` | 6.11 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointLoss` | 2.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentJointSecs` | 77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointAsk` | 65.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointDup` | 18.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointErr` | 18.79 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointLoss` | 0.68 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointPv` | 19.65 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointPvHi` | 20.47 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveJointSecs` | 60 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveProdAsk` | 71.7 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveProdDup` | 11.55 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveProdErr` | 12.21 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveProdLoss` | 0.66 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveProdPv` | 9.84 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimKsentPassFiveProdPvHi` | 10.46 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveProdSecs` | 64 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcAsk` | 71.8 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcDup` | 11.16 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcErr` | 11.86 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcLoss` | 0.70 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcPv` | 9.93 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcPvHi` | 10.55 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassFiveSrcSecs` | 64 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassJointAsk` | 79.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassJointDup` | 11.37 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassJointErr` | 12.63 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassJointLoss` | 1.27 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassJointPv` | 9.85 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimKsentPassJointPvHi` | 10.48 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassJointSecs` | 71 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdAsk` | 87.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdDup` | 4.29 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdErr` | 5.89 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdLoss` | 1.60 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassProdSecs` | 75 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcAsk` | 87.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcDup` | 4.20 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcErr` | 5.48 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcLoss` | 1.28 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentPassSrcSecs` | 75 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdDup` | 4.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdErr` | 6.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdLoss` | 1.95 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentProdSecs` | 77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentRulesAsk` | 49.4 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentRulesDup` | 24.42 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentRulesErr` | 24.49 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentRulesLoss` | 0.07 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentRulesPv` | 28.91 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 00-abstract.tex, 01-introduction.tex, 07-evaluation.tex, 07-real.tex |
| `\RsimKsentRulesPvHi` | 29.84 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentRulesSecs` | 53 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcDup` | 4.30 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcErr` | 6.35 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcLoss` | 2.05 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimKsentSrcSecs` | 77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointAsk` | 60.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointDup` | 2.92 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointErr` | 4.31 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointLoss` | 1.38 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixJointSecs` | 69 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdAsk` | 3.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdDup` | 0.15 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdErr` | 0.24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdLoss` | 0.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixProdSecs` | 25 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcAsk` | 60.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcDup` | 2.80 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcErr` | 4.20 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcLoss` | 1.40 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimMixSrcSecs` | 69 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassJointAsk` | 60.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassJointDup` | 6.97 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassJointErr` | 8.36 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassJointLoss` | 1.38 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassJointPv` | 5.21 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimPassJointPvHi` | 5.68 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassJointSecs` | 59 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassProdAsk` | 3.6 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassProdDup` | 11.25 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassProdErr` | 11.31 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassProdLoss` | 0.06 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassProdPv` | 14.59 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimPassProdPvHi` | 15.32 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassProdSecs` | 16 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcAsk` | 60.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcDup` | 6.85 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcErr` | 8.25 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcLoss` | 1.40 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcPv` | 5.21 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcPvHi` | 5.68 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPassSrcSecs` | 59 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointAsk` | 60.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointDup` | 2.92 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointErr` | 4.31 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointLoss` | 1.38 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolJointSecs` | 69 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdAsk` | 3.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdDup` | 0.15 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdErr` | 0.24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdLoss` | 0.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolProdSecs` | 25 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcAsk` | 60.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcDup` | 2.80 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcErr` | 4.20 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcLoss` | 1.40 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimPoolSrcSecs` | 69 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTail` | 2.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex, tab_realsim.tex |
| `\RsimTailCalJointAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalJointDup` | 4.62 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalJointErr` | 6.72 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalJointLoss` | 2.09 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalJointSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdDup` | 4.62 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdErr` | 6.57 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdLoss` | 1.96 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalProdSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcAsk` | 100.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcDup` | 4.60 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcErr` | 6.88 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcLoss` | 2.27 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailCalSrcSecs` | 74 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoAsk` | 39.4 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoDup` | 0.27 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoErr` | 2.40 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoLoss` | 2.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailGtwoSecs` | 33 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailJointAsk` | 74.4 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimTailJointDup` | 3.08 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailJointErr` | 5.22 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailJointLoss` | 2.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailJointSecs` | 72 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailProdAsk` | 3.4 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailProdDup` | 2.24 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailProdErr` | 2.34 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailProdLoss` | 0.10 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailProdPv` | 2.77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | 07-real.tex |
| `\RsimTailProdPvHi` | 3.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailProdSecs` | 19 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesAsk` | 9.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesDup` | 2.63 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesErr` | 2.77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesLoss` | 0.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesPv` | 2.77 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesPvHi` | 3.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesSecs` | 26 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtyAsk` | 3.3 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtyDup` | 2.19 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtyErr` | 2.30 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtyLoss` | 0.11 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtyPv` | 2.62 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtyPvHi` | 2.96 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailRulesThirtySecs` | 45 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcAsk` | 74.4 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcDup` | 2.88 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcErr` | 4.87 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcLoss` | 1.98 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimTailSrcSecs` | 72 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointAsk` | 73.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointDup` | 3.05 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointErr` | 5.27 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointLoss` | 2.22 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkJointSecs` | 78 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdAsk` | 3.0 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdDup` | 0.08 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdErr` | 0.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdLoss` | 0.03 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkProdSecs` | 26 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcAsk` | 73.9 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcDup` | 2.99 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcErr` | 5.12 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcLoss` | 2.13 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcPv` | 0.00 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcPvHi` | 0.04 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RsimUnkSrcSecs` | 78 | measured-parameter simulation | planner_real.csv (planner_sim.py real; params.csv) | (unused) |
| `\RuleBestTenAsk` | 16.3 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | 07-evaluation.tex |
| `\RuleBestTenName` | wait 60 s, all but VLM | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | (unused) |
| `\RuleBestTenPv` | 0.47 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | (unused) |
| `\RuleBestThreeAsk` | 17.6 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | 07-evaluation.tex |
| `\RuleBestThreeName` | wait 60 s, any two | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | 07-evaluation.tex |
| `\RuleBestThreePv` | 0.10 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | (unused) |
| `\RuleMinAsk` | 16.2 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | 07-evaluation.tex |
| `\RuleMinPv` | 0.08 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | (unused) |
| `\RuleMinPvAsk` | 24.1 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | (unused) |
| `\RuleN` | 12 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | 07-evaluation.tex |
| `\RuleOver` | 1 | model-based simulation | planner_rules_sweep.csv (planner_sim.py rulesweep) | (unused) |
| `\SagaMaxDup` | 0.86 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaMixMaxEight` | 14 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaMixMaxFour` | 18 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaMixSave` | 5.6 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaNaiveSixteen` | 9.6 | exact | saga_*.csv (sim_saga.py) | 07-evaluation.tex |
| `\SagaPredEight` | 1.5 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaSaveEight` | 1.5 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaWorseSixteen` | 4 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SagaWorseTwo` | 38 | exact | saga_*.csv (sim_saga.py) | (unused) |
| `\SensPvHiMax` | 0.26 | model-based simulation | planner_sensitivity.csv | (unused) |
| `\SensPvMax` | 0.09 | model-based simulation | planner_sensitivity.csv | (unused) |
| `\ShareDigest` | 44 | model-based simulation | planner_share.csv | 07-evaluation.tex |
| `\ShareHop` | 69 | model-based simulation | planner_share.csv | 07-evaluation.tex |
| `\ShareNonce` | 63 | model-based simulation | planner_share.csv | 07-evaluation.tex |
| `\ShareSrcDigest` | 72 | model-based simulation | planner_share.csv | (unused) |
| `\ShareSrcHop` | 83 | model-based simulation | planner_share.csv | (unused) |
| `\ShareSrcNonce` | 73 | model-based simulation | planner_share.csv | (unused) |
| `\ShareSrcVlm` | 17 | model-based simulation | planner_share.csv | (unused) |
| `\ShareVlm` | 16 | model-based simulation | planner_share.csv | 07-evaluation.tex |
| `\SimAltered` | 37 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimAskAllAsk` | 100.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAskAllDup` | 4.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimAskAllLoss` | 2.7 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimAskAllLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAskAllP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAskAllPv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAskAllPvHi` | 0.04 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAskAllSecs` | 75 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixAsk` | 0.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixDup` | 34.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimAtomixDurAsk` | 0.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixDurDup` | 5.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimAtomixDurLoss` | 9.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimAtomixDurLv` | 21.8 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixDurP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixDurPv` | 7.8 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixDurPvHi` | 8.39 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixDurSecs` | 13 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixLoss` | 6.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixLv` | 13.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixPv` | 52.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixPvHi` | 53.36 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimAtomixSecs` | 14 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimBudgetRatio` | 21 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimCkptAsk` | 0.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimCkptDup` | 67.7 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimCkptLoss` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimCkptLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimCkptP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimCkptPv` | 100.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimCkptPvHi` | 100.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimCkptSecs` | 14 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostAsk` | 24.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | 00-abstract.tex, 01-introduction.tex, 07-evaluation.tex |
| `\SimGhostBg` | 2.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostCloss` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostDup` | 0.94 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostLoss` | 0.84 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostP` | -- | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostPv` | 0.05 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimGhostPvHi` | 0.12 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimGhostReads` | 4.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostSecs` | 35 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGhostVsAskAll` | 4.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoAsk` | 73.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimGtwoDup` | 2.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoLoss` | 2.8 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoLv` | 0.07 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoPv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoPvHi` | 0.04 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimGtwoSecs` | 55 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimHalfWidth` | 0.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimJointAsk` | 66.7 | model-based simulation | planner_sim.csv (planner_sim.py main) | 00-abstract.tex, 01-introduction.tex, 07-evaluation.tex |
| `\SimJointDup` | 3.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimJointLoss` | 2.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimJointLv` | 0.05 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimJointP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimJointPv` | 0.05 | model-based simulation | planner_sim.csv (planner_sim.py main) | 00-abstract.tex, 01-introduction.tex, 07-evaluation.tex |
| `\SimJointPvHi` | 0.12 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimJointSecs` | 71 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAsk` | 0.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskAsk` | 4.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskDup` | 6.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskLoss` | 0.88 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskLv` | 1.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskPv` | 8.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskPvHi` | 9.52 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyAskSecs` | 16 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyDup` | 6.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyLoss` | 2.6 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyLv` | 5.7 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeyPv` | 9.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimKeyPvHi` | 10.20 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimKeySecs` | 13 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajAsk` | 52.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajDup` | 5.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajLoss` | 2.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajLv` | 0.93 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajPv` | 4.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajPvHi` | 4.47 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimMajSecs` | 50 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimN` | 12{,}000 | model-based simulation | planner_sim.csv (planner_sim.py main) | 01-introduction.tex, 07-evaluation.tex |
| `\SimNoAskAsk` | 4.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoAskDup` | 0.23 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoAskLoss` | 9.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoAskLv` | 20.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNoAskP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoAskPv` | 0.02 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoAskPvHi` | 0.09 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoAskSecs` | 21 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalAsk` | 12.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNoCalDup` | 1.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalLoss` | 0.49 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalLv` | 0.18 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalP` | 0.06 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalPv` | 1.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNoCalPvHi` | 1.30 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalRatio` | 22 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoCalSecs` | 18 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestAsk` | 45.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNoDigestDup` | 1.8 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestLoss` | 1.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestPv` | 0.04 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestPvHi` | 0.11 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoDigestSecs` | 48 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopAsk` | 48.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNoHopDup` | 1.6 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopLoss` | 1.6 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopPv` | 0.05 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopPvHi` | 0.12 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoHopSecs` | 45 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNonceAsk` | 35.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNoNonceDup` | 1.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNonceLoss` | 1.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNonceLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNonceP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNoncePv` | 0.02 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNoncePvHi` | 0.09 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNoNonceSecs` | 43 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNonceAskAsk` | 14.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNonceAskDup` | 5.7 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNonceAskLoss` | 0.49 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNonceAskLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNonceAskP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNonceAskPv` | 7.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimNonceAskPvHi` | 8.13 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimNonceAskSecs` | 22 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimPUni` | 0.57 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRedoAsk` | 0.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRedoDup` | 63.3 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRedoLoss` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRedoLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRedoP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRedoPv` | 100.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRedoPvHi` | 100.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRedoSecs` | 14 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesAsk` | 23.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRulesDup` | 0.97 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenAsk` | 8.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenDup` | 1.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenLoss` | 0.36 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenLv` | 0.34 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenP` | 0.17 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenPv` | 1.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRulesLenPvHi` | 1.42 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLenSecs` | 21 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLoss` | 1.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesLv` | 0.29 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimRulesP` | 0.84 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRulesPv` | 0.52 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRulesPvHi` | 0.70 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimRulesRatio` | 11 | model-based simulation | planner_sim.csv (planner_sim.py main) | 01-introduction.tex, 07-evaluation.tex |
| `\SimRulesSecs` | 35 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcAsk` | 47.4 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimSrcDup` | 2.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcLoss` | 1.6 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcLv` | 0.02 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcPv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcPvHi` | 0.04 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimSrcSecs` | 53 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniAsk` | 23.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniDup` | 1.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniLoss` | 0.55 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniP` | 0.57 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniPv` | 0.02 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniPvHi` | 0.09 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimUniSecs` | 34 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyAsk` | 0.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyDup` | 11.0 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyLoss` | 15.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyLv` | 33.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyPv` | 16.2 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifyPvHi` | 17.04 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVerifySecs` | 14 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisAsk` | 19.8 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimVisDup` | 0.67 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisLoss` | 0.57 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisLv` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisP` | 0.06 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisPv` | 0.04 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisPvHi` | 0.11 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVisSecs` | 31 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVoneAsk` | 5.5 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVoneDup` | 2.8 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVoneLoss` | 1.1 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVoneLv` | 1.9 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVoneP` | 0.00 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVonePv` | 3.7 | model-based simulation | planner_sim.csv (planner_sim.py main) | 07-evaluation.tex |
| `\SimVonePvHi` | 4.12 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SimVoneSecs` | 20 | model-based simulation | planner_sim.csv (planner_sim.py main) | (unused) |
| `\SprtAllWithin` | all | exact DP / MC | sprt_validation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\SprtCells` | 24 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\SprtENfive` | 3.3 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | (unused) |
| `\SprtENthirty` | 22.5 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | (unused) |
| `\SprtGapMax` | 2.4 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | 07-evaluation.tex |
| `\SprtMCN` | 40{,}000 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | (unused) |
| `\SprtMCdev` | 0.03 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | appendix-proofs.tex |
| `\SprtRatioMax` | 1.28 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | (unused) |
| `\SprtSlackMax` | 13 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | appendix-proofs.tex |
| `\SprtSlackMed` | 2.4 | exact DP / MC | sprt_validation.csv (sim_sprt.py) | appendix-proofs.tex |
| `\StressCombined` | 0.42 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressCombinedAsk` | 47.9 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressCommon` | 0.19 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressCrossAsk` | 26.7 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressDoze` | 5.8 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressDozeAsk` | 46.1 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressDozeVone` | 11.2 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressGbreakLoss` | 0.00 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressGbreakVoneLoss` | 3.4 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressLag` | 0.98 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressLagCalAsk` | 48.7 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressLagHi` | 1.22 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressLagRules` | 0.95 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressMaxHi` | 0.58 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressMon` | 0.05 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressMonAsk` | 25.6 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressMonLv` | 0.00 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressNodedupDup` | 2.4 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\StressNodedupPv` | 0.05 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressNover` | 2 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressPersistVone` | 0.42 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressRoneVone` | 0.04 | model-based simulation | planner_stress.part*.csv | (unused) |
| `\StressRulesOver` | 3 | model-based simulation | planner_stress.part*.csv | 07-evaluation.tex |
| `\SweepAskHi` | 54.7 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepAskLo` | 10.4 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepJointTenAsk` | 8.7 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepJointTenPv` | 0.88 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepJointThreeAsk` | 27.3 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepJointThreePv` | 0.21 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepNocalLoPv` | 1.39 | model-based simulation | planner_alpha_sweep.csv | (unused) |
| `\SweepPvLo` | 0.53 | model-based simulation | planner_alpha_sweep.csv | (unused) |
| `\SweepSecsHi` | 53 | model-based simulation | planner_alpha_sweep.csv | (unused) |
| `\SweepSecsLo` | 21 | model-based simulation | planner_alpha_sweep.csv | (unused) |
| `\SweepTenAsk` | 10.4 | model-based simulation | planner_alpha_sweep.csv | 07-evaluation.tex |
| `\SweepThreeAsk` | 17.6 | model-based simulation | planner_alpha_sweep.csv | (unused) |
| `\SweepThreePv` | 0.10 | model-based simulation | planner_alpha_sweep.csv | (unused) |
| `\UserAskAllTwenty` | 28.2 | model-based simulation | planner_user.csv | 07-evaluation.tex |
| `\UserGhostTwenty` | 6.8 | model-based simulation | planner_user.csv | 07-evaluation.tex |
| `\UserGhostZero` | 0.03 | model-based simulation | planner_user.csv | (unused) |
| `\UserMajTwenty` | 19.4 | model-based simulation | planner_user.csv | (unused) |
| `\UserNonceZero` | 5.2 | model-based simulation | planner_user.csv | (unused) |
| `\UserRulesTwenty` | 6.4 | model-based simulation | planner_user.csv | 07-evaluation.tex |
| `\VlmEN` | 4.4 | exact / MC | nonce.csv (sim_nonce.py) | (unused) |
| `\WhyContra` | 2.2 | model-based simulation | planner_sim.csv | 07-evaluation.tex |
| `\WhyStruct` | 12.0 | model-based simulation | planner_sim.csv | 07-evaluation.tex |
| `\WhyTotal` | 22.4 | model-based simulation | planner_sim.csv | (unused) |
| `\WhyUncert` | 4.5 | model-based simulation | planner_sim.csv | 07-evaluation.tex |
| `\WhyWait` | 3.8 | model-based simulation | planner_sim.csv | 07-evaluation.tex |

## 2. Claim → evidence map

| Claim (where) | Evidence | Kind |
|---|---|---|
| Thm 4.1(a–d), Cor 4.2, Prop 4.3, Eq. (2), Prop 4.4 (+ source variant with Q(t)=1 for t≥1), Lemma 4.5 (exchangeable case: m2 for 2≤V≤(1−m2)/(ε−m2), strictly smaller above), Lemma 4.6 (fault-class keyed, unknown-class max, δ=min(α,β)/(10K)), Lemma 4.7, Thm 4.8 (dedup horizon D, device scope; necessity of the horizon in App. A), Prop A.1 | statements §4, proofs App. A | proof |
| Default world (Table 2): product P_v 0.05% (CP 0.12) at 24.9% asks; source 0.00% at 47.4%; joint 0.05% at 66.7% (33.8% at 5,000 labels); rules 0.52% at 23.9%; Thm-4.8-only 0.00% at 73.0% | `planner_sim.csv` | model-based simulation |
| Rule family (Fig. 3): best rule at P_v≈0.1% = wait 60 s, any two (0.10%, 17.6% asks) = product at α=0.03 (0.10%, 17.6%); at P_v≈0.5% product (α=0.1, no 0.5% guarantee) 10.4% vs best rule 16.3% (wait 60 s, all but VLM, 0.47%); joint at α=0.1 0.88% at 8.7%; no rule below 16.2% asks | `planner_rules_sweep.csv`, `planner_alpha_sweep.csv` | model-based simulation |
| Stress / population / drift (§7.5, Tables 6–7): unchanged except every ghost-src row (source-family fix) | `planner_stress.part*.csv`, `planner_ncal.csv` | model-based simulation |
| Sample sizes (Table 1): product median-case 163/221 and zero-event 127 (α=1%); joint zero-event 1,700, at true rate α_test/4 3,723; lag 4,649; ×4 when keyed by class | `sample_size.csv` | exact CP |
| RQ7 G2 (Table 3a): Element 83/83 exactly once (62 retry acked before fault + 3 same-txnId re-send = 65; 18 /sync reconciliation without re-send); sticky v2 20 = 2 + 18; timeout 6/6 once (3 clean); DAVx5+Radicale 8/8 (412 on same-href re-PUT, incl. 5 kill/force-stop); K-9 12+8 lost-reply trials: permanent error state, 0 new DATA on Sync/Send messages, stays in Outbox; Sent folder never shows it 8/8; GUI redo duplicated K-9 20/20 (distinct Message-IDs), CalDAV 3/3 | `campaign2/c2_element_outcomes.csv`, `c2_element_timeout_trials.csv`, `c2_caldav_trials.csv`, `c2_k9_*_trials.csv`, `c2_k9_families.csv` | EMULATOR measurement |
| Synapse horizon: same device → same event; other device → new event; re-login same device_id → same; restart → same; row aged 25 h (timestamp shifted) → duplicate | `c2_synapse_txn.csv`; source `events_worker.py` v1.164.2 | EMULATOR measurement + source |
| RQ7 lag (Table 3b): none 2.5/2.9/3.8; kill -9 4.0/8.0/13.6; force-stop 12.0/12.3/12.7; net cut 2.4/2.7/2.9; sticky 4.1/4.4/4.6 and 11.1/12.3/12.4; censored 0/101 (window ≥120 s) | `c2_element_lag.csv` | EMULATOR measurement |
| RQ7 families (Table 3c): Element first read ⊥ 33/101 (31/31 force-stop), wrong 3/68 all lag-blind (visible at 4.6–13.6 s); late 0/99 per family (⊥ 2); co-failure 0/101 [0–3.7%]; indicator same dump as row 101/101, 'Sent' 1,036/1,036; campaign-1 five co-failures re-scored ⊥ (0/5 contradicting state, digest showed nonce 4/5, screen identity not logged); K-9 Outbox 20/20, notification 15/20, Sent 8/8 (with Outbox 8/8), acked 0/10 | `c2_element_families.csv`, `c2_element_cofailure.csv`, `c2_element_poll_verdicts.csv`, `c1_rescored_cofailures.csv`, `c2_k9_families.csv` | EMULATOR measurement |
| Measured-parameter simulation (Table 4): Element keyed fault labels: product 0.00% (CP 0.04) at 3.0% asks, source/joint 0.00% at 72.9% (2,000/class) and 18.4%/12.7% (5,000/class), pooled 2,000 joint 60.3%; Thm-4.8-only 0.00% at 37.2%; rules 10 s 0.00% at 9.0%, 30 s 0.00% at 3.1%; trust app status 1.33%; passive product 14.59%, joint 5.21%; unlogged 2.9% tail product/rules 2.77%, joint 0.00% at 74.4%; logged tail all ask 100%; K-9 every mode asks 100%, trust 27.67% (+34.34% loss), rules 65.85%; K-9+Sent fault labels every mode 100% asks, rules 28.91%, passive joint 9.85% (2,000), product 9.84% (5,000) | `planner_real.csv` | measured-parameter simulation |
| Ledger qemu SIGKILL: FULL 0 lost (3), OFF 15–158 lost 3/3, NORMAL 0 lost but each transaction in its own process | `ledger_powerloss.csv` | EMULATOR measurement (campaign 1) |

## 3. Known soft spots (for the next round)

- No LLM agent, no VLM, no physical phone; GUI redo is a scripted recompose. E2EE rooms untested; K-9's unattended 15-min poll not measured (queued-mail lag law is an assumption).
- n small outside Element (K-9 2–4 per cell, CalDAV 8, timeout 3 clean); one emulator image; ~2 s read resolution (lags are upper bounds); Synapse 24 h ageing simulated by shifting a timestamp.
- Measured-parameter labels are simulated draws from laws estimated from 8–101 trials: a tail up to 2.9% beyond 14 s is not excluded; if unlogged it breaks product and rules, if logged every mode asks on Element.
- On Element, simpler mechanisms (Thm 4.8 only; rules with a 10–30 s wait) also hold the budget; certification's distinct value shows on K-9+Sent (rules 28.9%) and in its knob/guarantee, not in escalations on Element.
- Joint certification (recommended) needs ~5,000 labels per class per app version to escalate ~13% on Element; at 2,000/class it escalates 73%; default world 66.7% at 2,000.
- In the default world a tuned rule family matches the product mode at P_v ≈ 0.1%; the default world satisfies A2 by construction.
- Region-level shift test for pooling joint regions across versions not built; no LP-optimal certified policy / escalation lower bound; no user study.
- On-device controller, MockBank, injector, PRISM/Storm: not built/run. Anonymized artifact link not yet created.
