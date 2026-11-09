# Code fixes và testbed reconstruction — 08/11/2026

**Cập nhật v7:** phần này ghi evidence v6. Calibration runtime/read cache/digest/classifier/GUIObserver/local-model binding và các backend/APK mới nằm ở [resolve-progress](resolve-progress.md). V7 đã cài Synapse/Radicale và smoke servers thật, không còn chỉ ASK-only code; actual Android/model/calibration vẫn chưa verified.

Đây là bước implementation sau review v6, được người dùng cho phép sửa code và dựng lại rig đang thiếu. Không viết lại paper, không thay năm framework/model/task catalogue/quota. **Testbed gốc không được phục hồi**; source mới ở [testbed](../testbed/README.md) là reconstruction, còn cần app/AVD/calibration thật.

## Các lỗi đã sửa

| Vấn đề | Thay đổi | Kiểm chứng/phạm vi |
|---|---|---|
| `plan` ghi đè COMMITTED; issue thiếu ID/issue lại; settle tùy ý | Transaction/state guards, idempotent metadata, collision rejection, chỉ retry từ ABSENT; giữ original t0; pending/asked có trong restart candidates | Missing ID, replan, DB rollback, restart, hai connection race, compensation không mở lại retry |
| `n_rate` bisection trên hàm không đơn điệu | Tìm minimum theo từng interval `ceil(p*n)=k` | Independent SciPy:48 small cases +16 actual table entries; ví dụ193 thay221 |
| Delta chỉ theo alpha | `min(alpha,beta)/(10K)` và class multiplier | Asymmetric/counterexample checks; default alpha=beta không chủ ý đổi policy/RNG |
| Denominator0 in thành0% | NaN/N/A, renderer in `--`; thêm n1/n0, q1/q0, simulated-user conditional error | Không lấy workflow ASK làm conditional effect ASK; không gọi synthetic user là human audit |
| Shell background jobs có thể che failure/stale output | `artifact/run_all.py`: fresh isolated workspace, per-child exit/timeout, CSV structure/count/hash, bounded workers, manifest FAILED/PASS | Failed worker/missing/malformed/stale output tests; full25jobs có REAL4 |
| Renderer xóa output trước khi validate | Generate trong staging rồi publish, rollback nếu rename lỗi | Missing input/late publish failure giữ generated cũ; giữ notes/assets ngoài `.tex` |
| REAL4 không được render | `tab_real4.tex` chứa toàn16tags/33rows | Có generated fragment trong isolated output; không tự thêm table vào manuscript |
| Build nuốt LaTeX/BibTeX error | Shell fail-fast, check PDF/log/undefined citations/references | Shell-control-flow tests với fake compiler có nhãn fixture; chưa fresh full TeX compile |
| Host crash benchmark có thể PASS khi không có tap/violation | No-tap/violation fail, POSIX-only, Linux fullfsync=N/A; kill window bắt đầu sau first tap và kiểm actual SIGKILL exit | 300-kill run và source hashes; process kill không phải physical power loss; host latency không phải phone |
| Nonce MC chậm vì luôn full Levenshtein | Exact threshold0/1 predicate, fallback DP cho threshold lớn | Exhaustive short strings +seeded MC +full9rows; không đổi RNG/corpus/noise/sample size |
| `params.csv` provenance diễn giải quá mức | Giữ22 numeric values; sửa mô tả 101 recorded endpoints và K-9 explicit Send8/20, không20/20 | Không tạo thêm real labels/late-duplicate window hoặc unattended evidence |

## Kết quả kiểm thử và bằng chứng

- Artifact regression:32 tests trên Windows và Linux; mỗi host skip1 do POSIX/SciPy availability. Independent reference chạy ở Windows; actual POSIX subprocess failure chạy ở Linux. Latest test logs: [final-validation](../tmp/code-fixes-v6/final-validation/).
- Reconstruction:19 tests qua trên cả Windows/Linux, có HTTP/SMTP loopback, barrier trước ACK, same-ID terminal reject, sticky retry, wrong account/room/foreground, failed/draft status, missing bottom receipt, ADB/PID failure, ledger-before-tap/restart và grader scan errors. Backend/screens của unit tests là **synthetic fixtures**.
- Full artifact: [RUN.json](../tmp/code-fixes-v6/full-artifact/RUN.json) PASS25jobs, historical5×2400/cell, đủ16REAL4tags, sample-size/host-ledger/renderer. Đây là snapshot code lúc bắt đầu run; các sửa provenance/caption/nonce optimization/benchmark readiness sau đó được kiểm riêng, không sửa manifest để giả cùng revision.
- Latest host benchmark:300 active-writer SIGKILL trials,3264taps,0write-ahead violations; [CSV](../tmp/code-fixes-v6/latest-components/artifact/results/ledger_bench.csv). Random window bắt đầu sau first tap, source hashes ở `latest-components/SOURCE.json`. Linux fullfsync không supported→N/A. Đây là process write ordering trên WSL, không power loss.
- Nonce optimized full run: `nonce.csv` khớp byte-for-byte original-DP run trên cùng corpus/seeds; so archived CSV chỉ2CP upper-bound strings lệch khoảng1e-15. `nonce_before.csv` byte-identical. Không báo speedup có kiểm soát từ hai host/load khác nhau.
- Real GreenMail2.1.2 đã tải vào `runtime/assets`, SHA256 khớp historical JAR; [integration result](../tmp/code-fixes-v6/testbed/greenmail-integration/RESULT.json) PASS4cases: nofault1copy, accepted/lostACK1copy, new-ID resend2copies, preapply reject+late sameID0copy. **Không Android, không app fault, không LLM**, không tính vào B0/A-native/calibration.
- [Preflight Windows](../tmp/code-fixes-v6/testbed/preflight-windows-final.json), [Linux](../tmp/code-fixes-v6/testbed/preflight-linux-final.json): GreenMail hash verified, chưa ADB/APK/AVD, WSL không `/dev/kvm`; Synapse/Radicale chưa cài. Đã xác nhận public package endpoints tồn tại, nhưng chưa có install/config/Android receipts. Không suy Windows hypervisor unavailable chỉ từ WSL thiếu KVM.

