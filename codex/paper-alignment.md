# Đối chiếu mục tiêu paper và kế hoạch thực thi — h100-plan-v6

## Material Passport

- Người dùng đã làm rõ: draft mô tả phương pháp/thiết kế; các số kết quả chỉ minh họa, không phải ràng buộc tái tạo. Đối chiếu bám pipeline, scope và estimands; dữ liệu mới có receipts là nguồn chuẩn. Không ép outcome theo H1–H4 hoặc archive.
- 2026-11-08; review inline và các vòng implementation/test tiếp theo, không reviewer độc lập. [V7 evidence/progress](resolve-progress.md) phân biệt numerical/protocol smoke với Android/LLM study chưa chạy.
- Nguồn trực tiếp: [planned study](../manuscript/sections/07-evaluation.tex), [app table](../manuscript/sections/tab-apps.tex), [implementation](../manuscript/sections/06-implementation.tex), [design](../manuscript/sections/05-design.tex), [review](../review.md).
- Mục tiêu lượt này: kế hoạch đúng phạm vi và có thể triển khai trên một H100. Chưa chứng minh hypotheses, readiness runtime hoặc hiệu năng tối ưu.
- V4 đã giảm việc thừa nhưng thu hẹp device study thành review-core. V5 khôi phục full paper target; v6 đối chiếu lại PDF trang11 §7.8 và trang18 Table10 với source, sửa backend/topology/calibration/H3. T-prototype không được thay P-final.

## 1. Requirement-to-evidence audit

| Yêu cầu gốc | Kế hoạch và evidence cần tạo | Hiện tại |
|---|---|---|
| Pipeline GUI-only, durable issue, nonce/digest/hop-1/Monitor/wait/budget/ASK | E02/E03/E07/E09/E20/E21; inspect dispatch order, certificates, oracle isolation, restart traces | Calibrated runtime/compiler/read cache/digest/classifier/GUI adapters có component tests; actual Android/agent integration và calibration còn thiếu |
| Năm frameworks, 40 tasks trên app table (§7.8) | P01–P40 ở matrix; five adapters, app pins, init/grader/reset, native/protected arms | Task proposals mới; apps/pins/fixtures còn thiếu, không gọi T40 là full coverage |
| Native duplicate/loss/false-success, H1 | E19, C-native nofault/interrupted; actual backend copies, reached-commit/fault receipts, fixed follow-up | Chưa chạy LLM agent |
| VLM error/correlation, H2 | E15, synchronized screen/tree, paired view error bits, ground truth riêng, missingness/CI | B0 corpus và verifier chưa có |
| Real memory pressure và idle lag | E22/E23; lmkd/process receipts và idle entry/exit/network/jobs receipts | Stressor/collector chưa có; am-kill no-op không thay LMK |
| Commit-classifier recall | E21; 200 action labels120dev/80heldout, ≥50 double-label; split theo task/effect | Lexicon classifier đã có code; chưa labeled heldout corpus/recall evidence |
| GhostEffect end-to-end và H4 | E20, 200 protected + calibration coverage, matched controls, ASK/risk/cost/CI | Bắt buộc trong roadmap paper; false startup flag không xóa yêu cầu |
| Review: native≥10 K-9 cases | A-native20 scheduled, ≥10 actual committed/interrupted valid cases | Chưa đạt; planned attempts không chứng minh actual n |
| Review: origin5/15s, tied2k/5k, tail2.9% at5k, vetted rules | E03–E09, original/corrected outputs và provenance, equal calibration information | Có historical outputs, chưa có fresh reproduction/corrections |
| Nonce field/consent, composed risk, reproducible anonymous rig | E26/E30/E00/E01; field/content receipts, q1/q0/r1/r0, attempt+source manifests | Còn thiếu verification; paper rewrite/publication ngoài lượt này |

Plan audit hoàn tất khi từng hàng có procedure, unit, gates, output và dependency rõ. Các trạng thái chưa chạy vẫn mở; không đổi requirement thành kết quả đã có.

## 2. Phân bổ task và tránh thu hẹp ngầm

P01–P40 bao phủ 10 app/variant entries của draft, bốn task proposals mỗi entry. Bảng apps không quy định4/app; allocation này giữ40 tổng mà không nhân full factorial. Không chạy thêm T400 mặc định trước P400.

K-9 Sent/no-Sent vẫn có A/B characterization; registry P giữ hai config trong bốn K-9 tasks. MockBank-A/B là hai biến thể có/không dedup, chỉ cần app/backend tối thiểu đúng contract. Không xây banking platform, payment integration hoặc dùng tài khoản tiền thật.

