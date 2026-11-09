# Checklist GhostEffect — h100-plan-v6

## Material Passport

- V10 đã có native AVD observation và scripted-response M3A/T3A BACK/reflection smoke. Không là model episodes/task completion; không đóng A-dev/A-native/calibration bằng fixture.67test cases có env skips và failures Android vẫn giữ; [progress](resolve-progress.md). Physical phone không dependency core.
- Số kết quả draft là minh họa theo người dùng; **khớp archive không là tiêu chí pass**. Nguồn chuẩn là run mới có source/config/receipts. Không còn blocker47.35%; các scientific gates bên dưới vẫn phải có actual evidence đúng scope.
- Không chỉnh paper theo yêu cầu mới nhất;21file generatedTeX/PDF đã khôi phục trước lượt refresh. V9 giữ numerical outputs riêng,66component cases ởWindows/Linux/agentenv và native binding tests thực chạy; SimpleSMSstartup PASS nhưng stable_tree=false. [Receipts và việc còn lại](resolve-progress.md); chưa đóng agent/reader/calibration gates.
- Trạng thái mới nhất: [v8, vòng25–26](resolve-progress.md), source/runtime local đã setup; M3A/T3A import được, chưa agent/model/campaign. Android input guard đã sửa, SimpleSMS role/capture còn NOT_READY/FAILED. Không đóng các checkbox scientific execution bằng import/startup smoke.
- 2026-11-08; review v6 đã chuyển sang core code fixes và testbed reconstruction được người dùng cho phép. [Evidence hiện tại](code-fixes.md); manuscript/raw giữ nguyên, chưa Android/LLM/H4.
- Limit một H100 80GB/250GB RAM. [Plan](plan.md)/[matrix](study-matrix.md) thay full-factorial/quota lớn của v2.
- L=legacy artifact, P=partial, N=chưa có new evidence, D=deferred. R/S/X theo [experiments](experiments.md); checkbox execution chỉ đóng khi có artifacts đúng scope.

## 1. Các thí nghiệm cũ có artifact

- [x] SPRT symmetric/asymmetric: `sprt_validation.csv` 24 dòng, `sprt_asym.csv` 8 dòng và log.
- [x] Calibration/correlation: 20/12 dòng; dữ liệu synthetic/exact, không real VLM.
- [x] Impossibility: 9 dòng; Bayes floor 19; cost policy 21; late commit 24; lag wait 12.
- [x] Saga exact/simulation: `saga_alloc.csv` 4 dòng, `saga_mixed.csv` 2 dòng.
- [x] Nonce noise simulation: `nonce.csv` 9 dòng, `nonce_before.csv` 1 dòng; không actual OCR corpus.
- [x] Restricted Markov: 7 dòng +1 PythonDP PRISM instance CSV; external PRISM/Storm chưa chạy.
- [x] Main planner: 24 policy dòng, 28 class dòng; workload 12.000 workflows/cell theo script.
- [x] Rules sweep: 12 dòng; alpha sweep 20 dòng; user-error sweep 20 dòng.
- [x] Stress/population: 6 parts, 95 dòng tổng (20+5 × 15).
- [x] Sensitivity 28 dòng; ncal/drift 29; decomposition 40; family share 15.
- [x] `planner_real.csv`: 59 dòng, 14 tags; measured-parameter simulation.
- [x] REAL4: 16 files/33 dòng, gồm `vet/vetk9/vetk9sent`, `lag2k/lag5k/lag10k/lag20k`, `boot10k`, `tail5/tail5tied`, `down5/down15/t0down5/t0down15`, `netlab/netlabkey`.
- [x] Host ledger benchmark: 1 CSV dòng +log; 300 process kills, 228,793 taps checked, 0 violations theo stored output; đây là historical host measurement.
- [x] C1 campaign: 72 app trials theo source summary, không full screen-validating reader.
- [x] C2 raw main: 101 Element+6 timeout+15 K-9 no-Sent+18 K-9 Sent+9 CalDAV=149 app trials.
- [x] Synapse 8-step scope/timestamp-aging sequence tồn tại; không 8 iid fresh app trials.
- [x] Emulator ledger FULL/NORMAL/OFF CSV tồn tại; 3 trials/mode theo summary; chưa physical-phone power study.
- [x] Build artifacts `main.pdf`/`main.log` và generated fragments tồn tại; không coi `|| true` runner là fail-fast verification.
- [ ] Giữ source/config/exit/schema/hash cho từng family trong run dùng báo cáo; không yêu cầu giải thích mọi diff với số draft minh họa.
- [ ] Truy nguồn active generator của `saga_het.csv` 5 dòng; chưa dùng làm claim mới.

