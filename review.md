# Hồ sơ phản biện MobiSys 2027: GhostEffect — Khôi phục hiệu ứng chỉ qua GUI theo ngữ nghĩa đúng một lần với ngân sách rủi ro cho tác tử di động

**Thư mục bài báo:** `/Users/xuanbachle/Workstation/MobiSys2027/papers/P03-ghosteffect/`  
**Ngày:** 2026-11-07  
**PDF:** `manuscript/main.pdf`, 20 trang (`main.log`: "Output written on main.pdf (20 pages)").  
**Độ dài nội dung chính so với giới hạn 12 trang:** Vừa đúng giới hạn, không còn dư chỗ. Theo `main.aux`, Mục 10 (Kết luận) nằm ở trang 12, Tài liệu tham khảo bắt đầu ở trang 13, Phụ lục A (Chứng minh) ở trang 15 và Phụ lục B (Kết quả bổ sung) ở các trang 17–20. Nội dung chính dài đúng 12 trang; tài liệu tham khảo (2 trang) và phụ lục (6 trang) không tính vào giới hạn. Có ba hộp nội dung tràn lề (*overfull boxes*), lớn nhất 7,9 pt.

**Tài liệu đã đọc (toàn bộ):** `manuscript/main.tex`; mọi tệp trong `manuscript/sections/` (tóm tắt, giới thiệu, bối cảnh–động lực, mô hình, lý thuyết, thiết kế, triển khai, đánh giá, 07-real, thảo luận, công trình liên quan, kết luận, appendix-proofs, tab-apps, tab-position); `manuscript/generated/macros.tex` (459 macro; mọi macro được trích bên dưới đều đã được thay bằng giá trị thực) cùng toàn bộ 18 bảng và hình được sinh tự động; `manuscript/figures/` (fig1.tex, fig-arch.tex, icons/); `STATUS.md`; `others/notes.md`; `others/citation-audit.md` (123 mục, tất cả đều được đánh dấu đã xác minh). Chỉ đọc lướt `reviews/round1..4` và `reviews/self-review.md` để nắm lịch sử; các nhận xét phản biện dưới đây được viết mới.

**`07-real.tex` có được đưa vào không?** Có. `07-evaluation.tex` nạp `generated/real_section.tex`, rồi tệp này nạp `sections/07-real`. Việc đưa vào phụ thuộc vào sự tồn tại của `artifact/results/real/SUMMARY.md` khi biên dịch; tệp này có tồn tại, nên RQ7 (Mục 7.7) xuất hiện trong PDF.

**Trạng thái bản thảo.** `STATUS.md` mô tả một bản sửa vòng 3 đã hoàn tất. Tuy nhiên, artifact đã phát triển xa hơn: `artifact/scripts/planner_sim.py` chứa mã bổ sung về sau (mốc thời gian, kích thước bảng độ trễ, quy tắc đã được thẩm định; bảng `REAL4` tại dòng 1870–1900), và `artifact/results/planner_real4_*.csv` chứa kết quả tương ứng. `render_real.py` không đọc các kết quả đó và không mục nào nhắc đến chúng. Việc phản biện dựa trên bản thảo hiện tại; các nhận xét sẽ chỉ ra những chỗ nội dung bài báo chưa phản ánh đầy đủ artifact của chính mình.

**Kiểm tra đối chiếu một số kết quả trong artifact (đọc CSV, không chạy lại):**

| # | Khẳng định trong bài báo (đã thay macro bằng giá trị) | Nguồn trong artifact | Kết quả |
|---|---|---|---|
| 1 | Thao tác làm lại qua GUI có kịch bản tạo bản sao ở 20/20 lần gửi K-9 | `campaign2/c2_k9_nosent_trials.csv` (12 dòng `recompose_server_copies=2`) + `c2_k9_sent_trials.csv` (8 dòng) | Khớp |
| 2 | CalDAV: 8/8 đúng một lần; làm lại tạo bản sao ở 3/3 | `campaign2/c2_caldav_trials.csv`: 9 lượt thử, 8 phản hồi bị bỏ, `server_copies_window=1` ở 9/9 và `recompose_server_copies=2` ở 3/3 | Khớp |
| 3 | Element: 83/83 đúng một lần; 65 dùng cùng `txnId`, 18 qua `/sync` | Dòng `ALL_interrupted(respdrop)` trong `c2_element_outcomes.csv` | Khớp |
| 4 | Độ trễ p50/p90/max: kill -9 = 4,0/8,0/13,6; force-stop = 11,9/12,3/12,7; mạng = 2,4/2,7/2,9; không lỗi = 2,5/2,9/3,8; không có mẫu bị kiểm duyệt (*censored*) | `c2_element_lag.csv` | Khớp |
| 5 | Lượt đọc muộn sai 0/99; không có hai nhóm bằng chứng cùng sai 0/101 (CI 0–3,7%); lượt đọc đầu trả `bottom` 33/101; lượt đọc đầu có quan sát nhưng sai 3/68 | `c2_element_families.csv`, `c2_element_cofailure.csv` | Khớp |
| 6 | Bảng 4, Element: product hỏi 3,0%; joint 72,9%; chỉ định lý 37,2%; rules 9,0%/3,1%; joint hỏi 12,7% với 5.000 nhãn; product dùng nhãn thụ động có `P_v` 14,59; product với đuôi trễ là 2,77 | `planner_real.csv` | Khớp |
| 7 | Bảng 4, K-9: rules có `P_v` 65,85 (không có Sent), 28,91 (có Sent); passive joint 9,85; trust-app 27,67 | `planner_real.csv` | Khớp |
| 8 | Bảng 2: product 0,05/24,9; joint 0,05/66,7; rules 0,52/23,9; chỉ định lý 73,0; làm lại 63,3 | `planner_sim.csv` | Khớp |
| 9 | Synapse: thiết bị khác tạo bản sao; bản ghi quá 24 giờ tạo bản sao | `c2_synapse_txn.csv` | Khớp |
| 10 | Sổ ghi dưới qemu SIGKILL: FULL mất 0 bản ghi (3 thử nghiệm), OFF mất 15–158 bản ghi trong 3/3 thử nghiệm | `ledger_powerloss.csv` qua SUMMARY.md | Khớp |
| 11 | Bảng 4 nêu ngân sách nhãn "2.000 / 5.000 cho mỗi lớp" | `planner_sim.py`: `N_LAG = 20000`; `planner_real4_lag5k.csv` (joint hỏi 30,6% với 5.000 mẫu độ trễ), `lag2k.csv` (100%) | **Thông tin bị bỏ sót:** các bảng độ trễ chứa 20.000 mẫu độ trễ bootstrap mỗi lớp, bất kể số nhãn được nêu; bài báo không nói rõ |
| 12 | Mục 3 và Thuật toán 1 chờ từ `t0` (lúc nhấn); độ trễ ở Bảng 3b tính từ lúc mở lại ứng dụng | `real_params.py` dòng 69; `planner_real4_t0down5.csv` (`P_v` 18,8% product, 29,9% joint nếu chờ tính từ lúc nhấn, với 5 giây ngừng hoạt động) | **Không nhất quán giữa mô hình và phép đo**, chưa được thảo luận |
| 13 | "Joint vẫn đạt ràng buộc chỉ vì phải hỏi 74,4%" dưới đuôi độ trễ không được ghi nhận (2.000 nhãn) | `planner_real4_tail5.csv`: với 5.000 nhãn, joint có `P_v` 2,01% (CP 2,32) | Đúng ở 2.000 nhãn, sai ở mốc 5.000 nhãn được nhấn mạnh; bài báo chưa đề cập |

Tất cả số liệu được in ra đều khớp. Các mục 11–13 cho thấy văn bản bài báo trình bày hẹp hơn dữ liệu sẵn có trong artifact.

---

## Phản biện 1 — Thành viên PC cấp cao chuyên hệ thống di động (ứng dụng Android, accessibility, tác tử chạy trên thiết bị)

**Tóm tắt bài báo.** Bài báo đặt tên cho một dạng lỗi của tác tử thao tác GUI di động: khi bị gián đoạn giữa thao tác nhấn để commit và việc nhận xác nhận, hệ thống để lại một "hiệu ứng ma" (*ghost effect*) mà tác tử không thể đọc lại kết quả; thực hiện lại qua GUI sẽ gửi thêm một lần nữa. Trên Android 13 emulator với máy chủ tự lưu trữ, K-9 Mail giữ một email đã được chấp nhận trong Outbox dưới dạng lỗi vĩnh viễn; một kịch bản thao tác lại tạo bản sao ở 20/20 email K-9 và 3/3 sự kiện CalDAV. Element và DAVx5 tự phục hồi nhờ cơ chế retry có tính idempotent của ứng dụng. GhostEffect là một tầng phục hồi gồm: sổ ghi SQLite kiểu write-ahead trong bộ điều khiển nằm ngoài tác tử; một mã nonce được nhập vào trường văn bản tự do; ba nhóm bằng chứng từ văn bản accessibility (outbox, nonce, bản tóm lược lịch sử) cùng một nhóm VLM; khoảng chờ được chứng nhận theo độ trễ hiển thị; và planner quyết định thử lại, tuyên bố hoàn thành hoặc hỏi người dùng theo ngân sách rủi ro trùng/loss. Các giới hạn được hiệu chuẩn bằng Clopper–Pearson trên những thao tác bị tiêm lỗi. Đánh giá bao gồm mô phỏng dựa trên mô hình, một chiến dịch 149 lượt thử emulator và mô phỏng được tham số hóa lại từ số liệu đo.

**Điểm tổng thể:** 3 (Nghiêng về chấp nhận / Weak accept)  
**Mức độ chuyên môn reviewer:** 4 (Chuyên gia)  
**Điểm thành phần (1–5):** Tính mới 3; tính vững chắc kỹ thuật 3; đánh giá thực nghiệm 2; mức độ quan trọng/tác động 3; trình bày và diễn đạt 3.

**Điểm mạnh**
- Phát hiện về K-9 (Mục 7.7, Bảng 3a, Hình 1) là một quan sát hệ thống cụ thể và có thể tái lập: sau khi mất phản hồi SMTP, K-9 24.0 ghi `send_state=error`, bỏ qua thư ở các lần đồng bộ tiếp theo, giữ thư trong Outbox và không bao giờ ghi nó vào thư mục IMAP Sent (0/8). Đây là lần đầu tôi thấy hiện tượng gửi trùng do "hiệu ứng ma" của GUI agent được đo trực tiếp.
- Cách nhìn hai chặng (*two-hop*, Mục 4.4) chuyển câu hỏi "retry có an toàn không?" thành một tính chất có thể kiểm tra riêng từng ứng dụng (G2), với thời hạn khử trùng (*dedup horizon*) được đo (Synapse: cùng thiết bị, 24 giờ; bản ghi quá hạn gây trùng lặp).
- Quy tắc đọc bằng chứng ở Mục 6 (mặc định `bottom` trừ khi đã xác minh package, tên phòng và timeline; chỉ kết luận "không tồn tại" trên màn hình đã cuộn đến đúng vị trí và có mốc neo) là điều một trình đọc cây accessibility cần có nhưng hiếm khi được nêu rõ.
- Ledger được đặt đúng vị trí (ngoài tác tử, ghi trước thao tác, WAL với `synchronous=FULL`) và đã thử nghiệm bằng qemu SIGKILL.
- Phạm vi được công bố trung thực: "Chúng tôi chưa chạy tác tử LLM và chưa thử trên điện thoại thật" (Mục 1).

