# Runbook phần B: chạy LLM agent trên GPU thuê (AWS g6e.xlarge)

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

## 1. Plan theo giờ (máy AWS, 14/11)

Server 80GB và 40GB không vào được từ 10/11. Nhóm thuê một máy AWS. Cấu hình chốt là `g5.xlarge`, nhưng máy được tạo (14/11) là `g6e.xlarge` (1 GPU L40S 48 GB, 4 vCPU, 30 GB RAM), us-east-1, Ubuntu 24.04 thường (không phải Deep Learning AMI, nên chưa có driver NVIDIA), ổ 300 GB, SSH chỉ mở cho IP của máy local. Trưởng nhóm chọn giữ máy này. AWS tính tiền theo giây khi máy bật, nên mọi việc không cần GPU làm trước hoặc sau, và tắt máy (Stop) ngay khi xong.

**Trước khi có máy (không tốn tiền):**

| Việc | Lệnh | Qua khi |
|---|---|---|
| Gộp PR có `server_gpu.sh`, `fake_model.py`, `run_agent_study.py`, `make_freeze.py`, `collect_agent.py`, `check_agent_data.py`, `render_agent.py` | | main có các file này |
| Tổng duyệt trên emulator với model giả (mục 6f) | `fake_model.py` và `agent_episode.py` | 1 episode dev ra kết quả hợp lệ, 1 episode có lỗi ra `RESENT_DUPLICATE` |
| Thêm máy vào `~/.ssh/config` khi biết IP (mục 2) | | `ssh ghost-gpu true` chạy được |

**Ngày có máy (máy bật, tính tiền):**

| Giờ (ước tính) | Server | Local |
|---|---|---|
| 0:00 đến 0:45 | Mục 3: chép code, `check`, `setup` (cài vLLM khoảng 10 phút, tải Qwen khoảng 5 phút), `serve` (nạp model và biên dịch 5 đến 10 phút) | Bật AVD sớm và để chạy vài phút (lỗi a11y chỉ gặp ngay sau cold boot); mở tunnel khi có `MODEL_SERVING_READY` |
| 0:45 đến 1:15 | Model chạy | Một episode dev đầu tiên, ngồi xem (`--dev-n 1`) |
| 1:15 đến 2:30 | Model chạy | 9 episode dev còn lại (B-07). Dưới 6/10 thành công thì báo trưởng nhóm trước khi đi tiếp, và Stop máy trong lúc chờ |
| 2:30 đến 2:45 | Model chạy (Stop nếu chờ gộp quá 30 phút; freeze không phụ thuộc phiên server) | `make_freeze.py`, commit, PR, trưởng nhóm gộp, `git fetch` (B-08). Runner chỉ chạy scheduled khi freeze đã nằm trong `origin/main` và khớp code, task, profile GPU |
| 2:45 đến khoảng 6:30 | Model chạy | `run_agent_study.py --phase scheduled`: 20 episode khoảng 10 phút mỗi episode, chạy thêm nếu dưới 10 hợp lệ (B-09). Báo C số đếm thô ngay khi xong |
| Xong | **Stop máy ngay** | `collect_agent.py`, `check_agent_data.py`, render, viết B-10 và B-11 |

Tổng thời gian máy bật khoảng 6 đến 8 giờ, tức khoảng 11 đến 15 USD với g6e.xlarge ở us-east-1 (1,861 USD/giờ). Giữ ổ đĩa (máy ở trạng thái Stop) đến khi nghiệm thu xong ngày 21/11 phòng phải chạy lại, rồi Terminate.

`server_gpu.sh` tự chọn profile theo GPU (`l40s` trên máy này, `a10g` nếu sau này đổi sang g5). Mọi episode scheduled phải chạy trên cùng một loại máy, vì freeze ghi `gpu_profile`; không đổi instance type sau khi freeze.

## 2. Kết nối máy AWS

