# Nhật ký phần A (Gia Huy)

Theo luật 1.8 trong `team/RULES.md`: chỉ thêm mục mới, không sửa hay xóa mục cũ.

## 10/11/2026

**Đã đọc:** `team/CONTRIBUTOR_FIXED.md`, `team/RULES.md`, hiện trạng `03-model.tex`, `04-theory.tex`, `05-design.tex`, `planner_sim.py` (các hàm của A), `testbed/calibration.py`, các CSV `planner_real4_*`, `planner_real.csv`, `planner_sim.csv`, `real/params.csv`.

**Đã làm:**
- A-09 (phần tên macro): chốt danh sách macro `\Cert*` ở mục "Hợp đồng macro của A" bên dưới, gửi C để C dùng với giá trị tạm `??`. Giá trị sẽ do `render_guarantee.py` sinh (hạn 17/11).
- Kiểm hiện trạng cho các task khác (chưa sửa file nào):
  - A-05: `k_total` trong `testbed/calibration.py` (`validate_spec`) đã nhân `bound_count` với số lớp của mỗi stratum, và `compile_store` dùng `δ = min(α, β) / (10 · k_total)`. Vì vậy **không cần nhờ B sửa**. `calibration_deltas` trong `planner_sim.py` cũng đúng: `min(α, β) / (10 · K · số lớp)` khi `keyed`, với `K = 11, 5, 8` (product, joint, source) và 4 lớp (`CLASSES`). Việc còn lại: `04-theory.tex` dòng 126 đang ghi `δ = min(α,β)/(10K)`, cần ghi rõ nhân số lớp.
  - A-01: §3 vẫn dùng `t_0`; Alg. 1 ở `05-design.tex` dòng 92 vẫn là `WaitUntil{t_0+w}`.
  - A-06: ký hiệu `D` còn ở `04-theory.tex` dòng 154 đến 162 và `05-design.tex` dòng 114.
  - A-08: câu "Hop 1 reads the app's local database" ở `05-design.tex` dòng 46; `tab_nsize` input ở dòng 67.
- Chạy `python -m unittest discover -s artifact/tests` trên Windows (Python 3.12.10): 32 test, 1 fail, 1 skip. Test fail là `test_failed_publication_restores_the_original_directory` (của C, `render.py`), không thuộc A; có thể chỉ lỗi trên Windows, chưa kiểm trên WSL. Test δ `test_asymmetric_calibration_pays_both_budgets_and_all_classes` qua.

**Trạng thái task:** A-09 đang làm (tên: xong, chờ C xác nhận; giá trị: chưa làm). A-05 đang làm (code đã kiểm, còn sửa §4.3). A-01, A-02, A-03, A-04, A-06, A-07, A-08 chưa làm.

**Bị chặn / phụ thuộc:** sửa `appendix-proofs.tex` (chứng minh của A-01, chuyển lemma của A-07) chờ C-01 (12/11). A-08 chờ `label_cost.csv` của B (18/11); trong lúc chờ viết với `??`.

**Tiếp theo:** A-05 (sửa §4.3, 13/11); khung `render_guarantee.py` đọc CSV, thoát khác 0 khi thiếu CSV; nháp A-06 và A-01 trên §3, §4, §5.

### Hợp đồng macro của A (A-09, gửi C ngày 10/11)

Quy ước chung:
- Mọi macro do `artifact/scripts/render_guarantee.py` ghi vào `manuscript/generated/macros_guarantee.tex`, có `\xspace` ở cuối như các file macro khác.
- `Pv` là cột `cdup` (phần trăm, 2 chữ số thập phân). `PvHi` là cột `cdup_hi`, tức cận trên Clopper-Pearson (phần trăm, 2 chữ số). `Ask` là cột `ask` (phần trăm, 1 chữ số).
- Chính sách: `Prod` là `ghost` (product), `Joint` là `ghost-joint`.
- Loại số: mọi macro bảng là **mô phỏng với tham số đo** (Element), trừ khi ghi khác.
- Mẫu số 0 thì macro in `N/A`.
- Tên không có chữ số (luật của LaTeX), nên 2k, 5k, 10k, 20k viết là `Two`, `Five`, `Ten`, `Twenty`.

**1. Mốc thời gian (A-01), bảng `tab_cert_clock.tex`.** Mẫu `\CertClock<Hàng><Chính sách><Cột>`:

| `<Hàng>` | CSV | Nghĩa |
|---|---|---|
| `DownFive` | `planner_real4_down5.csv` | mốc đúng `r_e`, mất mạng 5 s |
| `DownFifteen` | `planner_real4_down15.csv` | mốc đúng `r_e`, mất mạng 15 s |
| `TzeroDownFive` | `planner_real4_t0down5.csv` | mốc sai `t_0`, mất mạng 5 s |
| `TzeroDownFifteen` | `planner_real4_t0down15.csv` | mốc sai `t_0`, mất mạng 15 s |

