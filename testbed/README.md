# Testbed dựng lại cho GhostEffect

Đây là **reconstruction được người dùng cho phép**, dựa trên draft §5–§7, review và log campaign 2. Source `papers/shared-android/` gốc không có và người dùng xác nhận không còn thư mục khác. Code này **không mang hash của rig gốc**, không khôi phục dữ liệu/missing attempts, không chứng minh đã tái tạo 149 trial lịch sử.

Đường chạy tối thiểu giữ nguyên: app Android thật trên AVD → protocol proxy → backend test; injector giữ ACK sau acceptance rồi gây fault; reader chỉ dùng GUI; backend truth nằm riêng ở grader. Không thay năm framework bằng agent tự viết, không thay model, không thay quy mô 878/1090 của [plan](../codex/plan.md).

V7 tiếp tục ở [resolve-progress](../codex/resolve-progress.md): calibration compiler/Algorithm1 runtime, durable read cache, history-item digest, lexicon classifier và GUIObserver/local-model binding có58tests/host. Synapse1.164.2/Radicale3.9.0 đã cài và protocol smokePASS. SDK/emulator37.2.13/API33r17 x86_64 đã boot với WindowsWHPX;4measured-stack apps qua installedSHA/launch/capture. Cả10APKs (gồm2ElementABIs và5catalogue candidates) qua signature/manifest checks. App accounts/task profiles/agent/weights/calibration vẫn chưa có execution evidence; startup smoke không thay các mục này.

## Đã có gì và còn thiếu gì

V10: đã có actual native AndroidWorld screenshot/a11y observation trên AVD qua gRPC, chưa LLM episode. Forwarder date2024.05.13 được pin trong [agent-assets.lock.json](agent-assets.lock.json), signature/installedSHA được kiểm. `--native-env-capture` dùng native forwarder, không buộc thêm UI Automator vào observation protocol. `--scripted-agent-wire` là **SYNTHETIC_RESPONSE** fixture cho một native BACK/reflection step, không model/quality/task trial. Không có fallback giả lập responses trong `make_agent` hoặc LocalModel khi chạy model thật. Xem [progress](../codex/resolve-progress.md) vì các setup failures/ANR/empty forest vẫn phải xử lý; một observation PASS không qualify toàn pipeline.

Native setup smoke (Windows, source/runtime đã cài): `python testbed/smoke_android.py --verification <APK-verification-RESULT.json> --only net.gsantner.markor_146.apk --native-env-capture --output <fresh-output>`. Verification cần có forwarder đã kiểm chữ ký. Thêm `--scripted-agent-wire --gpu host` để chạy development recipe host02; đây là explicit dev renderer, không model GPU hoặc profile đã freeze. Downloader: `python testbed/setup_assets.py --lock testbed/agent-assets.lock.json --only 2024.05.13-accessibility_forwarder.apk`. Không chạy hai smoke cùng lúc.

V9: `androidworld_env.py` nối native AndroidWorld bằng adb/gRPC explicit và giữ endpoint khi reconnect; native M3A/T3A constructors giữ upstream defaults, có actual source-binding tests trong agentenv. Chưa actual gRPC/agent episode. `ui.py` giữ raw capture lỗi, không retry/repair; SimpleSMS startup mới mở MainActivity/capturePASS nhưng unstable tree nên reader chưa qualify. [Receipts/vòng27–28](../codex/resolve-progress.md). Số draft minh họa không là expected-output gate; source/config/raw mới là chuẩn.

V8: full pinned source bốn baseline repo và Python3.11.8 ở `runtime/`; M3A/T3A/env launcher import thực PASS ([receipt](../runtime/agents/SETUP.json)), chưa native episode/model inference. Window guard nay kiểm cả InputDispatcher sau actual SystemUI ANR; SimpleSMS default role đã gán nhưng dialog cũ/cold-start XML failure còn mở. Các startup PASS cũ không qualify readiness theo guard mới. [Vòng25–26 và giới hạn evidence](../codex/resolve-progress.md).

