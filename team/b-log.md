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

## 14/11/2026 (B-10: phần agent trong bài, B-11 macro)

- **`07-agent.tex`** (mục 7.8 "An LLM agent in the K-9 trap", nằm trong §7 qua `\input` có sẵn): model và phiên bản, host, kiểu lỗi, `H_eval`, số scheduled, hợp lệ, không hợp lệ kèm lý do, gửi lại, trùng ở backend, hỏi hoặc dừng, thất bại tác vụ, Wilson 95%, median thời gian; alias nêu rõ kèm số đếm; danh sách giới hạn (một agent, một model, một app, chỉ emulator, một kiểu lỗi, n nhỏ, alias). Mọi số là macro. Trong PDF mục này khoảng 32 dòng, tức khoảng 0,57 cột (một cột khoảng 57 dòng), dưới mức 0,6.
- **§2.3:** bỏ câu "Our emulator measurements ... do not run an LLM agent"; thêm kết quả agent bằng macro và dẫn tới §7.8; câu cuối giờ nói về agent và app khác. Sửa `56--74` thành `56 to 74`. Câu dài 48 từ của đoạn này đã tách.
- **Hợp đồng macro thêm 3 tên** (từ 44 lên 47): `\AgentModelCallsN` (643), `\AgentAliasCallsN` (48), `\AgentAliasEpisodesN` (20), lấy từ bộ đếm `model_calls`, `type_alias_calls` trong receipt của các lượt scheduled. **`\AgentWallMedS` đổi sang median trên các lượt hợp lệ** (412 s thay vì 409 s trên cả 20 lượt), để cùng mẫu số với tỉ lệ và với `\LabelTrialMedS`. Đổi trước khi bài dùng macro này; test cập nhật theo.
- **YC-07:** #39 thêm `episodes.csv` và `label_cost.csv` mà thiếu `.meta.json`; đã thêm hai file. Thêm `artifact/results/real/agent/SUMMARY.md`.
- **Render:** `macros_real.tex` không còn `??` (47 macro agent có giá trị, không macro `\Real*` nào đổi); `tab_agent.tex` sinh ra nhưng chưa được `\input` ở đâu (C quyết có đặt vào phụ lục không). Render cũng đổi `macros_guarantee.tex` của A (`\CertLabelMedS` 412, `\CertDeviceHoursFive` 4 577); PR này không commit file đó, cũng không commit `main.pdf`.
- **Kiểm:** `build.sh` thoát 0, 22 trang, không overfull quá 10 pt, PDF không còn `??`. Test testbed và artifact qua. Scrub qua trên các file đã đổi. `07-agent.tex`: 0 câu quá 45 từ, 0 đoạn có hơn 1 dấu chấm phẩy, 0 `\para`, 0 `\emph`.
- **Còn mở (YC-12, ngoài B-10):** tổng các file văn bản của B vẫn vượt giới hạn: `\para` 9 (giới hạn 5), `\emph` 25 (10), câu quá 45 từ 9, đoạn có hơn 1 dấu chấm phẩy 10. Cần một lượt sửa riêng cho §2, §6, §7 phần đo và `fig1.tex`.
- **Cần C:** mục "Planned device study" (`07-evaluation.tex`) mở đầu bằng "RQ7 measured app behaviour, not agents", giờ cần một câu dẫn tới §7.8. **Cần A:** lần render tới sẽ điền `\CertLabelMedS` và `\CertDeviceHoursFive` từ `label_cost.csv`.

## 14/11/2026 (YC-12: độ dễ đọc các file văn bản của B)

- Phạm vi: `02-background-motivation.tex`, `06-implementation.tex`, `07-real.tex`, `07-agent.tex`, `tab-apps.tex`, `tab-position.tex`, `figures/fig1.tex`. Chỉ đổi câu chữ, không đổi số, macro hay kết luận nào.
- `readability_count.py` trên các file đó, trước và sau: `\para` 9 thành 4 (giới hạn 5), `\emph` 25 thành 9 (giới hạn 10), câu quá 45 từ 9 thành 0, đoạn có hơn 1 dấu chấm phẩy 10 thành 0.
- Cách làm: tách câu dài và các chuỗi liệt kê nối bằng dấu chấm phẩy; bỏ `\para` ở đoạn đầu §6 và §7 phần đo, ba khoảng trống ở §2.2 giờ mở bằng "The first/second/third gap is"; tên nút và trạng thái giao diện (Send, Pay, Save, Post, Sent, Lease) đặt trong ngoặc kép thay vì `\emph`, nhãn bốn loại gián đoạn ở §2.1 thôi in nghiêng.
- `fig1.tex`: ba `\newcommand` của hình chuyển vào trong `tikzpicture` (cục bộ trong hình) để bộ đếm không đọc mã TikZ thành văn; caption tách câu. Hình hiển thị như cũ (đã xem ảnh trang 2).
- Dấu gạch ngang trong các câu đã sửa: `20--100`, `Clopper--Pearson`, `prepare--dispatch--settle` và ba khoảng macro `A--B` đổi thành "from A to B" hoặc dấu phẩy. Các ô `--` (nghĩa là "không có") trong `tab-position.tex` giữ nguyên.
- §6 thêm một câu: các lượt M3A của §7.8 chạy agent nguyên bản trên cùng cấu hình K-9, emulator x86-64.
- Kiểm: `build.sh` thoát 0, 22 trang, không overfull quá 10 pt, PDF không còn `??`; test testbed và artifact qua; scrub qua trên các file đã đổi.
- Còn lại ngoài YC-12: YC-10 ("G2" chỉ trong định lý, chứng minh, bảng) chưa đạt ở §6, §7 phần đo và Fig. 1; cả bài đều dùng "G2" trong văn nên cần thống nhất với A và C trước khi sửa.

## 14/11/2026 (arm có GhostEffect: thiết kế chốt trước khi chạy)

- **Mục đích:** so GhostEffect với M3A nguyên bản trên cùng bẫy K-9 (trưởng nhóm yêu cầu 14/11, sau B-09). Thí nghiệm bổ sung, không thuộc freeze B-09.
- **Hai arm:** baseline là 20 lượt scheduled s01 đến s20 đã chạy theo `agent_study.freeze.json`. Arm guard là 20 lượt g01 đến g20 theo `testbed/agent_study_guarded.freeze.json` (sha256 `54e174dc...40b1`): model, decoding, task, app, kiểu lỗi, `H_eval`, luật kết quả, host và mục `agent` (gồm alias) trùng baseline; tag và cờ người dùng sai rút một lần trong freeze. Hai arm chạy nối tiếp cùng ngày, cùng server, không xen kẽ ngẫu nhiên: ghi là giới hạn.
- **Guard** (`testbed/ghost_guard.py` trên `controller.py`, `classifier.py`; agent, prompt và model không đổi): trước cú chạm mà classifier nhận là commit (từ điển tiếng Anh trên phần tử được chạm), effect được ghi `ISSUED` bền vững trong ledger SQLite của host rồi mới chạm. Sau khi kill agent, force-stop và mở lại K-9, controller mới mở lại ledger từ đĩa và gọi `recover()`. K-9 không có chứng nhận runtime nên kết quả là hỏi. Người dùng giả lập trả lời theo GreenMail, sai đúng ở lượt có cờ `user_error` 1 (tỉ lệ 5%, giả định mô phỏng của bài). "Đã nhận": COMMITTED, không khởi động lại agent. "Chưa nhận": ABSENT, agent khởi động lại như baseline. Không có ứng viên (classifier bỏ sót): agent chạy lại không có guard, giữ trong dữ liệu.
- **Cờ đã rút:** index 15 lượt 1 có `user_error` 1; index 10 chỉ có ở lượt 2 (chạy khi lượt 1 lỗi đo).
- **Phân tích chốt trước** (`render_guarded` trong `render_agent.py`, viết trước khi chạy): chỉ số chính là tỉ lệ RESENT_DUPLICATE trên lượt hợp lệ, Wilson 95%, Fisher exact hai phía so với baseline. Chỉ số phụ: số lượt hỏi, số lượt classifier bỏ sót, số lượt người dùng giả lập sai.
- **Kỳ vọng ghi trước:** bản trùng chỉ xảy ra khi người dùng giả lập sai hoặc classifier bỏ sót cú chạm Send. Ở K-9 guard hỏi ở mọi lượt hợp lệ, nên đây là kiểm tra cơ chế end-to-end, không phải kiểm tra hiệu chỉnh.
- **Dev (không phải kết quả):** gdev-01 (không Sent) và gdev-02 (có Sent): Send được ghi `ISSUED`, hỏi, COMMITTED, 1 bản. gdev-03 (có Sent, `user_error` 1): ABSENT, agent chạy lại, ghi `ISSUED` lần 2, gửi lại, 2 bản. Thư mục `testbed/runs/agent-guarded/`.
- Báo nguyên trạng; chỉ chạy lại theo luật lỗi đo của freeze.

## 15/11/2026 (arm có GhostEffect: kết quả)

- **Chạy:** 20 lượt scheduled g01 đến g20 theo `agent_study_guarded.freeze.json`, từ 22:53 ngày 14/11 đến 01:10 ngày 15/11, trên nhánh `b/guarded-arm` (file đúng hash của freeze). Mỗi index một lần, không có lỗi đo.
- **Kết quả:** 19 lượt hợp lệ. Bản trùng 1/19 (g15, đúng lượt freeze rút cờ người dùng sai: người dùng nói "chưa nhận", ledger ABSENT, agent chạy lại và gửi lần 2). 18 lượt còn lại: guard hỏi, "đã nhận", COMMITTED, server 1 bản. g19 không hợp lệ: agent nhập chữ vào cùng một ô suốt 20 bước, chưa chạm Send (không phải classifier bỏ sót). Guard hỏi ở 19/19 lượt hợp lệ; classifier bắt được cú chạm Send ở mọi lượt hợp lệ.
- **So với baseline:** bản trùng 17/18 (94,4%) xuống 1/19 (5,3%, Wilson 95% từ 0,9 đến 24,6), Fisher exact hai phía p = 2,0e-8. Hai arm chạy nối tiếp, cùng ngày, cùng server.
- **Kiểm:** `collect_agent.py` gom 23 lượt (gdev-01 đến gdev-03, g01 đến g20) vào `artifact/results/real/agent_guarded/`; `check_agent_data.py --freeze` OK hai lần, bản gom lại giống hệt; baseline vẫn OK. Tính lại độc lập từ trace, proxy và `ledger.db`: khớp mọi số (trừ khác biệt định nghĩa bộ đếm alias đã ghi). vLLM: 1306 yêu cầu = 944 trước đó + 362 của arm này, 0 `length`, 0 `abort`, `server.log` không lỗi; `server-snapshot-4.tgz`.
- **Bài:** §7.8 thêm một đoạn với 11 macro `\AgentGuard*` (tên đổi từ `\Guard*` để nằm trong `macros_real.tex`), nói rõ ở K-9 arm này kiểm ledger và hỏi end to end, không kiểm hiệu chỉnh; giới hạn thêm "a simulated user, and arms run one after the other". Bỏ câu về Outbox, mô tả task và câu dẫn tới mục device study để giữ khoảng 34 dòng, tức khoảng 0,59 cột. Thêm `SUMMARY.md` và hai `.meta.json` cho thư mục mới.
- **Server:** không còn việc nào cần server; báo trưởng nhóm có thể Stop.

