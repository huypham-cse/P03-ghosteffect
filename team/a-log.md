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

## 11/11/2026 (khuya)

**Đã làm:** YC-12 (độ dễ đọc) và YC-10 (thuật ngữ) trên mọi file `.tex` của A (`03-model`, `04-theory`, `05-design`, `appendix-proofs`, `figures/fig-arch`), nhánh `a/yc12-readability` (dựng trên `a/a07-shorten`):
- `\para{`: 20 → 5. Giữ ba đoạn thiết lập ở §3 và "Calibration labels", "How many labels" ở §5.3; các đoạn khác mở bằng câu thường.
- `\emph{`: 47 → 10. Chỉ giữ chỗ định nghĩa lần đầu: committed, duplicate, loss, view, probe family, guarantee, verification-only, family verdicts, evidence sources, dedup horizon. Nhãn trong chứng minh ở App. A đổi thành câu ("For the miss rate, …") hoặc môi trường `proof`.
- Câu > 45 từ: 12 → 0 (ngoài Alg. 1). Tách câu ở Lemma 4.4(ii), Thm 4.5 (H1, H2, H3 thành câu riêng), §5.1, §5.3, §5.4, App. A (Lemma 4.4 (ii), Lemma nonce, chứng minh Thm 4.5).
- Đoạn > 1 dấu chấm phẩy: 13 → 0 (ngoài Alg. 1).
- YC-10: không còn "escalat"; "G2" chỉ còn trong Thm 4.5 và mã giả Alg. 1. Văn xuôi dùng "app with idempotent retries" theo C-02; nhãn Hình 2 đổi "G2" thành "retry class".

**Về Alg. 1:** `team/readability_count.py` (của C, nhánh `c/10-checks`) bỏ qua `tabular`, TikZ và code nhưng chưa bỏ qua `algorithmic`, nên tính cả thuật toán thành 2 "câu" dài và 1 đoạn 16 dấu chấm phẩy. Đề nghị C thêm `algorithmic` vào danh sách môi trường bỏ qua (một từ trong regex dòng 24). Với thay đổi đó, bốn file của A đạt đủ: `para 5, emph 10, câu dài 0, đoạn chấm phẩy 0`.

**Kiểm:** §4 vẫn 2,89 cột, Thm 4.1 vẫn 3 dòng, build thoát 0, overfull lớn nhất 3,46 pt, không tham chiếu thiếu, kết luận trang 13. Đã xem Hình 2 sau khi đổi nhãn. Test: 42, 1 fail cũ của C, 1 skip. Lệnh grep YC-A6 và YC-A8 vẫn rỗng.

**Trạng thái:** YC-12, YC-10 trên file của A xong, chờ C sửa công cụ cho Alg. 1. Còn lại: giá trị A-08 (chờ `label_cost.csv` của B, 18/11), PR nghiệm thu `[A] Nghiệm thu` chậm nhất 19/11.

## 18/11/2026

**Đã đọc:** review của trưởng nhóm ở #23 (9 ghi chú không chặn), #24 (1 lỗi chặn, 4 lỗi nhỏ), #25 (4 mục); `team/QUYET_DINH_CHUNG.md` (đã duyệt 18/11); `planner_sim.py` (cách tính `h1` của K-9, dòng 312; `calibration_deltas`; `N_LAG`); `07-agent.tex` (§7.8).

**Dựng lại nhánh:** #23 đã squash cả chuỗi A, nên rebase từng commit cũ chỉ sinh xung đột. `a/a07-shorten` dựng lại từ `main` bằng cherry-pick commit A-07; `a/yc12-readability` xếp trên nó bằng cherry-pick commit YC-12. Không xung đột (trên `main`, file của A trùng đầu nhánh `a/a01-table`).