| File | Chức năng thực có | Giới hạn |
|---|---|---|
| `androidworld_env.py` | Native config/controller/AsyncEnv và M3A/T3A factory, source-module checks, giữ adb endpoint khi reconnect | Native observation và scripted BACK/reflection wiring đã kiểm; real-model serving/full-task/protected harness còn thiếu |
| `capture_androidworld.py` | Một native screenshot/forest với input/window guard và source receipts | Setup only; không task grader/calibration/model episode |
| `smoke_agent_wire.py` | Native agent action/reflection + LocalModel transport với scripted BACK responses trên loopback | Synthetic wire fixture; không LLM baseline hoặc scientific episode |
| `faultproxy.py` | Matrix/CalDAV HTTP reverse proxy; SMTP DATA proxy; pass/reject/drop/sticky/withhold; journal fsync và barrier | Không TLS client-side/HTTP2/chunked upload; không tự suy ra packet RST hoặc app đã nhận ACK |
| `ui.py` | ADB capture có tree trước/sau screenshot; foreground; reader account/title/timeline/anchor/outgoing/status; scroll đến cuối | Cần IDs/navigation từ màn hình app thật; profile mẫu chưa freeze và luôn BOT |
| `controller.py`, `recovery.py` | Host issue-before-tap, durable per-attempt read cache, calibrated Algorithm1 cascade/wait/Monitor/ASK/PENDING | Chưa actual Android/official-agent integration; production thiếu matching measured certificate→ASK; chưa H4 |
| `calibration.py` | Compiler effect-level pilot/holdout/lag, CP/product/source/joint, actual K_total, domain/class và evidence hashes | Chưa measured labels/collector joins; assumptions cần actual evidence, synthetic store bị production loader từ chối |
| `probes.py`, `classifier.py`, `observer.py` | Semantic count digest, locale/structured commit classifier, profile-based GUI family adapter và isolated VLM prompt | App profiles/classifier corpus/Monitor eligibility còn phải kiểm thật; không oracle inputs |
| `local_model.py` | Thin M3A/T3A `predict`/`predict_mm` wrapper cho localhost vLLM, full images/prompt, no fallback/truncation | Wire tests chưa weights/serving/native-agent execution; các framework khác còn phải nối |
| `run_case.py`, `app_driver.py` | Optional profile-based compose/history navigation; arm → tap → barrier → force-stop → release → relaunch → GUI visibility polls | Development driver; selectors cần màn hình thật, chưa LLM/backend grading tự động; `CAPTURED_NOT_GRADED`, không PASS study |
| `grader.py` | Matrix room event count; receiver IMAP count; CalDAV collection count | Backend-only; finite-horizon zero không chứng minh permanent absence; không đưa vào controller |
| `setup_assets.py`, ba asset locks | Historical APK/JAR, x86 Element port và5catalogue APKs đã tải; signatures/manifests đã verify | Default historical lock; port/catalogue lock chọn explicit; license metadata cần hoàn thiện trước redistribution, không latest fallback |
| `setup_android.py`, `setup_avd.py` | Project-local pinned SDK/API33r17, actual WHPX check, AVD creation và apksigner/aapt verification | Windows development stratum mới, không historical ARM64 timing; server theo Linux runbook |
| `smoke_android.py` | Isolated adb5038/AVD serial, actual boot/installSHA/launch/capture và owned-process cleanup | Setup only; chưa accounts/tasks/commit/fault/agent/lag/calibration |
| `setup_backends.py` | Đã cài pinned Synapse/Radicale trong project-local Linux venv, pip report/hash/freeze và configs | Campaign accounts/reset/snapshots vẫn cần freeze; smoke dùng namespaces riêng |
| `preflight.py` | Inventory Python/SQLite/KVM/ADB/assets/backend versions | Không tự suy readiness từ GPU |
| `smoke_greenmail.py` | JVM GreenMail đúng hash + proxy + receiver IMAP, mail synthetic | Integration protocol, không Android/native agent/calibration |
| `smoke_http_backends.py` | Pinned Synapse/Radicale thật, lostACK/sameID/newID/reject checks và private graders | Payload synthetic, không Android app fault/LLM, không cohort/calibration |
| `tests/test_testbed.py` | HTTP/SMTP barrier/reject/retry, GUI negative cases, dispatch/restart và grader errors | Fixtures được ghi rõ synthetic; không tính vào B0 hoặc calibration |

Đã có driver/observer/compiler/runtime theo profile chung; chưa có profiles compose/navigation đã kiểm trên ba stacks, observed LMK/Doze/network injector, actual calibration collector/fate joins, năm framework environment/action bindings và P40 asset/reset/grader coverage. Không tạo file rỗng mang tên driver cũ để giả đã đủ rig.

## Kiểm thử hiện có, không cần GPU

Chạy từ root dự án:

```powershell
python -m unittest discover -s artifact/tests -v
python -m unittest discover -s testbed/tests -v
python testbed/preflight.py --output testbed/runs/preflight-01.json
python testbed/setup_assets.py --only greenmail.jar
python testbed/smoke_greenmail.py --output testbed/runs/mail-smoke-01
```

Mỗi output dùng tên mới. GreenMail được giữ trong `runtime/assets/greenmail.jar`; downloader đã khớp SHA256 `0d067681…c3004` với log gốc. Smoke đóng đúng JVM mà nó mở, backend mail không chuyển thư ra Internet. Kết quả đã chạy ở [report](../report.md) và [code-fixes](../codex/code-fixes.md).

