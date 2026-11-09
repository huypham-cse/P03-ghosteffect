# Ma trận thực thi GhostEffect — h100-plan-v6

## Material Passport

- 2026-11-08; plan only, một H100 80GB/250GBRAM.
- V6 giữ scope/quota v5 và sửa backend final, engine routing, calibration sizing và H3 readiness. Milestone878 giữ để chạy sớm; paper target dùng P01–P40 và cần E20/H4. T01–T40 là prototype/review-core, không full app coverage.
- Các tasks/adapters/collectors mới là đặc tả cần implement, chưa có results.

## 1. Attempt ledger và shared corpus

| Gói | Lịch scheduled attempts | n |
|---|---|---:|
| A-dev | M3A nofault development | 10 |
| A-native | Native K-9 committed/lost-ACK targets,10no-Sent/10Sent | 20 |
| A-guard | Protected integration trên 20 semantic schedules tương ứng A-native, reset độc lập | 20 |
| B0 | 4 configs×2terminal outcomes×40 effects | 320 |
| B1 | Element3response-loss forms×5causal cases | 15 |
| B2 | 15K-9 action-audit+8unattended≥20min | 23 |
| B3 | Một config,10 LMK target attempts; actual verified n báo riêng | 10 |
| B4 | Element3idle states×2 outcomes×10 | 60 |
| C0 | 5 agents×40 tasks native interrupted; paper=P, review-core=T | 200 |
| C2 | 5 agents×40 tasks native nofault | 200 |
| Milestone chưa protected | A50+B428+C400, chưa calibration/full device-study completion | **878** |
| Protected final, startup OFF | 5×40 protected interrupted +12 M3A vetted-rule sentinels; required paper roadmap | **212** |

Một case tối đa 1 instrumentation retry, cảcampaign tối đa 88 extra attempts, milestone actual ceiling966; với212protected/sentinels, subtotal1090/max1178 trước calibration. Các attempts trước failure vẫn giữ. Model/task/scientific failures không rerun để lấy valid cohort. Nếu không đạt valid n cần thiết, báo incomplete; không gọi878 là 878 independent Bernoulli hoặcquota valid.

B0 gồm 4 configs: Element/Synapse, K-9/GreenMail no-Sent, K-9/GreenMail Sent, Etar+DAVx5/Radicale. Mỗi(config,outcome)40 effect IDs, indices0..9development,10..39evaluation. Tổng development80/evaluation240, **không fresh calibration split**. Outcome target không phải ground truth.

Trong mỗi 40-record group, class=F[1+(index mod4)] →10 attempts/class; dev3/3/2/2, eval7/7/8/8. Mỗiclass/outcome cósmall n, chỉ characterization, không 1%certificate. Dev load assignment có thể benchmark20 effects/load ở1/2/4 AVD trong 80 dev(20/20/40); actual config/class/load receipts phải báo. Final240 effects thu dưới một selected load, khác ngày dev khi khả thi, không tune trên final.

B0 phục vụ E10/E11/E14/E15/E18/E26, không cộngE-ID thànhcohort mới. E15 chọn 100evaleffects/outcome(200/240) bằng IDs/seed định trước, chưa biếtreader scores. E21 là 200actionlabels từ development/evaltraces,120/80,≥50double-label; không 200deviceepisodes mới.

Pre-apply rejection cần terminal fate proof cho original request; temporarily offline/pending không làabsent. Original retry cùng ID vẫn có thểcommit thì chưa terminal; reject rule phải scope đúng original và late retries. Đối với intended X0 không realizable củaapp/class, giữ N/A/unknown, không fake label hoặc đổi app sau score. Never-visible/latepending challenges từ dev; không equate X_backend với X_paper ngoài domain.

A/B/C cónamespace/effect IDs riêng; labels/screen cùng effect không thành nhiều independent units. Eval không tune thresholds. C1 historical làcampaign1; CERT-1 làextension riêng OFF.

## 2. Recovery arms giữ ở đúng tầng evidence

Historical catalog giữ nguyên current source:
- redo, ckpt, atomix, atomix-durable, verify, key, key-ask, always-ask, nonce-ask, maj3-ask, ghost-v1, rules, rules-lenient, g2-only.
- ghost(product), ghost-src(source), ghost-joint(joint).
- ghost-nononce, ghost-nohop1, ghost-nodigest, ghost-nocal, ghost-uniform, ghost-noask, ghost-visible.
- app-state, rules-w{5,10,30,60}-{all,novlm,two}, rules-vetted, rules-vetted-small theo từng part.

