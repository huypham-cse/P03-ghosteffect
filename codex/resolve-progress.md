# Resolve tiếp theo v10 — giữ pipeline và đối chiếu code/paper

## Vòng 29 — Actual native AndroidWorld observation trên AVD

Giữ nguyên paper theo chỉ thị cuối; số draft không là target phải tái tạo. SDK37.2.13/API33r17 x86_64/WHPX local đã có **actual gRPC native observation**. [Smoke01](../tmp/resolve-v10/native-smoke-01/RESULT.json), [native receipt](../tmp/resolve-v10/native-smoke-01/native-env/RESULT.json): Markor IntroActivity, RGB2400×1080×3,5UIelements, window/input identity match, ownedAVD stopped. Đây là onboarding setup, không task/calibration/model inference.

Forwarder APK ngày2024.05.13 lấy từ URL hardcoded trong android-env1.2.3, SHA `97a56a544e44d79f9b3181fc7dbdd72cffa908efd3d53c82afad1773061a350a`. [Lock](../testbed/agent-assets.lock.json); [verification](../tmp/resolve-v10/apk-verification/RESULT.json) đủ11APKs, không11apps. Forwarder v3-signature valid, Android Debug signer; không gọi đây là historical paper checksum hoặc signing-key identity được xác nhận độc lập. Upstream binary license chưa audit cho redistribution; local test dùng asset đã pin.

`--native-env-capture` mởgRPC8554, cài instrumentation đã signature/hashverify, kiểm installedSHA và chạy `capture_androidworld.py` bằng project agentPython3.11. Env con allowlist OS/runtime paths, không truyền backend/API credentials; adb5038/serial5580 explicit. UI Automator không bị thêm thành observation requirement của M3A/T3A; đường standalone UI smoke giữ riêng. `ui.py` lưu raw display/input dumps khi focus check fail, có regression test.

## Vòng 30 — Native action/reflection qua scripted transport fixture

[Host02](../tmp/resolve-v10/native-wire-host-02/RESULT.json) PASS: native M3A/T3A thực thi BACK trong AVD, mỗi bên2requests/action+reflection và1historyentry; M3A2images/request, T3A0. [M3A](../tmp/resolve-v10/native-wire-host-02/native-env/scripted-wire-m3a/RESULT.json), [T3A](../tmp/resolve-v10/native-wire-host-02/native-env/scripted-wire-t3a/RESULT.json) giữ adb BACK statusOK và prompts/images/raw step data. Synthetic responses qua loopback HTTP thực thi LocalModel transport, không rewrite agent loop và không fallback trong production binding. **Không model-loaded/quality/real-model-native-episode và không scientific quota.** Chỉ BACK được kiểm, chưa full click/type/coordinate/task/fault behavior.

Các attempts giữ riêng: [wire01](../tmp/resolve-v10/native-wire-01/RESULT.json) FAILED focus guard trước native fixture; [wire02](../tmp/resolve-v10/native-wire-02/RESULT.json) FAILED, raw display/input xác nhận SystemUI ANR; [host01](../tmp/resolve-v10/native-wire-host-01/RESULT.json) FAILED emptyforest dù RGB có hình. Không bỏ guard/dismiss ANR để chạy tiếp. Host02 dùng `--gpu host` cùng corrected native reset(Home)→targetlaunch→hidepointer; không thể từ một PASS chốt renderer là nguyên nhân hoặc đã tối ưu. Default vẫnswiftshader, không silentfallback; graphics/load/profile phải freeze trước study.

Reset/launch được thêm vì native runner có env.reset và task initialization; test cũ chỉ init forwarder dưới màn hình tĩnh, khác lifecycle đó. Native agent.reset cũng chạy trước scripted step. Đây là sửa harness setup, không extra calibrated views. Source upstream không sửa. V10 smoke receipt cũ field `agent_steps=0` không đếm hai scripted native code steps; [qualification](../tmp/resolve-v10/RECEIPT-QUALIFICATIONS.json) giữ model-driven0/scripted2/scientific0, raw receipt không đổi. Future schema tách counts, không chạy thêm AVD chỉ để thay metadata.

