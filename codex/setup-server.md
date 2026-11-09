# Setup tối thiểu trên một H100 — h100-plan-v6

## Material Passport

- V10 local: forwarder APK từ URL của AndroidEnv1.2.3 đã pin/hash/signature verify, native AndroidWorld screenshot+a11y observation đã có AVD receipt. Native model episode/P40/calibration và H100 runtime còn chưa kiểm. Không cần điện thoại vật lý cho core; không chỉnh paper.
- 2026-11-08; local core/protocol smoke và GreenMail download có [receipts](code-fixes.md). Chưa có H100/Android/model runtime receipts; tiếp tục từ [testbed reconstruction](../testbed/README.md), không chờ source rig gốc mà người dùng xác nhận không còn.
- V7: bốn historical APK đúngSHA đã tải, Synapse1.164.2/Radicale3.9.0 đã cài local và real protocol integrations PASS. [Trạng thái mới](resolve-progress.md) supersede “chưa setup” của v6; actual server/Android/model/calibration vẫn cần kiểm.
- Vòng24 local Windows đã có actual WHPX boot/API33r17 x86_64,4stack-app installedSHA/launch/GUI smokePASS và10APK signature checks; khác historicalARM64 stratum. Người dùng chưa cóSSHserver. Không coi local startup là H100 readiness/model inference hoặc Android fault/agent/calibration.
- Một H100 80GB/250GB RAM; CPU/KVM/NVMe/network/ABI compatibility phải kiểm thật.
- Milestone878 theo [matrix](study-matrix.md); paper target P40/toàn catalogue và required protected đưa subtotal1090, chưa calibration. Startup C-guard/CERT-1 flags OFF vì chưa ready; phone/full saga là claim riêng.

## L00 — Source và stage flags

Hash originals/dirty state, isolated work copy trước generators. Recover shared-android/APK/AVD/backend source; thiếu thì reconstruction có nhãn. .env từ [.env.example](.env.example), ignore trước secrets, không log/export real.env.
Khởi đầu A/B/development; protectedbenchmark và livevetted flags false tới readiness. Paper C-native final phải freeze cùng C-guard/matched controls trước collection, không tự chạy native-only final. Native pilot model/rig có thể ready trước full controller.

## L01 — Runtime vừa đủ