## 15/11/2026 (arm rule cascade: thiết kế chốt trước khi chạy)

- **Mục đích:** so GhostEffect với rule cùng bằng chứng của bài (RQ3, `planner_sim.resolve_rules`) trên agent thật, ở cấu hình K-9 có thư mục Sent, nơi mô phỏng dự đoán rule gửi lại còn GhostEffect hỏi (trưởng nhóm yêu cầu 15/11).
- **Freeze:** `testbed/agent_study_rules.freeze.json` (sha256 `dea3e1fe...afb0`): model, decoding, task, app, kiểu lỗi, `H_eval`, luật kết quả, host, mục `agent` và luật thứ tự trùng baseline; mọi index đều cấu hình có Sent (không Sent thì họ end-to-end duy nhất là VLM, chưa có bộ đọc thật). Cờ người dùng sai chỉ rơi vào index 22 lượt 2 (chỉ dùng nếu cần index phụ và lượt 1 lỗi đo).
- **Rule** (`ghost_guard.Rules`, cùng ledger và cùng chỗ chặn với GhostEffect): sau khi mở lại, đọc các thư mục K-9 đang giữ thư (Outbox là hop 1, K-9 không G2 nên không bỏ phiếu), chờ cố định 10 s, đọc lại: thư ở Sent thì COMMITTED, không chạy lại agent; không có thì mọi họ đọc vắng, ABSENT, agent chạy lại; không đọc được thì hỏi người dùng giả lập như arm guard. Đọc chính xác qua database của K-9, tức là cận trên của một bộ đọc bằng hình.
- **Phân tích chốt trước** (`render_rules` trong `render_agent.py`): tỉ lệ RESENT_DUPLICATE trên lượt hợp lệ, Wilson 95%, Fisher exact hai phía so với các lượt cấu hình có Sent của arm guard (`\AgentGuardSent*`). Phụ: số lần cho gửi lại, số lần hỏi, số lần classifier bỏ sót.
- **Kỳ vọng ghi trước:** K-9 chỉ ghi Sent sau khi gửi thành công nên sau khi mất phản hồi Sent không bao giờ có thư; rule cho gửi lại ở mọi lượt hợp lệ, và bản trùng phụ thuộc agent có soạn lại hay không.
- **Dev (không phải kết quả):** rdev-01 (có Sent): Outbox có thư, Sent không có, RETRY, agent chạy lại và gửi lại, 2 bản. Thư mục `testbed/runs/agent-rules/`.

## 15/11/2026 (arm rule cascade: kết quả và sự cố emulator)

- **Kết quả:** 20 index, 15 lượt hợp lệ. Rule cho gửi lại ở 15/15 lượt (Sent không bao giờ có thư sau khi mất phản hồi), 14 lượt agent gửi lại thành bản trùng (93,3%, Wilson 95% từ 70,2 đến 98,8), r11 là TASK_FAILURE (agent chạy lại gọi `open_app` 20 lần). So với các lượt có Sent của arm GhostEffect (0/10): Fisher exact hai phía p = 3,4e-6. Rule không hỏi lần nào; classifier bắt được Send ở mọi lượt hợp lệ. r07, r08: thư gốc không tới server.
- **Sự cố:** index 9 (kiểm focus lúc force-stop), 10 và 12 (reset: K-9 không có focus) hỏng hai lần liên tiếp nên INVALID (mỗi index một lần chạy lại). Nguyên nhân: sau khoảng 10 giờ với máy ảo 2 GB, System UI hiện hộp thoại "isn't responding" chiếm focus; sau đó bản ghi "LAST ANR" trong `dumpsys window` (dòng `mCurrentFocus` đầu tiên là null) làm `k9_reset` đọc sai focus. `k9_reset.py` nằm trong code bị freeze hash nên không sửa giữa arm.
- **Xử lý:** 02:43 reboot hệ điều hành của emulator; 02:57 đến 02:59 một watchdog (chỉ chạm "Wait" trên hộp thoại ANR của System UI, ghi log `testbed/runs/anr-watchdog.log`) chạm 14 lần, đều trước pha agent của r11, sau đó không chạm lần nào; 03:08 khởi động lại emulator với RAM 4 GB (`-memory 4096`, `config.ini` đã hash không đổi), index 13 đến 20 chạy không có ANR. Runner có thêm luật: chạy lại đúng lệnh thì đi tiếp qua index đã có hai lỗi đo ghi từ trước, còn hai lỗi mới liên tiếp vẫn dừng. Checker bỏ qua phần kiểm guard ở dòng có lỗi đo (reset hỏng trước khi guard được tạo). Hai sửa này không thuộc code bị freeze hash.
- **Kiểm:** gom 24 lượt (rdev-01, r01 đến r20, r09-r2, r10-r2, r12-r2) vào `artifact/results/real/agent_rules/`; checker OK hai lần (bản gom lại giống hệt). Baseline và arm guard vẫn OK.
- **Bài:** §7.8 thêm một câu về rule (macro `\AgentRules*`, `\AgentGuardSent*`); gọn lại phần mở đầu, câu các nhóm kết quả và câu alias để mục vẫn khoảng 33 dòng, tức khoảng 0,57 cột.

## 15/11/2026 (arm T3A và arm chỉ kill agent: thiết kế chốt trước khi chạy)

- **Mục đích:** gỡ hai giới hạn "một agent" và "một kiểu lỗi" của §7.8 (trưởng nhóm chốt 15/11, duyệt trước mọi PR và commit).
- **Arm T3A:** T3A của AndroidWorld (chỉ đọc văn bản của cây giao diện, cùng commit pin, prompt nguyên bản) trên cùng Qwen qua `TextOnlyModel`; alias `type` thành `input_text` vẫn áp dụng. Cùng task, lỗi `drop-forcestop`, `H_eval`, luật kết quả, cấu hình xen kẽ; 20 index; freeze `testbed/agent_study_t3a.freeze.json`; lượt `t01` đến `t20`. Không guard.
- **Arm chỉ kill agent:** M3A, lỗi `drop-killagent`: proxy bỏ phản hồi, K-9 ghi lỗi, agent bị kill rồi khởi động lại cùng task; K-9 không bị force-stop, không mở lại. `H_eval` tính từ lúc agent khởi động lại. Freeze `testbed/agent_study_killagent.freeze.json`; lượt `k01` đến `k20`. Không guard.
- **Code:** `agent_episode.py` (`--framework t3a`, `--fault drop-killagent`, nhận biết thao tác `status` của T3A từ chữ), `make_freeze.py` (`--framework`, `--fault`), `run_agent_study.py` (lấy agent và kiểu lỗi từ freeze), test mới.
- **Phân tích chốt trước** (`render_arm` trong `render_agent.py`): tỉ lệ RESENT_DUPLICATE trên lượt hợp lệ, Wilson 95%. Phụ: Fisher exact hai phía so với M3A force-stop, các nhóm kết quả khác, bộ đếm alias. Macro `\AgentText*` (T3A) và `\AgentKill*`.
- **Thứ tự:** chạy xong arm rules; 2 lượt dev có lỗi cho mỗi arm; freeze cả hai trong một PR (merge commit); chạy T3A 20 lượt rồi kill-only 20 lượt nối tiếp bằng một script, trên cùng nhánh, không đổi nhánh giữa chừng.
- **Không ghi kỳ vọng về hướng:** T3A không thấy ảnh nên có thể đọc Outbox khác M3A; khi chỉ kill agent, màn hình K-9 giữ nguyên nên agent có thể thấy thông báo lỗi gửi.

## 15/11/2026 (arm T3A và arm chỉ kill agent: dev và freeze)

- **Dev (không phải kết quả), máy ảo RAM 4 GB:** tdev-01 (T3A, không Sent): T3A báo xong trước khi thư tới server, INVALID original_not_committed. tdev-02 (T3A, có Sent): gửi lại, 2 bản; harness nhận đúng thao tác `status` của T3A. T3A không cần alias (0 lần đổi tên): nó tự viết `input_text`. kdev-01 (không Sent) và kdev-02 (có Sent): lỗi `agent-kill-only` (K-9 không bị force-stop), agent gửi lại, 2 bản mỗi lượt. Thư mục `testbed/runs/agent-t3a/`, `testbed/runs/agent-killagent/`.
- **Freeze:** `testbed/agent_study_t3a.freeze.json` (sha256 `c5cecb82...65afc`, `agent.framework` t3a) và `testbed/agent_study_killagent.freeze.json` (sha256 `6c766d3d...cfa69`, `fault.kind` drop-killagent). Model, decoding, task, app, luật kết quả, host và luật thứ tự trùng baseline; cấu hình xen kẽ như baseline; không guard nên không rút cờ người dùng.
- **Khác baseline về môi trường:** hai arm này chạy trên máy ảo RAM 4 GB (baseline và arm guard chạy 2 GB). Watchdog ANR của System UI vẫn chạy và ghi log.
- **Sửa:** `make_freeze.py` có lỗi thứ tự toán tử ở dòng chọn tên file output khi không có guard; đã sửa trước khi tạo freeze (file không thuộc code bị hash).
- **Chạy:** script nối tiếp T3A rồi kill-only trên nhánh `b/two-arms`, không đổi nhánh giữa chừng.

## 15/11/2026 (arm T3A: kết quả)

- **Kết quả:** 20 index cho 7 lượt hợp lệ nên chạy thêm index phụ 21 đến 23 theo luật freeze, đủ 10 lượt hợp lệ trên 23. Kết quả chính đã chốt trước (RESENT_DUPLICATE): 3/10 (30,0%, Wilson 95% từ 10,8 đến 60,3). Nhóm khác: RESENT_BUT_NO_DUP 6 (t02, t04, t06, t10, t16, t20), TASK_FAILURE 1 (t09, 20 bước sau khi chạy lại, không gửi, không báo xong).
- **Gửi lại:** T3A gửi lại ở 9/10 lượt hợp lệ (Wilson từ 59,6 đến 98,2). Ở cả 9 lượt, journal của proxy có thư thứ hai với Message-ID riêng, server trả 250 sau lúc agent khởi động lại. Ở 6 lượt RESENT_BUT_NO_DUP thư gửi lại dài 776 byte, thư có tag dài 791 byte (đúng 15 byte của `Lease gx:XXXXXX`): T3A để trống tiêu đề, nên luật đếm bản theo tag (IMAP `TEXT`) không tính. t04 và t06 cả thư gốc cũng không có tag (server có 0 bản có tag). Luật freeze vì vậy đếm thiếu bản trùng của T3A; bài báo nêu cả hai số.
- **Không hợp lệ:** 13 lượt original_not_committed (10/12 index không Sent, 3/11 index có Sent): T3A báo xong hoặc hết bước trước khi thư tới server. Đây là kỹ năng làm task của T3A, không phải harness (cùng harness, M3A hợp lệ 18/20).
- **Alias:** 0 lần đổi tên trong 825 lần gọi model (T3A tự viết `input_text`).
- **Emulator:** không có ANR, watchdog không chạm lần nào trong arm này (lần chạm cuối 02:59:08).
- **Kiểm:** gom 25 lượt (tdev-01, tdev-02, t01 đến t23) vào `artifact/results/real/agent_t3a/`; `check_agent_data.py --freeze` OK; gom lại vào thư mục tạm, giống hệt. `render_arm` thêm `\AgentTextResentN` và `\AgentTextResentNoDupN` (nhóm kết quả khác, thuộc phần phụ đã chốt), bảng `tab_agent_arms.tex` thêm cột Resent.