Full67test cases PASS Windows/Linux/agentenv (skip4/3/1). [Validation](../tmp/resolve-v10/VALIDATION.json), [integrity](../tmp/resolve-v10/INTEGRITY.json) ghi source hashes và bảo toàn manuscript. Native smoke trước schema-count correction là snapshot riêng; metadata-only correction được component checked, không gộp receipt thành full revision đã chạy AVD.

**Remaining:** real-model serving/native harness/full actions, AgentProg/UI-TARS/MobileAgent adapters; actual app accounts/task fixtures/reset/grader/P40+MockBank/Postfix; interrupted-effect collector/fate/probe/clock receipts; classifier labels/calibration/coverage; actual H100 fit/load và final episodes. F3/F4 cần app/backend network isolation đúng scope và receipts vì forwarder có thể tự bật networking; không cắt observation/control plane. Không cần physical phone cho core. Có progress local nhưng chưa đủ cơ sở đóng toàn goal.

## Quyết định mới v9 — số draft không là core hoặc blocker

**Chỉ thị sau cùng: không sửa paper; paper để sau.** Lượt publish derivedTeX/PDF đã được undo21files, hash khớp bản trước lượt này; [restoration receipt](../tmp/resolve-v9/draft-refresh/PAPER-RESTORED.json). Thí nghiệm/CSV/code/plan/report được giữ. Không tiếp tục chạy root render/build hoặc ghi bất kỳ file nào trong `manuscript/`; render tests chỉ dùng isolated outputs. Các ghi chú publication bên dưới là lịch sử đã khôi phục, không phải trạng thái paper đang áp dụng.

Người dùng08/11/2026 xác nhận **tất cả số kết quả draft là minh họa; cái chạy mới là nguồn chuẩn**. Từ đây không truy thêm ASK47.35% hoặc ép kết quả mới khớp archive. Các ghi chú historical discrepancy ở vòng19–26 bên dưới chỉ còn là lịch sử điều tra, **không là việc cần người dùng resolve hoặc gate của E01**. Actual results vẫn phân loại đúng simulation/fixture/host/protocol/Android/agent/calibration; user cho phép thay số draft không biến synthetic thành measurement.

Giữ pipeline/phương pháp/năm frameworks và scope của kế hoạch; thiết kế/model/quota được freeze trước chạy, không điều chỉnh theo outcome. Lưu CSV mới có source/command/exit/hash cho giai đoạn paper sau; hiện không cập nhật manuscript. Không sửa RNG để đạt số. Native/controller/calibration/P40/H100 readiness mới là các việc cần làm tiếp.

## Vòng 27 — Refresh số từ run và sửa capture diagnostics

Đã chạy main5seeds×2400workflows/cell,24policy rows: source-family ASK47.008333% và displayed47.0%. [Publication](../tmp/resolve-v9/draft-refresh/PUBLICATION.json) ghi command/exit/source/output hashes; các component CSV khác lấy từ snapshot đã kiểm source của v6, không gọi tất cả là fresh run ởv9. Một invocation WSL trước đó mất process handle, Windows/WSL processes xác nhận không còn và không có mainCSV; giữ interrupted receipt riêng, lần hoàn tất sau chạyWindows. Không chạy lại scientific failure để lấy PASS. Draft được regenerate972macros cùng figures/tables; [PDF](../manuscript/main.pdf) build20pages bằng Tectonic, kiểm page9 và contact sheet; backup trước refresh ở `tmp/resolve-v9/draft-refresh/previous/`. Prose/lý thuyết và raw measurements không sửa. First staged compile thiếu PDF icons do filter copy scratch; đã sửa filter và restore21assets, compile02 thành công. Không phải lỗi source paper.

`ui.py` lưu nguyên raw first/second tree và dump output; malformed/non-hierarchy→capture failure cóstage, không repair/retry. Cleanup error không che parse failure. Đã có regression cho đúng failure path. [SimpleSMS startup diagnostic](../tmp/resolve-v9/sms-startup-diagnostics/RESULT.json) PASS install/hash/launch/capture, input/window cùng MainActivity; stable_tree=false. Diff raw chỉ thấy root bounds `[0,128]`→`[0,0]` ở lần này, không vì thế bỏ stable check hoặc suy mọi failure đã hết. App vẫn chưa qualify reader/task; v8ParseError giữ nguyên và nguyên nhân chưa xác minh. SMS setup helper được sửa chọn actual radio và xử lý checked+Currentdefault bằng Cancel; branch tests không thay clean-state GUI execution.