## Setup Android/backend để nối tiếp

Trên Windows hiện tại đã có SDK và AVD trong `runtime/`. Fresh setup chạy `python testbed/setup_android.py --bootstrap`, sau đó `setup_avd.py --java <java.exe-path> --install --create --verify-apks --output <fresh-directory>`; nếu AVD đã tồn tại thì bỏ `--create` để giữ state. Toolchain/image được pin, SDK setup không chỉnh Windows features/PATH. Java thực đã dùng: `C:\Program Files\Microsoft\jdk-17.0.20.8-hotspot\bin\java.exe`.

Kiểm lại4app startup: `python testbed/smoke_android.py --verification tmp/resolve-v7/android/setup-03/RESULT.json --output <fresh-directory>`. Muốn kiểm5candidates, thêm `--only com.arduia.expense_11.apk net.gsantner.markor_146.apk org.tasks_130605.apk com.simplemobiletools.smsmessenger_85.apk net.cozic.joplin_2097740.apk`. Không chạy hai invocations cùng lúc vì dùng mộtAVD/adb5038. [Smoke04](../tmp/resolve-v7/android/smoke-04/RESULT.json) đãPASS; Element carousel tree chưa ổn định nên chưa qualify reader. Không dùng boot seconds như paper lag/throughput.

[Smoke05](../tmp/resolve-v7/android/smoke-05/RESULT.json) cài5candidate đúngSHA,4app mở đúng package; SimpleSMS còn ở system role dialog→NOT_READY. Thử `--prepare-sms-role` ở06–09 chưa hoàn tất (CLI unsupported/timeout và GUI confirm disabled); flag này development/unqualified, không dependency đãpass. Xem [progress](../codex/resolve-progress.md) trước SimpleSMS task runs. Cả9apps installed chưa có nghĩa P40 fixtures/agent/calibration ready.