**Điểm yếu (sắp theo mức độ nghiêm trọng)**
1. **Chưa chạy một tác tử nào (Mục 6, 7.7, 7.8).** Hiện tượng gửi trùng được tạo bởi driver có kịch bản, "soạn lại và gửi lại cùng nội dung, như một tác tử tin vào màn hình sẽ làm". Việc M3A, UI-TARS hay AgentProg có thực sự làm vậy trước trạng thái lỗi của K-9 hay không quyết định ý nghĩa đóng góp; trong khi bộ thử nghiệm đã có. Chạy một tác tử LLM trên 20 lượt thử K-9 có thể giải quyết câu hỏi.
2. **Kiến trúc chạy trên thiết bị — khía cạnh quan trọng với MobiSys — mới ở mức thiết kế (Mục 5.1).** "Chúng tôi đã xây dựng lõi ra quyết định và ledger của kiến trúc chạy trên host; dịch vụ trên thiết bị mới là thiết kế." Chưa đo hành vi của bộ điều khiển dạng foreground service dưới LMK, chi phí đọc của accessibility service hay độ trễ từ ghi `ISSUED` đến trước thao tác nhấn trên điện thoại. Như bài báo đã thừa nhận, thời gian trên host (thêm bản ghi 0,04 ms trên laptop macOS) không phải số đo trên điện thoại.
3. **Độ bao phủ ứng dụng chỉ gồm ba client mã nguồn mở với server tự lưu trữ (Bảng 8).** Phân loại G2 yêu cầu quan sát được server. Với Gmail, WhatsApp, Signal hoặc ngân hàng, không thể quan sát thời hạn dedup; `FLAG_SECURE` chặn ảnh chụp màn hình và `accessibilityDataSensitive` ẩn view (Mục 8). Cần nói thẳng điều gì còn dùng được với ứng dụng đóng: ledger có; nonce chỉ khi có trường dành riêng cho người dùng; G2 không rõ; vậy mọi thao tác bị gián đoạn đều phải hỏi người dùng.
4. **Vị trí đặt nonce mâu thuẫn giữa các phần.** Mục 5.2: "Theo mặc định GhostEffect chỉ dùng các trường mà phía đối tác không thể nhìn thấy." Hình 1(b): "Nonce gx:7K2Q9F được nhập vào tiêu đề". Bảng 8: trường của K-9 là "nội dung email (hiển thị cho người nhận)". Thí nghiệm thực tế dùng tiêu đề (theo `SUMMARY.md` trong artifact). Nhãn ở tiêu đề hiển thị với người nhận và làm thay đổi email mà người dùng đã yêu cầu. Cần sửa phần mặc định hoặc Hình 1.
5. **Độ trễ được đo không phải độ trễ được mô hình hóa (Mục 3 so với Bảng 3b).** `T` tính "từ t0 đến khi hiệu ứng trở nên hiển thị"; `t0` là thời điểm `ISSUED` trước khi nhấn, và Thuật toán 1 chờ từ `t0`. Nhưng Bảng 3b đo "độ trễ từ lúc phục hồi tới lúc hiển thị", bắt đầu từ ý định mở lại ứng dụng. Trên điện thoại, thời gian từ nhấn đến mở lại có thể kéo dài hàng phút (Doze, người dùng quay lại muộn). Planner chờ tính từ `t0` nhưng dùng bảng đo từ lúc mở lại sẽ chờ thiếu. Bài báo không nêu planner dùng mốc đồng hồ nào.
6. **Ngữ nghĩa kết thúc tiến trình trên emulator khác điện thoại thật (Mục 6, 7.7).** `am kill` không có tác dụng với Element (13/13); độ trễ force-stop (12 giây) "chủ yếu là điều hướng" của test harness chứ không phải của ứng dụng; chưa thử LMK dưới áp lực bộ nhớ, Doze hay trình quản lý pin của nhà sản xuất.
7. **Chưa đo VLM** ("nhóm VLM được loại bỏ chứ không mô hình hóa", `params.csv`). Nhận định "VLM là nguồn phụ yếu để phá thế hòa" (Mục 7.4) là kết luận từ mô phỏng.

**Nhận xét chi tiết cho tác giả**
1. Mục 2.1 viết rằng ứng dụng foreground "về cơ bản hầu như không bao giờ bị thu hồi tiến trình". Emulator cho thấy `am kill` không kết thúc Element vì thành phần đồng bộ khiến ứng dụng luôn ở trạng thái hệ thống có thể nhận biết. Cần nói rõ ý nghĩa với phân bố lỗi: với ứng dụng G2 có foreground sync service, ứng dụng chết có thể hiếm còn tác tử chết lại phổ biến.
2. Mục 5.3: "Hop 1 đọc cơ sở dữ liệu cục bộ của ứng dụng." Không có quyền root, bộ điều khiển không thể đọc cơ sở dữ liệu của ứng dụng khác; thực tế nó đọc màn hình Outbox qua cây accessibility. Hãy chỉnh văn bản đúng với triển khai (`uiautomator dumps`).
3. Mục 5.3: một nhãn tốn "khoảng 15 giây". Các thử nghiệm campaign 2 sử dụng cửa sổ 120–300 giây cộng thời gian mở lại. Cần đối chiếu và tính lại chi phí cho 5.000 nhãn trên mỗi lớp và mỗi kết quả, nhân bốn lớp.
4. Mục 7.7: "Bảy lượt thử Element bị mất trước khi ghi được một dòng (sáu do hộp thoại ANR của hệ thống)." ANR tự nó là một gián đoạn mà tác tử phải đối mặt. Nếu những lần gửi đó đã commit, chúng phải được đưa vào bảng độ trễ dưới dạng quan sát kiểm duyệt (*censored*), chứ không bị loại bỏ.
5. Mục 7.7, thử nghiệm giữ lại phản hồi: Element hiển thị Sent thông qua echo `/sync` trước khi client timeout sau 70 giây. Vì vậy, một kết quả đọc "đã commit" có thể xuất hiện trước xác nhận của chính ứng dụng. Hãy nói A1 và điều kiện của hop 1 có bao quát đường đi này không.
6. Nhánh G2 ở Hình 1 viết "sau khi chờ được chứng nhận, bản ghi hiển thị Sent, đã commit, không cần hỏi". Bảng 4 cho thấy joint mode được khuyến nghị phải hỏi ở 72,9% (2.000 nhãn) hoặc 12,7% (5.000 nhãn) các lần gửi Element bị gián đoạn. Hình thực chất mô tả product mode; hãy ghi nhãn tương ứng.
7. Bảng 8 liệt kê MockBank, Pro Expense, Markor, Joplin, Tasks.org và Simple SMS; nhưng chỉ ba hệ thống đã được đo. Hãy đánh dấu từng dòng là đã đo hay dự kiến, thay vì chỉ viết trong chú thích bảng.
8. Mục 6: mỗi lần dump `uiautomator` mất khoảng 2 giây trên host tải cao (load average 16–38 theo `SUMMARY.md`). "Độ trễ" 2,5 giây khi không có lỗi chính là thời gian dump của trình đọc. Cần báo cáo tải máy chủ vì nó đặt cận dưới cho mọi phép đo độ trễ.

**Câu hỏi dành cho phần phản hồi của tác giả**
1. Chạy một tác tử LLM (M3A, T3A hoặc UI-TARS) trên 20 lần gửi K-9 bị gián đoạn bằng bộ thử nghiệm hiện có. Có bao nhiêu lần tác tử soạn lại và gửi lại?
2. Khoảng chờ được chứng nhận của planner sử dụng mốc `ISSUED` hay thời điểm mở lại? Nếu dùng `ISSUED`, làm sao đối chiếu với bảng độ trễ ghi từ lúc mở lại?
3. GhostEffect nhập nonce vào đâu trong email, và đây là hành vi mặc định hay người dùng phải chủ động đồng ý?
4. Với ứng dụng đóng (ví dụ Gmail) không thể quan sát server, GhostEffect làm gì khi một lần gửi bị gián đoạn?
5. Chi phí thời gian thực (*wall-clock*) cho một nhãn trên emulator là bao nhiêu, và cần bao nhiêu giờ-thiết-bị (*device-hours*) để có 5.000 nhãn cho từng lớp và kết quả trên một phiên bản ứng dụng?

**Vấn đề đạo đức / ẩn danh.** Không có. Dùng server tự lưu trữ, tài khoản thử nghiệm, ứng dụng mã nguồn mở; đã thảo luận việc xin phép dùng nonce; nghiên cứu yêu cầu người dùng trả lời được ghi nhận là cần phê duyệt IRB.

**Mức độ tin cậy và điều gì khiến tôi đổi điểm.** Tin cậy cao về Android, trung bình về thống kê. Nếu có tỷ lệ tác tử LLM thực sự gửi lại trên K-9 (ngay cả `n = 20`) và giải quyết được mốc đồng hồ độ trễ, tôi sẽ nâng lên 4. Nếu có đo bộ điều khiển trên thiết bị dưới LMK, tôi sẽ tích cực bảo vệ bài báo.

---

## Phản biện 2 — Reviewer chuyên hệ thống phân tán / lý thuyết

**Tóm tắt bài báo.** Việc phục hồi một hiệu ứng GUI sau gián đoạn được mô hình hóa thành bài toán quyết định tuần tự với kết quả nhị phân ẩn `X`, độ trễ hiển thị `T` và các phép đọc nhị phân có nhiễu, có thể tương quan. Bảo đảm là có điều kiện: `P(retry | committed)` không vượt `alpha` và `P(declare | absent)` không vượt `beta`. Định lý 4.1 trình bày lại cận SPRT của Wald, có phần ngân sách cho độ trễ, cận đảo về độ trễ, cận dưới KL cho số lần đọc và mức sàn của rủi ro Bayes. Mệnh đề 4.3 chứng nhận kết luận ở cấp nhóm bằng chứng với giả định độc lập giữa các nhóm (A2); Mệnh đề 4.4 chứng nhận toàn bộ miền dừng của planner mà không cần A2 bằng kiểm định Clopper–Pearson trên chuỗi cố định. Bổ đề 4.5 đưa ra sàn lỗi dai dẳng; Bổ đề 4.6 xử lý hiệu chuẩn bảo thủ và cận hợp (*union bounds*); Bổ đề 4.7 chặn xác suất khớp nonce sai; Định lý 4.8 (hai chặng) cho thấy Outbox cục bộ cộng với việc truyền lại idempotent trong thời hạn dedup `D` tạo đúng một bản sao. Phân bổ KKT chia ngân sách giữa các bước trong một saga.

**Điểm tổng thể:** 3 (Nghiêng về chấp nhận / Weak accept)  
**Mức độ chuyên môn reviewer:** 4 (Chuyên gia)  
**Điểm thành phần (1–5):** Tính mới 3; tính vững chắc kỹ thuật 4; đánh giá thực nghiệm 3; mức độ quan trọng/tác động 3; trình bày và diễn đạt 2.

