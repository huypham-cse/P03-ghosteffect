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

## 10/11/2026 (tối)

**Đã làm:**
- A-05: sửa §4.3 (`04-theory.tex`, Lemma 4.6(ii) và đoạn sau nó) và chứng minh ở App. A (`appendix-proofs.tex`, phần (ii)). Ký hiệu mới `n_cls` là số lớp lỗi. Lemma nói rõ union bound chạy trên `K · n_cls` cận. Công thức ghi đúng như code: `δ = min(α, β) / (10 · K · n_cls)` với `n_cls = 4`, `K = 11` (product), `8` (source), `5` (joint). Từ đó `K · n_cls · δ = min(α, β)/10 ≤ min(α_cal, β_cal)`, tức trả union bound ở cả hai phía. Khớp `calibration_deltas(keyed=True)` trong `planner_sim.py` và `k_total` trong `testbed/calibration.py` (cộng `bound_count × số lớp` của từng stratum).
- Build: `PYTHON=python sh manuscript/build.sh` thoát 0 trên Windows + MiKTeX, 20 trang, overfull lớn nhất 7,89 pt. Các file `manuscript/generated/*` và `main.pdf` mà build sinh lại trên Windows đã hoàn nguyên, không commit (thuộc C).
- Test: `python -m unittest discover -s artifact/tests` vẫn 32 test, 1 fail của C như mục trước, 1 skip; test δ qua.

**Trạng thái task:** A-05 xong, chờ nghiệm thu. A-09 tên: chờ duyệt PR #9.

**Lưu ý cho C:** dòng setup ở `07-evaluation.tex` (dòng 16) còn ghi `δ = α/(10K)`, cần đổi thành `min(α, β)/(10 · K · n_cls)` theo phụ thuộc số 5 của `CONTRIBUTOR_FIXED.md` §3.

**Tiếp theo:** nháp A-06 (đổi `D` thành `H_dedup`, các chi tiết lý thuyết), rồi A-01 trên §3 và §5.

## 10/11/2026 (khuya)

**Đã làm:** A-06, đủ bảy mục, sửa trong `03-model.tex`, `04-theory.tex`, `05-design.tex`, `appendix-proofs.tex`:
1. Hand-over (R12): Prop 4.3 nói hand-over đặt lại `P = 1` đúng một lần mỗi effect, và `R(τ)` gồm các phân bổ bắt đầu sau hand-over (bỏ qua hop 1). Thêm đoạn chứng minh trong App. A. Alg. 1 ghi "hand over, once". §5.4 nói hop-1 reads vẫn giữ trong audit log.
2. A1 (R13): ghi rõ `T` độc lập với lỗi của reader khi biết `X`, vì một lượt đọc chỉ phụ thuộc `T` qua việc effect đã hiện hay chưa.
3. H3: ghi cạnh Thm 4.8 rằng cửa sổ dương là tính chất của app, và Element không có hop 1 vì truyền lần đầu nhanh hơn một lần đọc accessibility. Không ghi số (20–100 ms, 2 s là số đo của B, phải là macro), chỉ dẫn sang §7.
4. Cỡ pilot của Prop 4.4: pilot tách khỏi `n` effect kiểm; pilot là một phần mười đầu của mỗi kết quả (khớp `joint_calibration`), `n` chỉ đếm chín phần mười còn lại.
5. Prop A.1 (R27): phần bảo đảm là union bound và là lý do có tầng saga; phần phân bổ KKT không tối ưu theo chi phí thật. Bỏ câu về phân bổ theo `π` (rút gọn theo review). §4 đoạn "Budgets across a saga" sửa theo cùng ý.
6. Đổi `D` (dedup horizon) thành `H_dedup` ở §4, §5 và App. A. `grep -nE 'horizon[^.]*\$D\$|within \$D\$' manuscript/sections/*.tex` rỗng.
7. Đường echo `/sync` của Element: ghi trong §3 rằng echo là view đầu-cuối theo A1, vì đó là event server đã áp dụng, chỉ hiện sau commit, và lúc nó đến là lúc `T` kết thúc.
- Ngoài ra "escalating" ở §4.4 đổi thành "handing it over to the end-to-end path" (đúng với Alg. 1).

