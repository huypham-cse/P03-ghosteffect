# Phân chia công việc theo phần (đề xuất thay cho cách chia trong CONTRIBUTOR_1..3)

> **Dự án:** GhostEffect: Budgeted Exactly-Once Recovery of GUI-Only Effects for Mobile Agents (MobiSys 2027)
> **Mốc cứng:** đăng ký abstract **27/11/2026**, chốt số liệu **1/12**, nộp HotCRP **3/12** (4/12 chỉ để dự phòng).
> **Trạng thái:** bản đề xuất, chờ trưởng nhóm duyệt. Khi được duyệt, file này thay cho phần phân việc và tracker trong `CONTRIBUTOR_1.md`, `CONTRIBUTOR_2.md`, `CONTRIBUTOR_3.md`. Phần "đọc trước", hướng dẫn cài đặt và quy tắc số liệu trong ba file đó vẫn dùng được.

---

## 1. Vì sao chia lại

Cách chia cũ theo **loại việc**: C1 viết, C2 làm số, C3 đo. Vì vậy gần như mục review nào cũng bị cắt đôi: C2 render bảng, C1 viết câu. 9 trên 20 task chính của C1 có cột "Dep", và không ai làm chủ trọn một phần nội dung.

Khi đối chiếu với code, phần lớn mục số liệu mà review đòi **đã có CSV sẵn** (`planner_real4_*.csv`, các cột `q1`/`q0` trong mọi CSV planner, macro `\StressNover`). Việc còn lại chủ yếu là render và viết. Cắt đôi một việc như vậy giữa hai người chỉ làm tăng phối hợp.

Một số task cũ đã xong hoặc sai tiền đề (xem §8).

## 2. Nguyên tắc

1. **Mỗi người làm chủ trọn một câu hỏi của bài**: dữ liệu, code, render, bảng và văn bản của phần đó.
2. **Mỗi file chỉ có một chủ** (§6). Muốn đổi file của người khác thì nhờ chủ file.
3. **Giao tiếp qua hợp đồng chốt trước 11/11** (§5): tên macro và schema CSV. Ai dùng số của người khác thì viết ngay bằng macro với giá trị tạm `??`, không chờ.
4. **Chỉ có một bước nối tiếp cứng**: C chạy lại pipeline và tách file macro, xong trước **12/11**. Trong lúc đó A viết lý thuyết, B dựng rig.
5. Ba phần chạy **song song**. Phụ thuộc còn lại đều là phụ thuộc mềm qua macro: thiếu số thì bản build vẫn chạy, chỉ hiện `??`.

## 3. Ba phần

| | Phần A | Phần B | Phần C |
|---|---|---|---|
| Câu hỏi | Bảo đảm có đúng không, và cần bao nhiêu nhãn? | Vấn đề có thật không? | GhostEffect có tốt hơn cách khác không, và nên dùng mode nào? |
| Tên | Lý thuyết, bảo đảm và hiệu chuẩn | Đo đạc thực tế và thí nghiệm LLM agent | Đánh giá so sánh và câu chuyện của bài |
| Cần máy | Laptop, LaTeX, Python (POSIX/WSL để chạy tag) | Máy có emulator (WHPX hoặc KVM) và GPU Linux từ 24 GB, hoặc API | Linux/WSL để chạy `run_all.py` (khoảng 25 đến 30 phút) |
| Hợp với | Người mạnh toán, thống kê | Người rành Android, có GPU | Trưởng nhóm hoặc người viết tốt nhất |
| Nhánh | `a/theory` | `b/measure` | `c/eval` |

### Phần A: Lý thuyết, bảo đảm và hiệu chuẩn

**Sở hữu:** `manuscript/sections/03-model.tex`, `04-theory.tex`, `05-design.tex`, `appendix-proofs.tex` (phần chứng minh); `artifact/scripts/sample_size.py`; trong `planner_sim.py` các hàm hiệu chuẩn và chứng nhận (`calibration_deltas`, `certified_wait`, `lag_tables`, `lag_tables_measured`, `lag_wait`, `joint_calibration`, `src_calibration`, `cpu`) và các tag REAL4 về clock, lag, tail; file mới `artifact/scripts/render_guarantee.py` xuất ra `manuscript/generated/macros_guarantee.tex` và các bảng của phần A. Tiền tố macro: `\Cert*`.

