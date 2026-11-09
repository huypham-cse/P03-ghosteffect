# Local và server — h100-plan-v6

## Material Passport

- Revision2026-11-08. Runtime chính một H100 80GB/250GBRAM theo [setup-server](setup-server.md); local đã có actual AVD/WHPX/API33r17 và native observation smoke, [receipts](resolve-progress.md). Chưa inference/agent quality/calibration thật.
- Local chạy audit, numerical/simulation, unit/fixture/parser tests; POSIX crash tests dùng Linux đúng failure domain.
- Local cũng chạy SDK/APK/app UI và native AndroidWorld wiring smoke trên AVD. Không cần điện thoại vật lý cho core; không suy 7B BF16 chạy vừa4GB từ việc AVD chạy được.
- A/B/C-native trên Android13/API33 AVD ở server; model7B BF16 theo [models](models.md), không 72B hoặc multi-GPU.
- Xem [execution-placement](execution-placement.md) và [study-matrix](study-matrix.md) cho quota/time/scope; physical phone không dependency core.

Native pilot không đợi fullcontroller hoặc cả ba model; A1 vẫn cần Qwen đúng pin/recipe và serving đã kiểm trước model-driven episode. Scripted-response wiring là test fixture, không native baseline result. Model/image/history theo upstream recipe, context32k; C-guard/CERT-1 OFF cho đến scientificgate.

V5 paper target dùng P01–P40 và cần protected/H4 cùng full app coverage.878 là milestone;1090 gồm protected/sentinels, chưa calibration/app-development. False startup flags không đồng nghĩa optional scientific requirement. [Paper alignment](paper-alignment.md) ghi các gates và điểm cần tác giả xác minh.

V6 giữ quy mô đó; core load chỉ1/2/4, engine theo checkpoint và AgentProg/V1 share Qwen. A/B mail giữ GreenMail, P-final dùng Postfix/IMAP như draft. KVM, app/rig pins và calibration n/cost còn phải xác minh; không suy runtime readiness từ hardware arithmetic hoặc việc có file plan.
