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