| Arm | Policy | Live scope v6 |
|---|---|---|
| M0 | Native/unprotected | A-native và C0/C2 |
| M1 | Always-ask | Policy reference, ask100% theo định nghĩa; simulation/replay. Không12livecases chỉ để đo constant |
| M2 | G2-only, không autonomous retry | Simulation/replay/fixture; không all-agent live arm |
| M3 | Strict rules10s | Simulation/replay/fixture |
| M4 | Strict rules30s | Simulation/replay/fixture |
| M5 | Equal-data vetted rule | Simulation/replay chính;12extra sentinel cases chỉ khi C-guard mở |
| M6 | Product | Historical/corrected simulation; live extension cần A2 riêng, không mặc định |
| M7 | Source | Historical/corrected simulation; independence còn lại phải cócơ sở |
| M8 | Joint | A-guard integration/fail-closed;200 protected cases C-guard chỉ sau scientific gate |

C-guard sentinels paper_draft: P01/P02/P05/P06/P09/P10/P13/P14/P17/P18/P29/P30; review_core: T01/T02/T03/T04/T17/T18/T19/T23/T24/T29/T30/T31. M0 đã ởC0, M8 ởC-guard; chỉ thêm M5=12, không 7policies×12. Method order random theo task blocks, initialapp/backend/ledger resets độc lập.

Rules cùng raw dev labels/measurement opportunity; shortlist freeze trên dev, không use eval để chọn rule. Source hiện dùng shared worlds nhưng prng riêng theo policy index. Đây là paired-world design, không identical noisy observations; không vì thế tự kết luận McNemar invalid. Giữ generator/law và kê đúng coupling. Equal-data review yêu cầu cùng calibration information/tuning opportunity, không yêu cầu viết observation-bank framework mới. Common-noise sensitivity chỉ optional trong fork nhỏ, có nhãn riêng.

Offline replay chỉ khi observation schedule/state hợp lệ; không reuse screenshot sau một method dispatch làmstate method khác. M1 analytical không làmeasured finaldup/loss. Simulator ports không thành upstream live systems.

## 3. T01–T40: prototype trên các app đã đo

| IDs | Config | Từng task: một effect chính |
|---|---|---|
| T01–T04 | Element | T01 tin mới room chính; T02 tin mới room phụ; T03 cùng text với tin cũ; T04 cùng text với tin của tài khoản khác |
| T05–T08 | Element | T05 text nhiều dòng; T06 Unicode tiếng Việt; T07 text dài có wrap; T08 text có URL synthetic |
| T09–T12 | Element | T09 gửi từ room list; T10 gửi sau search room; T11 gửi sau navigation khỏi room cũ; T12 gửi khi có tin người khác xen kẽ |
| T13–T16 | Element | T13 gửi sau scroll về bottom; T14 gửi khi có matching old item; T15 gửi sau cold launch; T16 gửi sau account/room re-verification |
| T17–T22 | K-9 no-Sent | T17 mail mới; T18 trùng subject thư cũ; T19 trùng subject/body cũ; T20 Unicode/multiline; T21 gửi từ draft thử nghiệm; T22 gửi sau cold launch |
| T23–T28 | K-9 Sent | T23–T28 cùng sáu semantics T17–T22, Sent mapping bật; ID/initial state riêng |
| T29–T32 | Etar/DAVx5 | T29 event mới; T30 trùng title cũ; T31 cùng title khác ngày; T32 Unicode description |
| T33–T36 | Etar/DAVx5 | T33 event có location synthetic; T34 event từ calendar view khác; T35 event all-day; T36 event giờ bắt đầu/kết thúc cố định |
| T37–T40 | Etar/DAVx5 | T37 event sau cold launch; T38 event sau sync navigation; T39 event cùng title/khác description; T40 event sau calendar/account re-verification |

Đây là 40 task instances/variants trên ba stacks (4 configs), không 40 app families hay40 independent device populations. Cần implement initialize/success/tear_down, exact content, account/room/calendar, effect ID, grader và reset. Các variants nhằm coverage lỗi visibility/attribution, không dùng task count để thổi độ đa dạng. Task multi-effect/saga giữ simulation và extension E28.