**Điểm mạnh**
- Bảo đảm (Phương trình 1) có điều kiện theo `X` và không cần xác suất tiên nghiệm; Hệ quả 4.2 cho thấy `alpha = 0` buộc `beta = 1`, nên ngân sách sai sót mới là đối tượng nên cam kết trung thực.
- Mệnh đề 4.4 giải quyết đúng vấn đề bằng chứng tương quan: hiệu chuẩn cả miền dừng thay vì các phần riêng lẻ. Lập luận chuỗi cố định (Phụ lục A.3) đúng và hệ quả về số mẫu được định lượng (Bảng 1).
- Phân phối cực trị hai điểm của Bổ đề 4.5 được kiểm tra và phù hợp (trung bình `epsilon`, phương sai `rho epsilon(1-epsilon)`); trường hợp hoán đổi được (*exchangeable*) được xử lý riêng.
- Định lý 4.8 là kiến thức kinh điển và bài báo cũng nói rõ; thời hạn `D` và phạm vi thiết bị mới là các yếu tố mới được đo (Mục 7.7).
- Bài báo phân biệt điều đã chứng minh với giả định ("Chúng tôi không khẳng định các bất đẳng thức này") và chỉ rõ loại nguồn gốc của từng con số.

**Điểm yếu (sắp theo mức độ nghiêm trọng)**
1. **Đại lượng được chứng nhận bỏ qua nguồn sai sót chi phối (Phương trình 1; Bảng 4).** `P_v` chỉ là tỷ lệ planner tự quyết định retry sai; câu trả lời sai của người dùng nằm "ngoài (1)". Với Element, joint có `P_v = 0,00%` nhưng tỷ lệ trùng `dup = 3,17%` và thất lạc `loss = 2,04%` vì nó hỏi 72,9% số lần trong khi người dùng trả lời sai với xác suất 5%. Product có `P_v = 0,00%`, `dup = 0,15%`, `loss = 0,09%`. Bảo đảm xếp hạng các mode ngược với lỗi đầu-cuối. Hãy nêu cận tổng hợp, ví dụ `P(dup) ≤ pi(alpha + P(ask) epsilon_u)`, và chỉ rõ người triển khai nên dùng đại lượng nào.
2. **Mốc tính độ trễ trong lý thuyết không khớp phân phối độ trễ được hiệu chuẩn (Mục 3, Phương trình 2, Thuật toán 1 so với Bảng 3b).** `T` bắt đầu từ `t0`; độ trễ emulator lại tính từ lúc mở lại ứng dụng hoặc phục hồi mạng (`real_params.py`: "t0 = relaunch intent / network restore / Send tap"). Nếu có thời gian ngừng hoạt động, planner chờ `w` tính từ `t0` thực chất chờ ít hơn `w` theo đồng hồ trong bảng, khiến phần ngân sách độ trễ không còn được chứng nhận. Artifact đã định lượng điều này (`planner_real4_t0down5.csv`: `P_v` 18,8% product, 29,9% joint khi ngừng 5 giây) nhưng bài báo không nói đến. Hãy định nghĩa lại `T` theo từng lớp lỗi từ một mốc quan sát được `r_e` và chứng minh Phương trình 2 tương ứng, hoặc cộng thời gian ngừng vào khoảng chờ.
3. **Số lượng nhãn được nhấn mạnh che khuất kích thước bảng độ trễ (Mục 7.7, Bảng 4).** "2.000 / 5.000 nhãn cho mỗi lớp" là nhãn kết luận; các bảng độ trễ chứa 20.000 mẫu bootstrap cho mỗi lớp (`N_LAG = 20000`). Bảng 1 cho biết một khoảng chờ ở mức `0.2 alpha`, với không lần vượt ngưỡng, cần 4.649 mẫu độ trễ khi `alpha = 0,01`, còn phải nhân bốn theo lớp. Con số 12,7% dựa trên số mẫu độ trễ mà ngân sách nhãn được công bố không trang trải; `planner_real4_lag5k.csv` cho thấy joint hỏi 30,6% và product hỏi 60,3% khi số mẫu độ trễ bằng số nhãn, còn `lag2k.csv` là 100%.
4. **Nhận định "joint vượt qua được đuôi độ trễ không ghi nhận" chỉ đúng với một số lượng nhãn nhất định (Mục 7.7).** Với 2.000 nhãn, joint giữ ràng buộc "chỉ vì nó hỏi 74,4%"; nhưng với 5.000 nhãn, `planner_real4_tail5.csv` cho `P_v` của joint là 2,01% (cận CP 2,32), vượt ngân sách. Abstract khiến người đọc hiểu joint miễn nhiễm với đuôi trễ. Điều đó không đúng.
5. **`R(tau)` trong Mệnh đề 4.3 chưa được đặc tả đủ rõ cho nhánh chuyển giao (*hand-over*).** Dòng 9 của Thuật toán 1 đặt lại `P = 1` sau khi một mục hop-1 lỗi/bị kẹt, rồi quay lại chuỗi kiểm chứng. Chứng minh Phương trình 2 bao quát trường hợp này dưới `Pi_0`, nhưng mệnh đề nên nêu `P` được đặt lại đúng một lần và `R(tau)` bao gồm cả phân bổ bắt đầu sau hand-over.
6. **Bổ đề 4.6(ii) trong hiệu chuẩn theo khóa lớp.** Với một hiệu ứng không biết lớp, cơ chế dự phòng dùng cận của cả bốn lớp nên phép hợp có `4K` cận. Với `delta = min(alpha, beta)/(10K)`, phần nới biên là `0.4 alpha`, vượt `alpha_cal = 0.1 alpha`. Hoặc phải chia `delta` thêm cho số lớp (và nói rõ), hoặc đường đi chưa biết lớp vượt ngân sách ở phần hiệu chuẩn.
7. **Định lý 4.1(c,d) yêu cầu `T` độc lập với các phép đọc khi đã biết `X`.** Phụ lục A giả định điều này ngay đầu phần chứng minh; A1 ở Mục 3 không ghi rõ. Cần bổ sung.

**Nhận xét chi tiết cho tác giả**
1. "`alpha = 0` buộc `beta = 1`" trong Hệ quả 4.2 là thông điệp quan trọng và giải thích tiêu đề; hãy diễn đạt bằng lời ở Mục 1.
2. Mệnh đề 4.4: bài báo chưa nói kích thước tập pilot dùng để cố định hàm điểm. Hãy nêu rõ nó tách biệt với `n` hiệu ứng mới và cho biết kích thước sử dụng trong simulator.
3. Định lý 4.8, H3: "cửa sổ dương" giữa lúc tạo mục và lần truyền đầu là tính chất của ứng dụng. Với Element, cửa sổ ngắn hơn một lần đọc (20–100 ms so với dump 2 giây), nên Element không có nhóm bằng chứng hop-1. Hãy ghi ngay cạnh H3.
4. Mệnh đề A.1: KKT "đôi khi còn tệ hơn phân bổ đều" (38% ở `k = 2`); phần thân bài nói phân bổ đều "không tạo khác biệt đáng kể (`p = 0,57`)". Giá trị của tầng saga nằm ở an toàn theo union bound, không phải tối ưu hóa. Nên rút gọn.
5. Ký hiệu: `D` vừa là thời hạn dedup (Định lý 4.8), trong khi `D0`, `D1` là các độ phân kỳ KL. Hãy đổi ký hiệu cho thời hạn.
6. Cụm "bất kể mức phụ thuộc giữa các nhóm bằng chứng" (Mệnh đề 4.4) là đúng, nhưng bảo đảm vẫn đòi hỏi quần thể hiệu chuẩn phù hợp với triển khai (Bổ đề 4.6(ii)). Câu "không giả định độc lập" trong abstract không nên bị hiểu thành "không cần bất kỳ giả định nào".

**Câu hỏi dành cho phần phản hồi của tác giả**
1. Định nghĩa mốc thời gian của `T` cho từng lớp lỗi và phát biểu lại Phương trình 2. `P_v` bằng bao nhiêu nếu planner chờ từ `ISSUED` còn bảng ghi từ lúc mở lại, với 5 và 15 giây ngừng hoạt động?
2. Bảng 4 dùng bao nhiêu mẫu độ trễ được ghi lại trên mỗi lớp, và tỷ lệ escalation là bao nhiêu khi kích thước bảng độ trễ bằng số nhãn công bố?
3. Với 5.000 nhãn, `P_v` của joint là bao nhiêu dưới phần đuôi độ trễ 2,9% không được ghi nhận?
4. Biểu diễn `P(dup)` qua `alpha`, `P(ask)` và `epsilon_u`; tính cho các dòng joint và product của Bảng 4.
5. Với hiệu ứng không xác định được lớp, `delta` có được chia cho cả số lớp lẫn `K` hay không?

**Vấn đề đạo đức / ẩn danh.** Không có.

**Mức độ tin cậy và điều gì khiến tôi đổi điểm.** Tin cậy cao; tôi đã kiểm tra mọi phát biểu và các chứng minh ở Phụ lục A đúng trong phạm vi tôi có thể đánh giá. Điểm 3 phản ánh khoảng cách giữa đại lượng được chứng minh (`P_v`) và đại lượng thực sự quan trọng (trùng + mất), cũng như vấn đề mốc thời gian và bảng độ trễ; các vấn đề này có thể sửa bằng văn bản và một lần chạy lại. Nếu sửa và nêu cận tổng hợp, tôi sẽ chấm 4.

---
## Phản biện 3 — Reviewer chuyên thực nghiệm, đo đạc và khả năng tái lập

**Tóm tắt bài báo.** GhostEffect giải quyết việc hiệu ứng GUI bị thực hiện trùng hoặc bị mất sau khi gián đoạn. Có ba tầng đánh giá: (i) mô phỏng dựa trên mô hình gồm 12.000 quy trình bị gián đoạn trên 8 hồ sơ ứng dụng giả lập, so sánh thao tác lại, checkpoint-resume, phương pháp kiểu Atomix, kiểm chứng trước khi retry, ledger cộng khóa, baseline luôn hỏi, chuỗi luật dựa trên cùng bằng chứng và ba mode chứng nhận (product, source families, joint), đồng thời nghiên cứu stress, phân bố quần thể và kích thước mẫu; (ii) chiến dịch 149 lượt chạy emulator trên Element, K-9 và Etar/DAVx5, đo hành vi hop 2 sau khi mất phản hồi, trùng lặp khi làm lại bằng GUI, độ trễ theo lớp lỗi và tỷ lệ sai của nhóm bằng chứng; (iii) "mô phỏng bằng tham số đo được" chạy lại tất cả mode trên các hồ sơ xây dựng từ (ii). Kết quả được nhấn mạnh: joint certification đáp ứng ngân sách trên Element với tỷ lệ phải hỏi 12,7% khi dùng 5.000 nhãn cho mỗi lớp, và hỏi với tất cả lần gửi K-9, nơi cách dùng luật gây trùng lặp.

**Điểm tổng thể:** 2 (Nghiêng về từ chối / Weak reject)  
**Mức độ chuyên môn reviewer:** 4 (Chuyên gia)  
**Điểm thành phần (1–5):** Tính mới 3; tính vững chắc kỹ thuật 3; đánh giá thực nghiệm 2; mức độ quan trọng/tác động 3; trình bày và diễn đạt 2.

**Điểm mạnh**
- Bài báo khớp artifact. Mọi số liệu là macro được sinh từ CSV (`others/notes.md` làm sổ theo dõi). Tôi đã đối chiếu 13 số liệu chính; tất cả khớp.
- Chiến dịch emulator cẩn thận ở những chỗ quan trọng: có ground truth từ server, proxy commit rồi làm rơi phản hồi, trình đọc xác minh trạng thái màn hình, không có mẫu bị kiểm duyệt (0/101 quá 120 giây), và độ trễ có điều kiện theo lớp lỗi.
- Các lần thử bị mất hay bị loại đều được công bố (bảy lượt mất vì ANR; bốn lượt bị loại khi khởi động lại tiến trình).
- Trùng lặp do làm lại bằng GUI được chứng minh bằng các `Message-ID` khác nhau (K-9) và tài nguyên server mới (CalDAV), loại trừ khả năng phía nhận đã khử trùng.
- Kết quả không thuận lợi vẫn được giữ: trên Element, luật chờ 30 giây ngang product (3,1% so với 3,0% phải hỏi); joint hỏi 72,9% với 2.000 nhãn; các luật đã tinh chỉnh ngang product ở `P_v` khoảng 0,1% trong thế giới mô phỏng mặc định.

