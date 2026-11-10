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