## Conflict mới phát hiện khi reproduction

**Archived aggregates chưa khớp hoàn toàn source đi kèm.** Main `ghost-src` lưu ASK47.35%, source trước sửa chạy trên cả Windows và Linux đều cho47.00833%, giống source sửa ở full run. Autonomous conditional duplicate lưu0%, run mới0.0120948%. Đây là pre-existing source/output discrepancy, chưa xác định root cause từ archive; không quy thành lỗi do các guards/delta/counts mới và cũng chưa có bằng chứng fabrication.

Ngoài `ghost-src` ở main/stress/sweep/ncal/share/class, có một `ghost` row tại ncal200 khác một workflow: source trước sửa và mới đều ASK39.69167%, archive39.7%, xác nhận discrepancy cũng có trước sửa. Full diff ở [ARCHIVE_COMPARISON.json](../tmp/code-fixes-v6/ARCHIVE_COMPARISON.json); CI floating differences tầm1e-10 cũng được giữ nguyên trong diff. **Không gộp tất cả vào “rounding”**. Measured-real/REAL4 point estimates khớp; các sai khác CI nhỏ và các cột conditional mới có scope riêng.

Controlled evidence: [baseline Windows](../tmp/code-fixes-v6/baseline-full-nt.json), [baseline Linux](../tmp/code-fixes-v6/baseline-full-posix.json), [ncal200 baseline](../tmp/code-fixes-v6/baseline-ncal200.json), [old/new80-workflow comparison](../tmp/code-fixes-v6/numerics/LEGACY_COMPARISON.json), [16 sizing references](../tmp/code-fixes-v6/numerics/REFERENCE.json).

Quyết định mới v9 theo người dùng: mọi số draft là minh họa; dùng kết quả run mới có source hashes làm chuẩn. **Không chỉnh paper, paper để sau**; lượt publish generatedTeX/PDF đã được khôi phục, CSV mới giữ riêng. Không cần truy nguyên hoặc khớp các old aggregates để tiếp tục. Không claim byte-identical archive reproduction và không đổi RNG để ép khớp. Điều tra discrepancy ở trên là lịch sử, không phải blocker hiện tại.

## Testbed giữ tinh thần paper ở đâu

- Proxy protocol thật; acceptance/ACK/fault là các receipts riêng, không ngụy tạo backend X từ GUI.
- Reject trước apply giữ original ID blocked; pending/finite-horizon zero không được đổi thành ABSENT.
- ADB driver dùng test AVD explicit serial, capture bracketing và profile negative controls; profile chưa có màn hình thật thì BOT.
- Một host controller ngoài agent; durable issue trước tap; nonce Crockford6symbols/private mặc định/visible opt-in/reuse. Digest hiện giữ XML identity, chưa semantic history digest.
- Driver compose/history dùng profile từ dev screens; visibility polling giữ BOT/censoring. Không dùng repeated polls làm independent votes cho certificate.
- Runtime thiếu certificate → ASK; chưa đưa synthetic q hoặc hidden backend truth vào auto-retry. Vì vậy **chưa đóng A-guard/H4**.

## Các việc chưa được đóng

1. Actual API33/ABI/APK/backend accounts, app profiles và clean snapshots/reset; network/clock/fate validator; đủ valid nofault/fault cases mỗi stack.
2. Official M3A adapter/native continuation trước; T3A/AgentProg/UI-TARS/Mobile-Agent-v3 đúng pinned model/role/history/input recipe ở stage C. Không thay bằng driver scripted.
3. Classifier/commit-slot mapping, semantic digest, calibrated cascade/product/source/joint adapter, qualified hop1/Monitor và foreground/account checks trên app thật.
4. Calibration acquisition theo coverage/actual K_total, labels/lag/censoring; không dùng B0eval/bootstrap như real certificate. H4 vẫn phải đo cả risk và ASK≤1/3, unsupported tasks vẫn trong denominator.
5. Verified LMK/Doze/AppStandby/DataSaver, WorkManager/G2 eligibility cho H3, Postfix/IMAP final và P40 assets/Pro Expense identity.
6. Source/output discrepancy nói trên; missing historical attempts/screens; actual H100 model fit/throughput/calibration cost; fresh TeX compile riêng khi có toolchain phù hợp.

Không cần thêm campaign/framework để xử lý các mục này. Giữ milestones878/1090, calibration là khoản chưa được tính đủ, review-only history ở các phần v6 cũ được hiểu theo thời điểm trước implementation này.
