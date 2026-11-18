# Nhật ký phần C (Bá Nguyên)

Theo `team/RULES.md` §1.8: chỉ thêm mục mới; không sửa hoặc xóa mục cũ.

## 09/11/2026 — Chuẩn bị C-01, C-02 và C-10

**Nhánh:** `c/eval`, tạo từ `main` sạch tại `a518b5f`.
Thay đổi hiện ở working tree, chưa commit, chưa mở PR và chưa merge.

**Tài liệu đã đọc:** `CONTRIBUTOR_FIXED.md`, `RULES.md`, `STATUS.md`,
`artifact/README.md`, `review.md`, `resolve.md`; xem nội dung abstract/intro
trong PDF hiện có và các source/renderer/kiểm thử liên quan. PDF hiện có 20
trang; đó là PDF cũ, chưa phải bản build từ thay đổi của buổi này.

### C-01 — Đang làm; chưa đạt nghiệm thu

Đã chuẩn bị phần cơ học trên nhánh C:

- Tách `render_realsim.py` chứa Table 4, REAL4 và macro `Rsim*`.
- Tách file macro: `render.py` ghi `macros.tex`; publisher trong
  `render_real.py` ghi `macros_real.tex`, gồm `Real*` và `Ledger*` hiện có;
  `render_guarantee.py` là khung rỗng cho A ghi `macros_guarantee.tex`.
- Chuyển phần ledger renderer sang B; giữ nguyên công thức và giá trị.
- Tách `07-realsim.tex`, tạo `07-agent.tex` rỗng cho B, tách
  `appendix-results.tex`; thêm các input tương ứng.
- Chuyển input `tab-position` vào §2.2. Không sửa các nhận định của A/B.
- Giữ cơ chế staging/rollback: lỗi đọc CSV hoặc lỗi publish không thay
  directory generated trước đó.
- Thêm tùy chọn `--notes-output` và sinh lại `others/notes.md` bằng code.

**Đối chiếu:** renderer trước và sau tách, dùng cùng CSV đang có, cho đúng
**972 tên/giá trị macro** và **19 bảng/hình giống từng byte**. Có kiểm tra
riêng việc chuyển nguyên văn nội dung `07-real.tex` sang file mới.
Hai lần render cho đầu ra giống nhau. Không thay seed, ngân sách, calibration
logic hoặc CSV; không chạy lại ledger benchmark của B.

**Chênh lệch đã phát hiện từ trước khi tách:** render từ CSV hiện có khác
macro đã commit ở **59 mục** (54 giá trị thay đổi, 5 macro mới), gồm
`NsizeProdTwo` 221 → 193, `SimSrcAsk` 47.4 → 47.0 và các macro ledger.
`LedgerFullPfifty`/`LedgerFullPninetyfive` thành `--` trên CSV hiện có;
B-15 vẫn phải cung cấp phép đo host phù hợp. Chênh lệch không phải do việc
tách renderer. Generated TeX hiện đã được sinh lại từ CSV lưu trong repo;
không coi đây là số liệu mới từ một lượt chạy mô phỏng sạch.

Danh sách đầy đủ, hash đầu vào/đầu ra và trạng thái PARTIAL ở
`artifact/runs/2026-11-09/MANIFEST.json`. A/B cần xem các macro đổi trước
khi tích hợp. Chưa gửi nhóm chat hoặc liên hệ người khác thay người dùng.

**Bị chặn:** máy hiện tại là Windows; `wsl --list --quiet` báo WSL chưa cài.
`run_all.py` từ chối chạy với mã thoát 2 vì cần POSIX SIGKILL. Không bỏ guard
hoặc thay Windows terminate thành phép đo SIGKILL. Máy cũng chưa có
pdflatex/BibTeX/TeX Live nên chưa build PDF thật. Các test build dùng command
fixtures chỉ kiểm failure propagation, không thay được build TeX.

### C-02 — Soạn xong đề xuất; chờ duyệt chung

Đã tạo `team/QUYET_DINH_CHUNG.md`: product khi có cơ sở cấu trúc cho A2,
joint nếu không có cơ sở A2 và đủ điều kiện chứng nhận, ASK khi không chứng
nhận được; app tự retry idempotent thì không GUI retry. Chọn từ ask trong
văn xuôi, thống nhất Outbox evidence và cách ghi loại kết quả.

Chưa có xác nhận của trưởng nhóm/A/B. Các tên macro của A/B trong phân công
vẫn là ví dụ, chưa giả định chúng đã được freeze. Còn cần trưởng nhóm xử lý
chỉ thị cũ không sửa paper trong `resolve.md` và chỉ định người nghiệm thu.
Yêu cầu hiện tại của người dùng cho phép chuẩn bị thay đổi để review trên
nhánh C; không tự ghi nhận quyết định tập thể hoặc merge vào main.

### C-10 — Đã triển khai và kiểm thử; chưa đưa lên main

- `team/scrub_check.sh`: quét đệ quy đường dẫn máy, tên/tài khoản/email,
  chuỗi giống token/key, private key và file/thư mục nội bộ. Báo file, dòng,
  loại lỗi; không in giá trị bí mật. Lỗi input thoát 2, phát hiện thoát 1,
  sạch thoát 0. PDF metadata và nội dung archive cần kiểm riêng.
- `team/readability_count.py`: stdlib, thống kê từng file, câu quá 45 từ,
  dấu chấm phẩy từng đoạn, para/emph; có JSON và chế độ strict. Mặc định
  giới hạn cộng dồn một vai trò; `--scope paper` dùng giới hạn cả bài.
