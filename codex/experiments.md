# Danh mục E00–E34 — h100-plan-v6

## Material Passport

- Theo xác nhận mới của người dùng: các tỷ lệ/số kết quả draft chỉ minh họa. Expect trong danh mục này là **mục tiêu phân tích/kiểm tra**, không phải số cần đạt hoặc phải khớp archive. Kết quả mới từ source/config/raw thực chạy là nguồn chuẩn; null/failure/ASK giữ nguyên. Thiết kế/quota của plan được freeze trước collection, tách khỏi outcome minh họa.
- 2026-11-08; một H10080GB vẫn là target. Sau review đã có core fixes, isolated numerical run và protocol smoke; [trạng thái/evidence](code-fixes.md). Chưa chạy Android/model/calibration campaigns.
- **R**: bắt buộc cho revision/review; **S**: scoped evidence B/C sau gates; **X**: extension mặc định OFF. Giữ35 IDs để trace report cũ, không có nghĩa 35 campaigns độc lập.
- [Plan](plan.md), [matrix](study-matrix.md) và [models](models.md) chốt scope/quota/model. Existing artifact không đồng nghĩa independent reproduction.
- Mọi item cần run/config/source/split manifest, raw attempt IDs, exits, truth/clock/denominators/CI/cost và null/negative outcomes. Missingness không bị xóa.

## A. Tái lập và corrections trên CPU

### E00 — Rig/provenance/reconciliation [R]
Mục tiêu: inventory hashes và khai báo provenance/missingness cho các inputs muốn tái sử dụng;72C1/149C2/8sequence là đếm trong artifact cũ, không là quota kết quả mới hoặc target phải tái tạo. Source rig gốc không còn, dùng reconstruction có nhãn; không chờ khôi phục source cũ hoặc ép khớp số draft. Smoke1nofault/1fault mỗi stack trong development để kiểm receipts rồi freeze source/config cho collection mới. Không tự nâng artifact cũ thành measured evidence đã xác minh.

### E01 — Historical pipeline và artifact [R]
Mục tiêu: chạy toàn bộ suite và16REAL4tags trong isolated copy. Đã có `artifact/run_all.py` và25-job PASS, giữ5×2400/cell; không đổi generative model/RNG để làm đẹp số. Expect: per-part exit/schema/count/hash và kết quả đúng source đang dùng. Số archive/draft không là target reproduction và discrepancy cũ không giữ E01partial; chỉ cần trace được run mới. Các sửa provenance/caption/nonce optimization/benchmark readiness sau snapshot được kiểm riêng. **Không chỉnh paper lúc này**; giữ CSV/run outputs cho giai đoạn paper sau, render tests chỉ trong isolated output.

### E02 — Ledger/dispatch/crash/race [R]
Mục tiêu: durable issue trước tap, state guards, no double dispatch. Core API và regression đã sửa/kiểm missing ID, replan COMMITTED, illegal transition, DB error, ASK/PENDING restart,2-worker race và compensation escape. POSIX host benchmark giữ300kills, random window bắt đầu sau first tap để tránh vacuous startup kills. Expect zero violations; actual agent/AVD dispatch/restart integration vẫn cần kiểm, không coi host component PASS là protected benchmark ready.

### E03 — Clock/downtime [R]
Tái lập down5/down15/t0down5/t0down15, matched recovery-origin vs tap-clock; giữ 12k/cell. 60s chỉ targeted sanity, không thêm huge grid. Expect wrong-clock failures được giải thích, correct-origin hoặc ASK, per-effect times rõ. Historical5s product/joint P_v18.82/29.93% là anchors simulation, không target live. Live clocks lấy B0/E10.

### E04 — Unique labels/lag/pilot budget [R]
Giữ historical untied20k và tied2k/5k rows; existing10k/20k/bootstrap tags chỉ reproduction/sensitivity. Kê measured unique, generated verdict/lag, pilot/holdout và overlap. Expect risk/ask/cost table giải thích 12,7% vs tied5k30,6%, không đổi 20k bootstrap thành 20k real quota. Fresh B0 chỉ characterization, không export empirical1% certificate; CERT-1 OFF.