**Kiểm:** build thoát 0, 20 trang, overfull lớn nhất 7,89 pt. `readability_count.py` (lấy từ nhánh `c/10-checks`) trên bốn file của A: trước `para 21, emph 50, câu dài 21, đoạn có dấu chấm phẩy 22`; sau `21, 50, 20, 21`. Không thêm vi phạm nào; phần còn lại sửa ở lượt đọc YC-12 sau A-07.

**Trạng thái task:** A-06 xong, chờ nghiệm thu. A-05 chờ PR #17, A-09 tên chờ PR #9.

**Tiếp theo:** A-01 (mốc `r_e` ở §3, Eq. 2, Alg. 1; chứng minh trong App. A).

## 11/11/2026 (rạng sáng)

**Đã làm:** A-01, phần văn bản và test:
- §3: định nghĩa `t_vis`, mốc `r_e` theo lớp lỗi (agent chết: `t_0` tức ISSUED; app chết: lúc controller xác nhận ý định mở lại; mất mạng: lúc khôi phục; kết hợp: mốc muộn hơn), `T_c = max(0, t_vis − r_e)`, `G_c(w)`, deadline `r_e + w_c`. Lớp không biết thì lấy deadline muộn nhất qua các lớp; thiếu mốc cần dùng thì ASK. A1 đổi thành `T ≤ t − r_e`.
- §4: Thm 4.1(a,b) chờ và quyết định theo `r_e + w`; Eq. 2 dùng `G_c(w_1)`, `G_c(w_0)` và câu nói rõ cả hai khoảng chờ chạy từ `r_e`.
- §5: Alg. 1 nhận `r_e` và gọi `WaitUntil{r_e+w}`; `CertifiedWait` dùng lag `T_c`; nhãn hiệu chuẩn ghi `T_c` từ `r_e`; nhánh hand-over đo từ `r_e`.
- App. A: chứng minh Thm 4.1(a,b) và Eq. 2 dùng `r_e + w`, thêm bước `t_vis ≤ r_e + T`.
- Test mới `artifact/tests/test_guarantee.py` (`AnchorTests`): chạy product và joint trên hồ sơ Element đo được, downtime 15 s, ghi lại mọi lượt đọc đầu-cuối và khoảng chờ chứng nhận. Với mốc đúng (`clock='origin'`): 0 lượt đọc trước `r_e + w` trên 53 effect retry. Test đối chứng với mốc sai (`clock='t0'`): bắt được 360 lượt đọc sớm. Test chỉ đọc, không sửa hàm nào của `planner_sim.py`.

**Kiểm:** `grep -n 'WaitUntil' manuscript/sections/05-design.tex` chỉ còn `r_e+w`; không còn `t_0+w` trong các file của A. Build thoát 0, 20 trang, overfull lớn nhất 7,89 pt. `python -m unittest discover -s artifact/tests`: 34 test, 1 fail cũ của C, 1 skip. Độ dễ đọc trên bốn file của A không đổi (21, 50, 20, 21).

**Còn lại của A-01:** bảng mốc đúng so với mốc sai (`down5`, `down15`, `t0down5`, `t0down15`; product và joint; `P_v` và cận CP), sinh bằng `render_guarantee.py` vào `tab_cert_clock.tex` với macro `\CertClock*`. Chờ C-01 merge (file `render_guarantee.py` và `macros_guarantee.tex` do C-01 tạo).

