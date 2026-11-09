# Nơi chạy và thời gian — h100-plan-v6

## Material Passport

- 2026-11-08, forecasts dưới đây vẫn là kế hoạch. Local Windows10/8logicalCPU/15.8GBRAM/QuadroP2000 4GB đã có SDK/AVD API33r17 với WHPX, app startup và native AndroidWorld screenshot/a11y observation smoke. [Evidence mới](resolve-progress.md). Chưa có model inference/campaign evidence; runtime forecasts không lấy từ boot seconds.
- Servertarget một H100 80GB/250GBRAM; CPU/KVM/NVMe/network/chínhGPUtype chưa được đo.
- Lịchv2/v3 không còn active. Mọiước lượng dưới đây làscenario để budget, chưa phải E18benchmark.

## 1. Placement

| Nơi | Côngviệc |
|---|---|
| LocalCPU | AuditE00/E17, simulation/numericsE01/E03–E09, existingE28–E30, tinyE33/E34 nếu cótools |
| LocalAVD | Actual AndroidOS/app setup, UI/capture/focus/forwarder và native-environment wiring smoke; model7B BF16 không được coi đã fit trên4GBVRAM |
| Linux đúng processdomain | Ledger/processkillE02; không gánLinux/WSL thànhmacOS historicaltiming |
| SingleH100+AVD | A/B/C-native, models7BBF16, realAndroidOS/framework/app/backend/fault/idle/LMK |
| Stages còn phải chuẩn bị | C-guard/calibration và full P40 là required paper roadmap; phone/E2EE/human/full saga chỉ theo claim riêng |

AVD không phải mockUI; AndroidOS thật trên virtualdevice. OEM/pin/physicalpower ngoài core. Phonecá nhân không cần và không dùng làmtestbed.

Không có dependency điện thoại vật lý cho A/B/C của plan hiện tại. Có native observation PASS trên AVD không đồng nghĩa task/calibration/agent đã ready. Local còn gặp SystemUI ANR/empty a11y forest ở các setup attempts; giữ failures và đóng guard, không dismiss để tạo benchmark PASS. Renderer/host/load phải được ghi và freeze trước data collection; đổi CPU/host graphics là cấu hình dev cần kiểm lại, không tự transfer calibration.

Modeldownloads theo stage: Qwen trước A/B, UI-TARS trước A3/A4, GUI-Owl trước A5. A4/A5 native-only development chạy đơnengine; paired C0/C-guard final giữ cùng resident topology/allocation theo models.md. AgentProg workflow/executor/V1 share Qwen và UI locator dùng engine thứ hai. Context32k/history/processor recipe giữ đúng; OOM giảm concurrency trước truncate. Một H100fit/fullrecipequality chưa benchmark.

## 2. Dựtoán attempt và runtime

| Gói | Scheduled | Full-cycle assumption | Serialdevice-hours trước contingency |
|---|---:|---|---:|
| A | 50 episodes | Budget5–10phút/episode với live follow-up300s | 4,2–8,3 |
| B0 | 320 effects | 60–180giây/effect | 5,3–16 |
| Btarget | 108 cases | Case thường1–5phút;8unattended≥20phút | Khoảng4,3–11, idle cóthể thêm |
| C-native | 400 episodes | Budget5–10phút/episode, H_eval300s | 33,3–66,7 |
| Milestone, chưa full paper | 878mixed scheduledunits | Aboveassumptions, P apps mới cần actual costs | Khoảng47–102 |
| C-guard startup OFF | 212extra, required paper stage | 5–10phút/episode assumption | 17,7–35,3extra |
| CERT-1OFF | 11kcalibrationeffects | Scripted60–180s/effect nếu applicable | 183–550, chưa evaluation; LLM-generatedstates cóthểchậm hơn |

1 AVD chạy serial sẽlâu. Với2–4 AVD cóeffectivethroughput phùhợp, coreA/B/C-native dự trù **2–6 ngày chạy saukhicode/rig sẵn**, gồmfixedday-heldout/idle và allowancequeue/reset. Khôngcam kết H100là đủ tấtcảCPU/AVDrequirements; nativefullhistory cóthểchậm hơn v3capinput.