Kiểm Linux/NVIDIA, CPU architecture, quyền truy cập KVM, virtualization và local SSD trước tải model/dựng nhiều AVD. H100 không thay VM acceleration của emulator; [Android hardware acceleration](https://developer.android.com/studio/run/emulator-acceleration) mô tả yêu cầu hypervisor/CPU/image. Nếu server thiếu KVM thì Android stage BLOCKED; CPU audit/model smoke có thể tiếp tục, không lấy software-emulation timing làm paper profile đã đạt. Numeric Python/SQLite stdlib giữ riêng; rig/agent deps dùng một environment chung nếu compatible, chỉ tách khi conflict thật. vLLM0.11.0 base container pin digest/deps sau smoke. Không globalpackage changes hoặc service-per-role framework.

Tensorparallel1, một GPU. Mộtengine memoryfraction≤.85; hai engines≤.45+.45 banđầu. Max2residentservices, không default90% mỗi engine. KV/vision/graph/runtime peak phải đo; dtype BF16/sourceUI-TARSF32 cast ghi đúng.

## L02 — Android OS/API33

Pin Android13/API33 image, resolution/font/locale/timezone/keyboard/animation/serial và APKs. Historicalarm64/r17 recover khi có; x86_64/KVM port cần compatibleAPK/image và newhash, ghi portability stratum. Không gọi timingbyte-identical.

Khởiđộng1 AVD, benchmark2/4 sau E18; trần4 phụthuộc actualCPU/KVM/NVMe, không chỉ 250GBRAM. Không phone cá nhân hoặc OEM/power claims.

## L03 — Reset/isolation/load

Mỗi worker có AVD/app/backend/account/room/mailbox/calendar/ledger/proxy namespace riêng. Reset cả backend và app, stale queue/receipt phải cleared theo recipe. Fault ảnhhưởng intended path, không cắt cảinference/grader.

Agent/controller/verifier không có oracle credentials/truth. Hostcontroller tách agentprocess; grader/proxy nằmtestapparatus. B0 dev đo load1/2/4 trước chọn final load; không dùng eval240 hoặcnative final để tune.

## L04 — Ba measured stacks trước

Element1.6.62/Synapse1.164.2; K-9 24.0/GreenMail2.1.2 no-Sent/Sent; Etar1.0.57/DAVx5 4.5.21-ose/Radicale3.9.0. Hash/source ở [setup-data](setup-data.md). Historical/A/B giữ GreenMail; P17–P20 final dùng Postfix + local IMAP theo draft, với version/hash/config/reset riêng. Không ghi đè lịch sử hoặc chuyển calibration giữa hai backend.

Chỉtest accounts/synthetic content/externaldeliveryoff. Independentgrader cóIDs/commit/fate;40 taskvariants một effect chính/task. Sau A/B, paper target cần P40 trên toàn catalogue: pin/setup Tasks.org/Joplin/SMS/MockBank-A/B/Pro Expense/Markor theo capability. Minimal fixtures, không xây platform mới. Pro Expense `com.arduia.expense` đã có source/binary/hash/signature/startup evidence; actual task/reset/grader còn cần hoàn thiện, không chờ tác giả đoán identity.

## L05 — Code theo đường chạy nhỏ nhất

1. Rig/proxy/barrier/recorder/grader/reset đủ A-native. Postcommit/preACK và preapplyterminalreject córeceipts; requestretries phải được fate tracking.
2. PinnedM3A adapter+observation-only tracing; A-dev development rồi A-native20. Không yêu cầu guardedledger/classifier/saga trước native.
3. Ledgerguards/interceptor/clock/foreground/identity và safeonecommit-slot recovery; S02/S05/S10 trước A-guard protected20.
4. Hop-1/Monitor/wait/nonce/digest/VLM/calibrationloader/ASK/PENDING đúng contract; thiếu certificate→ASK, không importfitted tables như realcertificate.
5. A2–A5framework adapters và 40fixtures trước C-native. AgentProg hard-code patch, T3Anoimages, UI-TARScoordinates, Mobile-Agentmulti-roles giữ đúng.
6. C-guard chỉ mở scientificgate ởmatrix; không xâygeneral intent-engine/fullcompensation/ondeviceforegroundservice cho core.

## L06 — Stage downloads và fidelity

.env loader explicit trước importHF, resolve PROJECT_ROOT/cache/local_dir. snapshot_download exactrepo/SHA/token; index/shards/tokenizer/processor/license/hash và offline reload; không providerfallback hoặcpaidAPI.
Qwen trước A/B; UI-TARS trước AgentProg/UI-TARS native; GUI-Owl trước Mobile-Agent-v3. Native-only development UI-TARS/GUI-Owl chạy đơnengine. Paired final giữ cùng resident topology ở controls. AgentProg workflow/executor và V1 share một Qwen engine bằng independent prompts/history, locator dùng UI-TARS engine; hai engines tổng, không V1 engine thứ ba. A1/A2 agent/V1 cũng share Qwen. Gate peakmemory theo actual topology ở [models](models.md#8-topology-thực-thi-v6), không service-per-role.

Context32768, globalinflight2, seq2/service làstartinglimits. Giữimage/history recipe từ source/processor; admissionmax5ảnh không phải truncatehistory. GUI-Owl5-image recipe và UIprocessor/parser phải đồngbộ. OOM giảm concurrency/AVD trước images/history/dtype; nếu recipe không fitthìsetup chưa đạt, không silentdowngrade. Chi tiết [models](models.md).

## L07 — Gates theo stage

S00/S06/S08/S09/S13/S14 cho A-native, với M3Aassets và modelrole cần thiết; E09numerics vẫn requiredreview nhưng không giảlàmdependencycủanativealgorithm. S01/S02/S05/S10 thêm trước A-guard. A2–A5models/adapters chỉ required trước C-native. S13 không đòitảicả 3model trước A.

Fixtures/reference kiểm CP/stopping/dispatch không tạo fresh calibrationcohort. Model weak/null và ASK-only làfindings, nofault wiring/model identity mới làhard readiness.

## L08 — Attempt/split/freeze

A50+B0 320+Btarget108+C-native400=878scheduled. Global≤88instrumentationretry/max1percase; no scientificreruns; max966defaultattempts. C-guardOFF thêm 212 nếu enable, dùng cùng globalretrycap→max1178, chưa CERT-1.

B0group(config,outcome)40 records:10 dev/30 eval; overall80/240, nofreshcalibration. Devload20/20/40 ở1/2/4 AVD, eval dưới onefrozenload. C-nativebalanced20X1/20X0 targets/taskset, actualtruth/validfault quyết định n. Denominator0→N/A, không rate0.

Freeze sources/model/prompt/parser/processor/history, faults/origins/class/app/load/steps/timeouts/seed/attempt-exclusion rules, endpoint/CI và C-guard eligibility trước final. Không autonomous action khi chưa certified. Protected/H4 là stage còn phải chuẩn bị; không dùng việc unreachable/ASK-heavy để loại strata hoặc chỉ giữ positive outcomes.

## L09 — Handoff gọn

Mộtrunner stage-based/reused upstreamadapters, không orchestrationframework mới. Giao exactcommands sau implementation, manifests/lockfiles, reset/workerIDs/attempt exits, raw→derived→summary/CI/cost/scope. Newoutputs codex/runs/<id>, không originalartifact.
Publish/paperrewrite làbước riêng. Rig/code/modeldataquality và actualH100perf chưa đo thì giữ unverified.

## Paper-target readiness bổ sung cho L04/L08

STUDY_TARGET=paper_draft và TASK_REGISTRY=P01-P40 là default; review_core/T là explicit scoped alternative trước final, không silent fallback. Hoàn thiện10app/variant entries ở matrix mục8, calibration coverage table, matched engine topology và full task freeze trước C0/C-guard. Startup false flags không bỏ E20/E31/E32 khỏi roadmap.

Milestone878 chưa protected/calibration; paper scheduled subtotal1090 gồm212protected/sentinels, max1178 với88extra retries. Calibration/fixture-development budget còn phải đo và chốt trước collection; không coi CERT-1 một stratum đủ cho mọi app.

Load dev giữ20/20/40 ở1/2/4, không thử8 trong core. B0 đo scripted rig; S15/dev fixtures kiểm thêm đúng framework/topology workload trước final. Chọn mức ổn định có throughput tốt nhất trong các mức đã đo, không mặc định4; giữ actual load trong certificate domain và matched controls. Không đổi load sau final.

L08 phải fail readiness cho C-final nếu paper_draft/REQUIRE_H4_EVALUATION=true mà guarded/calibration/topology gates chưa đủ; không tự tiếp tục native-only. A/B/dev không bị chặn bởi final-study gate này. Tất cả các flags mới là requirements cho future runner, chưa có runtime tiêu thụ template.