**Trạng thái task:** A-01 đang làm (văn bản và test xong, còn bảng). A-06, A-05 chờ duyệt (#18, #17), A-09 tên chờ #9.

**Tiếp theo:** khi C-01 merge: `render_guarantee.py` (bảng clock, ngân sách nhãn, cận tổng hợp), A-02, A-03, A-04.

## 11/11/2026 (sáng sớm)

**Đã làm:** A-09 phần giá trị, kèm số liệu cho A-01 (bảng), A-02, A-03, A-04:
- `artifact/scripts/render_guarantee.py`: chạy độc lập (`--results-dir`, `--output-dir`), chỉ đọc CSV, chỉ ghi `macros_guarantee.tex` và `tab_cert_{clock,budget,lagapp,bound}.tex`. Dựng mọi file trong bộ nhớ trước; thiếu CSV hay dòng hay cột thì thoát 1 và không ghi gì. Có hàm `render(results_dir)` để `render.py` gọi sau C-01.
- 105 macro đúng hợp đồng ở PR #9. Bảng:
  - `tab_cert_clock` (A-01): mốc `r_e` so với `t_0`, 5 s và 15 s, product và joint, `P_v` (CP) và ask.
  - `tab_cert_budget` (A-02, A-03): 2.000/20.000, 2.000/2.000 tied, 5.000/20.000, 5.000/5.000 tied, tail, tail tied; dấu † khi cận CP vượt α.
  - `tab_cert_lagapp` (A-02, phụ lục): 10k, 20k, boot10k.
  - `tab_cert_bound` (A-04): `q`, `ε`, cận dup và loss cho Element và thế giới mặc định.
- Dòng bất lợi giữ nguyên: ở mốc 5.000, đuôi trễ đưa cả product (`P_v` 2,83, CP 3,19) và joint (2,01, CP 2,32) vượt ngân sách; dòng tail tied product có `P_v` 0,99 nhưng CP 1,21 nên vẫn ghi vượt ngân sách. Mốc sai `t_0` cho `P_v` từ 18,82 đến 46,42.
- `\CertLabelMedS` và `\CertDeviceHoursFive` là `??` cho đến khi B giao `real/agent/label_cost.csv` (18/11); renderer báo trên stderr. Khi có file, renderer tự tính.
- Chú thích bảng ghi CP là đầu trên của khoảng Clopper–Pearson hai phía 95% (đúng với `clopper_pearson` trong `ge_core.py`), không phải một phía.
- Test mới trong `test_guarantee.py` (`RenderGuaranteeTests`): tham số khớp `planner_sim` (số lớp, K, α, β, δ); chạy hai lần giống từng byte và chỉ ghi file của A; thiếu CSV thì thoát khác 0 và giữ file cũ; giá trị khớp CSV (gồm một cận tự tính tay); `label_cost.csv` cho ra device-hours; mẫu số 0 in N/A.

**Kiểm:** 105 macro; hai lượt chạy cùng SHA-256; các bảng biên dịch sạch trong một tài liệu LaTeX thử. `python -m unittest discover -s artifact/tests`: 40 test, 1 fail cũ của C, 1 skip.

**Chưa làm và lý do:** chưa commit file sinh ra trong `manuscript/generated/`, vì `render.py` trên `main` thay cả thư mục khi build và sẽ xóa chúng; chưa input bảng vào `.tex`. Cả hai làm sau khi C-01 merge: C gọi `render_guarantee.render()` thay cho `exec` (YC-A9), rồi A input bảng vào §5.3, §3 và phụ lục.

**Trạng thái task:** A-09 giá trị xong (chờ nối sau C-01). A-01 bảng đã sinh được. A-02, A-03, A-04: số liệu và bảng xong, còn câu chữ trong §5.3 và §4.

## 11/11/2026 (trưa)

**Bối cảnh:** C-01 (#10) đã merge vào `main` lúc sáng. Pull về `dfd910a`.

**Đã làm:**
- A-09 (#20): merge `main` vào `a/a09-render`, giải xung đột add/add với file khung `render_guarantee.py` của C-01 (giữ bản của A). `render.py` của C chạy file này bằng `exec` trong namespace của nó, nên thêm khối cuối: khi chạy trong `render.py` thì ghi qua `W()` vào thư mục staging của C; chạy độc lập thì như cũ. Đổi tên các tên trùng với `render.py` (`HERE`, `f1`, `f2`, `sci`, `main`, `_half_up`, `col`) sang tiền tố `cert_`. Đầu ra qua pipeline và chạy độc lập giống hệt. Đã commit `macros_guarantee.tex` và bốn `tab_cert_*.tex`. Trên Windows, `render.py` tái tạo đúng mọi file `generated/` khác của C (chỉ khác ký tự xuống dòng).
- A-02, A-03, A-08 (một phần), nhánh `a/a02-label-budget`, sửa §5.3 (`05-design.tex`) và phụ lục (`appendix-proofs.tex`):
  - A-08: câu hop 1 giờ nói đọc màn hình Outbox qua cây accessibility, không đọc database. Thay "≈15 s" bằng `\CertLabelMedS` và `\CertDeviceHoursFive` (đang `??`, chờ `label_cost.csv` của B ngày 18/11). Table 1 (`tab_nsize`) chuyển xuống phụ lục mới `app:labels`.
  - A-02: đoạn mới nêu riêng bốn con số bằng macro (101 lượt đo emulator; 2.000 và 5.000 nhãn mỗi lớp và kết quả; pilot 500 và holdout 4.500; 20.000 mẫu lag bootstrap). Bảng `tab_cert_budget` vào §5.3, `tab_cert_lagapp` vào phụ lục. Câu về tỉ lệ hỏi ở mốc 5.000 luôn nói rõ kích thước bảng lag.
  - A-03: đoạn đuôi trễ: product vượt ngân sách; joint chỉ giữ ngân sách khi còn hỏi đủ nhiều (2.000 nhãn: hỏi 74,4%, giữ; 5.000 nhãn: hỏi 13,7%, `P_v` 2,01, CP 2,32, vượt); bảng lag tied cũng không cứu.
  - Bỏ "escalations" trong đoạn này (dùng "asks" theo C-02).

**Kiểm:** `grep -n 'local database' manuscript/sections/05-design.tex` và `grep -n 'tab_nsize' manuscript/sections/05-design.tex` rỗng. Build thoát 0, 21 trang (thêm trang phụ lục), kết luận vẫn ở trang 13 như trước thay đổi. Độ dễ đọc trên `05-design` và `appendix-proofs`: trước `para 14, emph 19, câu dài 10, đoạn chấm phẩy 13`; sau `14, 18, 8, 12`.

**Cho C:** caption của `tab_nsize` (do `render.py` sinh) còn ghi `δ = min(α,β)/(10K)`; theo §4.3 mới (A-05) phải là `min(α,β)/(10·K·n_cls)`. Dòng 16 của `07-evaluation.tex` cũng vậy.

**Trạng thái task:** A-02, A-03 xong phần văn bản và bảng (chờ nghiệm thu). A-08 còn chờ số đo của B.

## 11/11/2026 (chiều)

**Đã làm:** A-04, nhánh `a/a04-composed-bound` (dựng trên `a/a02-label-budget`):
- §3 (`03-model.tex`): đoạn mới định nghĩa `q_x`, `ε_x`, `r_x` và Eq. `eq:composed`: `P(dup∣X=1) ≤ min(1, α + q1·ε1 + r1)`, `P(loss∣X=0) ≤ min(1, β + q0·ε0 + r0)`, chứng minh một câu (union bound qua ba nguồn lỗi: planner, người dùng, app). Câu cho người triển khai: đọc cận tổng hợp, không chỉ `P_v`. Giá trị Element bằng macro: product 1,19%, joint 5,12% (joint hỏi 65,06% effect đã commit).
- `r1 = r0 = 0`: đã kiểm trong `planner_sim.py`, `g2_nodedup = 0` ở cả hồ sơ Element (`params.csv`) và thế giới mặc định, nên không app nào retransmit mà không dedup. Câu trong bài nói đúng điều đó.
- `ε`: nêu là tỉ lệ sai quan sát được trong mô phỏng (người dùng giả sai 5%, 10% khi có look-alike, `user_err = 0.05` trong `planner_sim.py`).
- Phụ lục `app:composed` với `tab_cert_bound` (Element và thế giới mặc định, mẫu số 0 in N/A).
- Phương trình hai vế ban đầu tràn 39 pt; tách thành hai dòng bằng `gathered`, hết tràn. Eq. của lag split giờ là (3); không chỗ nào ghi cứng số phương trình.

**Kiểm:** build thoát 0, overfull lớn nhất 3,46 pt, không tham chiếu thiếu. Độ dễ đọc trên `03-model` và `appendix-proofs` không tăng (8, 25, 2, 10 trước và sau).

**Trạng thái task:** A-04 xong (chờ nghiệm thu).

## 11/11/2026 (chiều, tiếp)

**Đã làm:** A-01, phần bảng, nhánh `a/a01-table` (dựng trên `a/a04-composed-bound`):
- §3: thêm câu cho thấy chờ từ `t_0` sai thế nào (mô phỏng với tham số đo, Element, mất kết nối 15 s: product retry 43,77% effect đã commit, so với 0,00% khi chờ từ `r_e`), bằng macro `\CertClock*`.
- Phụ lục `app:anchor` với `tab_cert_clock`: mốc đúng `r_e` so với mốc sai `t_0`, 5 s và 15 s, product và joint, `P_v`, cận CP và ask.
- Đối chiếu đủ 4 dòng × 2 chính sách của bảng với `planner_real4_{down5,down15,t0down5,t0down15}.csv`: khớp.
- Phát hiện và sửa: heredoc trong shell làm `\ref` thành ký tự CR; đã sửa và quét lại mọi dòng thêm mới trong file của A (không còn ký tự điều khiển hay lệnh thiếu dấu `\`).

**Kiểm:** build thoát 0, overfull lớn nhất 3,46 pt, không tham chiếu thiếu, kết luận vẫn trang 13. Test: 42, 1 fail cũ của C, 1 skip. Độ dễ đọc `03-model` và `appendix-proofs` không đổi.

**Trạng thái task:** A-01 xong cả văn bản, test và bảng (chờ nghiệm thu).

**Tiếp theo:** A-07 (rút §4 còn 1,5 trang, walk-through K-9 và Element ở §5.4) kèm lượt đọc YC-12; nhắn C xác nhận C-02 và hai chỗ δ của C.

## 11/11/2026 (tối)

**Đã làm:** A-07, nhánh `a/a07-shorten` (dựng trên `a/a01-table`):
- Đo bằng script đọc tọa độ tiêu đề trong PDF (pypdf): trước khi sửa, từ tiêu đề §4 đến tiêu đề §5 là khoảng 5,0 cột; sau khi sửa là **2,86 cột** (≤ 3 cột).
- Thm 4.1 trong thân bài còn **3 dòng** (đã kiểm bằng `pdftotext`), giả thiết đặt ở câu dẫn ngay trước (views i.i.d. có điều kiện; (b), (c) cho policy verification-only đạt β; (d) cho policy không hỏi). Đoạn "What is classical" ghi nguồn của từng phần và nói (c), (d) bằng lời. Phát biểu đầy đủ kèm Eq. `eq:ub`, `eq:lb` chuyển sang App. A.
- Giữ đủ Prop 4.4 (joint, giờ là Prop 4.3) và Thm 4.8 (two-hop, giờ là Thm 4.5). Corollary 4.2 giữ nguyên.
- Chuyển xuống App. A, có câu trỏ tới trong §4: Prop 4.3 (product, `prop:family`), Lemma 4.5 (`lem:floor`), Lemma 4.6(iii) thành `lem:drift` riêng, Lemma 4.7 (`lem:nonce`), đoạn saga, công thức source families, chi tiết dedup theo giao thức (Synapse, Matrix, CalDAV, SMTP).
- Lemma 4.6 trong thân bài chỉ còn (i), (ii) và đoạn δ của A-05 (giữ công thức `δ = min(α,β)/(10·K·n_cls)`).
- §5.4: hai walk-through dẫn số dòng của Alg. 1 qua `\label` (dòng 5, 10, 12, 13, 15, 19, 20; đã đối chiếu từng nhãn với số dòng trong PDF). K-9: hop 1 đọc "absent" vì thư nằm ở Outbox trạng thái lỗi, calibration thấy cùng cách đọc trên thư đã commit nên không retry, không Sent thì hỏi ở dòng 20, có Sent thì hỏi ở dòng 13 vì chờ vượt `W_max` (khớp `why_struct` 100% và `why_wait` 100% trong `planner_real.csv`). Element: không hop 1, chờ theo lớp, đọc mỗi view một lần, đánh dấu committed ở dòng 19.
- Hình 2 (`fig-arch`) đang nổi lên đầu cột chứa tiêu đề §5 và đẩy tiêu đề xuống; chuyển `\input` xuống cuối §5.1 để hình nằm sau tiêu đề.
- Nhãn "Proof." mới trong App. A dùng môi trường `proof` để không tăng `\emph`.

**Kiểm:** build thoát 0, 21 trang, overfull lớn nhất 3,46 pt, không tham chiếu thiếu, kết luận vẫn trang 13. Test: 42, 1 fail cũ của C, 1 skip. Độ dễ đọc bốn file của A: trước `para 21, emph 49, câu dài 16, đoạn chấm phẩy 19`; sau `20, 47, 12, 13`.

**Trạng thái task:** A-07 xong (chờ nghiệm thu). Còn lại của A: lượt đọc YC-12 (giới hạn `\para` 5, `\emph` 10, 0 câu dài, ≤ 1 chấm phẩy mỗi đoạn) và giá trị A-08 (chờ B, 18/11).