**Điểm yếu (sắp theo mức độ nghiêm trọng)**
1. **Kết quả chính là mô phỏng mà các phép đo khiến nó gần như hiển nhiên (Mục 7.7, Bảng 4).** Lỗi ở nhóm bằng chứng đọc muộn của Element là 0/99, nên hồ sơ đo được đặt mọi lỗi ở phía đã commit bằng 0 (`params.csv`: `hop1_view1 = 0`, `nonce_view = 0`, `digest_view = 0`). Phân phối độ trễ sinh các hiệu ứng kiểm tra cũng chính là bootstrap dùng để hiệu chuẩn planner. Vì vậy "mọi mode được chứng nhận đều trong ngân sách" gần như đã được bảo đảm bởi cách dựng mô phỏng; thí nghiệm kiểm tra cơ chế CP chứ không kiểm tra ứng dụng. Phải nói rõ Bảng 4 chứng minh được gì và không chứng minh được gì.
2. **Kích thước mẫu ngoài Element chỉ đủ để mô tả hành vi, nhưng khẳng định so sánh mạnh nhất lại dựa vào chúng (Bảng 3a, Bảng 4).** Các ô K-9 chỉ có `n = 2–4` (12 và 8 lượt thử); CalDAV có `n = 8` cộng 3 lượt làm lại. Độ trễ K-9 `U(45 s, 15 min)` "là một giả định" (chú thích Bảng 4). `P_v` 28,91–65,85% của rules trên K-9, được trích trong abstract, phần giới thiệu và kết luận đến hai chữ số thập phân, thực chất là kết quả mô phỏng từ phân phối độ trễ giả định và quan sát hành vi 15 lượt thử.
3. **Kích thước bảng độ trễ không được nêu và lớn gấp 4–10 lần ngân sách nhãn được công bố.** `N_LAG = 20000`; Bảng 1 cần 4.649 mẫu độ trễ cho mỗi lần chờ ở `alpha = 0,01`, còn phải nhân bốn theo lớp. Khi ràng buộc ngân sách mẫu độ trễ bằng ngân sách nhãn, artifact cho tỷ lệ hỏi 100% với 2.000 mẫu và 30,6% joint / 60,3% product với 5.000 mẫu. Không thể tái lập con số 12,7% chỉ từ thông tin "5.000 nhãn mỗi lớp".
4. **Chi phí gắn nhãn bị đánh giá thấp (Mục 5.3).** "Khoảng 15 giây" mỗi nhãn, trong khi trial dài 120–300 giây. Bốn lớp nhân hai kết quả nhân 5.000 là 40.000 hiệu ứng cho mỗi phiên bản ứng dụng: 670 giờ-thiết-bị nếu 60 giây/lần, 167 giờ nếu 15 giây/lần. Bài báo thừa nhận phép kiểm thử dịch chuyển phân phối ở cấp miền để gộp dữ liệu "chúng tôi chưa xây dựng".
5. **Baseline dùng luật không được tiếp cận cùng dữ liệu như GhostEffect (Mục 7.1, 7.7).** Các luật chờ cố định 10 hoặc 30 giây và tin vào thư mục Sent; GhostEffect có 2.000–5.000 nhãn tiêm lỗi cho mỗi lớp. Người thiết kế luật có các nhãn này sẽ nhận thấy Outbox và Sent của K-9 cho kết quả sai ở 20/20 và 8/8 lượt thử. Artifact đã có luật được thẩm định (`planner_real4_vet.csv`: Element hỏi 5,3% / 3,1%, `P_v = 0`), nhưng chúng không xuất hiện trong bài báo.
6. **"Nhãn thụ động làm hỏng mọi mode được chứng nhận" là việc vi phạm điều kiện tiên quyết nhưng lại được trình bày như một kết quả (Mục 7.7, abstract).** Phương pháp vốn yêu cầu nhãn từ thao tác tiêm lỗi (Bổ đề 4.6(ii)). Đây là cảnh báo hữu ích, không phải phát hiện có trọng lượng tương đương phép đo thực.
7. **Phạm vi bao phủ lỗi hẹp (Mục 6).** Chỉ một dạng lỗi mạng (TCP reset sau commit) trong 83/101 thử nghiệm Element, và giữ lại phản hồi trong 6 lượt; chưa tiêm lỗi tác tử chết trên emulator; không có LMK dưới áp lực bộ nhớ (`am kill` không có tác dụng); không có Doze. Hiệu chuẩn theo lớp chỉ khái quát được cho các lớp lỗi đã tiêm.
8. **Không có liên kết artifact.** "Một bản ẩn danh sẽ được cung cấp cho reviewer" (Mục 8, `artifact/README.md`). Với các kết luận dựa trên số liệu sinh tự động, artifact cần được cung cấp ngay khi nộp.

**Nhận xét chi tiết cho tác giả**
1. Chú thích Bảng 4: nêu rõ calibration và test lấy mẫu từ cùng một phân phối đo được, nên không có dịch chuyển phân phối trừ khi một dòng cố tình thêm vào (passive, tail).
2. Bảng 3b: p90 với `n = 20` là quan sát lớn thứ hai. Hãy báo cáo min/median/max hoặc vẽ đủ 20 điểm.
3. Bảng 3c, "không có hai nhóm bằng chứng cùng sai trong 0/101": các nhóm của Element đều đọc cùng một timeline đã render ("một nguồn bằng chứng", Mục 5.3), nên dòng này không kiểm tra A2 giữa các nguồn. Cần nói rõ.
4. Mục 7.7: "lần đọc có quan sát đầu tiên sai trong 3/68, tất cả đều không xét độ trễ". Khoảng chờ được chứng nhận bằng chính các thử nghiệm đã tạo ra dữ liệu này; một chiến dịch đo độ trễ độc lập (ngày khác, tải máy khác) sẽ làm bảo đảm đáng tin hơn.
5. Mục 7.5: đếm số dòng stress mà product vượt ngân sách (Bảng 6: đuôi trễ không ghi nhận 0,98; Doze không phát hiện 5,83) bên cạnh câu "rules vượt trong 3/14 trường hợp".
6. `SUMMARY.md` ghi rằng thành phần chuyển tiếp accessibility của AndroidWorld "đã được quan sát trả về cây trạng thái cũ (timeline của một phòng từ vài phút trước khi màn hình đang hiển thị danh sách phòng)", và một trial pilot có "digest cũ, một lần đọc thực sự sai" dù màn hình đã được xác minh. Đây là các sự kiện màn hình cũ duy nhất đã đo, đồng thời là bằng chứng trực tiếp cho dạng lỗi Mục 5.3. Hãy đưa vào bài cùng số đếm.
7. Khả năng tái lập: nêu phiên bản Python, ghi rõ `run_all.sh` chạy khoảng 20 phút và benchmark ledger trên host không có tính xác định hoàn toàn. Xóa đường dẫn host (`/Users/...` trong `run_all.log`).

**Câu hỏi dành cho phần phản hồi của tác giả**
1. Bảng 4 dùng bao nhiêu mẫu độ trễ trên mỗi lớp? Hãy báo cáo tỷ lệ escalation của joint và product trên Element với 2.000 và 5.000 mẫu độ trễ mỗi lớp.
2. Hãy báo cáo kết quả của các luật đã được thẩm định trên cùng bộ nhãn tiêm lỗi cho Element, K-9 và K-9+Sent.
3. Chi phí thời gian thực đo được của một nhãn tiêm lỗi là bao nhiêu, và cần bao nhiêu giờ-thiết-bị để đạt mốc 5.000 nhãn mỗi lớp?
4. Có trial nào cho kết quả đọc nhóm bằng chứng sai trên màn hình đã xác minh sau khi hiệu ứng hiển thị không? Nếu chỉ có digest cũ trong pilot, làm sao một hồ sơ không có lỗi có thể kiểm tra bộ máy chứng nhận?
5. Có thể cung cấp artifact ẩn danh, gồm cả bộ thử nghiệm emulator, trong giai đoạn phản hồi không?

**Vấn đề đạo đức / ẩn danh.** Không có, ngoại trừ đường dẫn host trong log.

**Mức độ tin cậy và điều gì khiến tôi đổi điểm.** Tin cậy cao. Các phép đo trung thực và khớp artifact; điều tôi lo ngại là các kết luận được xây dựng từ đó. Để đạt điểm 3 cần: (a) công bố kích thước bảng độ trễ cùng các dòng thí nghiệm ràng buộc ngân sách, (b) baseline luật được thẩm định, (c) bỏ số mô phỏng K-9 khỏi abstract hoặc nêu rõ xuất xứ, (d) liên kết artifact. Để đạt điểm 4 cần một thí nghiệm tác tử LLM và chiến dịch đo độ trễ trên tập độc lập.

---

## Phản biện 4 — Thành viên PC cấp cao tổng quát (mức liên quan đến LLM agent, mức phù hợp MobiSys, định vị, độ rõ ràng)

**Tóm tắt bài báo.** Khi tác tử GUI trên điện thoại nhấn Send và bị gián đoạn trước khi thấy kết quả, nó không thể biết tin đã gửi hay chưa; nếu làm lại, nó gửi hai lần. Bài báo gọi đây là ghost effect, đo trên emulator (làm lại bằng kịch bản gây trùng mọi email K-9 và sự kiện CalDAV được thử; Element và DAVx5 tự phục hồi vì client retry với ID idempotent), đồng thời đề xuất GhostEffect: ghi hiệu ứng vào ledger không mất cùng tác tử trước khi nhấn, gắn nonce, đọc màn hình ứng dụng làm bằng chứng sau khi khởi động lại, chờ khoảng thời gian đã hiệu chuẩn, chỉ retry khi các cận đã hiệu chuẩn cho thấy xác suất trùng thấp; nếu không, hỏi người dùng. Ngân sách là `(alpha, beta)`. Lý thuyết gắn bài toán với kiểm định tuần tự; đánh giá chủ yếu gồm mô phỏng và một chiến dịch emulator.

**Điểm tổng thể:** 3 (Nghiêng về chấp nhận / Weak accept)  
**Mức độ chuyên môn reviewer:** 3 (Có hiểu biết chuyên môn)  
**Điểm thành phần (1–5):** Tính mới 3; tính vững chắc kỹ thuật 3; đánh giá thực nghiệm 2; mức độ quan trọng/tác động 3; trình bày và diễn đạt 2.