T01–T40 chưa phủ Tasks.org/Joplin/SMS/MockBank/Pro Expense/Markor. Với paper_draft, phải hoàn thiện catalogue bằng P01–P40 ở mục8 trước final; bốn tasks/entry là allocation proposal, không quota được draft quy định. Pro Expense đã định danh `com.arduia.expense`, APK candidate11 từ pinned AndroidWorld; không âm thầm thay app khi binary/UI fixtures chưa kiểm. A/B và T K-9 characterization giữ GreenMail; P17–P20 dùng Postfix như app table, với local IMAP cho Sent/no-Sent. Hai backend là hai domains, không tự chuyển calibration.


## 4. T-native assignment:20committed/20absent targets; P exceptions ở mục8

Trong40 tasks, pair p=floor((taskID-1)/2), class F[1+(p mod4)]. TaskID lẻ targetX1/I3(aftercommit,beforeACK); taskID chẵn targetX0/I2(post-localissue,pre-apply terminal rejection). Hai members/pair cùng faultclass. Toàn40:20 targets/outcome và 5 tasks/class/outcome. T01–T16 Element8pairs; T17–T22 K-9 no-Sent3pairs; T23–T28 Sent3pairs; T29–T40 CalDAV6pairs. Mộtconfig cóthể không phủ đủ 4 classes; report coverage thay vì bị a full factorial.

F1=agent death, F2=background appdeath, F3=20s netblackout, F4=appdeath+net. Force-stop/kill9/clean/sticky/timeout subtypes riêng córeceipt. I1pre-dispatch ởnegative controls/S02/S05, không chiếmslot mainC; historical phaseweights .20/.25/.35/.20 không đổi.

Đây là balanced characterization, không factorial causal design; nhiệm vụ và fault/window vẫn khác nhau. Dùng matchedpair task blocking khi phân tích; không kết luận thiết kế loại mọiconfound. ActualX từ backend, không assignedX; agent không tới commit giữ ITT failure, loss-side denominator chỉ actual trueabsent.

Seed6101choC; A/B6102/6103 vớicontent/account namespaces riêng. Task order shuffled trước theoagent block, native/protected same semantic schedules khi mởguard, không giả identical stochastic UI. Mộtseed không tựthành seedrobustness. Sharedtask40 variants không 40independentdevices; CI theo effect/task clusters phù hợp.

Native restart dùng cơ chếframework có sẵn; nếu native không persist history thìkhởiđộng lại cùng user task+freshGUI, không hinttruth/resend haychèn checkpointpolicy mới. Logmemory retained/lost. Protected dùng cùng agentbinding rồiresolve ledger trước khiagent tiếp tục.

## 5. Calibration và gate C-guard

B0 **không xuất certificate thực**. CP/loader/stopping smoke dùng synthetic reference fixtures có nhãn riêng, không thu320calibrationeffects n=10/cell. B0eval240 effects cho rates/CI/BOT/censoring/cost; zerosmall-n không proof1%.

A-guard kiểm fail-closed dispatch/restart; khi certificate unavailable→ASK/PENDING vớireasoncert_unavailable. Báo là integration smoke, không autonomy benchmark. Không biến M8 thành heuristic retry để tạo usefulscore.

**C-guard startup OFF**, phải được chuẩn bị trong roadmap paper và quyết định trước final. Readiness:
1. Frozen model/reader/app/class/origin/load và certificate có provenance/proof hợp lệ cho regions được phép autonomous action; unsupported regions giữ ASK. Không borrow fitted-law/bootstrap/B0eval.
2. Certificate coverage/unsupported regions và calibration acquisition đã freeze; autonomy chỉ trong valid domain. Không chọn population theo việc có autonomous action hay score tốt.
3. Scope/evaluation population/outcome n, comparison endpoints/CI, coverage unsupported và runtimes chốt trước; khienable, chạy toàn200scheduledprotectedtaskdistribution, không chỉ selectedeasy tasks.
4. E02/S05/S10/oracle isolation pass; E09 và coverage table xác nhận action permission. Nếu thiếu calibration thì protected/H4 chưa ready; roadmap phải thu dữ liệu cần thiết, không báo native characterization là full device-study completion. Valid data nhưng ASK-heavy là kết quả âm, không loại stratum.