- `artifact/tests/test_eval.py`: 7 kiểm thử, có fixture nhạy cảm giả và
  trường hợp URL HTTPS hợp lệ không được báo thành đường dẫn máy.

Scrub PASS trên `manuscript/`, `artifact/scripts/`, `artifact/tests/`.
Tài liệu nội bộ `team/` có tên thành viên nên không phải gói ẩn danh.
C-10 còn cần PR và trưởng nhóm merge trước hạn 13/11.

### Kiểm chứng và lỗi đã gặp

- Artifact: **41 test**, **40 đạt**, **1 skip** do cần POSIX; đã chạy cả
  đối chiếu SciPy độc lập bằng `uv run --python 3.11 --with scipy`.
- Testbed: **70 test**, **66 đạt**, **4 skip** do thiếu Android/integration.
- Test mới: chia quyền macro, không trùng tên, deterministic output và
  rollback toàn bộ macro khi CSV campaign 2 bị thiếu đều đạt.
- `git diff --check`: đạt.
- Đã cài Python 3.11.18 bằng uv cho công cụ artifact; không sửa môi trường
  agent Python 3.11.8 của B.
- Lượt đọc PDF đầu tiên lỗi encoding console; chạy lại với `-X utf8` đọc
  được. pypdf cảnh báo ToUnicode trên PDF cũ; chưa sửa PDF.
- Lượt so đầu tiên phát hiện thụt lề trong string bảng sau khi bọc function;
  đã sửa để 19 bảng/hình trở lại giống từng byte với baseline.
- Lượt scrub đầu báo nhầm URL HTTPS; đã sửa boundary của regex và thêm
  trường hợp HTTPS vào kiểm thử trước khi ghi nhận PASS.

**Baseline độ dễ đọc phần thân bài của C:** 18 `para`, 34 `emph`, 17 câu
quá 45 từ, 16 đoạn có hơn một dấu chấm phẩy. Giới hạn phần C là 5/10/0/0.
Đây là baseline source trước biên tập C-06/C-08/C-09/C-11, chưa phải PASS.

### Việc tiếp theo

1. Trên Linux/WSL có Python, TeX Live và poppler-utils: chạy suite từ main
   sạch vào workspace mới theo RULES §2.3.2, so CSV, lưu manifest chạy thật.
   Branch hiện tại chuẩn bị refactor; không gọi working tree này là main sạch.
2. Sau khi review và promote kết quả theo đúng chủ file, kiểm renderer và
   build PDF trên nhánh C; xác nhận layout, citation/ref, giới hạn trang.
3. Trưởng nhóm/A/B duyệt tài liệu chung và hợp đồng macro; trưởng nhóm merge
   các PR tách theo task. Các file A/B đổi trong nhánh này chỉ thuộc ngoại lệ
   tách cơ học C-01, cần được chủ file review.
4. Tiếp tục C-03 sau khi baseline dữ liệu được chốt; C-04/C-06 và biên tập
   dùng macro tạm trong khi chờ số A/B. Chưa thực hiện C-03 đến C-09 hoặc C-11
   đến C-13 trong buổi khởi động này.

## 09/11/2026 — Cài môi trường để tiếp tục C-01

Theo yêu cầu của người dùng, đã chạy trình cài WSL chính thức bằng quyền
quản trị qua UAC. Kết quả: WSL 3.0.3.0 được cài; kernel 6.18.54.1-1;
VirtualMachinePlatform bật thành công; trình cài thoát 0. Windows báo rõ
thay đổi chỉ có hiệu lực sau khi reboot. Không tự reboot máy người dùng.

Lệnh cài Ubuntu-24.04 trước reboot chỉ trả thông báo cần reboot; chưa xác
nhận distro chạy được và chưa cài LaTeX. Đã chuẩn bị trong thư mục git-ignore
`tmp/wsl-setup/`: `install-latex.sh` (TeX Live, BibTeX, Poppler, Python/SciPy
và kiểm tra các package acmart/algorithm/pgfplots/newtx), cùng
`resume-setup.ps1` để tiếp tục cài Ubuntu và chạy script sau reboot.
Transcript và kết quả installer giữ cục bộ ở `install.log`, `result.json`;
không đưa log chứa danh tính máy vào artifact.

C-01 vẫn đang làm: bước tiếp theo cần người dùng lưu công việc và reboot,
sau đó chạy/kiểm chứng Ubuntu, cài LaTeX và chạy pipeline theo quy tắc nhóm.

## 10/11/2026 — WSL/LaTeX hoàn tất; chạy thật C-01 và build PDF

**Nhánh:** vẫn là `c/eval`; chưa commit/PR/merge. Người dùng đã reboot và yêu
cầu tiếp tục cài đặt. Không mở chiến dịch Android, agent hoặc VLM.

### Môi trường — Đã cài và kiểm chứng

- WSL 3.0.3, Ubuntu 24.04.5 LTS chạy WSL2, kernel 6.18.54.1.
- Python 3.12.3 và SciPy qua apt; không thay venv agent của B.
- TeX Live 2023, pdfTeX 1.40.25, BibTeX 0.99d, latexmk, Poppler 24.02.0.
- Đủ acmart, algorithm/algpseudocode, TikZ/pgfplots, newtx và bộ font.
- Lượt build đầu thiếu `binhex.tex`; cài thêm `texlive-plain-generic`, cập
  nhật script cài đặt và build lại thành công. Không chỉnh source toán để
  tránh lỗi môi trường. Script shell dùng LF để chạy được trong Linux.
