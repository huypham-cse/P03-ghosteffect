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