CERT-1 OFF là một recipe tùy chọn: một stratum chọn trước, 500 pilot+5000 holdout/outcome=11000 calibration effects. Nó không tắt yêu cầu chuẩn bị calibration cho protected final và không bảo đảm đủ mẫu. Committed holdout có thể reuse lag khi inferential design cho phép; không mặc định additional20k. E09 phải tính n theo actual K_total/budgets/censoring/stopping trước collection; thiếu thì chọn fixed acquisition budget mới trước khi chạy, không thu nối đến khi pass. Finalevaluation riêng, không nằm trong 878/212 counts.

Khôngcertificate thì không claim empiricalH4 hoặcfullend-to-end certification hoànthành. Giữhistorical joint/source/product results đúng scope; verdict error/guarantee/taskcompetence không gộpthành một accuracy.

## 6. Endpoints và nghiệm thu

H1 native retry/resend/duplicate trên actualcommittedinterrupted; H2whole-effect verifier error/correlation và CI/BOT; H3 app/fault-specific recovery cónull; H4 chỉ nếu validgate+population, không chọn Element sau khiK-9ASK nhiều.

Báo attempts/reachedcommit/validfault/actualX/observedcopies/false-success/completion/unresolved, P_v/L_v/q1/q0/ask/time/tokens/cost. Denominator0→N/A, không rate0. Conditional native/protected analyses đứngbênITT; repeatedscreens không independentn.

Live ASK kết thúcepochvớiescalation/unresolved. Observation horizon củarawcopies giữ fixed; server vẫn cóthểlatecommit. Oracle/syntheticuser downstream outcomes phân tích riêng, không measuredlive recovery. Actualhuman workflow cần protocolE30OFF.

TổngA50 gồm 30 native/dev và 20protectedintegration, không 50 native. Review gate là≥10valid K-9fault cases từ 20scheduledA-native, không chỉ run ID. C-native400 giữ 5 agents/40 tasks theo registry đã freeze; T chưa full catalogue. P-paper cần coverage mục8 và protected final; phone là claim riêng.

BalancedX1/X0benchmark không ước lượngnaturaloutcome priorpi. BáoconditionalP_v/L_v/dup/loss và overallbenchmarkrates vớiweights đã đăngký; không extrapolate deploymentprevalence từ injected50/50 targets. Nếu muốnprior khác,chỉ sensitivityweighting có nhãn riêng, không measurednaturalprevalence.

## 7. Atomic freeze cho nhánh protected

C-guard eligibility phải quyết định một lần trước C-native final. Nếu đủ và bật từ đầu, native/protected cùng model/SHA/decode/history, AVD/backend/load và resident-engine topology; chia method order trong matched task blocks. UI-TARS/GUI-Owl native ở nhánh paired cũng dùng cùng memory fractions/services như protected, kể cả V1 idle. Khi đó200nativeC0 được reuse làm control và212extras là budget đúng.

Nếu C-native đã chạy ở default single-engine hoặc config khác, không bật muộn rồi coi oldnative là matchedcontrol. C-guard tiếp tục deferred cho studyversion đó; muốn nghiên cứu tiếp phải tạo studyversion mới với native controls và budget mới. Không dùng212extras để hứa cost của một late follow-up. Startup model-memory topology đổi giữa stages cần stop/restart engine và verify GPU memory released, không giả chỉ đổi env là engine đang chạy đã đổi.

Equal-data gate cho M5: baseline được cùng development **và calibration labels/lag information** mà joint sử dụng, kể cả CERT-1 nếu mở. Chọn rule từ family định trước bằng thông tin đó, freeze trước independent final evaluation; không chỉ cấp80dev cho M5 khi joint được11klabels. Calibration holdout không phải final evaluation; M5 dùng nó không mang nghĩa baseline được formal guarantee. B0evaluation vẫn cấm tuning. Historical full-data vetted rows giữ cùng sample information budget/provenance.

S12/runner phải kiểm pair_id/task_seed và model/input/load/topology config hashes của matched arms; mismatch→khôngpairedanalysis, cần study revision. Native discovery không phải control tự động cho một config mới.

## 8. P01–P40: registry chính cho paper_draft

Nguồn scope là planned device study §7.8 và bảng apps của draft. Tên/tasks dưới đây là proposals cần fixture validation, không kết quả đã đo. Mỗi task một effect. Không đổi registry T thành P sau final scores; paper target mặc định P, review_core phải chọn rõ trước final.