`run_all.sh` nay gọi isolated `run_all.py`, gồm REAL4; renderer sinh `tab_real4.tex`. Full25jobs PASS với snapshot và các component refresh riêng. Người dùng xác nhận số draft minh họa: không cần claim byte-identical archive reproduction. Chi tiết ở [code-fixes](code-fixes.md).

## 2. E00–E34 và trạng thái thực thi

| ID | Phạm vi active | Bằng chứng còn thiếu (đều chưa hoàn tất) |
|---|---|---|
| E00 | R | [ ] Reconstruction có source ở `testbed/`; actual Android/profiles/reset và historical missingness còn thiếu |
| E01 | R | [ ] Runner/REAL4/render có25-job PASS; giữ manifest snapshot/component refresh cho run báo cáo, không gate bằng số draft |
| E02 | R | [ ] Core guards/restart/race và POSIX crash đã kiểm; actual agent/AVD dispatch boundaries còn thiếu |
| E03 | R | [ ] Origin controls5/15s, clock traces và corrected diff |
| E04 | R | [ ] Source/generated/unique/lag accounting, tied2k/5k; không empirical mass quota |
| E05 | R | [ ] Tail2,9% ở5k, fail-closed/domain/stress failures |
| E06 | R/S | [ ] Equal-data simulation/replay; C-guardOFF thì không live extras, M5conditional12 |
| E07 | R | [ ] Keyed/unknown/wrong-class receipts và budget |
| E08 | R | [ ] 3 fits×3 seeds×3 configs uncertainty, historical5 seeds giữ |
| E09 | R | [ ] Minimum/asymmetric/empty-rate có references; full stopping/domain/K_total và actual acquisition sizing còn thiếu |
| E10 | S B0 | [ ] Clocks/lag320shared effects,80 dev/240 eval,actualtruth/CI/censoring |
| E11 | S B0 | [ ] True absent/committed fate và pending challenge |
| E12 | S B1 | [ ] 15 verified causal cases |
| E13 | R/S B2 | [ ] 15 action-audit+8 unattended≥20min |
| E14 | R/S B0 | [ ] Stale/identity/digest corpus, synchronized screens/trees |
| E15 | S B0 | [ ] V1 Qwen7B,200balanced effects từ B0eval240, error/dependence CI |
| E16 | D X | [ ] Natural24h chỉ nếu mở claim; timestamp aging không thay |
| E17 | R | [ ] Missingness/ANR ledger và sensitivity |
| E18 | R | [ ] Actual oneH100 cost/1→2→4 AVD, frozen load |
| E19 | R A /S C | [ ] A-native30/dev; C-native400; ≥10validK-9 cases, no doublecountE20 |
| E20 | R A /R paper C | [ ] A-guard20; required C-guard200+12M5, calibration coverage và matched controls còn thiếu |
| E21 | S | [ ] 200 action labels (120 dev/80 heldout),50 double-label; recall/FN/FP |
| E22 | S B3 | [ ] 10 verified LMK events, process boundaries ởE02 |
| E23 | S B4 | [ ] 60 idle-state cases, actual state receipts |
| E24 | D X | [ ] Phone service/overhead chỉ khi mở scope, không core |
| E25 | R legacy /D physical | [ ] Existing/qemu audit; actual powerloss OFF |
| E26 | R/S B0 | [ ] Actual nonce field/opt-in/content attribution |
| E27 | D X | [ ] E2EE OFF; không bắt phone |
| E28 | R sim /D runtime | [ ] KKT/union-budget reproduction; full saga OFF |
| E29 | R sim /D real | [ ] Existing drift/no-pooling boundary; multi-version OFF |
| E30 | R sim /D human | [ ] q1/q0/composed sensitivity; human study OFF |
| E31 | R paper coverage | [ ] P01–P40/toàn app catalogue, pins/capabilities/fixtures/grader/reset; T40 chỉ prototype |
| E32 | R paper catalogue | [ ] MockBank-A/B tối thiểu, synthetic/test-only; chưa có code |
| E33 | D X | [ ] TinyLP chỉ nếu cần, không block core |
| E34 | D X | [ ] Một restricted external-checker instance nếu mở |