Case tối đa 1instrumentationretry, global88extra attempts; defaultmax966, không vô hạnrerun để đủ validquota. C-guard nếu enable tổngscheduled1090, cùng 88retrycap→max1178, chưa CERT-1. Scientific/modelfailures không rerun. Runtimecontingency30–50%làassumptionchowait/reset/queue/failureoverhead, không measured và không cho phép vượt attemptcap.

A-dev + A-native (30 episodes) có thể là milestone đầu, không đợi600 episodes/fullprotectedbenchmark. Code/rig/adapters/fixtures còn thiếu cóthểtốn vài ngày đến vài tuần riêng; chưa đủ evidence để hứa deadline. CPUhistoricalreruns vài giờ đến 1 ngày làbudgetscenario,chưa đo. Downloadtime chưa đo.

## 3. E18 chốtlịch và hiệu năng

B0dev80 effects chia 20/20/40 cho1/2/4 AVD, config/class/outcome receipts đủ để hiểuphânphối. Đo reset/inject/read/followup/backend/modelqueue/tokens, actualGPUpeak/KV/vision/CPU/RAM/disk và clock. Bổsungactualagent requestcost từ A-dev/devadapters, không nhânscriptedlabelcost cho every agent task.

Forecastcalendar=full-cyclehours/effectiveconcurrency+fixedwindows/setup, cóCI/uncertainty. Khôngchia theoAVDprocesscount hoặcH100TFLOPS, không épGPU100%bằng queuevô hạn. Chọnload trước eval240/Cnative; model/taskfailure không triggerautotuning trên final.

Offlineexact-inputVLMcache tránhrecompute sauanalysis, không increaseindependentn. Không giữ idleV1GPU khi nativeA4/A5 không cần, không load3enginessimultaneous.

## 4. HumanQA và data

Testaccounts/syntheticdata/self-hostedbackends; screenshots/tree/logcat và tokens trong logs phải được kiểm trước export. KhôngAPItrảphíbắtbuộc/không personalphone. HumanQA200actionlabels từ traces(120 dev/80 eval,≥50double-label), không 200deviceepisodes.
LiveASK=escalation/unresolved; oracle/syntheticuseranalysis gắn nhãn riêng, không measuredhumanstudy. Thiếulabel/proof thì giữ unknown/N/A, không lấyAIjudge thaybackendtruth.

## 5. Giới hạn forecast cho paper target

Mốc2–6ngày chỉ budget scenario A/B+C-native878 sau khi rig/code sẵn; chưa full device-study completion. C-guard+sentinels đưa scheduled subtotal1090, max1178 với88extra retries; calibration và development của apps mới chưa có cost đo nên chưa có full-paper calendar đáng tin.

P01–P40 giữ catalogue của draft, khác T40 chỉ ba measured stacks. Đo actual per-framework/per-app step/reset/LLM cost trong development; không lấy B0 scripted latency nhân cho mọi P task. Nếu cần CERT-1,183–550 serial hours chỉ một candidate stratum; không hứa bằng đó đủ mọi app/agent.

E18 giữ80dev effects theo20/20/40 ở1/2/4 AVD; không thử8 trong core. Kiểm thêm dev model request fixtures cho mỗi topology, rồi chọn mức throughput ổn định tốt nhất trong những mức đã đo. Scripted B0 có thể bottleneck khác agent runs; không gọi kết quả B0 là mức tối ưu chung. Không cố GPU100% khi queue/reset/latency làm end-to-end throughput giảm.

V5 đã tính live follow-up300s vào budget A/C, không dùng giả định3phút/episode cho campaign giữ namespace đủ300s. Các raw/runtime assumptions chưa benchmark;2–6ngày vẫn là calendar budget scenario của milestone, không hứa full paper.

V6 giữ nguyên attempt budget. Forecast 1090 episodes vẫn chưa gồm calibration và fixtures của apps mới/Postfix. CERT-1 11k là candidate, không n đã được chứng minh đủ: E09 phải tính actual K_total/lag và fixed n trước collection. Đây có thể là chi phí lớn nhất, cần bảng coverage/cost trước khi đặt lịch server dài; không nhân11k cho mọi app/agent/fault một cách máy móc. H3 còn cần eligible WorkManager app, chưa được bao phủ chỉ bằng10LMK targets.