## Vòng 28 — Native environment binding, giữ thuật toán upstream

`testbed/androidworld_env.py`: official AndroidEnv config/loader/controller/AsyncEnv với cổng explicit. Override duy nhất ở native controller là factory reconnect để không rơi về adb5037. Native observation/action/a11y code giữ nguyên; M3A/T3A được instantiate trực tiếp, M3A pause2s/defaulttransition1s, T3A text-only. `verify_source` kiểm commit/tracked clean và8imported module hashes so với full pinned source. Không đổi prompts/history/parser, không single-loop thay baseline. `EpochStop` chỉ là marker cho host stop không bị upstream `except Exception` nuốt, chưa là protected integration.

Actual agentenv đã chạy3binding tests với native modules/config/reconnect factory, không device/weights/API. Full66test cases: WindowsPython3.12 PASS/4skip; Linux PASS/3native-env skip; agentPython3.11 PASS/1POSIX skip. [Validation](../tmp/resolve-v9/VALIDATION.json), [integrity](../tmp/resolve-v9/INTEGRITY.json). V8manifests vẫn là historical receipts, không bị sửa để ghép với code mới.

**Chưa có execution evidence:** native gRPC/forwarder trên AVD; full native/protected episode; frameworkA3–A5 action wiring; actual P40 reset/grader; collector semantic joins; measured calibration; H100 weights/serving/load. Native forwarder còn có behavior tự khôi phục networking khi a11y không gửi được; cần ghi/kiểm khi thiết kế fault receipts, không âm thầm thay upstream hoặc gọi networking fault đã được giữ ổn định. Cần cài/freeze upstream forwarder APK từ project asset trước measured episode; factory không tự download lúc chạy study.

## Material Passport

Ngày08/11/2026; task là tiếp tục sửa plan/code theo draft/review, không viết lại manuscript hoặc đổi kỳ vọng để ép kết quả đẹp. Worktree trước vòng này có hash manifest ở `tmp/resolve-v7/before.json`. Numerical/raw/PDF gốc được giữ. Đây là các vòng kiểm inline, không reviewer/subagent độc lập mới.

**Scope giữ nguyên:** host controller ngoài agent; GUI-only decisions; Algorithm1 hop1/Monitor → certified wait → nonce/digest/VLM; product/source/joint; ASK/PENDING. Năm frameworks/P40, ba model pins BF16, A/B GreenMail/P-final Postfix+IMAP,878/1090scheduled và calibration acquisition riêng. Driver scripted/protocol smoke không thay agent baseline. Kết quả âm/ASK nhiều giữ nguyên; H1–H4 là hypotheses phải đo, không là số được lập trình để đạt.

## Vòng 25 — Source/runtime baseline đã setup thực

Trạng thái mới nhất ngày08/11/2026, sau vòng24. Người dùng đã yêu cầu setup và xác nhận chưa có SSH, tiếp tục local. Tải/cài trong `runtime/`; chưa weights, chưa model inference, chưa native agent episode, chưa campaign paper/calibration thật, chưa paid model API. [Receipt](../runtime/agents/SETUP.json) và [dependency freeze](../runtime/agents/requirements-resolved.txt) chỉ xác nhận source/import.

| Source | Thư mục đầy đủ | Commit đã kiểm; tracked source sạch |
|---|---|---|
| AndroidWorld | `runtime/vendor/android_world_full` | `55ddaf5edc6f6c25673aed343907d5b9dca66f84` |
| AgentProg | `runtime/vendor/agentprog` | `ef5e2998ac2defa86e0dc4c13e7e00d595e1e7cf` |
| UI-TARS | `runtime/vendor/ui_tars` | `582f3a7ea5d285ee8ed9e2e84048d1ab01453c49` |
| Mobile-Agent | `runtime/vendor/mobileagent` | `c4cd0a8f9ddedad24dd8a3daf3a56ca69343849f` |