| ID | Việc | Nguồn review | Hạn | Xong khi |
|---|---|---|---|---|
| A-01 | **Mốc thời gian `r_e` theo lớp lỗi.** Định nghĩa `T_c = max(0, t_visible − r_e)` và `G_c(w)`; deadline `r_e + w_c`; lớp hoặc mốc không biết thì lấy max hoặc ASK. Sửa §3, Eq. 2, Alg. 1, chứng minh. Bảng nhỏ mốc đúng (`down5`, `down15`) so với mốc sai (`t0down5`, `t0down15`); CSV đã có. | R03, meta bắt buộc 1 | 20/11 | Văn bản, thuật toán và chứng minh khớp nhau; bảng render từ CSV |
| A-02 | **Kế toán nhãn.** Tách bốn con số: số đo thật, số nhãn, pilot và holdout (500 + 4.500 ở mốc "5.000"), số mẫu lag (`N_LAG = 20000` là mẫu bootstrap). Thêm dòng tied (`lag2k`, `lag5k`); `lag10k`, `lag20k`, `boot10k` vào phụ lục. | R04, meta bắt buộc 2 | 19/11 | Không câu nào ngụ ý 5.000 nhãn một mình cho ra 12,7% |
| A-03 | **Đuôi trễ ở mốc 5k** (`tail5`, `tail5tied`). Báo cả dòng bất lợi: product ở dòng tied vượt ngân sách (cận CP 1,21%). Viết lại "joint vẫn giữ ngân sách" thành "joint chỉ giữ khi còn hỏi đủ nhiều". | R05, meta bắt buộc 3 | 19/11 | Câu khớp `planner_real4_tail5*.csv` |
| A-04 | **Cận tổng hợp dup/loss.** `P(dup∣X=1) ≤ min(1, α + q1·ε1 + r1)`, `P(loss∣X=0) ≤ min(1, β + q0·ε0 + r0)`. Dùng cột `q1`, `q0` đã có; mẫu số 0 ghi N/A. Tính cho các dòng product và joint của Table 4; nói người triển khai nên đọc đại lượng nào. | R10, meta bắt buộc 9 | 21/11 | Bảng hoặc macro `\Cert*`; không dùng con số minh họa `0.05 × 72.9%` |
| A-05 | **δ và lớp không biết.** Code đã chia theo số lớp khi `keyed='all'` (có test). Sửa δ dùng `min(α, β)` thay vì chỉ `α`, thêm test β < α. Viết rõ ở §4.3. Nếu `testbed/calibration.py` cần sửa thì nhờ B. | R11 | 18/11 | Test qua; §4.3 nêu đúng công thức |
| A-06 | **Chi tiết lý thuyết:** hand-over đặt lại `P` đúng một lần và `R(τ)` gồm phân bổ sau hand-over (R12); A1 nêu `T` độc lập với lượt đọc khi biết `X`; H3 ghi Element không có hop 1 (cửa sổ 20 đến 100 ms ngắn hơn một lần dump); cỡ pilot của Prop 4.4; Prop A.1 là an toàn theo union bound chứ không tối ưu; đổi tên `D` (ví dụ `H_dedup`); đường echo `/sync` của Element có thuộc A1 không. | R12, R13, R22, R27; C1-18, C1-24, C1-27 đến C1-30 cũ | 18/11 | Mỗi mục một câu hoặc một đoạn trong §3, §4 hoặc App. A |
| A-07 | **Rút §4 còn khoảng 1,5 trang.** Thm 4.1 ba dòng; giữ Prop 4.4 và Thm 4.8; chuyển Prop 4.3, Lemma 4.5, Lemma 4.6(iii), Lemma 4.7, saga xuống App. A. Dùng chỗ trống cho walk-through Alg. 1 (một lượt K-9, một lượt Element) ở §5.4. | R29; C1-13 cũ | 22/11 | §4 khoảng 1,5 trang |
| A-08 | **§5.3:** hop 1 đọc màn hình Outbox qua cây accessibility, không đọc DB của app; thay "khoảng 15 s mỗi nhãn" bằng macro thời gian đo của B và tính device-hours cho 5.000 nhãn × lớp × kết quả; chuyển Table 1 (cỡ mẫu) xuống phụ lục. | R15; C1-14, C1-19 (Table 1), C1-21 cũ | 28/11 | Dùng `\LabelTrial*` của B |
| A-09 | **Render riêng.** `render_guarantee.py` chỉ đọc CSV, viết `macros_guarantee.tex` và bảng của A. Gửi danh sách tên macro cho C trước 11/11. | | 11/11 (tên), 22/11 (giá trị) | Build chạy với file macro riêng |

