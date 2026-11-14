# Nhật ký phần B (Trung Nguyên)

Theo luật 1.8 trong `team/RULES.md`: chỉ thêm mục mới, không sửa hay xóa mục cũ. Receipt nằm trong `testbed/runs/` và `runtime/` trên máy chạy, không commit.

## 09/11/2026

**Host local:** Windows 11 (10.0.26200), 8 luồng CPU, 31,5 GB RAM, Intel Arc 140V, WHPX 10.0.26200 dùng được, Java Temurin 21.0.12, Python 3.11.8 qua uv cho agent.

**Đã làm:**
- B-05: thử SSH vào server H100 80GB (103.73.232.225, port 52194) lúc 22:30: hết thời gian chờ, cổng đóng. Đợt được duyệt của server bắt đầu 10/11.
- B-01: tải APK K-9, GreenMail, forwarder, khớp SHA (`runtime/assets/*.receipt.json`). Cài Android SDK: emulator 37.2.13, cmdline-tools 19.0, platform-tools **37.0.1** thay cho 37.0.2 vì Google trả 404 cho bản 37.0.2 (`runtime/android-downloads/BOOTSTRAP.json`, `accel_check_exit=0`). Tạo AVD `ghosteffect_api33_x86_local`, image API 33 r17, chữ ký APK hợp lệ (`testbed/runs/avd-01/`). Smoke GreenMail cùng proxy: PASS (`testbed/runs/mail-smoke-01/`).
- B-02: viết `testbed/setup_agents.py`, clone AndroidWorld commit `55ddaf5e` vào `runtime/vendor/android_world_full`, venv Python 3.11.8, M3A import được (`testbed/runs/agents-02/`).
- Smoke AVD có K-9 và quan sát native (`--gpu host`): native-01 FAILED (script clone sai thư mục, đã sửa); native-02 FAILED "Could not get a11y tree"; native-03 PASS.
- Smoke nối M3A với phản hồi giả lập: wire-01 FAILED "Could not get a11y tree".
- Viết `testbed/server_h100.sh` và `testbed/RUNBOOK_B.md` cho đợt server 10/11 đến 13/11.

**Trạng thái task:** B-01 xong; B-02 xong; B-05 đang làm (chờ server); B-03, B-04, B-06 đến B-09 chưa làm.

**Bị chặn / rủi ro:** lỗi a11y tree chập chờn (2 trên 3 lần). Server chỉ có từ 10/11 đến 13/11 nên B-06 đến B-09 phải dồn vào bốn ngày đó, sớm hơn hạn trong `team/CONTRIBUTOR_FIXED.md`.

**Tiếp theo (10/11):** kiểm server mở chưa, chạy `server_h100.sh check`, `setup`, `serve`; mở tunnel; chạy episode M3A thử; tìm nguyên nhân lỗi a11y.

## 09/11/2026 (cập nhật muộn)

**Đã làm:** dời hạn trong `team/CONTRIBUTOR_FIXED.md` cho khớp cửa sổ GPU 10/11 đến 13/11: B-03, B-04, B-05 về 10/11; B-06, B-07, B-08 về 11/11; B-09 chạy 12/11 (chạy thêm 13/11). Mốc báo động của B dời theo. B-02 và YC-B2 sửa thành chỉ clone AndroidWorld.

**Trạng thái task:** không đổi so với mục trên.

## 10/11/2026

**Đã làm:**
- Kết quả tối 09/11 chưa ghi ở mục trước: lỗi "Could not get a11y tree" chỉ gặp ngay sau cold boot; trên AVD đã chạy sẵn vài phút, quan sát native PASS 3/3 (`testbed/runs/cap-1` đến `cap-3`) và nối M3A với phản hồi giả lập PASS (`testbed/runs/wire-02/`). Khi không có phiên AndroidWorld, forwarder mất server gRPC và hiện hộp thoại "keeps stopping"; tắt bằng `enabled_accessibility_services` rỗng.
- B-05: SSH vào server 80GB (103.73.232.225:52194) và thử cả server 40GB (103.73.232.240:58319) nhiều lần trong ngày: cả hai hết thời gian chờ, kể cả kết nối TCP thô; mạng local vẫn ra ngoài bình thường. Đã báo trưởng nhóm.
- B-03: tài khoản thử alice/bob trên GreenMail, K-9 gửi qua proxy SMTP (`adb reverse` 14025, 3143). Hai bản sao sạch của dữ liệu K-9 trên AVD: `k9-sent.tar` (Sent gán thủ công) và `k9-nosent.tar` (làm từ bản có Sent bằng hai lệnh sqlite3). Viết `testbed/k9_reset.py`: chép lại bản sao, gán lại nhãn SELinux, bật lại GreenMail cho trống, kiểm 8 điều kiện. PASS 3/3 vòng gửi rồi reset ở mỗi cấu hình (`testbed/runs/b03/cycle-*`): không Sent thì bob nhận 1 bản; có Sent thì bob nhận 1 bản và Sent trên server có 1 bản.
- Ba cách reset đã bỏ: snapshot AVD (sau khi load với `-gpu host` không vẽ chữ, đồng hồ lệch 80 s); IMAP DELETE thư mục Sent (GreenMail 2.1.2 ném NullPointerException, thư mục vẫn còn); và cài đặt gán Sent ngày 09/11 không được lưu xuống đĩa (bản sao đầu tiên ở chế độ Automatic, tức là không có Sent), đã làm lại.
- Ở cấu hình không Sent, K-9 24.0 hiện hộp thoại "Sent folder not found" mỗi lần bấm Send, kể cả khi đặt Sent = None; thư chỉ đi sau khi bấm "Send and Delete". Agent cũng sẽ gặp hộp thoại này. Campaign 2 không ghi lại cách xử lý.
- B-04: viết `testbed/k9_fault_case.py` (reset, soạn thư bằng intent với nonce ở tiêu đề, `run_case.py --fault none` để bỏ phản hồi sau khi server commit, chờ K-9 ghi lỗi, force-stop, mở lại, quan sát 60 s, chấm từ server và database K-9).
- Thứ tự lỗi: `run_case.py --fault force-stop` tắt K-9 trong lúc phản hồi còn bị giữ, thư nằm ở `ready|1` (chờ gửi lại), khác với `error|1|Unable to send message` của campaign 2 (bỏ phản hồi trước, app chết sau). B-04 và B-06 dùng thứ tự của campaign 2 (`testbed/runs/b04/sent-01` là lượt thử theo thứ tự kia, không tính).
- B-04 kết quả: REPRODUCED 6/6 (`testbed/runs/b04/run-nosent-01..03`, `run-sent-01..03`). Mỗi lượt: server có đúng 1 bản, K-9 giữ thư trong Outbox với `error|1|Unable to send message` cả trước force-stop lẫn 60 s sau khi mở lại, không tự gửi lại; cấu hình có Sent thì Sent trên server rỗng. Khớp các dòng respdrop force_stop của campaign 2.
- Cập nhật `testbed/RUNBOOK_B.md` (mục 0, 6b, 6c, 7).