`<Chính sách>` ∈ {`Prod`, `Joint`}; `<Cột>` ∈ {`Pv`, `PvHi`, `Ask`}. Tổng 24 macro. Ví dụ: `\CertClockTzeroDownFiveProdPv`.

**2. Ngân sách nhãn, dòng tied (A-02), bảng `tab_cert_budget.tex` trong §5.3.** Mẫu `\CertTied<Mốc><Chính sách><Cột>`, `<Mốc>` ∈ {`Two` (`lag2k`), `Five` (`lag5k`)}. Tổng 12 macro. Ví dụ: `\CertTiedFiveJointAsk`.

**3. Đuôi trễ ở mốc 5k (A-03), cùng bảng `tab_cert_budget.tex`.** Mẫu `\CertTailFive<Chính sách><Cột>` (`tail5`) và `\CertTailFiveTied<Chính sách><Cột>` (`tail5tied`), `<Cột>` ∈ {`Pv`, `PvHi`, `Ask`, `Over`}. `Over` là chữ: `over budget` khi `PvHi` lớn hơn α, ngược lại `within budget`. Tổng 16 macro. Ví dụ: `\CertTailFiveTiedProdPvHi`, `\CertTailFiveTiedProdOver`.

**4. Phụ lục ngân sách nhãn (A-02), bảng `tab_cert_lagapp.tex`.** Mẫu `\CertTied<Mốc><Chính sách><Cột>` với `<Mốc>` ∈ {`Ten` (`lag10k`), `Twenty` (`lag20k`)} và `\CertBootTen<Chính sách><Cột>` (`boot10k`). Tổng 18 macro.

**5. Kế toán nhãn (A-02), dùng trong §5.3.**

| Macro | Nghĩa | Nguồn | Định dạng |
|---|---|---|---|
| `\CertElemTrialsN` | số lượt đo thật trên emulator đứng sau hồ sơ trễ Element | đếm phần tử trong `elem_lag_*` của `real/params.csv` | số nguyên, có dấu phẩy nghìn |
| `\CertLabelsBase` | nhãn mỗi lớp ở mốc chính | cột `ncal` của `planner_real.csv`, tag `main` | như trên |
| `\CertLabelsFive` | nhãn mỗi lớp ở mốc 5k | cột `ncal` của `planner_real4_lag5k.csv` | như trên |
| `\CertPilotFive` | phần pilot ở mốc 5k (một phần mười, theo `joint_calibration`) | `ncal // 10` | như trên |
| `\CertHoldoutFive` | phần holdout ở mốc 5k | `ncal − ncal // 10` | như trên |
| `\CertLagBootN` | số mẫu bootstrap của bảng trễ (`N_LAG`) | cột `nlag` của `planner_real4_down5.csv` | như trên |
| `\CertClassesN` | số lớp lỗi quan sát được | số lớp trong `planner_sim.CLASSES` | số nguyên |

**6. Cận tổng hợp dup/loss (A-04), bảng `tab_cert_bound.tex`.** Mẫu `\CertBound<Thế giới><Chính sách><Cột>`:
- `<Thế giới>`: `Elem` (hồ sơ Element đo được, `planner_real.csv` tag `main`) hoặc `Def` (thế giới mặc định, `planner_sim.csv`).
- `<Cột>`:
  - `Dup` là `min(1, α + q1·ε1 + r1)`.
  - `Loss` là `min(1, β + q0·ε0 + r0)`.
  - `Qone` và `Qzero` là cột `q1`, `q0`.
  - `EpsOne` và `EpsZero` là cột `user_e1`, `user_e0`.
- Mọi cột là phần trăm, 2 chữ số. `r1 = r0 = 0` là giả định trong simulator và được ghi rõ trong câu.

Tổng 24 macro. Ví dụ: `\CertBoundElemJointDup`.

**7. δ (A-05), tính chính xác.** `\CertDeltaProd` và `\CertDeltaJoint` là `min(α, β) / (10 · K · số lớp)` với α = β = 1%. Định dạng: `$x.x\times10^{-y}$`.

**8. Chi phí nhãn (A-08), §5.3.**
- `\CertLabelMedS`: median thời gian một lượt, dòng `total` của `real/agent/label_cost.csv` (của B). Định dạng: giây, số nguyên.
- `\CertDeviceHoursFive`: `5.000 nhãn × \CertClassesN lớp × 2 kết quả × median / 3600`. Định dạng: giờ, số nguyên.

Đây là số đo trên emulator kết hợp phép tính. Giá trị có từ 18/11; trước đó là `??`.

Tổng 105 macro (24 + 12 + 16 + 18 + 7 + 24 + 2 + 2). Phần A không dùng macro của C. Phần A dùng một số của B: `label_cost.csv` (đọc trực tiếp CSV, không dùng macro `\LabelTrial*`).
