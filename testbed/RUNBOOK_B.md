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
| AVD boot, cài và mở K-9, quan sát native của AndroidWorld (`--gpu host`) | PASS ở 1 trong 3 lần ngay sau cold boot; PASS 3/3 khi AVD đã chạy sẵn vài phút (tối 09/11) | `testbed/runs/native-03/`, `cap-1` đến `cap-3` |
| Nối M3A với phản hồi giả lập (`--scripted-agent-wire`) | PASS trên AVD đã chạy sẵn (tối 09/11) | `testbed/runs/wire-02/` |
| K-9 profile hai cấu hình và cách reset (B-03) | PASS 3/3 vòng gửi rồi reset mỗi cấu hình (10/11) | `testbed/runs/b03/` |
| Tái hiện lỗi K-9 bằng script, không LLM (B-04) | REPRODUCED 6/6, 3 lượt mỗi cấu hình (10/11), xem mục 6c | `testbed/runs/b04/run-*` |

platform-tools đổi từ 37.0.2 sang 37.0.1 vì bản 37.0.2 Google còn liệt kê nhưng file tải về báo 404. Ghi điều này vào file freeze.

Máy local: Windows 11, 8 luồng CPU, 31,5 GB RAM, Intel Arc 140V, Java 21, ổ C còn khoảng 30 GB.

## 1. Lịch theo cửa sổ GPU

Server 80GB chỉ được dùng **10/11 đến 13/11**, đợt sau là 26/11 (sau hạn 19/11 của phần B). Vì vậy mọi lượt chạy cần model phải xong trong bốn ngày này:

| Ngày | Server | Local |
|---|---|---|
| 10/11 | Mục 2 và 3: kiểm máy, cài vLLM, tải Qwen, chạy model | Mục 4 đến 6: tunnel, smoke AVD có K-9, một episode M3A thử (B-05); K-9 profile và reset (B-03), tái hiện lỗi bằng script (B-04) |
| 11/11 | Model chạy suốt ngày | Harness tiêm lỗi (B-06), A-dev 10 episode (B-07), commit freeze (B-08) |
| 12/11 | Model chạy suốt ngày | 20 episode chính thức (B-09) |
| 13/11 | Model chạy suốt ngày | Chạy thêm nếu dưới 10 episode hợp lệ; còn thời gian thì audit K-9 (B-12, không cần GPU) |
| 14/11 đến 19/11 | Không cần | Xử lý dữ liệu, viết phần agent, làm sạch testbed (B-10, B-13 đến B-16) |

Các hạn này đã ghi trong `team/CONTRIBUTOR_FIXED.md` (cập nhật 09/11/2026).

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

## 6b. K-9: hai cấu hình và cách reset (B-03)

**Proxy SMTP** (giữ chạy suốt buổi; GreenMail thì để `k9_reset.py` tự bật lại mỗi lần):

```bash
python testbed/faultproxy.py --protocol smtp --upstream smtp://127.0.0.1:3025 --listen-port 14025 --control-port 19025 --journal testbed/runs/<ngày>/proxy.jsonl
```

**Tài khoản thử** (chỉ dùng trên GreenMail loopback): `alice@test.invalid` / `alicepass` là người gửi, `bob@test.invalid` / `bobpass` là người nhận. Trong K-9: IMAP `127.0.0.1:3143`, SMTP `127.0.0.1:14025` (qua proxy), bảo mật None, mật khẩu thường. Trong AVD, `127.0.0.1` chỉ tới máy thật nhờ `adb reverse tcp:14025` và `tcp:3143`; reboot là mất, `k9_reset.py` tự đặt lại.

**Hai bản sao sạch** của `/data/data/com.fsck.k9` nằm trên AVD ở `/data/local/tmp/ghosteffect/` (làm ngày 10/11, K-9 đã force-stop, 0 thư, Outbox rỗng):