Source pins giữ nguyên [models](models.md). Bản selected-file AndroidWorld trước đó giữ riêng, không thay receipt cũ. Đã cài Python3.11.8 vào `runtime/python`, venv `runtime/agent-venv`; import thực `android_world.agents.m3a`, `t3a` và `env.env_launcher` thành công. Không đổi global Python/PATH. Lựa chọn3.11 phù hợp pinned requirements; matplotlib3.6.1 không có wheel cho Python3.12 trên máy này. Đây chưa là recipe bootstrap tự động hoàn chỉnh cho cả bốn repo.

Đối chiếu source cho bước tiếp: giữ M3A reflection/history, hai ảnh raw+SoM và pause mặc định2s; T3A text-only. Không chạy nguyên `minimal_task_runner.py` với legacy paid-model default. Native environment dùng gRPC; smoke hiện chưa nối AndroidEnv. Factory phải giữ adb server5038/serial riêng, và freeze reader bounds/profile sau native environment setup vì upstream có thể đổi UI settings. Upstream M3A/T3A bắt `Exception` quanh action: controlled stop của protected harness cần đi qua boundary không bị nuốt. AgentProg có pinned Google/protobuf dependencies khác AndroidWorld; phải kiểm hoặc tách env khi cần, không thay program/PC/belief bằng loop tự viết. Các điểm này còn là việc cần triển khai, chưa đóng bằng import PASS.

## Vòng 26 — Input guard và giới hạn Android readiness

Live AVD diagnostic lưu [thư mục evidence](../tmp/resolve-v8/live-01): screenshot/dumps cho thấy SystemUI ANR có thể che role chooser trong khi accessibility vẫn thấy chooser. Không có bằng chứng đủ để chốt nguyên nhân ANR hoặc khẳng định OS đã ổn định. Setup diagnostic có thử Wait/Close trên ANR trong AVD; đó không phải scientific fault/probe và không được tự động đưa vào recovery policy.

`testbed/ui.py` nay so live window token/component với InputDispatcher; reject mismatch, input frozen/missing và display không hỗ trợ. Capture bracket full window identity. Sửa CRLF native adb Windows để parser tương đương LF, tránh false rejection của implementation. Guard này phát hiện modal input đã quan sát, chưa chứng minh không có mọi loại non-focusable overlay. `testbed/tests/fixtures/anr-focus.json` là **synthetic regression combination từ dump thực ở hai thời điểm**, không observation nguyên tử/calibration sample.

Đã chạy lại toàn bộ60testbed tests trên Windows và Linux: [Windows](../tmp/resolve-v8/testbed-tests-windows.json) PASS/1POSIX skip; [Linux](../tmp/resolve-v8/testbed-tests-linux.json) PASS/khôngskip. Các source numerical/artifact không sửa ởv8 nên không gọi đây là một lần chạy lại full25-job suite. [Validation](../tmp/resolve-v8/VALIDATION.json) và [integrity](../tmp/resolve-v8/INTEGRITY.json) giữ test scope và protected-file checks.

[SimpleSMS diagnostic02](../tmp/resolve-v8/sms-live-02/RESULT.json) chọn đúng radio và confirm; `roles.txt` ghi target là SMS holder. Nhưng dialog cũ còn trên màn hình nên NOT_READY. [Cold-start smoke01](../tmp/resolve-v8/sms-startup-01/RESULT.json) sau đó FAILED với XML ParseError; chưa lưu raw lỗi nên nguyên nhân chưa xác minh, không được sửa nội dung XML để ép PASS hoặc suy thành kết quả agent. Owned AVD đã dừng; không có SMS gửi ra ngoài. Các failures trước giữ nguyên. Smoke04/05 cũ không qualify input/capture theo guard mới.