### E05 — Tail/never-visible [R]
Rerun existing tail/tailcal/tail5/tail5tied và thêm đúng tail2,9225% ở5k vì meta yêu cầu; cùng product/source/joint/vetted,12k/cell. Không bắt sweep mọi n×mass×app. Expect failure boundary, asks, censoring; joint có thể fail, không claim tail immunity. Runtime unsupported→ASK/PENDING; không cắt tail để được số đẹp.

### E06 — Fair vetted rules và modes [R; live conditional]
Giữ toàn historical baseline/ablation catalog; vetted được cùng development/calibration labels và lag information mà joint dùng, kể cả CERT-1 nếu bật, với cùng tuning opportunity; freeze một vetted rule, rerun rulesweep/vet/vetk9/vetk9sent. Shared worlds/policy-specific probe RNG được giữ và ghi paired-world design; không tự coi McNemar invalid hoặc bắt rewrite noise generator. Common-noise sensitivity optional, không hard gate. Không xây image counterfactual bank hoặc reuse screenshots sau live policy đổi state.
M1 always-ask là policy reference/simulation; không Android trials để đo ask100%. M2–M7 simulation/replay hợp lệ. Nếu C-guard đủ scientific gate, M5 chạy thêm 12 sentinel cases, không 84 cases/7arms mặc định. Expect equal-data risk/ask/cost/CI hoặc parity, không ép rules thua.

### E07 — Fault class/mix/fallback [R]
Rerun pooled/mixlab/mixkeyed/unknown và netlab/netlabkey; bổ sung một wrong-class counterexample, không broad grid. Expect known/unknown/wrong-class khác nhau, observed receipts và K_total accounting. Wrong class có thể unsafe; class/key unsupported→ASK. Live confusion traces lấy B/C, không coi am-kill no-op là LMK.

### E08 — Fitted-law uncertainty [R]
Nested simulation **3 calibration fits×3 eval seeds trên 3 headline configs**; historical5 seeds vẫn giữ. Source-effect bootstrap có nhãn simulation, conservative uncertainty envelope, conditional asks. Expect range/variance/q1/q0, không coi shared fitted law là independent real evidence. 27 fit/seed/config combinations là auxiliary analysis, không fresh device labels.

### E09 — Numerical/theory/sample sizing [R]

V7 thêm compiler/sizer/runtime tại `testbed/calibration.py` và `recovery.py`; `--size-plan` ghi best-case zero-event minima từ actual spec/K_total, không là sufficient guarantee. Read-once/domain/censoring/pilot-only fixed grid có tests; actual measured acquisition và whole stopping/domain proof audit chưa đóng. [Evidence](resolve-progress.md).
Minimum search đã sửa theo ceil(p*n) intervals, kiểm independent SciPy references; empty-denominatorN/A và asymmetric delta đã triển khai. E09 vẫn cần full stopping/handover/skip, lag order statistics, X/backend proof-domain và actual coverage K_total/acquisition design. CERT-1 không mở chỉ vì numerical unit tests PASS; không dùng historical simulation labels làm real certificate.

Sizing phải dùng actual coverage/multiplicity trước khi chốt holdout n: 5000 không phải default chứng nhận đủ. Ví dụ zero-exceedance/target.002 với K_total55 cần5453 mẫu, không4947 của K20; đây là minh họa, không K thật đã freeze. Candidate CERT-1 không thay collection plan cho các domains cần bảo vệ. Expect fixed acquisition budget/cost và explicit ASK coverage, không full-factorial11k/domain hoặc stop-when-pass.

## B. Một corpus dùng chung và vài substudies nhỏ

### E10 — Fresh clocks/lag [S; correction R]
Dùng B0=320 effects, split80development/240evaluation; fault classes phân bổ trong mỗi(config,outcome), không calibration-smoke cohort. Log issue/tap/commit/kill/relaunch/restore/polls, clock offsets và observed class. Final dưới load đã freeze, khác ngày dev khi khả thi.
Expect raw points/min/median/max/censoring và correct-origin/ASK behavior; không certify tail từ n nhỏ. Đo natural/app visibility và reader/navigation lag riêng khi timestamp cho phép. Recorder/rig/reset còn thiếu.