- Chi tiết phiên bản package ở `artifact/runs/2026-11-10/ENVIRONMENT.json`.
  Log cài đặt giữ trong `tmp/wsl-setup/` đã git-ignore.

### C-01 — Chạy pipeline và phần tách cơ học đạt kiểm tra kỹ thuật

1. Tạo checkout `main` riêng ở `tmp/c01-main`, commit
   `a518b5f0628d8864b43b2ac34c137d40d9bdac12`; kiểm trạng thái sạch trước và
   sau lượt chạy bằng Git của Windows. Không chạy thí nghiệm từ working tree
   đang sửa của nhánh C.
2. Chạy `python3 artifact/run_all.py --output-dir
   /root/ghosteffect-runs/c01-20261110 --jobs 4` bằng WSL trên checkout đó.
   **25/25 job thoát 0**, gồm mọi mô phỏng, 16 tag REAL4, sample size, phép đo
   SIGKILL POSIX thật và renderer. Không đổi seed, code chứng nhận hay budget.
3. Promote **48 CSV tổng hợp của C**, kèm file `.meta.json` ghi lệnh, commit,
   seed/biểu thức seed, hash script/CSV, Python, ngày và loại host. **47 file
   giống từng byte với archive**. `planner_sim.csv` chỉ khác ba giá trị
   p-value ở mức sai số floating-point (không đổi outcome/count/rate):
   rules `p_err` 0.8576646516117299 → 0.8576646516117297;
   ghost-nocal `p_dup` 0.05714154868081257 → 0.05714154868081256;
   ghost-uniform `p_err` 0.8576646516117299 → 0.8576646516117297.
4. Không thay `artifact/results/ledger_bench.csv` của B. Receipt đo mới nằm
   tại `artifact/runs/2026-11-10/ledger_bench_run.csv`; phép đo này đạt và
   không được dùng để tự sửa phần Implementation của B.
5. Không thay dữ liệu dưới `artifact/results/real/`. Hash các input gốc được
   đối chiếu với manifest đầu lượt chạy, và Git Windows xác nhận không diff.
   Git Linux mặc định khác thiết lập CRLF của Git Windows, nên đã dùng hash
   byte để tránh kết luận nhầm rằng log/SUMMARY cũ bị sửa.
6. Render lại cùng các CSV sau promote bằng renderer main chưa tách và
   renderer C đã tách: **972 macro giữ nguyên tên/giá trị**, **19 bảng/hình
   giống từng byte**. Sinh lại `others/notes.md` bằng renderer.
7. So với generated TeX đã commit, vẫn có **59 mục macro khác** như báo cáo
   09/11. Danh sách đầy đủ ở `macro_changes_vs_committed_tex` trong manifest;
   đây là tài liệu để A/B review, chưa gửi tin nhắn ra ngoài thay người dùng.

**Điểm cần B review:** `real_params.py` trên main sinh hai mô tả provenance
mới cho `elem_tail_ub` và `k9_failed_commit`; các cột name/value đều giống
archive. Mô tả mới phân biệt order-statistic reference với common-window
censoring và xác nhận chỉ 8/20 lượt có tap Send-messages được ghi nhận.
C giữ nguyên `params.csv` do B sở hữu và lưu toàn bộ diff mô tả trong
`b_owned_params_provenance_changes_not_promoted`. Vì vậy chưa tuyên bố mọi
CSV của repo trùng toàn bộ output lượt chạy hoặc phần C đã nghiệm thu.

Manifest chính: `artifact/runs/2026-11-10/MANIFEST.json` (pipeline PASS,
không phải xác nhận nghiệm thu của nhóm). Bản PARTIAL ngày 09/11 được giữ
nguyên làm lịch sử, không thay bằng dữ liệu giả hoặc sửa log cũ.

### Build và kiểm tra

- `sh manuscript/build.sh`: thoát 0 sau khi bổ sung gói TeX thiếu.
- PDF mới: **20 trang**, max overfull **7.89293 pt**, 0 ref/citation chưa
  định nghĩa, 0 chuỗi `??`; metadata không có trường tác giả lộ tên.
- **Conclusion ở trang 13, References bắt đầu trang 13.** Cổng cuối yêu cầu
  Conclusion hết ở trang 12 nên vẫn chưa đạt; để C-06 và các lượt biên tập
  sau xử lý, không tự rút nội dung A/B trong bước tách cơ học.
- Artifact: **41/41 test đạt**, không skip; gồm đối chiếu SciPy và đường
  lỗi runner POSIX mà lần trước Windows chưa chạy được.
- Testbed: **70 test**, **67 đạt**, **3 skip** do thiếu integration Android.
- Chạy thêm 5 test renderer sau khi promote dữ liệu: đạt hết, gồm ownership,
  deterministic output và rollback khi CSV thiếu/publish lỗi.
- Scrub: PASS trên manuscript, code/test artifact và receipts ngày 10/11.
- Git whitespace check dùng `-c core.whitespace=cr-at-eol` để nhận đúng CRLF
  do CSV writer xuất ra; không thay bytes CSV chỉ để làm đẹp diff.

### Trạng thái và bước tiếp theo

- Cài WSL/LaTeX: **xong**; không còn blocker môi trường của C-01.
- C-01: **đã chạy xong và kiểm chứng phần kỹ thuật**, còn review B về metadata
  và review/PR của nhóm; chưa tự nghiệm thu.
