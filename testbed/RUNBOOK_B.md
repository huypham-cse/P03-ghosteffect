# Runbook phần B: chạy LLM agent với server H100 80GB

Làm theo thứ tự, mỗi bước có lệnh và điều kiện qua. Chạy lệnh từ thư mục gốc repo. Ghi mọi việc đã làm vào `team/b-log.md` theo luật 1.8.

## 0. Đã chuẩn bị sẵn trên máy local (09/11/2026)

| Việc | Trạng thái | Receipt (chỉ có trên máy, không commit) |
|---|---|---|
| APK K-9, GreenMail, forwarder của AndroidWorld | Đã tải, khớp SHA | `runtime/assets/*.receipt.json` |
| Android SDK, emulator 37.2.13, platform-tools 37.0.1 | Đã cài; WHPX dùng được | `runtime/android-downloads/BOOTSTRAP.json` |
| AVD `ghosteffect_api33_x86_local` (API 33 r17), chữ ký APK K-9 và forwarder | Xong | `testbed/runs/avd-01/` |
| AndroidWorld đúng commit `55ddaf5e` ở `runtime/vendor/android_world_full`, venv Python 3.11.8, M3A import được | Xong | `runtime/agents/SETUP.json` |
| GreenMail cùng fault proxy (smoke) | PASS | `testbed/runs/mail-smoke-01/` |
| AVD boot, cài và mở K-9, quan sát native của AndroidWorld (`--gpu host`) | PASS ở 1 trong 3 lần; 2 lần còn lại lỗi "Could not get a11y tree" | `testbed/runs/native-03/` |
| Nối M3A với phản hồi giả lập (`--scripted-agent-wire`) | Chưa qua, cùng lỗi a11y tree | `testbed/runs/wire-01/` |

platform-tools đổi từ 37.0.2 sang 37.0.1 vì bản 37.0.2 Google còn liệt kê nhưng file tải về báo 404. Ghi điều này vào file freeze.

Máy local: Windows 11, 8 luồng CPU, 31,5 GB RAM, Intel Arc 140V, Java 21, ổ C còn khoảng 30 GB.

## 1. Lịch theo cửa sổ GPU

Server 80GB chỉ được dùng **10/11 đến 13/11**, đợt sau là 26/11 (sau hạn 19/11 của phần B). Vì vậy mọi lượt chạy cần model phải xong trong bốn ngày này:

| Ngày | Server | Local |
|---|---|---|
| 10/11 | Mục 2 và 3: kiểm máy, cài vLLM, tải Qwen, chạy model | Mục 4 đến 6: tunnel, smoke AVD có K-9, một episode M3A thử (B-05); K-9 profile và reset (B-03), tái hiện lỗi bằng script (B-04) |
| 11/11 | Model chạy suốt ngày | Harness tiêm lỗi (B-06), A-dev 10 episode (B-07), commit freeze (B-08) |
| 12/11 | Model chạy suốt ngày | 20 episode chính thức (B-09) |
| 13/11 | Model chạy suốt ngày | Chạy thêm nếu dưới 10 episode hợp lệ, audit K-9 (B-12), dữ liệu chi phí nhãn (B-11) |
| 14/11 đến 19/11 | Không cần | Xử lý dữ liệu, viết phần agent, làm sạch testbed (B-10, B-13 đến B-16) |

Lịch này sớm hơn các hạn B-06 đến B-09 trong `team/CONTRIBUTOR_FIXED.md`; cần dời các hạn đó cho khớp.

## 2. Mỗi sáng: server đã mở chưa

```bash
ssh -p 52194 -o ConnectTimeout=15 root@103.73.232.225 'nvidia-smi -L'
```

Qua khi in ra một GPU H100. `~/.ssh/config` đã có sẵn user `root` và khóa `id_ed25519` cho địa chỉ này. Không vào được thì ghi vào `b-log.md` và báo ngay trên nhóm chat.

## 3. Server: chép code, cài, chạy model

Chép code lên server (cách này chạy được cả khi repo đã chuyển sang private):

```bash
git archive HEAD | ssh -p 52194 root@103.73.232.225 'mkdir -p ~/P03 && tar -x -C ~/P03'
```

Vào server, mở `tmux` để model không tắt khi rớt SSH:

```bash
ssh -p 52194 root@103.73.232.225
tmux new -s qwen
cd ~/P03
bash testbed/server_h100.sh check     # phải thấy một H100 khoảng 80 GB; ghi lại KVM, RAM, ổ đĩa
bash testbed/server_h100.sh setup     # venv vLLM 0.11.0 và tải khoảng 16,6 GB trọng số Qwen, kiểm từng file
bash testbed/server_h100.sh serve     # chờ dòng MODEL_SERVING_READY
```

Qua khi thấy `MODEL_SERVING_READY testbed/runs/serve-<ngày giờ>/SERVING.json`. Thoát tmux bằng `Ctrl-b` rồi `d`; model vẫn chạy. Nếu server bị dọn sạch giữa các đợt thì chạy lại `setup`.