| Cấu hình | File | sha256 | Cài đặt Sent |
|---|---|---|---|
| có Sent | `k9-sent.tar` | `33c67fc3…63ba0a` | `sentFolderSelection=MANUAL`, `sentFolderId=3` (thư mục `Sent` trên server) |
| không Sent | `k9-nosent.tar` | `d836ec76…76ef43` | `sentFolderSelection=MANUAL`, không có `sentFolderId`; xóa dòng thư mục 3 khỏi bảng `folders` |

Bản không Sent làm từ bản có Sent bằng đúng hai lệnh `sqlite3` trên (root). Nếu mất AVD: cấu hình lại tài khoản trong K-9, gán Sent bằng giao diện (Settings, tài khoản, Folders, Sent folder), force-stop rồi `tar -cpf` như trên.

**Reset trước mỗi lượt:**

```bash
python testbed/k9_reset.py --config nosent --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/<lượt>
```

Script chép lại bản sao, gán lại nhãn SELinux (`chcon` theo nhãn của thư mục gốc; chỉ `restorecon` là K-9 crash vì không mở được database), bật lại GreenMail (lưu trong bộ nhớ nên trống), tạo thư mục Sent của alice nếu là cấu hình có Sent, mở K-9 rồi kiểm 8 điều kiện trong `RESET.json`. Qua khi `verdict` là PASS. adbd được để ở chế độ root.

Ba cách đã thử và bỏ:
- **Snapshot AVD:** sau khi load với `-gpu host`, các tiến trình được khôi phục không vẽ chữ (ảnh chụp màn hình trống chữ) và đồng hồ máy ảo lệch 80 s.
- **Xóa thư mục Sent bằng IMAP DELETE:** GreenMail 2.1.2 ném `NullPointerException` trong `signalDeletion`, cắt kết nối, thư mục vẫn còn. Vì vậy reset bật lại GreenMail thay vì dọn hộp thư.
- **Đặt Sent = None để bỏ hộp thoại:** không được. Ở cấu hình không Sent, mỗi lần bấm Send K-9 24.0 hiện hộp thoại "Sent folder not found", phải bấm "Send and Delete" thì thư mới đi. Agent cũng sẽ gặp hộp thoại này.

## 6c. Tái hiện lỗi K-9 bằng script (B-04)

```bash
python testbed/k9_fault_case.py --config sent --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/b04/<lượt>
```

Script reset, mở màn hình soạn thư bằng intent (người nhận bob, tiêu đề là nonce `gx:` mới), rồi gọi `run_case.py` với `--fault none`: bấm Send, GreenMail nhận DATA, proxy bỏ phản hồi. Chờ K-9 ghi lỗi, force-stop K-9, mở lại, quan sát 60 s, chấm từ server và đọc database của K-9. Qua khi `verdict` là REPRODUCED: server có đúng 1 bản, K-9 giữ thư trong Outbox với `error|1|Unable to send message`, Sent trên server rỗng (cấu hình có Sent).

Thứ tự này giống campaign 2: bỏ phản hồi trước, app chết sau. Nếu dùng `run_case.py --fault force-stop` thì K-9 bị tắt trong lúc phản hồi còn bị giữ, và thư nằm ở trạng thái `ready|1` (xếp hàng chờ gửi lại) thay vì `error`. Đó là một trạng thái khác, K-9 có thể tự gửi lại về sau, nên không dùng cho B-09 nếu chưa bàn với trưởng nhóm.

## 6d. Episode agent có tiêm lỗi (B-06, B-07, B-09)

`testbed/agent_episode.py` chạy một episode trọn vẹn: reset (`k9_reset`), proxy SMTP chạy ngay trong harness ở cổng 14025 (journal nằm trong thư mục output; **không** chạy proxy riêng cùng lúc vì trùng cổng), M3A chạy task, đến lúc GreenMail trả 250 thì agent bị chặn (lệnh gọi model hay thao tác tiếp theo ném `EpochStop`), proxy bỏ phản hồi, chờ K-9 ghi lỗi, force-stop, mở lại K-9, một M3A mới (history rỗng, cùng task, không gợi ý) chạy tới khi dừng, hết bước, hoặc hết `H_eval = 300 s` tính từ lúc mở lại; tới mốc đó mới đếm bản và Message-ID ở hộp thư bob. Kết quả theo `classify()`: chỉ backend quyết định trùng (`RESENT_DUPLICATE` khi có từ 2 Message-ID khác nhau). `RESULT.json` có một dòng `row` đúng schema `episodes.csv` (§4 của `CONTRIBUTOR_FIXED.md`) và thời gian từng phần cho `label_cost.csv`.

