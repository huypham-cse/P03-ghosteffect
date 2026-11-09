# Review loops bổ sung — h100-plan-v6

## Material Passport

- 2026-11-08; giữ vòng5–8 như lịch sử v4 và thêm vòng9–12 kiểm full paper fidelity. Review inline, không tuyên bố reviewer độc lập/subagent mới.
- Chỉ sửa tài liệu/template, chưa benchmark server hoặc chạy thí nghiệm. Một H100 80GB/250GBRAM.
- Đã đọc current plan/resolve/experiments/setup/data/models/smoke/checklist/structure, draft §3–7.8/app table và meta-review; kiểm lại simulator RNG/Family/summarize và official deployment recipes.
- Vòng1–4 của v3 đã giảm full factorial nhưng chưa đủ để gọi tối ưu. Auditv3 là lịch sử, không dùng làm evidence cho scalev4.

Vòng13–16 dưới đây là review mới của v6. Các vòng5–12 giữ để trace lịch sử; đặc biệt đề xuất thử8AVD của vòng11 đã bị bỏ khỏi active core. Review thực hiện inline theo bốn lượt có trọng tâm khác nhau, không tuyên bố bốn reviewer độc lập. Không chạy model/AVD hoặc sửa manuscript/original code/raw. Các phép tính CP/reference nhỏ phục vụ audit planning, không phải experiment results.

## Vòng 5 — B1 review utility của sample, B2 đối chiếu paper

| Finding có evidence | Revision | Giữ đúng paper bằng cách nào |
|---|---|---|
| B0v3=960 effects nhưng320calibration-smoke bị chia n=10/cell, bound quá rộng | B0=320 characterization,80 dev/240 eval, không freshcalibration split | Small samples có thể ASK theo §5.3, không fake 1%certificate |
| C600+84extra có thể lặp hàng trăm ASK-only decisions vì thiếu realcalibration | C-native400 mặc định; A-guard20integration; C-guard200+12vetted OFF tới scientificgate | Algorithm1/alpha-beta giữ, usefulness/H4 chưa chứng minh thì ghi đúng |
| 16/40Ctasks bị gán pre-dispatchI1, không phải committed ghost hazard | 20X1/I3+20X0/I2 targets, class5/outcome | Native committed duplicate và actualabsent/loss đều có mục tiêu; I1 vẫn ởnegative controls/simulator |
| taskIDmod4 và odd/evenoutcome có thể confound class/outcome | Matchedpairs:class dựa pairindex, outcome dựa member | Balancedclass/outcome; task/app confounds vẫn công khai, không claim causal factorial |
| A-native bị kéo sau ledger/controller hoặc5modelroles | 30 native/dev trước,20guard integration sauhardgates | Meta-review chỉ cần ≥10actualvalid nativeK-9 cases; không dời milestone |

Kết luận: default878scheduled thay1802, không giảm alpha hoặc đổi thuật toán. Ba measuredstacks vẫn scoped;5 agents/40 variants giữ ởnative characterization, full futureappcatalogue/H4 không tự hoàn tất.

## Vòng 6 — B1 performance/fidelity, B2 kiểm nguồn

| Finding | Revision cụ thể | Acceptance |
|---|---|---|
| Cap16k/2 images/pixel1M tự đặt áp chung có thể đổi baseline | Context32k; upstream image/history/processor recipe; no silent truncation | S14history/coordinates và S15peakmemory trước freeze |
| Native UI-TARS/GUI-Owl bị giữ thêm V1idle, A phải đợi ba downloads | Qwen trước A, UI trước A3/A4, GUI trước A5; nativeA4/A5 engineđơn | Download/offline/identity stage cần thiết thôi |
| Processor resize và parsercoordinate defaults dễ lệch | Resolve pixelparams từ pinnedprocessor/recipe và truyền cùng parser | Round-tripfixtures; không chỉ modelID đúng |
| Repeated verifieranalysis gâycalls thừa | Offlineexact-input memoization(effect/view/image/prompt/model/decode) | Không tăng n hoặc reuse liveeffects/statechanged |
| Immutable observation-bank/new RNG harness bị nâng thành bắt buộc | Đọc code: sharedworlds, prng riêng theo policyindex; giữ historicallaw/coupling | Paired-world không identicalnoise, không tự coi McNemar invalid; common-noise diagnostic optional |
| Futuretree đòi nhiều services/modules trước M3A20 cases | Một reused stage runner, thinadapters và onecommit-slotID | Không generalintentengine/neworchestration/full saga |