Key `MobiSYS.pem` do người tạo máy gửi; để ở `~/.ssh/`, ngoài repo, chỉ tài khoản mình đọc được (Windows: `icacls <file> /inheritance:r /grant:r "<user>:R"`). Thêm vào `~/.ssh/config` (IP lấy trên EC2 console; IP đổi sau mỗi lần Stop rồi Start, khi đó sửa dòng `HostName`):

```
Host ghost-gpu
    HostName <IP của máy EC2>
    User ubuntu
    IdentityFile ~/.ssh/MobiSYS.pem
    IdentitiesOnly yes
    ServerAliveInterval 30
```

```bash
ssh -o ConnectTimeout=15 ghost-gpu 'nvidia-smi -L'
```

Qua khi in ra một GPU L40S (sau bước `setup`; trước đó máy chưa có driver). SSH bị treo thì kiểm security group có mở cổng 22 cho đúng IP local không.

## 3. Server: chép code, cài, chạy model

Chép code lên server (cách này chạy được cả khi repo đã chuyển sang private). Trên Windows phải có `-c core.autocrlf=false`: không có nó, `git archive` đổi xuống dòng sang CRLF và bash trên server báo `set: pipefail: invalid option name`.

```bash
git -c core.autocrlf=false archive HEAD | ssh ghost-gpu 'mkdir -p ~/P03 && tar -x -C ~/P03'
```

Vào server, mở `tmux` để model không tắt khi rớt SSH:

```bash
ssh ghost-gpu
tmux new -s qwen
cd ~/P03
bash testbed/server_gpu.sh check     # GPU, profile (a10g/l40s/h100), RAM, ổ đĩa, Python phải dưới 3.14
bash testbed/server_gpu.sh setup     # driver NVIDIA nếu thiếu, python3-venv, gcc và python3-dev (Triton biên dịch module C lúc vLLM khởi động), venv vLLM 0.11.0, khoảng 16,6 GB trọng số Qwen, kiểm từng file
bash testbed/server_gpu.sh serve     # chờ dòng MODEL_SERVING_READY
```

Trên AMI Ubuntu thường, lần `setup` đầu cài driver 580-server dựng sẵn cho đúng kernel rồi dừng ở dòng `driver installed but not loaded` vì nouveau đang giữ card: `sudo reboot` (reboot không đổi IP), chờ khoảng một phút, chạy lại `setup`.

Qua khi thấy `MODEL_SERVING_READY testbed/runs/serve-<ngày giờ>/SERVING.json`. Thoát tmux bằng `Ctrl-b` rồi `d`; model vẫn chạy. Lỗi thì `serve_model.py` in `FAILED <loại lỗi>: <thông báo>` và ghi vào `SERVING.json`; log của vLLM ở `testbed/runs/serve-*/server.log`.

Profile bộ nhớ (trong `serve_model.py`) chỉ đổi phần bộ nhớ vLLM giữ và số yêu cầu chạy song song, không đổi model, ngữ cảnh 32768 hay cách xử lý ảnh: A10G dùng 90% bộ nhớ GPU và 1 yêu cầu một lúc (mỗi episode chỉ gửi một yêu cầu một lúc); L40S và H100 dùng 85% và 2. Ảnh giới hạn `max_pixels=3211264` để vLLM không phải giữ chỗ cho ảnh 16384 token; ảnh chụp 1080x2400 sau khi làm tròn là 2629536 điểm ảnh, dưới mức đó, nên không ảnh nào bị thu nhỏ.

## 4. Local: tunnel và receipt

Mở một terminal riêng và giữ nó mở trong lúc chạy episode:

```bash
ssh -N -L 8101:127.0.0.1:8101 ghost-gpu
```

Ở terminal khác:

```bash
curl -s http://127.0.0.1:8101/version          # phải là 0.11.0
scp 'ghost-gpu:~/P03/testbed/runs/serve-<ngày giờ>/SERVING.json' testbed/runs/SERVING.json   # đúng thư mục in ở dòng MODEL_SERVING_READY
```