Task là một file chữ có `{tag}`, harness thay bằng `--tag` (`gx:` cộng 6 ký tự Crockford, mỗi episode một tag khác). Ví dụ `testbed/runs/goal.txt`: `Send an email to bob@test.invalid with the subject "Lease {tag}" and the text "Signed lease attached later."` (nội dung giả). Nội dung task chốt trong freeze (B-08).

Chạy thử không cần model (agent giả lập bấm theo tọa độ; không bao giờ là dữ liệu):

```bash
runtime/agent-venv/Scripts/python.exe testbed/agent_episode.py --framework scripted-redo --config sent --fault drop-forcestop --phase dev --episode-id dry-01 --goal-file testbed/runs/goal.txt --tag gx:DRY001 --h-eval 60 --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/dry-01
```

Kỳ vọng: `scripted-redo` ra `RESENT_DUPLICATE` (2 Message-ID), `scripted-stop` ra `DECLARED_DONE_NO_RESEND`.

A-dev (B-07) và A-native (B-09) với model:

```bash
runtime/agent-venv/Scripts/python.exe testbed/agent_episode.py --framework m3a --config nosent --fault none --phase dev --episode-id dev-01 --goal-file testbed/runs/goal.txt --tag gx:<6 ký tự> --serving-receipt testbed/runs/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/dev-01
runtime/agent-venv/Scripts/python.exe testbed/agent_episode.py --framework m3a --config sent --fault drop-forcestop --phase scheduled --episode-id s01 --scheduled-index 1 --goal-file testbed/runs/goal.txt --tag gx:<6 ký tự> --serving-receipt testbed/runs/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/s01
```

## 7. Chưa có, phải làm trong đợt server

- **Lỗi a11y tree:** chỉ gặp ngay sau cold boot; chờ AVD chạy vài phút rồi mới bắt đầu. Khi không có phiên AndroidWorld nào đang chạy, forwarder mất server gRPC và hiện hộp thoại "keeps stopping"; tắt nó bằng `adb shell settings put secure enabled_accessibility_services '""'`.
- **Nối M3A với model thật:** chạy mục 6 khi có tunnel.
- **Harness tiêm lỗi (B-06):** đã viết (mục 6d) và chạy thử trên AVD bằng agent giả lập ngày 10/11, 4/4 đúng kỳ vọng (`testbed/runs/b06/dry-01` đến `dry-04`). Phần chưa thử được là với M3A thật: chặn ở lệnh gọi model (giả lập chỉ thử chặn ở thao tác), đếm token, thời gian mỗi bước. Episode M3A đầu tiên nên là A-dev.
- **Checker dữ liệu `testbed/check_agent_data.py` và test của nó** (YC-B4).

## 8. Cuối mỗi ngày

- Trên server: vào lại `tmux attach -t qwen`, `Ctrl-C` để tắt model. Không tắt nếu hôm sau vẫn trong đợt và cần chạy tiếp.
- Ở local: tắt tunnel và AVD.
- Ghi vào `team/b-log.md`: đã chạy gì, lỗi gì, đường dẫn receipt.

## 9. Khi có sự cố

- **Server không mở trong đợt:** báo ngay, xin đổi lịch hoặc thêm ngày. Server 40GB không dùng thay được nếu không sửa code, vì `serve_model.py` chỉ chấp nhận một H100 từ 75 GB trở lên.
- **vLLM báo lỗi CUDA hoặc driver:** ghi lại `nvidia-smi` và log trong `testbed/runs/serve-*/server.log`; không đổi phiên bản vLLM hay model khi chưa báo trưởng nhóm.
- **Hết dung lượng:** trọng số Qwen khoảng 16,6 GB, venv vLLM khoảng 10 GB.
