# Smoke tests theo stage — h100-plan-v6

## Material Passport

- 2026-11-08; S01–S04 có component/numerical evidence một phần và reconstruction protocol có tests ở [code-fixes](code-fixes.md). GiữS00–S15; chưa đóng actual Android/model/calibration gates bằng fixtures.
- Hard gates làwiring/identity/truth/clock/dispatch đúng. Modelweak/null/ASK-only không tựthànhsetupfail.
- Fixtures/syntheticreferences không freshcalibration; B0dev80,eval240. C-guard/CERT-1OFF.

## Bộ kiểm

| ID | Quy mô/scope | Acceptance |
|---|---|---|
| S00 | Source/hash/72C1/149C2/8sequence,dirty state | Originals giữ; missing/reconstruction khai báo |
| S01 | CP/minimum/asymmetric/K_total/zero-denominator/local-budget references | Numerics đúng; n=0→N/A; local-only alpha_test=.9alpha, alpha_lag0; không max(1,n) pseudo-rate |
| S02 | Guardedledger missingID/replan/DBerror/race/restart,300randomprocesskills | Zero violated durable-issue/dispatch invariants; required A-guard, không block native tracing |
| S03 | Workerfail/staleCSV/schema/hash trong isolatedcopy | RunnerFAIL, không renderstaleoriginals |
| S04 | Small50workflows rồihistorical5×2400/cell | Schema và explaineddiffs; fullsuite không thayraw |
| S05 | Wrong/correctorigin0/5/15s và pre-dispatchnegative | End-to-endabsence≥origin+wait; qualifiedhop1nhánh sớm đúng; unknown→ASK |
| S06 | No-fault/preapplyreject/postcommitdrop/4class receipts | ActualX/ACK/barrier/fate proof, pending≠absent; required A-native |
| S07 | Wrongroom/account/stale/missingdigest/oldmatching;≥5storedfixtures/family | BOT/ASK và undetectederrors giữ calibrationlimits, không oraclereader |
| S08 | K-9Send/Sync/noaction/recompose receipts | Action→DATA/MessageID, đoactionwindow trước redo |
| S09 | A-devtennofault M3Adev; lateradapters trên reuseddevfixtures | Trace/model/input/restartnative đúng, không gate bằng benchmarkscore |
| S10 | Issue/tap/fault/ASK/PENDING/restart/commit-slotmapping | No unsafe dispatch; syntheticfixtures exercise RETRY/COMMITTED code paths, không fake scientificcertificate; required A-guard |
| S11 | B0dev80allocation20/20/40 ở1/2/4 AVD | Load/queue/cost/CPU/KVM/NVMe; bổ sung dev model fixtures ở S15, chọn load trước final, không useeval; không8AVD |
| S12 | ≥10stored/syntheticreset/splitfixtures | Same semantic schedules/reset/namespace, fairlabels; không 10freshcases/methodmọipolicy |
| S13 | .env-before-HF, exactassets/hash/license/offline | Qwen trước A; UI-TARS/GUI assets theo stage, không 3downloadsmandatoryA. Secrets trống trong template |
| S14 | ≥20parser/inputfixtures/role cần thiết | T3Azeroimages, nativehistory, UIprocessor/parser cùng pixelparams, AgentProg bindings, MobileAgentroles |
| S15 | Actual1H100, fullrecipe32k/up-to5 images,1 engine rồi2 nếu required | Recordpeak/KV/vision/queue cho từng topology; AgentProg workflow/executor/V1 share Qwen+UI locator, không3engines; .85single/.45+.45dual; không silenttruncate; reduceconcurrency trước input |

## Gates và scientific stopping

- A-native cần S00/S06/S08/S09/S13/S14 relevant và fault/grader/reset. S04 thuộc CPU reproduction track riêng, không chặn native. Không phải chờguardedcontroller hoặc mọiHFsnapshot.
- A-guard protectedintegration thêm S01/S02/S05/S10. Thiếucertificate→ASK/PENDING reasoncert_unavailable; exercise autonomousbranches ởfunctionalfixtures riêng.
- B0development chọn reader/load/classifier trước 240evaluation. Protectedbenchmark không dùng B0evaluation làmcertificate.
- C-native chỉ sau5frameworkadapters/40fixtures/restartprotocolready. Actual no-commit/failed-injection/unknownoutcomes giữ ITT.
- C-guard startup OFF: paper target cần calibration coverage và pre-registered matched design ở [matrix](study-matrix.md). Unsupported→ASK giữ population; no positive-outcome gate. E20/H4 còn phải thực hiện, không được đóng bằng native-only.
- ≥10actualvalidK-9interruptedcommittedcases mới đóngreviewrequirementA; planned20 không đươngnhiên đủ.
- Case tối đa 1instrumentationretry/global88; scientificfailure không rerun. KeepattemptIDs và nvalid thật; n=0→N/A.
- Review/history/publication scope được báo riêng; không gọi878 attempts hoặczeroobservederrors là 1%certificate/H4proof.

Freeze source/model/SHA/patch/prompt/processor/parser/history/image, app/backend/API/ABI/locale, class/origin/fate/outcome target, taskseed/load/timeouts/registeredrerunrules/endpoints/CI và C-guardeligibility. Không đổi input/labels/faultallocation saufinalscores.

S12 kiểm atomic branch freeze trước C-native final: paired arms cùngresidenttopology/memory fractions vàmodel/input/load. Không dùng oldsingle-engine native làm matchedcontrol cho laterdual-engine guarded arm; late activation cần studyrevision, không thuộc212extras hiện tại.

## Paper-target acceptance

S12 phải assert STUDY_TARGET/TASK_REGISTRY, P01–P40 package/fixture/receipt coverage và matched pair/config hashes. P17–P20 dùng frozen Postfix/IMAP pins, A/B giữ GreenMail. S06 xử lý local-only P33–P40 bằng persistence boundary, không network-fault receipt giả; exact P class targets6/6/4/4 mỗi outcome. S09/S14 giữ five upstream algorithms và backbone-variant label. S11/S15 chỉ xét1/2/4 AVD và actual profile trước final.

Một smoke pass không đóng H4; thiếu calibration khác hypothesis thất bại sau test. [Paper alignment](paper-alignment.md) định nghĩa experiment completion, finite-n limits và outputs.

E21 classifier/reader phải freeze trước B0 evaluation240, không tune bằng heldout80 labels hoặc final scores. E31 ghi rõ eligible WorkManager/F2 force-stop slots cho H3; nếu thiếu thì NOT_TESTED, không dùng LMK receipts thay thế. Hai yêu cầu này không tạo thêm smoke IDs/cohorts.

S07/S10 cũng kiểm nonce ở optimistic Outbox/draft/failed item không thành committed-history evidence, actual subject/body/ON-OFF config khớp grader. B4 E23 ghi idle entry/exit trước wake/relaunch; không dùng GUI thao tác làm thoát Doze rồi gắn nhãn still-idle. Local autosave trước interceptor là NOT_READY protected fixture, không giả ASK an toàn; không thêm quota hoặc ID cho các kiểm này.

Vòng review v6 không tìm thấy thư mục `collab/` trong checkout. S00–S15 ở đây là protocol IDs; chưa xác minh mapping tới notebook00–06 từng được trao đổi. Không coi notebook gate chạy exit0 là actual serving/AVD/end-to-end pass nếu chưa có requests/receipts tương ứng.