**Việc còn lại và thứ tự:** capture diagnostics/Android readiness → account và task fixtures/reset/grader → native agent environment/action binding → interrupted-effect collector/fate/probe/clock joins → measured calibration → native/protected pilot → full paired paper study. P40/5frameworks/3model pins/878–1090 giữ nguyên; không thêm campaign, phone hoặc dịch vụ riêng cho từng role. Actual H100 fit/throughput chờ có server. Historical mismatch không còn blocker theo quyết định v9. Chưa hoàn thành toàn mục tiêu.

## Vòng 19 — Calibration và decision core

Đọc lại model §3, theory §4 (family/joint/calibration/twohop) và design §5 Algorithm1, đối chiếu với `planner_sim.py`.

| Yêu cầu paper | Code bổ sung/sửa | Bằng chứng cần giữ / còn thiếu |
|---|---|---|
| Nhãn theo interrupted effect, không theo view | `testbed/calibration.py`: quotas pilot0/1, calibration0/1, lag1; duplicate/eval/passive rejected; exact domain/class | Fixture tests; actual collector/fate/probe joins và measured labels chưa thu |
| CP/fixed-sequence/product/source | Reuse numerical CP/certification; region score và candidate grid từ pilot; holdout chỉ tính risk bounds; actual K_total/class/domain multiplicity | Source grid không đổi khi thay holdout; full empirical/proof assumptions vẫn phải kiểm |
| Nonce analytic có điều kiện | Explicit6symbols/Crockford/edit1/M40/no-uncommitted-visible contract; không qualify thì dùng empirical X0 bounds | Reader vượt40tokens→BOT; field/status/app qualifications phải kiểm thật |
| Clock, lag và censoring | `recovery.py`: origin cùng lag law, remaining wait≤120s; censored null→infinity; unknown class intersection/maxwait | Fixture wrong-origin/idle/censoring/unsupported tests; actual boot/recovery/clock receipts còn thiếu |
| Local-only / G2 / Monitor | .9alpha test cho local, no lag; force-stop downgradeG2; pending/failed/stuck/acked paths và handover | Fixture tests; actual app G2/WorkManager/Monitor eligibility chưa có |
| Một read/view, không thêm votes sau crash | `controller.py`: durable STARTED/DONE read cache; interrupted read→BOT; cùng attempt không đổi certificate/domain/context | Crash-mid-read/restart tests; real Android/controller-process boundary chưa đo |
| No certificate/domain mismatch→ASK | Production loader từ chối synthetic; runtime không nhận backend X; backend-visibility qualification cần explicit | Synthetic fixtures không thành calibration; guarantee vẫn conditional trên assumptions |

Một điều chỉnh đúng fixed-sequence: source runtime scores vẫn dùng pilot factors; holdout hop1 rate chỉ vào risk bound. Không chọn score grid từ holdout rồi gọi đó là kiểm định một chuỗi đã cố định. Đây là triển khai cùng source-family rule, không thêm policy mới. Không thay generative model/RNG hoặc archived outputs.

## Vòng 20 — Digest, classifier và model binding

- `probes.py`: digest là multiset/count của matching history items trước/sau tap, kiểm identity/status/bottom. Đổi bounds/layout XML không được coi là new item; old look-alike không thành effect mới. Missing/disappearing baseline→BOT. Concurrent identical effects vẫn có thể gây FP và phải nằm trong calibration.
- `classifier.py`: per-locale text/content-desc/resource-ID lexicon hoặc structured effect annotation như draft; stable(run,task,commit-slot) identity. Không gắn classifier coverage là100%; unknown/no-match vẫn cần E21 và phải báo unprotected false negatives.
- `local_model.py`: thin `predict`/`predict_mm` interface đúng source AndroidWorld pinned. Giữ prompt và toàn bộ ảnh, không crop/truncate/retry/fallbackAPI; T3A text-only; completion sai model/length/error→failure. Binding không thay M3A reflection/history hoặc tự viết agent loop mới. Actual weights/serving/native agent còn chưa chạy.
- Production recovery yêu cầu app-version match, pre-tap semantic snapshot nếu dùng digest, nonce policy availability và current Linux boot identity cho monotonic clocks; XML capture SHA không giả làm semantic digest. Synthetic code tests phải opt-in rõ.

## Vòng 21 — Assets và backend thật