### Phần B: Đo đạc thực tế và thí nghiệm LLM agent

**Sở hữu:** `testbed/**`; `artifact/results/real/**` (dữ liệu thô chỉ thêm, không sửa); `artifact/scripts/real_params.py` (sinh `params.csv`); phần đo đạc của `render_real.py` (Table 3, macro `\Real*`); file mới `render_agent.py`; `bench_ledger.py`; tất cả xuất ra `manuscript/generated/macros_real.tex`. Văn bản: §2 (trọng tâm §2.3), §6, các đoạn đo đạc của §7 (Setup, G2 theo app, Evidence families and lag) và mục agent mới, `figures/fig1.tex`, `sections/tab-apps.tex`. Tiền tố macro: `\Real*`, `\Agent*`, `\Ledger*`, `\LabelTrial*`.

| ID | Việc | Hạn | Xong khi |
|---|---|---|---|
| B-01 | **Dựng lại rig.** `runtime/` không có trong git. Chọn một host (Windows + WHPX hoặc Linux + KVM), cài SDK, AVD API 33, APK đúng hash, GreenMail, fault proxy, forwarder của AndroidWorld. Chỉ `--gpu host` từng chạy được; mặc định swiftshader gặp ANR. | 12/11 | Preflight và smoke qua; ghi vào `team/b-log.md` |
| B-02 | `testbed/setup_agents.py`: clone 4 repo ở commit pin (`codex/models.md`), venv Python 3.11.8, kiểm `import android_world.agents.m3a`. | 13/11 | Clone mới chạy script là import được |
| B-03 | Profile K-9 (không Sent, có Sent) và cách reset trạng thái (campaign 2 dọn Outbox bằng root). | 14/11 | Reset 3/3 lần ra cùng trạng thái |
| B-04 | Tái hiện lỗi K-9 bằng `run_case.py` (commit, bỏ phản hồi, force-stop, mở lại). | 15/11 | 3/3 lượt ra trạng thái lỗi K-9, backend có đúng 1 bản |
| B-05 | **Cổng model G1.** Ưu tiên Qwen2.5-VL-7B BF16 trên vLLM, máy Linux GPU từ 24 GB, nối với AVD qua SSH tunnel. Phương án API: `local_model.py` chỉ nhận endpoint loopback và `codex/` cấm API trả phí, nên phải viết binding mới và trưởng nhóm duyệt cả ngân sách lẫn thay đổi chính sách. | 14/11 | Quyết định ghi vào log |
| B-06 | **Harness episode**: mở rộng `testbed/native_episode.py` có sẵn (không viết file mới). Reset, chạy M3A, bắt lúc Send, để commit rồi bỏ phản hồi, kill agent và force-stop K-9, mở lại, chạy lại M3A cùng task, quan sát `H_eval = 300 s`, chấm bằng backend, ghi receipt JSON. | 18/11 | Chạy thử 2 episode ra receipt đầy đủ |
| B-07 | A-dev: 10 episode không lỗi (5 mỗi cấu hình). | 19/11 | Thành công từ 6/10, không thì báo trưởng nhóm |
| B-08 | Freeze: `testbed/agent_study.freeze.json` (model, decoding, hash prompt, task, hash APK/AVD, horizon, luật kết quả, thứ tự episode). | 19/11 | Merge trước lượt chính thức đầu tiên |
| B-09 | A-native: 20 episode chính thức (10 không Sent, 10 có Sent, xen kẽ); mỗi episode tối đa một lần chạy lại vì lỗi đo; giữ mọi lần chạy. | 24/11 | Từ 10 episode hợp lệ trở lên |
| B-10 | **Giao dữ liệu và tự viết phần agent.** `artifact/results/real/agent/` (schema ở `CONTRIBUTOR_3.md` §4), `render_agent.py` sinh `tab_agent.tex` và `\Agent*` (Wilson CI 95%). Viết mục agent ở §7 (khoảng 0,3 trang) và khung lại §2.3 theo kết quả, kể cả khi agent không gửi lại lần nào. | 26/11 (số), 29/11 (văn bản) | Mọi số trong mục agent là macro |
| B-11 | **Chi phí nhãn đo thật**: thời gian một lượt tiêm lỗi chia theo reset, soạn, lỗi, mở lại, quan sát, chấm; min, median, max thành macro `\LabelTrial*` cho A. | 26/11 | Macro có giá trị |
| B-12 | **Audit thao tác K-9** (R19). SUMMARY ghi "Send messages 0/12" cho cấu hình không Sent, nhưng `c2_k9_nosent_trials.csv` có `sendmsgs_tapped=0` ở cả 12 dòng đó. Tách Sync / Send messages / không thao tác / soạn lại; sửa câu trong §7 cho đúng. | 24/11 | Câu trong bài khớp dữ liệu |
| B-13 | **Trình bày dữ liệu đo:** Table 3b đổi p90 (n = 20) thành min/median/max hoặc dot plot; stale-screen (digest cũ đếm được 1/3 lượt pilot; forwarder trả cây cũ chỉ nêu định tính vì log không còn); lượt mất do ANR coi là quan sát censored; ghi load host (16 đến 38) và thời gian dump khoảng 2 s; câu ở §2.1 về app foreground. | 22/11 | C1-16, C1-17, C1-22, C1-23, C1-26 cũ được xử lý |
| B-14 | **Nonce, Fig. 1, tab-apps:** K-9 dùng subject (người nhận thấy được) trên tài khoản thử có opt-in; sửa Fig. 1(b) và `tab-apps.tex`; thêm cột measured/planned; nhánh G2 của Fig. 1 ghi theo mode khuyến nghị chung. | 15/11 | Không còn mâu thuẫn với §5.2 |
| B-15 | Chạy lại `bench_ledger.py` trên host POSIX mới; viết lại đoạn "laptop running macOS" ở §6 (bản render mới cho `\LedgerFull*` là "--" trên WSL). | 20/11 | §6 khớp số mới |
| B-16 | Làm sạch `testbed/` để đóng gói (không `runtime/`, `runs/`, `*.local.json`, `.env`), qua scrub check của C. | 30/11 | Giao cho C |
| B-17 | (Chỉ khi trưởng nhóm duyệt và B-09 xong trước 22/11) Đo độ trễ Element độc lập; cần thêm kill -9 và netcut vào `run_case.py` và một bộ phân tích ra schema `c2_element_first_visible.csv`. | 28/11 | |