### E11 — Terminal absent/unobservable [S B0]
4 configs×2 outcomes×40=320 scheduled effects; mỗi group10development/30evaluation. Target outcome không phải truth: trueX0 cần terminal pre-apply reject/fate proof, X1 có backend receipt, pending giữ unknown/censored. Class/outcome cell small-n, không 1%certificate.
Pre-apply reject phải scope đúng original request và các late retry cùng ID, không vô tình reject cả GUI retry mới rồi gọi retry failure. G2 app không tạo terminalX0 được thì N/A/unknown, không fake balancing. Never-visible challenge thuộc dev/outside-domain khi cần. Expect label/visibility confusion/BOT và counts có provenance.

### E12 — Causal fault trước retry ACK [S]
B1=**15 cases**: Element một config,3 response-loss forms(clean RST/sticky/withheld)×5, chọn một meaningful commit-before-ACK fault schedule. Reset queue mỗi lần; log ACK/request/PID. Expect mechanism traces tách retry cùng ID và GUI redoID mới; giữ limitation60 historical cells đã ACK trước fault. Không mở135-cell Cartesian campaign.

### E13 — K-9 action audit/unattended [R audit; S B2]
B2=15 action-audit trials:3paths(explicit Send messages, Sync, no action)×5 trong một lost-ACK/no-Sent fault config đã pin; không nhầm3fault subcells với 3 actions. Chốt cửa sổ action→DATA trước mọi GUI-redo diagnostic để tránh contamination.
Thêm8 unattended cases=2Sent modes×2background states×2, ≥20phút/case. Log verified tap, DATA/Message-ID/SentAPPEND/copies. Expect trả conflict12no-Sent rows và small descriptive pending/survival; unknown vẫn unknown, U(45,900) còn assumed nếu chưa đủ data. Không tự sửa historical provenance.

### E14 — Screen validity/digest attribution [R audit; S B0]
Dùng B0 development80 effects và stored/synthetic fixtures cho wrong identity, stale forwarder/digest, old matching item, concurrent event, missing snapshot; ≥5fixtures/failure family, không 5fresh effects bắt buộc cho mỗi tổhợp. Frozen reader chấm evaluation240 effects, không chọn test dễ.
Expect present/absent/BOT/source co-failure và uncertainty; label synthetic/stale-injected challenge riêng, không coi repeated screenshots là independent new effects. No oracle-assisted navigation/reader.

### E15 — Real VLM verifier [S]
V1Qwen7B BF16, V2OFF. Chọn200B0evaluation effects(100/outcome từ 120/outcome, stratified IDs/seed trước scores). Một call cho mỗi available list/detail/search view, tối đa 600 calls; skip/BOT đúng contract. Offline exact-input memoization giảm repeated analysis, không tăng n hayreuse live effects.
Expect whole-effect error/BOT/correlation vớiCI và source availability; không có đủ wrong events thìH2inconclusive, không proofindependence. Native agent vision không thay verifier evidence. Processor/history recipe và parsed coordinates phải giữ đúng; không global2-image truncation.

### E16 — Dedup scope/natural horizon [X]
Historical8-step sequence/spec scope được audit ởE00/E01; không claim natural24h từ timestamp shift. Nếu mở:3 independent ≥24h sequences với same/new key/device và separate namespace. Expect scoped horizon, không broad guarantee. OFF không chặn core; không rút horizon cho throughput.

### E17 — Missing/discarded/ANR [R]
Audit7 lostElement/4 C1 discards/carry-over, toàn attempted legacy history. Future attempt ledger tạo trước action; failure fixtures lấy B0 dev, không cohort riêng. Expect intention-to-run/completed/unknown +best/worst-case sensitivity. Không tự điền fate chưa có.

### E18 — Measured cost/load [R]
B0development80 effects phân bổ20/20/40 cho concurrency1/2/4 AVD, configs/outcomes córeceipt, không phải 80×3. Ghi full reset/fault/read/followup/backend/inference queue/tokens/failures. Native model request cost lấy thêm từ A-dev và dev adapters, tách script label cost khỏi agent cost.
Expect median/raw time, p95 chỉ diagnostic cón/method, actual GPU peak/CPU/KVM/NVMe và forecast878default attempts. Chọnload trước final240 effects/C; không dùng final để tune. Giảmconcurrency trước input/history/precision. Chưa benchmark server thì lịch chỉ assumption.

