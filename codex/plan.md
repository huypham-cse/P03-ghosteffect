# Kế hoạch GhostEffect — h100-plan-v6

## Material Passport

- V10: actual native AVD screenshot/a11y đãPASS; M3A/T3A BACK+reflection wiring cóPASS với **scripted response fixtures**, không model episodes/quality/calibration.67component cases PASS có skip theo env; ANR/emptyforest attempts vẫn giữ. [Vòng29–30](resolve-progress.md). Core không cần điện thoại vật lý; model-driven/full-task/injector/calibration/H100 gates còn mở.
- **Chỉ thị mới nhất: không chỉnh paper, paper để sau.** Không ghi vào `manuscript/`, kể cả generatedTeX/PDF; không chạy root renderer/build để publish. Lượt refresh số đã được khôi phục21files đúng hash trước lượt này. Chỉ làm code, plan/report và thí nghiệm; outputs/render tests dùng isolated directory.
- Chốt lại theo người dùng08/11/2026: **mọi số kết quả trong draft là minh họa; kết quả thực chạy có source/config/raw receipts mới là nguồn chuẩn**. Không yêu cầu khớp47.35% hoặc bất kỳ tỷ lệ cũ nào; không mất thêm thời gian truy nguyên để ép tái tạo số draft. Giữ phương pháp/pipeline/framework và thiết kế đã chốt, freeze tham số thiết kế trước run; hypotheses có thể bị bác bỏ. Simulator/fixture vẫn phải ghi đúng loại, không gọi thành Android/agent measurements.
- V9 giữ numerical outputs có provenance riêng; paper refresh đã undo. Factory M3A/T3A/native env/reconnect có binding tests, chưa actual gRPC/agent episode. Full66component cases có per-environment skip receipts; SimpleSMS mở được MainActivity nhưng unstable tree nên task/reader chưa ready. [Vòng27–28](resolve-progress.md) là status mới nhất.
- V8: đã setup đầy đủ pinned source bốn repo và Python3.11.8 local; M3A/T3A imports PASS, chưa native episode/weights. Guard window/input được tăng sau actual SystemUI ANR; SimpleSMS role đã gán nhưng startup/capture vẫn FAILED/NOT_READY. [Evidence và việc còn lại vòng25–26](resolve-progress.md). Setup/smoke không tính vào878/1090 hoặc calibration.
- Revision 2026-11-08; sau review đã sửa core code và dựng [testbed reconstruction](../testbed/README.md) theo ủy quyền mới. Regression/numerical/GreenMail evidence ở [code-fixes](code-fixes.md); Android local startup mới ở vòng24, chưa LLM/H4/model weights; manuscript/raw giữ nguyên.
- V7 tiếp tục [resolve-progress](resolve-progress.md): calibration compiler/Algorithm1 runtime/read-once/digest/classifier/model binding đã có component tests; bốn APK đúng historical hash đã tải; Synapse/Radicale đã cài và protocol integrations PASS. Không đổi core/quota/expected hypotheses; actual Android/LLM/calibration vẫn phải chạy.
- Vòng23–24:58testbed tests/host PASS; SDK37.2.13/API33r17 x86_64/WindowsWHPX và bốn app boot/install/hash/launch/capture smokePASS. Năm catalogue APK đã signature-verify. Chưa có serverSSH theo người dùng; tiếp tục local. App accounts/profiles/fault/agent/calibration khác startup smoke và vẫn required.
- Giới hạn một H100 80GB và khoảng 250GB RAM. CPU, KVM, SSD và hiệu năng inference chưa được kiểm trên server.
- Vòng 13–16 kiểm lại trực tiếp PDF trang 11/18, scale, dependencies và overengineering; quyết định mới ở [review-loop](review-loop.md#vòng-13--đối-chiếu-lại-draft-pdf). Giữ năm frameworks/40 tasks, không thêm campaign.
- [Ma trận](study-matrix.md) chốt cohort/task/quota; [đối chiếu paper](paper-alignment.md) chốt yêu cầu, kết quả cần đo và các việc tác giả cần xác minh.
- Runbook: [models](models.md), [setup](setup-server.md), [data](setup-data.md), [experiments](experiments.md), [smoke](smoke-tests.md), [checklist](checklist.md), [thời gian](execution-placement.md), [resolve](../resolve.md).

## 1. Những gì giữ nguyên từ paper

GUI-only controller ngoài agent; SQLite WAL/FULL; durable ISSUED trước tap; nonce gx:+6 symbols; pre-tap digest; qualified hop-1/G2/Monitor; certified wait; nonce/digest/VLM cascade; product/source/joint; ASK/PENDING và foreground recheck. Backend/DB chỉ nằm ở injector/grader/calibration, không đưa hidden truth vào decision path.

Algorithm 1: phân loại action → metadata/nonce/digest và durable issue → dispatch → fault/restart → hop-1/Monitor → wait khi cần chứng cứ end-to-end absence → evidence cascade → quyết định đủ ngân sách hoặc ASK/PENDING. Giữ t0=ISSUED; nếu lag law có recovery origin thì deadline=recovery-origin+wait. Không trừ downtime khỏi wait của law khác origin.

Nếu class chưa rõ và các class dùng origin khác nhau, phải có receipt cho từng origin và chờ `max_c(origin_c+w_c)`, đồng thời mọi class cùng certify action. Không cộng `max(w_c)` vào một clock tùy chọn. Thiếu origin→ASK. Monitor kiểm stuck/dedup age từ original ISSUED, không reset tuổi outbox lúc relaunch. Adapter/collector phải nối các clock receipts thật trước production; component tests không thay phần nối này.

Alpha=beta=.01; alpha split .5 test/.4 lag/.1 calibration, beta .9 test/.1 calibration; delta=min(alpha,beta)/(10 K_total). K_total phải tính đủ classes, bounds và stopping configurations. Wmax=120s additional wait; mỗi view đọc một lần. Giữ KKT/exact saga simulation; task live chính có một effect, không xây saga engine để chạy native milestone.

Ngoại lệ local-only giữ đúng design §5.4: không có hop2 nên trả lag share về test share (alpha_test=.9alpha, alpha_lag=0; calibration share giữ.1alpha), không áp network wait giả. Wmax kiểm phần chờ còn lại: max(0, origin+w−now)≤120s; origin phải cùng bảng lag. Early hop1 decisions chỉ dùng khi qualification/proof đúng; không mở early end-to-end reads mới để tăng tốc.

## 2. Đích hoàn thành và phần có thể chạy trước

Đích là kế hoạch thí nghiệm bám draft §7.8: năm frameworks, 40 effectful tasks trên catalogue trong bảng apps, native duplicate/loss/false-success, VLM error/correlation, real LMK/idle lag, classifier recall và GhostEffect end-to-end/H4.

Có thể chạy A/B trên ba stack đã đo trước để sửa wiring và đáp ứng review. **878 lượt là ngân sách milestone A/B + C-native, chưa phải toàn bộ thí nghiệm của paper.** C-guard và catalogue còn thiếu là công việc phải triển khai để đánh giá device-study target, không bị loại chỉ vì chưa có code/calibration.

Hai registry có mục đích riêng:
- T01–T40: prototype trên ba stack đã đo, dùng cho development hoặc một study review-core có nhãn phạm vi riêng.
- P01–P40: allocation chính cho paper, gồm 10 app/variant entries ×4 task proposals; xem matrix. Pin app, task fixtures và grader trước final. Đây là lựa chọn phân bổ để hiện thực hóa draft, không phải quota do draft quy định.

STUDY_TARGET mặc định là paper_draft, dùng P01–P40. Không tự chạy cả T400 rồi P400. Nếu chọn review_core thì không được báo đã hoàn tất paper target; đổi registry sau final cần study version/control/budget mới.

## 3. Quy mô và các khoản chưa thể chốt

| Gói | Scheduled executions | Mục tiêu |
|---|---:|---|
| A-dev | 10 | M3A no-fault development, wiring và trace |
| A-native | 20 K-9 targets, 10 Sent/10 no-Sent | Đo native resend sau committed/lost-ACK; cần ≥10 actual valid interrupted cases để đóng yêu cầu review |
| A-guard | 20 | Protected integration, ledger/restart/ASK; không gọi ASK-only smoke là H4 |
| B0 | 320, gồm 80 dev/240 eval | Clock, fate, lag, screen/verifier characterization và cost |
| B-target | 15 causal +23 K-9 action/unattended +10 LMK +60 idle =108 | Kiểm tra cơ chế có receipt |
| C-native | 5 frameworks×40 tasks×2 native arms=400 | Interrupted và no-fault trên registry đã freeze |
| Milestone A/B+C-native | **878** | Chưa gồm protected final và calibration còn thiếu |
| C-guard | 200 protected interrupted | Đánh giá GhostEffect end-to-end trên cùng 40-task distribution |
| M5 sentinel | 12 | Kiểm vetted-rule wiring; không đủ để suy rộng superiority của baseline |
| Tổng có protected | **1090** | Chưa tính calibration/fixture development còn thiếu |

Mỗi case tối đa một instrumentation retry, global cap88 extra attempts: max966 cho milestone hoặc max1178 cho 1090 scheduled. Scientific/model failures không rerun để lấy kết quả thuận lợi. Counts là các execution units hỗn hợp, không iid sample size.

Không tự cộng 11.000 effects cho mỗi app/agent. Sau E09, lập coverage table cho app/backend/reader/model/fault/origin/load và nhu cầu labels/lag thực tế. CERT-1 (500 pilot+5000 holdout mỗi outcome) là một candidate recipe cho một stratum, không chứng minh đủ cho toàn catalogue. Calibration thật còn thiếu phải có collection plan trước protected final; không thay bằng bootstrap/fitted simulation.

## 4. Gate protected và tiêu chí đánh giá

RUN_PROTECTED_BENCHMARK=false là trạng thái ban đầu trước readiness, không phải bỏ E20/H4 khỏi đích paper. Freeze native/protected cùng model, input/history, task seeds, load và resident-engine topology trước final để có matched controls. Không dùng native .85 single-engine làm control cho protected .45+.45 nếu so latency/cost.

B0 không xuất runtime certificate. Loader/CP/stopping smoke dùng synthetic reference fixtures có nhãn rõ. Autonomous action chỉ được phép với certificate đúng domain; unsupported/uncertain → ASK/PENDING, vẫn giữ trong final task distribution và denominator.

Không yêu cầu phải thấy autonomous region hoặc score tốt mới cho phép đánh giá H4. Valid calibration dẫn tới ASK100% là kết quả âm, không được bỏ stratum hay chọn app dễ sau khi thấy kết quả. Nếu chỉ thiếu calibration thì H4 đang thiếu evidence. Nếu quyết định không chạy các case đã chứng minh toàn ASK, chỉ được báo phân tích/reference, không báo measured end-to-end.

H4 giữ đúng hai vế: risk trong ngân sách theo contract và ASK ít nhất 3 lần thấp hơn always-ask. Với one-effect tasks, tỷ lệ ASK mục tiêu ≤1/3; báo riêng unresolved/timeout/task failure, không coi các lỗi đó là thành công tự động. CI, unit và population phải được chốt trước final. 200 protected episodes không tự đủ để chứng minh empirical risk≤1% cho mọi app/agent. [Paper alignment](paper-alignment.md) nêu estimands và cách diễn giải inconclusive/null.

## 5. Thứ tự thực hiện

1. E00 tiếp tục từ `testbed/` reconstruction: người dùng xác nhận không có source rig gốc. E01 đã có isolated25-job run và các component refresh; **khớp số draft không phải gate**. E02/E09 giữ core correctness/tests. Actual Android/profiles/calibration và E03–E09 scientific checks chưa được đóng chỉ vì smoke PASS.
2. A-dev/A-native sau model, barrier, trace, grader/reset gates. Không bắt đợi controller và tất cả adapters.
3. Sửa ledger/controller rồi A-guard. B0 dev80 chọn reader/load/classifier trước eval240; E15 lấy200 effects từ eval, E21 gắn200 action labels từ traces, ≥50 double-label.
4. Hoàn thiện P01–P40 cùng app capability/reset/grader, năm adapters và certificate coverage table. Pro Expense đã định danh `com.arduia.expense` từ AndroidWorld pin; cần binary/hash/signature/UI fixtures, không thay app.
5. Chốt calibration acquisition/evaluation design, H1–H4 estimands và matched topology. Thu calibration riêng nếu còn thiếu. Đây là dependency cần giải quyết, không dừng roadmap ở native benchmark.
6. C-native và C-guard theo frozen task blocks; B-target chạy sau gates liên quan. Giữ null, unknown, failed injection và actual valid n. Không run-until-pass.
7. Xuất evidence pack/report với raw attempts, CI, cost, model/stratum/coverage limitations. Chưa viết lại paper hoặc publish.

## 6. Hiệu năng trên một H100

Qwen2.5-VL-7B, UI-TARS1.5-7B và GUI-Owl7B BF16 là backbone variants có pin. Draft không chốt backbone; chưa có evidence rằng 7B ngang Gemini/72B. M3A/T3A/AgentProg/UI-TARS/Mobile-Agent phải giữ roles/history/parser/action semantics.

Tải theo stage; resident tối đa hai services; native A4/A5 không giữ verifier idle khi chạy study native-only. Context32k và upstream input/history recipe, không silent truncate. Giảm concurrency trước dtype/input. Matched protected study vẫn dùng cùng topology ở controls.

E18 chỉ đo 1→2→4 AVD trong kế hoạch chính, giữ allocation 20/20/40 của 80 dev effects. Chọn mức có full-cycle throughput tốt nhất trong các mức đã đo và qua gates; không mặc định 4 nhanh hơn 2. Bỏ nhánh thử 8 để tránh mở thêm load domain/calibration và tuning. Dùng dev fixtures sẵn có kiểm thêm tải model của từng framework/topology, vì B0 scripted không đại diện mọi agent. Batch/concurrency chỉ đổi trên dev, phải S15 pass trước freeze; giữ model/input/history/dtype.

Memoize offline đúng effect/view/image/prompt/processor/model/decode. Không cache live actions xuyên effects hoặc tạo counterfactual screens. Historical simulator giữ luật/RNG/coupling gốc; không dựng observation-bank framework.

## 7. Các extension thực sự ngoài đích chính

Physical-phone/OEM/power, human-response study, E2EE, natural24h retention, full saga runtime, pooling và LP/checker lớn chỉ mở khi có claim riêng. Tasks.org/Joplin/SMS/MockBank/expense/Markor thuộc planned app coverage của §7.8; chúng khác các extension này và không được gộp thành “không cần cho paper”.

Chưa có benchmark để hứa thời gian hoàn tất full paper study. Mốc2–6 ngày chỉ áp dụng scenario milestone878 khi rig/code sẵn; đọc [execution placement](execution-placement.md) trước khi đặt lịch server.

Với paper_draft/REQUIRE_H4_EVALUATION=true, C-native final và C-guard là cùng matched study: thiếu coverage/calibration/topology readiness thì chưa freeze/chạy final C. A/B và development vẫn tiến hành. Không tự hạ sang native-only để báo paper hoàn tất; review_core là scope riêng phải chọn rõ trước final.

H4 không được đạt nhờ timeout/abandon: báo q_manual gồm ASK/unresolved/recovery failures và yêu cầu cả q_ASK, q_manual≤1/3 trên valid recovery epochs, cùng ITT/coverage. Fixed live follow-up H_eval=300s từ recovery origin (nofault: primary commit dispatch), giữ namespace tới horizon; hết thời gian không phải terminal absence proof.

## 8. Quyết định vận hành sau review v6

| Điểm | Quyết định thực hiện |
|---|---|
| Quy mô | Giữ 878 milestone/1090 có protected và sentinel, cap 88 instrumentation retries. Đây là ngân sách benchmark cơ chế, không 1090 mẫu iid và không bao gồm calibration hay fixture development. Không thêm full factorial hoặc model sweep. |
| Mail backend | A/B và historical replication giữ GreenMail. P17–P20 final bám bảng apps của draft: Postfix + local IMAP cho Sent/no-Sent. Pin backend/version/reset trước freeze; calibration GreenMail không tự chuyển sang Postfix. |
| Nonce field | Default private-only/visible opt-in như design. A/B mail giữ subject; P17–P20 final dùng body theo app table nếu opt-in, nếu không nonce OFF. Không đổi field hoặc strip tag ngầm; reader/grader/calibration phải biết actual field/ON-OFF config. |
| Model resident | Một engine cho mỗi checkpoint cần thiết. AgentProg workflow/executor và V1 dùng chung Qwen engine, locator dùng UI-TARS: hai engines, không ba. Tách prompts/history/permission giữa roles. Xem topology ở [models](models.md#8-topology-thực-thi-v6). |
| Calibration | Coverage/acquisition plan là dependency bắt buộc của protected study; CERT-1 là một recipe tùy chọn. E09 tính actual K_total/n trước collection; không mặc định 5000 đủ hoặc nhân 11000 cho mọi domain. Forecast phần task buộc ASK trên dev để biết H4 có khả thi trong ngân sách; không thay population để được score tốt. |
| H3 | E31 xác minh WorkManager/outbox và G2 trước. Nếu có eligible app trong P40, freeze force-stop subtype cho các F2 task phù hợp và dùng C0/C2 receipts; không mở campaign mới. Không có eligible app hoặc valid cases thì H3 chưa được kiểm định, không đổi LMK thành force-stop. |
| Implementation | Một runner theo stage, thin adapters, một config và các manifest tối thiểu. Giữ S00–S15; schema có thể là JSON/CSV đơn giản. Không thêm scheduler framework, service-per-role, saga runtime, pooling hay app ngoài catalogue. |

Các điểm không thể đóng bằng review: actual task fixtures/reset/grader, H3 eligibility, actual H100/multiAVD fit/throughput và measured calibration acquisition. Missing raw cũ chỉ là giới hạn nếu muốn tái sử dụng claim lịch sử, không chặn thí nghiệm mới; số draft đã được người dùng xác nhận là minh họa. Pro Expense identity/binary/signature, backend pins/install/protocol smoke và local AVD startup đã có evidencev7; không tiếp tục ghi chúng là hoàn toàn chưa biết. Chưa có cơ sở gọi tối ưu toàn cục hoặc bảo đảm H1–H4 sẽ đạt.

Checkout ở vòng review này không có `collab/` hoặc `collab.zip`. Chưa kiểm được notebooks 00–06/downloader; numbering của notebook trước đây không tự tương ứng S00–S15 trong tài liệu này. Khi nhận lại bundle, chỉ cần đối chiếu mapping/gates, không xây thêm một smoke framework.