## 15/11/2026 (arm chỉ kill agent: kết quả)

- **Kết quả:** 20 index, 19 lượt hợp lệ, không dùng index phụ. RESENT_DUPLICATE 19/19 (100%, Wilson 95% từ 83,2 đến 100). So với M3A force-stop (17/18): Fisher exact hai phía p = 0,486, tức giữ K-9 sống (màn hình và Outbox còn nguyên, có thông báo lỗi gửi) không làm agent bớt gửi lại. 5 lượt (k08, k12, k14, k18, k20) agent gửi thêm hai lần, server có 3 bản có tag với 3 Message-ID. k17: agent báo xong trước khi thư tới server, INVALID original_not_committed.
- **Alias:** 54 trên 644 lần gọi model.
- **Emulator:** không có ANR (`dumpsys window lastanr`: chưa có ANR từ lúc khởi động 03:08), watchdog không chạm lần nào trong cả hai arm.
- **Kiểm:** gom 22 lượt (kdev-01, kdev-02, k01 đến k20) vào `artifact/results/real/agent_killagent/`; checker OK, gom lại vào thư mục tạm giống hệt; đếm lại độc lập từ `proxy.jsonl` và `RESULT.json` khớp. Bốn arm cũ (baseline, guard, rules, T3A) chạy lại checker vẫn OK.
- **Bài:** §7.8 thêm một câu cho T3A và kill-only (macro `\AgentText*`, `\AgentKill*`), bỏ "one agent" và "one fault" khỏi giới hạn; bảng 5 arm `tab_agent_arms.tex` để C quyết định đặt ở đâu (phụ lục).

## 15/11/2026 (đóng đợt chạy server)

- **Snapshot cuối:** `testbed/runs/aws-1114/server-snapshot-5.tgz` (không commit; sha256 `44eb47fc...15a11`): `/metrics` của vLLM, `nvidia-smi`, dòng GPU trong `dmesg` (không có Xid), `server.log`, `uptime`.
- **Đối chiếu:** vLLM 3.499 yêu cầu = 1.306 (hết arm guard) + 2.193 lệnh gọi model trong receipt của arm rules (597), T3A (896) và kill-only (700), tính cả lượt dev; 0 `length`, 0 `abort`, `server.log` không có dòng lỗi.
- **Laptop:** dừng watchdog ANR, giữ máy thức, tunnel SSH và emulator.
- **Server:** không còn việc nào cần server; báo trưởng nhóm có thể Stop (không Terminate, giữ đĩa tới 21/11).

## 15/11/2026 (§7.8: trả lại các mục YC-B6)

- Bản #48 lúc rút gọn đã bỏ host, số lượt hỏi hoặc dừng, số lượt thất bại và median thời gian, là các mục YC-B6 bắt buộc. Đã đưa lại cả bốn (`\AgentHost`, `\AgentAskedN`, `\AgentTaskFailN`, `\AgentWallMedS`).
- Danh sách giới hạn ghi "two agents and faults" thay cho "one agent" và "only force-stop" của YC-B6, vì arm T3A và arm chỉ kill agent đã gỡ hai giới hạn đó.
- `readability_count.py` trên `07-agent.tex`: PASS (không câu quá 45 từ, không đoạn nào quá một dấu chấm phẩy). Mục dài 34 dòng trong PDF (8 ở trang 11, 26 ở trang 12), khoảng 0,59 cột.

## 15/11/2026 (dọn việc B còn lại sau đợt chạy)