**Điểm mạnh**
- Vấn đề thực sự tồn tại nhưng ít được nghiên cứu. Benchmark thường thưởng cho việc thay đổi trạng thái, framework chạy lại hoặc phát lại khi phục hồi, nhưng chưa ai đo điều gì xảy ra với thông điệp khi tác tử chết sau khi nhấn Send. Quan sát lỗi vĩnh viễn của K-9 tuy nhỏ nhưng đáng nhớ; việc dẫn lại tiền lệ từ năm 1988 (RFC 1047) cũng thú vị.
- Ý tưởng hai chặng là đóng góp dễ chuyển giao nhất: Outbox của ứng dụng là tầng retry mang khóa mà tác tử không tự xây dựng; "ứng dụng có thuộc G2 không?" là câu hỏi người xây dựng harness có thể trả lời cho từng ứng dụng.
- Định vị nghiên cứu toàn diện và công bằng. Bảng 5 so sánh khóa, mô hình đọc lại, khả năng hỏi, độ bền trước crash và GUI của 12 hệ thống; idempotency key, saga, RPC at-most-once, Kafka idempotent producer, thực thi bền vững và các paper gần đây về khôi phục tác tử (LIMBO, UndoBench, RetryBench, Atomix, Agent libOS, Cordon) đều được đặt đúng vị trí trong phạm vi tôi đánh giá.
- Thẳng thắn: "Chúng tôi chưa chạy LLM agent và chưa dùng điện thoại thật"; "Trên Element, cơ chế đơn giản hơn cũng giữ được ràng buộc".

**Điểm yếu (sắp theo mức độ nghiêm trọng)**
1. **Tầm quan trọng mới được lập luận, chưa được đo (Mục 1, 2.3, 7.8).** Khẳng định tạo động lực là tác tử khi triển khai gây trùng ghost effect; nhưng bài báo chỉ đo một driver có kịch bản làm lại. Việc tác tử LLM nhìn thấy "Unable to send message" của K-9 rồi có gửi lại hay không được để dành cho nghiên cứu tương lai. Bộ thử nghiệm đã có. Không chạy một thí nghiệm agent nhỏ thì câu khẳng định mở đầu vẫn là giả thuyết.
2. **Mode được khuyến nghị không phải mode hiệu quả trong phép đo (abstract, Mục 7.7, Bảng 4).** Abstract khuyến nghị joint certification. Với Element, joint hỏi 72,9% khi có 2.000 nhãn và 12,7% khi có 5.000; product hỏi 3,0% và luật chờ 30 giây hỏi 3,1%, tất cả vẫn trong ngân sách. Với K-9, mọi mode đều hỏi 100%. Mục 7.7 thừa nhận "yếu tố quyết định là phân loại G2, nhãn tiêm lỗi và hỏi người dùng", nhưng abstract và kết luận lại đặt joint lên trước.
3. **Mức phù hợp với MobiSys thể hiện quá ít ở phần thân.** Hai trong 12 trang dành cho lý thuyết, bốn trang dành cho mô phỏng một thế giới do tác giả định nghĩa, chỉ một trang dành cho phép đo di động (7.7). Những gì độc giả MobiSys cần đọc (G2 từng ứng dụng, trạng thái K-9, độ trễ theo lớp lỗi, ledger khi mất điện, ngữ nghĩa `am kill`) lại xuất hiện cuối cùng.
4. **Quá nhiều mode, câu hỏi nghiên cứu và bảng (Mục 7).** Bảy RQ, ba mode chứng nhận, hai biến thể luật cộng họ 12 luật, một "thiết kế trước đó", 15 bảng và 5 hình. Người đọc cần biết một điều: mode nào mới thực sự là GhostEffect? Abstract chọn joint, Hình 1 và dòng in đậm Bảng 2 chọn product, còn K-9 thì "mọi mode đều hỏi".
5. **Tiêu đề so với nội dung.** Hệ quả 4.2 nói đạt exactly-once chỉ bằng kiểm chứng là bất khả thi, nhưng tiêu đề dường như cam kết điều đó. "Budgeted exactly-once" chỉ được giải thích ở Mục 4.1, nơi độc giả MobiSys có thể chưa kịp đọc tới.
6. **Mật độ thông tin quá dày.** Abstract có 287 từ và 18 con số. Câu trung bình 23 từ, 31 câu dài hơn 45 từ, 151 dấu chấm phẩy, 43 đoạn mở đầu in đậm và 373 dấu ngoặc đơn. Xem báo cáo về độ dễ đọc.

**Nhận xét chi tiết cho tác giả**
1. Phần giới thiệu, "Vì sao các giải pháp hiện có không áp dụng trực tiếp": câu đầu nhồi ba kết quả của ba paper vào cùng một cụm trích dẫn. Nên tách câu và gán nguồn rõ ràng.
2. Phần giới thiệu, "Phương pháp" (187 từ) giới thiệu khoảng 16 khái niệm được đặt tên trước khi định nghĩa bất kỳ khái niệm nào. Hãy đưa phiên bản một câu trước (báo cáo độ dễ đọc, 3d).
3. Tiêu đề Mục 2.3 "Tác tử tạo ghost effect thường xuyên đến đâu?" lại được trả lời bằng "Chưa có nghiên cứu công bố nào đo" và bằng một kịch bản thao tác lại. Hãy đổi tiêu đề cho đúng nội dung: "Các ứng dụng có biểu hiện bẫy này không?".
4. Mục 5.4: Thuật toán 1 có 29 dòng với chú thích rút gọn như "bkgd., fallible". Thêm phần diễn giải năm dòng về một ca K-9 và một ca Element trước phần thuật toán.
5. Mục 7.4: "Chỉ dùng Định lý 4.8 không retry lần nào nhưng escalation 73,0%". Baseline này cùng always-ask xác định hai phía của không gian thiết kế; hãy mở đầu so sánh bằng chúng và mode khuyến nghị, đưa 11 baseline khác vào bảng mà không cần diễn giải dài.
6. Bảng 5 (định vị) nên ở thân bài; Bảng 1 (kích thước mẫu) nên ở phụ lục.
7. "G2" là nhãn từ chứng minh. Trong văn xuôi, hãy gọi là "ứng dụng tự retry idempotent".
8. Kết luận lặp abstract với cùng các con số. Hãy dùng kết luận cho bài học: ở ứng dụng tự retry idempotent, agent không nên retry; ở ứng dụng không có cơ chế đó, GUI không cho biết kết quả nên phải hỏi; calibration là chi phí để biết mình có thể tin vào trường hợp nào.
9. Các tài liệu có thể trích dẫn nhưng cần kiểm tra: Gray và Reuter, "Transaction Processing: Concepts and Techniques" (1992) cho thảo luận exactly-once/at-least-once; Bailis và cộng sự, "Coordination Avoidance in Database Systems" (VLDB 2015). Đây không phải yêu cầu bắt buộc.

**Câu hỏi dành cho phần phản hồi của tác giả**
1. Nếu phải đưa ra sản phẩm một mode ngay hôm nay, bạn chọn mode nào và vì sao abstract lại khuyến nghị mode khác?
2. Trong các lần gửi K-9 bị gián đoạn trên harness, tỷ lệ lần mà tác tử LLM gửi lại là bao nhiêu? Mười lượt thử với một tác tử đã trả lời được câu hỏi.
3. Có ứng dụng nào ở Bảng 8 mà chứng nhận xác suất, thay vì chỉ phân loại G2 cộng việc hỏi người dùng, đã thay đổi kết quả đo được không?
4. Với người xây dựng harness không có pipeline calibration, bài học thực dụng có phải là "phân loại G2, đọc Outbox, nếu không chắc thì hỏi" không?

**Vấn đề đạo đức / ẩn danh.** Không có; cần xóa đường dẫn host khỏi artifact.

**Mức độ tin cậy và điều gì khiến tôi đổi điểm.** Trung bình đến cao. Bài báo đúng đắn và trung thực; nhưng nội dung quan trọng với độc giả MobiSys vừa ít vừa nằm cuối bài, phía sau bộ khung phương pháp mà đầu ra được khuyến nghị chưa được phép đo ủng hộ. Một thí nghiệm agent ngắn, bố cục đưa phép đo lên trước và abstract khuyến nghị cơ chế thực sự hiệu quả sẽ khiến đây là bài rõ ràng đáng chấp nhận.

---
## Tổng hợp phản biện (Meta-review)

### Bảng điểm

| Reviewer | Tổng thể | Chuyên môn | Tính mới | Độ vững chắc | Thực nghiệm | Tầm quan trọng | Trình bày |
|---|---|---|---|---|---|---|---|
| R1 (hệ thống di động) | 3 — Nghiêng chấp nhận | 4 | 3 | 3 | 2 | 3 | 3 |
| R2 (lý thuyết) | 3 — Nghiêng chấp nhận | 4 | 3 | 4 | 3 | 3 | 2 |
| R3 (thực nghiệm) | 2 — Nghiêng từ chối | 4 | 3 | 3 | 2 | 3 | 2 |
| R4 (tổng quát) | 3 — Nghiêng chấp nhận | 3 | 3 | 3 | 2 | 3 | 2 |

### Quyết định: Sửa đổi lớn một lần (Major revision — one-shot)

Hội đồng thống nhất rằng bài toán là có thật; các phép đo K-9 và hai chặng là đóng góp hệ thống xác thực; lý thuyết đúng và nêu phạm vi rõ ràng; bài báo khớp artifact (13/13 số liệu đối chiếu khớp). Tuy nhiên, hội đồng cũng thống nhất rằng phần đánh giá chưa đủ hỗ trợ cách bài báo định vị đóng góp. Mode được nhấn mạnh (joint) tốn kém nhất nhưng không mang lại lợi ích trên các ứng dụng đã đo. Số nhãn được nhấn mạnh không tính một bảng độ trễ 20.000 mục mà artifact cho thấy là thiết yếu (tỷ lệ escalation 12,7% thành 30,6% khi số mẫu độ trễ bị ràng buộc bằng số nhãn). Mốc độ trễ trong mô hình (từ lúc nhấn) không khớp mốc đo (từ lúc khởi động lại); artifact cho thấy sai khác này gây hậu quả rõ rệt. Chưa chạy một LLM agent nào dù đã có test rig. Baseline luật lại không được cấp cùng dữ liệu nhãn như GhostEffect. Những vấn đề này không phủ nhận tính đúng đắn của những gì đã đo. Có thể xử lý bằng sửa văn bản, các lần chạy lại vốn đã có trong artifact và một thí nghiệm agent nhỏ. Hội đồng ưu tiên sửa lớn một lần thay vì chấp nhận có người giám sát sửa (*shepherding*) vì abstract, kết quả chính và mode khuyến nghị đều phải thay đổi; cũng không chọn từ chối vì lõi phép đo đáng tin và cách sửa đã rõ.

### Các điểm đồng thuận
- Cách đặt vấn đề ghost effect và phát hiện lỗi vĩnh viễn của K-9 là mới và được đo tốt (cả bốn reviewer).
- Phân rã hai chặng với thời hạn dedup được đo là ý tưởng có thể tái sử dụng tốt nhất (R1, R2, R4).
- Lý thuyết đúng và trung thực về phần nào là kiến thức kinh điển (R2; R4 đánh giá tính trung thực).
- Bài báo khớp artifact; việc công bố các lượt thử bị loại là tốt (R1, R3).
- Không chạy LLM agent nên tuyên bố về tầm quan trọng chưa được kiểm chứng (R1, R3, R4).
- Joint mode được khuyến nghị chưa được các phép đo ứng dụng thực ủng hộ (R2, R3, R4).
- Văn bản quá dày và chứa quá nhiều số (R2, R3, R4).

