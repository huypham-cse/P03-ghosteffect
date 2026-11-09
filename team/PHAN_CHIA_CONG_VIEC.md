# Phân chia công việc: ba phần độc lập

> **Dự án:** GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents (MobiSys 2027)
> **Mốc của hội nghị:** đăng ký abstract **27/11/2026**, nộp bài **4/12/2026**.
> **Mốc của nhóm:** mỗi vai trò xong việc **25/11**; cả ba vai trò được nghiệm thu và chốt số liệu **28/11**; xong hết và nộp HotCRP **30/11**. Từ 1/12 đến 4/12 chỉ để dự phòng.
> **Trạng thái:** bản đề xuất, chờ trưởng nhóm duyệt.

---

## 1. Nguyên tắc

1. **Mỗi người làm chủ trọn một câu hỏi của bài**: dữ liệu, code, render, bảng và văn bản của phần đó.
2. **Mỗi file chỉ có một chủ** (§2). Muốn đổi file của người khác thì nhờ chủ file. `planner_sim.py` là ngoại lệ duy nhất, chia theo hàm.
3. **Giao tiếp qua hợp đồng chốt trước 11/11** (§4): tên macro và schema dữ liệu. Ai dùng số của người khác thì viết ngay bằng macro với giá trị tạm `??`, không chờ.
4. **Chỉ có một bước nối tiếp cứng ở đầu kỳ**: C chạy lại pipeline và tách file (C-01), xong trước **12/11**. Trong lúc đó A viết lý thuyết, B dựng rig.
5. Ba phần chạy **song song**. Chỉ có ba chỗ phải chờ thật (§3): ba ngày đầu với các file C-01 tách, và giai đoạn chốt chờ testbed sạch cùng việc nghiệm thu. Các phụ thuộc còn lại là mềm: thiếu số thì bản build vẫn chạy, chỉ hiện `??`.
6. **Mỗi vai trò xong mọi việc của mình chậm nhất 25/11** và mở PR nghiệm thu cùng ngày. Từ 26/11 đến 30/11 chỉ còn nghiệm thu, sửa lỗi nghiệm thu và chốt chung.
7. **Một phần chỉ được nghiệm thu khi đạt mọi yêu cầu ở §7**, gồm yêu cầu chung và yêu cầu riêng của phần đó.

## 2. Ba phần

| | Phần A | Phần B | Phần C |
|---|---|---|---|
| Câu hỏi | Bảo đảm có đúng không, và cần bao nhiêu nhãn? | Vấn đề có thật không? | GhostEffect có tốt hơn cách khác không, và nên dùng mode nào? |
| Tên | Lý thuyết, bảo đảm và hiệu chuẩn | Đo đạc thực tế và thí nghiệm LLM agent | Đánh giá so sánh và câu chuyện của bài |
| Cần máy | Laptop, LaTeX, Python 3.10+ | Máy có emulator (WHPX hoặc KVM) và GPU Linux từ 24 GB, hoặc API | Linux/WSL để chạy `run_all.py` (khoảng 25 đến 30 phút) |
| Hợp với | Người mạnh toán, thống kê | Người rành Android, có GPU | Trưởng nhóm hoặc người viết tốt nhất |
| Nhánh | `a/theory` | `b/measure` | `c/eval` |

**Đọc trước (ngày đầu, cả ba phần):** `manuscript/main.pdf`, `STATUS.md`, `review.md` (bản phản biện nội bộ và checklist cho tác giả), `resolve.md` (quyết định cho từng điểm review, đánh số R01 đến R32). Phần B đọc thêm `testbed/README.md` và `artifact/results/real/SUMMARY.md`; phần C đọc thêm `artifact/README.md`.

### Phần A: Lý thuyết, bảo đảm và hiệu chuẩn

**Sở hữu:**
- Văn bản: `manuscript/sections/03-model.tex`, `04-theory.tex`, `05-design.tex`, `appendix-proofs.tex` (sau C-01 chỉ còn phần chứng minh và bảng của A).
- Code: trong `artifact/scripts/planner_sim.py` các hàm hiệu chuẩn và chứng nhận (`calibration_deltas`, `certified_wait`, `lag_tables`, `lag_tables_measured`, `lag_wait`, `joint_calibration`, `src_calibration`, `cpu`); file mới `artifact/scripts/render_guarantee.py`; test mới `artifact/tests/test_guarantee.py`.
- Đầu ra: `manuscript/generated/macros_guarantee.tex` và các bảng `generated/tab_cert_*.tex`. Tiền tố macro: `\Cert*`.
- A **chỉ đọc** các CSV `artifact/results/planner_real4_*.csv` do C chạy (các tag `down5`, `down15`, `t0down5`, `t0down15`, `lag2k`, `lag5k`, `lag10k`, `lag20k`, `boot10k`, `tail5`, `tail5tied` đã có). Cần tag mới thì nhờ C.

| ID | Việc | Nguồn | Hạn |
|---|---|---|---|
| A-01 | **Mốc thời gian `r_e` theo lớp lỗi.** Định nghĩa `T_c = max(0, t_visible − r_e)` và `G_c(w)`; deadline `r_e + w_c`; lớp hoặc mốc không biết thì lấy max theo lớp hoặc ASK. Sửa §3, Eq. 2, Alg. 1, chứng minh ở App. A. Bảng nhỏ mốc đúng (`down5`, `down15`) so với mốc sai (`t0down5`, `t0down15`). | R03 | 20/11 |
| A-02 | **Kế toán nhãn.** Tách bốn con số: số lượt đo thật đứng sau hồ sơ Element, số nhãn mỗi lớp (2.000; 5.000), pilot và holdout (500 + 4.500 ở mốc "5.000"), số mẫu lag (`N_LAG = 20000` là mẫu bootstrap). Bảng ngân sách nhãn của A trong §5.3 có dòng tied (`lag2k`, `lag5k`); `lag10k`, `lag20k`, `boot10k` vào phụ lục của A. | R04 | 19/11 |
| A-03 | **Đuôi trễ ở mốc 5k** (`tail5`, `tail5tied`) trong cùng bảng ngân sách nhãn. Báo cả dòng bất lợi: product ở dòng tied vượt ngân sách. Viết trong §5.3 rằng joint chỉ giữ ngân sách khi còn hỏi đủ nhiều. | R05 | 19/11 |
| A-04 | **Cận tổng hợp dup/loss.** `P(dup∣X=1) ≤ min(1, α + q1·ε1 + r1)`, `P(loss∣X=0) ≤ min(1, β + q0·ε0 + r0)`. Dùng cột `q1`, `q0` đã có trong mọi CSV planner; mẫu số 0 ghi N/A. Tính cho product và joint (hồ sơ Element đo được và thế giới mặc định); nói người triển khai nên đọc đại lượng nào. | R10 | 21/11 |
| A-05 | **δ và lớp không biết.** Code đã đúng: `calibration_deltas` dùng `min(α, β)` và chia theo số lớp khi `keyed='all'`; test `test_asymmetric_calibration_pays_both_budgets_and_all_classes` đã có. Việc còn lại: kiểm `k_total` trong `testbed/calibration.py` có gồm số lớp (sai thì nhờ B sửa), và §4.3 nêu đúng công thức. | R11 | 15/11 |
| A-06 | **Chi tiết lý thuyết:** hand-over đặt lại `P` đúng một lần và `R(τ)` gồm phân bổ sau hand-over; A1 nêu `T` độc lập với lượt đọc khi biết `X`; H3 ghi Element không có hop 1 (cửa sổ 20 đến 100 ms ngắn hơn một lần dump); cỡ pilot của Prop 4.4; Prop A.1 là an toàn theo union bound chứ không tối ưu; đổi tên `D` (ví dụ `H_dedup`); đường echo `/sync` của Element có thuộc A1 không. | R12, R13, R22, R27 | 18/11 |
| A-07 | **Rút §4 còn khoảng 1,5 trang.** Thm 4.1 ba dòng kèm ghi chú phần kinh điển; giữ đủ Prop 4.4 và Thm 4.8; chuyển Prop 4.3, Lemma 4.5, Lemma 4.6(iii), Lemma 4.7, saga xuống App. A. Dùng chỗ trống cho walk-through Alg. 1 (một lượt K-9, một lượt Element) ở §5.4. | R29 | 22/11 |
| A-08 | **§5.3:** hop 1 đọc màn hình Outbox qua cây accessibility, không đọc DB của app; thay "khoảng 15 s mỗi nhãn" bằng thời gian đo của B (có từ 24/11) và tính device-hours cho 5.000 nhãn × lớp × kết quả; chuyển Table 1 (cỡ mẫu) xuống phụ lục của A. | R15 | 25/11 |
| A-09 | **Render riêng.** `render_guarantee.py` chỉ đọc CSV, viết `macros_guarantee.tex` và bảng của A. Gửi danh sách tên macro cho C trước 11/11. | | 11/11 (tên), 22/11 (giá trị) |