V6 chỉ xét1/2/4 AVD. Phân bổ configs/outcomes/faults giữa load blocks trước run; báo thành phần để tránh quy khác biệt task thành speedup. S15 dùng dev request fixtures của từng framework/topology để bổ sung load test; không lấy B0 scripted throughput làm agent throughput. Không thêm8AVD/grid hoặc số effect mới.

## C. Agent và controller

### E19 — Native LLM resend [R A; S C-native]
A-dev=10 nofault M3A dev; A-native=20fresh native K-9 postcommit/lost-ACK targets,10Sent/10no-Sent. Chạy sau model/rig/grader/barrier gates, không đợi guardedledger/5adapters. Chỉ hoàn thành reviewer requirement khi ≥10actual valid committed/interrupted cases, không chỉ 20 attempt IDs.
Native restart giữ đúng memory/recovery của framework; nếu không persist thì cùng task+freshGUI, không hint truth/resend hoặc áp checkpointpolicy mới. C-native=5×40 native interrupted +5×40 native nofault=400 episodes;20X1/20X0 targets/agent theo matrix, notnatural prevalence.
Expect conditional resend/dup/loss/false-success/abandon và CI, nofault baseline, attempts/reachedcommit/validfault/actualX denominators. Null được giữ, reasoning failure không rerun để đổi kết quả.

### E20 — Protected integration và paper end-to-end [R A-guard; required paper C-guard]
A-guard=20 protected integration episodes, thuộcA50; chỉ sauE02/S05/S10, foreground/oracle isolation. Scope một effect/task, stable(run,task,commit-slot) mapping; không fullsemantic-intent/saga engine.
C-guard startup OFF vì chưa ready; đây là required stage để đánh giá planned device study/H4. Hoàn thiện calibration/lag/proof coverage và freeze native/protected controls trước final, rồi200protected+12M5sentinels. Unsupported→ASK, vẫn trong denominator; không chọn app/region có score tốt. Valid calibration nhưng ASK100% là negative result, không gate chỉ cho positive outcomes. Nếu chỉ có thiếu calibration thì H4 vẫn missing evidence. Không dùng B0eval/fitted tables làm certificate.
Expect dispatcher/restart/Monitor/ASK correctness; autonomous P_v/L_v và ASK/unresolved cóbounds status rõ. Quan sát copies tới fixedhorizon; no useranswer→unresolved, không actual resumedworkflow success. H4 giữ frozen full task population, ASK≤1/3 và risk-contract status; report uncertainty/timeout/unresolved, không chuyển riêng Element sau scores. Chi tiết estimands/CI ở paper-alignment. Controller/calibrationcode vẫn thiếu.

### E21 — Commit classifier/foreground guard [S]
**200 action annotations** từ traces:120 development+80 heldout, phân tầng commit/non-commit; ≥50 double-labeled với adjudication. Split theo effect/workflow, không 200 device episodes mới. Frozen classifier chấm heldout annotations và live task-boundary truth, không chọn lại dễ. Expect recall/FN/FP/CI, foreground/account mismatch→block/BOT. n nhỏ không chứng minh coverage mọi risky tap; pilot có thể annotated commit points và báo scope đó.

Classifier/reader/dev→heldout split phải được chọn trước và freeze trước B0 evaluation240, không chỉ trước C. Không dùng80 heldout labels để sửa classifier rồi tiếp tục gọi B0 là evaluation độc lập; lỗi phát hiện sau freeze được giữ và sửa ở revision/dataset khác nếu cần. Không suy200annotations là200independent workflows; báo positive/negative counts và grouping.

### E22 — Process death/LMK [S B3]
Process/ledger boundaries dùng E02; B3schedule10memory-pressure LMK target events trên một AVD/appconfig. Verify lmkd/process exit/restart, no-op không thànhLMK; không bắt retry tới đủ 10valid events. Expectedmechanism receipts và survival limits, không OEM robustness/1%survival certificate. Controller trên host khác Androidapp failure domain, ghi đúng scope.

### E23 — Doze/Standby/Data Saver [S B4]
B4schedule60 cases:3 states×2 outcomes×10, một Elementconfig; entry/exit/network/jobs receipts. Không nhânagents/apps. Unknownstate→ASK, không dùng active calibration choidle.
Expect measured visibility/pending/wake và uncertainty; outcome/state không valid thìfailed injection/unknown giữ ledger, không auto-fill quota hoặcclaim state thật từ flagplanned.