| IDs | App/config entry | Bốn task proposals cần init/grader/reset |
|---|---|---|
| P01–P04 | Element/Synapse | P01 tin mới room chính; P02 tin multiline; P03 trùng text tin cũ; P04 Unicode ở room phụ |
| P05–P08 | Etar+DAVx5/Radicale | P05 event mới; P06 event có description; P07 trùng title khác ngày; P08 Unicode/location synthetic |
| P09–P12 | Tasks.org+DAVx5/Radicale | P09 task mới; P10 task có note; P11 trùng title cũ; P12 Unicode note |
| P13–P16 | Joplin/WebDAV | P13 note mới; P14 note nhiều dòng; P15 trùng title cũ; P16 Unicode body |
| P17–P20 | K-9/Postfix + local IMAP, pins còn phải xác minh | P17 mail mới no-Sent; P18 Unicode mail no-Sent; P19 mail mới Sent; P20 Unicode mail Sent. A/B giữ GreenMail, không thay historical |
| P21–P24 | Simple SMS/isolated AVD endpoints | P21 tin mới; P22 multiline; P23 trùng text cũ; P24 Unicode. Console/receiver receipts và default-SMS role phải verify, không gửi ra số thật |
| P25–P28 | MockBank-A, dedup by request ID | P25 transfer synthetic mới; P26 cùng amount khác ID; P27 cùng private note; P28 Unicode note. Không thanh toán thật |
| P29–P32 | MockBank-B, no server dedup | P29–P32 cùng semantics P25–P28, backend ledger/config riêng |
| P33–P36 | Pro Expense/local | P33 expense mới; P34 note; P35 cùng title/amount; P36 Unicode note. Package `com.arduia.expense`, APKcode11/1.0.0-beta05 đã hash/signature/install/launch verify; actual task UI/reset/grader còn phải kiểm |
| P37–P40 | Markor/local | P37 file note mới; P38 multiline; P39 cùng tên/content scenario; P40 Unicode. Commit/save semantics phải verify từ actual UI |

Source/package/version/ABI/signature, nonce field/opt-in, hop-1/digest/history capability, G2 scope/horizon và grader/reset phải có per-entry readiness record. Không giả mọi UI hỗ trợ field đã đề xuất; fixture không hợp lệ thì sửa proposal trên dev trước freeze, giữ revision log.

P17–P20 nonce candidate là mail body, với explicit visible opt-in; subject thuộc historical/A/B replication. Không opt-in→nonce OFF, không tự đổi content. Local P33–P40 dùng local budget allocation như design; autosave/text-entry có thể là effectful action. Không có identifiable interception/persistence boundary thì protected fixture NOT_READY, không gọi đó là một ASK-safe case khi đã có write trước interceptor. Resolve bằng actual UI/fixture trên dev, không tạo commit tap giả hoặc semantic-intent engine.

P dùng outcome target lẻ X1/I3, chẵn X0/I2 như T. Với P01–P32, class dùng pair formula mục4. Local-only P33–P40 chỉ agent/app kill: P33/P34/P37/P38=F1, P35/P36/P39/P40=F2; inject quanh local-persistence boundary, không dựng network fault để lấp ô. P có6/6/4/4 targets theo F1/F2/F3/F4 ở mỗi outcome, khác T5/class/outcome. Đây là coverage có applicability, không factorial causal study. Actual fate vẫn quyết định truth.

C0/C2/C-guard lần lượt200/200/200 cho P; tổng có A/B và12M5=1090scheduled, max1178 với cap88 retries, chưa calibration/extra app-development. P40 và T40 không tự cộng thành80tasks.

## 9. H4, CI và missing-data analysis

Theo [paper alignment](paper-alignment.md), H4 giữ risk contract và ASK≤1/3 trên frozen paper distribution. Unsupported→ASK, không bỏ khỏi denominator. Báo q_ASK và unresolved/timeouts/taskfail riêng; taskfail không thành successful autonomous recovery.12M5cases chỉ sentinel/wiring, không chứng minh superiority trên toàn catalogue.

B0/E15: whole-effect unit; error joint-counts theo outcome/view pair, BOT/missing riêng; variance0→correlation N/A. Paired comparison block theo task/semantic schedule, cùng pair/config hashes. H4 point metric là fixed benchmark; task-block bootstrap sensitivity resample40 task IDs, giữ cả five frameworks trong mỗi block. Không suy từ bootstrap ra population ngoài40 tasks khi chưa có sampling assumption.