**Đã làm, #24 (`a/a07-shorten`):**
1. Lỗi chặn, walk-through K-9 ở §5.4: thư lỗi trong Outbox cho hop 1 đọc phía committed (`h1=1` trong simulator), không phải "absent". Mục đó mơ hồ vì K-9 hiện cùng mục lỗi khi server chưa áp dụng thư. Dòng 6 của Alg. 1 (nhãn mới `alg:g2`) chỉ tin phía này với app tự retry idempotent và app local, nên với K-9 thì `P = 1`, `d = ⊥`, và planner hỏi.
2. Walk-through Element: "absent" chỉ retry khi `P ≤ τ_a`, nếu không thì hỏi.
3. Thm 4.1: (c) và (d) giờ là bất đẳng thức (`E_0[N] ≥ d(1−β‖α)/D_0`; `P(dup)+P(loss) ≥ π̄(1−√(D_0 E_0[N]/2))`). Câu dẫn nêu prior π, `π̄ = min(π, 1−π)`, `d` là entropy tương đối nhị phân và điều kiện "chỉ đọc đầu-cuối" của (b). Định lý vẫn 3 dòng (đã xem ảnh trang 4).
4. Câu nonce ở §4.3 giữ hệ số `M|B_t|/m^k` và điều kiện hiển thị (không đọc nháp, mục lỗi, thông báo).
5. App. A: "from 30 to 60 min".

**Đã làm, #25 (`a/yc12-readability`):**
1. Alg. 1 không còn G2: dùng `idem` (định nghĩa ở dòng Require). G2 chỉ còn trong Thm 4.5 và chứng minh của nó.
2. Hình 2: "retry class" thành "idempotent retries".
3. "Clopper-Pearson" (gạch nối) ở §4.3, §5.3, App. A và chú thích bảng do `render_guarantee.py` sinh; đã render lại `tab_cert_*.tex`.
4. YC-12 với Alg. 1: không sửa được bằng câu chữ. Mã giả dùng dấu chấm phẩy để ngăn lệnh và không có dấu chấm, còn `readability_count.py` trên `main` vẫn chưa bỏ qua `algorithmic`. Theo luật 1.3, A không sửa file của C. Đã kiểm: bỏ riêng khối `algorithmic` khỏi bản sao `05-design.tex` thì năm file của A đạt `para 5, emph 10, câu dài 0, đoạn chấm phẩy 0`.

**Đã làm, nhánh mới `a/acceptance` (xếp trên `a/yc12-readability`):**
- A-10 (a): render lại `macros_guarantee.tex` từ `real/agent/label_cost.csv` của B: `\CertLabelMedS` = 412 s, `\CertDeviceHoursFive` = 4.577 giờ. File macro không còn `??`.
- A-10 (b): walk-through K-9 dẫn sang §7.8 (thí nghiệm LLM agent chạy đường này end to end), không thêm số.
- Ghi chú #23:
  1. Câu đuôi trễ ở mốc 5.000 nêu thêm `\CertLagBootN` mục lag.
  2. `n_cls = 4` khi keyed theo lớp, `1` khi gộp (khớp `calibration_deltas`).
  3. H3: Element thỏa H3, chỉ không có họ hop 1 vì cửa sổ ngắn hơn một lần đọc accessibility.
  4. Alg. 1 có deadline `D ← r_e + w` (lớp không biết: `max_c(r_c + w_c)`), hỏi khi thiếu mốc `D` cần, bỏ `elapsed` chưa định nghĩa. Chứng minh Cor. 4.2 dùng `T > t_n − r_e` và `G(t_n − r_e)`.
  5. §3: `r_1 = r_0 = 0` ghi là giả định của simulator; thêm cận loss (`\CertBoundElemProdLoss`, `\CertBoundElemJointLoss`). Docstring `render_guarantee.py` định nghĩa r như §3.
  6. Hợp đồng macro: xem mục bổ sung bên dưới.
  7. `render_guarantee.py`: dòng không có cột `nlag` (`planner_real.csv`, tag `main`, `five`) dùng `N_LAG = 20000` (hằng số mặc định của simulator), không mượn `nlag` của `down5`. Renderer thoát 1 nếu `nlag` của các dòng bootstrap (`down5`, `tail5`) khác `N_LAG`. Test mới so `N_LAG` với `planner_sim.N_LAG`. Giá trị bảng không đổi.
  8. Clopper-Pearson: như #25 mục 3.
  9. Thuộc B (`07-real.tex`), không làm.

