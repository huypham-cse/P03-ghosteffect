# Setup, nguồn tải và tiền xử lý

## Material Passport

- h100-plan-v6 và implementationv7, 2026-11-08; nguồn/pins giữ nguyên. [Progress vòng24](resolve-progress.md) ghi SDK/AVD local, backend installation, APK hash/signature/launch evidence; model và full upstream framework environments chưa cài/chạy.
- Bản pin historical căn cứ `artifact/results/real/campaign2/logs/versions_hashes.txt`; không coi trang latest là đúng binary đã đo.

## 1. Dữ liệu cần tải là gì?

Không cần dataset ngôn ngữ/ảnh công cộng cho thí nghiệm cơ sở. Dữ liệu chính là **fresh interrupted app effects**, backend truth và màn hình/tree đồng thời. Việc tải cần thiết là phục hồi rig/phần mềm, còn calibration/evaluation corpus phải được tạo bằng protocol riêng. Public OCR images không thay được recovery screens cùng interrupted population.

Người dùng xác nhận không có thêm source `shared-android` và cho phép dựng lại. [Reconstruction hiện có](../testbed/README.md) giữ protocol draft, không mang historical script hashes. Đã tải GreenMail+bốn historical APK đúng SHA; local Synapse/Radicale đã cài/smoke. SDK/API33r17 x86_64 và Element x86 port đã boot/install/launch cùng K9/DAVx5/Etar. Năm catalogue APK còn lại đã download/signature-verify, hashes trong [catalogue lock](../testbed/assets-catalogue.lock.json). Đây là setup mới, không khôi phục missing attempts/calibration; model chưa tải/chạy.

## 2. Môi trường server và historical stratum

Mục tiêu là server theo [setup-server.md](setup-server.md); giới hạn một H100 80GB/250GB RAM, chạy 7B BF16 và tối đa4 AVD sau E18. Server runtime dùng Android13/API33 và source/model lock; ba measured stacks phục vụ A/B trước, P40 final phải phủ catalogue của draft. Kiểm KVM/CPU/SSD trước downloads lớn, không suy khả năng chạy emulator từ GPU.

Historical stratum giữ arm64-v8a r17, exact APK hashes và macOS host benchmark nếu phục hồi được môi trường gốc. Nếu API33 image/ABI/host mới thì đó là replication stratum mới, thu calibration/lag mới và không gọi timing byte-identical. Ghi OS/API/ABI và actual CPU/GPU/RAM/load để tái lập; historical và server stratum tách riêng.

AndroidWorld setup không được tự thay APK/app state đã pin. SDK/AVD/backend/model/cache đều nằm trong project server root; chi tiết L00–L09 và model snapshots trong [models.md](models.md).

## 3. Danh mục thu hồi/tải và điều kiện nhận

