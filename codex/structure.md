# Cấu trúc repo GhostEffect

## Material Passport

- h100-plan-v6, đối chiếu checkout hiện tại 2026-11-08; PROJECT_ROOT xác định tại server.
- Các cây “hiện có” phản ánh file đã nhìn thấy. Cây “dự kiến” chỉ là thiết kế, không phải modules đã được tạo.

## 1. Cấu trúc hiện có

```text
P03-ghosteffect/
├── STATUS.md                      Trạng thái draft; có cả đoạn cũ superseded
├── review.md                      Review packet hiện tại, bản tiếng Việt
├── report.md                      Audit trước: evidence/code/conflicts/E00–E34
├── resolve.md                     Quyết định kỹ thuật và mapping review
├── README.md                      Archive provenance/restore, không phải rig README
├── MANIFEST.tsv[.gz]              Manifest archive gốc
├── 01_root__small-items.zip       Archive gốc
├── artifact/
│   ├── README.md                  Script/result inventory và caveats
│   ├── run_all.sh                 Thin wrapper gọi isolated Python runner
│   ├── run_all.py                 Checked processes/fresh outputs/hash manifest
│   ├── tests/test_regressions.py  Numerical/state/failure-path regression
│   ├── scripts/                   13 Python files
│   │   ├── ge_core.py             CP/SPRT/DP/bounds/statistical utilities
│   │   ├── ledger.py              SQLite WAL/FULL, guarded transitions/replan/issue
│   │   ├── bench_ledger.py        Host timing và process-kill benchmark
│   │   ├── planner_sim.py         Generative world, policies, calibration, real/real4
│   │   ├── sample_size.py         Minimum theo ceil intervals, independent references
│   │   ├── real_params.py         C2 measurements → fitted/assumed parameters
│   │   ├── render.py              CSV → staging → publish/rollback generated output
│   │   ├── render_real.py         C1/C2 + planner_real/REAL4 → tables/macros
│   │   ├── sim_sprt.py            Exact/MC SPRT, calibration và correlation
│   │   ├── sim_impossibility.py   Floors, waits, costs, late commit simulation
│   │   ├── sim_saga.py            Budget allocation exact/simulation
│   │   ├── sim_nonce.py           Analytic/synthetic nonce-noise study
│   │   └── markov_planner.py      Legacy restricted DTMC/MC, không joint runtime
│   ├── prism/
│   │   ├── ghosteffect.pm         Restricted model có sẵn
│   │   └── ghosteffect.props      Properties; chưa external checker evidence
│   └── results/
│       ├── *.csv / *.log          Simulation, exact computation, host measurements
│       ├── planner_real.csv       59 rows measured-parameter simulation
│       ├── planner_real4_*.csv    16 files / 33 sensitivity rows
│       └── real/
│           ├── SUMMARY.md         C1/C2 protocol, measurements và limitations
│           ├── params.csv         name,value,provenance; derived/synthetic có nhãn
│           ├── e4_*.csv           C1 app/protocol/lag data
│           ├── e5_*.csv           C1 evidence-family data
│           ├── ledger_powerloss*.csv
│           └── campaign2/
│               ├── c2_element_trials.csv          101 main trials
│               ├── c2_element_timeout_trials.csv    6 timeout trials
│               ├── c2_k9_nosent_trials.csv         15 trials
│               ├── c2_k9_sent_trials.csv           18 trials
│               ├── c2_caldav_trials.csv             9 trials
│               ├── c2_synapse_txn.csv               8 protocol sequence steps
│               ├── c2_* derived CSVs              Lag, outcomes, families, polls
│               ├── pilot_*.csv                    Discovery, không final evaluation
│               └── logs/                          Request logs, hashes, excerpts
├── manuscript/
│   ├── main.tex / references.bib
│   ├── main.pdf / main.log / ...  Build outputs hiện có
│   ├── build.sh                   Hiện có || true; chưa fail-fast
│   ├── sections/                  Abstract–conclusion, proofs, app/position tables
│   ├── figures/                   Architecture và scenario figures
│   └── generated/                 CSV-derived macros/tables/figures đã có
├── others/
│   └── notes.md                   Number ledger/claim notes
└── codex/                         Tài liệu tạo trong lượt lập plan này
    ├── plan.md                    Thứ tự setup/run, scope, sample design
    ├── setup-data.md              Nguồn tải, environment, schema, preprocessing
    ├── setup-local.md             Redirect giữ link cũ, trỏ single-H100 runbook
    ├── setup-server.md            Runbook server L00–L09
    ├── models.md                  Five-agent models/HF snapshots/.env/inference
    ├── .env.example               Template cấu hình không secrets
    ├── study-matrix.md            Simulator catalog, P01–P40 final/T01–T40 prototype, quotas/applicability
    ├── paper-alignment.md         PDF requirement-to-evidence, hypotheses và dependencies
    ├── execution-placement.md     Local/server/phone scope và thời gian single-H100
    ├── review-loop.md             Biên bản đối chiếu nhiều vòng và audit cuối
    ├── smoke-tests.md             S00–S15, development search, gates/freeze
    ├── experiments.md             E00–E34, objectives/expect/cost/dependencies
    ├── structure.md               File này
    └── checklist.md               Artifact status, rerun/new-work checklist
```

## 2. Những thành phần chưa thấy trong checkout

`papers/shared-android/` được README/SUMMARY dẫn tới nhưng không nằm trong repo/sibling path đã kiểm. Các file `c2_element.py`, `c2_k9.py`, `faultproxy.py`, `ui.py`, `analyze_c2.py` có hash nhưng chưa có source ở đây. Không coi logs/source excerpts là source rig đầy đủ.