**Bổ sung hợp đồng macro của A (ghi chú 6 của #23, báo C):** §5.3 và §5.4 của A dùng các macro của C sau, chỉ đọc, không đổi tên: `\RsimFiveJointAsk`, `\RsimTail`, `\RsimTailJointAsk`, `\RsimTailJointPv`, `\RsimKnineProdAsk`, `\RsimKsentProdAsk`, `\RsimElemProdAsk`. Câu "Phần A không dùng macro của C" ở mục 10/11 không còn đúng; mục này thay nó.

**Kiểm (Windows, MiKTeX, Python 3.12):**
- Build thoát 0, 23 trang, overfull lớn nhất 3,46 pt, không tham chiếu thiếu, PDF không còn `??`.
- §4 dài 2,96 cột (pypdf: tọa độ tiêu đề §4 trang 4 và §5 trang 5, chia theo chiều cao cột lấy từ số dòng lề). Đạt nhưng sát giới hạn 3 cột: phần tăng từ 2,89 là do (c), (d) giờ là công thức.
- Kết luận ở trang 14, giống bản build `main` (`ad27858`) trong worktree tạm. Thay đổi của A không đẩy trang.
- Test artifact: 55 test, 1 fail cũ của C (`test_failed_publication_restores_the_original_directory`, lỗi cả trên cây sạch), 1 skip. Test testbed: 116, OK, 4 skip.
- YC-A9: chạy hai lần cùng SHA-256 (5 file); đổi tên `planner_real4_tail5.csv` thì thoát 1 và không ghi file nào.
- YC-04: chỉ còn `0.5/0.4/0.1` (tham số). YC-A1, YC-A6, YC-A8, YC-10: grep đạt.
- Scrub qua trên file bài và code của A. `a-log.md` bị báo tên người ở dòng 1, như `c-log.md`; log là tài liệu nội bộ của nhóm, không vào gói.
- Lưu ý kỹ thuật: heredoc trong Git Bash gộp `\\` thành `\`. Đã quét mọi file của A: không có ký tự điều khiển hay CR lạc.

**Cho C:** (1) thêm `algorithmic` vào danh sách môi trường bỏ qua trong `team/readability_count.py` (regex ở hàm `prose`), để YC-12 của A đạt trên công cụ; (2) hợp đồng macro bổ sung ở trên.

**Trạng thái:** A-01 đến A-10 xong. #24, #25 đã sửa theo review và nằm trên `main`. PR `[A] Nghiệm thu` mở từ `a/acceptance`. Chặn duy nhất còn lại: YC-12 chờ C sửa công cụ cho Alg. 1.

## 21/11/2026

**Đã làm (sẵn sàng cho cổng cuối, C-13):** kiểm lại `main` ở `6d07ec1` (sau #83; freeze candidate trong `others/c13-final-checklist.md` vẫn ghi `29c2990`, nên ZIP phải tạo lại từ commit đã chốt).
- Bản clone WSL sạch của `main`: test artifact 68 OK (1 skip), test testbed 119 OK (3 skip).
- `make_bundle.sh` ra `ghost-effect-final-6d07ec1.zip`, SHA-256 `4c408e04b4ac62ad54cf7fd50f83593fbc2b2064fa7552af10f730ed841dd416`; scrub qua trên gói đã giải nén; test trong gói 68 OK (10 skip, công cụ `team/` không đi kèm).
- `run_all.py` chạy từ gói: thoát 0. So 108 CSV: 106 trùng byte; `ledger_bench.csv` khác (phụ thuộc host, đã ghi trong README); `lag_wait.csv` khác ở chữ số cuối của hai số thực (ví dụ `...392` so với `...391`). Nguyên nhân: Python 3.14.4 trên máy này, freeze dùng 3.12.3; macro làm tròn nên bài không đổi. Báo C: README nên nêu rõ phiên bản Python cho phép so byte, hoặc liệt kê `lag_wait.csv` là khác ở mức làm tròn.
- PDF build trên Windows (MiKTeX): thoát 0, 23 trang, 0 `??`, overfull lớn nhất 1,53 pt, kết luận trang 12, scrub `manuscript/` qua.
- Nhánh `a/final-wording`: §4.1 đổi "We claim none of these inequalities" (dễ hiểu thành "không khẳng định các bất đẳng thức đúng") thành "None of these inequalities is new". Build lại: kết luận vẫn trang 12, 0 `??`; scrub và độ dễ đọc `04-theory.tex` qua. Chưa mở PR: freeze chỉ cho phép thêm commit link artifact, cần trưởng nhóm quyết.
- Đọc lại §3, §4, §5, App. A (chứng minh Thm 4.1): không thấy lỗi khác.

**Cho C (file của C, không sửa):** §1 dòng 40 dùng "A2" trước khi §3 định nghĩa; đề nghị viết "when independence across families has a structural basis" như abstract.

**Trạng thái:** phần A xong. Còn lại của cả nhóm (C-13, trưởng nhóm): chốt commit freeze, tạo lại ZIP, đăng link ẩn danh, chèn link vào §8, chạy lại cổng PDF, nộp HotCRP kèm thông tin tác giả.

## 21/11/2026 (chiều): đọc và sửa câu chữ lần cuối trước khi nộp

Theo yêu cầu của A, sửa trên toàn bài (kể cả file của B và C), chỉ đổi chữ, không đổi số, macro hay dữ liệu:
- Lỗi cấu trúc: phần mô phỏng với tham số đo (Table 4, Table 5) không có tiêu đề nên nằm lẫn trong §7.2; thêm `\subsection{Measured-parameter simulation}` (§7.3), đưa đoạn mô tả lên trước đoạn giới hạn và viết gọn đoạn giới hạn (giữ đủ các ý của YC-C5). Đoạn mở §7 nêu bốn mục theo đúng thứ tự.
- Lỗi thực tế ở §6: chỉ Doze cần tắt màn hình; App Standby và Data Saver hạn chế app chạy nền cả khi màn hình bật.
- Abstract: "decides ghost effects" thành "resolves ghost effects", câu cuối rõ hơn; 199 từ (≤ 200), vẫn 4 con số.
- Câu chữ: §1 "differs twice"; §2 T3A nêu số bản trùng có tag; §4 bỏ câu mở đầu và lần nhắc RFC 1047 thứ hai; §5.3 bỏ ngoặc thừa; §6 bỏ câu PRISM/Storm chưa chạy; §7.1 hai câu khó đọc; §7.2 câu về bản trùng còn lại; §7.4 "favoring"; §8, §9 (câu nối dài, "our foundations"), §10.
- Kiểm: build thoát 0, 23 trang, 0 `??`, không overfull; kết luận và References đều ở trang 12; độ dễ đọc toàn bài `para 14/15, emph 28/30`, 0 câu dài, 0 đoạn chấm phẩy; không thêm "escalate", "G2" hay số gõ tay; scrub qua; YC-C9 grep kết luận ra 0.

## 21/11/2026 (chiều, tiếp): Figure 5 chồng chữ

- Figure 5 (phụ lục B.6, `fig_pareto`): nhãn α trên đường product bị cắt ở mép trái và đè lên các đường cong; ở hình dưới, "key" đè "Atomix-durable" và "key+ask" chạm điểm "nonce+ask". Sửa trong `artifact/scripts/render.py` (chỉ phần trình bày): bỏ nhãn α khỏi hình, chú thích liệt kê các mức α lấy từ CSV theo thứ tự điểm; hình dưới cao 4,8 cm, "key" đặt sang phải như các nhãn khác, "key+ask" đặt ở góc trống dưới trái có đường nối.
- YC-10: trục và chú thích Figure 5, chú thích Table 24 và các bảng `tab_corr`, `tab_pop`, `tab_sens` đổi "escalations/escalated" thành "asks"; `generated/` không còn "escalat".
- Không đổi CSV hay macro. So với manifest freeze 20/11, năm file sinh ra này khác do đổi trình bày (`fig_pareto`, `tab_corr`, `tab_planner_extended`, `tab_pop`, `tab_sens`).
- Kiểm: build thoát 0, 23 trang, 0 `??`, không overfull; kết luận và References ở trang 12; đã xem ảnh Figure 5 ở 300 dpi. Test artifact: 1 fail cũ chỉ trên Windows (`test_failed_publication_restores_the_original_directory`), còn lại OK.