## 3. Attempt và scope ledger

- [ ] A-dev ten nofault development +A-native twenty native K-9 +A-guard twenty protected integration=50.
- [ ] B0=4 configs×2 outcomes×40=320;80development/240evaluation, không freshcalibration.
- [ ] B1/B2/B3/B4=15+23+10+60=108; A+B=478scheduled executions.
- [ ] C-native5×40×2(nativeinterrupted/nativenofault)=400.
- [ ] Default878scheduled; max1instrumentationretry/case/global88,max966actualattempts. Scientific failure không rerun.
- [ ] C-guard200+12M5 startup OFF tới readiness; required paper stage, subtotal1090/max1178 với88retrycap, chưa calibration.
- [ ] C-native20X1/I3+20X0/I2 targets/agent; T5/class/outcome, P6/6/4/4 theo local applicability; actual receipts. Balanced benchmark không natural prior.
- [ ] Calibration coverage/acquisition bắt buộc cho protected study; CERT-1OFF chỉ là candidate11k/một stratum. E09 phải tính actual K_total/lag/fixed n/cost trước collection; 5000 không mặc định đủ.

## 4. Những gì còn thiếu thật

- [ ] Originalshared-android/APK/ABI/backendrecipes/attemptlogs; missingthìreconstruction và unknownhistory.
- [ ] ActualserverCPU/KVM/NVMe/network; fullrecipe7Bpeakmemory/perf.
- [ ] Observation-only native tracing/barrier/grader/reset trước A-native.
- [ ] Guardedledger/controller/GUIrecovery trước A-guard; stablecommit-slotmapping, không semantic-intentframework.
- [ ] A2–A5adapter/40taskfixtures trước C-native, AgentProg bindingpatch và history/parseridentity.
- [ ] Actualfreshoutcomes/labels/CI; noexport B0evalcertificate, zero-denominatorN/A.
- [ ] C-guard calibration coverage/acquisition và paired controls còn thiếu; no score-based eligibility; phải đánh giá H4 để hoàn tất paper study.
- Phone/E2EE/human/full-saga/pooling là extensions. MockBank/new planned apps không chặn A/B nhưng là dependency của full P40, không được báo full paper done khi thiếu.

## 5. Setup L00–L09

- [ ] L00source/isolatedcopy/.envstageflags, không secretslog.
- [ ] L01oneH100/Linux/KVM/environment compatibility, chỉ táchvenvkhi cần.
- [ ] L02API33/ABI/APK/load1→2→4, không phonecá nhân.
- [ ] L03 AVD/app/backend/ledger/proxynamespaces/reset,actualclass/fate proof.
- [ ] L04 ba stacks trước A/B; P40/toàn catalogue required trước paper final. Pro Expense source identity đã verify, binary/UI/reset/grader còn thiếu.
- [ ] L05nativeM3A trước controller; onetask-onecommitslot.
- [ ] L06Qwen trước A,UI trước A3/A4,GUI trước A5; engine theo checkpoint. AgentProg workflow/executor/V1 share Qwen + UI locator, không3engines; A1/A2 agent/V1 dùng một Qwen engine.
- [ ] L07stage-specificS00–S15/fullrecipe32k/processor-parsermatching,no silent2-imagetruncation.
- [ ] L08default878/80dev240 eval/C-native; conditionalC-guard, boundedattemptretry.
- [ ] L09runnablehandoff/manifests/raw→derived→CI/scopes, publication riêng.

## 6. Revision audit

- [x] Additional loops9–12: đối chiếu §7.8/full catalogue/H4/finite-n/overengineering; evidence ở paper-alignment.
- [x] Historical revision v5 đã thống nhất oneH100/P40/paper_draft; vòng13–16 kiểm lại và sửa thêm chi tiết ở v6, không xem audit v5 là bằng chứng execution.
- [x] IDs/links/math/splits/T-P applicability/pins/flags/protected hashes kiểm trước final.
- [x] Không claim optimal performance/model parity/empirical1%/H4 hoặc full paper coverage khi chưa actual evidence.