1. Trên server Linux, kiểm `/dev/kvm`, CPU/RAM/SSD trước. Cài SDK/emulator/API33 vào `runtime/android-sdk`, AVD/home/cache cũng đặt trong root dự án. Giữ arm64/r17 khi tái tạo historical stratum; nếu dùng x86_64/KVM, ghi new image/APK hashes và thu calibration mới. Không tự coi APK Element arm64 trong lock chạy được trên x86_64. Recipe SDK và model pins vẫn theo [setup-data](../codex/setup-data.md), [setup-server](../codex/setup-server.md), [models](../codex/models.md).
2. Historical APKs: `python testbed/setup_assets.py --only im.vector.app_40106622.apk com.fsck.k9_39046.apk at.bitfire.davdroid_405210002.apk ws.xsoh.etar_57.apk`. X86 Element: chọn `--lock testbed/assets-windows.lock.json --only im.vector.app_40106624.apk`;5app candidates dùng `--lock testbed/assets-catalogue.lock.json` và explicit filenames. Cả10binary đã signature-verify local; SHA/version/ABI trong receipts, không bypass mismatch. Model chưa tải/chạy.
3. Linux: `python3 testbed/setup_backends.py --install` cho fresh setup, `--resume` chỉ cho partial setup local chưa hoàn tất. Môi trường hiện tại đã cài xong, không cài lại. Dùng `runtime/backend-venv/bin/python` để chạy Synapse với `runtime/backends/synapse/homeserver.yaml`; Radicale với `--config runtime/backends/radicale/config`. Pins1.164.2/3.9.0; pip report ghi dependencies/hashes. Config không mở registration/federation public.
4. GreenMail2.1.2: chỉ bật SMTP3025/IMAP3143 trên127.0.0.1, users test, API/TLS không bật nếu chưa cần. Theo [upstream standalone options](https://greenmail-mail-test.github.io/greenmail/#deploy_standalone). K-9 A/B dùng GreenMail như historical; P-final giữ Postfix/IMAP riêng theo draft, không dùng smoke này để đổi backend final.
5. Tạo isolated test accounts, room/calendar/receiver mailbox và old-message anchor. Không dùng dữ liệu/tài khoản cá nhân. Cấu hình Sent/no-Sent là hai configs riêng. Reset backend **và** client queue theo snapshot đã freeze; ghi SHA và receipt. Hiện chưa có tự động reset của app.
6. Chạy proxy, ví dụ Matrix: `python testbed/faultproxy.py --protocol matrix --upstream http://127.0.0.1:8008 --listen-port 18008 --control-port 19008 --journal testbed/runs/matrix-01/proxy.jsonl`. CalDAV tương tự upstream5232/proxy15232; SMTP `--protocol smtp --upstream smtp://127.0.0.1:3025` với proxy14025/control19025. Một proxy/run/worker; control chỉ loopback và chỉ injector được dùng.
7. Với AVD trên cùng host, dùng `adb -s emulator-5554 reverse tcp:18008 tcp:18008` (và ports CalDAV/SMTP/IMAP cần dùng). App trỏ localhost port đã reverse. Không expose control port vào Android; không đưa backend/IMAP oracle credential vào agent/controller environment.
8. Capture màn hình dev bằng `ui.py`, điền `reader-profile.example.json` sang file `.local.json`. Chốt account/title/anchor/timeline/row/outgoing/acknowledged/excluded states, swipe hướng latest và app version/hash. Chỉ freeze sau negative controls wrong-room/account/failed/draft/stale. Không đoán resource IDs từ tên app.
9. Có thể chạy `run_case.py` sau khi compose screen/queue đã chuẩn bị. Bắt buộc explicit AVD serial/package/activity/tap/control/fault/output; `--help` liệt kê tham số. `--request-id` nên là ID chính xác; arm-next chỉ dùng isolated queue sạch và phải xác minh matched request. Driver không tự gọi đó là completed experiment: tiếp tục GUI polling và grader tới horizon theo matrix. Không đưa receipt true-X cho agent.
10. Chỉ nối M3A upstream sau nofault/fault stack receipts, rồi A-native. A-guard cần classifier/interceptor/clock/certificate/Monitor đã kiểm thật; các framework còn lại theo stage C. Profile, load, model/input/history và task registry phải freeze trước eval. Không mở H4 chỉ vì ledger hoặc GreenMail smoke PASS.

## Ý nghĩa receipt và các giới hạn phải giữ

- Matrix acceptance cần200+event_id; CalDAV cần201/204; SMTP cần final250 sau endDATA. Đây là protocol receipts; inbox visibility/client Sent/app ACK-consumption cần evidence riêng. [Matrix API](https://spec.matrix.org/v1.12/client-server-api/#put_matrixclientv3roomsroomidsendeventtypetxnid), [CalDAV RFC4791](https://www.rfc-editor.org/rfc/rfc4791).
- Postcommit drop: journal `UPSTREAM_ACCEPT → PRE_ACK_BARRIER → FAULT_RECEIPT → REPLY_DROP`; injector ghi actual PID/fault class. Barrier timeout đánh dấu `INVALID_BARRIER_TIMEOUT`, không tính valid interrupted case. `ACK_WRITE` chỉ là socket write, không phải app tiêu thụ ACK.
- Reject: proxy không forward original request; cùng request ID tiếp tục bị reject trong suốt process. Đổi Message-ID/txnId/href là request mới. Chết proxy trước horizon hoặc còn queue chưa xét thì không đủ chứng minh X0/permanent absence.
- Sticky chỉ giữ/drop replies của immediate retry **cùng ID** đến fault release; không tự dedup backend. Withhold kết thúc do client/injector/timeout phải đọc receipt, không tự gắn nhãn client timeout.
- GUI `com/abs` là family observation, có thể sai do optimistic/stale history; cần interrupted-effect calibration. BOT, duplicate candidate và missing profile không trở thành absence. Screenshot/tree là sequential bracketed capture, không atomic capture.
- `probes.py` có semantic history-item digest; production controller yêu cầu semantic snapshot khi dùng digest family, không lấy XML hash thay thế. `calibration.py`/`recovery.py` có product/source/joint runtime; thiếu measured certificate/domain thì ASK. Code fixtures không chứng minh lợi ích H4.
- Native driver hiện chỉ force-stop; không đổi nhãn thành LMK/SIGKILL. H_eval và polling, delayed recovery/Doze, verifier errors, actual calibration/cost và paper P40/five-agent study vẫn theo [experiments](../codex/experiments.md).

## Việc cần nối tiếp, theo thứ tự

1. Actual AVD/API/ABI/APK/backend/setup/reset receipts và ba app profiles; smoke nofault + committed/lostACK + terminal reject từng stack.
2. Freeze/kiểm actual profiles cho driver compose/history/poll; nối private grader và fate/horizon/clock validator. A-native M3A phải có ≥10 valid interrupted cases.
3. Một interceptor/commit-slot mapping và certificate/cascade adapter từ numerical core; qualified hop1/Monitor chỉ trên app có source eligibility. Thu calibration thật trước autonomous protected runs.
4. Nối đủ năm frameworks theo pins đã chốt, P40 assets và paired load; chạy quotas hiện có. Không mở thêm platform hay campaign để bù thiếu source gốc.