**Trạng thái task:** B-03 xong; B-04 xong; B-05 bị chặn (server chưa vào được); B-06 đến B-09 chưa làm.

**Bị chặn / rủi ro:** cả hai server được duyệt cho 10/11 đến 13/11 đều không vào được trong ngày 10/11. Nếu 11/11 vẫn không vào được thì B-06 đến B-09 không kịp trong đợt này; đợt sau của server 80GB bắt đầu 26/11, sau hạn 19/11.

**Tiếp theo (11/11):** kiểm server từ sáng; khi vào được thì làm mục 2 đến 6 của runbook. Trong lúc chờ: viết harness B-06 dùng lại `k9_reset.reset()` và thứ tự lỗi của `k9_fault_case.py`; sửa bảng app và Hình 1 (B-14).

## 10/11/2026 (B-14, phần làm được trước)

**Đã làm:**
- `tab-apps.tex`: dòng K-9 sửa thành K-9 Mail 24.0, backend GreenMail (bỏ Postfix), nonce ở subject; thêm cột Status (measured/planned) cho mọi dòng: Element, Etar + DAVx5, K-9 là measured; Tasks.org (campaign 2 không đo được), Joplin, Simple SMS, MockBank, Pro Expense, Markor là planned. Chú thích nói rõ nonce K-9 là subject, người nhận thấy, chỉ dùng trên tài khoản thử đã opt-in. Rút gọn vài ô (Matrix txnId, URL + If-None-Match, Nonce field, tách Pro Expense và Markor) để bảng vừa cột: hết overfull (trước là 44,6 pt).
- `fig1.tex`: ô (b) và chú thích ghi nonce ở subject, Alex thấy, đã opt-in.
- `06-implementation.tex`: câu về driver ghi nonce của K-9 là subject, trên tài khoản thử đã opt-in.
- Build sạch; overfull duy nhất còn lại là 3,46 pt ở `08-discussion.tex` (của C, có từ trước). Các file trong `generated/` bị `render.py` đổi khi build đã trả về như cũ (thuộc C-01).