Executioncheckboxes chỉ đóng bằng run/config/split/source/attempt/exit/raw/derived/CI artifacts đúng scope; revisionplan không đóngexperimentchecks.

## 7. Paper-target completion gates còn mở

- [ ] STUDY_TARGET=paper_draft, P01–P40; không silent T-registry fallback hoặc chạy thêm T400 mặc định.
- [x] Pro Expense identity từ pinned AndroidWorld: `com.arduia.expense`, APK candidate11; [nguồn/evidence](resolve-progress.md).
- [ ] Tất cả app/ABI/binary hash/signature/capability/reset/grader ready; E32 MockBank-A/B code còn thiếu.
- [ ] Calibration coverage table + actual CP/K_total/lag/domain/sample-acquisition budget chốt trước collection; CERT-1 một stratum không tự phủ catalogue.
- [ ] C-guard200+12M5sentinels được chuẩn bị như required paper stage; matched native controls/topology freeze trước final.
- [ ] H1–H4 estimands, fixed horizon, unknown/timeout/ASK handling và task-block sensitivity freeze; H4 ASK≤1/3 và risk status report, null giữ.
- [ ] E15 pairwise error counts/BOT/zero-variance N/A; E21 heldout task/effect labels; không inflation từ repeated views.
- [ ] Paper subtotal1090/max1178 chưa calibration và app development. Mốc2–6ngày chỉ milestone scenario, không full completion promise.

Kế hoạch chi tiết ở [paper alignment](paper-alignment.md). Các boxes thực thi trên vẫn mở; chỉ revision audit mục6 có thể đóng trong lượt sửa tài liệu.

## 8. V6: fixes và remaining readiness

- [x] Đối chiếu PDF trang11/18 với active plan, kiểm IDs/links/math/config consistency và original hashes sau revise; biên bản vòng13–16 ở [review-loop](review-loop.md).
- [ ] P17–P20 Postfix+localIMAP pins/delivery/Sent/reset/proxy/grader ready; A/B GreenMail giữ nguyên, calibration hai backend tách riêng.
- [ ] E31 ghi actual WorkManager-based outbox/G2 và F2 force-stop slots cho H3; thiếu eligible cases→NOT_TESTED, không dùng LMK thay thế.
- [ ] E21 reader/classifier split/freeze trước B0eval240, heldout80 không dùng tuning; report grouped action counts/recall/FN/FP.
- [ ] S15 verify shared Qwen serving/role isolation và full recipe cho từng topology; S11 core1/2/4, không8-worker grid.
- [x] Core fixes: checked isolated runner/REAL4, staged renderer/rollback, fail-fast build logic, minimum search, delta/N/A, guarded ledger và exact nonce optimization; [validation](code-fixes.md).
- [x] V7: bốn historical APK tải đúng SHA, Synapse1.164.2/Radicale3.9.0 local installation và protocol integrations PASS; calibrated compiler/runtime, durable read cache, digest/classifier và M3A/T3A local-model wire binding có tests. [Progress](resolve-progress.md).
- [x] Vòng23–24:58testbed tests/host; WindowsWHPX/API33r17 x86_64 AVD thực; signatures cho10APKs (gồm2ElementABIs), installed SHA/launch/capture của4measured-stack apps. Đây là startup/setup, không account/task/agent readiness. [Receipts](resolve-progress.md#vòng-24--setup-android-local-và-app-assets).
- [ ] E01/E02/E09 cần current run manifests, actual Android/agent boundaries và full proof-domain/stopping/K_total/acquisition design; không đóng bằng component tests hoặc khớp số draft.
- [ ] Nhận lại collab bundle để kiểm notebook mapping nếu tiếp tục workflow đó; hiện checkout không có bundle, không đánh notebook tests đã pass ở lượt này.

Không thêm campaign hoặc quota. Review đạt khi plan nhất quán; scientific/runtime readiness chỉ đóng bằng artifacts đúng domain.

- [x] Rà đủ10meta requirements và R01–R32; sửa R14/R21/R23 còn mâu thuẫn, local-only budget, nonce evidence và Doze measurement protocol. [Nghiệm thu nội dung](review-loop.md#nghiệm-thu-nội-dung-theo-yêu-cầu-reviewer-và-người-dùng) tách rõ planning completion và execution còn mở.