Package/version/ABI của mỗi entry phải được pin trước final. Pro Expense đã định danh từ AndroidWorld source pin: `com.arduia.expense`, APK `com.arduia.expense_11.apk`, manifest1.0.0-beta05; [nguồn/verification](resolve-progress.md#vòng-24--setup-android-local-và-app-assets). Binary/hash/signature đã verify; task UI/reset/grader còn phải kiểm. Không thay app expense hoặc tăng task Markor.

Backend mail là sai khác cụ thể đã sửa ở v6: PDF/Table10 nêu Postfix, còn measured campaign dùng GreenMail. Vì vậy historical/A/B giữ GreenMail, P17–P20 final dùng Postfix + local IMAP cho hai Sent configs, pins/reset/proxy/grader còn phải xác minh. Chúng là domains khác nhau; không transfer calibration chỉ vì cùng client K-9. Không cần campaign Postfix characterization riêng ngoài P development/final đã có.

T40 chỉ làm dev/prototype hoặc review-core campaign có nhãn riêng. Không dùng số task giống nhau để tuyên bố tương đương scope. Với paper_draft, faults/outcomes vẫn phân bổ20X1/20X0 targets; local apps chỉ applicable kills, nên class coverage P là6/6/4/4 mỗi outcome, T là5/5/5/5. Actual fate quyết định truth và coverage.

## 3. H1–H4: mục tiêu, estimand và kết quả kỳ vọng

| Hypothesis | Thiết kế/estimand | Kết quả cần xuất và điều kiện diễn giải |
|---|---|---|
| H1: redo-based agents duplicate phần lớn committed interrupted effects | C0 thực tế X1/reached commit/valid interruption; native nofault control; stratify framework/app/fault | Resend, copies>1, false-success, loss, abandon và denominators/CI. Không áp H1 cho toàn bộ five agents nếu chỉ subset có redo behavior; negative result giữ nguyên |
| H2: VLM errors across views positively correlated | E15 paired list/detail/search trên cùng effect; X1/X0 tách, screen validity/BOT tách | Joint error counts00/01/10/11, marginal/co-error rates và CI theo effect; phi/correlation chỉ khi variance khác0. Không đọc được view→missing/BOT, không gán error0; phân biệt lag-blindness với perception error sau visible |
| H3: force-stop breaks G2 for WorkManager outboxes | E31 xác minh actual WorkManager outbox/G2 và eligible F2 slots, freeze force-stop subtype; dùng C0/C2 với same-key retry/ACK/relaunch/backend receipts | Hiện chưa định danh app eligible nên đây là dependency mở. Không có eligible app hoặc valid n=0→NOT_TESTED. Element/DAVx5 không phải mặc định; LMK không thay force-stop; không thêm app/campaign chỉ để lấy positive result |
| H4: risk within budget và ASK ít nhất3× thấp hơn always-ask | 200 protected one-effect tasks, cùng frozen population với C0; always-ask reference q=1; paper metric q_ASK và unresolved/timeout riêng | q_ASK≤1/3 là point target. Primary là point metric trên fixed benchmark; báo task-block bootstrap95% sensitivity interval và per-framework/task results. Kết luận cho population rộng hơn cần sampling/CI assumptions riêng. Không xóa unsupported/ASK-heavy apps, không đổi population sau score; timeout/unresolved không tính là successful autonomous recovery |

Các hypotheses có thể rejected hoặc inconclusive. Mục tiêu thí nghiệm là phân biệt cơ chế và kiểm định, không ép kết quả ủng hộ paper. H4 còn thiếu calibration là missing evidence, khác H4 đã được test và không đạt.

Live ASK kết thúc epoch với unresolved/escalation. Báo số server copies ở fixed horizon; không giả lập user answer thành measured completion. Composed duplicate/loss khi user sai chỉ ở simulation/sensitivity riêng nếu chưa làm human study.

## 4. Risk guarantee khác finite-run confidence

- Autonomous certificate phải đúng app/backend/model/processor/reader/fault/origin/load/population và stopping contract. Một verifier dùng chung weights không tự chứng minh independence hay transferability.
- B0eval không calibration; fitted-law/bootstrapped synthetic labels không thành fresh device effects. CERT-1 chỉ là candidate sample recipe; actual K_total/censoring/CP/lag/certification feasibility phải kiểm E09.
- Với iid Bernoulli, zero errors trên100 effects cho one-sided95% upper bound ≈2.9513%; trên200 ≈1.4867%. Muốn bound≤1% với zero errors cần ít nhất299 valid independent effects cho MỘT endpoint/domain, chưa multiple testing. Đây là arithmetic planning reference, không quota tự động.
- 200 protected tasks có target outcomes khoảng100/100 tổng, thực tế valid n có thể ít hơn và chia theo agent/app nhỏ hơn nhiều. Không gọi zero observed errors là empirical1% theo stratum.
- Nếu formal certificate hợp lệ, báo guarantee dựa trên proof/calibration contract và test CI riêng. Nếu mục tiêu là empirical≤1% thì phải chốt n/power/cluster/multiplicity budget trước collection; không tăng n sau khi thấy lỗi để pass.
- Shared tasks, repeated views, calibration reuses và one-seed task blocks không iid populations. Report task-level blocks/paired controls; bootstrap nếu dùng chỉ phản ánh sample design và không tạo population generalization.

V6 giữ quota vì 600 C episodes đã có native interrupted/nofault/protected cho five frameworks/40 tasks. Điều này đủ mô tả benchmark và failure mechanisms, chưa phải power cho rare events riêng từng cell; không cần tăng repeats một cách tự động. Mỗi framework có20 committed interrupted targets/arm trước invalid cases. Muốn empirical1% per-framework là scope/budget khác, không được suy từ tổng1090.

Calibration sizing phải tính actual K_total/candidate selection/censoring trước collection. Với delta=.01/(10 K_total), target lag.002 và zero exceedances, K20 cần4947 nhưng K55 cần5453; con số5000 trong CERT-1 không là guarantee. K55 chỉ ví dụ số học, chưa phải multiplicity thực đã chọn. Không bootstrap thành fresh labels hoặc full-factorial11k mỗi app/agent/class. Coverage forecast trên dev phải nêu phần buộc ASK; actual U/N_epoch sau run là lower bound cho q_ASK. Nếu forecast vượt1/3 thì báo feasibility issue/negative utility, không chọn lại easy tasks.

## 5. Code tối thiểu cần hoàn thiện

| Thành phần | Reuse | Phần còn thiếu / acceptance |
|---|---|---|
| Rig/proxy/reader | Original source không còn theo xác nhận người dùng; reconstruction ở `testbed/` | Proxy barriers/reject/GUI reader có component tests; actual app profiles/reset/fate/clock và Android receipts còn thiếu |
| Controller | Guarded ledger, semantic digest, compiler/loader/cascade, per-view durable cache và GUI Monitor adapter có tests | Stable agent commit-slot mapping và actual app/certificate/clock integration chưa kiểm; production Windows boot-clock adapter còn thiếu, Linux boot identity đã có |
| Agents | Pinned five upstream frameworks | Thin Android/environment/model bindings; AgentProg hard-code patch; history/parser/coordinate parity; model errors không bị che |
| Tasks/apps | Three measured stack recipes và AndroidWorld primitives | P40 init/success/tear_down, package/ABI/signatures, backend namespaces; mock A/B tối thiểu; no unpinned replacement |
| Truth/split/analysis | Numerical references/N/A/conditional counts và backend grader đã có | Fresh immutable attempts, joined fate/clock/GUI evidence, effect-level split và hypothesis summaries/CI còn cần chạy |
| Serving/scheduler | Isolated checked CPU runner đã có25-job PASS; vLLM profiles mới ở mức plan | Actual one-/two-engine peak test, workload blocks, queue/reset timings và H100/AVD execution còn thiếu |

Topology v6: engine theo checkpoint, role→endpoint bằng config. A1/A2 dùng một Qwen engine cho agent/V1; A3 dùng Qwen cho workflow/executor/V1 và UI-TARS cho locator; A4/A5 protected thêm Qwen V1 cạnh native model. Vẫn tối đa hai engines, prompts/history/permissions riêng. Shared serving là optimization thiết kế, chưa benchmark và không chứng minh statistical independence. E18 core chỉ1/2/4 AVD, không8-worker sweep.

Một runner theo stage + thin adapters đủ; không service-per-role, semantic-intent framework, new simulator RNG engine hoặc full compensation subsystem. Trạng thái code/evidence ở [code-fixes](code-fixes.md); reconstruction có modules runnable, chưa có Android/LLM end-to-end verification.

## 6. Các đầu vào cần người dùng/tác giả xác minh

| Đầu vào | Ai có thể giải quyết / fallback | Ảnh hưởng |
|---|---|---|
| Original shared-android/snapshots/raw screens/missing attempts | Người dùng xác nhận không còn source khác; đã reconstruct có nhãn, giữ historical unknown; không hỏi lại cùng đầu vào | Exact historical provenance không thể khôi phục bằng code mới |
| Pro Expense task capability | Source/binary/SHA/signature/install/first-launch đã verify; actual P33–P36 task UI/reset/grader còn mở | Full P40 task coverage |
| APK/backend/model availability, licenses, exact hashes | Người triển khai xác minh từ nguồn chính thức; alternate binary là stratum mới | Setup/compatibility |
| Server CPU/KVM/SSD/access | Người có server chạy preflight/readiness khi implementation được bắt đầu | Effective concurrency, calendar forecast |
| Calibration law/domain có recovery visibility và true-absent fate phù hợp | Implementer thu fresh labels sau E09; tác giả cung cấp provenance nếu dùng existing data | Protected autonomy, H4 |
| WorkManager-based outbox/G2 và eligible force-stop slots | E31/source+dev receipts, không suy từ tên app | H3 hiện chưa có subgroup đã xác minh |
| Muốn claim physical phone/OEM/energy hoặc human recovery hay không | Ngoài đích Android AVD hiện tại; chỉ mở khi có yêu cầu riêng | Không cản A/B/P40 trên AVD |

Không cần hỏi lại quyền sửa plan. Các điểm trên là dữ liệu không thể tự xác nhận, không phải lời yêu cầu dừng công việc đã được phép.

## 7. Completion boundary của lượt review

Đã chọn roadmap giữ đủ paper target, tách milestone878 khỏi protected+coverage/calibration; model/inference giữ một H100 và không silent input reduction. Các E/R/S/L IDs được giữ để trace. Checklist experiment vẫn mở; benchmark và hypotheses chưa chạy.

Không tuyên bố “sát nhất/tối ưu nhất” bằng số học VRAM hoặc audit Markdown. E18/S15 chốt throughput/memory, E19–E23 và full P40 chốt evidence khoa học. Không viết lại manuscript trong lượt này.

Analysis freeze: dùng seed6104 cho10.000 task-block bootstrap resamples (40task IDs, five frameworks đi cùng block). Interval percentile là empirical task-mix sensitivity, không certificate hay confidence guarantee cho apps ngoài registry. Giữ exact CP theo đúng iid/calibration assumptions của historical/numerical track; không áp CP một cách mặc định cho mọi heterogeneous task aggregate.

P40 có10app/variant entries nhưng11config identities vì K-9 Sent/no-Sent. Request/effect matching phải phân biệt primary logical create/save với background metadata/sync traffic. Không giả mọi notes app có atomic commit tap; unsupported autosave boundary phải được giải quyết trên dev và giữ capability status trước freeze.

H4 failure guard: N_epoch là actual eligible recovery epochs, đồng thời báo tất cả scheduled attempts/failed injection/no-commit trong ITT. Ngoài q_ASK, q_manual gộp các categories rời nhau ASK, unresolved PENDING và recovery timeout/failure cần can thiệp; resolved PENDING không gộp. Chỉ gọi đạt utility của H4 khi q_ASK≤1/3 và q_manual≤1/3, không dùng timeout/abandon để giảm ASK. N_epoch=0→N/A; thiếu coverage hoặc ít valid n phải nói rõ inconclusive, không tuyên bố đạt toàn catalogue.

H_eval=300s cho live C/A fault epochs, tính từ verified recovery origin; no-fault control tính từ primary commit dispatch. Giữ app/backend namespace tới horizon, không reset trước khi đo xong. Backend copies/late commits sau horizon vẫn được ghi nếu xuất hiện nhưng không tự thành primary endpoint; true absent vẫn cần terminal fate proof, không chỉ hết300s. B2 unattended≥20min và B4 idle có entry/exit windows riêng trước follow-up. Đây là preregistered planning choice dựa trên historical rig maximum window, không con số được paper quy định.

Phân biệt nguồn yêu cầu: draft quy định5frameworks/40tasks/fault families/endpoints/H1–H4 và catalogue; 878/1090, bốn tasks/entry,7B pins,300s horizon,88retrycap và1/2/4load là operational choices của plan. Những lựa chọn này phải được đăng ký/ghi provenance, không trình bày như con số draft đã chốt. Không đổi Algorithm1 hoặc điều kiện của guarantees để vừa hardware.
