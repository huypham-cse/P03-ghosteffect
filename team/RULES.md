# Luật làm việc

> Áp dụng cho cả nhóm từ 09/11/2026 đến khi nộp bài.
> **Thành viên:** A là Gia Huy, B là Trung Nguyên, C là Bá Nguyên.
> **Trưởng nhóm:** Trung Nguyên (tài khoản GitHub `nguyennguyen938-debug`). Mọi chỗ "báo trưởng nhóm" trong file này là báo Trung Nguyên.
> `team/CONTRIBUTOR_FIXED.md` quyết định **ai làm gì và khi nào**; file này quyết định **làm như thế nào**. Hai file mâu thuẫn thì báo trưởng nhóm.

---

## 1. Luật chung

### 1.1 Sở hữu file
1. Mỗi file chỉ có một chủ, theo bảng sở hữu ở `team/CONTRIBUTOR_FIXED.md` §2. Chỉ sửa file của mình.
2. `artifact/scripts/planner_sim.py` là ngoại lệ duy nhất, chia theo hàm: A giữ các hàm hiệu chuẩn và chứng nhận, C giữ phần còn lại. Cần thêm gì thì thêm hàm mới, không sửa hàm của người kia.
3. Cần đổi file của người khác thì nhắn chủ file hoặc mở issue. Góp ý câu chữ thì bình luận trong PR, không sửa thẳng.
4. File chưa có tên trong bảng sở hữu thì hỏi trưởng nhóm trước khi sửa.

### 1.2 Git, nhánh và PR
1. **Không commit thẳng vào `main`.** Mỗi phần làm trên nhánh của mình: `a/...`, `b/...`, `c/...`.
2. Commit message và tiêu đề PR bắt đầu bằng ID task, ví dụ `[B-06] harness cho M3A`. Mỗi PR chỉ làm một việc.
3. Trước khi mở PR: rebase lên `main`, `sh manuscript/build.sh` chạy qua, test qua, và chạy `team/scrub_check.sh` trên các file đã sửa (script có từ 13/11).
4. Chỉ trưởng nhóm merge vào `main`, theo kiểu squash.
5. Chạy `git status` trước mỗi commit.

### 1.3 Không bao giờ commit
`runtime/`, `testbed/runs/`, `tmp/`, `*.local.json`, `.env`, khóa API, token, mật khẩu, ảnh chụp màn hình có thông tin cá nhân, file log lớn.

### 1.4 Số liệu
1. Không gõ tay con số kết quả vào `.tex`. Mọi số đi qua macro do script sinh ra.
2. Không sửa tay bất kỳ file nào trong `manuscript/generated/`.
3. Mỗi câu có số phải nói rõ loại số: đo trên emulator, mô phỏng theo mô hình, mô phỏng với tham số đo, tính chính xác, hay chạy LLM agent.
4. Tiền tố macro theo phần: A dùng `\Cert*`; B dùng `\Real*`, `\Agent*`, `\Ledger*`, `\LabelTrial*`; C dùng `\Sim*`, `\Rsim*` và các tiền tố cũ khác.
5. Tên macro và schema CSV chốt ngày 11/11. Sau đó muốn đổi phải báo cả nhóm và được trưởng nhóm duyệt.
6. Chưa có số thì dùng giá trị tạm `??`. Bản nộp không được còn `??`.
7. Mỗi CSV mới có file `<tên>.meta.json` ghi lệnh chạy, git commit, seed, phiên bản Python, ngày và host.

### 1.5 Trung thực với kết quả
1. Không đổi seed, họ luật, ngân sách nhãn, `N_LAG` hay file freeze sau khi đã thấy kết quả. Nếu buộc phải đổi thì làm trong commit riêng, ghi lý do, và trước khi sinh các CSV chịu ảnh hưởng.
2. Dòng kết quả bất lợi cho GhostEffect vẫn phải vào bài. Giấu dòng bất lợi là vi phạm nặng.
3. Dữ liệu thô trong `artifact/results/real/**` chỉ được thêm, không sửa, không xóa. `SUMMARY.md` chỉ được thêm đoạn mới.
4. Mẫu số bằng 0 thì ghi N/A, không ghi 0.
5. Số trong bản thảo cũ chỉ để minh họa; lần chạy mới là chuẩn. Có chênh lệch thì báo, không chỉnh seed để khớp số cũ.

### 1.6 Ẩn danh và bảo mật
1. Bài nộp double-blind: không đưa tên người, email, tài khoản GitHub hay đường dẫn máy vào bản thảo, artifact hoặc testbed.
2. Khóa API và token chỉ để trong `.env`, không đưa vào receipt, log hay tin nhắn nhóm.
3. Thí nghiệm chỉ dùng nội dung giả và tài khoản thử; không gửi thư thật, không dùng tài khoản cá nhân.

### 1.7 Viết bài
1. Dùng thuật ngữ trong `team/QUYET_DINH_CHUNG.md` (có từ 11/11), ví dụ chỉ dùng một trong hai từ ask hoặc escalate.
2. File của mình phải đạt mức độ dễ đọc ở YC-12: không câu nào quá 45 từ, mỗi đoạn tối đa một dấu chấm phẩy.
3. Trích dẫn mới phải kiểm với nguồn thật và ghi vào `others/citation-audit.md` kèm DOI hoặc URL.
4. Không thêm phần cảm ơn hay bất cứ chi tiết nào làm lộ danh tính.