`run_agent_study.py` kiểm endpoint trước mỗi episode; tunnel chết thì nó dừng hẳn, không tiêu lượt chạy. Tunnel rớt giữa một episode thì episode đó ghi `measurement_error` và được chạy lại lần 2; lỗi đo hai lần liên tiếp thì runner dừng để tìm nguyên nhân. Mở lại tunnel rồi chạy lại đúng lệnh; episode đã xong được bỏ qua.

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

**Proxy SMTP** (chỉ cần khi tự gửi thư bằng tay; `k9_fault_case.py` và `agent_episode.py` tự chạy proxy riêng cho từng lượt trên cùng cổng 14025, nên tắt proxy này trước khi chạy chúng; GreenMail thì để `k9_reset.py` tự bật lại mỗi lần):

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

Script tắt dịch vụ forwarder của AndroidWorld (nó crash và hiện hộp thoại "keeps stopping" đè lên K-9 khi không có phiên AndroidWorld), chép lại bản sao, gán lại nhãn SELinux (`chcon` theo nhãn của thư mục gốc; chỉ `restorecon` là K-9 crash vì không mở được database), bật lại GreenMail (lưu trong bộ nhớ nên trống), tạo thư mục Sent của alice nếu là cấu hình có Sent, mở K-9 rồi kiểm 9 điều kiện (thêm K-9 giữ focus) trong `RESET.json`. Qua khi `verdict` là PASS. adbd được để ở chế độ root.

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

A-dev (B-07), freeze (B-08), A-native (B-09) với model, chạy bằng Python của agent venv. Task chốt ở `testbed/agent_goal.txt`.

```bash
runtime/agent-venv/Scripts/python.exe testbed/run_agent_study.py --phase dev --dev-n 1 --serving-receipt testbed/runs/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe
runtime/agent-venv/Scripts/python.exe testbed/run_agent_study.py --phase dev --serving-receipt testbed/runs/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe
runtime/agent-venv/Scripts/python.exe testbed/make_freeze.py --serving-receipt testbed/runs/SERVING.json --goal-file testbed/agent_goal.txt --host "<máy model>; <máy AVD>" --adb runtime/android-sdk/platform-tools/adb.exe
# commit testbed/agent_study.freeze.json, PR, trưởng nhóm gộp, rồi:
runtime/agent-venv/Scripts/python.exe testbed/run_agent_study.py --phase scheduled --serving-receipt testbed/runs/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe
```

Episode dev là `dev-01` đến `dev-10` (không lỗi, xen kẽ hai cấu hình). Episode scheduled theo đúng thứ tự và tag trong freeze: `s01` đến `s20`, `sNN-r2` là lần chạy lại sau lỗi đo, `s21` trở đi chỉ khi dưới 10 hợp lệ. Lệnh `scheduled` từ chối chạy nếu freeze chưa commit. Bị ngắt giữa chừng thì chạy lại đúng lệnh; episode đã có kết quả được bỏ qua, thư mục dở dang thì dời sang chỗ khác và ghi vào b-log. `--host` không ghi gì lộ danh tính, ví dụ `one NVIDIA L40S (48 GB) cloud VM; x86-64 laptop running the Android emulator (API 33)`.

Sau khi chạy xong (máy AWS đã Stop):

```bash
python testbed/collect_agent.py testbed/runs/agent/* --out artifact/results/real/agent
python testbed/check_agent_data.py artifact/results/real/agent
python artifact/scripts/render.py
```

`collect_agent.py` chỉ thêm dòng mới vào `episodes.csv`; `check_agent_data.py` phải in `OK`. Render ghi 44 macro `\Agent*`, `\LabelTrial*` và `generated/tab_agent.tex` (trước khi có dữ liệu thì in `??`).

## 6f. Tổng duyệt với model giả (không cần GPU)

`testbed/fake_model.py` giả làm vLLM ở cổng 8101 và trả lời prompt M3A thật theo một luật cố định (mở soạn thư, điền người nhận, tiêu đề, nội dung từ task, gửi, bấm "Send and Delete" nếu có, báo xong). Receipt của nó có `synthetic: true`, nên `agent_episode.py` ghi `study_data: false`; `make_freeze.py` và `check_agent_data.py` không nhận nó. Mục đích: thử trọn đường M3A, chặn lệnh gọi model ở barrier, đếm token, receipt và chấm điểm, để ngày có máy không mất tiền gỡ những lỗi này.