- C-02: đề xuất đã soạn, còn trưởng nhóm và A/B chốt trước 11/11.
- C-10: công cụ đã kiểm chứng cả Windows và Linux, còn PR/merge trước 13/11.
- Tiếp theo: chốt các điểm review trên, chia PR theo task; sau đó C-03
  (baseline cùng dữ liệu) và C-04/C-06 (bảng và cấu trúc bài). Các việc này
  chưa được báo là hoàn thành chỉ vì môi trường và pipeline đã chạy được.

## 10/11/2026 — Chuẩn bị PR riêng C-01

Đã cấu hình tác giả Git theo tên Bá Nguyên và email người dùng cung cấp.
Đã fetch origin: main vẫn ở a518b5f. Chọn riêng thay đổi C-01 vào index;
C-02 và công cụ/test C-10 chưa nằm trong commit này. Có bản sao an toàn
working tree ở `tmp/pre-pr-backup/` (không commit).

Kiểm tra trên snapshot chỉ chứa nội dung staged của C-01:
**34/34 artifact test đạt**, build thật thoát 0, PDF 20 trang, max overfull
7.89293 pt. Con số 41 test ở mục trước là snapshot phát triển có thêm 7
test công cụ C-10; không coi cả 41 test là nội dung PR C-01.

Trạng thái: commit C-01 chuẩn bị để review, không phải PR nghiệm thu cuối.
Còn chờ đăng nhập GitHub để push/mở PR; C-02 và C-10 sẽ có commit/PR riêng.
Hai provenance của B và giới hạn body trang 13 vẫn còn mở như đã báo.

## 10/11/2026 — Commit riêng C-10

C-02 được lưu ở commit d901d5b và nhánh `c/02-conventions`.
Đưa riêng hai công cụ kiểm và 7 test của chúng vào commit C-10. Đã chạy lại
7/7 test trên WSL: PASS. Không thêm dependency runtime ngoài Python stdlib
và shell. Trạng thái: code và test sẵn sàng review; còn PR/merge lên main
trước 13/11. Nhánh PR này nối tiếp C-02 để mỗi diff chỉ chứa một task.

Tiếp theo: push ba nhánh sau khi xác thực GitHub; tiếp tục C-03 trong nhánh
phát triển. C-01/C-02/C-10 chưa được tự đánh dấu nghiệm thu hoặc merge.

## 11/11/2026 — C-10 cập nhật main và kiểm tra lại

Đã rebase C-10 trực tiếp lên main sau squash-merge #10; PR #12 không còn
phụ thuộc tài liệu C-02. Xung đột nhật ký được giải bằng cách giữ phần main
và chỉ nối mục C-10. Một lệnh sửa bằng Windows python thất bại do alias Store;
đã dùng Python WSL, sửa sạch dấu xung đột trước khi publish.
Lần kiểm đầu sau checkout có lỗi scrub vì Git Windows đổi shell script sang
CRLF. Đã đặt *.sh text eol=lf trong .git/info/attributes (chỉ máy local) và
chuẩn hóa shell script; không thay code hay dữ liệu để né test.
Bộ artifact trên nhánh C-03 kế thừa C-10: 46/46 test qua trên WSL sau sửa
môi trường. C-10 triển khai xong, chờ review/merge #12; không tự nghiệm thu.
Tiếp theo: retarget #12 về main, kiểm build và scrub trước publish.
## 10/11/2026 — C-03: freeze thiết kế trước thí nghiệm

Thêm bốn tag match2k, match5k (Element), matchk9 và matchk9sent. Mỗi tag
so rules-vetted với ghost-joint bằng cùng bản ghi calibration và cùng object
lag table. Budget 2.000 nhãn/outcome (và/class khi keyed) đi cùng 2.000 lag;
Element có thêm cấu hình 5.000/5.000. Các seed, budget rủi ro, tag lịch sử,
pilot/holdout và công thức joint không đổi.

Đã xác nhận AST: chỉ hai hàm cũ của C là vetting/run đổi; không sửa các hàm
hiệu chuẩn/chứng nhận của A. Hàm mới chỉ tạo input chung rồi gọi certifier
hiện có. Có 4 test C-03 mới: cùng object dữ liệu, cùng kết quả certifier cũ,
ngân sách/tag đúng và từ chối input thiếu/sai. Artifact 45/45 test PASS.

Đây là commit thiết kế trước khi chạy các tag mới, chưa có kết quả để chọn
cấu hình theo ý muốn. Bước tiếp theo chạy riêng tag mới từ snapshot commit
sạch của C-03, lưu rõ source branch/commit; không gọi đó là một lần rerun
pipeline từ main, và không thay 16 CSV REAL4 lịch sử.

## 10/11/2026 — C-03: kết quả cùng dữ liệu, renderer và văn bản

Thiết kế đã freeze ở d87fb23 trước khi thu kết quả. Chạy bốn tag mới từ
snapshot commit sạch `tmp/c03-frozen`; job thoát 0, source commit, hash input,
seed và command nằm trong `artifact/runs/2026-11-10/C03-MANIFEST.json`.
Chỉ thêm bốn CSV mới và metadata; không thay 16 CSV REAL4 lịch sử, dữ liệu
thô, baseline parameters hoặc các công thức chứng nhận của A.

| Profile | Nhãn/lag | Vetted ASK | Joint ASK | P_v quan sát |
|---|---|---|---|---|
| Element, keyed | 2.000/2.000 | 2,2% | 100% | Cả hai 0 |
| Element, keyed | 5.000/5.000 | 7,8% | 30,6% | Cả hai 0 |
| K-9 không Sent | 2.000/2.000 | 100% | 100% | Cả hai 0 |
| K-9 có Sent | 2.000/2.000 | 100% | 100% | Cả hai 0 |