B4 giữ60cases, ba trạng thái Doze/App Standby/Data Saver được pin và ghi restrictions/exemptions riêng, không coi chúng là một state chung. Agent đã dừng trong idle interval; ghi screen-off, state entry, interval, network/jobs và state exit trước GUI recovery. Freeze idle duration trên dev và log actual duration. Không mở màn hình/relaunch để đọc rồi gọi đó là quan sát khi vẫn Doze; các thao tác đó phải được ghi vào exit/recovery origin. Passive system/backend logs chỉ ở test apparatus, không vào decision path. Forced-state AVD test không thành natural overnight/OEM evidence. [Android test protocol](https://developer.android.com/training/monitoring-device-state/doze-standby#testing_doze_and_app_standby).

### E24 — Phone/on-device service [X]
Không cần để mởA/B/C. Nếu giữ phone-specific claim mới port helper/service và đo100 normal effects/app cùng boundary cases, phone riêng. Expect actual phone overhead/survival, không extrapolate host timing. Hiện Android foreground service/device instrumentation chưa có; không dùng phone cá nhân.

### E25 — Durability/power boundary [R existing audit; X new physical]
Audit existing host300 kills và qemu3 trials/mode; Linux process-crash regression dùng E02. Nếu mở:long-lived WAL FULL/NORMAL/OFF, ≥10 cases/mode/boundary ban đầu và external acknowledged truth. Expect phân biệt process vs OS crash vs physical power; qemu-kill không thành actual power loss. Không cần mua/dùng phone cho core.

### E26 — Nonce/digest/content [R field audit; S fresh]
Giữ gx:+6 Crockford symbols, retry same nonce; K-9 field thực subject/body/visible opt-in có log. Dùng B0 evaluation screens và dev fixtures wrap/Unicode/old/concurrent, không thêm large corpus. Expect FN/FP/BOT/content-delta và exact-content controls, không claim10^-6 false match từ n nhỏ. Nonce không thành server idempotency key.

Historical/A/B K-9 giữ subject; P-final chọn body theo app table khi opt-in, nếu không nonce OFF. Không coi optimistic Outbox/draft/failed-entry chứa tag là nonce-present của committed effect; hop1 reader và committed-history nonce reader có semantics khác nhau. Acceptance fixtures cho negative/source-attribution và local .9alpha test allocation dùng cùng E09/E14/E26, không cohort mới.

### E27 — Element E2EE [X]
OFF; encrypted-room fixture/verified-device/reset keys còn thiếu. Nếu mở40 committed pilot(4×10) và true-absent coverage riêng; re-calibrate khi law đổi. Có thể chạy trên AVD, không bắt phone vật lý. Expect scoped mechanism/readability, không coi plain room đã phủE2EE.

### E28 — Saga/compensation [R simulation; X full runtime]
Giữ sim_saga/KKT/union-budget reproduction, uniform ablation. A/B/C task chính một effect; không cần full saga engine. Nếu mở actual runtime:workflow k2/4,10 schedules/config trước, new-effect compensation/ASK restart/pending. Expect budget/ledger correctness; không nói simulation đã chứng minh compensation runtime.

### E29 — Drift/pooling [R simulated; X real multi-version]
Giữ existing drift/class sensitivity và unknown-state fail-closed. Không build region pooling detector hoặc collect nhiều devices/versions cho core. Nếu mở:≤200 dev effects/target stratum để cost/power exploration rồi chốt final n riêng; no reject không proof exchangeability. Expect rate/dependence shift và typeII, không auto-poolB0 giữa agents/apps.

### E30 — User error/composed risk [R synthetic; X human study]
Báo q1/q0 và r1/r0 residual paths; historical user5%/look-alike10%/delay60s giữ. Live ASK dừng với escalation/unresolved, oracle xử lý ASK chỉ ở analysis riêng; sensitivity0/1/5/10/20% bằng simulation/replay, không real extra cohort. Expect proper composed risk/final outcomes; không gọi synthetic replies là measured human behavior. Không cần tuyển người choA/B/C.

## D. Required app catalogue và các extension theo claim

### E31 — App capability/task inventory [R; required paper fixtures]
Paper target dùng P01–P40 trên10app/variant entries của draft; T01–T40 trên3stacks chỉ prototype/review-core. E31 phải hoàn thiện package/version/ABI/signature, nonce/digest/G2/commit semantics, init/grader/reset và applicability. Không chạy thêm T400 mặc định. Pro Expense `com.arduia.expense`, APKcode11/1.0.0-beta05 đã source/hash/signature/install/launch verify ởv7; tiếp tục actual task validation, không tự thay app.
Expect measured/planned/unsupported matrix và frozen40tasks; local-only apps inject quanh persistence, không fake network fault. P allocation có6/6/4/4 class targets/outcome, T5/class/outcome; không factorial/generalization claim.

P17–P20 final pin Postfix + local IMAP như draft, A/B vẫn GreenMail. Xác minh WorkManager-based outbox/G2 và F2 force-stop applicability cho H3 trước freeze; dùng existing C0/C2 slots khi phù hợp. Chưa có eligible app/case thì H3 NOT_TESTED, không dùng E22 LMK hay mặc định Element để tuyên bố đã kiểm H3.

### E32 — MockBank-A/B [required for paper catalogue; not review-core blocker]
Implement app/backend tối thiểu hai config: request-ID dedup và không dedup, synthetic balances/private notes, receiver-side attempt/commit ledger, reset và response-loss barrier. Client phải persist request ID/outbox trước dispatch, retry cùng ID sau restart; kiểm actual dedup scope/horizon. Backend dedup đơn lẻ chưa đủ để gọi client G2. P25–P32 tái dùng runner/controller chung, không thêm480trials hoặc build financial platform.
Expect scoped mechanism contrast và truthful backend copies; dữ liệu synthetic app là controlled experiment, không real banking evidence. Chưa có code; đây là implementation dependency để giữ full app scope.

### E33 — LP/optimal policy [X]
Tiny same-information exact/LP instances nếu cần giải thích certification slack; không solver framework lớn. Expect optimality gap/lower-bound có scope, có thể không đáng triển khai. Chưa có solver connector; không chặnA/B/C.

### E34 — PRISM/Storm [X independent checker]
Một restricted instance hiện có, đúng constants/version/hash và DP comparison; không mở model toàn Android. Expect reachability/expected-reads match hoặc discrepancy điều tra. External logs chưa có; checker không chứng minh joint runtime/ledger.

## E. Nghiệm thu

Review bắt buộc mapping tại [review-loop](review-loop.md). R được đóng bằng evidence đúng scope hoặc limitation/minimal correction xác định; không phải mọi X phải chạy. S chỉ đánh passed sau traces thật. H4 usefulness và 1% empirical certification có thể còn unverified dù runtime technically correct; không đánh paper hypotheses đúng bằng một checklist xanh.

C-guard chỉ là212extras khi eligibility/config/resident topology đãfreeze trước C-native final và C0 là matchedcontrol. Đã chạy native single-engine khácconfig thì khônglate-enable; follow-up phải studyversion/nativecontrols/budget mới. Đây không phải instrumentation retry.

## E19–E21: analysis và completion boundary v5

C-native là400episodes trên registry P cho paper_draft, T chỉ khi chọn review_core rõ trước final; không tự cộng cả hai. C-guard200 và12M5sentinels đưa tổngA/B/C lên1090, chưa calibration. H4 không bị đổi thành optional extension.

E15 dùng paired error-count tables theo actual outcome/view; missing/BOT riêng, zero-variance→correlation N/A, whole-effect unit. E21 split theo task/effect, report sampling scheme; stratified labels không tự cho deployment PPV/prevalence. H4 q_ASK point target≤1/3; bootstrap task-block sensitivity10k/seed6104, không claim population CI nếu không có sampling assumptions.12M5sentinels là wiring, equal-data comparison chính ở simulation/replay; không kết luận live superiority từ12cases. [Đối chiếu chi tiết](paper-alignment.md).

E19/E20 follow-up H_eval300s từ verified recovery origin (nofault từ primary commit dispatch), app/backend namespace giữ tới horizon; no-commit/failed injection báo ITT riêng. H4 phải có q_manual≤1/3 bên cạnh q_ASK để tránh timeout/abandon bị tính như autonomy. X0 vẫn cần terminal fate proof, không chỉ hết window.