### Điểm bất đồng và cách kết luận
- **R3 (điểm 2) so với các reviewer khác (điểm 3) về thực nghiệm.** R3 cho rằng Bảng 4 gần như hiển nhiên đối với Element (lỗi ở phía đã commit bằng 0; calibration và test dùng cùng một phân phối). R2 chấp nhận mô phỏng như phép thử bộ máy chứng nhận nhưng muốn thêm cận lỗi tổng hợp. R1 và R4 đánh giá cao hơn phần đo thực tế. Người tổng hợp đồng ý với R3 ở điểm cụ thể này (bài báo phải nêu Bảng 4 chứng minh được gì) và theo đa số về giá trị bài: các phép đo tự đứng vững nếu cách định vị phù hợp với chúng.
- **Vấn đề mốc thời gian có chặn chấp nhận không?** R2 và R1 nói triển khai đúng nguyên văn Thuật toán 1 sẽ chờ thiếu; R4 không nêu vấn đề. Kết luận: đây là vấn đề bắt buộc sửa, vì chính các dòng trong artifact cho `P_v` từ 18,8% đến 46,4% dưới thời gian ngừng hoạt động tương đối nhỏ.
- **Có bắt buộc thí nghiệm tác tử LLM không?** R1 và R4 yêu cầu 10–20 lượt; R3 xem đây là đường để tăng lên điểm 4. Kết luận: bắt buộc, vì đã có test rig, chi phí tính bằng giờ và tuyên bố mở đầu phụ thuộc vào kết quả này.

### Checklist dành cho tác giả

**Bắt buộc (vấn đề chặn chấp nhận)**
- [ ] Xác định mốc đồng hồ của `T` theo từng lớp lỗi (lúc nhấn cho lỗi tác tử chết, lúc khởi động lại cho lỗi ứng dụng chết, lúc phục hồi kết nối cho lỗi mạng); phát biểu lại Phương trình 2 và `CertifiedWait` theo mốc đó; báo cáo các dòng mô phỏng theo tham số đo được với 5 giây và 15 giây ngừng hoạt động (Mục 3, 4.2, 5.4, 7.7).
- [ ] Nêu kích thước bảng độ trễ trong Bảng 4 và thêm các dòng có số mẫu độ trễ theo lớp bằng đúng lượng nhãn đã công bố (2.000; 5.000); sửa cách diễn đạt "escalation 12,7% (5.000 nhãn mỗi lớp)" cho phù hợp (Bảng 4, abstract, Mục 1, 10).
- [ ] Báo cáo `P_v` của joint dưới đuôi độ trễ 2,9% chưa được ghi nhận với 5.000 nhãn; sửa "joint vẫn đạt ràng buộc" thành "joint chỉ đạt ràng buộc khi nó còn hỏi đủ nhiều" (Mục 7.7, abstract).
- [ ] Thêm các luật được thẩm định bằng cùng bộ nhãn tiêm lỗi vào Bảng 4 cho Element, K-9, K-9+Sent; viết lại nhận định "rules retry 28,91–65,85%" (Mục 7.1, 7.7, abstract, 1, 10).
- [ ] Chạy tối thiểu một tác tử dựa trên LLM trên ít nhất 10 lần gửi K-9 bị gián đoạn với bộ thử nghiệm hiện có và báo cáo số lượt gửi lại; nếu không lần nào gửi lại thì nói rõ và đổi cách đặt vấn đề ở Mục 2.3 (Mục 2.3, 7.7, 7.8).
- [ ] Thống nhất mode được khuyến nghị giữa abstract, Hình 1, dòng in đậm của Bảng 2, Mục 7.7 và kết luận; nếu chọn "product khi đã xác minh A2, joint ở các trường hợp khác, hỏi khi không cách nào chứng nhận" thì ghi rõ trong abstract.
- [ ] Hòa giải mâu thuẫn về trường chứa nonce trong email: mặc định ở Mục 5.2 so với Hình 1 (tiêu đề) và Bảng 8 (nội dung); nêu rõ các lượt đo dùng trường mà người nhận nhìn thấy, với sự đồng ý chủ động của người dùng.
- [ ] Trong chú thích Bảng 4, ghi rằng hồ sơ Element có tỷ lệ sai phía đã commit của các nhóm bằng chứng bằng 0 theo phép đo, rằng calibration và test có cùng một phân phối, và từ đó Bảng 4 thực sự kiểm tra điều gì (Mục 7.7).
- [ ] Bổ sung cận tổng hợp cho `P(dup)` theo `alpha`, `P(ask)`, `epsilon_u` và tính giá trị với Bảng 4 (Mục 3 hoặc 4.1, Mục 7.7).
- [ ] Cung cấp artifact ẩn danh kèm test rig emulator khi nộp bản sửa (Mục 8).

**Rất nên làm**
- [ ] Sắp xếp lại Mục 7 để đưa phép đo emulator lên trước; rút gọn mô phỏng còn các baseline đại diện cho không gian thiết kế (redo, chỉ Định lý 4.8, always-ask, rules, vetted rules, product, joint).
- [ ] Abstract tối đa 200 từ và 4 con số; không đưa số mô phỏng K-9 đến hai chữ số thập phân.
- [ ] Rút ngắn Mục 4 trong thân bài (Định lý 4.1 chỉ ba dòng; Bổ đề 4.5 và Mệnh đề A.1 đưa vào phụ lục); dùng diện tích tiết kiệm được để diễn giải từng bước Thuật toán 1 với ví dụ K-9/Element (Mục 4, 5.4).
- [ ] Sửa ước lượng chi phí gắn nhãn (15 giây) thành thời lượng trial đo thực tế và báo cáo giờ-thiết-bị để có 5.000 nhãn mỗi lớp và kết quả (Mục 5.3).
- [ ] Sửa union bound khi không biết lớp lỗi: `delta` có được chia cho số lớp không? (Mục 4.3, Bổ đề 4.6).
- [ ] Thêm hai sự kiện màn hình cũ đã đo từ artifact (forwarder trả cây cũ; digest cũ ở pilot), kèm số lượng (Mục 7.7).
- [ ] Thay p90 tính từ `n = 20` bằng min/median/max hoặc biểu đồ chấm (*dot plot*) (Bảng 3b).
- [ ] Đổi ký hiệu `D` của thời hạn dedup (Mục 4.4).
- [ ] Chuyển Bảng 5 vào thân bài và Bảng 1 sang phụ lục (Mục 2.2, 5.3).
- [ ] Đếm số dòng stress mà product vượt ngân sách (Mục 7.5, Bảng 6).

**Có thì tốt (nice to have)**
- [ ] Đo độ trễ từ `ISSUED` đến trước thao tác nhấn và khả năng sống sót dưới `am kill`/LMK của bộ điều khiển trên thiết bị (foreground service), trên emulator (Mục 5.1, 6).
- [ ] Báo cáo phương sai giữa các seed cho các dòng kết quả chính của Bảng 2 và 4 (Mục 7.1).
- [ ] Thực hiện chiến dịch đo độ trễ độc lập với tập hiệu chuẩn (ngày khác hoặc mức tải host khác) cho Element (Mục 7.7).
- [ ] Thử một phòng Element có mã hóa đầu-cuối (E2EE) để xác nhận đường xử lý `txnId` và phép dò nonce (Mục 8).
- [ ] Cân nhắc Gray và Reuter (1992), Bailis và cộng sự (VLDB 2015) nếu phù hợp (Mục 9; phải kiểm tra nguồn).

### Ghi chú về quá trình sửa dưới sự giám sát (shepherding)

Nếu PC chuyển sang chấp nhận có người giám sát sửa, người giám sát nên yêu cầu tác giả hoàn thành sáu mục bắt buộc đầu tiên (mốc thời gian, kích thước bảng độ trễ, đuôi trễ ở 5.000 nhãn, luật đã thẩm định, một thí nghiệm agent, thống nhất mode khuyến nghị) và viết lại abstract. Phần còn lại là thay đổi văn bản tác giả có thể tự xử lý.

---
## Báo cáo về độ dễ đọc, độ rõ ràng và cách viết "ít giống AI" hơn

### 1. Chẩn đoán

**(a) Abstract giống một bảng kết quả được viết thành văn xuôi.** Có 287 từ, 18 token là số cùng cặp ký hiệu `(alpha, beta)`; 14 số được lấy từ macro và bốn số có hai chữ số thập phân (28,91; 65,85; 0,05; 12,7). Người đọc phải tới câu thứ 6 trong tổng số 11 câu, sau 118 từ trình bày phép đo, mới biết GhostEffect thực sự làm gì.

**(b) Các câu khẳng định trước khi giải thích.** Đoạn "Approach" (Phương pháp) trong phần giới thiệu (187 từ) sử dụng các khái niệm ngân sách, ngưỡng sàn, hop 1, nonce, digest, hiệu chuẩn trên toàn bộ hiệu ứng, family, product, joint, phần ngân sách độ trễ, phân rã hai chặng, thời hạn dedup, ledger, controller, planner và người dùng có thể mắc lỗi, trước khi định nghĩa bất kỳ khái niệm nào:

> "Điều làm ngân sách rủi ro trở nên khả thi là bằng chứng được đọc dưới dạng văn bản accessibility: Outbox cục bộ của ứng dụng (hop 1), nonce mang trong nội dung để biến các mục trông giống nhau thành đối tượng có thể so khớp bằng văn bản (Bổ đề 4.7), và digest của danh sách lịch sử."

> "Điều làm kết quả có thể được chứng nhận là hiệu chuẩn trên toàn bộ hiệu ứng: theo từng nhóm bằng chứng, cho phép các lượt đọc trong nhóm phụ thuộc tùy ý (Mệnh đề 4.3), hoặc hiệu chuẩn chung trên miền dừng của chuỗi quyết định mà không cần các nhóm độc lập với nhau (Mệnh đề 4.4)."

**(c) Quá nhiều khái niệm có tên riêng.** Số lần xuất hiện trong phần thân: `family` 79, `certif-` 70, `hop` 66, `joint` 63, `G2` 57, `nonce` 53, `escalat-` 39, `ledger` 38, `budget` 37, `product` 32, `digest` 20, `ghost` 18, `look-alike` 11, `fault class` 10, `passive label` 8, `dedup horizon` 7, `lag tail` 7, `two-hop` 6, `certified wait` 4. Có ít nhất 19 khái niệm được đặt tên; ba khái niệm trong số đó (`product`, `source families`, `joint`) là các lựa chọn thay thế lẫn nhau. Ký hiệu: `alpha`, `beta`, `alpha_test`, `alpha_lag`, `alpha_cal`, `G(w)`, `T`, `X`, `t0`, `w0`, `w1`, `q`, `q_h`, `tau`, `B(tau)`, `R(tau)`, `Q(t)`, `K`, `delta`, `kappa`, `eta`, `epsilon_0`, `epsilon_1`, `epsilon_u`, `D0`, `D1`, `D` (thời hạn), `u*`, `v*`, `P_v`, `L_v`, `W_max`, `n1`, `C_e`, `G2`, `G2-prime`.

**(d) Độ dài câu và dấu câu.** Có 427 câu trong thân bài, trung bình 22,9 từ/câu; 31 câu dài hơn 45 từ; 151 dấu chấm phẩy (mỗi 2,8 câu có một dấu); 66 mệnh đề dẫn bằng dấu hai chấm; 373 dấu ngoặc đơn mở. Ví dụ (Mục 4.4):

> "Vì vậy, planner đếm các mục hop-1 được tạo sau `t0` (hai mục có nghĩa là một bản sao trùng), coi 'không tồn tại' là không xuất hiện ở cả Outbox và danh sách Sent, đồng thời theo dõi mục đang chờ cho đến khi được xác nhận; nếu tuổi của mục tiến gần `D` thì chuyển sang hỏi người dùng."

