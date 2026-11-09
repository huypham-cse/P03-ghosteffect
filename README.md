# GhostEffect (MobiSys 2027)

Repo làm việc của bài *GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents*: bản thảo, artifact mô phỏng, dữ liệu đo trên emulator và testbed.

Bài nộp theo kiểu double-blind: không thêm tên người, email hay đường dẫn máy vào bất kỳ file nào sẽ vào bài hoặc vào gói artifact.

## Bắt đầu từ đâu

| File | Dùng để |
|---|---|
| `team/PHAN_CHIA_CONG_VIEC.md` | Ai làm phần nào, lịch, phụ thuộc và yêu cầu nghiệm thu |
| `team/SETUP.md` | Cài máy và các lệnh chạy |
| `review.md` | Bản phản biện nội bộ; checklist cuối file là nguồn việc |
| `resolve.md` | Quyết định cách sửa cho từng điểm review (R01 đến R32) |
| `STATUS.md` | Trạng thái hiện tại của bài |

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `manuscript/` | Bản thảo LaTeX. `generated/` do script sinh ra, không sửa tay |
| `artifact/` | Script mô phỏng, CSV kết quả (`results/`), dữ liệu đo trên emulator (`results/real/`, chỉ được thêm), test và `run_all.py` |
| `testbed/` | Rig emulator: fault proxy, driver, grader, harness cho LLM agent |
| `others/notes.md` | Sổ tra macro nào lấy từ CSV nào |
| `codex/` | Tài liệu tham khảo cho phần B: commit pin của model, giao thức chạy agent, cách cài máy, nhật ký các lần đã chạy |
| `team/` | Kế hoạch làm việc của nhóm |

## Lệnh nhanh

```bash
cd manuscript && sh build.sh                        # build PDF
python3 -m unittest discover -s artifact/tests      # test artifact
python3 artifact/run_all.py --output-dir ../ge-run --jobs 4   # chạy lại toàn bộ mô phỏng (Linux hoặc WSL)
```