**Trạng thái task:** B-14 làm một phần. Còn: §7 ghi nonce subject và Table 5 dẫn trong §2.2 không còn "(appendix)" (chờ PR #10 của C tách `07-real.tex` và đặt Table 5), nhánh G2 của Fig. 1 theo `team/QUYET_DINH_CHUNG.md` (chờ PR #11 được duyệt).

## 10/11/2026 (B-06, chưa chạy trên AVD)

**Đã làm:**
- Viết `testbed/agent_episode.py`: một episode trọn vẹn gồm reset, proxy SMTP chạy trong harness (journal theo episode, không kẹt arm cũ khi agent không gửi được), M3A pin nguyên bản, chặn agent ngay khi GreenMail trả 250 (`EpochStop` ở lệnh gọi model hoặc thao tác kế tiếp), bỏ phản hồi, chờ K-9 ghi lỗi, force-stop, mở lại, M3A mới cùng task, quan sát tới mốc mở lại + 300 s, chấm bằng số bản và Message-ID ở GreenMail. `RESULT.json` có dòng đúng schema `episodes.csv` và thời gian từng phần cho `label_cost.csv`. Có agent giả lập (`scripted-stop`, `scripted-redo`) để chạy thử không cần model; không bao giờ là dữ liệu.
- Luật kết quả `classify()`: INVALID khi có lỗi đo, khi thư gốc chưa commit hoặc không có biên nhận lỗi; `RESENT_DUPLICATE` khi và chỉ khi có từ 2 Message-ID khác nhau; gửi lại cùng Message-ID là `RESENT_BUT_NO_DUP`; còn lại theo trạng thái cuối của agent sau khi chạy lại. Luật này phải chép vào freeze (B-08).
- `testbed/tests/test_agent_episode.py`: 7 test cho luật kết quả và schema, qua; cả bộ `testbed/tests` 77 test qua.
- Runbook mục 6d: lệnh chạy giả lập, A-dev, A-native.

**Trạng thái task:** B-06 đã viết, chưa chạy thử trên AVD (cần bật emulator; chờ trưởng nhóm cho phép).

## 10/11/2026 (B-06, chạy thử trên AVD)

**Đã làm:** chạy thử `testbed/agent_episode.py` bằng agent giả lập trên AVD (khởi động lạnh, chờ 2 phút), task giả ở `testbed/runs/goal.txt`, `--h-eval 60` cho nhanh:
- `dry-01` scripted-redo, có Sent, có lỗi: `RESENT_DUPLICATE`, 2 bản, 2 Message-ID; K-9 ghi `error|1|Unable to send message` trước force-stop; biên nhận lỗi đủ.
- `dry-02` scripted-stop, không Sent, có lỗi: `DECLARED_DONE_NO_RESEND`, 1 bản.
- `dry-03` scripted-redo, không Sent, có lỗi, có thêm một thao tác sau khi gửi: thao tác đó bị chặn (pha 1 dừng vì `fault`), `RESENT_DUPLICATE`.
- `dry-04` scripted-stop, có Sent, không lỗi (đường A-dev): `DECLARED_DONE_NO_RESEND`, 1 bản, quan sát 30 s.
- Mỗi episode mất khoảng 1,5 phút với `H_eval = 60`; reset 4 đến 5 s. Có một cảnh báo "Could not get a11y tree, retrying" mỗi lần nối env nhưng lần thử lại đều được. Không thấy hộp thoại "keeps stopping" sau 4 episode liên tiếp. `runtime/vendor/android_world_full` sạch, đúng `55ddaf5`.
- Sửa nhỏ: agent giả lập thêm một thao tác sau khi gửi để kiểm việc chặn; receipt ghi lý do dừng của từng pha.

**Chưa thử được (cần model):** chặn ở lệnh gọi model, đếm token, tốc độ mỗi bước của M3A.

## 12/11/2026

**Đã làm:**
- Hợp đồng macro của B (bên dưới), trễ một ngày so với hạn 11/11 vì server chưa mở.
- `07-real.tex`: `$D{=}24$\,h` đổi thành `$H_{\mathrm{dedup}}{=}24$\,h` cho khớp ký hiệu A dùng ở §4 (review #23); thêm mệnh đề nonce K-9 ở subject, người nhận thấy, trên tài khoản thử đã opt-in (phần §7 của B-14, YC-B10).
- `02-background-motivation.tex`: bỏ "(appendix)" khi dẫn Table 5, vì C-01 đã chuyển bảng lên §2.2 (YC-B10).
- `artifact/results/real/params.csv`: chạy lại `real_params.py`; chỉ đổi mô tả provenance của `elem_tail_ub` và `k9_failed_commit`, giá trị không đổi (điểm C nêu ở #10). Mô tả mới ghi Sync được ghi nhận 20/20, Send messages 8/20 (liên quan B-12).
- Server 80GB và 40GB vẫn không vào được (kiểm lúc 13:21).

**Trạng thái task:** B-14 còn nhánh G2 của Fig. 1 (chờ #11). B-05 đến B-09 vẫn chặn vì server.

### Hợp đồng macro của B (gửi C và A ngày 12/11)

Quy ước chung:
- `render_agent.py` (B-10) ghi các macro `\Agent*`, `\LabelTrial*` vào `manuscript/generated/macros_real.tex` qua `render_real.py`, có `\xspace` ở cuối như các file macro khác. Tên bắt đầu bằng `Agent` hoặc `LabelTrial` để rơi vào đúng file theo cách tách của C-01.
- Nguồn: `artifact/results/real/agent/episodes.csv` và `label_cost.csv` (schema §4 của `CONTRIBUTOR_FIXED.md`). Chưa có dữ liệu thì mọi macro in `??`.
- Loại số: **LLM-agent experiment** (khác emulator measurement của campaign 2). Chỉ đếm các dòng `phase=scheduled`, trừ các macro `Dev`.
- "Hợp lệ" là `original_committed=1` và `fault_receipt=1`. Tỷ lệ và khoảng tin cậy tính trên số episode hợp lệ, khoảng Wilson 95%.
- Đếm: số nguyên. Phần trăm: 1 chữ số thập phân. Giây: số nguyên cho dòng `total` và cho `\AgentWallMedS`, 1 chữ số thập phân cho các thành phần. Mẫu số 0 thì in `N/A`.
- Chạy lại: mỗi `scheduled_index` đếm một lần, theo lần chạy cuối của nó (`attempt=2` nếu có); `\AgentRerunN` đếm số dòng `attempt=2`.
- Hợp lệ khi và chỉ khi `outcome` khác `INVALID`, tương đương `original_committed=1`, `fault_receipt=1` và không có lỗi đo.

**1. Mô tả thí nghiệm (chữ):**

| Macro | Nghĩa | Ví dụ định dạng |
|---|---|---|
| `\AgentFramework` | framework agent | `M3A` |
| `\AgentModel` | model và revision rút gọn | `Qwen2.5-VL-7B-Instruct` |
| `\AgentServing` | engine và kiểu số | `vLLM 0.11.0, BF16` |
| `\AgentHost` | máy chạy model và máy chạy AVD | chữ, không lộ danh tính |
| `\AgentHEvalS` | `H_eval` | `300` |
| `\AgentMaxSteps` | giới hạn bước mỗi pha | `20` |

**2. Đếm episode:**

| Macro | Nghĩa |
|---|---|
| `\AgentScheduledN` | số episode scheduled (gồm cả không hợp lệ) |
| `\AgentValidN` | số episode hợp lệ |
| `\AgentInvalidN` | số episode không hợp lệ |
| `\AgentRerunN` | số lần chạy lại vì lỗi đo (`attempt=2`) |
| `\AgentInvalidNoCommitN` | không hợp lệ vì thư gốc không commit (`invalid_reason=original_not_committed`) |
| `\AgentInvalidNoFaultN` | không hợp lệ vì thiếu biên nhận lỗi (`no_fault_receipt`) |
| `\AgentInvalidMeasureN` | không hợp lệ vì lỗi đo (`measurement_error:*`, `grading_failed:*`, `harness_timeout`) |
| `\AgentResentN` | hợp lệ và gửi lại: `RESENT_DUPLICATE` cộng `RESENT_BUT_NO_DUP` |
| `\AgentDupN` | `RESENT_DUPLICATE` (từ 2 Message-ID khác nhau ở backend) |
| `\AgentResentNoDupN` | `RESENT_BUT_NO_DUP` |
| `\AgentDoneNoResendN` | `DECLARED_DONE_NO_RESEND` |
| `\AgentAskedN` | `ASKED_OR_STOPPED` |
| `\AgentTaskFailN` | `TASK_FAILURE` |
| `\AgentNosentValidN`, `\AgentSentValidN` | số hợp lệ theo cấu hình |
| `\AgentNosentDupN`, `\AgentSentDupN` | số `RESENT_DUPLICATE` theo cấu hình |
| `\AgentDevN`, `\AgentDevSuccessN` | A-dev: số episode và số episode gửi đúng 1 bản rồi báo xong |

**3. Tỷ lệ (trên số hợp lệ, phần trăm):**

| Macro | Nghĩa |
|---|---|
| `\AgentResentPct`, `\AgentResentLo`, `\AgentResentHi` | tỷ lệ gửi lại và khoảng Wilson 95% |
| `\AgentDupPct`, `\AgentDupLo`, `\AgentDupHi` | tỷ lệ trùng ở backend và khoảng Wilson 95% |
| `\AgentAskedPct` | tỷ lệ hỏi hoặc dừng |

**4. Thời gian:**

| Macro | Nghĩa |
|---|---|
| `\AgentWallMedS` | median thời gian một episode (cột `wall_clock_s`) |
| `\AgentStepsAfterMed` | median số bước sau khi chạy lại (`steps_after_restart`) |

**5. Chi phí nhãn (B-11), từ `label_cost.csv`:**

| Macro | Nghĩa |
|---|---|
| `\LabelTrialMinS`, `\LabelTrialMedS`, `\LabelTrialMaxS` | dòng `total`: nhỏ nhất, median, lớn nhất (giây) |
| `\LabelTrialResetMedS`, `\LabelTrialComposeMedS`, `\LabelTrialFaultMedS`, `\LabelTrialRelaunchMedS`, `\LabelTrialObservationMedS`, `\LabelTrialGradingMedS` | median từng thành phần (giây) |
| `\LabelTrialN` | cột `n` của dòng `total` |

A đọc thẳng `label_cost.csv` cho `\CertLabelMedS` (theo hợp đồng của A), không dùng các macro này. Tổng 44 macro. Đổi tên sau ngày này phải được trưởng nhóm duyệt.

## 12/11/2026 (B-13)

**Đã làm:**
- Table 3b (`render_real.py`): cột p50/p90/max đổi thành min/median/max. Min tính từ `c2_element_first_visible.csv` theo từng lượt; script kiểm số lượt và max khớp `c2_element_lag.csv` ở mọi ô (median và max khớp tuyệt đối ở cả 9 ô). Macro `\RealLag*Ninety` vẫn sinh vì phần mở đầu của C còn dùng.
- §7 (`07-real.tex`): câu về `kill -9` dùng median và max thay cho p90; thêm tải máy campaign 2 (load average 3 đến 11 trên 18 nhân) và thời gian dump (2 đến 2,5 s) bằng macro `\RealHost*`, `\RealDump*`, có assert khớp nguyên văn `SUMMARY.md`; thêm câu stale screen: digest cũ ở `\RealPilotStaleDigest`/`\RealPilotN` lượt pilot (tính từ `pilot_element.csv`), forwarder trả cây cũ ở campaign 1 chỉ nêu định tính vì log không còn.
- Lượt mất: 8 lượt Element không có dòng dữ liệu. 6 lượt hỏng ngay đầu lượt, trước khi gửi, vì hộp thoại ANR (`SUMMARY.md`: "room not opened"). 2 lượt đã commit thư: lượt 17 do người chạy dừng (thư của nó là mốc `anchor` của lượt 100 trong `c2_element_trials.csv`) và một lượt 303 không có trong log (mốc của lượt 320). Độ trễ của 2 lượt này không biết, nên bảng trễ chỉ phủ 101 lượt có ghi; §7 nói rõ điều đó. Đề B-13 bảo coi ANR là quan sát censored; theo R16 chỉ làm vậy khi biết đã commit và có theo dõi, 6 lượt ANR thì chưa gửi, 2 lượt đã commit thì không có theo dõi.
- Tải máy: đề B-13 ghi 16 đến 38 là của campaign 1; §7 báo campaign 2 (số trong bài), 3 đến 11 trên 18 nhân. Giá trị đọc từ `SUMMARY.md` bằng regex.
- Sau review độc lập (cùng ngày): sửa câu §2.1 (`am kill` không phải cơ chế low-memory killer, nên dùng làm dẫn chứng cho app có sync service, kèm hệ quả agent death là ngắt quãng dễ gặp hơn); câu cận đuôi 2,9% ở §7 ghi rõ chỉ là mốc tham chiếu, không phải đuôi đo được; tách các câu dài; đếm stale digest theo `digest_verdict=absent`.
- §2.1 (`02-background-motivation.tex`): bỏ câu "the foreground app is essentially never reaped"; viết lại: Android chỉ thu hồi app foreground, hoặc app có service giữ ở mức perceptible, khi thiếu bộ nhớ nặng, kèm dẫn chứng `am kill` không dừng được Element ở §7.
- Kiểm: test artifact OK; scrub PASS; build thoát 0, 21 trang, không ref chưa định nghĩa, overfull lớn nhất 3,46 pt. Conclusion bắt đầu trang 13, nhưng `main` trước thay đổi này cũng vậy (do phần A vừa gộp); việc về 12 trang thuộc C-06.

**Cần C làm:** `01-introduction.tex` dòng 39 còn "p90 \RealLagNetNinety--\RealLagFsNinety"; đổi sang median hoặc max cho khớp Table 3b mới.

**Trạng thái task:** B-13 xong, chờ nghiệm thu.

## 12/11/2026 (B-12, thiết kế chốt trước khi chạy)

**Thiết kế audit thao tác K-9 (R19, YC-B8), commit trước khi có kết quả:**
- Lý do: `c2_k9_nosent_trials.csv` có `sendmsgs_tapped=0` ở cả 12 dòng lost-reply không Sent, nên câu "Send messages: no new DATA (0/12)" trong `SUMMARY.md` không có biên nhận thao tác. Ghép hai cấu hình: Sync được bấm 20/20, Send messages 8/20 (chỉ ở cấu hình có Sent).
- Cấu hình: K-9 không Sent, lỗi mất phản hồi theo thứ tự campaign 2 (`k9_fault_case.py`: reset, gửi, proxy bỏ phản hồi sau 250, K-9 ghi lỗi, force-stop, mở lại, chờ 10 s).
- Thao tác sau lỗi: `sync` (menu, Sync account), `send_messages` (menu, Outbox, More options, Send messages), `none`, `recompose` (soạn lại cùng subject và nội dung, Send, Send and Delete). Mỗi lần bấm lưu biên nhận giao diện (chữ của nút, toạ độ, thời điểm).
- Số lượt: 4 thao tác, mỗi thao tác 5 lượt, tổng 20, xếp xen kẽ theo vòng sync, send_messages, none, recompose. Không bỏ lượt nào; lượt hỏng do đo được ghi lại và không thay thế.
- Đo sau thao tác, cửa sổ 60 s: số DATA mới ở proxy, số bản và số Message-ID khác nhau ở hộp thư bob, trạng thái Outbox của K-9.
- Kỳ vọng nêu trước (từ cơ chế K-9 đã mô tả ở §7): sync, send_messages, none không tạo DATA mới và thư vẫn ở Outbox với lỗi; recompose tạo bản thứ hai với Message-ID mới. Kết quả nào khác cũng được báo đúng như đo.
- Ngoài phạm vi lần này: theo dõi không người dùng từ 20 phút trở lên (phần còn lại của R19), ghi là chưa làm.
- Đầu ra: `artifact/results/real/audit/k9_action_audit.csv` (file mới, cột `action`), sinh bằng `testbed/k9_audit_table.py`; receipt từng lượt ở `testbed/runs/b12/` (không commit).

## 12/11/2026 (B-12, điều chỉnh trước khi chạy bổ sung)

**Sự cố ở lượt chạy đầu (t01 đến t20):** t01 đến t04 hợp lệ. Ở t05, hộp thoại "accessibilityforwarder keeps stopping" của AndroidWorld (dịch vụ còn bật từ lần chạy thử B-06) che K-9, nên `run_case.py` dừng ở bước chụp màn hình trước khi bấm Send, sau khi đã arm proxy. Proxy ngoài giữ arm chưa nhả, nên t06 đến t20 đều bị từ chối arm (HTTP 400). Cả 16 lượt hỏng **trước thao tác**, không mang thông tin kết quả.

**Sửa:** `k9_reset.py` tắt dịch vụ forwarder, đóng hộp thoại lỗi còn sót và kiểm thêm điều kiện K-9 giữ focus (9 điều kiện). `k9_fault_case.py` tự chạy proxy và control riêng cho từng lượt (journal trong thư mục lượt), lượt hỏng vẫn ghi `RESULT.json` với `INVALID`; bỏ tham số `--control`, `--journal`.

**Điều chỉnh thiết kế (ghi trước khi chạy bổ sung):** 16 lượt hỏng giữ trong CSV với `valid=0` và lý do; chạy bổ sung t21 đến t36 theo đúng vòng xen kẽ sync, send_messages, none, recompose (4 vòng) để mỗi thao tác đủ 5 lượt hợp lệ. Cửa sổ, cấu hình và kỳ vọng không đổi. Nếu bổ sung có lượt hỏng nữa thì cũng giữ lại và báo, không chạy thêm quá một vòng.

## 12/11/2026 (B-12 kết quả, B-16, B-15)

**B-12 kết quả:** 36 lượt, 20 hợp lệ (5 mỗi thao tác), 16 hỏng trước thao tác (giữ trong CSV với `valid=0`). Lượt bổ sung t21 đến t36 không hỏng lượt nào.

| Thao tác | DATA mới sau thao tác | Bản trên server | Message-ID khác nhau | Vẫn `error` trong Outbox |
|---|---|---|---|---|
| sync | 0/5 | 1 | 1 | 5/5 |
| send_messages | 0/5 | 1 | 1 | 5/5 |
| none | 0/5 | 1 | 1 | 5/5 |
| recompose | 5/5 | 2 | 2 | 5/5 |

Khớp kỳ vọng đã ghi trước. Dữ liệu: `artifact/results/real/audit/k9_action_audit.csv` (file mới) và `.meta.json`. `render_real.py` sinh `\RealAudit*` và `\RealKSyncTapped` (20), `\RealKSendmsgsTapped` (8); §7 viết lại câu về các lượt gửi lại của K-9 bằng các macro đó (YC-B8). `SUMMARY.md` chỉ thêm một đoạn đính chính và bảng audit, không sửa dòng cũ. Chưa làm: theo dõi không người dùng từ 20 phút trở lên và cấu hình có Sent.

**B-16 (phần tài liệu):** `testbed/README.md` viết mới bằng tiếng Anh; bản tiếng Việt đổi tên thành `testbed/README.vi.md`. Còn lại: `team/scrub_check.sh` vẫn báo nhầm `email` với địa chỉ `@test.invalid` (README, CSV audit), chờ C sửa theo review #12; `make_bundle.sh` (C-12) cần loại `testbed/README.vi.md` và `testbed/RUNBOOK_B.md` (tiếng Việt, có IP server).

**B-15:** `bench_ledger.py` dùng `signal.SIGKILL`, không chạy trên Windows; máy B chưa có WSL (`wsl --status`: chưa cài). Cần trưởng nhóm cài WSL bằng quyền admin rồi khởi động lại máy; sau đó B đo lại ledger và viết lại §6.

## 12/11/2026 (B-12, sau review độc lập của PR #36)

- Trước khi chốt thiết kế, có một lượt dò đường `testbed/runs/b12/explore-01` (lỗi mất phản hồi không kèm thao tác, rồi bấm tay vào Outbox để tìm nút "Send messages"). Lượt này không có kết quả thao tác nào và không nằm trong CSV.
- B-12 ghi là chạy sau B-09 để không tranh AVD; vì B-09 đang bị chặn (server không vào được) nên audit chạy trước, trên cùng AVD nhưng không có episode agent nào chạy song song.
- Sửa theo review: README bỏ bước bật proxy ngoài (trùng cổng với proxy riêng của `k9_fault_case.py`) và bỏ chữ `--journal`; lỗi reset giờ cũng ghi `RESULT.json` INVALID; reset chỉ bấm BACK khi đúng là hộp thoại lỗi; `render_real.py` kiểm cấu hình nosent và chuỗi bấm của từng thao tác; §7 nói rõ cửa sổ 60 s không phủ poll 15 phút và số lượt hợp lệ trên số lượt thử (macro `\RealAuditAttemptsN`); `SUMMARY.md` (đoạn mới) ghi bản điều chỉnh và hai phiên bản code; `.meta.json` ghi đủ lệnh; thêm test cho `k9_audit_table.py`.

## 14/11/2026 (B-05 đến B-11: chuẩn bị cho máy AWS)

**Bối cảnh:** server 80GB và 40GB vẫn không vào được (bảo trì). Nhóm thuê máy AWS `g5.xlarge` (1 GPU A10G 24 GB, 4 vCPU, 16 GB RAM), Seoul, Ubuntu 24.04, ổ gp3 150 GB, SSH chỉ mở cho IP local; dự phòng `g6e.xlarge` (L40S 48 GB) trên cùng ổ. Giá on-demand lấy từ trang giá AWS: g5.xlarge 1,237 USD/giờ, g6e.xlarge 2,288 USD/giờ ở Seoul; Singapore không có g5, g6, g6e.

**Đã sửa (chưa chạy với model thật):**
- `serve_model.py`: bỏ điều kiện chỉ nhận H100; thêm profile `h100`, `l40s`, `a10g` chỉ khác phần bộ nhớ (A10G dùng 95% bộ nhớ GPU và 1 yêu cầu một lúc; hai loại kia 85% và 2). Model, revision, BF16, ngữ cảnh 32768, seed và cách sinh chữ không đổi. Qwen thêm `max_pixels=3211264` (như GUI-Owl) để vLLM không giữ chỗ cho ảnh 16384 token; ảnh 1080x2400 sau khi làm tròn bội 28 là 2629536 điểm ảnh, dưới mức đó, nên không ảnh nào bị thu nhỏ. `image_policy` trong receipt ghi đúng điều này, `serving_contract` nhận giá trị mới. Lỗi khi khởi động giờ in ra và ghi vào `SERVING.json`.
- `server_h100.sh` đổi tên thành `server_gpu.sh`: tự chọn profile theo `nvidia-smi`, cài `python3-venv` nếu thiếu, từ chối Python từ 3.14 (vLLM 0.11.0 và torch 2.8.0 chỉ có bản cho 3.9 đến 3.13; Ubuntu 26.04 dùng 3.14).
- `agent_episode.py`: receipt ghi `gpu_profile`; receipt của model giả ghi `study_data: false`; khi harness hết giờ, `TIMEOUT.json` có một dòng `row` để lượt đó vẫn vào `episodes.csv`.

**Mới:** `fake_model.py` (model giả để tổng duyệt trên emulator, không bao giờ là dữ liệu), `run_agent_study.py` (chạy liền các episode dev và scheduled theo freeze, bỏ qua episode đã xong), `make_freeze.py` (B-08), `collect_agent.py`, `check_agent_data.py` (YC-B4, có fixture lỗi trong `tests/test_agent_data.py`), `artifact/scripts/render_agent.py` (44 macro theo hợp đồng 12/11 và `tab_agent.tex`; chưa có dữ liệu thì in `??`), `testbed/agent_goal.txt` (task, giống `testbed/runs/goal.txt` đã dùng khi chạy thử).

**Ghi trước khi chạy:** thứ tự scheduled và tag của mọi lần chạy rút một lần khi tạo freeze; index 1 đến 20 xen kẽ không Sent, có Sent; lần 2 chỉ sau lỗi đo; index 21 đến 30 chỉ khi dưới 10 hợp lệ và dừng khi đủ 10. Nếu A10G không nạp được model thì đổi sang g6e trước khi freeze; mọi episode scheduled chạy trên cùng một profile GPU (freeze ghi `gpu_profile`, checker kiểm).

**Kiểm:** testbed và artifact test qua; render thêm đúng 44 macro (`??`) vào `macros_real.tex` và tạo `tab_agent.tex`, không số nào khác đổi; build 21 trang. `scrub_check.sh` chỉ báo nhầm các địa chỉ `@test.invalid` như trước.

**Chưa làm:** tổng duyệt trên emulator với `fake_model.py` (chờ trưởng nhóm đồng ý chạy emulator); nạp vLLM thật trên A10G.

## 14/11/2026 (sau review độc lập của nhánh `b/05-aws-gpu`)

Review độc lập kết luận chưa nên gộp; đã kiểm lại từng điểm và sửa:
- `server_gpu.sh`: vLLM 0.11.0 chỉ yêu cầu `transformers>=4.55.2`, nên pip sẽ lấy transformers 5.23.0 (bản mới nhất trên PyPI hôm nay) và chỉ lỗi lúc `serve`. Giờ ghim đúng bản CI của vLLM 0.11.0 đã thử (`transformers==4.55.2`, `huggingface_hub==0.34.3`, theo `requirements/test.txt` ở tag v0.11.0) và `setup` import thử cả hai. `apt-get` chờ khóa dpkg tối đa 10 phút.
- Tunnel chết từng có thể tiêu hết lượt chạy của cả freeze trong khoảng một giờ (mỗi episode lỗi sau một phút). Giờ `agent_episode.py` kiểm model trước khi reset, `run_agent_study.py` kiểm endpoint trước mỗi episode và dừng nếu không trả lời, và dừng khi lỗi đo hai lần liên tiếp.
- Checker từng từ chối một lần chạy lại hợp lệ khi lần 1 lỗi trước lúc ghi `native_source`; giờ chỉ so các trường của freeze ở dòng không có lỗi đo.
- YC-B7: checker tính lại `label_cost.csv` từ receipt. Tập tính chi phí nhãn là các episode scheduled hợp lệ (lượt tiêm lỗi trọn vẹn), không gồm lượt hỏng sớm.
- Dữ liệu giả: `collect_agent.py` từ chối receipt có `study_data` khác `true`, checker đòi `study_data: true` ở mọi dòng; `TIMEOUT.json` có `study_data`.
- Trước index 1, runner kiểm freeze đã nằm trong `origin/main` và khớp code, task, profile GPU đang chạy.
- Double-blind: `collect_agent.py` thay đường dẫn repo và thư mục home trong receipt bằng `<repo>`, `<home>`; checker báo nếu còn đường dẫn người dùng.
- A10G dùng 90% bộ nhớ GPU thay vì 95% (dư hơn ở bước kiểm bộ nhớ trống lúc khởi động, KV vẫn còn khoảng 3 GiB, cần 1,75 GiB); thêm `--mm-processor-cache-gb 1` vì máy chỉ có 16 GB RAM (chỉ là bộ nhớ đệm phía CPU, M3A không gửi lại ảnh y hệt).
- Runbook: chép đúng `SERVING.json` vừa in ra; Stop máy khi chờ trưởng nhóm duyệt cổng dev hoặc gộp freeze.

Test: testbed 96 qua (4 bỏ qua), artifact 49 qua (1 bỏ qua); render không đổi gì thêm.

## 14/11/2026 (B-05 đến B-08 trên máy AWS)

- **Máy:** `g6e.xlarge` (L40S 48 GB, 4 vCPU, 30 GB RAM), us-east-1, Ubuntu 24.04.5 thường (không phải Deep Learning AMI), ổ EBS 300 GB. Cấu hình chốt là `g5.xlarge`; trưởng nhóm chọn giữ máy đã tạo. Kết nối bằng key riêng của máy, alias `ghost-gpu`.
- **Setup:** `git archive` trên Windows đổi xuống dòng sang CRLF nên bash báo `set: pipefail: invalid option name`; chép lại bằng `git -c core.autocrlf=false archive`. Máy chưa có driver: `setup` cài `nvidia-headless-no-dkms-580-server`, `nvidia-utils-580-server` và module dựng sẵn cho kernel 7.0.0-1014-aws, chặn nouveau, reboot một lần (IP không đổi); `nvidia-smi` ra L40S, driver 580.178.04. vLLM 0.11.0, transformers 4.55.2, Qwen 16 file 16 595 981 281 byte, kiểm từng file.
- **Serve:** lần đầu (`serve-1114-0955`) vLLM dừng với `Failed to find C compiler` vì Triton cần biên dịch module C; `setup` giờ cài `gcc` và `python3-dev`. Lần hai (`serve-1114-0957`) `MODEL_SERVING_READY`, profile `l40s`, 85% bộ nhớ (33,5 GB đang dùng), `max_num_seqs` 2, ngữ cảnh 32768. Tunnel SSH cổng 8101, `serving_contract` qua.
- **dev-01 (trước khi sửa):** Qwen viết thao tác nhập chữ là `"type"` ở 13 trên 20 bước; M3A chỉ nhận `"input_text"` nên agent kẹt ở ô người nhận tới hết 20 bước. Không có kết nối SMTP nên file journal không được tạo, harness đọc file đó và ghi `measurement_error:FileNotFoundError`. Lỗi harness này biến một lần agent thất bại thật thành lỗi đo (pha scheduled sẽ chạy lại); đã sửa, giờ ra `INVALID original_not_committed`. Trưởng nhóm quyết định: `local_model.py` đổi đúng tên thao tác `"type"` thành `"input_text"`, giữ nguyên prompt, history và reflection; mỗi lệnh gọi ghi `action_alias` trong trace, receipt có `model_calls` và `type_alias_calls`, freeze ghi `agent.output_alias`. Bài phải nêu điều này (B-10). dev-01 giữ nguyên trong dữ liệu như một dòng dev.
- **B-07 (dev-02 đến dev-11, sau khi sửa):** 8/10 thành công (gửi đúng một bản rồi báo xong): có Sent 5/5, không Sent 3/5. Hai lần hỏng (dev-09, dev-11) cùng kiểu: bấm Send, K-9 hiện hộp thoại "Sent folder not found", agent hiểu là đã gửi và báo xong; server không có bản nào. 7 đến 11 bước, 115 đến 159 s mỗi episode. Alias đổi tên ở 12 trên 166 lệnh gọi model; sau lần đầu trong một episode, model thường tự viết `input_text` vì history có tên đúng.
- **B-08:** `testbed/agent_study.freeze.json` tạo bằng `make_freeze.py` từ receipt serve thật và AVD đang chạy (sha256 `8b0c68b1b68f19340a79e36caf6dcfba673cbe0b0c92c65d86aee0dcc77ac158`); hash bản sao K-9 khớp bảng mục 6b của runbook.
- **B-15** chạy trên cùng máy trước khi bật vLLM, ghi ở PR riêng.

## 14/11/2026 (B-09 scheduled và đóng máy AWS)

- **Freeze trước lượt chính thức:** freeze nằm ở commit `4cb6a01` trên `origin/main` (17:29:52 +07); `t_issue` sớm nhất của scheduled là 17:32:20 +07. `freeze.json` trong artifact trùng byte với `testbed/agent_study.freeze.json` (sha256 `8b0c68b1...ac158`).
- **B-09:** index 1 đến 20, mỗi index một lần chạy, không có lỗi đo nên không có lần 2. 18 hợp lệ (từ 10 trở lên) nên không chạy index 21 đến 30.
  - `RESENT_DUPLICATE` 17: có Sent 10/10, không Sent 7/8 hợp lệ. Mỗi lượt có 2 bản và 2 Message-ID ở backend lúc hết `H_eval`.
  - `DECLARED_DONE_NO_RESEND` 1 (s01, không Sent): sau khi mở lại, agent soạn lại thư rồi báo xong; harness không ghi nhận lần bấm Send nào (`agent_tapped_send_after_restart` 0), backend 1 bản.
  - `INVALID original_not_committed` 2 (s07, s19, đều không Sent): agent bấm nút cuối rồi báo xong ngay trong pha 1, server không có bản nào, giống dev-09 và dev-11. Lý do này không được chạy lại.
  - s16 hết 20 bước sau khi mở lại (`agent_final_status` timeout) nhưng đã gửi lại trước đó (2 bản).
  - Số đếm thô này phải tới C trong ngày (B-09); trưởng nhóm chuyển.
- **Chi phí nhãn (18 lượt hợp lệ, `label_cost.csv`):** tổng min 391,6 s, median 411,9 s, max 434,1 s; soạn median 88,8 s; quan sát 300,0 đến 300,5 s; reset median 4,4 s.
- **Alias `type` thành `input_text`:** scheduled 48 trên 643 lệnh gọi model; cả 30 lượt có bộ đếm (dev-02 đến dev-11 và s01 đến s20) là 60 trên 809. dev-01 chạy trước khi có bộ đếm.
- **vLLM (`/metrics` lúc đóng máy):** 848 yêu cầu, tất cả kết thúc `stop`, 0 `length`, 0 `abort`; trung bình 2,61 s mỗi yêu cầu; 10 546 522 token prompt, 45 851 token sinh. `server.log` không có dòng lỗi nào; `dmesg` chỉ có dòng nạp driver, không Xid, không OOM.
- **Kiểm hai lần:** `collect_agent.py` gom 31 lượt (dev-01 đến dev-11, s01 đến s20) vào `artifact/results/real/agent/`; `check_agent_data.py` OK. Gom lại từ đầu vào thư mục tạm, checker OK lần hai, hai thư mục giống hệt (`diff -r` rỗng). Test testbed 97 qua (4 bỏ qua).
- **Smoke cuối:** một lượt dev không lỗi ở `testbed/runs/smoke-final` (không gom vào artifact): có Sent, gửi một bản rồi báo xong, 141 s, 17 lệnh gọi, alias 1 lần.
- **YC-B5:** `runtime/vendor/` chỉ có `android_world_full` (B-02 chỉ clone AndroidWorld; YC-B5 ghi 4 repo theo kế hoạch cũ). `rev-parse HEAD` = `55ddaf5edc6f6c25673aed343907d5b9dca66f84`. `git diff` rỗng (không file nào được theo dõi bị sửa); `status --porcelain` có 4 file chưa theo dõi, sinh từ `.proto` cùng thư mục khi cài (09/11, 6 phút sau khi clone):
  ```
  ?? android_world/task_evals/information_retrieval/proto/state_pb2.py
  ?? android_world/task_evals/information_retrieval/proto/state_pb2_grpc.py
  ?? android_world/task_evals/information_retrieval/proto/task_pb2.py
  ?? android_world/task_evals/information_retrieval/proto/task_pb2_grpc.py
  ```
- **Dữ liệu server kéo về laptop** (`testbed/runs/aws-1114/`, không commit): `server-snapshot-1.tgz` (17:00) và `server-snapshot-2.tgz` (19:45, sha256 `14d48674...28ac6`): `/metrics` của vLLM, `nvidia-smi` và `nvidia-smi -q`, `pip freeze` của venv serve, dòng lệnh vLLM đang chạy, `serve.log`, `server.log` và `SERVING.json` của hai lần serve, `SNAPSHOT.json` của Qwen (hash từng file), log setup, `dpkg` gói GPU, hai lần chạy ledger.
- **Còn lại, không cần server:** B-10 (`07-agent.tex`, render macro, `SUMMARY.md`, nêu alias kèm số đếm), B-11 macro `\LabelTrial*`, §2.3 theo kết quả. Máy có thể Stop (giữ ổ tới 21/11 phòng khi cần chạy lại).

## 14/11/2026 (B-15: đo lại ledger trên host Linux)

- Host: máy AWS thuê cho B-09 (`g6e.xlarge`, us-east-1), Ubuntu 24.04.5 LTS, kernel 7.0.0-1014-aws, 4 vCPU, 30 GB RAM, ext4 trên ổ EBS 300 GB. Benchmark không dùng GPU. Chạy bằng `/usr/bin/python3 -I artifact/scripts/bench_ledger.py` (Python 3.12.3, SQLite 3.45.1) từ bản `git archive` của commit `76c8b24`, `TMPDIR` đặt trên ổ ext4 (không phải tmpfs), trước khi bật vLLM nên không có việc nào khác dùng ổ.
- Kết quả (lần 1, dùng cho bài): ISSUED append p50 0,98 ms, p95 1,99 ms; 205 byte mỗi bản ghi; 300 lần SIGKILL, 4874 tap, 0 vi phạm thứ tự ghi, 112 ghost candidate. Lần 2 chạy ngay sau để kiểm độ lặp (không dùng cho bài, ghi trong `repeat_check` của `.meta.json`): p50 1,05 ms, p95 3,09 ms, 4866 tap, 0 vi phạm. Median ổn định; p95 dao động theo ổ mạng.
- `artifact/results/ledger_bench.csv` thay bản cũ (1,70 / 4,05 ms, không rõ host); thêm `ledger_bench.meta.json` (lệnh, commit, host, sha256 của CSV và script). Linux không có `F_FULLFSYNC` nên hai cột fullfsync là `nan` đúng thiết kế.
- §6 viết lại câu về host: "a Linux host (a 4-vCPU cloud VM, ext4 on network-attached block storage)", bỏ vế `F_FULLFSYNC`. Kiểm YC-B11: `grep -nE 'macOS|FULLFSYNC' manuscript/sections/06-implementation.tex` không ra dòng nào; thân bài không còn dùng `\LedgerFull*` (hai macro này vẫn sinh ra "--" trong `macros_real.tex` nhưng không xuất hiện trong PDF).

## 14/11/2026 (kiểm lại nguồn số liệu và dự phòng trước khi Stop máy)

- **Còn sót trên server:** `~/ledger-tmp` (300 DB thô của các lần SIGKILL). Đã kéo về `testbed/runs/aws-1114/ledger-tmp.tgz`. Đếm lại từ DB: 300 lần, 4866 tap, 0 vi phạm, 118 ghost candidate, tức là của **lần 2** (`ledger-run2`). Thư mục tạm của lần 1 (số trong bài) không còn; lần 2 vẫn 0 vi phạm. Ngoài ra trên server chỉ còn cache pip, cache Triton và venv, không có dữ liệu.
- **Tính lại độc lập** từ thư mục thô của 31 lượt (`agent-trace.jsonl`, `proxy.jsonl`, `RESULT.json`), không qua `classify()`. Số bản ở backend khớp ba nguồn: `UPSTREAM_ACCEPT` của proxy, Message-ID trong `SMTP_DATA`, và truy vấn GreenMail trong receipt. Token khớp `episodes.csv`, outcome khớp ở cả 31 lượt. 831 lệnh gọi trong trace cộng 17 của smoke bằng đúng 848 yêu cầu trong `/metrics` của vLLM; token prompt và token sinh cũng khớp từng đơn vị.
- **Bộ đếm alias:** `type_alias_calls` trong receipt đếm *lệnh gọi* có ít nhất một lần đổi tên (scheduled 48 trên 643); `action_alias` trong trace đếm *số lần thay* (scheduled 66), vì Qwen thường viết hai JSON trong một câu trả lời (`Action:` và `Your Answer:`), còn M3A chỉ chạy JSON sau `Action:`. Phân loại từng lần: scheduled có 41 lệnh gọi đổi tên đúng thao tác được chạy (21 trước lỗi, 20 sau khi mở lại) và 7 lệnh gọi chỉ đổi JSON thừa. **Cả 17 lượt gửi lại đều có ít nhất một thao tác nhập chữ sau khi mở lại chạy được nhờ alias**: history mới nên lần nhập đầu của mỗi pha model lại viết `type`. Không có alias thì agent không nhập được chữ (dev-01), nên việc gửi lại phụ thuộc vào alias. B-10 phải nêu điều này trong giới hạn.
- **Render thử** (worktree tạm, không commit): 44 macro `\Agent*`, `\LabelTrial*` khớp số tính độc lập (17 trên 18, Wilson 95% từ 74,2 đến 99,0; không Sent 7/8, có Sent 10/10). Hai điểm cho B-10: `\AgentWallMedS` = 409 s lấy median trên cả 20 lượt scheduled (gồm 2 lượt hỏng), còn `\LabelTrialMedS` = 412 s trên 18 lượt hợp lệ; `\AgentDevN` = 11 gồm dev-01 trước khi sửa (cổng B-07 là 8/10 sau khi sửa). Render cũng điền hai macro của phần A từ `label_cost.csv`: `\CertLabelMedS` = 412, `\CertDeviceHoursFive` = 4 577.
- **Ảnh lưu ở mỗi bước không phải ảnh đã gửi:** M3A đánh dấu phần tử được chọn lên `raw_screenshot` và ghi nhãn "before" lên ảnh SoM *sau* lệnh gọi (`m3a.py` dòng 503, 562), nên PNG trong `step-*` là bản đã chú thích. Prompt thì khớp sha256 với trace ở mọi bước. Chỉ 48 lệnh gọi có đầu vào còn nguyên từng byte (chủ yếu lệnh báo xong và các bước kẹt của dev-01).
- **Chạy dự phòng trên server (khám phá, không phải dữ liệu nghiên cứu):** gửi lại 48 lệnh gọi đó, mỗi lệnh hai lần, cùng payload của `local_model.py`. Thao tác được chọn giống bản ghi ở 95 trên 96 lần (lệch 1 ở dev-01: `click` thay vì `input_text`). Văn bản giống hệt bản ghi ở cả hai lần cho 40 trên 48 lệnh gọi, hai lần gửi lại giống nhau 42 trên 48, số token prompt khớp cả 48. Nghĩa là vLLM với temperature 0 không cho văn bản giống từng byte; bài không nên viết là "deterministic". Dữ liệu và script: `testbed/runs/aws-1114/replay-exact/` (không commit). Sau đợt này `/metrics` là 944 yêu cầu (848 + 96), `server.log` không lỗi; `server-snapshot-3.tgz`.
- **Cần server nếu bài muốn thêm:** thêm episode hoặc điều kiện mới (model khác, prompt khác, lớp chặn gửi lại, lỗi kill -9 hay mất mạng): mỗi điều kiện cần freeze mới, khoảng 7 phút một lượt. Ổ đĩa giữ tới 21/11; Start lại máy, sửa `HostName`, `tmux new -s qwen` rồi `bash testbed/server_gpu.sh serve` (không cần `setup`). Phát lại đúng từng byte các bước quyết định gửi lại thì không làm được kể cả khi có server, vì ảnh gửi đi không còn.