### Phần B: Đo đạc thực tế và thí nghiệm LLM agent

**Sở hữu:**
- Code và dữ liệu: `testbed/**` (gồm `check_agent_data.py` và `tests/test_agent_data.py` mới); `artifact/results/real/**` (dữ liệu thô chỉ thêm, không sửa), gồm thư mục mới `agent/`; `artifact/scripts/real_params.py`, `render_real.py` (sau C-01 chỉ còn phần đo đạc), `render_agent.py` (mới), `ledger.py`, `bench_ledger.py`; `artifact/results/ledger_bench.csv`.
- Đầu ra: `manuscript/generated/macros_real.tex`, `tab_real.tex`, `tab_realcone.tex`, `real_section.tex`, `tab_agent.tex`. Tiền tố macro: `\Real*`, `\Agent*`, `\Ledger*`, `\LabelTrial*`.
- Văn bản: `manuscript/sections/02-background-motivation.tex`, `06-implementation.tex`, `07-real.tex` (sau C-01 chỉ còn phần đo đạc), `07-agent.tex` (mới), `tab-apps.tex`, `tab-position.tex`, `manuscript/figures/fig1.tex`.

**Phạm vi thí nghiệm agent:** M3A từ AndroidWorld (commit pin `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, giữ nguyên prompt, history và reflection) trên K-9 Mail 24.0 + GreenMail 2.1.2 qua `testbed/faultproxy.py`, hai cấu hình không Sent và có Sent. Lỗi: proxy chuyển DATA, server trả 250 (đã commit), proxy bỏ phản hồi, rồi force-stop và mở lại K-9. Agent bị kill tại lúc lỗi và chạy lại với cùng task trên GUI mới, không được gợi ý gì. Chỉ backend (số bản và Message-ID ở GreenMail) quyết định có trùng hay không. Mỗi episode thuộc đúng một nhóm: `RESENT_DUPLICATE`, `RESENT_BUT_NO_DUP`, `DECLARED_DONE_NO_RESEND`, `ASKED_OR_STOPPED`, `TASK_FAILURE`, `INVALID`. Chỉ dùng nội dung giả trên tài khoản thử.

| ID | Việc | Hạn |
|---|---|---|
| B-01 | **Dựng lại rig.** `runtime/` không có trong git. Chọn một host (Windows + WHPX hoặc Linux + KVM), cài SDK, AVD API 33, APK đúng hash, GreenMail, fault proxy, forwarder của AndroidWorld. Chỉ `--gpu host` từng chạy được; mặc định swiftshader gặp ANR. Ghi nhật ký vào `team/b-log.md`. | 12/11 |
| B-02 | `testbed/setup_agents.py`: clone 4 repo ở commit pin (`codex/models.md`), venv Python 3.11.8, kiểm `import android_world.agents.m3a`. | 13/11 |
| B-03 | Profile K-9 (không Sent, có Sent) và cách reset trạng thái (campaign 2 dọn Outbox bằng root). | 14/11 |
| B-04 | Tái hiện lỗi K-9 bằng `run_case.py` (commit, bỏ phản hồi, force-stop, mở lại). | 15/11 |
| B-05 | **Cổng model.** Ưu tiên Qwen2.5-VL-7B BF16 trên vLLM 0.11.0, máy Linux GPU từ 24 GB, nối với AVD qua SSH tunnel. Phương án API: `local_model.py` chỉ nhận endpoint loopback và `codex/` cấm API trả phí, nên phải viết binding mới và trưởng nhóm duyệt cả ngân sách lẫn thay đổi chính sách. Khóa API chỉ để trong `.env` (đã git-ignore). | 14/11 |
| B-06 | **Harness episode**: mở rộng `testbed/native_episode.py` có sẵn. Reset, chạy M3A, bắt lúc Send, để commit rồi bỏ phản hồi, kill agent và force-stop K-9, mở lại, chạy lại M3A cùng task, quan sát `H_eval = 300 s`, chấm bằng backend, ghi receipt JSON. | 17/11 |
| B-07 | A-dev: 10 episode không lỗi (5 mỗi cấu hình), chỉ để gỡ lỗi, không báo cáo làm kết quả. Thành công dưới 6/10 thì báo trưởng nhóm. | 18/11 |
| B-08 | Freeze: `testbed/agent_study.freeze.json` (model, decoding, hash prompt, task, hash APK/AVD, horizon, luật kết quả, seed, thứ tự episode), merge trước lượt chính thức đầu tiên. | 18/11 |
| B-09 | A-native: 20 episode chính thức (10 không Sent, 10 có Sent, xen kẽ), chạy từ 19/11; mỗi episode tối đa một lần chạy lại vì lỗi đo; giữ mọi lần chạy. "Hợp lệ" nghĩa là backend xác nhận thư gốc đã commit và có biên nhận lỗi. Dưới 10 hợp lệ thì chạy thêm tối đa 10 episode với cùng freeze, xong 23/11. **Chạy xong ngày nào thì báo C số đếm thô (hợp lệ, gửi lại, trùng) ngay ngày đó.** | 22/11 (23/11 nếu chạy thêm) |
| B-10 | **Giao dữ liệu và tự viết phần agent.** `artifact/results/real/agent/` gồm `episodes.csv` (schema §4), `label_cost.csv` (schema §4), `freeze.json`, `receipts/<episode_id>.json`, `SUMMARY.md`. `render_agent.py` sinh `tab_agent.tex` và `\Agent*` (Wilson CI 95%). Viết `07-agent.tex` (khoảng 0,3 trang) và khung lại §2.3 theo kết quả, kể cả khi agent không gửi lại lần nào. | 24/11 (số), 25/11 (văn bản) |
| B-11 | **Chi phí nhãn đo thật**: thời gian một lượt tiêm lỗi chia theo reset, soạn, lỗi, mở lại, quan sát, chấm; min, median, max vào `label_cost.csv` và macro `\LabelTrial*`. | 24/11 |
| B-12 | **Audit thao tác K-9** (R19). `SUMMARY.md` ghi "Send messages 0/12" cho cấu hình không Sent, nhưng `c2_k9_nosent_trials.csv` có `sendmsgs_tapped=0` ở cả 12 dòng đó (số đúng là 8/20 lượt có bấm Send messages). Tách Sync / Send messages / không thao tác / soạn lại; sửa câu trong §7 cho đúng. Lượt audit chạy sau B-09, không chạy song song trên cùng AVD. | 24/11 |
| B-13 | **Trình bày dữ liệu đo:** Table 3b đổi p90 (n = 20) thành min/median/max hoặc dot plot; stale-screen (digest cũ đếm được 1/3 lượt pilot; forwarder trả cây cũ chỉ nêu định tính vì log không còn); lượt mất do ANR coi là quan sát censored; ghi load host (16 đến 38) và thời gian dump khoảng 2 s; câu ở §2.1 về app foreground; Table 5 nằm trong §2.2 (bỏ chữ "(appendix)"). | 22/11 |
| B-14 | **Nonce, Fig. 1, tab-apps:** K-9 dùng subject (người nhận thấy được) trên tài khoản thử có opt-in; sửa Fig. 1(b) và `tab-apps.tex`; thêm cột measured/planned; nhánh G2 của Fig. 1 ghi theo mode khuyến nghị chung. | 15/11 |
| B-15 | Chạy lại `bench_ledger.py` trên host POSIX của B; viết lại đoạn "laptop running macOS" ở §6 (trên WSL, `\LedgerFull*` render ra "--"). | 20/11 |
| B-16 | Làm sạch `testbed/` để đóng gói: không `runtime/`, `runs/`, `*.local.json`, `.env`; `testbed/README.md` bằng tiếng Anh (bản tiếng Việt đổi tên thành `README.vi.md`, không đưa vào gói). | 25/11 |
| B-17 | (Chỉ khi trưởng nhóm duyệt và B-09 xong trước 20/11) Đo độ trễ Element độc lập; cần thêm kill -9 và netcut vào `run_case.py` và một bộ phân tích ra schema `c2_element_first_visible.csv`. | 25/11 |

### Phần C: Đánh giá so sánh và câu chuyện của bài

**Sở hữu:**
- Code: `artifact/run_all.py`, `run_all.sh`, `artifact/scripts/render.py`, `render_realsim.py` (tách ra ở C-01), các script mô phỏng còn lại (`sim_*.py`, `markov_planner.py`, `sample_size.py`, `ge_core.py`); trong `planner_sim.py` mọi thứ không thuộc A (chính sách, baseline, `vetting`, `run`, `summarize`, định nghĩa part, bảng tag REAL4); `artifact/tests/test_regressions.py`, test mới `artifact/tests/test_eval.py`; công cụ của nhóm `team/scrub_check.sh`, `team/readability_count.py`, `team/make_bundle.sh` (mới).
- Đầu ra: `manuscript/generated/macros.tex` và mọi bảng, hình còn lại (gồm `tab_realsim.tex`, `tab_real4.tex`). Tiền tố macro: `\Sim*`, `\Rsim*` và các tiền tố cũ khác.
- Văn bản: `manuscript/main.tex`, `build.sh`, `references.bib`; `manuscript/sections/00-abstract.tex`, `01-introduction.tex`, `07-evaluation.tex`, `07-realsim.tex` (mới), `08-discussion.tex`, `09-related-work.tex`, `10-conclusion.tex`, `appendix-results.tex` (mới); `others/notes.md`.

| ID | Việc | Hạn |
|---|---|---|
| C-01 | **Bước nối tiếp duy nhất** (cơ học, trước khi ai sửa nội dung). (a) Chạy lại toàn bộ (`run_all.py`), diff với CSV và macro đang commit, promote; manifest vào `artifact/runs/<ngày>/MANIFEST.json`. (b) Tách macro thành ba file: `render.py` viết `macros.tex`, `render_real.py` viết `macros_real.tex`, `render_guarantee.py` (khung rỗng cho A) viết `macros_guarantee.tex`; `main.tex` input cả ba. (c) Tách phần Table 4 của `render_real.py` (`\Rsim*`, `tab_realsim`, `tab_real4`) sang `render_realsim.py`. (d) Tách `07-real.tex` từ dòng `\input{generated/tab_realsim}` trở đi sang `07-realsim.tex`. (e) Tách `appendix-proofs.tex` từ `\section{Additional results}` trở đi sang `appendix-results.tex`. (f) Chuyển dòng `\input{sections/tab-position}` từ phụ lục vào §2.2. (g) Tạo `07-agent.tex` rỗng cho B và input nó. (h) Sinh lại `others/notes.md`. Lưu ý: lần build đầu đổi khoảng 54 macro, 11 trong thân bài (`\SimSrcAsk`, `\Ledger*`...). | 12/11 |
| C-02 | **Quyết định chung, phát trước 11/11** (ghi vào `team/QUYET_DINH_CHUNG.md`): mode khuyến nghị theo R06 (product khi A2 có cơ sở cấu trúc, joint ở trường hợp còn lại, ASK khi không gì chứng nhận được, app G2 thì không retry); bảng thuật ngữ (G2 trong văn xuôi là "app tự retry idempotent", hop 1 là "Outbox evidence", chọn một trong ask/escalate). | 11/11 |
| C-03 | **Vetted rules cùng dữ liệu** (R07). Code hiện tại chưa thật sự cùng dữ liệu: vetted lấy max trên n mẫu lag, joint dùng 20.000. Thêm tag cùng ngân sách nhãn và cùng thông tin lag, cho Element, K-9, K-9+Sent; báo cả dòng bất lợi (cùng 2k mẫu lag, joint hỏi 100% còn vetted hỏi 5,3% trên Element). Viết lại các câu "rules retry 28,91 đến 65,85%" và bỏ khỏi abstract. | 20/11 |
| C-04 | **Table 4 và đoạn mô phỏng tham số đo** (`07-realsim.tex`): chú thích nói rõ calibration và test cùng phân phối, lỗi phía committed của Element đo được là 0 (0/99, 0/101), nên bảng kiểm tra bộ máy chứng nhận và cái giá bằng số lần hỏi, không kiểm tra lỗi reader trên màn hình thật; dẫn sang bảng ngân sách nhãn của A khi nói về 12,7%, đuôi trễ và dòng tied. Bỏ các con số viết cứng trong caption của renderer ("12,000", "2,000 per class"). | 22/11 |
| C-05 | **Seed variance**: part mới chạy từng seed (khoảng 40 dòng code) cho các dòng chính của Table 2 và 4. | 24/11 |
| C-06 | **Sắp lại §7:** đo emulator (B), agent (B), mô phỏng tham số đo, mô phỏng mô hình (cắt còn redo, Thm-4.8-only, always-ask, rules, vetted, product, joint), stress và population một đoạn, cơ chế một đoạn. RQ1 đến RQ2 xuống `appendix-results.tex`. Mục "Planned device study" bỏ hoặc còn một câu future work. Dùng `\StressNover` cạnh "rules over in 3/14". Sửa công thức δ ở dòng 16 của `07-evaluation.tex` theo §4.3 của A. | 22/11 |
| C-07 | **Related work:** một câu so sánh cho LIMBO, Agent libOS, VeriGUI; cân nhắc Gray & Reuter 1992, Bailis VLDB 2015 (kiểm nguồn thật trước khi thêm). | 24/11 |
| C-08 | **Abstract** tối đa 200 từ, tối đa 4 con số, viết bằng macro. Khung câu viết trước với `??` và chỉnh theo số đếm thô B báo khi chạy xong (22/11 hoặc 23/11), để câu đúng với mọi kết quả. | 24/11 chốt, 25/11 đăng ký HotCRP |
| C-09 | Intro (mở bằng câu chuyện K-9, tách câu gộp ba kết quả trong một citation), §8 Discussion (giới hạn mới), §10 Conclusion (ba câu bài học, không số). | 25/11 |
| C-10 | **Công cụ kiểm cho cả nhóm:** `team/scrub_check.sh` (quét chuỗi lộ danh tính như tên, tài khoản GitHub, email của nhóm, đường dẫn máy như `/Users/`, `C:\Users`, `D:\`, và chuỗi giống khóa API; thoát khác 0 khi gặp) và `team/readability_count.py` (stdlib; đếm câu quá 45 từ, dấu chấm phẩy mỗi đoạn, `\para{`, `\emph{` theo từng file). Cả nhóm dùng cho YC-09 và YC-12. | 16/11 |
| C-11 | **Lượt đọc cho dễ hiểu** theo checklist 15 điểm ở `review.md` §5 trên các file của C. | 25/11 |
| C-12 | **Chuẩn bị artifact ẩn danh:** README tiếng Anh (lệnh tái lập một dòng, phiên bản Python, thời gian chạy, đầu ra nào phụ thuộc host); `team/make_bundle.sh` đóng gói `artifact/` và `testbed/`, loại `tmp/`, `codex/`, `team/`, `review.md`, `resolve.md`, `report.md`, `runtime/`, `.git`; chạy thử gói qua scrub check. | 25/11 |
| C-13 | **Điều phối chốt chung** (không tính vào hạn 25/11 của vai trò): chạy freeze 28/11 sau khi cả ba vai trò được nghiệm thu; đóng gói, tải artifact và chèn link vào §8 ngày 29/11; kiểm cổng cuối và nộp HotCRP chậm nhất 30/11 (§7.6). | 28/11 đến 30/11 |

## 3. Phụ thuộc giữa các phần

| # | Ai chờ | Chờ gì | Từ ai, khi nào | Loại | Trong lúc chờ |
|---|---|---|---|---|---|
| 1 | A, B | C-01 tách xong file. A chờ `appendix-proofs.tex`; B chờ `07-real.tex`, `render_real.py` và chỗ đặt Table 5 ở §2 | C, 12/11 | **Cứng**, chỉ với các file bị tách | A sửa §3, §4, §5; B dựng rig |
| 2 | A, B | Bản chạy lại và ba file macro | C, 12/11 | Mềm | Dùng CSV đang có trong repo |
| 3 | Cả ba | Chốt tên macro và schema | Cả ba, 11/11 | Mềm, cần một buổi họp ngắn | Làm việc riêng |
| 4 | B | Mode khuyến nghị để ghi nhãn Fig. 1 | C (C-02), 11/11 | Mềm | Dùng mặc định theo R06 |
| 5 | C | Công thức δ cho dòng setup ở §7 | A (A-05), 15/11 | Mềm | Sửa một dòng khi A xong |
| 6 | A, B | `scrub_check.sh` và `readability_count.py` để tự kiểm YC-09, YC-12 | C (C-10), 16/11 | Mềm | Viết bình thường |
| 7 | A | Sửa `k_total` trong `testbed/calibration.py`, chỉ khi A thấy sai | B | Mềm | Viết §4.3 |
| 8 | C | Macro `\Cert*` (tied 5k, đuôi trễ, cận tổng hợp) cho abstract và `07-realsim.tex` | A (A-09), 22/11 | Mềm | Viết câu với `??` |
| 9 | C | Số đếm thô của thí nghiệm agent để viết khung abstract và intro | B (B-09), ngày chạy xong (22/11 hoặc 23/11) | Mềm | Viết câu đúng với mọi kết quả |
| 10 | C | Macro `\Agent*` | B (B-10), 24/11 | Mềm | Viết với `??`; abstract chốt 24/11 |
| 11 | A | `label_cost.csv` để tính device-hours ở §5.3 | B (B-11), 24/11 | Mềm khi viết; **cứng khi nghiệm thu** | Viết công thức với `??` |
| 12 | C (chốt chung) | Testbed sạch để đóng gói artifact | B (B-16), 25/11 | **Cứng**, dùng ngày 29/11 | Chuẩn bị gói phần `artifact/` |
| 13 | C (chốt chung) | Cả ba vai trò được nghiệm thu | Người nghiệm thu, 28/11 | **Cứng** với lần freeze 28/11 và cổng cuối | Không |

## 4. Hợp đồng chốt trước 11/11

- **Tên macro**: mỗi phần gửi danh sách tên macro mà phần khác sẽ dùng, kèm nghĩa và định dạng. Ví dụ phía B: `\AgentScheduledN`, `\AgentValidN`, `\AgentResentN`, `\AgentDupN`, `\AgentAskedN`, `\LabelTrialMedS`; phía A: `\CertTiedFiveJointAsk`, `\CertTailFiveTiedProdPvHi`, `\CertDupBoundJoint`. Giá trị tạm là `??`.
- **`artifact/results/real/params.csv`** giữ nguyên schema `name,value,provenance`.
- **`artifact/results/real/agent/label_cost.csv`**: `component,n,min_s,median_s,max_s`, với `component` thuộc `reset, compose, fault, relaunch, observation, grading, total`.
- **`artifact/results/real/agent/episodes.csv`**, một dòng mỗi lần chạy (kể cả lần không hợp lệ và lần chạy lại):

  ```
  episode_id, scheduled_index, config(nosent|sent), attempt(1|2), agent(m3a), model_id, phase(dev|scheduled),
  t_issue_utc, t_data_250_utc, t_fault_utc, t_relaunch_utc, t_agent_restart_utc, t_end_utc,
  backend_copies_at_horizon, distinct_message_ids, original_committed(0|1), fault_receipt(0|1),
  agent_tapped_send_after_restart(0|1), agent_final_status(done|infeasible|asked|error|timeout),
  outcome(RESENT_DUPLICATE|RESENT_BUT_NO_DUP|DECLARED_DONE_NO_RESEND|ASKED_OR_STOPPED|TASK_FAILURE|INVALID),
  invalid_reason, steps_before_fault, steps_after_restart, prompt_tokens, completion_tokens,
  wall_clock_s, reset_s, observation_s, notes
  ```
- **Mode khuyến nghị và bảng thuật ngữ**: C phát trong `team/QUYET_DINH_CHUNG.md` (C-02).

## 5. Quy tắc làm việc

- **File**: chỉ sửa file mình sở hữu (§2). Trong `planner_sim.py` chỉ sửa các hàm của mình; cần thêm gì thì thêm hàm mới.
- **Test**: mỗi phần viết test trong file test của mình (`test_guarantee.py`, `testbed/tests/test_agent_data.py`, `test_eval.py`). Thay đổi làm hỏng test của phần khác thì báo chủ test.
- **Macro**: mỗi phần render vào file macro của mình; không sửa tay `manuscript/generated/*`.
- **Số liệu**: không gõ tay số kết quả vào `.tex`; mỗi số nói rõ loại (đo trên emulator, mô phỏng theo mô hình, mô phỏng với tham số đo, tính chính xác, chạy LLM agent).
- **Không chỉnh kết quả theo ý muốn**: không đổi seed, họ luật hay ngân sách nhãn sau khi thấy kết quả. Dòng bất lợi vẫn vào bài.
- **Dữ liệu thô** trong `artifact/results/real/**` chỉ được thêm.
- **Không commit** `runtime/`, `testbed/runs/`, `*.local.json`, `.env`, khóa API.
- **Nhánh và PR**: `a/...`, `b/...`, `c/...`; tiêu đề PR `[A-xx]`, `[B-xx]`, `[C-xx]`; trưởng nhóm merge; rebase lên `main` trước mỗi PR.
- **Họp**: tối Chủ nhật, 30 phút. Việc bị chặn thì báo ngay trên nhóm chat.

## 6. Lịch

| Giai đoạn | A | B | C |
|---|---|---|---|
| 9 đến 15/11 | A-05, A-06, nháp A-01; tên macro (A-09) | B-01 đến B-05, B-14 | C-01 (12/11), C-02 (11/11) |
| 16 đến 22/11 | A-01 đến A-04, A-07 | B-06 đến B-08, B-09 (chạy agent từ 19/11, xong 22/11), B-13, B-15 | C-10 (16/11), C-03, C-04, C-06 |
| 23 đến 25/11 | A-08; **xong việc, mở PR nghiệm thu 25/11** | B-10, B-11, B-12, B-16; **xong việc, mở PR nghiệm thu 25/11** | C-05, C-07, C-08 (đăng ký abstract 25/11), C-09, C-11, C-12; **xong việc, mở PR nghiệm thu 25/11** |
| 26 đến 28/11 | Nghiệm thu A, sửa lỗi nghiệm thu | Nghiệm thu B, sửa lỗi nghiệm thu | Nghiệm thu C, sửa lỗi nghiệm thu; **28/11 chạy freeze, chốt số liệu** |
| 29 đến 30/11 | Sẵn sàng sửa lỗi cổng cuối | Sẵn sàng sửa lỗi cổng cuối | C-13: đóng gói artifact 29/11; cổng cuối và **nộp HotCRP chậm nhất 30/11** |
| 1 đến 4/12 | Dự phòng | Dự phòng | Dự phòng (hạn nộp của hội nghị 4/12) |

**Báo ngay cho trưởng nhóm nếu:** emulator chưa chạy ổn trước 13/11; chưa có model trước 14/11; A-dev dưới 6/10 vào 18/11; chưa đủ 10 episode hợp lệ vào 22/11; một vai trò thấy không kịp xong vào 25/11 (báo trước 23/11); build đỏ quá một ngày.

## 7. Yêu cầu nghiệm thu

### 7.1 Quy trình

1. Mỗi vai trò mở PR `[A] Nghiệm thu` (hoặc `[B]`, `[C]`) **chậm nhất 25/11**, chép nguyên bảng §7.2 và yêu cầu riêng của phần mình vào mô tả PR, đánh dấu từng dòng và dán bằng chứng (kết quả lệnh, đường dẫn file, số trang trong PDF).
2. **Người nghiệm thu** là trưởng nhóm hoặc người được trưởng nhóm chỉ định, **không phải chủ phần**. Người nghiệm thu tự chạy lại các lệnh ở cột "Cách kiểm" trên một bản clone sạch của nhánh PR đã rebase lên `main`, không dựa vào kết quả chủ phần dán.
3. **Chỉ nghiệm thu khi đạt mọi yêu cầu**: tất cả yêu cầu chung (YC-01 đến YC-12) và tất cả yêu cầu riêng của phần đó. Không có nghiệm thu một phần, không có miễn trừ. Một dòng không đạt thì PR quay lại chủ phần; sửa xong, người nghiệm thu kiểm lại toàn bộ. **Cả ba vai trò phải được nghiệm thu chậm nhất 28/11.**
4. Yêu cầu kiểm **quy trình và tính trung thực**, không kiểm kết quả đẹp. Không yêu cầu nào đòi GhostEffect thắng baseline hay đòi agent phải gửi lại. Dòng bất lợi được báo đúng là đạt; dòng bất lợi bị giấu là không đạt.
5. Sau khi nghiệm thu, mọi thay đổi trên phần đó phải qua PR mới và kiểm lại các yêu cầu bị ảnh hưởng.
6. **Nghiệm thu cuối** (§7.6) kiểm bản chốt của cả nhóm và phải xong chậm nhất 30/11.
7. Các lệnh kiểm chạy trên Linux hoặc WSL có TeX Live và poppler-utils (`pdftotext`, `pdfinfo`), trừ các lệnh cần rig của B (chạy trên host của B).

### 7.2 Yêu cầu chung (cả ba phần)

| ID | Đạt khi | Cách kiểm |
|---|---|---|
| YC-01 | Bản build sạch: `build.sh` thoát 0 (script đã tự báo lỗi khi có ref hoặc citation chưa định nghĩa); không có overfull box quá 10 pt. | `cd manuscript && sh build.sh`; `grep -oE 'Overfull \\[hv]box \(([0-9.]+)pt' main.log \| tr -dc '0-9.\n' \| awk '$1>10'` không in gì |
| YC-02 | Mọi test qua; phần này có ít nhất một file test cho logic mới của mình. | `python3 -m unittest discover -s artifact/tests` và `python3 -m unittest discover -s testbed/tests` báo OK (chỉ chấp nhận skip vì thiếu môi trường Android) |
| YC-03 | PR chỉ đổi file thuộc phần mình (§2); với `planner_sim.py`, chỉ đổi trong các hàm của mình. | `git diff --name-only origin/main...HEAD`; đọc `git diff origin/main...HEAD -- artifact/scripts/planner_sim.py` |
| YC-04 | Trong các file `.tex` của phần mình, mọi con số kết quả là macro. Tham số (α = 1%, tỉ lệ chia 0,5/0,4/0,1), năm, số hiệu mục không tính. | `grep -nE '[0-9]+([.,][0-9]+)?\\?%\|[0-9]+/[0-9]+' <file .tex của phần>`; người nghiệm thu xét từng dòng |
| YC-05 | Mỗi câu có số nói rõ loại số (đo trên emulator, mô phỏng theo mô hình, mô phỏng với tham số đo, tính chính xác, chạy LLM agent). | Đọc các file của phần |
| YC-06 | File macro của phần không còn `??`. Ở bản nộp, PDF không còn `??`. | `grep -c '??'` trên file macro của phần (A: `macros_guarantee.tex`, B: `macros_real.tex`, C: `macros.tex`) bằng 0; `pdftotext manuscript/main.pdf - \| grep -c '??'` bằng 0 |
| YC-07 | Mỗi CSV mới trong `artifact/results/` có file `<tên>.meta.json` ghi lệnh chạy, git commit, seed, phiên bản Python, ngày, host. | `for f in $(git diff --name-only --diff-filter=A origin/main...HEAD \| grep -E '^artifact/results/.*\.csv$'); do test -f "${f%.csv}.meta.json" \|\| echo THIEU $f; done` không in gì |
| YC-08 | Không chỉnh kết quả theo ý muốn: thay đổi seed, họ luật, ngân sách nhãn, `N_LAG` hay file freeze nằm trong commit riêng, có lý do, và có trước các CSV chịu ảnh hưởng. | `git log -p -- artifact/scripts/planner_sim.py testbed/agent_study.freeze.json`, so thứ tự commit |
| YC-09 | Ẩn danh và bí mật: file của phần qua scrub check; không có file cấm hay khóa trong git. | `sh team/scrub_check.sh <các file của phần>` thoát 0; `git ls-files \| grep -E '^runtime/\|^testbed/runs/\|\.local\.json$\|(^\|/)\.env$'` rỗng; `git grep -nIE '(sk-\|AIza\|hf_)[A-Za-z0-9_-]{16,}'` rỗng |
| YC-10 | Thuật ngữ theo `team/QUYET_DINH_CHUNG.md`: chỉ dùng một trong ask/escalate; "G2" chỉ xuất hiện trong định lý, chứng minh hoặc bảng. | `grep -nE 'escalat\|G2' <file .tex của phần>`, xét từng dòng |
| YC-11 | PR nghiệm thu có đủ checklist và bằng chứng như §7.1. | Đọc PR |
| YC-12 | **Độ dễ đọc** trong các file `.tex` của phần: 0 câu quá 45 từ; mỗi đoạn tối đa 1 dấu chấm phẩy; `\para{` tối đa 5 và `\emph{` tối đa 10 (cả bài tối đa 15 và 30). Bảng số đếm trước và sau dán trong PR. | `python3 team/readability_count.py <file .tex của phần>` |

### 7.3 Yêu cầu riêng của phần A

| ID | Đạt khi | Cách kiểm |
|---|---|---|
| YC-A1 | **Mốc thời gian.** §3 định nghĩa `r_e` cho cả bốn lớp (agent chết: ISSUED; app chết: lúc xác nhận ý định mở lại; mất mạng: lúc khôi phục; kết hợp: mốc muộn hơn), `T_c`, `G_c(w)`, và cách xử lý lớp hoặc mốc không biết. Eq. 2, Alg. 1 và chứng minh ở App. A dùng `r_e + w`. Có bảng mốc đúng so với mốc sai (5 s, 15 s; product và joint; `P_v` và cận CP). Có test kiểm rằng planner không kết luận "absent" trước `r_e + w`. | `grep -n 'WaitUntil' manuscript/sections/05-design.tex` không còn `t_0+w`; đối chiếu 4 ô của bảng với `planner_real4_{down5,down15,t0down5,t0down15}.csv`; test trong `test_guarantee.py` qua |
| YC-A2 | **Kế toán nhãn.** §5.3 nêu riêng bốn con số (lượt đo thật, nhãn mỗi lớp, pilot và holdout 500 + 4.500, mẫu lag 20.000 bootstrap) bằng macro. Bảng ngân sách nhãn có dòng tied 2k và 5k cho product và joint trên Element (`P_v`, cận CP, % hỏi); `lag10k`, `lag20k`, `boot10k` ở phụ lục. Trong file của A, không câu nào ngụ ý 5.000 nhãn một mình cho ra tỉ lệ hỏi của dòng không tied. | Đối chiếu bảng với `planner_real4_lag2k.csv`, `lag5k.csv`; đọc mọi câu dùng macro tỉ lệ hỏi ở mốc 5.000 nhãn |
| YC-A3 | **Đuôi trễ.** Bảng ngân sách nhãn có dòng `tail5`, `tail5tied` (joint và product: `P_v`, cận CP, % hỏi) khớp CSV. Dòng nào có cận CP vượt α được ghi "vượt ngân sách" trong bảng và trong câu. §5.3 có câu: joint chỉ giữ ngân sách khi còn hỏi đủ nhiều. | Đối chiếu với `planner_real4_tail5.csv`, `tail5tied.csv` |
| YC-A4 | **Cận tổng hợp.** Công thức cho `P(dup∣X=1)` và `P(loss∣X=0)` với định nghĩa `q1, q0, ε1, ε0, r1, r0`; giá trị cho product và joint (hồ sơ Element đo được và thế giới mặc định) tính từ cột `q1`, `q0`; nêu rõ ε dùng giá trị nào và `r1 = r0 = 0` là giả định trong simulator; mẫu số 0 in N/A; một câu nói người triển khai nên đọc đại lượng nào. | Người nghiệm thu tự tính lại 2 giá trị bằng tay từ CSV; test N/A trong `test_guarantee.py` qua |
| YC-A5 | **δ.** §4.3 nêu `δ = min(α, β) / (10 · K · số lớp)`, khớp `calibration_deltas` và `k_total` trong `testbed/calibration.py`. | Đọc §4.3 và hai đoạn code; `test_asymmetric_calibration_pays_both_budgets_and_all_classes` qua |
| YC-A6 | **Chi tiết lý thuyết** có đủ bảy mục của A-06. Ký hiệu horizon cũ `D` không còn. | Đọc §3, §4, App. A; `grep -nE 'horizon[^.]*\$D\$\|within \$D\$' manuscript/sections/*.tex` rỗng |
| YC-A7 | **Độ dài và bố cục.** Trong PDF, từ tiêu đề §4 đến tiêu đề §5 không quá 3 cột (1,5 trang). Thm 4.1 trong thân bài không quá 3 dòng và có ghi chú phần kinh điển. Prop 4.3, Lemma 4.5, Lemma 4.6(iii), Lemma 4.7 và saga nằm ở App. A, có câu trỏ tới. §5.4 có hai walk-through (K-9, Element) dẫn số dòng của Alg. 1. | Đếm cột trong PDF; đọc |
| YC-A8 | **§5.3.** Không còn câu hop 1 đọc DB của app. Chi phí nhãn dùng số đo của B: median một lượt và device-hours cho 5.000 nhãn × lớp × kết quả, đều là macro có giá trị. Table 1 chỉ còn ở phụ lục. | `grep -n 'local database' manuscript/sections/05-design.tex` rỗng; `grep -n 'tab_nsize' manuscript/sections/05-design.tex` rỗng |
| YC-A9 | **Render.** `render_guarantee.py` chạy chỉ từ CSV, chỉ ghi `macros_guarantee.tex` và `tab_cert_*.tex`, chạy hai lần ra kết quả giống hệt từng byte, và thoát khác 0 khi thiếu CSV đầu vào (không ghi số 0). | Chạy hai lần, so `sha256sum`; đổi tên tạm một CSV rồi chạy, phải lỗi |

### 7.4 Yêu cầu riêng của phần B

| ID | Đạt khi | Cách kiểm |
|---|---|---|
| YC-B1 | **Rig.** `team/b-log.md` có nhật ký theo ngày từ đầu đến cuối (đã chạy gì, lỗi gì, đường dẫn receipt) và mô tả host (OS, CPU, RAM, tăng tốc, chế độ GPU). SHA-256 của mọi APK và JAR đã dùng khớp file lock. | Đọc log; kết quả kiểm hash của `setup_assets.py` dán trong PR |
| YC-B2 | **`setup_agents.py`.** Trên bản clone mới, script tạo `runtime/agents/SETUP.json` với 4 repo đúng commit pin trong `codex/models.md`, cây sạch; import M3A trong venv thành công. | Chạy script; python của `runtime/agent-venv` chạy `-c "import android_world.agents.m3a"` thoát 0 |
| YC-B3 | **Freeze trước khi chạy.** Thời điểm commit của `testbed/agent_study.freeze.json` sớm hơn `t_issue_utc` nhỏ nhất của các episode `scheduled`. Freeze có model và revision, decoding, hash prompt, task, hash APK/AVD, `H_eval = 300`, luật kết quả, seed, thứ tự episode. `artifact/results/real/agent/freeze.json` giống hệt bản đã commit. | `git log -1 --format=%cI -- testbed/agent_study.freeze.json` so với CSV; `sha256sum` hai file |
| YC-B4 | **Dữ liệu agent hợp lệ.** `check_agent_data.py` thoát 0. Script kiểm: header đúng schema và thứ tự §4; có mọi lần chạy (dev, scheduled, invalid, chạy lại); từ 20 episode scheduled theo đúng thứ tự trong freeze; **từ 10 episode hợp lệ** (`original_committed=1` và `fault_receipt=1`); mỗi episode tối đa một lần chạy lại và chỉ vì lỗi đo; `outcome` thuộc 6 nhóm và khớp trường backend (ví dụ `RESENT_DUPLICATE` khi và chỉ khi `distinct_message_ids ≥ 2`); dòng nào cũng có receipt; hash prompt trong mọi receipt bằng hash trong freeze. Test của checker có một fixture lỗi và phải bắt được lỗi đó. | `python3 testbed/check_agent_data.py artifact/results/real/agent`; `python3 -m unittest testbed/tests/test_agent_data.py` |
| YC-B5 | **Agent không bị sửa.** Cuối đợt chạy, 4 repo trong `runtime/vendor/` sạch và đúng commit pin; mọi sửa binding nằm trong `testbed/` và có test. | Kết quả `git -C runtime/vendor/<repo> status --porcelain` và `rev-parse HEAD` dán trong `b-log.md` |
| YC-B6 | **Mục agent trong bài.** `07-agent.tex` không quá 0,6 cột trong PDF; nêu model và phiên bản, host, kiểu lỗi, `H_eval`, số episode scheduled, hợp lệ, không hợp lệ (kèm lý do), gửi lại, trùng ở backend, hỏi hoặc dừng, thất bại tác vụ, khoảng tin cậy Wilson 95% cho tỉ lệ gửi lại, median thời gian; mọi số là macro `\Agent*`; có danh sách giới hạn (một agent, một model, chỉ emulator, chỉ force-stop, n nhỏ). §2.3 khớp kết quả: nếu không lần nào gửi lại thì tiêu đề và câu chữ §2.3 không còn nói agent hay tạo ghost effect. | Đọc PDF; YC-04 trên `07-agent.tex` |
| YC-B7 | **Chi phí nhãn.** `label_cost.csv` đúng schema §4, tính từ receipt bằng script; checker tính lại ra cùng giá trị; macro `\LabelTrial*` khớp CSV. | `check_agent_data.py` kiểm lại; so macro với CSV |
| YC-B8 | **Audit K-9 và dữ liệu thô.** Câu trong bài về thao tác "Send messages" khớp số đếm `sendmsgs_tapped` trong CSV; lượt audit mới nằm trong CSV mới có cột loại thao tác (sync, send_messages, none, recompose). File thô cũ không bị sửa hay xóa; `SUMMARY.md` chỉ được thêm đoạn mới. | `git diff --numstat origin/main...HEAD -- artifact/results/real/ \| awk '$2!=0'` rỗng (không file nào bị xóa dòng) |
| YC-B9 | **Trình bày số đo.** Table 3b có min, median, max và n cho từng lớp lỗi (hoặc dot plot đủ điểm); có số sự kiện stale-screen kèm mẫu số; lượt mất do ANR được mô tả là censored và nói cách xử lý; có load host và thời gian dump, ghi là cận dưới của mọi độ trễ; câu §2.1 về app foreground đã sửa. | Đọc PDF |
| YC-B10 | **Nonce, Fig. 1, tab-apps, Table 5.** Fig. 1(b), `tab-apps.tex`, §6 và §7 cùng ghi K-9 dùng subject (người nhận thấy được), có opt-in trên tài khoản thử. `tab-apps` có cột measured/planned điền cho mọi dòng. Nhánh G2 của Fig. 1 ghi đúng mode trong `team/QUYET_DINH_CHUNG.md`. Table 5 được dẫn trong §2.2, không còn chữ "(appendix)". | `grep -ni 'subject' manuscript/sections/*.tex manuscript/figures/fig1.tex`; đọc PDF |
| YC-B11 | **Ledger.** `ledger_bench.csv` chạy lại trên host của B, có `.meta.json`; §6 nêu đúng host đó; không còn chữ macOS hay `F_FULLFSYNC` trừ khi đo trên macOS; không macro `\Ledger*` nào trong thân bài render ra "--". | `grep -nE 'macOS\|FULLFSYNC' manuscript/sections/06-implementation.tex`; đọc PDF |
| YC-B12 | **Gói testbed.** Scrub check qua trên `testbed/`; `testbed/README.md` bằng tiếng Anh; test testbed qua. | `sh team/scrub_check.sh testbed/` thoát 0 |

### 7.5 Yêu cầu riêng của phần C

| ID | Đạt khi | Cách kiểm |
|---|---|---|
| YC-C1 | **Chạy lại sạch.** Từ `main` sạch, `run_all.py` chạy mọi job thoát 0; manifest ghi từng job, mã thoát, hash đầu vào và đầu ra, phiên bản Python, và được lưu ở `artifact/runs/<ngày>/MANIFEST.json`. CSV trong `artifact/results/` trùng đầu ra của lần chạy (trừ `ledger_bench.csv` của B). `others/notes.md` sinh lại từ macro hiện tại. | `python3 artifact/run_all.py --output-dir <thư mục> --jobs 4`; so `sha256sum`; kiểm ngẫu nhiên 5 macro trong `notes.md` |
| YC-C2 | **Cấu trúc sau C-01.** Có ba file macro, mỗi file do đúng một renderer ghi (dòng đầu ghi tên renderer); `07-realsim.tex`, `07-agent.tex`, `appendix-results.tex` tồn tại và được input; Table 5 input trong §2.2; renderer lỗi thì `generated/` giữ nguyên. | `head -1 manuscript/generated/macros*.tex`; YC-01 qua; test renderer trong `test_regressions.py` qua |
| YC-C3 | **Mode khuyến nghị.** `team/QUYET_DINH_CHUNG.md` có ngày không muộn hơn 11/11. Abstract, dòng in đậm của Table 2, §7, §10 và Fig. 1 nêu cùng một mode. | `grep -ni 'recommend' manuscript/sections/*.tex`; đọc Table 2 và Fig. 1 trong PDF |
| YC-C4 | **Vetted cùng dữ liệu.** Có tag mà vetted rules và joint nhận cùng ngân sách nhãn và cùng số mẫu lag, cho Element, K-9, K-9+Sent; test kiểm hai bên nhận cùng đầu vào; bảng có các dòng này kể cả khi bất lợi cho GhostEffect. Abstract không còn số P_v của rules trên K-9; mọi số rules trên K-9 còn lại ghi rõ là mô phỏng với luật trễ K-9 giả định. | Test trong `test_eval.py` qua; `grep -nE 'RsimK(sent\|nine)RulesPv' manuscript/sections/00-abstract.tex` rỗng |
| YC-C5 | **Table 4.** Chú thích nêu đủ: calibration và test cùng phân phối đo được; lỗi phía committed của Element đo được là 0 (0/99, 0/101); bảng kiểm tra bộ máy chứng nhận và cái giá bằng số lần hỏi, không kiểm tra lỗi reader trên màn hình thật. Mọi câu dùng tỉ lệ hỏi của dòng 5.000 nhãn đều nói rõ kích thước bảng lag hoặc dẫn sang bảng ngân sách nhãn của A. Caption trong renderer không còn kích thước viết cứng. | Đọc PDF; `grep -nE "12\{?,\}?000\|2\{?,\}?000 per class" artifact/scripts/render*.py` rỗng |
| YC-C6 | **Seed variance.** CSV theo từng seed (5 seed) cho các dòng chính của Table 2 (product, joint, rules, Thm-4.8-only) và Table 4 trên Element (product, joint, vetted); bài nêu mean ± sd hoặc khoảng bằng macro. | Đọc CSV và PDF |
| YC-C7 | **§7.** Thứ tự: đo emulator, agent, mô phỏng tham số đo, mô phỏng mô hình, stress và population (một đoạn), cơ chế (một đoạn). RQ1 đến RQ2 nằm ở `appendix-results.tex`. Bảng mô phỏng chính chỉ còn redo, Thm-4.8-only, always-ask, rules, vetted rules, product, joint. Công thức δ ở phần setup khớp §4.3. `\StressNover` đứng cạnh số stress của rules. | Đọc PDF |
| YC-C8 | **Abstract.** Không quá 200 từ; không quá 4 con số trong PDF; không có số mô phỏng hai chữ số thập phân; có kết quả agent; mode khuyến nghị khớp YC-C3; đã đăng ký HotCRP chậm nhất 25/11. | `detex manuscript/sections/00-abstract.tex \| wc -w`; đếm số trong abstract của PDF; xác nhận đăng ký dán trong PR |
| YC-C9 | **Intro, Discussion, Conclusion.** Intro mở bằng câu chuyện K-9 và có câu mô tả một câu trước khi đặt tên khái niệm; câu gộp ba kết quả trong một citation đã tách. Câu "We ran no LLM agent" được cập nhật theo kết quả của B ở mọi chỗ. Conclusion có ba câu bài học, không chữ số và không macro kết quả. Discussion nêu giới hạn khớp phạm vi của B. | `grep -n 'no LLM agent' manuscript/sections/*.tex`; `sed 's/K-9//g' manuscript/sections/10-conclusion.tex \| grep -cE '[0-9]\|\\(Sim\|Rsim\|Real\|Agent\|Cert)'` bằng 0 |
| YC-C10 | **Related work và citation.** Mỗi hệ LIMBO, Agent libOS, VeriGUI có một câu so sánh. Mọi bib key mới có trong danh sách kiểm nguồn `others/citation-audit.md` kèm DOI hoặc URL đã mở được. | Đọc §9; so `git diff origin/main...HEAD -- manuscript/references.bib` với danh sách kiểm |
| YC-C11 | **Công cụ kiểm của nhóm.** `team/scrub_check.sh` và `team/readability_count.py` có trên `main` chậm nhất 16/11. `scrub_check.sh` thoát khác 0 trên một file tạm chứa `/Users/abc` và thoát 0 trên file sạch. `readability_count.py` chạy trên toàn bộ thân bài cho tổng `\para{` tối đa 15, `\emph{` tối đa 30 và 0 câu quá 45 từ; bảng tổng trước và sau dán trong PR. | `git log --diff-filter=A --format=%cI origin/main -- team/scrub_check.sh team/readability_count.py`; chạy hai script |
| YC-C12 | **Chuẩn bị artifact.** README tiếng Anh nêu lệnh tái lập một dòng, phiên bản Python, thời gian chạy, đầu ra nào phụ thuộc host. `team/make_bundle.sh` tạo gói không có `tmp/`, `codex/`, `team/`, `review.md`, `resolve.md`, `report.md`, `runtime/`, `.git`; gói chạy thử qua scrub check. | Chạy `sh team/make_bundle.sh <thư mục thử>`; liệt kê file trong gói; `sh team/scrub_check.sh <thư mục thử>` thoát 0 |

### 7.6 Nghiệm thu cuối (cả nhóm, chậm nhất 30/11)

C điều phối (C-13), trưởng nhóm nghiệm thu. Từ 29/11 đến 30/11 cả ba vai trò phải sẵn sàng sửa lỗi. Mọi dòng dưới đây phải đạt mới được nộp.

| ID | Đạt khi | Cách kiểm |
|---|---|---|
| YC-F1 | **Freeze 28/11.** Sau khi cả ba vai trò được nghiệm thu, chạy sạch `run_all.py` từ `main`: mọi job thoát 0, manifest lưu ở `artifact/runs/<ngày>/MANIFEST.json`, CSV trong repo trùng đầu ra. Sau commit freeze chỉ còn commit chèn link artifact vào §8. | So `sha256sum`; `git log` sau commit freeze không đổi `artifact/` hay số liệu |
| YC-F2 | **Artifact ẩn danh.** Gói tạo bằng `make_bundle.sh` từ commit freeze; scrub check qua trên gói và trên `manuscript/`; link mở được từ cửa sổ ẩn danh và có trong §8; tải gói từ link rồi chạy `run_all.py` ra CSV trùng `artifact/results/` (trừ file phụ thuộc host đã liệt kê trong README). | `sh team/scrub_check.sh <thư mục gói>` và `sh team/scrub_check.sh manuscript/` thoát 0; tải, chạy, so `sha256sum` |
| YC-F3 | **Cổng cuối của PDF.** Kết luận kết thúc ở trang 12 hoặc sớm hơn, References bắt đầu ở trang 13 hoặc sớm hơn; PDF không còn `??`; `pdfinfo` không lộ tên người; không có phần cảm ơn; các lệnh kiểm YC-01 đến YC-12 chạy lại trên bản cuối đều đạt. | `main.aux` và PDF; `pdfinfo manuscript/main.pdf`; `pdftotext manuscript/main.pdf - \| grep -c '??'` bằng 0 |
| YC-F4 | **Nộp bài.** Đã nộp HotCRP chậm nhất 30/11; nội dung chữ của PDF đã nộp trùng PDF build lại từ commit cuối (freeze cộng link artifact). | Xác nhận nộp dán trong PR; so `pdftotext` của hai PDF |

## 8. Cần trưởng nhóm quyết

1. Duyệt cách chia này, giao người cho A, B, C và chỉ định người nghiệm thu cho từng phần.
2. Xác nhận nhóm **được sửa paper**: `resolve.md` và `report.md` còn ghi quyết định cũ "không chỉnh paper, paper để sau".
3. Đường model cho B: máy GPU Linux hay API (kèm ngân sách).
4. Mode khuyến nghị cuối cùng (mặc định theo `resolve.md` R06).