Đã tải Element1.6.62 arm64, K9 24.0, DAVx5 4.5.21-ose, Etar1.0.57 vào `runtime/assets/`; bốn SHA256 khớp historical log. GreenMail2.1.2 đã có từv6. Chưa xác minh APK signatures/installed ABI bằng Android tools nên chưa gọi Android ready.

Synapse1.164.2 và Radicale3.9.0 đã cài vào `runtime/backend-venv` trên WSL; resolved versions/wheel hashes trong `runtime/backends/pip-install-report.json`, freeze trong `requirements-resolved.txt`. Ubuntu thiếu ensurepip được xử lý bằng PyPA get-pip trong venv riêng; system Python không đổi. Setup không dùng latest backend để né pin.

Radicale integration có [RESULT](../tmp/resolve-v7/caldav-integration/RESULT.json): nofault1copy; lostACK+samehref conditional retry412 giữ1copy; newhref/newUID cùng effect content2copies; reject+late sameID0copy. Synapse integration [RESULT](../tmp/resolve-v7/matrix-integration/RESULT.json) PASS: nofault1event; lostACK+sametxnId1event; newtxnId2events; reject+late sameID0event. Đây là payload synthetic qua servers thật, không DAVx5/Etar/Element/Android/model/calibration.

## Pro Expense đã định danh từ nguồn chính thức

AndroidWorld commit `55ddaf5edc6f6c25673aed343907d5b9dca66f84`:

- [ExpenseApp setup](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/setup_device/apps.py) gọi “Arduia Pro Expense”, `app_name="pro expense"`, `apk_names=("com.arduia.expense_11.apk",)`.
- [Expense task evals](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/task_evals/single/expense.py) dùng `/data/data/com.arduia.expense/databases/accounting.db`; chỉ grader được đọc DB.

Chốt package `com.arduia.expense`, upstream APK candidate versionCode11 cho P33–P36. Identity issue đã resolve ở source level; binary SHA/signature/download compatibility, actual UI notes và P33–P36 fixtures còn phải kiểm. Không hỏi lại người dùng để đoán app khác. Selected upstream sources+LICENSE và hashes được giữ trong `runtime/vendor/android_world/`, không gọi đó là complete checkout/install.

## Công việc tiếp theo giữ nguyên scope

1. Hoàn thành protocol integrations và backend/account/reset recipes; cài Android toolchain/verify acceleration/ABI, kiểm APK signature và actual profiles. WSL thiếuKVM không tự chứng minh Windows host không thể chạy AVD; đã thấy HypervisorPresent=true, cần emulator accel-check thực.
2. Nối GUIObserver/collector có receipts vào calibrated controller; nguyên tắc truth/clock/fate/read-once phải đi cùng actual interrupted effects. Không đưa backend oracle vào agent/controller.
3. Nối official framework environment/action boundary và weights serving theo pins; M3A nativepilot trước, rồi protected integration, các baseline khác ởC. Local-model wire tests chưa chứng minh agent đúng/weights đã load.
4. Coverage/actualK_total/quota/cost và labels thật trước protected final; giữ H3 eligibility, H4 risk và ASK≤1/3/q_manual, P40 backend/reset/grader. Không thêm trials chỉ để có kết quả thuận lợi.
5. Dùng frozen new runs làm nguồn chuẩn; số draft minh họa không cần tái tạo. Không dành thêm thí nghiệm để truy discrepancy cũ. Chỉ tái sử dụng raw cũ khi provenance/semantics đủ cho claim tương ứng.

Không đánh toàn goal hoàn tất khi vẫn thiếu các mục trên. Tiếp tục vòng code/plan → test → đọc lại draft; chỉ đóng từng mục bằng evidence đúng scope.

## Vòng 23 — Clock, effect binding và dispatch guard

Đối chiếu lại §5 Algorithm1/nonce/digest/Monitor và §6 fault origins; không sửa manuscript, hypotheses hoặc quota.