## 4. Local: tunnel và receipt

Mở một terminal riêng và giữ nó mở trong lúc chạy episode:

```bash
ssh -N -L 8101:127.0.0.1:8101 -p 52194 root@103.73.232.225
```

Ở terminal khác:

```bash
curl -s http://127.0.0.1:8101/version          # phải là 0.11.0
scp -P 52194 'root@103.73.232.225:~/P03/testbed/runs/serve-*/SERVING.json' testbed/runs/SERVING.json
```

## 5. Local: smoke AVD có K-9 và forwarder

```bash
python testbed/smoke_android.py --verification testbed/runs/avd-01/RESULT.json --only com.fsck.k9_39046.apk --native-env-capture --gpu host --output testbed/runs/native-01
```

Qua khi có screenshot và cây accessibility, định danh cửa sổ khớp. Chỉ `--gpu host` từng chạy được; không tắt guard để lấy PASS.

Lỗi "Could not get a11y tree" xảy ra chập chờn (máy này 2 trong 3 lần, máy cũ cũng từng gặp): chạy lại với thư mục output mới. Mỗi lần lỗi vẫn giữ receipt và ghi vào `b-log.md`.

## 6. Local: bật AVD để chạy episode, rồi chạy một episode M3A thử

Bật AVD (PowerShell, giữ cửa sổ này mở):

```powershell
$r = (Get-Location).Path
$env:ANDROID_HOME = "$r\runtime\android-sdk"; $env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:ANDROID_USER_HOME = "$r\runtime\android-home"; $env:ANDROID_EMULATOR_HOME = $env:ANDROID_USER_HOME
$env:ANDROID_AVD_HOME = "$r\runtime\android-avd"; $env:ANDROID_ADB_SERVER_PORT = "5038"
& "$env:ANDROID_HOME\platform-tools\adb.exe" -P 5038 start-server
& "$env:ANDROID_HOME\emulator\emulator.exe" -avd ghosteffect_api33_x86_local -port 5580 -grpc 8554 -no-audio -no-snapshot -no-boot-anim -accel on -gpu host
```

Viết mục tiêu của task vào một file (ví dụ `testbed/runs/goal-dev.txt`, nội dung giả, tài khoản thử), rồi chạy:

```bash
runtime/agent-venv/Scripts/python.exe testbed/native_episode.py --framework m3a --goal-file testbed/runs/goal-dev.txt --max-steps 15 --timeout-seconds 600 --serving-receipt testbed/runs/SERVING.json --endpoint http://127.0.0.1:8101/v1 --adb runtime/android-sdk/platform-tools/adb.exe --console-port 5580 --adb-server-port 5038 --grpc-port 8554 --output testbed/runs/episode-dev-01
```

Qua khi episode chạy hết mà không lỗi kết nối hay lỗi model (task có thành công hay không thì chưa quan trọng ở bước này).

## 7. Chưa có, phải làm trong đợt server

- **Lỗi a11y tree chập chờn:** rủi ro lớn nhất. Episode nào gặp lỗi này ở bước reset sẽ thành INVALID. Cần tìm nguyên nhân (thời điểm forwarder kết nối sau khi boot, cổng gRPC 8554) trước A-dev; không sửa mã AndroidWorld upstream.
- **Nối M3A với model thật:** `--scripted-agent-wire` chưa qua vì lỗi trên; chạy lại sau khi xử lý được lỗi a11y.
- **K-9 profile và cách reset (B-03):** tài khoản thử trên GreenMail qua proxy SMTP (`adb reverse`), hai cấu hình không Sent và có Sent.
- **Harness tiêm lỗi (B-06):** mở rộng `native_episode.py`: bắt lúc Send, để commit rồi bỏ phản hồi, kill agent và force-stop K-9, mở lại, chạy lại M3A cùng task, quan sát 300 s, chấm bằng backend.
- **Checker dữ liệu `testbed/check_agent_data.py` và test của nó** (YC-B4).

## 8. Cuối mỗi ngày

- Trên server: vào lại `tmux attach -t qwen`, `Ctrl-C` để tắt model. Không tắt nếu hôm sau vẫn trong đợt và cần chạy tiếp.
- Ở local: tắt tunnel và AVD.
- Ghi vào `team/b-log.md`: đã chạy gì, lỗi gì, đường dẫn receipt.

## 9. Khi có sự cố

- **Server không mở trong đợt:** báo ngay, xin đổi lịch hoặc thêm ngày. Server 40GB không dùng thay được nếu không sửa code, vì `serve_model.py` chỉ chấp nhận một H100 từ 75 GB trở lên.
- **vLLM báo lỗi CUDA hoặc driver:** ghi lại `nvidia-smi` và log trong `testbed/runs/serve-*/server.log`; không đổi phiên bản vLLM hay model khi chưa báo trưởng nhóm.
- **Hết dung lượng:** trọng số Qwen khoảng 16,6 GB, venv vLLM khoảng 10 GB.
