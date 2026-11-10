# Quy ước chung cho đợt nộp GhostEffect

Ngày soạn: **09/11/2026**. Chủ trì soạn: phần C (C-02).

**Trạng thái:** bản đề xuất để trưởng nhóm và A/B duyệt; chưa phải biên bản
phê duyệt của cả nhóm. Phạm vi theo `CONTRIBUTOR_FIXED.md`, không mở lại
chiến dịch P40/C-guard cũ trong `resolve.md`.

## Mode khuyến nghị

| Điều kiện | Cách xử lý |
|---|---|
| Có cơ sở cấu trúc cho giả định A2, các điều kiện chứng nhận còn lại thỏa | Product certification |
| Không có cơ sở A2, nhưng chứng nhận joint và các điều kiện còn lại thỏa | Joint certification |
| Không chứng nhận được, thiếu lớp lỗi/mốc thời gian phù hợp và không có fallback hợp lệ | ASK; không suy ra absent từ màn hình failed hoặc lịch sử trống |
| App tự retry idempotent trong đúng scope và dedup horizon | Không GUI retry; xác nhận done khi có bằng chứng hợp lệ, nếu chưa đủ thì ASK/PENDING |

Joint là lựa chọn cho trường hợp không có cơ sở A2; không hứa joint luôn ít
hỏi hơn vetted rules. Source certification là mode so sánh, vẫn phải nêu
giả định độc lập giữa các nguồn còn tách biệt. Không thay ngân sách, seed,
họ luật hoặc dữ liệu để làm mode nào thắng.

Abstract, dòng nhấn mạnh trong Table 2, phần đánh giá, Conclusion và nhánh
G2 của Figure 1 phải theo cùng quy tắc điều kiện trên sau khi được duyệt.
Không biến khuyến nghị có điều kiện thành tuyên bố product luôn là mặc định.

## Thuật ngữ

| Khái niệm | Quy ước đề xuất |
|---|---|
| Yêu cầu trợ giúp | Dùng **ask**, **asking**, **ASK**; thay escalate/escalation trong văn xuôi |
| G2 trong văn xuôi | **app tự retry idempotent**; tiếng Anh: **app with idempotent retries** |
| Ký hiệu G2 | Giữ trong định lý, chứng minh và bảng |
| Hop 1 | **Outbox evidence**; đọc bằng GUI/accessibility, không truy cập database app |
| Đo thực tế | **emulator measurement**; tách riêng **LLM-agent experiment** |
| Mô phỏng với tham số đo | **measured-parameter simulation**; không gọi là agent/emulator run |
| Mô phỏng theo mô hình | **model-based simulation** |
| Tính chính xác | **exact computation** |
| Đo ledger trên host | **host measurement**; kết quả phụ thuộc máy |

Không đổi tên cột CSV hay tên macro cũ chỉ để thay từ trong văn xuôi.
Ví dụ macro có tên Ask vẫn giữ nguyên; schema dữ liệu không đổi.

## Hợp đồng macro và dữ liệu cần xác nhận trước 11/11

- A cung cấp danh sách `\Cert*`, nghĩa, đơn vị và định dạng; các tên ví dụ ở
  §4 của phân công chưa được coi là danh sách đã freeze.
- B cung cấp danh sách `\Agent*`, `\LabelTrial*`, cùng nghĩa, đơn vị và định dạng.
- C dùng `\Sim*`, `\Rsim*` và các tiền tố cũ; khi tách renderer giữ nguyên tên
  và giá trị, chỉ chuyển quyền ghi sang đúng file.
- Chưa có giá trị thì dùng `??`; không dùng 0 làm số liệu thay thế.
- Giữ nguyên schema `params.csv`, `episodes.csv`, `label_cost.csv` trong §4
  của phân công. Sau 11/11, thay hợp đồng phải được trưởng nhóm duyệt.

## Những điểm còn cần quyết định

1. Trưởng nhóm xác nhận mode và bảng thuật ngữ ở trên.
2. Trưởng nhóm xác nhận cho sửa paper: `resolve.md` còn chỉ thị cũ không sửa
   manuscript, trong khi phân công ngày 09/11 yêu cầu C-01 tách manuscript.
   Yêu cầu hiện tại của người dùng cho phép chuẩn bị thay đổi trên nhánh C;
   việc tích hợp vẫn theo PR và quyền merge của trưởng nhóm.
3. A/B xác nhận hợp đồng macro. C không tự ghi nhận thay người khác.
4. Trưởng nhóm chỉ định người nghiệm thu C; chủ phần không tự nghiệm thu.

Không có chữ ký/đồng ý của A, B hoặc trưởng nhóm trong bản soạn này.