- Compiler hỗ trợ `class_origins` đầy đủ, domain `origin_kind=per_class`; mỗi effect phải khớp đúng clock law của class. Runtime unknown-class chờ `max_c(origin_c+w_c)` và giao các certified action sets; thiếu bất kỳ clock receipt cần thiết→ASK. Không lấy max duration cộng vào một origin tùy chọn.
- Stuck/dedup age của Monitor dùng original issued clock, không reset ở recovery. Thiếu clock này không cho pending kéo dài. Collector/official-action adapter vẫn phải nối receipts thật; fixture clocks chưa là deployment evidence.
- Hop1 khi không có nonce dùng matching-item counts đã capture trước tap trên qualified local views; old lookalike không thành new entry, hơn một new entry→BOT/duplicate candidate. Monitor phải bind đúng row/effect, không đọc global pending/acked của mục khác. Profile eligibility vẫn cần chứng minh trên app thật.
- Controller suy lookalike từ semantic baseline đã lưu, không phụ thuộc caller nhớ set flag; VLM được skip theo draft. Prepared app có version pin phải cung cấp full activity/account/window context guard trước issue và ngay sau durable issue; đổi identity→không tap, ISSUED vẫn ambiguous.
- Loader kiểm acquisition spec hash và metadata, classes/families/counts, finite/ranged bounds, monotone fixed-sequence tables, lag/censoring denominator. Checksum không phải chứng minh dữ liệu xác thực; semantic backend/fault/probe/clock joins và true-absent fate còn phải triển khai/kiểm actual collector.

Latest component validation: [Windows](../tmp/resolve-v7/component-final/windows.json)58tests, skip1actualPOSIX; [Linux](../tmp/resolve-v7/component-final/linux.json)58tests, khôngskip. Artifact32tests/host đã PASS và source artifact không đổi trong v7; không chạy lại full25jobs chỉ để tăng số lần PASS.

## Vòng 24 — Setup Android local và app assets

Người dùng xác nhận chưa có server SSH: tiếp tục local, không suy H100 đã fit/chạy. Project-local SDK/emulator37.2.13/platform-tools37.0.2/cmdline-tools19.0/build-tools33.0.2, imageGoogleAPIs API33/r17 x86_64; Java17 đang có. Publisher checksums và acceleration thực trong [BOOTSTRAP](../runtime/android-downloads/BOOTSTRAP.json). `-accel-check` exit0, WHPX10.0.19045 installed/usable; WSL thiếuKVM không chặn Windows AVD.

