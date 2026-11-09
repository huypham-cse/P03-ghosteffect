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