### Phần C: Đánh giá so sánh và câu chuyện của bài

**Sở hữu:** `artifact/run_all.py`, `artifact/run_all.sh`, `artifact/scripts/render.py`, phần Table 4 của `render_real.py` (macro `\Rsim*`, `tab_realsim.tex`); trong `planner_sim.py` phần chính sách, baseline và part (`resolve_rules`, `resolve_baseline`, `vetting`, `run`, `summarize`, định nghĩa part và tag không thuộc A); `manuscript/generated/macros.tex`; `manuscript/main.tex`, `references.bib`; section 00, 01, 07-evaluation (khung chung và phần mô phỏng), 08, 09, 10, `tab-position.tex`; `others/notes.md`; `manuscript/build.sh`. Tiền tố macro: `\Sim*`, `\Rsim*` và các tiền tố cũ khác.

| ID | Việc | Hạn | Xong khi |
|---|---|---|---|
| C-01 | **Bước nối tiếp duy nhất.** Chạy lại toàn bộ (`run_all.py`), diff với CSV và macro đang commit, promote. Tách macro thành ba file (`macros.tex`, `macros_guarantee.tex`, `macros_real.tex`), `main.tex` input cả ba. Lưu ý: lần build đầu đổi khoảng 54 macro, 11 trong thân bài (`\SimSrcAsk`, `\Ledger*`...). Sinh lại `others/notes.md`. | 12/11 | PR có manifest; build xanh; báo A và B danh sách macro đổi |
| C-02 | **Quyết định chung, phát trước 11/11:** mode khuyến nghị theo R06 (product khi A2 có cơ sở cấu trúc, joint ở trường hợp còn lại, ASK khi không gì chứng nhận được, app G2 thì không retry); bảng thuật ngữ (G2 trong văn xuôi là "app tự retry idempotent", hop 1 là "Outbox evidence", chọn một trong ask/escalate). | 11/11 | Cả nhóm dùng chung |
| C-03 | **Vetted rules cùng dữ liệu** (R07). Code hiện tại chưa thật sự cùng dữ liệu: vetted lấy max trên n mẫu lag, joint dùng 20.000. Thêm tag cùng ngân sách và báo cả dòng bất lợi (cùng 2k mẫu lag, joint hỏi 100% còn vetted hỏi 5,3% trên Element). Viết lại các câu "rules retry 28,91 đến 65,85%" và bỏ khỏi abstract. | 20/11 | Bảng so sánh công bằng, có ghi rõ nguồn dữ liệu |
| C-04 | **Table 4:** chú thích nói rõ calibration và test cùng phân phối, lỗi phía committed của Element đo được là 0 (0/99, 0/101), nên bảng kiểm tra bộ máy chứng nhận và cái giá bằng số lần hỏi, không kiểm tra lỗi reader trên màn hình thật. Bỏ các con số viết cứng trong caption của renderer ("12,000", "2,000 per class"). | 22/11 | Trả lời R3 điểm yếu 1 |
| C-05 | **Seed variance**: part mới chạy từng seed (khoảng 40 dòng code) cho các dòng chính của Table 2 và 4. | 28/11 | Macro hoặc chú thích mean ± sd |
| C-06 | **Sắp lại §7:** đo emulator, agent (của B), mô phỏng tham số đo, mô phỏng mô hình (cắt còn redo, Thm-4.8-only, always-ask, rules, vetted, product, joint), stress và population một đoạn, cơ chế một đoạn. RQ1 đến RQ2 xuống phụ lục. Table 5 lên §2. Dùng `\StressNover` cạnh "rules over in 3/14". Sửa công thức δ ở dòng 16 của `07-evaluation.tex` theo §4.3 của A. | 22/11 | Khung §7 có chỗ cho đoạn của A và B |
| C-07 | **Related work:** tách câu gộp ba kết quả trong một citation; một câu so sánh cho LIMBO, Agent libOS, VeriGUI; cân nhắc Gray & Reuter 1992, Bailis VLDB 2015 (kiểm nguồn thật trước khi thêm). | 25/11 | Citation đã kiểm |
| C-08 | **Abstract** tối đa 200 từ, tối đa 4 con số, viết bằng macro (macro agent của B để `??` đến khi có số). | 25/11 chốt, 27/11 đăng ký | Đăng ký xong |
| C-09 | Intro (mở bằng câu chuyện K-9), §8 Discussion (giới hạn mới), §10 Conclusion (ba câu bài học, không số). | 29/11 | |
| C-10 | **Lượt đọc cho dễ hiểu** theo checklist 15 điểm ở `review.md` §5: không câu nào quá 45 từ, tối đa 1 dấu chấm phẩy mỗi đoạn, `\para{}` tối đa 15, `\emph{}` tối đa 30. Áp cho cả bài sau khi A và B xong phần mình. | 2/12 | Dán số đếm trước và sau vào PR |
| C-11 | **Artifact ẩn danh:** đóng gói `artifact/` và `testbed/` của B, loại `tmp/`, `codex/`, `review.md`, `resolve.md`, `report.md`, `runtime/`, `.git`; `team/scrub_check.sh`; README tiếng Anh; đoạn availability ở §8 kèm link. | 1/12 | Link mở được từ cửa sổ ẩn danh |
| C-12 | **Chốt và nộp:** lần chạy sạch cuối từ `main` (freeze 1/12); thân bài hết trang 12; 0 lỗi LaTeX và ref; ẩn danh (cả PDF metadata); citation đã kiểm; nộp HotCRP. | 3/12 | Đã nộp |