Sau khi người dùng xác nhận không có source gốc, đã tạo `testbed/` reconstruction: `faultproxy.py`, `ui.py`, `app_driver.py`, `controller.py`, `run_case.py`, `grader.py`, download/setup/preflight và tests. Có protocol integration, conservative GUI reader và durable dispatch boundary; chưa actual per-app profiles/Android receipts. [Inventory và cách chạy](../testbed/README.md).

Còn thiếu integrated official-agent bindings/classifier, actual calibration collector/certificate cascade/Monitor, snapshot/reset orchestration cho app, LMK/idle injector, semantic digest và P40 coverage. Android foreground service/human study không phải core host target. Numerical modules không tự trở thành Android runtime.

`others/citation-audit.md`, lịch sử `reviews/round*` và `artifact/retired/illustrative*` được tài liệu nhắc nhưng không thấy trong inventory hiện tại. Không tạo stub giả để lấp chỗ thiếu.

Vòng review v6 cũng không thấy `collab/` hoặc `collab.zip` trong checkout. Notebook00–06/downloader từng trao đổi chưa được kiểm lại; không coi numbering đó là mapping đã xác minh với S00–S15.

## 3. Implementation dựkiến: giữ tối thiểu

Không tạo một package/framework mới cho mỗi E-ID. Reuseupstreamrig và adapters, một stage-basedrunner đủ khiinterface đã rõ. Chỉtáchenvironment hoặcprocesskhicódependency/failure-domain/quyềnoracle lýdo thật.

```text
codex/
├── vendor/                  recoveredrig và pinnedupstreamsources
├── environment/             SDK/AVD/backends/venv hoặccontainerconfig cần thiết
├── models/                  modelSHAassets, tải theo stage
├── cache/                   HF/Torch/downloadcache trong project
├── runtime/                 runner, sharedADB/controller và mỏngagentbindings
├── data/                    source-index/dev/calibration/eval; acquisition sau coverage gate
└── runs/<id>/               manifest,attempts/raw,derived,summary/CI/logs
```

Cây này là layout dự kiến, không bắt buộc tạo đủ thư mục. Implementation hiện dùng `artifact/run_all.py`, `artifact/tests/`, `testbed/`, assets trong `runtime/`, validation trong `tmp/code-fixes-v6/`; không cần dời code chỉ để khớp sơ đồ. Không xây serviceperrole, counterfactual image bank, semanticintentengine, regionpooling, fullsaga hoặcphoneforegroundservice.
Controller phải outliveagentprocess, oraclegrader nằm ngoài decisionpath; ítfiles không có nghĩa gộpcredential/truth vào agent.
One-effecttasks dùng stable(run,task,commit-slot), không generalworkflowplanner mới. Runtimestart/stop/reset/exit-handling cócommands sau implementation, không lấydocs thaycoderunnable.

## 4. Chuỗi phụ thuộc hiện tại và dự kiến

```text
Historical C2 CSV → real_params.py → params.csv → planner_sim.py real / real4
Historical simulation CSV + real CSV → render.py / render_real.py → generated/*.tex
manuscript source + generated fragments → LaTeX build → PDF

Future fresh attempts + independent grader → raw immutable events/screens
    → schema/truth/clock/visibility preprocessing → dev/calibration/eval cohorts
    → frozen policy comparisons → aggregate tables/CI/cost → experiment report
```

Chuỗi future dừng ở experiment report trong scope hiện tại. Việc tích hợp results mới vào paper là lượt công việc khác.

## 5. Nguồn cấu hình và ranh giới version

Project root .env là cấu hình secrets lúc triển khai, không phải artifact; template không secrets nằm ở [codex/.env.example](.env.example). Loader phải resolve paths theo PROJECT_ROOT trước child/container launches. Không copy real .env vào manifests.

Model IDs/SHA/roles/inference lấy từ [models.md](models.md); task/policy/fault/quota từ [study-matrix.md](study-matrix.md). Không duy trì model matrix thứ hai trong source cũ rồi ghi alias trùng. Server source lock khác historical host stratum; current/predicted modules phân biệt bằng existence và runtime receipts, không bằng việc có tên trong cây này.


## 6. Active scope

Milestone878scheduled attempts; B0 320(80 dev/240 eval), C-native400, A50,Btarget108. Retryglobal88. Paper target dùng P40/toàn catalogue, required C-guard+sentinels212 đưa subtotal1090; startup OFF tới readiness. Calibration acquisition chưa chốt toàn domain; CERT-1 chỉ candidate recipe. OneH100, staged7Bdownloads, upstream image/history recipe. [Study matrix](study-matrix.md)là nguồn quota/gates; [models](models.md)là nguồn model/env. Inventorytree mục1làexistingfiles, runtime mục3làproposal tối thiểu.

## 7. V5 paper target và code inventory

[paper-alignment.md](paper-alignment.md) nối từng requirement draft với evidence cần tạo và code còn thiếu. P40/full catalogue và E32MockBank-A/B tối thiểu là paper dependencies, không core-only optional extensions. T40 là prototype; không hai main registries chạy cộng dồn.

Tree tương lai vẫn một stage runner/sharedcontroller/thinadapters, app fixtures dùng cùng init/grader/reset interface. Không cần banking platform/service-per-app, saga framework hoặc engine semantic mới. paper-alignment.md là tài liệu mới đã có; runtime/modules/tasks còn là proposal.