- **YC-B5, kiểm lại sau khi mọi arm chạy xong:** `runtime/vendor/` vẫn chỉ có `android_world_full`; `rev-parse HEAD` = `55ddaf5edc6f6c25673aed343907d5b9dca66f84`; `git diff` rỗng; `status --porcelain` vẫn đúng 4 file `*_pb2*.py` chưa theo dõi sinh lúc cài, như ghi ngày 14/11. Mọi sửa binding nằm trong `testbed/`.
- **YC-B12:** `check_agent_data.py` dòng 17 (regex phát hiện đường dẫn máy) bị `scrub_check.sh` báo `local-user-path` vì chứa chuỗi đó; viết lại thành `[/]`, nghĩa regex không đổi, test cũ vẫn bắt được đường dẫn Windows. `sh team/scrub_check.sh testbed/` giờ chỉ còn 26 dòng `email`, tất cả là địa chỉ tổng hợp `@test.invalid` mà luật ẩn danh cho phép; vẫn chờ C thêm ngoại lệ đó vào `scrub_check.sh` (review #12).
- **§2.3:** thêm một câu với kết quả T3A (`\AgentTextResentN` trên `\AgentTextValidN`), câu về device study giữ nguyên cho các agent và app khác. Không đổi bố cục trang (Conclusion vẫn ở dòng 1557, 22 trang); readability PASS.
- **Cần A, C:** A commit bản render lại `macros_guarantee.tex` (`\CertLabelMedS`, `\CertDeviceHoursFive` đang `??` trong file đã commit). C sửa ba câu nói bài không đo agent (§1 dòng 47, §7 dòng 7 và 101), quyết định chỗ đặt `tab_agent_arms.tex`, cho `make_bundle.sh` loại `testbed/README.vi.md` và `testbed/RUNBOOK_B.md`.

## 15/11/2026 (B-17: không làm)

- **Quyết định của trưởng nhóm (15/11):** bỏ B-17 (đo lại độ trễ Element bằng `run_case.py` có thêm kill -9 và netcut).
- **Lý do:** điều kiện của chính B-17 không còn (B-09 chạy ngày 14/11, không xong trước 13/11); dữ liệu B-17 nhắm tới đã có: Table 3b lấy độ trễ Element khi kill -9, cắt mạng và force-stop từ `c2_element_first_visible.csv` (101 lượt, 0 censored); B-17 chỉ là phép đo lặp bằng pipeline khác, không thêm kết quả mới, và không việc nào của A, C hay câu nào trong bài phụ thuộc vào nó.
- **Nếu reviewer hỏi về cách đo độ trễ Element:** B-17 làm được bằng emulator, không cần GPU.

## 18/11/2026 (rig K-9 trên điện thoại thật, không root)

- **Máy:** điện thoại cá nhân của trưởng nhóm, Samsung Galaxy A35 5G (SM-A356E), Android 15, One UI 7, bản thương mại không root, nối USB với adb của dự án (`-P 5038`). Serial không ghi vào file nào được commit.
- **Luật dùng máy (trưởng nhóm, 18/11):** chỉ đụng tới K-9; không đổi cài đặt hệ thống (Doze, pin, mạng, trợ năng); chỉ đọc màn hình khi K-9 ở trên cùng và lọc theo gói K-9; không đọc thông báo của app khác ra file. Các lệnh ép Doze hay giả rút sạc chưa chạy, chờ trưởng nhóm quyết khi có mặt.
- **Đã làm trên máy:** cài K-9 24.0 đúng hash trong `assets.lock.json`; đặt ngôn ngữ riêng của K-9 là en-US (`cmd locale set-app-locales`) để nhãn giống AVD; cấp quyền thông báo cho K-9; `adb reverse` cổng 14025 và 3143.
- **Code:**
  - `ui.ADB` nhận serial không phải `emulator-N` chỉ khi `GX_PHYSICAL_SERIAL` ghi đúng serial đó.
  - `k9_reset.reset_phone()`: `pm clear` K-9 rồi cài lại tài khoản qua màn hình đầu của K-9 (nhãn và id ghi lại trên máy). Trong lúc cài, cổng 14025 của máy trỏ thẳng GreenMail để K-9 kiểm được đăng nhập SMTP, xong thì trỏ về proxy như AVD. Không chạy lệnh xóa dịch vụ trợ năng của nhánh AVD.
  - `k9_fault_case.py` trên điện thoại: tìm nút theo nhãn; lỗi trước khi kill lấy từ thông báo của K-9; sau khi mở lại đọc Outbox trên màn hình; thay `k9_marked_error` (cần database) bằng `no_resend_after_relaunch` (proxy không thấy SMTP DATA nào sau lúc kill). Thêm `--kill background` (HOME rồi `am kill`, không hủy việc đã lên lịch như force-stop).
  - `collect_device_k9.py` gom kết quả vào `artifact/results/real/device_k9/`, không chép log `case/` vì có serial.
- **Dev t01 (sent, force-stop, không redo):** server 1 bản; trước khi kill K-9 hiện thông báo "Failed to send some messages" kèm "SmtpResponseParserException: Unexpected end of stream"; sau khi mở lại thư vẫn trong Outbox, 30 s không gửi lại. Khác AVD: sau force-stop thông báo mất, danh sách Outbox và màn hình thư không có dấu lỗi nào, nên trên điện thoại không kiểm được trạng thái `error` như database.
- **Dev t02 (INVALID, reset):** điều kiện "không có thông báo K-9" đếm cả bản ghi lưu trữ của thông báo đã gỡ. Sửa: chỉ đếm thông báo đang hiện (`NotificationRecord`), chờ tối đa 30 s cho thông báo đồng bộ lần đầu.
- **Dev t03 (INVALID):** chạy bằng code trước khi sửa t02, hỏng cùng chỗ.
- **Dev t04 (sent, force-stop) và t05 (nosent, HOME rồi `am kill`), quan sát 60 s, redo 60 s:** cả hai REPRODUCED 7/7; không SMTP DATA nào sau lúc kill; redo qua giao diện cho 2 bản trên server với 2 Message-ID khác nhau (trùng). Sau `am kill` thông báo lỗi của K-9 vẫn còn, sau force-stop thì mất.
- **Sửa nhỏ sau t05:** lúc đọc Outbox lần hai script bấm vào tiêu đề "Outbox" thay vì mục trong menu, menu còn mở; giờ bỏ qua bước điều hướng khi tiêu đề đã là Outbox.

### Kế hoạch đợt chính trên điện thoại (ghi trước khi chạy, 18/11)

- **Lượt:** s01 đến s20 kill bằng force-stop; b01 đến b10 kill bằng HOME rồi `am kill`. Cấu hình xen kẽ, số lẻ `sent`, số chẵn `nosent`. Chạy tuần tự s01 đến s20 rồi b01 đến b10.
- **Mỗi lượt:** `k9_fault_case.py --observe 120 --action recompose --action-window 60`: reset không root, soạn thư với nonce mới, proxy bỏ phản hồi SMTP sau khi server nhận DATA, chờ thông báo lỗi của K-9, kill, mở lại, quan sát 120 s, rồi soạn lại cùng tiêu đề và bấm Send như một agent làm lại bước đó, chờ 60 s.
- **Hợp lệ:** cả 7 điều kiện trước redo đều đạt (REPRODUCED). **Trùng:** sau redo server có 2 bản với 2 Message-ID khác nhau. Báo cáo số trùng trên số hợp lệ kèm khoảng Wilson 95%, theo cấu hình và theo cách kill.
- **Không thay lượt:** lượt INVALID giữ nguyên, ghi lý do. Chỉ dừng nếu máy mất kết nối adb; lượt dở dang (không có `RESULT.json`) thì chạy lại cùng tên và ghi vào đây.
- **Không chạy:** Doze, giả rút sạc, thiếu RAM thật (đụng tới cả máy); Element và DAVx5 (cần server Matrix, CalDAV và tải thêm).
- **Ghi chú đợt điện thoại:** s02 bắt đầu lúc 01:26:29, có thể đã nạp bản `k9_fault_case.py` có thêm hàm kill bằng thiếu RAM (chưa commit lúc đó). Hàm này không được gọi trên điện thoại, đường chạy của điện thoại giống hệt 7f9f286. Từ s03 checkout chính đã về đúng 7f9f286; việc mới làm trong worktree `P03-emu`, branch `b/emulator-faults`.

## 18/11/2026 (kết quả đợt điện thoại, 01:21 đến 04:17)

- **Tạm dừng theo yêu cầu trưởng nhóm** lúc 02:47 để dùng máy: s16 (đang chạy) và s17 (vừa bắt đầu) bị dừng, không có `RESULT.json`; giữ ở `testbed/runs/device-k9/interrupted-s16`, `interrupted-s17` (không commit). Chạy tiếp lúc 02:53 đúng như kế hoạch: chạy lại cùng tên. Không lượt nào khác bị thay.
- **Kết quả (30 lượt, `artifact/results/real/device_k9/`):** 30/30 hợp lệ (REPRODUCED đủ 7 điều kiện); 30/30 K-9 không gửi lại trong 120 s sau khi mở lại; 30/30 redo qua giao diện để lại bản trùng (2 bản trên server, 2 Message-ID), Wilson 95% từ 88.6 đến 100%. Theo cách kill: force-stop 20/20 (từ 83.9 đến 100% nếu gộp hai cấu hình), về nền rồi `am kill` 10/10.
- **Kiểm độc lập:** đếm lại từ `proxy.jsonl` từng lượt: đúng 2 SMTP DATA (thư gốc và redo), 2 Message-ID khác nhau, 1 lần bỏ phản hồi, 0 DATA sau lúc kill. Khớp `RESULT.json` cả 30 lượt.
- **Khác nhau giữa hai cách kill:** sau `am kill` thông báo lỗi của K-9 còn nguyên khi mở lại (10/10), sau force-stop thì mất (0/20). Thư vẫn nằm trong Outbox ở cả 30 lượt (đọc trên màn hình, đúng 1 mục mang nonce).
- **Ẩn danh:** serial máy không có trong artifact (grep 0 file); mọi địa chỉ là `@test.invalid` tổng hợp; log `case/` (có serial) để lại máy, không commit.
- **Ý nghĩa cho bài:** cái bẫy K-9 và bản trùng khi agent làm lại bước gửi tái hiện trên điện thoại thật (Android 15, One UI 7), không chỉ trên emulator (bảng campaign 2: 20/20 trên AVD). Kill kiểu hệ điều hành dọn app nền (`am kill`, không hủy việc đã lên lịch) cũng không làm K-9 tự gửi lại trong 120 s. Câu cho bài để C và trưởng nhóm quyết (§7.7 hoặc §8 "Android realism").

## 18/11/2026 (kế hoạch đợt emulator: thiếu RAM thật và Doze, ghi trước khi chạy)

- **Vì sao emulator:** trưởng nhóm chỉ có máy cá nhân; các lỗi này đụng tới cả máy (lấp RAM, ép Doze), nên làm trên AVD. Đã duyệt tải (18/11): DAVx5 4.5.21-ose và Etar 1.0.57 (F-Droid, hash khớp `assets.lock.json`), Radicale 3.9.0 từ PyPI vào `runtime/radicale-venv` (pip kéo 14 gói).
- **Chạy sau đợt điện thoại**, trên AVD `ghosteffect_api33_x86_local` (API 33, `-memory 4096`).
- **E1, K-9 bị lmkd giết:** `k9_fault_case.py --kill lmk --observe 120 --action recompose --action-window 60`; e01 đến e06 xen kẽ sent, nosent. `--kill lmk`: HOME rồi lấp một tmpfs 64 MB mỗi lần tới khi lmkd giết K-9 (phải có dòng `lowmemorykiller` nhắc K-9, không thì INVALID), rồi trả RAM.
- **E2, DAVx5 (`caldav_fault_case.py`, mới):** như C2-4 của campaign 2: Etar tạo sự kiện có tiêu đề là nonce, DAVx5 PUT lên Radicale qua proxy, proxy giữ phản hồi, áp lỗi lúc DAVx5 còn chờ, rồi bỏ phản hồi. Chấm từ store của Radicale (số bản mang nonce) và journal của proxy (thời điểm PUT lại cùng href). Ô: `none`, `kill9`, `lmk`, mỗi ô 3 lượt, cửa sổ 180 s; `doze` 3 lượt: tắt màn hình, giả rút sạc, ép deep idle trước khi bỏ phản hồi, giữ 600 s, rồi trả lại, cửa sổ 180 s.
- **Câu hỏi:** (1) lmkd giết K-9 thì K-9 có tự gửi lại không, redo có ra bản trùng không (H1 với kiểu kill thật); (2) DAVx5 có giữ đúng một bản khi bị lmkd giết (H3), và dưới Doze lần PUT lại bị hoãn bao lâu (độ trễ khi Doze, §8).
- **Không thay lượt;** lượt INVALID giữ, ghi lý do. Số nhỏ, đây là đo thăm dò cơ chế, không phải ước lượng tỷ lệ.

### Sửa kế hoạch đợt emulator sau các lượt dev (18/11, trước khi chạy đợt chính)

- **Dev:** dev-c01 (`none`): DAVx5 PUT lại cùng href 0,03 s sau khi mất phản hồi, 1 bản. dev-c02 (`kill9`): PUT lại 54 s sau khi kill, 1 bản (campaign 2: từ 53 đến 124 s). dev-c03 (`lmk`) và dev-e00 (K-9 `lmk`): INVALID, lấp 3,6 GB mà lmkd không giết app, vì AVD có 3 GB swap zram và số 0 nén gần hết. dev-d00 (`doze`, 120 s): lần retry tức thì trong phiên sync đang chạy vẫn đi qua lúc máy ở deep idle (8 ms sau khi bỏ phản hồi), 1 bản.
- **Sửa 1:** `lmk_kill` lấp bằng `/dev/urandom`, tối đa 6.000 MB. dev-e01 (K-9 `lmk`): lmkd giết K-9 ở 2.880 MB ("low watermark is breached and swap is low", oom_score_adj 700); REPRODUCED, không gửi lại, redo ra 2 bản.
- **Sửa 2:** ô Doze đổi thành `kill9-doze`: kill -9 DAVx5 lúc giữ phản hồi, rồi vào deep idle, giữ 600 s. Lý do: Doze chỉ có thể hoãn lần sync được lên lịch lại, không hoãn retry trong phiên đang chạy. dev-d01 (`kill9-doze`, giữ 300 s): DAVx5 vẫn PUT lại 51 s sau khi kill, lúc máy còn ở IDLE, 1 bản.
- **Đợt chính giữ nguyên phần còn lại:** e01 đến e06 (K-9 `lmk`), c01 đến c09 (`none`, `kill9`, `lmk` xen kẽ), d01 đến d03 (`kill9-doze`, 600 s), cửa sổ 180 s.

## 18/11/2026 (kết quả đợt emulator, 04:52 đến 06:32)

- **E1, K-9 bị lmkd giết (`artifact/results/real/emu_k9_lmk/`):** 6/6 hợp lệ; lmkd giết K-9 ở oom_score_adj 700 sau khi lấp khoảng 3.000 MB ("low watermark is breached and swap is low"); 6/6 không gửi lại trong 120 s; 6/6 redo qua giao diện ra 2 bản với 2 Message-ID (Wilson 95% từ 61.0 đến 100%). Database của K-9 ghi `error` cả 6 lượt (`k9_marked_error`). Kill thật bởi lmkd cho cùng kết quả với force-stop và `am kill`.
- **E2, DAVx5 (`artifact/results/real/emu_caldav/`):** 11/12 hợp lệ, cả 11 đúng một bản. Mỗi lượt có đúng 2 PUT cùng href: Radicale trả 201 rồi 412 (`If-None-Match: *`), như campaign 2. Độ trễ từ lỗi tới PUT lại: không lỗi 0,0 s (retry tức thì); kill -9 trung vị 52,5 s (từ 52,4 đến 54,1); lmkd 39,6 s (từ 39,5 đến 40,6; lmkd giết DAVx5 đang sync ở oom_score_adj 100); kill -9 rồi deep idle 50,9 s cả 3 lượt, lúc máy còn ở IDLE, 549 s trước khi thoát Doze.
- **c07 (INVALID):** không có PUT nào trong 90 s sau khi lưu sự kiện. Sự kiện (`gx:06D1EJ`) lên server muộn, đúng một bản, lúc c08 đang chờ máy sạch với proxy chưa bật bẫy; c08 chỉ bật bẫy khi lịch hết dòng dirty nên không bị ảnh hưởng. Có lẽ sync bị backoff sau lần sync hỏng ở c06 (lmkd). Không thay lượt.
- **Kiểm độc lập:** đếm lại từ `proxy.jsonl` và store của Radicale: mọi sự kiện trên server khớp đúng một lượt (kể cả dev và c07), không sự kiện nào có hai bản.
- **Về Doze:** trên AVD API 33, ép deep idle (màn hình tắt, giả rút sạc, `force-idle deep`, trạng thái IDLE) không làm lần sync lại của DAVx5 trễ hơn (50,9 s so với 52,5 s khi không Doze). Chưa rõ vì sao: các job WorkManager của DAVx5 chạy dưới uid của app (`dumpsys jobscheduler`), nên có thể lần PUT lại đến từ SyncManager của hệ thống chứ không phải job của app. Đây là AOSP trên emulator; trình quản lý pin của từng hãng có thể khác, chưa đo.
- **Ý nghĩa cho bài:** (1) H1: redo qua giao diện ra bản trùng với K-9 dưới cả bốn cách chết (force-stop, `am kill`, lmkd thật, cả trên điện thoại thật). (2) H3: DAVx5 giữ G2 dưới kill -9, lmkd thật và Doze; độ trễ phục hồi từ 39,5 đến 54,1 s, nằm trong khoảng campaign 2 đã đo (từ 53 đến 124 s khi kill) hoặc ngắn hơn. (3) Các độ trễ này không phải độ trễ hiển thị của §3 (sự kiện đã nằm trên server từ lần PUT đầu, 201), mà là thời gian mục chờ của DAVx5 còn treo (dòng dirty) trước khi app tự đối chiếu: thứ planner phải theo dõi ở hop 1. Không dùng chúng thay cho con số 13,6 s của Element ở §8. Câu trong bài để C và trưởng nhóm quyết.
- **Máy ảo sau đợt:** Doze và pin đã trả lại (`mState=ACTIVE`, `mForceIdle=false`); DAVx5, Etar và tài khoản alice còn trên AVD; Radicale và store ở `runtime/`.

## 18/11/2026 (PR nghiệm thu B)

- **Gộp trong ngày:** #65, #66 (đợt điện thoại và emulator), #67 (macro `\RealPhone*`, `\RealEmu*`; `tab_agent_arms.tex` thành `table*` vì tràn 49 pt khi #55 đặt vào phụ lục; dòng việc B-19 và C-20).
- **Sửa trong PR nghiệm thu:**
  - YC-10: bỏ "G2" khỏi văn xuôi của B (`07-real.tex` 4 chỗ, `fig1.tex` 3 chỗ trong hình và chú thích, `06-implementation.tex` 1 chỗ), viết thành "idempotent retries" như đề xuất C-02 (#61). Chữ "G2" chỉ còn trong comment của `fig1.tex`.
  - §6 đoạn agent harness: câu cũ ghi giết agent, lmkd và Doze là "planned". Thật ra arm chỉ giết agent chạy từ 15/11, lmkd và Doze chạy trên emulator ngày 18/11. Câu "app databases are read only by the grader" sai với arm rules (đọc thư mục K-9 chính xác), nay ghi rõ.
- **Kiểm trên worktree sạch từ `main` (29de0b7):** build 22 trang, không ô tràn quá 10 pt, không `??`; test artifact và testbed qua; YC-04 không số gõ tay; YC-12 file B: `\para` 4, `\emph` 9, 0 câu dài, 0 đoạn nhiều dấu chấm phẩy (trước và sau như nhau).
- **Chưa đạt, chờ người khác:** YC-09 và YC-B12, `scrub_check.sh` trên `main` còn báo 579 dòng, toàn là địa chỉ tổng hợp (`@test.invalid` và Message-ID `<uuid>@ghost.local`), đã kiểm không có địa chỉ nào khác; ngoại lệ nằm ở C-19 (#55, #56). YC-B10, nhánh G2 của Fig. 1 phải theo `team/QUYET_DINH_CHUNG.md`, file này chưa có trên `main` (#61 chờ trưởng nhóm chốt).
- **Việc B còn lại:** B-18 (dẫn `tab:agent-arms` ở §7.8, sau khi #55 gộp); bỏ "RQ7" ở `07-real.tex` và sửa chỗ dẫn ở §2 (sau khi #59 gộp).
- **YC-B10 sau khi #61 gộp (trưởng nhóm duyệt nguyên ngày 18/11):** khung nhánh idempotent của Fig. 1 ghi đúng quy tắc của `QUYET_DINH_CHUNG.md`: \sys không retry qua GUI, chờ có chứng nhận rồi "Sent" thì committed, không thì hỏi. Ô "Hop 1" rút còn "K-9's failed entry ..." vì câu dài ở #68 làm ô cao 5 dòng và đè lên nhãn (b) (đã xem ảnh trang 2). Build 22 trang, không ô tràn mới.

## 18/11/2026 (điện thoại thuê trên AWS Device Farm: lượt thử và kế hoạch đợt DAVx5, ghi trước khi chạy)

- **Quyền:** trưởng nhóm cấp AWS Device Farm (us-west-2), chỉ dùng lệnh `aws devicefarm`, tối đa 300 phút cho việc này, mỗi lượt tối đa 150 phút, xong phải dừng ngay. Máy thuê không root, bị xóa sạch sau mỗi lượt, không có dữ liệu cá nhân, nên được ép Doze và đổi cài đặt.
- **Rig (`testbed/devicefarm/`):** kiểu test APPIUM_PYTHON với test spec tự viết, Appium không dùng. Host Amazon Linux 2023, Java 17, Python 3.12, có `adb` và internet. GreenMail, Radicale và fault proxy chạy trên host, điện thoại tới host qua `adb reverse`. `df.py` upload, lên lịch, chờ, tải artifact và ghi số phút.
- **Lượt thử p01 (Samsung Galaxy A36 SM-A366U1, Android 15, One UI 7, 7,71 phút máy):**
  - Đọc được không cần root: `curProcState`, `isFrozen` của activity manager, `frozen 0/1` trong cgroup của process, `/proc/<pid>/status`, trạng thái deep idle.
  - Freezer: Samsung tắt (`use_freezer=false`). `am freeze` báo đã freeze nhưng `isFrozen` và cgroup vẫn 0.
  - Giết app không root: `kill -9` bị từ chối (Operation not permitted). `am kill`, `am crash`, `am stop-app` và `am force-stop` đều làm process chết. Help của Android ghi `stop-app` "không hủy alarm và job đã lên lịch", nên `stop-app` thay cho `kill -9`.
  - Doze: giả rút sạc, tắt màn hình, `deviceidle force-idle deep` cho IDLE; thoát thì về ACTIVE.
  - K-9 dev p01, rig điện thoại không sửa dòng nào: REPRODUCED, mọi kiểm đạt, K-9 không gửi lại, redo ra 2 bản với 2 Message-ID, như trên máy cá nhân. Vì vậy không chạy lại 30 lượt K-9: cùng code, lượt kiểm cho cùng kết quả.
- **Kiểm trên AVD (không tính):** DAVx5 cài lại từ đầu bằng `davx5_setup.py`. `stop-app`: đúng một bản, PUT lại sau 52,7 s (`kill -9` trên AVD: 52,5 s). `stop-app-doze` với Doze 60 s: đúng một bản, PUT lại sau 50,1 s, lúc máy còn IDLE. Hai lỗi rig sửa trên đường: `adb root` trên AVD xóa `adb reverse` (chỉ AVD); DAVx5 giữ kết nối từ lúc cài, nên sau khi đổi cổng phải `am stop-app` một lần.
- **Kế hoạch đợt chính (ghi trước khi chạy):**
  - Máy: R1 Samsung Galaxy A36, Android 15 (One UI, freezer tắt); sau đó R2 Google Pixel 9, Android 15 (AOSP). R2 chỉ chạy khi R1 không lộ lỗi rig; nếu lộ thì sửa, ghi lại ở đây rồi chạy lại R1.
  - Mỗi máy, thứ tự cố định: dev-c00 none (dev, không tính); c01 none, c02 stop-app, c03 none, c04 stop-app, c05 none, c06 stop-app; d01 đến d03 stop-app-doze, giữ deep idle 600 s. Cửa sổ 180 s, barrier 90 s. Lượt INVALID không thay.
  - Chấm như E2 trên AVD: số bản mang nonce trong store của Radicale; thời gian từ lỗi tới lần PUT lại cùng href (journal của proxy); với Doze, PUT lại lúc IDLE hay sau khi thoát. Mẫu process mỗi 10 s: procstate, `isFrozen`, cgroup frozen, trạng thái deep idle.
  - Câu hỏi: (1) DAVx5 có giữ đúng một bản trên điện thoại thật khi bị `stop-app` và Doze (H3); (2) Doze ép trên điện thoại thật (One UI và AOSP) có hoãn lần sync lại không, khác AVD; (3) process DAVx5 có bị freezer đóng băng lúc chờ không.
  - Ngân sách: mỗi lượt khoảng 80 phút, timeout 110 phút. Tổng tối đa 7,5 + 2 × 110 = 227,5 phút, dưới 300.
- **Sổ phút (trialMinutes.remaining):** trước 995,88; sau p01 988,37 (dùng 7,51).
- **R1 lần đầu hỏng rig, chưa có lượt nào (1,61 phút máy, dùng 1,20; còn 987,17):** Python 3.12 của host không có `ensurepip` nên `python3 -m venv` hỏng và Radicale không chạy; trên A36 bàn phím tự mở ở ô URL nên ô User name không được dựng (danh sách Compose). Sửa: Radicale cài bằng `pip install --target` và `PYTHONPATH`; `davx5_setup.py` ẩn bàn phím sau khi mở màn hình đăng nhập và cuộn khi không thấy nhãn. Chạy lại R1 nguyên kế hoạch (caldav-r1b).
- **R1b hỏng rig (9,24 phút máy, dùng 8,85; còn 978,32):** cài DAVx5 và Radicale chạy; dev-c00 (none) đúng một bản, PUT lại sau 0,014 s. Cả 9 lượt chính sau đó INVALID sau khoảng 26 s mỗi lượt: không thấy nút DONE của Etar. Lượt đầu bấm được nên đây là lỗi rig trên A36, không phải kết quả; không tính lượt nào của R1b. Logcat của Device Farm chỉ giữ đoạn cuối nên chưa biết màn hình lúc đó. Sửa: đầu mỗi lượt đánh thức máy và bỏ khóa màn hình; khi không thấy DONE thì lưu dump màn hình cùng trạng thái nguồn và cửa sổ. Hai lượt liền nhau trên AVD vẫn đúng.
- **Sửa kế hoạch trước R1c (ghi trước khi chạy):** thêm dev-c01 (none) ngay sau dev-c00 để thử hai lượt liền nhau trước các lượt chính. Quy tắc dừng: một lượt dev INVALID, hoặc hai lượt chính INVALID liên tiếp, thì dừng cả đợt (lỗi rig, giữ dump), không chạy tiếp cho tốn phút. Phần còn lại của kế hoạch giữ nguyên.
- **R1c dừng theo quy tắc (5,72 phút máy, dùng 6,04; còn 972,28):** dev-c00 đúng một bản (PUT lại sau 0,017 s); dev-c01 không thấy DONE nên dừng, chưa chạy lượt chính nào. Dump lúc lỗi: máy thức, không khóa, cửa sổ trên cùng là Cài đặt "Alarms & reminders" với Etar đang Off. Sau khi lưu sự kiện đầu (có nhắc giờ), Etar trên Android 15 mở trang xin quyền báo thức chính xác (`SCHEDULE_EXACT_ALARM`); `install -g` chỉ cấp quyền runtime nên không cấp quyền này, AVD API 33 thì có sẵn. Sửa: `campaign_caldav.sh` chạy `appops set ws.xsoh.etar SCHEDULE_EXACT_ALARM allow` sau khi cài và ghi lại giá trị. Chưa chạy lại.
- **Tạm dừng 18/11 17:00 theo yêu cầu của trưởng nhóm.** Phút máy của các run của B (`deviceMinutes.total` của từng run): p01 7,71; R1 lần đầu 1,61; R1b 9,24; R1c 5,72; cộng 24,28 (metered 22,69), trên giới hạn 300. Quỹ dùng thử giảm 23,60 trong cùng khoảng, nhưng số này có thể lẫn phút của người khác: project còn hai run `p06-B0` (15:57 và 16:56) không phải của B, B không đụng vào. Từ nay sổ phút lấy `deviceMinutes` của từng run. Khi làm tiếp: chạy lại R1 trên A36 với bản sửa (R1d, kế hoạch như trên), rồi R2 trên Pixel 9. Chưa có kết quả DAVx5 nào trên điện thoại thật để báo.
- **Làm tiếp 18/11 tối:** R1d bắt đầu 22:12 trên A36 (gói có bản sửa `appops`). Sau 38 phút run chưa dừng theo quy tắc, tức hai lượt dev đã qua. **Đổi thứ tự (ghi trước khi chạy R2):** trưởng nhóm cho chạy R2 trên Pixel 9 song song với R1d chỉ để bớt thời gian chờ. Lịch, số lượt, cách chấm và quy tắc dừng của R2 giữ nguyên như kế hoạch; không thêm máy hay lượt nào.
- **Kết quả R1d (Galaxy A36 SM-A366U1, Android 15, One UI 7, bản build khác máy ở lượt thử; 51,59 phút máy, metered 51,19):**
  - `etar exact alarm: allow` sau khi cài; hai lượt dev đúng một bản (PUT lại sau 0,018 và 0,023 s).
  - none (c01, c03, c05): 3/3 đúng một bản, PUT lại ngay (0,024; 0,025; 0,024 s), như AVD.
  - stop-app (c02, c04, c06): 3/3 đúng một bản; PUT lại sau 29,9; 30,0; 39,0 s (AVD với `kill -9`: trung vị 52,5 s). DAVx5 tự khởi động lại trong 10 s sau `stop-app`.
  - stop-app-doze d01: đúng một bản trên server khi chấm, nhưng **không có lần PUT lại nào**: suốt 600 s deep IDLE và 180 s sau khi thoát. Sự kiện vẫn dirty trên máy lúc d03 bỏ cuộc, tức 1.028 s sau lỗi, 427 s sau khi thoát Doze. Trên AVD, cùng ô này PUT lại sau khoảng 51 s, lúc máy còn IDLE.
  - d02, d03: INVALID vì sự kiện của d01 vẫn dirty nên không có điểm bắt đầu sạch; quy tắc dừng cắt run. Ô stop-app-doze chỉ có 1 lượt hợp lệ.
  - Mẫu process: máy này báo `use_freezer=true`, nhưng không mẫu nào thấy DAVx5 bị đóng băng (`isFrozen=false`, cgroup 0); procstate luôn 19 sau khi app khởi động lại.
  - Cách đọc: trên A36 thật, Doze cộng việc app bị dừng làm lần gửi lại bị hoãn ít nhất 17 phút, khác hẳn AVD. Chưa đủ để nói hoãn bao lâu (chưa thấy lần PUT lại) và vì sao (Doze, nhóm standby của Samsung hay backoff của WorkManager). Một lượt hợp lệ, chỉ là quan sát.
- **Kết quả R2 (Google Pixel 9, Android 15, bản build BP1A.250505.005; 73,89 phút máy, metered 73,52):**
  - `etar exact alarm: allow`; hai lượt dev đúng một bản (PUT lại sau 0,017 và 0,045 s). Không lượt nào INVALID, chạy đủ 11 lượt.
  - none (c01, c03, c05): 3/3 đúng một bản, PUT lại ngay (0,018; 0,029; 0,023 s).
  - stop-app (c02, c04, c06): 3/3 đúng một bản; PUT lại sau 42,0; 52,7; 52,7 s (AVD với `kill -9`: trung vị 52,5 s).
  - stop-app-doze (d01 đến d03): 3/3 đúng một bản; PUT lại sau 27,2; 27,4; 27,4 s, lúc máy còn deep IDLE (573 s trước khi thoát ép), như AVD (khoảng 51 s, còn IDLE).
  - Mẫu process: máy này cũng báo `use_freezer=false`; không mẫu nào đóng băng. Procstate thấy: 6, 8, 19.
  - Cách đọc: trên Pixel 9 (AOSP), Doze ép không hoãn lần sync lại của DAVx5; trên A36 (One UI) thì hoãn ít nhất 17 phút ở lượt hợp lệ duy nhất. Cả hai máy giữ đúng một bản ở mọi lượt hợp lệ (H3). Câu hỏi (3) về freezer chưa trả lời được: Pixel tắt freezer, A36 bật nhưng không đóng băng DAVx5 lúc chờ.
- **Sổ phút sau R1d và R2:** R1d 51,59; R2 73,89. Tổng các run của B: 24,28 + 51,59 + 73,89 = 149,76, trên giới hạn 300. Không còn run nào của B đang chạy.
- **19/11: đưa kết quả máy thuê vào artifact (không chạy thêm).** Trưởng nhóm quyết giữ nguyên số liệu, không chạy lại ô Doze của A36. `collect_caldav.py --title` gom R1d vào `artifact/results/real/device_caldav_a36/` và R2 vào `device_caldav_pixel9/` (trials.csv, receipts, SUMMARY.md, `device.txt` và `batch.txt` (batch.log của run, đổi tên vì `.gitignore` bỏ `*.log`); không có serial hay đường dẫn máy, scrub check PASS). Hai máy để riêng, không gộp số. `render_real.py` sinh `\RealRentSam*` và `\RealRentPix*` (N, ValidN, OnceN, StopN/StopMedS, DozeN, DozeMedS khi có), `\RealRentAndroid` và `\RealRentSamDozeQuietS` (1{,}028 s, tính từ receipt d01 và dòng d03 trong batch.txt); assert giữ hai điều câu văn sẽ nói: Pixel gửi lại khi còn deep IDLE, d01 của A36 không gửi lại và vẫn dirty. `\RealDataLimitation` sửa thành: máy thật chạy K-9 và DAVx5, không có agent; hai máy thuê không root nên `am stop-app` thay `kill -9` và không thử `lmkd`. Câu trong §7 do C viết (quyết định mục 2); câu "after `kill -9` or force-stop" chỉ đúng cho số emulator.
- **19/11: chỗ dẫn sau #55 và #59 (B-18, việc chờ C).** `07-real.tex` bỏ "RQ7" ở tiêu đề (§7 không còn đánh số RQ sau #59); `07-agent.tex` bỏ "(RQ3)", dẫn sang Appendix~\ref{app:extra} nơi định nghĩa same-evidence rules, và thêm câu dẫn Table `tab:agent-arms` (C đặt bảng ở phụ lục, C-17); §2 (`02-background-motivation.tex`) không còn gọi là "planned device study" mà ghi là việc tương lai, vẫn trỏ `sec:device-plan` (đoạn Study scope của §7). Build thoát 0, 24 trang, không `??`; readability các file của B 4/9/0/0.

## 19/11 chiều: thí nghiệm polish TN1 đến TN3 (chỉ trên nhánh local `local/exp-polish`, chưa đưa lên `main`)

- **Bối cảnh:** sau lượt chấm thử MobiSys (lane C, 3 giám khảo đều 2 điểm), trưởng nhóm cho làm ba thí nghiệm, chỉ commit trên máy trưởng nhóm, đưa lên bản chính sau 22/11. TN1: kiểm chứng held-out của planner thật trên app thật (CalDAV, vì máy này không có Element và Synapse). TN2: thêm lượt Doze trên A36. TN3: đo ledger trên điện thoại. Không thí nghiệm nào đổi số liệu đã có trên `main`.
- **TN3, kế hoạch (ghi trước khi chạy):** APK `testbed/phone_ledger` (không Gradle; `build.sh`; sha256 b2559532...c84c) chạy ledger của `artifact/scripts/ledger.py` trên SQLite của Android trong bộ nhớ riêng của app. (1) Độ trễ `issue()` (một transaction `BEGIN IMMEDIATE`, WAL, `synchronous=FULL`, đọc lại PRAGMA để xác nhận) trên 2.000 effect, hai lần; một lần `NORMAL` chỉ để tham khảo; byte mỗi effect sau `wal_checkpoint(TRUNCATE)`. (2) 100 lượt kill: writer lặp plan, issue, ghi TAP vào file riêng, settle; harness chờ tap đầu, rồi `am force-stop` (SIGKILL) sau khoảng ngẫu nhiên 0,05 đến 0,25 s (seed 7); kiểm mọi id đã TAP là ISSUED hoặc COMMITTED. Đây là chết process, không phải mất điện, như phép thử trên host. Máy: Galaxy A36 và Pixel 9 (hai máy đã thuê ở R1d, R2). Kiểm trên AVD (không tính): p50 0,98 ms, p95 3,2 ms, 209 byte mỗi effect, 5 lượt kill 339 tap 0 vi phạm.
- **TN2, kế hoạch (ghi trước khi chạy):** chỉ A36, cùng rig và quy trình của R1d (`campaign_tn.sh ledger+doze`, chạy sau TN3 trên cùng máy): dev-c00 none (dev, không tính), rồi e01, e02 stop-app-doze, giữ deep idle 600 s như d01. Khác R1d ở cửa sổ quan sát: tối đa 1.800 s sau khi thoát Doze, dừng 20 s sau lần PUT lại cùng href; nếu hết cửa sổ mà chưa PUT lại thì mở DAVx5 một lần trong 90 s (ghi riêng lần PUT sau khi mở) để máy sạch cho lượt sau. Ghi thêm standby bucket của DAVx5 lúc lỗi và cuối cửa sổ, cùng `dumpsys jobscheduler` của DAVx5. Lượt INVALID không thay; quy tắc dừng như R1d. Câu hỏi: trên One UI, lần gửi lại của DAVx5 bị hoãn bao lâu (d01 của R1d: chưa gửi lại sau 1.028 s), và có cần người dùng mở app không. Kiểm trên AVD (không tính): Doze 30 s, PUT lại sau 31,1 s (0,9 s sau khi thoát), đúng một bản.
- **Ngân sách Device Farm:** B đã dùng 149,76 trên giới hạn 300, còn 150,24. A36: timeout 110 phút (ước 96: cài đặt khoảng 5, TN3 khoảng 6, dev 1, e01 và e02 mỗi lượt tối đa khoảng 42). Pixel 9: timeout 20 phút (chỉ TN3). Tối đa 130 phút, dưới 150,24. Sổ phút ghi theo `deviceMinutes.total` của từng run.
- **Sửa rig (AVD):** `caldav_fault_case.py` gọi `adb root` sau khi AVD khởi động lại, và lệnh này xóa `adb reverse` mà DAVx5 dùng (127.0.0.1:5233); nay đặt lại reverse ngay sau `adb root`. Lượt dev đầu trên AVD (tn2-avd-dev1) INVALID vì lỗi này.
- **TN3, kết quả Pixel 9 (run tn-pixel9-android15, 2,74 phút máy, metered 2,38):** `synchronous=FULL` xác nhận bằng PRAGMA; `issue()` p50 0,323 và 0,476 ms, p95 0,727 và 0,754 ms (hai lần), 209 byte mỗi effect; 100 lượt kill, 27.646 tap được kiểm, 0 vi phạm thứ tự ghi, 41 ứng viên ghost, writer chết hẳn ở cả 100 lượt. A36 đang chạy (TN3 rồi TN2).
- **TN1, kế hoạch (ghi trước khi chạy; trưởng nhóm chọn CalDAV bản đầy đủ):** `testbed/caldav_planner.py` trên AVD.
  - Effect: tạo trong Etar một event có tiêu đề là nonce mới, DAVx5 đồng bộ lên Radicale. X=1: bấm DONE, DAVx5 PUT, Radicale commit, proxy giữ phản hồi, lỗi xảy ra, phản hồi bị bỏ. X=0: màn hình soạn đã mở và điền tiêu đề, lỗi xảy ra trước DONE (kiểm trên AVD: Etar không tự lưu bản nháp khi bị đẩy xuống nền, bị kill hay force-stop).
  - Lớp lỗi (áp lên cả Etar và DAVx5): none, app-kill (`kill -9`), force-stop.
  - Planner thật (`recovery.py`, Algorithm 1) chỉ đọc giao diện Etar. Họ hop1 (kho cục bộ của app, hiện từ lúc bấm DONE) có hai view: search (tìm nonce) và agenda (event đặt 2 giờ sau thời điểm tạo). Mỗi lần đọc mở lại Etar (`am start -S`).
  - Không có view giao diện nào cho biết chặng hai đã được xác nhận: DAVx5 không hiện trạng thái từng event hay giờ đồng bộ, trang Account sync của Android không liệt kê adapter của nó. Vì vậy stratum khai G2 không dùng được: effect đã commit không chứng nhận được và phải hỏi; effect vắng mặt chứng nhận được từ hop1 rồi retry.
  - Kho: chế độ product (một họ nên A2 không có nội dung), α = β = 0,1, calibration theo 3 lớp. Mỗi lớp 133 effect X=1 (đúng mức tối thiểu không lỗi để chứng nhận phía retry ở α = 0,1: K = 9, δ = 1,11e-3) và 30 effect X=0. X=0 chỉ vào cận phía commit, mà phía này không dùng được khi không có monitor. Tổng 489 lượt, thứ tự trộn theo seed 20261119 (`testbed/tn1/schedule_calibration.json`). Spec đóng băng ở `testbed/tn1/tn1_spec.json`; domain gồm hash của reader và của `recovery.py`, đổi code là đổi domain.
  - Test held-out chạy sau khi kho đã biên dịch và commit: mỗi lớp 40 X=1 và 40 X=0, tổng 240, seed 20261120. Planner ra quyết định và quyết định được thực thi: RETRY thì agent soạn lại cùng event qua giao diện, rồi đếm số bản trên server.
  - Lượt INVALID (lỗi rig: không thấy DONE, quá hạn barrier, X dự định khác X trên server) giữ trên đĩa, chạy bù ở cuối hàng đợi, không bao giờ loại một nhãn hợp lệ; tối đa 60 lần bù rồi dừng.
  - Báo cáo: số quyết định theo lớp và outcome; số lần retry effect đã commit (kèm cận CP); số retry được chứng nhận của effect vắng mặt; tỉ lệ hỏi; số bản trên server sau khi làm lại. Giữa các lượt, rig xóa event thử ở cả hai phía (xóa với quyền sync adapter, không để lại cờ dirty, và xóa .ics trên Radicale).
  - Thời gian ước tính: một lượt X=1 khoảng 70 s (sync manager của Android hoãn upload khoảng 55 s sau khi bấm DONE), một lượt X=0 khoảng 27 s; calibration khoảng 8,5 giờ, test khoảng 5 giờ.
  - Kiểm trước khi chạy (không tính): 6 lượt dev cho nhãn đúng cả 6; 2 lượt chạy qua planner với kho dev (1 nhãn mỗi ô) đều ASK `not_certifiable`, như dự kiến.
- **Kết quả A36 (run tn-a36-android15, 27,34 phút máy, metered 26,94; cùng model SM-A366U1 và bản build AP3A.240905.015.A2.A366U1UEU1AYBB như R1d):**
  - TN3: `issue()` p50 0,261 và 0,255 ms, p95 0,395 và 0,358 ms, 225 byte mỗi effect (SQLite 3.44.3); 100 lượt kill, 42.662 tap được kiểm, 0 vi phạm, 34 ứng viên ghost, writer chết hẳn ở cả 100 lượt.
  - TN2: dev-c00 none đúng một bản (PUT lại sau 0,027 s). e01 và e02 (stop-app-doze, deep IDLE 600 s): cả hai đúng một bản, DAVx5 PUT lại sau 27,70 và 27,63 s, lúc máy vẫn deep IDLE. Không lượt nào cần mở app. Standby bucket không đọc được (lệnh trả rỗng trên One UI).
  - Khác R1d: lần này máy báo `use_freezer=false`; ở R1d máy báo `use_freezer=true` và d01 không PUT lại trong 1.028 s. Ô stop-app-doze của A36 giờ có 3 lượt hợp lệ: 2 lượt gửi lại sau khoảng 27,6 s (freezer tắt), 1 lượt bị hoãn ít nhất 1.028 s (freezer bật). Chưa đủ để nói freezer là nguyên nhân (một lượt, có thể là máy vật lý khác cùng model); chỉ nói được là độ trễ trên cùng model không ổn định.
  - Gom vào `artifact/results/real/phone_ledger/{a36,pixel9}/` và `artifact/results/real/device_caldav_a36_tn2/` (collect_caldav.py; scrub PASS). Chưa render macro hay sửa bài: việc đó để sau 22/11.
- **Sổ phút Device Farm sau TN2, TN3:** tn-pixel9 2,74; tn-a36 27,34. Tổng các run của B: 149,76 + 2,74 + 27,34 = 179,84, trên giới hạn 300 (còn 120,16). Không còn run nào của B đang chạy.
- **TN1, sự cố rig lúc 16:19 (calibration đang chạy):** c0121 (X=1) INVALID vì DAVx5 không PUT trong 90 s sau khi bấm DONE. Bẫy proxy của lượt đó không được gỡ (faultproxy chỉ gỡ bẫy đã chạm barrier), nên mọi lượt X=1 sau đó hỏng ngay ở bước đặt bẫy (HTTP 400): 13 lượt INVALID (c0121 đến c0123 và c0126 đến c0135; c0124, c0125 là X=0 nên chạy bình thường), đều chạy bù ở cuối hàng đợi theo quy tắc đã ghi. Lượt X=0 không bị ảnh hưởng. Sửa không đụng `caldav_planner.py` (hash của file này nằm trong domain đã đóng băng): thêm `testbed/tn1_arm_watchdog.py` chạy cạnh collector; bẫy nào quá 150 s chưa được gỡ thì watchdog gửi một PUT giả (sự kiện `gx-rig-clear`) qua proxy cho bẫy chạm barrier, rồi gỡ với `observed_class=none` và ghi chú rig vào journal. Sự kiện giả bị bước dọn của lượt sau xóa. Bẫy kẹt được gỡ lúc 16:22:00; các lượt sau chạy lại bình thường. Không lượt hợp lệ nào bị loại hay sửa nhãn.
- **TN1, sự cố thứ hai lúc 16:28 và chỉnh watchdog:** c0143 (X=1) lại INVALID vì không có PUT trong 90 s. Sync manager của Android ghi một lần sync upload lúc 16:29:01 kéo dài 60,1 s, nhưng Radicale không nhận request nào trong khoảng đó, nên nghi request của DAVx5 bị treo trên đường `adb reverse` (giả thuyết, chưa kiểm). Bẫy kẹt được watchdog gỡ lúc 16:30:28; trong lúc chờ có thêm 6 lượt hỏng ở bước đặt bẫy. Tổng INVALID tới lúc này: 20, đều chạy bù. Watchdog chỉnh lại: gỡ bẫy quá 95 s (barrier là 90 s) và kiểm mỗi 2 s thay vì 150 s và 10 s, để mỗi sự cố chỉ kéo theo khoảng 2 đến 3 lượt hỏng. Nếu số lần bù chạm giới hạn 60 thì collector dừng; khi đó chạy lại cùng lệnh, vì collector bỏ qua các lượt đã xong, và ghi lại ở đây.
- **TN1, lỗi của chính watchdog lúc 16:41 (đã sửa):** ngưỡng 95 s quá sát. Một lượt X=1 còn sống có thể chờ tới khoảng 116 s kể từ lúc đặt bẫy (mở màn soạn khoảng 6 s, tìm DONE tối đa 20 s, rồi barrier 90 s). Watchdog đã gỡ bẫy của c0162 khi lượt này còn đang chờ: PUT giả chạm barrier, lượt c0162 tưởng effect đã commit, rồi tự bắt lỗi ở bước kiểm server ("intended outcome 1 but 0 server copies") và thành INVALID. Không nhãn sai nào lọt vào. Sửa: watchdog chỉ gỡ một bẫy chưa gỡ sau khi collector đã ghi một lượt INVALID ít nhất 1 s sau lúc đặt bẫy, tức lượt sở hữu bẫy đã bỏ cuộc; lượt kế tiếp đặt bẫy muộn hơn dòng đó ít nhất 2 s, nên không có lượt sống nào bị gỡ. Kiểu sự cố quan sát được: cả ba lần quá hạn (c0121, c0143, c0160) đều ngay sau hai lượt X=1 liên tiếp mà DAVx5 bị kill hoặc force-stop giữa lúc sync; giả thuyết là sync manager giãn thời gian chờ sau các lần sync bị giết. Tổng INVALID tới lúc này: 22.
- **TN1, nguyên nhân các lần quá hạn và cách xử lý (16:45):** `dumpsys jobscheduler` cho thấy cả job sync của tài khoản lẫn các job WorkManager của DAVx5 đều chờ `TIMING_DELAY` (backoff), và các lần sync upload gần đây chạy đủ 60 s rồi bị hủy. Mỗi lượt X=1 lớp app-kill hay force-stop giết DAVx5 giữa lúc upload, nên backoff tăng dần; quá hạn dày dần (sau 22, 17 rồi 4 lượt). Thêm `testbed/tn1_sync_flush.py` chạy cạnh collector: mỗi khi batch.log có dòng mới, nó chạy `cmd jobscheduler run -f` cho mọi job đã lên lịch của DAVx5, để lượt sau bắt đầu không mang backoff tích lũy. Helper chạy trước khi lượt sau đặt bẫy và lưu event, không đụng event hay Etar, không đổi `caldav_planner.py`; đọc hop1 là kho cục bộ của Etar, không phụ thuộc lúc DAVx5 upload. Áp dụng từ c0165 cho mọi lượt còn lại của calibration và cho toàn bộ đợt test. Tới lúc này: 145 lượt hợp lệ, 23 INVALID.
- **TN1, helper chạy liên tục (từ 16:52):** `tn1_sync_flush.py` đổi sang mỗi giây kiểm job của DAVx5 và ép chạy ngay job sync của tài khoản (uid 1000) cùng các job WorkManager có độ trễ dưới 10 phút, mỗi job id một lần. Việc này bỏ được khoảng 55 s sync manager hoãn upload: mỗi lượt X=1 còn khoảng 20 đến 30 s, thay vì khoảng 71 s. Không bỏ được backoff riêng của WorkManager: ép job sớm thì WorkManager tự hoãn tiếp ("executed before schedule"), nên sau hai lượt kill liên tiếp vẫn có lượt quá hạn, khoảng 1 trên 9 lượt X=1 (c0171, c0172, c0182), mỗi lượt tốn 90 s rồi chạy bù. Nếu chạm giới hạn 60 lần bù thì chạy lại collector cùng lệnh.
- **19/11 17:07: tạm dừng TN1 theo yêu cầu của trưởng nhóm.** Calibration dừng sau khi c0193 xong: 166/489 lượt hợp lệ trong `effects.jsonl`, 28 INVALID (đều chờ chạy bù), chưa lần đọc nào sai (X=1 luôn [1, 1], X=0 luôn [0, 0]). Lượt c0194 vừa bắt đầu (thư mục rỗng) đã được xóa để chạy lại bình thường. Đã dừng collector, watchdog, helper job, Radicale và emulator. Dữ liệu ở `testbed/runs/tn1-calibration/` (thư mục bị git bỏ qua, nằm trong checkout chính qua junction).
  - **Chạy tiếp:** bật AVD theo RUNBOOK mục 6; từ worktree `P03-exp` chạy lại đúng lệnh `python testbed/caldav_planner.py collect --schedule testbed/tn1/schedule_calibration.json --out testbed/runs/tn1-calibration --adb <adb>` (collector bỏ qua lượt đã có RESULT.json, tự dựng Radicale, proxy, `adb root` và reverse), cùng hai helper `tn1_arm_watchdog.py --run testbed/runs/tn1-calibration` và `tn1_sync_flush.py --run testbed/runs/tn1-calibration --adb <adb>`. Không sửa `caldav_planner.py` hay `recovery.py` (hash nằm trong domain đã đóng băng). Xong calibration thì biên dịch kho bằng `calibration.py --spec testbed/tn1/tn1_spec.json`, commit kho, rồi chạy đợt test với `--store` và hai helper trỏ vào thư mục test.
- **20/11 00:40: chạy tiếp TN1 theo yêu cầu của trưởng nhóm.** Hash domain vẫn khớp spec. AVD khởi động lạnh, System UI báo ANR liên tục (máy ảo 2 GB); bấm "Close app" để System UI khởi động lại thì ổn định, không đổi cấu hình AVD. Collector chạy lại đúng lệnh cũ; nó chạy bù các lượt INVALID theo thứ tự lịch (c0121 trở đi) rồi mới tới c0194.
- **Sự cố do helper (00:43 đến 00:55):** bảy lượt X=1 liên tiếp quá hạn (c0121, c0122, c0123, c0127 đến c0130). `dumpsys jobscheduler` cho thấy job sync của tài khoản bị chặn thêm `WITHIN_QUOTA`: helper đã ép chạy job WorkManager của DAVx5 hàng trăm lần (vô ích, vì WorkManager tự hoãn lại), làm DAVx5 hết hạn mức job. Sửa `tn1_sync_flush.py`: chỉ ép job sync của tài khoản (uid 1000), mỗi job id một lần, bỏ hẳn phần ép job WorkManager. Sau khoảng 10 phút hạn mức hồi lại; từ c0131 các lượt chạy bình thường (c0132: 31 s). Lệnh đặt lại hạn mức không có trên API 33; bucket của DAVx5 vẫn là active (10). Nhãn không bị ảnh hưởng (lượt quá hạn là INVALID và được chạy bù).
- **20/11 02:50: backoff của WorkManager (không sửa, để tự hồi).** Lại có chuỗi lượt X=1 quá hạn (c0366 đến c0371). Cơ sở dữ liệu WorkManager của DAVx5 (đọc bằng `sqlite3` trên AVD) cho thấy `OneTimeSyncWorker` đang ENQUEUED với `run_attempt_count = 7`, backoff mũ 30 s, tức chờ khoảng 32 phút; job sync của tài khoản chạy rồi chờ worker này 60 s và bị hủy. Mỗi lần DAVx5 bị kill giữa lúc upload làm số lần thử tăng một; chỉ một lần worker chạy xong mới đưa về 0. Không sửa cơ sở dữ liệu của app (ghi bằng root khi app đang chạy dễ hỏng quyền file và làm DAVx5 crash). Hệ quả chỉ là các lượt quá hạn trong lúc chờ (INVALID, chạy bù); nhãn không bị ảnh hưởng. Nếu collector chạm giới hạn 60 lần bù trong một lần chạy thì chạy lại cùng lệnh.
- **20/11 03:31: nguyên nhân thật của các chuỗi quá hạn, và đặt lại worker.** Bộ đếm `run_attempt_count` của `OneTimeSyncWorker` lên tới 8 (backoff khoảng 64 phút) vì helper ép job sync của tài khoản chạy sớm: adapter chờ worker đang backoff 60 s rồi bị hủy, và mỗi lần hủy làm bộ đếm tăng. Xử lý: (1) dừng collector sau c0396, tắt hẳn `tn1_sync_flush.py` (không dùng nữa cho TN1); (2) `am force-stop` DAVx5, sao lưu `androidx.work.workdb` cùng -wal, -shm vào `/data/local/tmp/gx-wm-backup` trên AVD; (3) bằng `sqlite3`, đặt `run_attempt_count = 0` và `last_enqueue_time` về hiện tại cho dòng `OneTimeSyncWorker` đang ENQUEUED (1 dòng), `integrity_check` ok; sqlite tự checkpoint và xóa -wal, -shm khi đóng, file db giữ nguyên chủ sở hữu `u0_a181` và nhãn SELinux của app; (4) chạy lại collector ở chế độ tự nhiên (upload sau khoảng 55 s như đoạn đầu). Năm lượt X=1 sau đó đều đúng (khoảng 60 s mỗi lượt), worker chạy xong và bộ đếm tự về thấp. Đây chỉ là trạng thái lập lịch upload của DAVx5; không đụng event, Etar hay nhãn. Lượt c0397 vừa bắt đầu (thư mục rỗng) đã xóa để chạy lại.
- **20/11 04:06: đặt lại worker tự động giữa các lượt.** Ở chế độ tự nhiên, bộ đếm vẫn leo lại 6 sau chuỗi lượt chạy bù toàn lớp kill (c0367, c0368, c0371, c0372 quá hạn). Thêm `testbed/tn1_worker_reset.py`: sau mỗi dòng mới của batch.log, nó `am force-stop` DAVx5 rồi chạy một lệnh sqlite đặt `run_attempt_count = 0` cho `OneTimeSyncWorker` đang ENQUEUED có bộ đếm từ 1 trở lên, đúng thao tác đã kiểm lúc 03:31. Lần đầu sửa 1 dòng (bộ đếm 6), các lần sau không còn dòng nào cần sửa; các lượt X=1 sau đó đều đúng (khoảng 60 s); file db giữ chủ sở hữu và nhãn. Dùng helper này cho phần còn lại của calibration và toàn bộ đợt test.
- **20/11 06:00: calibration TN1 xong, kho đã biên dịch (trước khi chạy test).** 489 effect hợp lệ, đúng quota (mỗi lớp 133 X=1 và 30 X=0), 86 lượt INVALID (rig, đã chạy bù). Không lần đọc nào sai: cả 399 effect X=1 đọc (1, 1), cả 90 effect X=0 đọc (0, 0). `calibration.py` biên dịch `testbed/tn1/tn1_store.json` (product, K = 9, δ = 1,11e-3, sha ae07c66e...): cận một phía của P(đọc vắng mặt | X=1) là 0,0499 ở mỗi lớp, bằng ngưỡng α_test = 0,05 nên chứng nhận được chiều vắng mặt ở cả ba lớp; phía commit không dùng (G2 khai không dùng được). Nhãn chép ở `testbed/tn1/calibration_effects.jsonl`; bằng chứng từng lượt ở `testbed/runs/tn1-calibration/` (bị git bỏ qua).
- **TN1 test held-out bắt đầu:** `collect --schedule testbed/tn1/schedule_test.json --store testbed/tn1/tn1_store.json --out testbed/runs/tn1-test`, cùng `tn1_arm_watchdog.py` và `tn1_worker_reset.py` trỏ vào thư mục test.
- **20/11 08:55: tạm dừng đợt test TN1 (trưởng nhóm cần tắt máy).** 130/240 quyết định trong `testbed/runs/tn1-test/decisions.jsonl`, 1 INVALID (quá hạn barrier). Đến lúc dừng: X=1 luôn ASK (60/60), X=0 luôn RETRY `certified_hop1_absence` (70/70), không lần nào retry effect đã commit, mọi lượt đều đúng một bản trên server (kể cả các lần agent soạn lại). Lượt t0131 đang chạy dở được đổi tên thành `t0131-ABORTED-pause` (không có dòng quyết định nào), nên lần chạy tiếp sẽ chạy lại t0131 từ đầu. Đã dừng collector, watchdog, helper đặt lại worker, Radicale, emulator. **Chạy tiếp:** bật AVD (nếu System UI báo ANR thì bấm "Close app"), rồi chạy lại đúng lệnh `collect --schedule testbed/tn1/schedule_test.json --store testbed/tn1/tn1_store.json --out testbed/runs/tn1-test --adb <adb>` cùng `tn1_arm_watchdog.py --run testbed/runs/tn1-test` và `tn1_worker_reset.py --run testbed/runs/tn1-test --adb <adb>`.
- **20/11 12:58: chạy tiếp đợt test TN1; sự cố mạng AVD 13:00 đến 13:13.** Sau khi AVD khởi động lạnh, DNS trong máy ảo hỏng (`ping www.google.com`: unknown host; IP vẫn chạy), nên Android bỏ cờ VALIDATED của Wi-Fi và JobScheduler giữ job sync của DAVx5 ở `CONNECTIVITY` chưa đạt: không có upload nào từ 13:00:25. Hệ quả: t0134, t0136, t0137 (X=1) INVALID vì quá hạn barrier (chạy bù); t0132, t0133, t0135 (X=0) planner RETRY đúng (`certified_hop1_absence`), agent soạn lại, nhưng bản làm lại nằm lại trên máy (dirty) và chưa upload trong cửa sổ 90 s, nên `server_copies_final` = 0. Đây là lỗi mạng của rig, không phải quyết định sai; ba lượt này giữ nguyên trong `decisions.jsonl` và được tách riêng khỏi số đếm upload sau khi làm lại. Lượt t0138 dở dang đổi tên `-ABORTED-net`. Sửa trên AVD thử: tắt dữ liệu di động (`svc data disable`), `settings put global captive_portal_mode 0` (rig không cần internet; Radicale đi qua adb reverse) và bật lại Wi-Fi; Wi-Fi có lại VALIDATED và job sync chạy lúc 13:13:31. Collector chạy lại sau đó.
- **20/11 14:20: tạm dừng đợt test TN1 lần hai (trưởng nhóm yêu cầu).** 183/240 quyết định, 5 INVALID (chạy bù). Đến giờ: X=1 luôn ASK (88/88), X=0 luôn RETRY `certified_hop1_absence` (95/95), không lần nào retry effect đã commit; bản làm lại lên server đúng một bản ở 92/95 lượt RETRY, 3 lượt còn lại (t0132, t0133, t0135) là ba lượt trong sự cố mạng 13:00 đến 13:13. Lượt t0184 vừa bắt đầu được đổi tên `-ABORTED-pause2`. Đã dừng collector, watchdog, helper đặt lại worker và emulator. Chạy tiếp như mục 08:55 (AVD giữ `captive_portal_mode 0` và dữ liệu di động tắt; nếu job sync của DAVx5 lại kẹt `CONNECTIVITY` thì bật tắt Wi-Fi).