## 4. Phụ thuộc giữa các phần (đều là phụ thuộc mềm)

| Ai cần | Cần gì | Từ ai | Khi chưa có thì |
|---|---|---|---|
| A, B | Pipeline chạy lại và ba file macro | C (C-01) | A viết lý thuyết, B dựng rig; không bị chặn trong 3 ngày này |
| A | `\LabelTrial*` (thời gian một lượt) | B (B-11) | Viết công thức với macro `??` |
| C | `\Agent*` cho abstract và intro | B (B-10) | Viết câu với macro `??` |
| C | Macro `\Cert*` cho abstract (joint tied 5k, cận tổng hợp) | A (A-09) | Viết câu với macro `??` |
| B | Mode khuyến nghị để ghi nhãn Fig. 1 | C (C-02) | Đã chốt sẵn theo R06 |
| C | Công thức δ cuối cùng cho dòng setup ở §7 | A (A-05) | Sửa một dòng khi A xong |

## 5. Hợp đồng chốt trước 11/11

- **Tên macro**: mỗi phần gửi danh sách tên macro mà phần khác sẽ dùng, kèm nghĩa và định dạng. Ví dụ phía B: `\AgentScheduledN`, `\AgentValidN`, `\AgentResentN`, `\AgentDupN`, `\AgentAskedN`, `\LabelTrialMedS`. Giá trị tạm là `??`.
- **Schema dữ liệu**: `artifact/results/real/params.csv` giữ nguyên (`name,value,provenance`); `artifact/results/real/agent/episodes.csv` theo `CONTRIBUTOR_3.md` §4.
- **Mode khuyến nghị và bảng thuật ngữ**: C phát (C-02).