```bash
python testbed/fake_model.py --receipt testbed/runs/fake/SERVING.json --delay 6
runtime/agent-venv/Scripts/python.exe testbed/agent_episode.py --framework m3a --config nosent --fault none --phase dev --episode-id fake-dev-01 --goal-file testbed/agent_goal.txt --tag gx:FAKE01 --serving-receipt testbed/runs/fake/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/fake/dev-01
runtime/agent-venv/Scripts/python.exe testbed/agent_episode.py --framework m3a --config nosent --fault drop-forcestop --phase dev --episode-id fake-fault-01 --goal-file testbed/agent_goal.txt --tag gx:FAKE02 --serving-receipt testbed/runs/fake/SERVING.json --adb runtime/android-sdk/platform-tools/adb.exe --output testbed/runs/fake/fault-01
```

`--delay 6` giả lập khoảng 6 giây mỗi lệnh gọi model (ước tính cho A10G). Kỳ vọng: lượt đầu một bản trên server và `agent_final_status=done`; lượt sau `RESENT_DUPLICATE`. Nếu luật của model giả không khớp màn hình K-9 (ví dụ không nhận ra ô người nhận) thì sửa luật trong `fake_model.py`; đó không phải lỗi của harness.

## 7. Chưa thử được trước khi có máy

- **Lỗi a11y tree:** chỉ gặp ngay sau cold boot; chờ AVD chạy vài phút rồi mới bắt đầu. Khi không có phiên AndroidWorld nào đang chạy, forwarder mất server gRPC và hiện hộp thoại "keeps stopping"; `k9_reset.py` tắt nó, `agent_episode.py` bật lại khi nạp môi trường.
- **Tốc độ thật của model:** số bước M3A làm được trong `H_eval = 300 s` chỉ biết khi chạy dev.

## 8. Cuối mỗi ngày

- Trên server: vào lại `tmux attach -t qwen`, `Ctrl-C` để tắt model, rồi **Stop máy trên EC2 console**. Máy chỉ bật khi đang chạy episode.
- Ở local: tắt tunnel và AVD.
- Ghi vào `team/b-log.md`: đã chạy gì, lỗi gì, đường dẫn receipt, giờ bật và tắt máy.

## 9. Khi có sự cố

- **vLLM hết bộ nhớ GPU:** không tự hạ ngữ cảnh hay đổi cách xử lý ảnh; ghi log và báo trưởng nhóm.
- **vLLM báo lỗi CUDA hoặc driver:** ghi lại `nvidia-smi` và log trong `testbed/runs/serve-*/server.log`; không đổi phiên bản vLLM hay model khi chưa báo trưởng nhóm.
- **Hết dung lượng:** trọng số Qwen khoảng 16,6 GB, venv vLLM khoảng 10 GB; ổ 300 GB thừa.
- **SSH treo sau khi Start lại máy:** IP của máy EC2 đã đổi; sửa `HostName` trong `~/.ssh/config`.

## 6e. Audit thao tác K-9 (B-12)

```bash
python testbed/k9_fault_case.py --config nosent --adb runtime/android-sdk/platform-tools/adb.exe --observe 10 --action sync --action-window 60 --output testbed/runs/b12/audit/t01-sync
python testbed/k9_audit_table.py testbed/runs/b12/audit --output artifact/results/real/audit/k9_action_audit.csv
```

`--action` là `sync`, `send_messages`, `none` hoặc `recompose`; mỗi lần bấm có biên nhận giao diện. Kết quả 12/11: mỗi thao tác 5 lượt hợp lệ; sync, send_messages, none không tạo DATA mới, recompose tạo bản thứ hai với Message-ID mới. Tạo thư mục output cha trước khi chuyển log của từng lượt vào đó.
