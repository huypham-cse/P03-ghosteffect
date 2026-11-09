# Cài đặt và lệnh chạy

Phân việc, lịch và yêu cầu nghiệm thu nằm ở `team/CONTRIBUTOR_FIXED.md`. File này chỉ ghi cách cài máy và các lệnh chạy.

## 1. Lấy repo

```bash
git clone https://github.com/huypham-cse/P03-ghosteffect.git
cd P03-ghosteffect
git checkout -b a/theory      # B dùng b/measure, C dùng c/eval
```

## 2. Build bản thảo (cả ba phần)

Cần một bản LaTeX có `acmart`, `pgfplots`, `tikz`, `algorithmicx`, cùng Python 3.10 trở lên (chỉ dùng thư viện chuẩn), vì `build.sh` chạy `render.py` trước khi build.

- Linux hoặc WSL: `sudo apt install texlive-full`, hoặc TeX Live 2023 trở lên.
- macOS: MacTeX.
- Windows: TeX Live hoặc MiKTeX; chạy `build.sh` từ Git Bash hoặc WSL.
- Lệnh kiểm trong yêu cầu nghiệm thu cần thêm `poppler-utils` (`pdftotext`, `pdfinfo`) trên Linux hoặc WSL.

```bash
cd manuscript
sh build.sh      # render generated/*.tex từ artifact/results, rồi pdflatex, bibtex, pdflatex hai lần
```

`build.sh` cố ý dừng khi có lỗi LaTeX hoặc ref, citation chưa định nghĩa.

## 3. Artifact và mô phỏng (chủ yếu phần C)

Artifact chỉ dùng thư viện chuẩn của Python nhưng cần môi trường POSIX: bài test ledger dùng SIGKILL nên không chạy trên Windows thuần. Dùng **Linux hoặc WSL2 Ubuntu**.

```bash
python3 --version                                   # 3.10 trở lên; ghi lại phiên bản chính xác
python3 -m unittest discover -s artifact/tests -v
python3 -m unittest discover -s testbed/tests -v    # vài test bỏ qua khi chưa có môi trường Android, như vậy là bình thường
```

Chạy lại toàn bộ (khoảng 25 đến 30 phút với 2 job; nhiều nhân thì tăng `--jobs`):

```bash
python3 artifact/run_all.py --output-dir "$PWD/../ge-run-$(date +%Y%m%d-%H%M)" --jobs 4
```

Runner chép script và dữ liệu đầu vào sang thư mục đầu ra và ghi manifest gồm hash và mã thoát của từng job. Runner không ghi đè `artifact/results/` hay `manuscript/`; muốn đưa kết quả vào repo thì phải chép có chủ ý.

Chỉ cài SciPy nếu cần bộ đối chiếu độc lập cho test: `pip install scipy`.

## 4. Rig emulator và LLM agent (phần B)

`runtime/` không có trong git nên phải dựng lại. Máy cũ chạy Windows 10 với WHPX và AVD x86_64 API 33; Linux với KVM cũng chạy được và nhanh hơn. Chọn một host và giữ nguyên host đó suốt đợt đo.

```bash
python -m unittest discover -s testbed/tests -v       # test trên host; test Android bỏ qua cho tới khi cài xong
python testbed/preflight.py --output testbed/runs/preflight-01.json
```

Sau đó làm theo mục cài Android và backend trong `testbed/README.md`. Tóm tắt:

| Bước | Lệnh (chạy từ thư mục gốc repo) | Kiểm |
|---|---|---|
| Android SDK, emulator, image API 33 r17 | `python testbed/setup_android.py --bootstrap` | Có `BOOTSTRAP.json`, `emulator -accel-check` thoát 0 |
| AVD | `python testbed/setup_avd.py --java <đường dẫn java 17 trở lên> --install --create --verify-apks --output testbed/runs/avd-01` | Có AVD `ghosteffect_api33_x86_local` |
| APK K-9 và GreenMail | `python testbed/setup_assets.py --only com.fsck.k9_39046.apk greenmail.jar` | SHA khớp file lock |
| Forwarder của AndroidWorld | `python testbed/setup_assets.py --lock testbed/agent-assets.lock.json --only 2024.05.13-accessibility_forwarder.apk` | SHA khớp |
| Mã nguồn agent và venv Python 3.11.8 | `python testbed/setup_agents.py --output testbed/runs/agents-01` (task B-02, cần `uv`): clone AndroidWorld vào `runtime/vendor/` đúng commit pin, tạo `runtime/agent-venv` | Script in `READY`; `runtime/agents/SETUP.json` có commit đúng pin |
| Smoke GreenMail | `python testbed/smoke_greenmail.py --java <đường dẫn java> --output testbed/runs/mail-smoke-01` | PASS |
| Quan sát native của AndroidWorld | `python testbed/smoke_android.py --verification <RESULT.json kiểm APK> --only <apk K-9> --native-env-capture --output testbed/runs/native-01` | Có screenshot và cây accessibility, định danh cửa sổ khớp |

Các bước cụ thể với server H100 80GB của nhóm nằm ở `testbed/RUNBOOK_B.md`.

**Model:** Qwen2.5-VL-7B BF16 chạy trên vLLM 0.11.0 cần GPU từ 24 GB trên Linux. Máy GPU có thể là máy thuê theo giờ, nối về máy chạy emulator qua SSH tunnel, vì `testbed/local_model.py` và `testbed/native_episode.py` chỉ nhận endpoint loopback hoặc SSH forward. Khóa và token chỉ để trong `.env` (đã git-ignore); mẫu biến môi trường ở `codex/.env.example`.

**Lỗi đã gặp trên máy cũ** (ghi trong `codex/resolve-progress.md`): hộp thoại ANR của SystemUI, cây accessibility rỗng, focus guard báo lỗi, cây onboarding không ổn định.
- Không tắt các guard để lấy PASS.
- Giữ các lần thất bại trong `testbed/runs/` (đã git-ignore) và ghi tóm tắt vào `team/b-log.md`.
- Smoke có kịch bản chỉ qua được khi chạy emulator với `--gpu host`.
- Không chạy hai smoke hay hai thí nghiệm cùng lúc trên một AVD hoặc cổng adb 5038.

## 5. Không commit

`runtime/`, `testbed/runs/`, `*.local.json`, `.env`, khóa API, ảnh chụp màn hình có thông tin cá nhân. Kiểm `git status` trước mỗi commit.