## 6. Quy tắc làm việc

- **File**: chỉ sửa file mình sở hữu (§3). `planner_sim.py` là file duy nhất có hai chủ: A sở hữu các hàm hiệu chuẩn và chứng nhận, C sở hữu phần còn lại. Cần thêm gì thì thêm hàm hoặc tag mới, không sửa hàm của người kia.
- **Macro**: mỗi phần render vào file macro của mình; không sửa tay `manuscript/generated/*`.
- **Số liệu**: không gõ tay số kết quả vào `.tex`; mỗi số nói rõ loại (đo trên emulator, mô phỏng theo mô hình, mô phỏng với tham số đo, tính chính xác, chạy LLM agent).
- **Không chỉnh kết quả theo ý muốn**: không đổi seed, họ luật hay ngân sách nhãn sau khi thấy kết quả. Dòng bất lợi vẫn vào bài.
- **Dữ liệu thô** trong `artifact/results/real/**` chỉ được thêm.
- **Nhánh và PR**: `a/...`, `b/...`, `c/...`; tiêu đề PR `[A-xx]`, `[B-xx]`, `[C-xx]`; trưởng nhóm merge; rebase lên `main` trước mỗi PR.
- **Họp**: tối Chủ nhật, 30 phút. Việc bị chặn thì báo ngay trên nhóm chat.

## 7. Lịch

| Tuần | A | B | C |
|---|---|---|---|
| 9 đến 15/11 | A-05, A-06, nháp A-01; tên macro (A-09) | B-01 đến B-05, B-14 | C-01 (xong 12/11), C-02 (11/11) |
| 16 đến 22/11 | A-01 đến A-04, A-07 | B-06 đến B-09, B-13, B-15 | C-03, C-04, C-06 |
| 23 đến 29/11 | A-08, hoàn thiện App. A | B-09 xong 24/11, B-10 đến B-12 | C-07, C-08 (đăng ký 27/11), C-05, C-09 |
| 30/11 đến 4/12 | Trả lời câu hỏi của C | B-16 | C-10, C-11, C-12 (freeze 1/12, nộp 3/12) |

**Báo ngay cho trưởng nhóm nếu:** emulator chưa chạy ổn trước 13/11; chưa có model trước 14/11; A-dev dưới 6/10 vào 19/11; chưa đủ 10 episode hợp lệ vào 23/11; build đỏ quá một ngày.

## 8. Điều chỉnh so với các brief cũ

| Task cũ | Thực tế khi đối chiếu code | Xử lý |
|---|---|---|
| C2-07 (thêm q1/q0) | Cột `n1, n0, ask1, ask0, q1, q0` đã có trong mọi CSV planner | Gộp vào A-04, chỉ còn tính và render |
| C2-08 (δ theo lớp) | `calibration_deltas` đã chia theo số lớp, có test | A-05 chỉ còn sửa `min(α, β)` và viết rõ |
| C2-15 (đếm stress) | Macro `\StressNover` đã có | C dùng ngay (C-06) |
| C2-09(a) (forwarder trả cây cũ) | Log nằm ở `shared-android/logs`, không có trong repo | B-13 chỉ nêu định tính |
| C2-06 (vetted cùng dữ liệu) | Chưa thật sự cùng dữ liệu (n mẫu lag so với 20.000) | C-03 làm lại và báo cả dòng bất lợi |
| C3-06 (`agent_episode.py` mới) | `testbed/native_episode.py` đã có, chưa được nhắc trong README | B-06 mở rộng file có sẵn |
| C3 phương án API | `local_model.py` chỉ nhận endpoint loopback | B-05 cần binding mới và trưởng nhóm duyệt |

## 9. Cần trưởng nhóm quyết

1. Duyệt cách chia này và giao người cho A, B, C.
2. Xác nhận nhóm **được sửa paper**: `resolve.md` và `report.md` còn ghi quyết định cũ "không chỉnh paper, paper để sau".
3. Đường model cho B: máy GPU Linux hay API (kèm ngân sách).
4. Mode khuyến nghị cuối cùng (mặc định theo `resolve.md` R06).