**(e) Phân biệt mô phỏng và phép đo được giải thích quá muộn.** Bảng 1 và 2 (mô phỏng) xuất hiện trước Bảng 3 (phép đo); Bảng 4 là loại thứ ba và chỉ được định nghĩa trong chú thích ("không phải một lần chạy emulator"). Mục 7.7:

> "Bảng 4 chạy lại từng mode trên các hồ sơ xây dựng từ phép đo này (`params.csv` ghi nguồn của từng giá trị), với độ trễ riêng cho từng lớp và `bottom` biểu thị không có quan sát."

**(f) Độ dài đoạn văn và cách nhấn mạnh.** Mục 4 có các đoạn dài 436, 268, 243 và 227 từ; Mục 7.7 có các đoạn dài 275, 268 và 209 từ. Có 43 phần mở đầu in đậm bằng `\para` và 94 đoạn nhấn mạnh bằng `\emph`, khiến việc nhấn mạnh mất tác dụng phân biệt thông tin quan trọng.

Bằng chứng bổ sung, mỗi mục một câu ví dụ:

> Mục 1: "Với tác tử dùng công cụ, khóa idempotency giảm trùng lặp từ 28% xuống 4%; các mô hình hàng đầu tạo bản sao trong 56–74% episode khi đọc lại không thể xác nhận kết quả; và không chính sách chỉ dựa vào kiểm chứng nào bảo đảm đúng một lần nếu commit có thể đến muộn mà không có cận cho thời gian đang xử lý."

> Mục 5.3: "Chứng nhận joint và các khoảng chờ cần khoảng `ln(1/delta)/alpha_test` mẫu ngay cả khi không quan sát lỗi; tức hàng nghìn mẫu ở `alpha = 1%` và hàng chục nghìn ở `10^-3`, khoảng gấp đôi khi tỷ lệ thật của miền bằng một phần tư `alpha_test`, và gấp bốn khi chia theo lớp lỗi."

> Mục 7.4: "Ở `P_v` xấp xỉ 0,1%, biến thể tốt nhất trong 12 biến thể (chờ 60 giây, bất kỳ hai bằng chứng) có escalation 17,6%, bằng product chạy với `alpha = 0,03`; ở `P_v` khoảng 0,5%, product chạy với `alpha` danh nghĩa 0,1 (bảo đảm 10%, không phải 0,5%) hỏi 10,4% so với 16,3% của luật tốt nhất, còn chứng nhận joint hỏi 8,7% tại `P_v = 0,88%`; không luật nào giảm escalation xuống dưới 16,2%."

### 2. Các dấu hiệu văn phong giống AI được phát hiện

Các lệnh sau được chạy trong `manuscript/sections/` trên 12 tệp `.tex` phần thân sau khi bỏ các dòng chú thích (`$FILES` đại diện cho 12 tệp này). **Giữ nguyên mẫu chuỗi và cú pháp trong lệnh**, vì chúng dùng để tìm đúng văn bản tiếng Anh của bản thảo:

```
for pat in "not only" "not merely" "not just" "rather than" "crucially" "notably" \
  "importantly" "in essence" "robust" "leverag" "delve" "landscape" "seamless" \
  "novel" "comprehensive" "---" "; " "We present" "We propose" "We recommend" \
  "What makes" "by design" "the price"; do
  printf "%-14s %s\n" "$pat" "$(cat $FILES | grep -v '^%' | grep -o -i -- "$pat" | wc -l)"; done
cat $FILES | grep -v '^%' | sed 's/\\[a-zA-Z]*//g; s/[{}$]//g' | tr '\n' ' ' | sed 's/\. /.\n/g' \
  | grep -cE "^ *(This|These|It) "          # câu bắt đầu bằng đại từ chỉ định chung
cat $FILES | grep -o "\\\\para{" | wc -l    # phần mở đầu in đậm
cat $FILES | grep -o "\\\\emph{" | wc -l    # phần in nghiêng
cat $FILES | grep -o "(" | wc -l            # dấu ngoặc đơn
```

**Số lần xuất hiện:** `not only` 0; `not merely` 0; `not just` 0; `rather than` 1; `crucially` 0; `notably` 0; `importantly` 0; `in essence` 0; `robust` 3; `leverage` 0; `delve` 0; `landscape` 0; `seamless` 0; `novel` 0; `comprehensive` 0; dấu gạch ngang dài `---` 0; dấu chấm phẩy 151; `We present/We propose` 0; `We recommend` 2; `What makes ...` 2; `by design` 4; `the price` 3; câu mở đầu bằng `This/These/It` 7; đoạn mở đầu in đậm 43; `\emph` 94; dấu ngoặc đơn 373; câu trên 45 từ: 31/427.

**Diễn giải:** Những dấu hiệu từ vựng thường thấy của văn bản do máy tạo (`crucially`, `leverage`, `landscape`, dấu gạch ngang dài, cấu trúc "không phải X mà là Y") đều vắng mặt; đây là điểm tốt của tác giả. Tuy nhiên, dấu hiệu về cấu trúc vẫn tồn tại: chuỗi mệnh đề nối bằng dấu chấm phẩy; chồng chất tham chiếu trong ngoặc; các danh sách theo quy tắc bộ ba ("tác tử, ứng dụng hoặc mạng"; "Outbox, nonce mang trong nội dung, digest lịch sử"; "retry, tuyên bố đã hoàn thành hoặc hỏi"); kết luận dạng câu chốt ở cuối hầu hết các đoạn ("chứng nhận dùng những gì nhãn thể hiện"; "hiệu chuẩn bổ sung bảo đảm đi theo dữ liệu nhãn"; "phân rã hai chặng là nơi điện thoại khác biệt"; "việc agent làm lại thì không"); cách mở đầu mang tính tu từ "Điều khiến X trở thành Y là Z"; số liệu quá chi tiết trong abstract. Ít có các chuỗi diễn đạt dè dặt chồng nhau, đây là điểm tốt.

### 3. Các đoạn đề xuất viết lại

**(a) Abstract, tối đa 200 từ và 4 con số**

> Một tác tử thao tác GUI trên điện thoại khi nhấn Gửi rồi bị gián đoạn sẽ không biết thông điệp đã được gửi đi hay chưa. Nếu làm lại bước đó, ứng dụng tạo một yêu cầu mới và máy chủ không có khóa để khử trùng. Chúng tôi gọi kết quả như vậy là *ghost effect*. Trên Android emulator với máy chủ tự lưu trữ, chúng tôi trực tiếp chứng minh cái bẫy này: sau khi mất phản hồi SMTP, K-9 Mail vẫn giữ email đã được máy chủ chấp nhận trong Outbox dưới trạng thái lỗi vĩnh viễn; thao tác làm lại có kịch bản khiến cả 20 lần gửi đều bị trùng. Những ứng dụng có client tự thử lại bằng mã định danh idempotent (Element với Matrix, DAVx5 với CalDAV) có thể tự phục hồi trong thời hạn khử trùng của máy chủ. GhostEffect là tầng phục hồi ghi mỗi hiệu ứng vào ledger kiểu write-ahead trước khi nhấn, gắn nonce, đọc các màn hình của ứng dụng làm bằng chứng sau khi khởi động lại, chờ khoảng thời gian đã hiệu chuẩn để kết quả hiển thị trên server, và chỉ thử lại khi các cận sai số đã hiệu chuẩn giữ xác suất tạo bản sao dưới mức ngân sách. Khi không thể chứng nhận, hệ thống hỏi người dùng. Trên các ứng dụng đã đo, điều quyết định là biết ứng dụng có retry idempotent hay không, hiệu chuẩn bằng các lần gửi bị gián đoạn thay vì các lần gửi bình thường, và hỏi khi màn hình không thể cho biết kết quả; với K-9, điều đó nghĩa là hỏi trong mọi lần gửi bị gián đoạn.

*(Bản gốc tiếng Anh: 197 từ, 2 con số. Số từ có thể khác trong bản dịch.)*

**(b) Đoạn đầu tiên của phần giới thiệu**

> Hãy yêu cầu một tác tử trên điện thoại gửi email kèm hợp đồng thuê nhà đã ký cho Alex. Nó mở K-9 Mail, soạn email và nhấn Gửi. Máy chủ SMTP chấp nhận thông điệp, nhưng phản hồi bị mất khi kết nối đứt. K-9 ghi nhận lần gửi là thất bại, và trạng thái ấy không tự biến mất: email vẫn ở Outbox với lỗi, các lần đồng bộ tiếp theo đều bỏ qua nó. Tác tử khôi phục, đọc màn hình, thấy email chưa gửi, soạn lại rồi nhấn Gửi. Alex nhận hợp đồng hai lần và tác tử báo thành công. Chúng tôi đã chạy tình huống này trên Android emulator với máy chủ email riêng; kịch bản làm lại khiến mọi email K-9 được thử đều bị gửi trùng. Chúng tôi gọi một hiệu ứng mà tác tử không thể đọc lại kết quả là *ghost effect*. Bài báo này nghiên cứu cách quyết định phải làm gì với một hiệu ứng như vậy.

**(c) Mười ví dụ sửa câu — Trước/Sau**