AVD `ghosteffect_api33_x86_local` dùng2vCPU/2048MB,1080×2400/420dpi; setup không thay Windows features/systemPATH. [SDK install01](../tmp/resolve-v7/android/setup-01/RESULT.json) cài image nhưng fail tên Java main class ở create; đã sửa đúng entrypoint trong `avdmanager.bat`, [setup02](../tmp/resolve-v7/android/setup-02/RESULT.json) tạoAVD và kiểm signatures/manifests PASS. Không thay emulator pin qua dependency resolution. Cách dùng dựa trên [sdkmanager](https://developer.android.com/tools/sdkmanager) và [emulator CLI](https://developer.android.com/studio/run/emulator-commandline).

[Smoke04](../tmp/resolve-v7/android/smoke-04/RESULT.json) PASS actual boot, installed APK SHA, launcher và GUI PNG/XML của Element/K9/DAVx5/Etar. Boot43.58s ở run này; lần đầu154.97s. Đây là startup dưới tải desktop hiện tại, không benchmark throughput hay lag paper. Khi chạy thấy freeRAM khoảng0.5GB; chưa có cơ sở chọn nhiều AVD/localLLM hoặc hứa thời gian toàn campaign. Local model weights/agent inference chưa chạy.

Ba lượt trước được giữ: smoke01 fail focus query; smoke02 streaming reinstall timeout120s; smoke03 lộ stale LastANR focus và missing-package path handling. Đã sửa sang `dumpsys window displays`, từ chối multiple/unknown focus, kiểm exact installed APK trước reuse và dùng adb nonstreaming install khi cần. Smoke04 chụp đúng foreground cả4apps; K9/DAVx5/Etar tree ổn định, Element onboarding carousel chưa ổn định nên chưa qualified profile. Không lấy thêm reads để thay votes trong recovery; các lượt này chỉ development setup. Emulator/adb5038 do smoke tạo đã được dừng.

Element historical ARM64 vẫn giữ byte/hash; port x86_64 versionCode40106624 cùng1.6.62/signer, [source](https://f-droid.org/packages/im.vector.app/), [lock riêng](../testbed/assets-windows.lock.json). Đây là ABI/host stratum mới và cần calibration mới, không gọi byte-identical historical timing.

Năm APK candidate còn lại đã lấy từ GCS URL của [pinned AndroidWorld AppSetup](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/setup_device/apps.py): ProExpense,Markor,Tasks.org,SimpleSMS,Joplin. Cả5qua apksigner/aapt, hashes và actual manifest versions ở [setup03](../tmp/resolve-v7/android/setup-03/RESULT.json) và [catalogue lock](../testbed/assets-catalogue.lock.json). Không suy versionName từ tênAPK: Joplinfile2097740 báo3.0.1, Tasksfile130605 báo13.6.3. Source/package/binary/signature ProExpense đã resolve; actual task UI/reset/grader còn mở. Upstream license metadata cần ghi trước redistribution.

[Smoke05](../tmp/resolve-v7/android/smoke-05/RESULT.json) xác minh installedSHA của cả5candidate trên AVD: ProExpense/Markor/Tasks/Joplin mở đúng package, tree ổn định; SimpleSMS ở `RequestRoleActivity` của Android nên run được đánh **NOT_READY**. Tổng9real apps đã cài,8apps có startup foreground đúng; chưa task functionality/sync/grader. Các lượt06–08 thử roleCLI không thành công: API33 thiếu `get-role-holders`, help exit255 dù in đúnghelp, sau khi sửa xử lýhelp thì actual add-role-holder timeout. Lượt09 dùng selectors từ dialog đã chụp, nhưng sau tap chọnSMS, nút Set as default vẫn disabled; runFAILED và XML trước/sau được giữ. Không đổi rule để coi permission dialog là appready. Flag `--prepare-sms-role` vẫn development/unqualified; cần debug actual input/role controller trước SimpleSMS task runs, không yêu cầu người dùng chọn/duyệt hộ.

Các emulator/adb do09runs tạo đã dừng; chưa có SMS nào được gửi. Failed setup/development runs không cộng vào878/1090 hoặc calibration. [Tổng hợp nghiệm thu vòng24](../tmp/resolve-v7/VALIDATION-v24.json) giữ đủ kết quả dương/âm và source hashes.

**Remaining scope không bị xóa:** accounts + actual compose/history/search profiles và negative controls; calibrated production clock/action/nonce bindings và semantic evidence collector/fate joins; năm official frameworks, model weights/serving/full recipe; P40 init/grader/reset, Postfix/IMAP, MockBankA/B; actual LMK/idle/H3 eligibility và calibration acquisition/coverage/cost; fresh protected/native paired trials. Local smoke không tự đóng các gates này. Archived aggregate discrepancy vẫn unknown, giữ numerical/raw/PDF.

## Vòng 22 — Kiểm phủ định và nghiệm thu component

Windows:32artifact tests (skip1POSIX) +48testbed tests (skip1SIGKILL); Linux:32artifact (skip1SciPy) +48testbed khôngskip. Actual SIGKILL mới giết controller giữa view acquisition sau durable STARTED; process restart không đọc lại view đó. Test còn kiểm T3A không images, M3A không làm mất ảnh/prompt, missing/changed domain→ASK, censoredlag→khôngfinitewait, local budget, source pilot-only grid và semantic digest. Các GUI/model inputs của tests vẫn là fixtures, không chuyển thành real labels.

Đã thử riêng hai giả thuyết về archived `ghost-src`: sửa comparison predicate và so trực tiếp score products thay phép chia. Cả hai variant vẫn cho ASK47.00833% trên5×2400workflows, không giải thích archive47.35%. Giữ kết quả phủ định trong `tmp/resolve-v7/source-boundary/`; không thay numerical source/RNG chỉ để ép số khớp. Conflict lịch sử vẫn mở, đã khoanh vùng thêm nhưng chưa tìm root cause.