Nguồn: [GUI-Owl7B official recipes](https://huggingface.co/mPLUG/GUI-Owl-7B) có32k và 5 image example; [UI-TARS source pin](https://github.com/bytedance/UI-TARS/tree/582f3a7ea5d285ee8ed9e2e84048d1ab01453c49) cho processor/action mapping; [vLLM memory controls](https://docs.vllm.ai/en/v0.11.0/configuration/conserving_memory.html). Không suy từ recipe rằng dual-engineH100 đã loadtest.

Kết luận: tối ưu scheduling/cache/downloads trước giảm thông tin quan sát. Hiệu năng tốt nhất và 7Bquality vẫn cần E18/S09, không được xác nhận bằng VRAM arithmetic.

## Vòng 7 — B1 adversarial audit, B2 sửa gaps còn lại

1. Plannedtargets bị nhầm validn: đổi counts thành scheduledattempts; review chỉ đóng khi ≥10verifiedcommitted/interruptednativeK-9 cases. Failedfate/injection/agentnocommit giữ ITT.
2. Unlimited “run until valid” cóthể đội cost/selectionbias: max1instrumentationretry/case, global88extra, max966defaultattempts; scientificfailures không rerun. Mọiattempts giữ ledger.
3. Emptydenominator cócode path max(1,n) trong summarize: historical giữ nguyên, newanalysis yêu cầuN/A và S01/E09regression; không rate0/noerrorclaim khi không cósamples.
4. BalancedX1/X0 không phải naturaldeploymentprior: conditionaloutcomes/benchmarkmixture và unknown/censoring riêng, không extrapolateprevalence.
5. B2v3 “3faultsubcells” không chốt Send/Sync/noaction đối chứng: đổi 15 trials=3actionpaths×5 trên một faultconfig, primaryactionwindow trước GUIredo.
6. A1/A2 vừa agentIDs vừa cohort cóthểlẫn: cohort dùng A-dev/A-native/A-guard, A1–A5 chỉ framework/modelroles.
7. B0 eval không đủ certificate: cấmexport/tune từ eval. C-guard phải có valid non-vacuousdomain và pre-registeredanalysis, thiếu thì deferred, không claimH4.
8. LiveASK/oraclesynthetic không được trộn thành observed finaloutcomes hoặcusefulness. Functionalfixtures cósyntheticcertificate để exercisebranches được gắn nhãn, không scientific1%data.

Kết luận: cácgaps được xử lý ởmức protocol/implementation requirements, chưa giả kết quả. Remainingdependencies làoriginalrig/servercompatibility/code/modelperformance/dataforCERT-1, không phải quota/phạmvi chưa quyết định.

9. Model memory topology khác giữa native .85 và protected .45+.45 có thể confound latency: quyết định C-guard trước final, paired arms dùng cùng resident services/fractions/load. Native đã chạy ở config khác không thành matched control cho late activation; study revision/budget mới cần thiết.

10. Equal-data có thể bị mất nếu M5 chỉ nhận80dev còn joint dùng CERT-1: baseline được cùng development/calibration labels và lag information, freeze trước independent evaluation. Calibration holdout khác final evaluation; không đòi baseline cóformalguarantee khi nó dùng thông tin để chọn rule.
11. Native vẫn bị S04/fullCPU suite chặn ở một runbook: tách CPUreproduction/correction track khỏi native-readiness; giữ numerical/ledger gates trước protected, không trước native observation.

## Vòng 8 — Snapshot audit v4, superseded về scope bởi v5

Đã kiểm 13 Markdown + .env.example: đủ E00–E34 (35), R01–R32 (32), S00–S15 (16), L00–L09 (10), T01–T40 (40) và M0–M8 (9); local links/anchors và code fences hợp lệ. Quota khớp A50+B0 320+B-target108+C-native400=878, retry cap88→966; nhánh C-guard bật từ đầu thêm212→max1178, không gồm CERT-1. B0 split80/240; C phân bổ5 tasks cho mỗi class/outcome. Model pins/.env/stage flags thống nhất, secrets trong template trống. Đã gỡ S04 khỏi native readiness ở cả runbook và smoke gates; S04 vẫn thuộc CPU reproduction track. SHA-256 của 239 original files khớp baseline, không sửa paper/code/raw; git diff --check đạt. Đây là kiểm tài liệu và số học, chưa phải chạy smoke/benchmark hoặc xác minh hypotheses.

## Trace10 mục meta-review

| Yêu cầu | Nơi xử lý trong v4 | Loại evidence cần |
|---|---|---|
| Clock/class và downtime5/15s | R03/E03/E10 | Reproducedwrong/correctorigin và timestamps |
| Lag20k/tied2k/5k/provenance | R04/E04/E18 | Existing/generated/unique/pilot/lag accounting, costforecast |
| Tail2,9%/5k | R05/E05 | Logged/unlogged P_v/CI/ASK, failures giữ |
| Equal-data vetted rules | R07/E06 | Cùngcalibrationinformation/devbudget; không cần 7livearms |
| Native LLM≥10K-9 | R08/E19 | Actualvalidcases, requestIDs/resend/CI; null giữ |
| Mode recommendation | R06/R32 | Jointcandidate/admissibleproduct/source; paperedits sau evidence |
| Nonce field/privacy/optin | R14/E26 | Actualsubject/bodyfield/contentdelta |
| Fittedlaw/sharedlaw/zeroerrors | R23/E08/E10/E11 | Provenance/uncertainty/independentsplits, không freshcertificategiả |
| Composedrisk/asks/users | R10/E08/E20/E30 | q1/q0/r0/r1 và observed/syntheticoutcomes tách đúng |
| Anonymousrigreproducibility | R25/R30/E00/E01 | Source/reconstruction/attempts/hash/recipe/export, chưa publish |

R29presentation/paperrewrite vẫn ngoài lượt này. Requirednumerical/clock/ledgerbug không hạthànhtext-onlyfix. C-guard/CERT-1 thiếu realdata thìH4/usefulness vẫn unverified, dùplan audit đạt.

## Kết luận phạm vi v4 — lịch sử

Default878 attempts làphương án đã sửa để vừa một H100 và trả đúng câu hỏi review; không chứng minh globaloptimum, fullappcatalogue, phone/OEM hoặcempirical1% trên mọistratum. Tiêu chí dừng review là current plan không còn conflict xử lý được bằng tài liệu và các dependency/limitations/gates rõ, không phải mọi hypothesis đều có kết quả thuận lợi.

## Vòng 9 — Đối chiếu lại full requirement, không chỉ review-core

Evidence: manuscript/sections/07-evaluation.tex lines99–104 nêu5frameworks/40tasks trên app table và GhostEffect end-to-end/H4; tab-apps liệt kê thêm Tasks.org/Joplin/SMS/MockBank/local apps. V4 chỉ T40 trên3stacks và để protected/calibration OFF như extension. Đây là thiếu scope thực sự, audit counts/links v4 không chứng minh full fidelity.

Revision: paper_draft/P01–P40 là default roadmap; T40 giữ prototype/review-core có nhãn riêng. P40 gồm10app/config entries×4task proposals, không thêm T400 trước P400. E20/H4/E31/E32 được giữ là required stages; startup false flags chỉ readiness. Package/Pro Expense identity và calibration acquisitions là dependencies mở, không bị lờ đi.

## Vòng 10 — Adversarial scientific/scale review

- Gate “có autonomous region mới enable” có thể chọn chỉ positive outcomes: bỏ positive-score eligibility. Unsupported/ASK-heavy vẫn trong denominator, null được giữ; thiếu calibration khác H4 fail sau test.
- H4 giữ risk contract +ASK≤1/3;200protected không chứng minh empirical1% mọi stratum. Arithmetic iid: zero/100→one-sided95% upper2.9513%; zero/200→1.4867%; zero-error n tối thiểu299 cho một endpoint1%, chưa multiple testing.
- P33–P40 là local-only; genericF3/F4 network allocation không áp dụng. P pin local kills, exactclass targets6/6/4/4 mỗi outcome; T vẫn5/5/5/5. Không fake receipt để giữ balance.
- H2 phải giữ paired view error counts/BOT và correlation N/A khi variance0; E21 heldout theo task/effect, không lấy stratified PPV làm deployment prevalence.
- 12M5cases là sentinel/wiring, không evidence live superiority toàn catalogue. H4 bootstrap resample taskblocks với five frameworks cùng block, không coi views/method arms là independentn.

## Vòng 11 — Performance và overengineering

Giữ oneH100, existing7Bpins, stageddownloads/twoengine cap, full history/input recipe và offline exact-input cache. Một runner/thinadapters/minimal app fixtures; không full saga/banking platform/service-per-role/newRNG framework.

Không dùng “4workers” làm chứng minh tối ưu. E18 có thể dành20dev effects cuối thử8 thay block4 thứ hai nếu resources đủ; tổng80dev giữ nguyên, inputs/dtype không giảm, chọn/freeze trước final. Full planned-app cost phải lấy từ actual development, không suy từ scriptedB0.

Milestone878 chưa protected/calibration/full app readiness. Required protected+sentinels đưa subtotal1090/max1178, calibration/app development chưa có aggregatecost. Không hứa2–6ngày là toàn paper; no downloads/experiments trong lượt revise.

## Vòng 12 — Completion audit v5

FINAL_AUDIT_V5_PASS — Đã kiểm14Markdown+.env.example: E35/R32/S16/L10/M9 và23baseline policy IDs khớp source; T40 và P40 không cộng dồn; P6/6/4/4 mỗi outcome, T5/5/5/5, local faults có applicability. Env chọn paper_draft/P01-P40/REQUIRE_H4=true/no scope downgrade, model pins/BF16/32k giữ nguyên. Totals878milestone/1090cóprotected, retry88→966/1178; B0split80/240, no eval-to-calibration leakage. H4 có q_ASK/q_manual guard và fixed300s follow-up, finite-n limits rõ; không positive-outcome eligibility. Links/anchors/fences/UTF-8/trailing-whitespace checks đạt; đã đọc lại15files và so nội dung.239original SHA-256 khớp baseline, dirty tracked files được giữ; git diff --check không báo lỗi (untracked docs kiểm riêng bằng Python). Đây là audit kế hoạch/source, chưa execution/benchmark.

V5 completion của lượt này là kế hoạch có procedure/evidence/gates/owners cho toàn yêu cầu, không giả runtime ready hoặc hypothesis đạt. Các executioncheckboxes vẫn mở. [Paper alignment](paper-alignment.md) là bảng requirement-to-evidence và các input tác giả phải xác minh.

## Vòng 13 — Đối chiếu lại draft PDF

Đọc trực tiếp PDF20trang, trích và xem trang11 (§7.8/H1–H4) và trang18 (Table10 apps), đối chiếu source evaluation/implementation/design và current plan/resolve.

| Finding trước revise | Sửa v6 | Mục tiêu kiểm chứng khi triển khai |
|---|---|---|
| Năm frameworks/40tasks/end-to-end vẫn đúng, nhưng P17–P20 ghi GreenMail trong khi Table10 nêu Postfix; GreenMail chỉ là measured substitution | A/B/history giữ GreenMail, P-final pin Postfix+localIMAP cho Sent/no-Sent; không thêm cohort riêng | Package/backend/request/grader/reset receipts và calibration đúng backend; không giả exact reproduction |
| H3 đã được chép vào plan nhưng chưa có actual WorkManager-based outbox/G2 app hay force-stop slots đã xác minh | E31 thêm capability/source eligibility và F2 subtype freeze; reuse C0/C2 khi phù hợp, thiếu thì NOT_TESTED | Same-key retry/outbox/relaunch/ACK/copies và valid n; LMK/force-stop khác nhau |
| Một số operational choices bị đọc như yêu cầu draft | Ghi riêng5frameworks/40tasks/catalogue/H1–H4 là draft;1090/7B/300s/88retries/1–2–4 là plan choices | Không đổi Algorithm1/alpha-beta/domain assumptions để đạt score hoặc vừa hardware |

Kết luận vòng13: phạm vi cốt lõi giữ nguyên. Sát hơn về backend và khả năng kiểm H3; full catalogue vẫn chưa ready vì APK/fixtures/Pro Expense identity còn thiếu. Không có claim paper đã được tái lập.

## Vòng 14 — Quy mô, calibration và inference

| Finding | Quyết định | Evidence đã kiểm ở vòng này |
|---|---|---|
| 878/1090 là tổng execution units hỗn hợp, không sample size cho risk1% per app/agent | Giữ quota, không tự thêm repeats; báo ITT/actual fate/task blocks và finite-n limitations | Tính lại50+320+108+400=878; +200+12=1090, retry88→966/1178 |
| CERT-1 5000holdout có thể bị hiểu là luôn đủ, hoặc OFF làm optional toàn bộ calibration | E09 tính actual K_total/n trước collection; optional recipe flag đổi thành RUN_CERT1_EXTRA_COLLECTION, protected coverage vẫn required | Với target.002/delta=.01/(10K), zero-exceedance n: K5=4255,K20=4947,K55=5453; CP(0,5000) ởK55≈.002181. K55 là minh họa, không K thực đã freeze |
| Chưa có budget cho useful coverage trên P catalogue; nhân11k/domain có thể quá lớn | Coverage/cost/ASK-feasibility table trước acquisition; một fixed collection plan, không full factorial hoặc collect-until-pass | No-data→ASK; forecast trên dev không cho phép bỏ unsupported tasks hoặc tune final. Actual q_min=U/N_epoch và ITT report sau run |
| E21 freeze chỉ ghi rõ ở mức C có thể khiến B0eval bị tái dùng tuning | Reader/classifier split/freeze trước B0eval240; heldout80 labels chỉ evaluation | Không tăng200annotations thành200episodes; còn phải thu labels thật |

Tính lại one-sided95% zero-error bound: n100→2.9513%,n200→1.4867%,n299→0.9969% dưới iid assumption cho một endpoint. C mỗi framework chỉ20committed interrupted targets/arm trước invalid cases; tổng1090 không sửa được thiếu n của từng cell. Không tăng quota khi chưa có mục tiêu inferential riêng.

Kiểm planning risks: giữ per-app/framework strata tránh aggregate reversal/ecological extrapolation; giữ ITT tránh survivorship/selection; không lấy50/50 injected outcomes làm natural prior; freeze before test và K_total tránh forking paths/multiplicity; correlation không thành causation; không reselect easy strata hoặc rerun model errors. Đây là kiểm thiết kế, chưa statistical validation trên fresh data.

## Vòng 15 — Hiệu năng và loại việc thừa

| Finding | Revision tối thiểu | Giới hạn |
|---|---|---|
| A3 cần Qwen workflow/executor + UI locator; cách ghi activeagent+V1 chưa chỉ rõ share, dễ triển khai3engines | Role→endpoint config: workflow/executor/V1 share Qwen, locator UI-TARS. A1/A2 share Qwen agent/V1; A4/A5 protected dùng native model+Qwen | Max2checkpoint engines; prompts/history/permission isolation. Chưa serving benchmark, không independence claim |
| Nhánh8AVD mở thêm tuning/load domains trước khi có throughput1/2/4 | Bỏ8core, giữ80dev20/20/40; kiểm thêm actual framework/topology bằng dev fixtures hiện có | Chọn mức tốt nhất trong mức đã đo, không gọi global optimum; không lấy scriptedB0 cost làm agent cost |
| Chỉ biết H100/RAM không xác nhận KVM/CPU/SSD/ABI | Preflight các tài nguyên đó trước model downloads lớn | Android BLOCKED nếu thiếu KVM trong target profile; GPU không thay VM acceleration |
| Tăng số modules/gates/campaigns dễ làm chậm native pilot | Giữ35E/32R/16S/10L, một runner/thin adapters/JSON-CSV manifests và one-effect commit slot | Không scheduler framework, service-per-role, full saga, pooling, model sweep hoặc app ngoài catalogue |

Tham chiếu kỹ thuật đã mở lại: [vLLM0.11 serving API](https://docs.vllm.ai/en/v0.11.0/serving/openai_compatible_server.html), [memory controls](https://docs.vllm.ai/en/v0.11.0/configuration/conserving_memory.html), [Android VM acceleration](https://developer.android.com/studio/run/emulator-acceleration). Shared-engine routing là inference/implementation choice từ request API, không chứng minh throughput hoặc full-context fit. Pins/model/input/32k/BF16 được giữ nguyên.

Các code blockers đã đọc lại và vẫn mở: `sample_size.n_rate` bisection không bảo đảm minimum (reference193 vẫn thỏa ví dụ R30); `run_all.sh` bare wait chưa check từng PID/REAL4; LaTeX `|| true`; ledger INSERT OR REPLACE/missing-ID/transitions/restart guards. Chỉ revise plan, không tuyên bố sửa xong code đó.

## Vòng 16 — Đọc chéo bản revise và nghiệm thu

Kiểm sau sửa và nghiệm thu nội dung:15Markdown và1template.env,116local links/anchors, UTF-8/fences/trailing whitespace không lỗi; giữ35E/32R/16S/10L và mapping đủ10meta requirements. B0split80/240 và quota878/1090/retry966/1178 đúng; P fault counts mỗi outcome6/6/4/4. Model SHA trong template khớp models.md;15env assertions về model profile/oneH100/32k/twoengine/load4/paper target/flags/quotas đạt. SHA-256 của238files hiện có trong artifact/manuscript/others và review/STATUS/README khớp trước lượt sửa, không thêm/sửa originals.

Global `git diff --check` còn báo trailing whitespace sẵn có ở review.md (Markdown hard line breaks); giữ nguyên file đó. Các tài liệu sửa trong lượt này đã kiểm whitespace bằng Python vì chúng đang untracked. Đây là document/math/integrity audit, không runtime execution PASS.

Những phần vẫn chưa thể xác nhận: original rig/raw/screens missing; Pro Expense identity; new APK/backend/Postfix/IMAP pins/reset; eligible WorkManager app; H100/KVM/SSD/full-recipe fit/throughput; actual calibration n/domain/cost. Không có `collab/` hoặc `collab.zip` trong checkout lượt này nên notebook mapping/execution chưa kiểm lại. Không dựng stub/framework mới để che việc thiếu bundle.

Kết luận review v6: quy mô hợp lý cho benchmark cơ chế, sát draft hơn ở các chi tiết nêu trên, chưa đủ rare-event confidence per stratum và chưa phải runnable/verified full paper study. Tiếp theo là implement/recover minimum rig và A-dev/A-native, thu dev/cost để khóa calibration/final; không cần thêm vòng thiết kế framework hoặc tăng quota ngay.

### Nghiệm thu nội dung theo yêu cầu reviewer và người dùng

Đọc chéo tiếp sau audit cấu trúc phát hiện và sửa R23 còn ràng calibration vào switch CERT-1, R21 diễn đạt V1 runtime chưa phân biệt native calls với paired resident allocation, và R14 chưa tách subject campaign cũ khỏi body final. Đã bổ sung local-only budget return theo design §5.4, Doze entry/exit trước GUI wake/relaunch, và optimistic Outbox không phải committed nonce evidence. Các sửa này nằm trong existing E09/E14/E23/E26/S01/S07/S10; không tăng quota/IDs hoặc thay Algorithm1.

| Meta-review bắt buộc | Resolution/procedure trong plan hiện tại | Bằng chứng đóng khi triển khai; trạng thái hiện tại |
|---|---|---|
| 1. Clock theo fault và downtime5/15s | R03, E03/E10/E20: recovery-origin deadline, unconditional fallback nếu thiếu independence | Timestamps/proof-domain + original/corrected CSV; protocol rõ, chưa fresh run |
| 2. Lag budget2k/5k/20k và unique labels | R04, E04: untied/tied rows, pilot/holdout/lag overlap và cost riêng | Reproduced tags/accounting; existing outputs không thành unique real labels |
| 3. Unseen tail2.9% tại5k | R05, E05: logged/unlogged/product/source/joint/vetted, giữ failure | P_v/CI/ASK/tail provenance; không có tail-immunity claim |
| 4. Equal-data vetted rules | R07, E06: cùng dev/calibration/lag information, freeze trước independent evaluation | Reproduced vetted rows/risk/ask/cost;12livecases chỉ wiring, không superiority |
| 5. Native LLM K-9≥10 valid cases | R08, E19:20scheduled A-native, actual committed+interrupted receipts | LLM resend/requestIDs/copies/CI và null; chưa có live LLM evidence |
| 6. Mode recommendation thống nhất | R06/R29, E06/E09: joint primary candidate, product khi A2 justified, source khi remaining independence justified, unsupported ASK | Chọn/freeze theo contract/dev, không theo final score; manuscript edits sau results |
| 7. Nonce private/subject/body/opt-in | R14, E26: default private; A/B subject, P-final body opt-in hoặc nonce OFF, optimistic rows excluded | Field/content/opt-in/config/grader receipts; không claim content unchanged hoặc nonce=idempotency |
| 8. Zero-error/shared fitted law | R23, E08/E10/E11: historical plug-in giữ scope, uncertainty/fresh independent evaluation | Measured/derived/assumed/synthetic labels tách; chưa coi simulated labels là empirical certification |
| 9. Composed duplicate/loss | R10, E30/E20: conditional q1/q0 + residual r1/r0, user sensitivity riêng | Event-level conditional asks/denominators/composed bounds; không lấy overallASK×.05 làm kết quả đã đo |
| 10. Anonymous reproducible artifact | R25, E00/E01/L09: source recovery, locks/manifests/raw-derived mapping và scrubbed export | Package/rig reproducibility trước submission; upload/publication là bước riêng, chưa tạo link giả |

Các nhận xét chi tiết R1–R4 vẫn truy về đủ R01–R32 ở resolve.md mục3. Readability/layout/citation optional chuyển backlog R29 đúng yêu cầu chưa viết lại paper. Phone/OEM/power chỉ deferred khi không claim; E24/E25 phải mở trước nếu sau này muốn claim đó. Không gọi các câu hỏi khoa học chưa đo là đã resolve bằng thực nghiệm.

| Yêu cầu của lượt review/revise | Evidence đủ để nghiệm thu phần kế hoạch |
|---|---|
| Bám paper và tinh thần phương pháp | PDF§7.8/Table10 đối chiếu source; plan§1 giữ GUI-only/write-ahead/nonce-digest/qualifiedhop1/Monitor/wait/CP/modes/ASK; local budget và field exceptions đã reconcile |
| Review nhiều vòng, sửa lỗi/lập lờ | Vòng13–16 ghi finding→revision→acceptance; bảng10meta ở trên và R01–R32 giữ trace; phần contradiction mới sửa trực tiếp thay vì chỉ thêm disclaimer |
| Hiệu năng và quy mô hợp lý | Giữ878/1090, fiveframeworks/40tasks; engine sharing/staged downloads/exact-input offline cache và measured1/2/4; finite-n/calibration cost được tách |
| Không overengineering | Không thêm framework/campaign/IDs; một stage runner/thin bindings, shared checkpoint engine, one-effect task;8AVD/fullsaga/pooling/service-per-role không core |
| Revise thành tài liệu dùng được | report/resolve/plan/matrix/models/setup/data/experiments/smoke/checklist cập nhật cùngv6; recipe flags/gates không mâu thuẫn với required paper target |
| Chỉ rõ chỗ cần xác minh, không giả đã có kết quả | App/rig/H3/backend/hardware/calibration dependencies có owner/procedure/status; runtime checkboxes mở; collab bundle missing được ghi, không fake notebook PASS |

Nghiệm thu này hoàn tất yêu cầu review/revise kế hoạch, không đóng E00–E34 hay tuyên bố hypotheses/runtime đã được xác minh. Các đầu vào cần tác giả/implementer giải quyết được giữ rõ để triển khai sau, không dùng chúng để đổi scope sang ba apps hoặc native-only.

## Vòng 17 — Core code và failure-path review sau ủy quyền sửa

Đây là audit inline tiếp theo, không thêm reviewer độc lập. Đã triển khai R30: guarded ledger; exact minimum search có SciPy reference; asymmetric delta; N/A/conditional counts; isolated checked runner cóREAL4; staged renderer/rollback; fail-fast build; exact nonce predicate. Kiểm32regressions trên Windows/Linux, full25-job numerical/artifact suite và300active-writer POSIX kills/3264taps/0violations. Không đổi generative noise/sample count/model/quota để tăng tốc.

Phản biện kết quả: full runner PASS chưa chứng minh archive tái lập byte-identical. So full aggregates phát hiện ghost-src và một ncal200 row lệch; rerun source trước sửa trên Windows/Linux và ncal200 xác nhận pre-existing source/output discrepancy. Giữ archive và old/new lineage, không sửa số để khớp draft. Measured-real/REAL4 point estimates vẫn khớp, CI có floating differences.

## Vòng 18 — Reconstruction protocol và ranh giới evidence

Người dùng xác nhận original rig không còn và cho phép dựng lại. `testbed/` dùng protocol đúng draft: Matrix/CalDAV/SMTP acceptance trước lostACK; preapply terminal reject giữ originalID blocked; sticky/withheld có receipts; ADB reader kiểm foreground/account/title/timeline/anchor/status/bottom; driver giữ BOT/censoring; grader oracle riêng; host controller durable trước tap và ASK khi thiếu certificate.

19tests qua cả Windows/Linux; actual pinned GreenMail protocol integration PASS4cases, SHA khớp historical JAR. Phản biện: đó là synthetic messages/fixture screens, không Android/native agent/calibration. Profile chưa freeze từ app thật thì BOT; noADB/APK/AVD và noKVM ở WSL được ghi trong preflight. Không đóng H4 hoặc thay five-framework pipeline bằng scripteddriver. [Evidence, inventory và remaining work](code-fixes.md), [cách setup/chạy](../testbed/README.md).

Review/plan vẫn giữ878/1090, P40/fiveframeworks, BF16/model pins, private nonce/visible opt-in, local budget/origin correction và required calibration acquisition. Không thêm campaign/framework/phone service hoặc quota bù source bị thiếu. Manuscript/raw/PDF chưa sửa; kiểm integrity238baseline files ở [INTEGRITY.json](../tmp/code-fixes-v6/INTEGRITY.json) ghi rõ các code files được phép đổi.

## Vòng19–22 — Tiếp tục resolve theo yêu cầu giữ core paper

[Biên bản và mapping code/paper](resolve-progress.md) ghi calibration/read-once/digest/classifier/GUIObserver/local-vLLM interface, negative controls, APK/backend setup, actual Synapse/Radicale protocol smoke và Pro Expense source identity. Windows/Linux component tests đã chạy; actual Android/model/calibration và P40/H100 gates chưa đóng. Hypothesis floating-boundary giải thích archived source-mode đã được kiểm và không giải thích được; giữ negative result, không đổi RNG/source aggregate để ép khớp. Đợt tiếp tục này vẫn active, không dùng chữ “review xong” để dừng implementation còn thiếu.

## Vòng 23–24 — Per-class clocks, effect binding và Android local

Đối chiếu lại §5/Algorithm1 và §6 với code: unknown-class max deadlines theo từng origin, original issue age cho Monitor, hop1 không nonce với pre-tap counts, Monitor bind đúng effect, lookalike skipVLM và guard activity/account/window tại dispatch.58testbed tests/host PASS, Linux có actualSIGKILL. Không đổi models/quota/hypotheses hoặc historical numbers.

Project-local emulator37.2.13/API33r17 x86_64 bootWHPX thật; smoke04PASS4stack-app startup/installedSHA/GUI. Phát hiện và sửa stale LastANR focus reader, install/path handling; giữ failed receipts.10APKs signature/manifest verified, gồm Element2ABIs và5catalogue candidates từ AndroidWorld pin; ProExpense binary đã resolve. Smoke05 cài thêm5apps nhưng SimpleSMS đang ở system role dialog nên NOT_READY; không gọi package installed là app/taskready. Trạng thái tiếp theo và receipts ở [progress](resolve-progress.md#vòng-24--setup-android-local-và-app-assets).

User chưa có SSH server, tiếp tục local. H100/model/5official-framework execution, actual profiles/accounts/faults/collector/calibration, H3 và P40 reset/grader/MockBank/Postfix còn mở. Đây là inline code/paper/evidence loops, không independent subagent review mới.