Nhãn tính theo outcome và class khi keyed; bảng lag cũng keyed tương ứng.
Mỗi cấu hình dùng năm seed đã định, tổng 12.000 workflow. Các dòng đều là
mô phỏng với luật tham số đo, không phải phép đo GUI/agent mới. Vetted có
zero observed error không đồng nghĩa nó có certificate như joint.

Kết quả vetted 2,2% ở dòng 2k khác ví dụ 5,3% trong phân công do nay dùng
chính các records và lag của joint thay vì draw riêng của baseline cũ. Đã
kiểm trước kết quả rằng joint_from_matched cho cùng output với certifier
cũ trên cùng RNG/records. Không tune seed hoặc budget để ép ra 5,3%.

Đã thêm bảng generated `tab_matched.tex` và macro RsimMatch*, giữ đầy đủ
cả hai policy cho ba profile. Renderer từ chối budget/metadata không khớp,
và test chứng minh lỗi đó không ghi đè output đã publish. Bỏ tỷ lệ rules
K-9 khỏi abstract; sửa intro/evaluation/realsim để phân biệt fixed-wait
unvetted rules dưới giả định lag K-9 với vetted rules dùng input chung.
Các câu liên quan số liệu B còn cần B duyệt trong PR.

Kiểm tra: **46/46 artifact test PASS**, build PDF thật thoát 0, 20 trang,
max overfull 7.89293 pt, không ?? hoặc ref/cite chưa định nghĩa. Scrub PASS
trên manuscript, code/test artifact và receipts. Conclusion vẫn trang 13;
đó là việc biên tập C-06, không coi bản này đạt cổng nộp cuối.

Trạng thái C-03: triển khai/thí nghiệm/bảng/văn bản xong để review; chưa
nghiệm thu. C-01/C-02/C-10 có nhánh/commit riêng; vẫn chờ người dùng hoàn
thành GitHub device login để push và tạo các PR nối tiếp, không tự merge.

## 18/11/2026 — C-10 cập nhật bộ đếm readability cho mã giả

Thêm môi trường `algorithmic` vào danh sách khối không phải văn xuôi của
`team/readability_count.py`. Bổ sung test bảo đảm dấu chấm phẩy và câu dài
trong Algorithm 1 không bị tính như câu văn. Đây là sửa công cụ dùng chung,
giúp YC-12 của phần A chạy đúng trên mã giả mà không thay đổi nội dung A.

## 18/11/2026 — C-07 rà soát related work

Đã tách câu so sánh Agent libOS khỏi câu RFC 1047 để mỗi nguồn có phạm vi
riêng. Câu mới nêu rõ Agent libOS kiểm soát capability và checkpoint quanh
tool dispatch, còn GhostEffect xử lý effect GUI đã externalize. Bib đã pin
Agent libOS ở v3; `others/citation-audit.md` ghi URL nguồn và lý do không thêm
Gray--Reuter hoặc Bailis.

## 18/11/2026 — C-20 device and emulator evidence

Thêm vào §8 hai câu dùng macro B-19: kết quả K-9 trên physical Android phone,
kết quả lmkd trên emulator và DAVx5 dưới kill/Doze, ghi rõ loại phép đo và
giới hạn chưa đo quản lý pin của hãng. Không sửa file sở hữu của B và không
đưa số gõ tay vào văn bản. C-20 cần được kiểm lại cùng C-14/C-16 sau khi chuỗi
agent và evaluation rebase lên main.

## 18/11/2026 — C-12 kiểm đường dẫn dữ liệu phụ thuộc host

README artifact và README nhúng trong bundle đều ghi rõ
`artifact/results/ledger_bench.csv` là file phụ thuộc host. Bundle vẫn yêu
cầu cây `artifact`, `testbed`, `manuscript` sạch, tạo manifest từ commit hiện
tại, loại tài liệu nội bộ và chỉ scrub sau khi giải nén.

## 18/11/2026 — C-14–C-19 rà soát agent và conclusion

Đã chỉnh phần văn bản sở hữu C để khuyến nghị certification có điều kiện theo A2,
mô tả đúng thí nghiệm agent trên emulator, và thay các câu cũ về agent/RQ7 trong
evaluation. Conclusion hiện báo cáo các số agent bằng macro `Agent*`; các số mới vẫn
cần review khi nội dung C-20 và các PR dữ liệu được tích hợp.

## 19/11/2026: C-04 sửa theo review #57 (trưởng nhóm sửa trên nhánh)

`\RsimFitLateObs` lấy số lượt quan sát của một họ muộn (ba họ có cùng số lượt, cùng số sai, renderer kiểm), nên caption Table 4 và §7.3 ghi 0/99 lượt đọc mỗi họ, không cộng thành 297. Caption `tab_nsize` trở lại "certified at δ/4" (δ trong caption là min(α,β)/(10K), keyed theo 4 lớp chia thêm 4, khớp `sample_size.py` và δ ở §4.3 với n_cls = 4). Render lại `tab_nsize`, `tab_planner`, `tab_realsim` và `others/notes.md` cho khớp renderer.

## 19/11/2026: C-05 sửa theo review #58 (trưởng nhóm sửa trên nhánh)