Calibrated guarantee và evaluation CI là hai đầu ra riêng. Zero errors trên100 actual committed cases có one-sided95% upper≈2.95% dưới iid assumption, không≤1%; không auto-collect-until-pass. Xem E09 trước khi đăng ký mục tiêu empirical≤1%.

Matching model/input/history nghĩa là cùng recipe/policy và initial semantic task; không ép ảnh/history trung gian giống nhau sau khi methods chọn actions khác nhau. Nonce opt-in/content changes là component của treatment, phải log E26; grader/agent task text không được lộ hidden truth.
Local autosave hoặc UI không có identifiable commit boundary phải được đánh unsupported/thiết kế lại task trên dev trước freeze, không tạo commit tap giả để đáp ứng classifier hoặc X labels.

P có10app/variant entries; K-9 entry gồm2configs Sent/no-Sent, nên11config identities thực tế. Không dùng10entries làm số calibration domains. App/backend versions, source capability và applicable fault/origin/load còn chia domain tiếp.

Paper target với REQUIRE_H4_EVALUATION=true không được chạy C-native final ở native-only config rồi tự defer guarded arm để đóng study. Chốt coverage/calibration/readiness và matched topology trước cả hai final arms; thiếu thì giữ C-final chưa ready, tiếp tục A/B/development. review_core chỉ là explicit separate study, không auto fallback.

H4 utility guard: q_manual=(ASK + unresolved PENDING + recovery timeout/failure requiring intervention)/N_epoch với mutually exclusive categories. Đòi q_ASK và q_manual≤1/3 để không tạo fake ASK reduction; N_epoch0→N/A, ITT và failed-injection/no-commit counts luôn đi cùng. H_eval300s từ recovery origin, nofault từ primary commit dispatch; không reset app/backend namespace trước horizon. B0 giữ characterization reader protocol riêng, không tự biến thành calibration.

## 10. Calibration và H3: phần cần chốt trước final

Coverage table tối thiểu theo actual app/backend/reader/model/fault/origin/load: protocol/hash, available views, existing source, pilot/holdout/lag unique IDs và overlap, K_total/budget, fixed n/cost, status `supported` hoặc `ASK`. Chỉ tạo các domain thực sự cần cho frozen decisions; không tự nhân app×agent×fault×load thành một full factorial collection. Shared Qwen engine không cho phép tự pool calibration giữa domains.

Ví dụ sizing chỉ để lập kế hoạch: alpha=beta=.01, delta=.01/(10 K_total), lag target .002, zero exceedances và fixed candidate. K_total=20 cần n=4947; K_total=55 cần n=5453. 5000 mẫu ở ví dụ thứ hai cho upper bound≈.002181, chưa đạt .002. Actual K_total phải E09 xác minh; không coi 55 là K đã chốt cho project. Pilot/candidate selection và right-censoring cần accounting riêng.

Dùng dev capability/measurement cost để chốt thứ tự thu dữ liệu trước holdout. Forecast tỷ lệ scheduled recovery slots chắc chắn phải ASK theo frozen coverage; nếu đã trên1/3, H4 utility trong scenario đó không khả thi dù các supported slots đều autonomous. Đây là feasibility forecast, không lý do bỏ task hay thay population. Sau run, tính actual lower bound U/N_epoch từ unsupported eligible epochs và báo ITT; forecast không thay actual denominator.

E31 phải ghi app nào thực sự có WorkManager-based outbox và G2 contract. Nếu có eligible app ở F2 slots, freeze subtype force-stop và dùng C0/C2 cùng request/outbox/relaunch/backend receipts để kiểm H3. Không suy WorkManager từ tên app, không coi LMK là force-stop, không dùng app death đã ACK làm ghost trial. Nếu chưa định danh được eligible app/slot hoặc valid n=0, H3 là `NOT_TESTED`; không thêm app ngoài paper hoặc thêm campaign lớn chỉ để lấp checkbox. B1/B3 vẫn giữ đúng mục tiêu causal response-loss/LMK của chúng.

Quy mô 1090 gồm 600 C episodes (5 frameworks×40 tasks×3 arms) và các A/B/sentinel khác. Mỗi framework chỉ có tối đa20 committed interrupted targets ở mỗi arm, actual n có thể ít hơn. Hợp lý cho benchmark và failure mechanisms, không đủ để diễn giải risk≤1% ở từng framework/app bằng observed zero errors. Giữ tổng, báo hạn chế; chỉ tăng quota nếu mục tiêu inferential cụ thể yêu cầu và budget được chốt trước collection.