### 1.8 Báo cáo tiến độ (bắt buộc)
1. **Luôn cập nhật tiến độ theo những gì đã làm.** Mỗi phần có một file nhật ký riêng do chủ phần giữ: `team/a-log.md`, `team/b-log.md`, `team/c-log.md`. Sau mỗi buổi làm việc, và trước khi mở hay cập nhật PR, thêm một mục có ghi ngày gồm:
   - đã làm gì, theo ID task, kèm commit hoặc PR;
   - trạng thái từng task vừa đụng tới: chưa làm, đang làm, xong, hoặc bị chặn (kèm lý do);
   - việc làm tiếp theo.
2. Nhật ký chỉ được thêm, không sửa hay xóa mục cũ. Ghi cả việc hỏng và lần chạy thất bại.
3. Mỗi PR liệt kê các ID task liên quan cùng trạng thái, và phải kèm phần cập nhật nhật ký tương ứng.
4. Hai ngày liền không có mục nhật ký mới thì trưởng nhóm coi phần đó đang bị chặn và sẽ hỏi lại.
5. Bị chặn (thiếu số của người khác, thiếu máy, lỗi không tự gỡ được) thì nhắn ngay trên nhóm chat, đồng thời ghi vào nhật ký.
6. Gặp một trong các mốc báo động sau thì báo trưởng nhóm ngay trong ngày:
   - emulator chưa chạy ổn vào 12/11;
   - chưa có model vào 13/11;
   - A-dev thành công dưới 6/10 vào 15/11;
   - chưa đủ 10 episode hợp lệ vào 17/11;
   - thấy phần của mình không kịp xong vào 19/11 (báo trước 17/11);
   - build trên `main` đỏ quá một ngày.

### 1.9 Nghiệm thu
Mỗi phần mở PR nghiệm thu chậm nhất 19/11. Người nghiệm thu không phải chủ phần, tự chạy lại mọi lệnh kiểm, và chỉ nghiệm thu khi đạt hết yêu cầu. Nhật ký tiến độ (1.8) phải đầy đủ thì mới được nghiệm thu. Chi tiết ở `team/CONTRIBUTOR_FIXED.md` §7.

---

## 2. Luật riêng

### 2.1 Phần A: Gia Huy (lý thuyết, bảo đảm, hiệu chuẩn)
1. Đổi định nghĩa, định lý hay thuật toán thì sửa luôn chứng minh và mọi chỗ dẫn tới nó trong cùng một PR.
2. Chỉ đọc CSV do C chạy. Cần thêm tag mô phỏng thì nhờ C, không tự chạy lại pipeline để đổi số.
3. Mọi thay đổi trong các hàm hiệu chuẩn của `planner_sim.py` phải có test trong `artifact/tests/test_guarantee.py`.
4. Không dùng con số minh họa thay cho số tính từ CSV (ví dụ `0.05 × 72.9%`).

### 2.2 Phần B: Trung Nguyên (đo đạc và LLM agent)
1. Commit file freeze trước lượt chạy chính thức đầu tiên. Sau đó không đổi model, decoding, prompt, task, horizon hay luật kết quả.
2. Mỗi episode được chạy lại tối đa một lần, và chỉ khi lỗi đo. Giữ mọi lần chạy, kể cả lần hỏng.
3. Chỉ backend quyết định có trùng hay không. Agent và controller không được thấy kết quả của backend.
4. Không sửa mã agent upstream. Sửa phần nối (binding) thì làm trong `testbed/` và kèm test.
5. Không tắt các guard để lấy PASS. Lỗi gặp phải ghi vào `team/b-log.md` theo ngày.
6. Mỗi AVD chỉ chạy một thí nghiệm một lúc; không chạy song song trên cùng cổng adb.
7. Không đổi schema `params.csv`, `episodes.csv`, `label_cost.csv`. Số trong `params.csv` đổi thì báo C để chạy lại Table 4.
8. Chạy agent xong ngày nào thì báo C số đếm thô ngay ngày đó.

### 2.3 Phần C: Bá Nguyên (đánh giá và câu chuyện của bài)
1. C-01 chỉ làm thay đổi cơ học (chạy lại, tách file, tách macro), không sửa nội dung của A và B khi tách.
2. Chỉ chạy lại pipeline trên `main` sạch. Mỗi lần đưa kết quả mới vào repo phải kèm manifest và báo A, B danh sách macro đổi.
3. So sánh với baseline phải dùng cùng dữ liệu cho cả hai bên.
4. Câu nào trong abstract, §1, §8, §10 nói về phần của A hoặc B thì phải được chủ phần đó duyệt trong PR.
5. Lượt đọc cuối chỉ gửi đề xuất cho file của người khác, không sửa thẳng.
6. Sau freeze 21/11 không chạy thêm gì; chỉ được thêm link artifact vào §8.
7. Gói artifact không chứa `tmp/`, `codex/`, `team/`, `review.md`, `resolve.md`, `runtime/`, `.git`, và phải qua scrub check trước khi tải lên.
8. Sau mỗi lần đưa kết quả mới vào repo, sinh lại `others/notes.md`.

### 2.4 Trưởng nhóm: Trung Nguyên
1. Merge vào `main`, chỉ định người nghiệm thu cho từng phần. Phần B do chính trưởng nhóm làm nên phải giao cho Gia Huy hoặc Bá Nguyên nghiệm thu.
2. Duyệt mọi thay đổi về hợp đồng (tên macro, schema) sau 11/11.
3. Ra các quyết định còn treo ở `team/CONTRIBUTOR_FIXED.md` §8.

---

## 3. Khi vi phạm
1. PR vi phạm luật bị trả lại cho chủ phần, chưa merge. PR không kèm cập nhật nhật ký tiến độ cũng bị trả lại.
2. Vi phạm luật trung thực (1.5) hoặc ẩn danh, bảo mật (1.6) phải báo trưởng nhóm ngay và sửa trước mọi việc khác. Lỡ commit khóa API thì thu hồi khóa đó ngay, không chỉ xóa khỏi repo.