Thêm test: `render.py` phải thoát lỗi khi `planner_seed_variance.csv` thiếu hoặc trùng một dòng (thử đột biến: bỏ đoạn kiểm thì test fail). Renderer kiểm câu ở phụ lục (một seed duy nhất kéo SD của vetted rules trên Element), caption ghi loại số (model-based và measured-parameter simulation), câu phụ lục bỏ chữ "four" viết tay. Gộp `main` (#57), `tab_planner` khớp renderer. Meta còn ghi `git_commit` 09a20fd (trước force-push); chạy lại với code đã commit cho cùng số đếm, số thực lệch tối đa 1,2e-12; freeze 21/11 sẽ sinh lại meta.

 

## 10/11/2026 — Trạng thái publish sau C-03

Đã commit C-01 (84aa339), C-02 (d901d5b), C-10 (afb023a), thiết kế C-03
(d87fb23) và kết quả C-03 (c3e6ab5). Các nhánh c/01-pipeline,
c/02-conventions, c/10-checks, c/03-matched đã có; c/eval giữ toàn bộ chuỗi
phát triển. Working tree sạch sau các commit, chưa push hoặc mở PR.

Đã cài GitHub CLI portable từ release chính thức, kiểm SHA-256. GitHub
plugin được khai báo installed nhưng không có tool repo khả dụng trong phiên
này, nên dùng CLI. Device login đầu tiên hết thời gian chờ mà chưa được
xác nhận. Lệnh tự mở trình duyệt bị automatic approval review từ chối với
lý do 'blocked by policy'; không thử cách khác để vượt chặn đó. Người dùng
cần tự mở trang GitHub device login để hoàn tất xác thực. Không ghi token
hoặc mã đăng nhập vào repo.

Mô tả cho bốn PR đã chuẩn bị ở tmp/pr-bodies/ (git-ignore), nêu đúng test,
manifest, kết quả bất lợi và các điểm review còn mở. Khi xác thực xong,
push các nhánh và tạo PR nối tiếp theo từng task; chỉ trưởng nhóm merge.

## 10/11/2026 — Push và mở bốn PR thành công

Người dùng đã hoàn tất đăng nhập CLI trực tiếp trong Terminal. Đã xác minh
account GitHub LeNguyenBaNguyen có quyền push repo huypham-cse/P03-ghosteffect.
Đã push bốn nhánh và kiểm tra lại các PR trên GitHub:

| Task | Nhánh | PR | Base |
|---|---|---|---|
| C-01 | c/01-pipeline | https://github.com/huypham-cse/P03-ghosteffect/pull/10 | main |
| C-02 | c/02-conventions | https://github.com/huypham-cse/P03-ghosteffect/pull/11 | c/01-pipeline |
| C-10 | c/10-checks | https://github.com/huypham-cse/P03-ghosteffect/pull/12 | c/02-conventions |
| C-03 | c/03-matched | https://github.com/huypham-cse/P03-ghosteffect/pull/13 | c/10-checks |

Tất cả ở trạng thái draft. Các PR nối tiếp để mỗi diff chỉ chứa đúng task;
sau khi trưởng nhóm squash/merge PR trước, cần rebase và retarget PR sau
lên main tương ứng trước khi merge tiếp. Không tự merge, không yêu cầu
review/nhắn người khác bằng công cụ, không nhận thay xác nhận A/B.

Các mô tả PR có test/manifest và ghi rõ điểm còn mở: provenance do B sở hữu,
đề xuất C-02 chưa được nhóm duyệt, phần body vẫn kết thúc trang 13 và chưa
đạt cổng nộp cuối. C-03 giữ đầy đủ kết quả bất lợi cho joint.

Tiếp theo: nhóm review C-01 trước để gỡ chờ A/B; phía C tiếp tục C-04
(chú thích và nguồn số của Table 4), C-05 (variance theo seed), C-06
(cấu trúc evaluation và rút độ dài). Đăng nhập không còn là blocker.

## 11/11/2026 — C-02 sau khi C-01 được squash-merge

C-01 đã được trưởng nhóm duyệt và merge tại PR #10. Đã rebase C-02 lên
main mới, giữ PR #11 chỉ chứa tài liệu quy ước và nhật ký của C-02.
Review của trưởng nhóm xác nhận nội dung đúng R06. A đã cung cấp hợp đồng
105 macro tại PR #9; không nhận thay quyết định hoặc sự đồng ý của A/B.
C-02 còn chờ trưởng nhóm chốt quyền sửa paper, chỉ định người nghiệm thu C,
và hợp đồng Agent*/LabelTrial* từ B theo review #11 ngày 11/11.
Tiếp theo: retarget #11 về main; chờ xác nhận để chốt tài liệu, không tự merge.
## 11/11/2026 — C-04 Table 4 và cập nhật chuỗi PR

C-01 đã được duyệt/merge #10. Đã rebase #11 và #12 lên main rồi retarget
cả hai về main; #13 vẫn dựa #12 để không lẫn thay đổi công cụ vào diff C-03.
Các bản trước rebase được giữ ở backup/c02-pre-main, backup/c10-pre-main,
backup/c03-pre-main. Không chạy lại thí nghiệm C-03; receipt vẫn chỉ đến commit
thiết kế lịch sử d87fb23 đã có trước CSV. Việc rebase không đổi dữ liệu hay seed.
C-10 kiểm độc lập tại tmp/c10-review: 41 test qua, build 20 trang, không ref
chưa định nghĩa, overfull lớn nhất 3,46388 pt. Log nằm trong worktree local.

C-04: renderer lấy số workflow/ngân sách nhãn từ CSV, kiểm nhất quán giữa
các policy; lấy số đo late Element từ CSV campaign2 chỉ đọc. Caption và văn
bản phân biệt calibration/test cùng fitted law với reader trên màn hình thật;
giữ kết quả zero late family errors 0/99 và pairwise cofailures 0/101, không
đánh đồng hai mẫu số. Bỏ số 12.000, 2.000, 5.000 viết cứng trong caption/nhãn.
Thêm 7 macro Rsim* cho số đếm; không thay tên macro/schema cũ hoặc số liệu.
Chưa dẫn nhãn bảng ngân sách chưa merge của A; dùng sec:design-probes hiện hữu.

Validation C-04: 47 test artifact qua; build 20 trang, không ref/cite chưa định
nghĩa, overfull lớn nhất 3,46388 pt; scrub manuscript/scripts/tests PASS.
Sinh lại others/notes.md. Không thay CSV/raw measurements hay hàm của A/B.
C-04 xong triển khai, chờ review; vẫn cần A review cách diễn giải ngân sách.
Tiếp theo: C-06 cấu trúc đánh giá và rút bài; C-05 seed variance; C-02 chờ
quyết định trưởng nhóm/hợp đồng B. Chỉ trưởng nhóm merge và người khác nghiệm thu.
## 11/11/2026 — C-06 sắp lại đánh giá và rút phần thân

Đưa emulator, agent placeholder và measured-parameter simulation lên trước
model-based comparison. Chuyển RQ1/RQ2, cấu hình chi tiết, so sánh baseline và
ablation đầy đủ xuống appendix-results; giữ mọi kết quả bất lợi. Renderer sinh
bảng model gọn 6 policy và bảng đầy đủ riêng ở phụ lục, không xóa CSV hay kết quả.
Bảng vetted matched vẫn ở phần fitted-law: planner_sim.csv chưa có dòng vetted
matched trong default model; không ghép số từ thế giới khác thành một hàng giả.
Cần review yêu cầu hàng vetted của C-06 trước khi nghiệm thu toàn bộ task.

Sửa delta trong setup và caption tab_nsize theo công thức A-05 (#17), có số lớp;
đưa StressNover cạnh kết quả stress, và rút planned study thành một câu.
Build đầu thất bại do bỏ label sec:device-plan còn được B dẫn; đã giữ label ở
câu scope/future work. Lỗi cú pháp renderer khi tách biểu thức đã sửa trước build.
Bản cuối build 21 trang tổng, Conclusion ở trang 12 (trước là 13), không ref/cite
thiếu; overfull còn 3,46388 pt ở discussion chưa xử lý. 47 test artifact qua,
scrub manuscript/scripts/tests PASS. Macro values và CSV không đổi; notes sinh lại
để chỉ đúng vị trí văn bản mới. C-06 xong phần cấu trúc/rút bài, chờ review; chưa
nghiệm thu toàn task, đặc biệt hàng vetted cùng mô hình và readability C-11.

Tổng việc còn lại: C-02 chờ quyết định lead/hợp đồng B; C-10 chờ review #12;
C-03 chờ review #13; C-04 chờ review #26; C-05 seed variance chưa triển khai;
C-07 related work, C-08 abstract, C-09 intro/discussion/conclusion, C-11 readability,
C-12 anonymous bundle còn phải làm. Chỉ chốt nhận định agent khi B có dữ liệu thật.
C-13 là freeze/submit đúng lịch, không thực hiện sớm hoặc tự nghiệm thu thay nhóm.

## 11/11/2026 — C-05 freeze thiết kế trước khi chạy

Đóng băng part seedvariance: dùng nguyên SEEDS 101,202,303,404,505 và 2.400
workflow mỗi seed; alpha/beta mặc định, không sửa ngân sách hoặc calibrator.
Dòng model: redo, theorem-only, always-ask, rules, product, joint. Dòng measured:
Element 2k/5k, K9 không/có Sent, product/joint, đúng ngân sách Table 4 hiện hữu.
Xuất riêng từng seed (70 dòng), báo mean/sample SD/range, không coi SD là CI.
Sẽ kiểm weighted pooled metrics khớp CSV gốc trước khi promote. Part mới được
commit trước output, chạy trong workspace riêng từ snapshot commit sạch;
đây là thí nghiệm bổ sung theo seed, không gọi là rerun toàn pipeline trên main.
Không đổi dữ liệu raw hoặc số aggregate cũ. C-05 đang làm; chưa có kết quả.


## 11/11/2026 — C-05 kết quả theo seed và kiểm pooled equivalence

Đã chạy snapshot thiết kế db47f5595b07a24dc4365203e086d43f8ad37919 trong
/root/ghosteffect-runs/c05-20261111; chỉ part mới, không phải full main rerun.
70 dòng (14 policy/profile × 5 seed), giữ nguyên toàn bộ seed/budget. Cả 14
nhóm đều khớp n,n1,n0 và weighted pooled ask/dup/loss/cdup/closs của CSV cũ
(sai số tối đa cho phép 1e-10). Không thay các CSV aggregate cũ hoặc raw.
Receipt tại artifact/runs/2026-11-11/C05-MANIFEST.json; CSV kèm .meta.json.

Sinh tab_seed_variance ở phụ lục: mean ± sample SD và range asking; không gọi
SD là CI, không lấy trung bình CP interval. Có test kiểm tách seed không đổi
workflow/effect counts và renderer từ chối seed trùng mà giữ output cũ.
Lần test đầu phát hiện import planner_sim không hoạt động khi renderer chạy
qua runpy; đã load bằng đường dẫn script để không phụ thuộc sys.path.
Bản cuối 49 test qua, build 22 trang, không ref/cite thiếu; scrub PASS.
Chỉ thêm macro SimSeedCount, không đổi giá trị macro kết quả cũ; notes sinh lại.
C-05 xong triển khai và thí nghiệm, chờ review/merge; không tự nghiệm thu.
Tiếp theo: hoàn thiện C-06 model-vetted trên cùng label records/lag table,
đóng băng thiết kế riêng trước khi sinh CSV; sau đó C-07 và C-11/C-12.


## 11/11/2026 — C-06 freeze model-vetted trước kết quả

Thêm part modelmatched riêng: giữ default model, passive calibration population,
2k labels/outcome/app, 20k lag samples và 5 seed/2.400 workflows như Table 2.
So joint/vetted bằng cùng record objects và lag table objects; product giữ
calibrator cũ, dùng làm control cùng joint để kiểm tương đương aggregate cũ.
Chỉ mở guard trong helper C-owned matched_labels bằng flag matched_model;
không sửa calibrator của A hoặc lịch sử thí nghiệm C-03. Vetted ở đây dùng
passive labels đúng default model, không gọi là fault-injected labels.
Commit thiết kế trước output. Dự kiến thêm một dòng vetted vào bảng model,
chỉ publish nếu hai control product/joint khớp CSV cũ. C-06 vẫn đang làm.

C-06 lần chạy đầu dừng ở guard measured-only trong vetting, chưa sinh CSV.
Đã mở guard C-owned chỉ khi matched_model; không đổi seed/budget. Giữ receipt
FAIL tại workspace c06-model-20261111, commit sửa trước lần chạy v2.


## 11/11/2026 — C-06 model-vetted và hoàn thiện baseline

Run v2 từ commit 206a7cfd3c052997dad2de90f3b92b463fb67f39 thành công.
Vetted dùng cùng passive label records/lag objects với joint trong default
model; không đánh đồng với measured/fault-injected experiment của C-03.
Vetted hỏi 100%, P_v 0% (CP upper 0,0446064%); product/joint khớp CSV cũ về
n,n1,n0,dup,loss,ask,cdup/closs và CP bounds, thời gian (tol 1e-10).
Giữ nguyên raw/aggregate cũ, thêm planner_model_matched.csv cùng .meta.json.
Receipt PASS và receipt FAIL đầu ở artifact/runs/2026-11-11/C06-*.json.

Đưa đủ 7 baseline chính vào bảng model; renderer kiểm control tương đương
trước khi publish. Thêm 3 SimModelVetted* macro, không đổi giá trị macro cũ.
Test kiểm cùng record objects/lag object, control decisions không đổi và
renderer rollback khi control khác. Lần test đầu dùng lag budget nhỏ cho
model nhưng lag_tables model cố định 20k; đã sửa fixture dùng ngân sách thật,
không sửa A-owned lag_tables hoặc số liệu để né lỗi. Bản cuối 52 test qua;
build 22 trang không ref/cite thiếu, overfull 3,46388 pt; scrub trên manuscript,
scripts/tests/receipts PASS. notes.md sinh lại. C-06 xong triển khai, chờ review
và nghiệm thu độc lập, kể cả A review công thức delta và thuật ngữ.

C-12 precheck trên toàn artifact/testbed báo email và internal runs, nên chưa
đóng gói/phát hành. Cần phân loại địa chỉ giả/Message-ID trước khi làm gói;
không sửa raw dữ liệu và không tự coi mọi chuỗi giống email là danh tính thật.
Tiếp theo: C-07 kiểm nguồn related work, C-11 readability và C-12 bundle;
C-08/C-09 chỉ chốt các nhận định agent sau khi B có kết quả thật.

## 19/11/2026: C-06 sửa theo review #59 (trưởng nhóm sửa trên nhánh)

Gộp `main` (có #55, #57, #58). Phần seed variance (C-05) lấy đúng bản của #58 trên `main`: `SEED_CASES`, `part_seedvariance`, CSV, meta và khối render; #59 không còn đổi seed hay CSV nào ngoài `planner_model_matched` (hết vấn đề YC-08 và trùng phạm vi). Khối kiểm model-matched (C-06) giữ nguyên. Câu mở §7 nêu đủ loại số như #55; các sửa của #55 ở phần Setup và stress (nay nằm trong phụ lục) được áp lại. Thêm kiểm `replace` của bảng planner; caption `tab_nsize` theo #57 (δ/4); bỏ "RQ2", "RQ4 and RQ5" ở phụ lục; §7 dẫn Table `tab:planner`. Render lại `tab_planner`, `tab_planner_extended`, `notes.md`. Build: Kết luận và References bắt đầu ở trang 13.

## 19/11/2026: C-01, C-18 sửa theo review #63 (trưởng nhóm sửa trên nhánh)

Xóa `artifact/runs/2026-11-17/MANIFEST.json` (bản 11-18 đã thay; bản cũ còn đường dẫn máy, scrub lỗi). `run_all.py`: khi thư mục không có `.git` (gói ẩn danh của `make_bundle.sh`) thì lấy `source_commit` từ `BUNDLE-MANIFEST.json`, `source_tree_clean` để `None`, thay vì dừng với lỗi git; có test. Gộp `main` và sinh lại `others/notes.md` từ macro hiện tại (có `\RealRent*`). `macros_guarantee.tex` nay trùng `main` (A đã gộp ở #73). Manifest 11-18 lấy từ 0729af4, trước #76; freeze 21/11 chạy lại toàn bộ.