1. **Mục 1.** **Trước:** "Chúng tôi biểu diễn tính đúng một lần bằng một ngân sách: xác suất `alpha` của việc thử lại một hiệu ứng đã commit và `beta` của việc bỏ qua một hiệu ứng chưa tồn tại, có điều kiện theo kết quả ẩn." **Sau:** "Không thể bảo đảm đúng một lần chỉ từ màn hình. Thay vào đó, chúng tôi đặt ngân sách: xác suất thử lại một hiệu ứng đã commit không vượt `alpha`, và xác suất bỏ qua một hiệu ứng chưa tồn tại không vượt `beta`."
2. **Mục 2.2.** **Trước:** "Đọc lại GUI là một hình thức nhận thức có thể sai, có xu hướng lặp lại lỗi khi đọc lại và dễ bị đánh lừa bởi các mục trông giống nhau; VeriGUI huấn luyện bộ xác minh hiệu ứng thao tác trong bối cảnh này nhưng không có bảo đảm lỗi." **Sau:** "Đọc màn hình là một hoạt động nhận thức. Nó có thể sai và lặp lại cùng lỗi khi đọc lại; một mục trông giống mục cần tìm khiến màn hình phù hợp với cả hai kết quả. VeriGUI học một bộ xác minh như vậy nhưng không đưa ra cận sai số."
3. **Mục 3.** **Trước:** "Đọc lại một view không bổ sung thông tin trong mô hình này (trình đọc có xu hướng lặp lại câu trả lời)." **Sau:** "Trong mô hình này, mỗi view chỉ được đọc một lần. Đọc lại sẽ trả về cùng câu trả lời và không bổ sung bằng chứng."
4. **Mục 4.1.** **Trước:** "Đúng một lần nhờ kiểm chứng là một giới hạn chứ không phải điểm có thể đạt, vì vậy GhostEffect cung cấp `(alpha, beta)` như núm điều chỉnh; chi phí lượt đọc xấp xỉ `log(1/alpha)/D0`, và khoảng cách giữa cận trên `(ub)` và cận dưới `(lb)` với `X = 1` tiến tới `u*/D1` khi `alpha, beta → 0`, nếu `alpha log(1/beta) → 0`." **Sau:** "Kiểm chứng có thể tiến gần tới đúng một lần nhưng không bao giờ đạt tuyệt đối, nên GhostEffect cho phép điều chỉnh ngân sách. Mỗi lần `alpha` giảm một bậc thập phân cần thêm khoảng `1/D0` lượt đọc. Ở giới hạn, cận trên và cận dưới chênh nhau lượng bằng chứng tương đương một lượt đọc."
5. **Mục 4.2.** **Trước:** "A2 cho phép nhân các cận với nhau, nhưng giả định này đáng ngờ khi các nhóm cùng đọc một màn hình: lịch sử cũ sau khi khởi động lại có thể cùng lúc đánh lừa nonce, digest và VLM." **Sau:** "Muốn nhân các cận cần giả định các nhóm bằng chứng độc lập. Điều này đáng ngờ khi chúng đọc cùng màn hình: lịch sử cũ sau khi khởi động lại có thể đồng thời đánh lừa nonce, digest và VLM."
6. **Mục 5.3.** **Trước:** "Tính hợp lệ được giữ ở mọi kích thước mẫu; mẫu nhỏ chỉ làm các cận rộng hơn và tăng escalation." **Sau:** "Bảo đảm vẫn đúng ở mọi kích thước mẫu. Khi có ít nhãn, các cận lỏng hơn nên planner phải hỏi thường xuyên hơn, chứ không retry thường xuyên hơn."
7. **Mục 5.4.** **Trước:** "Một kết luận hop-1 khởi tạo tích xác suất ở cả hai phía, nên phía 'đã commit' của ứng dụng G2 hoặc ứng dụng cục bộ được chứng nhận như các kết luận khác (cận của nó được đưa vào `B_com`), còn kết luận 'không tồn tại' của hop-1 cho phép nới điều kiện chờ riêng `w1`, với một nửa ngân sách độ trễ (Phương trình 2)." **Sau:** "Lượt đọc Outbox là thừa số đầu tiên của tích xác suất. Nếu nó báo đã commit đối với ứng dụng tự retry idempotent, kết luận đó được chứng nhận như mọi kết luận khác. Nếu nó báo không tồn tại, planner có thể chờ ít hơn vì Outbox không có độ trễ; cách này dùng một nửa phần ngân sách độ trễ (Phương trình 2)."
8. **Mục 7.1.** **Trước:** "Thế giới mặc định đi chệch giả định của planner: lỗi không thấy nonce có tính dai dẳng (`eta = 1%` do trường ẩn, cộng 0,6% mỗi view); các view hop-1 sai 1–5% mỗi view cộng 0,5% lỗi dai dẳng; Monitor đọc sai 1% trạng thái kết thúc; các view digest bỏ sót 3% mỗi view cộng 2% lỗi dai dẳng; view VLM có tỷ lệ sai `epsilon_0` thuộc `U[0.06, 0.26]`, `epsilon_1` thuộc `U[0.04, 0.20]`, tương quan trong view là 0,6 và giữa các view là 0,1." **Sau:** "Thế giới mô phỏng cố ý vi phạm các giả định của planner. Một số lỗi có tính dai dẳng: trường nonce bị ẩn (1%), lượt đọc Outbox bị kẹt (0,5%), digest cũ (2%). Các lượt đọc VLM có nhiễu và tương quan cả trong lẫn giữa các view. Toàn bộ tham số được ghi trong chú thích Bảng 2."
9. **Mục 7.7.** **Trước:** "Trên các ứng dụng thật, yếu tố quyết định là phân loại G2, nhãn tiêm lỗi và hỏi khi GUI không thể tiết lộ kết quả; hiệu chuẩn bổ sung bảo đảm phù hợp với các nhãn." **Sau:** "Trên các ứng dụng đã đo, ba điều quyết định kết quả: biết ứng dụng có retry idempotent không, hiệu chuẩn bằng những lần gửi bị gián đoạn và hỏi khi màn hình không trả lời được. Hiệu chuẩn không thay đổi các kết quả ấy; nó cho biết lúc nào có thể tin chúng."
10. **Mục 8.** **Trước:** "Các kết quả ra quyết định đến từ mô phỏng, hoặc dựa trên mô hình hoặc theo tham số đo được; mô hình sinh dữ liệu cố ý đi chệch các giả định của planner, nhưng là mô hình do chúng tôi xây dựng." **Sau:** "Mọi kết quả ra quyết định đều đến từ mô phỏng. Thế giới mô phỏng cố ý vi phạm các giả định của chúng tôi, nhưng chính chúng tôi là người xây dựng thế giới ấy."

**(d) Một câu mô tả mà bài báo còn thiếu**

> GhostEffect ghi lại một hiệu ứng GUI trước khi tác tử thực hiện nó; sau gián đoạn, hệ thống dùng chính màn hình ứng dụng, một khoảng chờ đã hiệu chuẩn và, nếu cần, ý kiến người dùng để quyết định có làm lại hay không, sao cho xác suất làm lại hiệu ứng đã commit không vượt `alpha` và xác suất bỏ qua hiệu ứng chưa tồn tại không vượt `beta`.

Đặt câu này ở cuối đoạn đầu tiên của phần giới thiệu.

### 4. Đề xuất chỉnh sửa cấu trúc

- **Abstract.** Dùng bản 197 từ ở trên. Giữ kết quả K-9 20/20 và sự tương phản với Element/DAVx5. Bỏ số liệu mô phỏng.
- **Mục 1.** Mở bằng câu chuyện K-9 (3b). Rút đoạn "Vì sao các giải pháp hiện có không áp dụng trực tiếp" xuống ba câu. Thay phần "Approach" và "Results" bằng một đoạn gồm câu mô tả ngắn (3d), các cơ chế (ledger, nonce, bằng chứng trên màn hình với cận đã hiệu chuẩn, chờ được chứng nhận, hỏi người dùng) và hai phát hiện đo được. Bốn gạch đầu dòng đóng góp, đưa phép đo lên trước.
- **Mục 2.** Gộp 2.1 và 2.2 còn một trang. Đổi tên 2.3 thành "Các ứng dụng có biểu hiện bẫy này không?" rồi trả lời bằng Bảng 3a. Chuyển Bảng 5 từ phụ lục vào đây.
- **Mục 3.** Giữ nguyên. Thêm bảng bốn dòng: ký hiệu, ý nghĩa, nơi đo. Chuyển cách chia ngân sách 0,5/0,4/0,1 sang Mục 5.
- **Mục 4.** Rút còn 1,5 trang. Định lý 4.1 còn ba dòng cộng ghi chú "phần nào là kiến thức kinh điển". Giữ đầy đủ Mệnh đề 4.4 và Định lý 4.8. Chuyển Mệnh đề 4.3, Bổ đề 4.5, Bổ đề 4.6(iii), Bổ đề 4.7 và phân bổ saga sang phụ lục, có chỉ dẫn tham chiếu. Đổi tên ký hiệu `D`.
- **Mục 5.** Trong 5.3, thay "Cần bao nhiêu nhãn" bằng Bảng 1 và hai câu; sửa chi phí nhãn. Trong 5.4, thêm ví dụ cụ thể trước Thuật toán 1 (một lần gửi K-9: hop 1 thất bại, không gì chứng nhận được nên hỏi; một lần gửi Element: không có hop 1, chờ được chứng nhận 13,6 giây, bản ghi hiển thị Sent). Hình 1 đã kể câu chuyện này; hãy trỏ sang hình.
- **Mục 6.** Giữ. Báo cáo tải host và thời gian dump. Chuyển "Planned agent harness" sang 7.8 hoặc bỏ.
- **Mục 7.** Sắp xếp lại: 7.1 phép đo emulator (Bảng 3); 7.2 chạy lại với tham số đo được (Bảng 4, bổ sung kích thước bảng độ trễ và luật đã thẩm định); 7.3 mô phỏng dựa trên mô hình (Bảng 2 rút xuống redo, chỉ định lý, always-ask, rules, vetted rules, product, joint); 7.4 stress và phân bố (một đoạn, Bảng 6–7 sang phụ lục); 7.5 cơ chế (một đoạn). Bỏ RQ1–RQ2 khỏi thân bài (kiểm chứng kết quả cổ điển; chỉ một câu và dẫn sang phụ lục). Thay cột p90 của Bảng 3b bằng biểu đồ chấm của 83 độ trễ, chia theo lớp.
- **Mục 7.8.** Rút còn ba câu trong Mục 8, hoặc thay bằng kết quả thí nghiệm agent.
- **Mục 8.** Giữ phần Hạn chế và mức độ sát thực tế Android; gộp Đạo đức thành một đoạn; thêm cận lỗi tổng hợp tại đây hoặc Mục 3.
- **Mục 9.** Thêm một câu cho mỗi hệ thống LIMBO, Agent libOS và VeriGUI để nêu khác biệt.
- **Mục 10.** Ba câu rút ra bài học. Không cần số liệu.
- **Ngân sách trang.** Nội dung chính đang đúng 12 trang. Cắt bớt (Mục 4 khoảng 0,7 trang; Mục 7.2–7.6 khoảng 1 trang; Mục 7.8 khoảng 0,2; phần giới thiệu 0,3) giải phóng khoảng 2 trang. Dùng chỗ đó cho thí nghiệm agent (0,3), ví dụ chạy từng bước (0,3), biểu đồ độ trễ (0,2), Bảng 5 chuyển vào thân bài (0,3) và các dòng luật đã thẩm định (0,1), vẫn còn một ít dự phòng.

### 5. Checklist phong cách viết cho bài báo

1. Mỗi câu chỉ đưa ra một luận điểm; tách mọi câu dài trên 35 từ (có 31 câu trên 45 từ).
2. Tối đa một dấu chấm phẩy trong mỗi đoạn; thay các dấu còn lại bằng dấu chấm.
3. Không đưa con số nào mà thiếu loại kết quả trong cùng câu: đo thực tế, mô phỏng hay chính xác theo lý thuyết. Mọi số trong Bảng 4 đều phải được mô tả là "mô phỏng với tham số đo được".
4. Viết số lượng dạng phân số (20/20); tỷ lệ phần trăm một chữ số thập phân; abstract không nêu thêm tỷ lệ ngoài số đếm của K-9 và Element.
5. Định nghĩa thuật ngữ trước lần dùng đầu tiên hoặc đừng dùng trong mục đó: hop 1, G2, family, verdict, product, joint.
6. Một tên cho mỗi khái niệm: dùng "ứng dụng tự retry idempotent" trong văn xuôi, `G2` trong định lý; dùng "bằng chứng Outbox" trong văn xuôi, `hop 1` trong định lý; chọn thống nhất "escalation" hoặc "ask".
7. Thay cấu trúc "Điều khiến X thành Y là Z" bằng "Z khiến X thành Y".
8. Chuyển tham chiếu trong ngoặc về cuối câu hoặc sang câu kế tiếp.
9. Chỉ dùng phần mở đầu in đậm ở nơi người đọc cần quét nhanh (thiết lập, baseline, metric), không dùng cho từng bước lập luận.
10. Chỉ in nghiêng thuật ngữ khi định nghĩa lần đầu; 94 đoạn `\emph` là quá nhiều.
11. Kết thúc mỗi đoạn bằng kết quả chứ không bằng câu châm ngôn; bỏ những câu như "chứng nhận dùng những gì nhãn thể hiện" nếu không thêm thông tin.
12. Trình bày mối liên hệ giữa mô phỏng và phép đo một lần, từ sớm trong Mục 7, bằng ba câu.
13. Câu đầu mỗi chú thích bảng phải trả lời "đây là phép đo đại lượng gì, với cỡ mẫu n bao nhiêu?".
14. Chỉ viết danh sách ba mục khi thực sự có ba ý; đừng thêm hoặc bỏ ý chỉ để đủ ba.
15. Đọc to abstract; nếu mất hơn 60 giây thì quá dài.