| ID | Thành phần | Nguồn ưu tiên | Pin/cách xác minh |
|---|---|---|---|
| D01 | Rig gốc | Backup/tác giả `papers/shared-android/` | Lấy README, proxy, UI, drivers, analyzers, templates, configs, attempt logs; đối chiếu hashes script bên dưới |
| D02 | Android SDK/platform tools/emulator/API33 image | [Android Studio](https://developer.android.com/studio), [SDK manager](https://developer.android.com/tools/sdkmanager) | Đã tải/cài emulator37.2.13/build16740729 và API33r17 x86_64 local, checksums/receipts ở vòng24. Historicalarm64 r17 là stratum khác; không coi x86 timing tương đương |
| D03 | Element Classic | [F-Droid package](https://f-droid.org/packages/im.vector.app/) | Historical1.6.62 arm64/code40106622 đúngSHA/signature. X86_64/code40106624 đã download/verify/install/launch, cùng signer; [port lock](../testbed/assets-windows.lock.json), calibration mới |
| D04 | K-9 | [F-Droid package](https://f-droid.org/packages/com.fsck.k9/) | 24.0 versionCode 39046; signature, SHA256 và version sau cài |
| D05 | DAVx 5 | [F-Droid package](https://f-droid.org/packages/at.bitfire.davdroid/) | 4.5.21-ose versionCode 405210002 theo package source và log hash |
| D06 | Etar | [F-Droid package](https://f-droid.org/packages/ws.xsoh.etar/) | 1.0.57 versionCode 57; hash/signature |
| D07 | Synapse | [Official repository](https://github.com/element-hq/synapse) | Version1.164.2 theo historical log đã cài local và protocol smokePASS; dependency/wheel hashes/config trong runtime. Không claim recovered historical server image/config |
| D08 | GreenMail | [Official project/download](https://greenmail-mail-test.github.io/greenmail/) | 2.1.2 theo draft; đúng JAR hash trong log; Java compatibility theo artifact. Trang hiện tại mô tả versions mới hơn |
| D09 | Radicale | [Official documentation/downloads](https://radicale.org/v3.html) | Version 3.9.0 theo versions log; recover config/storage/collection permissions và package hash |
| D10 | M3A/T3A/AndroidWorld | [Official repository](https://github.com/google-research/android_world), [agents](https://github.com/google-research/android_world/blob/main/android_world/agents/README.md) | Pin commit + requirements lock; upstream recipe Python 3.11.8 là starting point, smoke compatibility trước dùng; model snapshot riêng |
| D11 | AgentProg | [Official repository](https://github.com/MobileLLM/AgentProg) | Pin commit, program/PC/prompts; HF-main Qwen7B workflow+executor/UI-TARS7B locator; upstream-reference Gemini riêng; phải xử model hard-code lệch README |
| D12 | UI-TARS-1.5 | [Official repository](https://github.com/bytedance/UI-TARS) | Official UI-TARS-1.5-7B tại SHA trong models.md, BF16 primary, mobile prompt và parser; research service là arm khác |
| D13 | Mobile-Agent-v3 / GUI-Owl | [Official repository](https://github.com/X-PLUG/MobileAgent) | Pin Mobile-Agent-v3 multi-agent code cùng official GUI-Owl-7B snapshot cho HF-main; giữ roles/memory/coordinate semantics |
| D14 | PRISM/Storm optional | [PRISM](https://www.prismmodelchecker.org/), [Storm](https://www.stormchecker.org/) | Chỉ cần E34; exact version/container digest phải verify lúc triển khai; chưa kiểm tra release binary ở lượt plan |
| D15 | Screens/raw attempts còn thiếu | Original rig backup | Không có public download thay thế; keep missing khi không phục hồi được |
| D16 | P17–P20 Postfix SMTP + local IMAP cho Sent/no-Sent | Official backend sources, pins còn phải xác minh lúc implementation | Draft final mail backend; version/hash/license/delivery/reset/proxy/grader phải freeze. GreenMail vẫn giữ cho historical/A/B; không tự transfer calibration |

Trang SDK manager hiện dẫn sang Android CLI mới và vẫn mô tả sdkmanager cũ. Khi thực thi, chọn một toolchain được pin, ghi manager version và cú pháp thực dùng; không viết recipe phụ thuộc `latest` rồi gọi reproducible. Các đường URL trên là **nguồn**, không cam kết exact artifact còn available.

Historical SHA256 APK/JAR để đối chiếu:

| File trong log gốc | SHA256 |
|---|---|
| `im.vector.app_40106622.apk` | `ff73751599211c709c1e691d1a2b7412df0bab979ffbe8ff0d4b7f31c6a444c9` |
| `com.fsck.k9_39046.apk` | `0f9dd57fbd06dddfd8bcf7de6106d27fa0f0297793193828c4eac904518b1e05` |
| `at.bitfire.davdroid_405210002.apk` | `41cf9832d97c31e3fc694e5c66b38990dec3312936cc336141714db07259081b` |
| `ws.xsoh.etar_57.apk` | `dae01d93c8920aa63845868db2190bcc4aa6ff8410b1289de1ce27b1bb89c599` |
| `backends/greenmail/greenmail.jar` | `0d0676812f656ff84e484ef736d9149d324d2dec0ea8dbfd6dbd0b59283c3004` |

Rig expected files: `scripts/c2_element.py`, `c2_k9.py`, `c2_caldav.py`, `c2_synapse_txn.py`, `analyze_c2.py`, `faultproxy.py`, `ui.py`. Hashes hiện là hash final scripts sau run, không tự chứng minh chính xác code revision chạy mọi historical trial; recover modification history nếu cần exact provenance.

Mỗi download phải có manifest: source URL, retrieval time, version/commit, SHA256, signature nếu có, byte size, license và purpose. Không tải screenshot/text private lên model để dịch/review ngoài phạm vi agent experiment đã được cấu hình. Nếu không đúng SHA thì giữ riêng alternative, không thay tên để vượt hash check.

## 4. Trình tự setup sau khi chuyển sang implementation

1. Tách numerical environment stdlib khỏi AndroidWorld dependencies. Ghi Python/SQLite thực tế; dùng dedicated virtual environment, không sửa global packages.
2. Phục hồi/cài platform tools và image phù hợp CPU; verify boot, adb serial, API, ABI, storage và clock. Ghi load/concurrency, locale, font scale, display size, animation và timezone.
3. Backend test-only: Synapse account/device/room, SMTP/IMAP users và Sent mapping, CalDAV account/collection. Tắt external delivery; lưu clean snapshots.
4. Proxy có arm ID, matched request ID, commit receipt, response-drop receipt và fault barrier. Grader đọc server riêng; controller không nhận server endpoint/credential.
5. Cài đúng APK, xác nhận package/version/signature; thao tác thủ công no-fault một effect/stack để kiểm tra wiring.
6. Khôi phục UI reader/navigation; screenshot và tree luôn gắn cùng trial/view/time. Kiểm tra stale forwarder, wrong screen và account trước native agent.
7. Smoke M3A/V1 trước A, A2–A5 trước C theo model matrix, giữ input/PC/multi-role/action semantics; wrapper ghi action trước khi bật recovery/interception tại commit dispatch thực.
8. Freeze baseline snapshots/configs và reader/classifier trước B0eval240. Chạy gates S00–S15 phù hợp stage, không yêu cầu fullCPU suite/ba model trước A-native; xem [smoke-tests](smoke-tests.md). Paper final cần P40 assets/calibration/matched topology readiness.

## 5. Dữ liệu hiện có và provenance

| Tập | Unique units hiện có | Vai trò trong kế hoạch |
|---|---: |---|
| C1 app data | 72 trials theo summary | Historical/discovery; reader không xác minh screen như C2 |
| C2 Element |101 main +6 timeout | Historical/discovery; timeout có clean/carry-over flags |
| C2 K-9 |15 no-Sent +18 Sent | Historical/discovery; 20 scripted redo cases, activated-action evidence không đồng đều |
| C2 CalDAV |9 total, 8 actual response drops | Characterization; arm-miss không tính thành fault receipt |
| Synapse |8 bước sequence | Mechanism intervention; không 8 iid app trials |
| `planner_real.csv` |59 aggregate dòng | Generated simulation results, không raw calibration labels thật |
| `planner_real4_*.csv` |16 files/33 dòng | Historical sensitivities, chưa cần tạo lại để biết chúng tồn tại |
| `params.csv` |Name/value/provenance mapping | Giữ measured/derived/assumed/synthetic riêng |

## 6. Tiền xử lý bắt buộc

1. **Preserve:** checksum nguyên bản, immutable raw; parse sang derived mới, không sửa tại chỗ C1/C2.
2. **Inventory attempts:** global attempt ID, campaign, state started/completed/missing/excluded, reason, log offset. Link pilots/discards/ANR; không chỉ ingest dòng thành công.
3. **Normalize schema:** thống nhất units giây/ms, timezone, booleans và BOT codes; giữ raw string. Parse `inf`/unknown/censored riêng, không fill missing thành zero.
4. **Deduplicate ingestion:** chỉ loại duplicate ingestion cùng event ID/hash. Hai request cùng content nhưng khác Message-ID/txnId/href có thể là scientific duplicate, phải giữ.
5. **Truth:** original ID và retry IDs, commit timestamps, server copies từng horizon, terminal non-apply proof. Queued/pending còn có thể apply → unresolved/right-censored.
6. **Clock:** lưu monotonic time + clock origin/boot ID; wall clock chỉ correlation. Bridge host/device bằng offset/uncertainty, không so raw monotonic của hai máy. First-visible thành interval `(last verified absent, first verified present]`; BOT không phải last-absent. Nếu lần đầu đã present thì left-censored; chưa thấy khi kết thúc thì right-censored. Eligibility origin không xác minh được → unknown/ASK.
7. **Screen/evidence:** package/activity/account/room, anchors, list-at-bottom, tree/screenshot timestamps/hash, freshness, read verdict và BOT reason. Mỗi effect có ordered family tuple; repeated polls link effect ID.
8. **Fault verification:** planned class khác observed class; PID/ACK/drop receipts; `am kill` NOOP giữ riêng. Sai class receipt không tự sửa nhãn thành intended để pass coverage.
9. **Derived labels:** false-com/false-abs/structural no-observation; visibility-lag blindness khác perception error sau visible. Keep committed-never-visible, optimistic UI và late commit như separate strata.
10. **Reconcile:** raw requests ↔trial dòng ↔polls↔derived aggregates. Export unmatched IDs và missingness table; chỉ regenerate các macros trong isolated copy khi mapping hoàn chỉnh.

## 7. Splits, provenance và scope

- Historical C1/C2 làdiscovery, không freshvalidation. Generated/bootstrap2k/5k/20k đúng tag không unique real data.
- B0=4 configs×2 outcomes×40=320scheduled:80 dev(10/group),240 eval(30/group), không freshcalibration-smoke. Classbalanced10/group, eval7/7/8/8 tùyclass; no pooling để certify.
- Dev chọn reader/classifier/load; E18 dùng 80 dev phânload20/20/40. Evalthu sau freeze, khác ngày devkhi khảthi, dưới one matchedload. Khôngtune từ eval.
- E15 dùng 200B0evaleffects100/outcome; E21làactionlabels120 dev/80 eval split theoeffect/task, không cohort200 episodes.
- B0evaluation chỉ rates/CI/BOT/lag/cost, không exportcertificate. SyntheticCP/loaderfixtures làreference tests, không measuredsamples.
- CERT-1OFF là recipe tùy chọn500pilot+5000holdout/outcome cho một stratum, không bảo đảm đủ n và không tắt requirement calibration coverage của protected study. E09 tính actual K_total/lag/censoring và fixed acquisition n trước collection. Scriptedstates không autoexchangeable vớiagent-createdstates; costforecast phải đo đúng driver/modelmix.
- C-native40 tasks có20X1/I3 và 20X0/I2 targets, T class5/outcome; P áp local-only mapping6/6/4/4 mỗi outcome. Đây làbenchmarkmixture, không naturalpi; conditionaloutcomes và ITT luôn cùng report.
- Actualoutcome/fault phải verified, intendedlabels không truth. Failed/unknown/censored giữ raw, denominator0→N/A.
- Mỗitrialtối đa 1instrumentationretry, global88default extras; model/scientificfailure không rerun để bùvalidquota. KeepallattemptIDs.
- C-guard startup OFF; paper roadmap phải bổ sung valid calibration coverage và freeze scope/endpoints/load/controls trước final. Unsupported→ASK giữ denominator; không gate bằng positive score/autonomous region. B0eval/fitted law không thay calibration.
- Reuse screens/VLM chỉ offlineexactinputhash, không reuse acrossliveeffects hoặcstate-changingmethods. Không cần potentialimagebank framework.

## 8. Schema tối thiểu cho dữ liệu mới

| Nhóm | Fields cần giữ |
|---|---|
| Identity |campaign/run/attempt/trial/workflow/effect IDs; split; seed; method; config hash |
| Stack |host/CPU/ABI/device/AVD/build; app/backend/reader/agent/model versions; locale; account/device scope |
| Action |commit target; classifier/annotated flag; nonce field/opt-in; digest snapshot; attempt index; tap receipt |
| Clocks |issue/tap/commit/fault/kill/relaunch/restore/poll/start/end; origin type; clock source/offset bounds |
| Fault |intended/observed class/subtype; proxy arm/match/ACK/drop; process PIDs; Doze state; NOOP reason |
| Evidence |view/family; screenshot/tree hash; freshness/anchors; present/absent/BOT; terminal-monitor result |
| Truth |original request IDs; retry IDs; commit state; copies at horizons; terminal proof; censoring and unknown |
| Policy |bound/calibration ID; alpha/beta/shares; decision/score/wait; fallback/ask reason; user answer origin |
| Cost |setup/reset/wait/read/API/controller durations; tokens; failures/operator time; storage/load/concurrency |

Schemas/validators mới chỉ là đặc tả; chưa có collector, runtime hay parser mới được viết trong lượt này.

## 9. Model server và tải Hugging Face qua .env

[models.md](models.md) là cấu hình model duy nhất có hiệu lực: HF-main Qwen2.5-VL-7B, UI-TARS-1.5-7B, GUI-Owl-7B, full official Safetensors, BF16 inference, giữ five-agent algorithms. Một H100 80GB là giới hạn mới; topology hai services BF167B,1→2→4 AVD theo E18. Không 72B/multi-GPU. Upstream-reference API recipes được ghi riêng, không phải HF weights.

Dùng [`.env.example`](.env.example) làm mẫu cho project `.env`; loader phải nạp token/model IDs/SHA/cache paths trước HF import. Tải bằng `snapshot_download` với exact revision và `local_dir` trong `codex/models/`. Kiểm đủ index/shards/config/processor/tokenizer/license/hash rồi offline reload; không lưu token vào metadata xuất bản. Endpoint tự host không tự phát sinh phí model API, nhưng inference/device-hours vẫn được đo.

Dữ liệu cần tạo cho paper không đến từ model hub: fresh interrupted effects, outcome/lag/GUI evidence và fault receipts vẫn phải thu theo schema/splits ở trên. Grader không được dùng chính VLM để quyết định hidden server truth. Thay model/prompt/precision/processor làm reader stratum mới, cần calibration tương ứng.

Lựa chọn model đã chốt ở mức plan; download receipts, adapter checks và main results chưa tồn tại. Bảng task/fault/quy mô đầy đủ ở [study-matrix.md](study-matrix.md).

## 10. Trình tự nhận dữ liệu trên server

L00–L09 ở [setup-server.md](setup-server.md) bao gồm cài môi trường, tải HF model qua `.env`, dựng rig/backends/five-agent adapters và bàn giao recipe chạy lại. Mọi payload nằm dưới project; không khởi tạo hay đọc real `.env` trong lượt revise plan.

Nguồn 40 task templates, fault applicability, main repeats và calibration demand nằm ở [study-matrix.md](study-matrix.md). App chưa có APK/package pin hoặc missing original rig cần được xác minh trong L00/L04/E00, không thay bằng dataset công cộng hay app dễ hơn. Model checkpoint/hash lấy ở [models.md](models.md); wrapper/model transport wiring vẫn là phần cần triển khai sau.

## 11. Cohort authority

Quy mô v5 theo [study-matrix](study-matrix.md): milestoneA50+B0 320+Btarget108+C-native400=878, globalretrycap88. Paper target P40 và C-guard200+12sentinels đưa subtotal1090, chưa calibration acquisition/app development. Planned apps ngoài3stacks phải hoàn thiện cho full paper coverage; không chặn A/B. Thaydata/model/registry sau freeze tạo study revision.

## Paper-target assets và calibration coverage

Ngoài D01–D15, E31 giữ Tasks.org, Joplin, Simple SMS, Pro Expense và Markor; MockBank-A/B phải viết ở E32. Năm binary đã tải/verifySHA/signature/manifest từ pinned AndroidWorld, [catalogue lock](../testbed/assets-catalogue.lock.json). Pro Expense `com.arduia.expense`, versionCode11/1.0.0-beta05 đã xác minh; [nguồn và startup receipts](resolve-progress.md). Actual task fixtures/sync/reset/grader còn thiếu. Record fields vẫn gồm source/package/version/ABI/SHA/signature/license/commit/nonce/reset/grader/fault domain trước final.

D16 áp dụng cho P-final mail, không ghi đè GreenMail data. E31 cũng phải xác minh actual WorkManager/outbox/G2 và F2 force-stop slots để biết có test H3 được hay không. Không có source/receipt thì status NOT_TESTED; không tự thêm app ngoài paper.

Model assets vẫn tải trong project theo models.md. Không có public dataset nào thay valid interrupted calibration. Lập coverage table theo actual app/backend/reader/model/fault/origin/load, gồm existing source/provenance, missing labels/lag, candidate CP/K_total và acquisition cost. Nếu thiếu certificate cho full paper target, collection là required dependency; CERT-1 chỉ candidate recipe một stratum, không default11k×apps. Unknown domain→ASK; không lấy B0eval làm calibration hoặc bỏ app sau scores.
