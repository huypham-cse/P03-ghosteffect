# Quyết định xử lý review và hướng thí nghiệm GhostEffect

> **Ghi chú (09/11/2026):** đợt nộp này làm theo phạm vi và lịch trong `team/PHAN_CHIA_CONG_VIEC.md`; các phần về H100, P40 và C-guard bên dưới không áp dụng. Các file được dẫn tới `report.md`, `codex/plan.md`, `codex/checklist.md`, `codex/review-loop.md`, `codex/study-matrix.md`, `codex/paper-alignment.md` và `codex/structure.md` đã bị xóa khỏi repo; cần thì xem lịch sử git.

## Material Passport

- Quyết định mới v9 của người dùng: **không chỉnh paper, paper để sau; số draft chỉ minh họa, kết quả thực chạy là nguồn chuẩn**. Không còn blocker ASK47.35% hoặc yêu cầu khớp archive. Lượt publish generatedTeX/PDF đã khôi phục21files; chỉ giữ code/plan/report và CSV thí nghiệm. Không ghi vào `manuscript/` tiếp. Các status lịch sử bên dưới không ghi đè quyết định này; không ép hypotheses đạt.
- V7 đang tiếp tục implementation theo yêu cầu mới: [resolve-progress](codex/resolve-progress.md) ghi vòng19–22, code/paper checks, pinned APK/backend integration và remaining scope. Pro Expense identity đã xác minh từ AndroidWorld pin; historical source/output mismatch vẫn chưa giải thích. Không đổi core/hypotheses hoặc đóng goal bằng component smoke.
- Vòng23–24:58component tests/host PASS, per-class clocks/Monitor/effect binding/dispatch guards đã sửa; SDK/AVD WindowsWHPX/API33r17 thực và4stack apps startupPASS;10APKs signature/manifest verified. ProExpense binary đã có; model/agent/calibration và task readiness còn phải kiểm. Người dùng chưa có serverSSH, tiếp tục local.

- Chế độ hiện tại: review v6 + core code fixes/testbed reconstruction được người dùng cho phép; [evidence và phần chưa đóng](codex/code-fixes.md). Chưa có fresh Android/agent/calibration campaign.
- Ngày đối chiếu: 2026-11-08, h100-plan-v6; repo gốc `c3323582e59c6cfaa7df9bb6516a5c0cada3c2d8`, kèm thay đổi đang có trong workspace.
- Đầu vào đã đọc: toàn bộ `review.md` hiện tại, `STATUS.md`, `report.md`, các phần model/theory/design/implementation/evaluation/real, runner, code liên quan và CSV/log hiện có.
- Trạng thái: model/server/task matrix giữ v6; đã sửa numerical/ledger/runner/render/build, chạy isolated artifact và dựng protocol rig mới. GreenMail JAR đúng historical hash có download/integration receipt; chưa model/APK/AVD setup.
- Manuscript text/PDF và archived raw/CSV được giữ; source code được sửa theo ủy quyền mới. Các đoạn review-only cũ dưới đây có thời điểm trước implementation, ưu tiên status mới ở code-fixes/report.

## 1. Tôi chốt hướng nào?

Giữ nguyên đóng góp trung tâm của draft: **pre-tap nonce/digest +ledger ngoài agent → qualified hop-1/Monitor → chờ ở đường cần end-to-end absence → nonce/digest/VLM cascade → quyết định có ngân sách → ASK/PENDING khi chưa đủ thông tin**. Giữ characterization K-9/Element/CalDAV, lý thuyết và simulator. Hoàn thiện host topology với thí nghiệm native nhỏ đúng meta-review trước, protected integration20 cases sau technical gates; C-native5 agents/40tasks theo paper registry P01–P40; T01–T40 chỉ scoped prototype. C-guard200+12vetted cases chỉ sau scientificgate. V5 khôi phục planned-device target: P40 trên toàn app catalogue và GhostEffect end-to-end/H4 là required roadmap. T40/ba measured stacks chỉ prototype/review-core; phone/full saga runtime vẫn extension. Giới hạn một H100 80GB, 250GB RAM; scope ở [plan](codex/plan.md) thay v2.

Ứng viên chính vẫn là **joint certification** vì các reader đo trên Element cùng dùng một lịch sử hiển thị. Product là nhánh so sánh và chỉ là lựa chọn triển khai khi có cơ sở cấu trúc cho A2. Source mode vẫn cần độc lập giữa các nguồn còn tách biệt. **Vetted rules, G2-only và always-ask là đối chứng bắt buộc**, không bị làm yếu để joint thắng.

Cách có lợi nhất cho paper là sửa các lỗi khiến kết quả mất hiệu lực, tận dụng các sensitivity đã có và tìm phạm vi joint thực sự hữu ích bằng một pilot có kiểm soát. Không hứa trước joint sẽ ít hỏi hơn rules trên Element: artifact hiện có cho thấy điều ngược lại trong một số cấu hình. Kết quả ngang nhau vẫn giúp xác định đúng đóng góp về bảo đảm có điều kiện và characterization.

Quy ước vận hành đã chốt:

| Mục | Quyết định mặc định |
|---|---|
| Phạm vi chính | Một H100 + Android13/API33 AVD; A/B dùng ba measured stacks, P40 final phủ catalogue của draft; K-9 A/B GreenMail, P-final Postfix/IMAP; không full factorial |
| Models/agents | M3A20 native+20 protected và 10 nofault trước; C giữ 5 frameworks/40 tasks. Qwen7/UI-TARS1.5-7B/GUI-Owl7 BF16 theo [models](codex/models.md) |
| Bằng chứng controller | Giữ hop-1/nonce/digest và VLM family; historical measured profiles VLM-off; B0 đo verifier độc lập, C-native không có recovery verifier. A-guard/C-guard dùng VLM theo actual certificate/skip contract; agentvision khác verifier evidence |
| Mode chính | Joint, fault-injected, keyed theo lớp quan sát được, cấu hình frozen; không đủ chứng nhận thì ASK/PENDING |
| Budget | `alpha=beta=0.01` cho single-effect; chia `alpha: 0.5 test / 0.4 lag / 0.1 cal`, `beta: 0.9 test / 0.1 cal` như draft |
| Clock | Giữ t0=ISSUED; corrected wait deadline=t0+downtime+w_recovery (tương đương r_e+w). Đo cả issue-to-visible và recovery-to-visible; historical law giữ riêng |
| Nonce | Giữ `gx:` + 6 Crockford base 32, reuse cùng effect; K-9 subject chỉ trong test account có opt-in như campaign cũ |
| K-9 ambiguous | Không tự resend chỉ vì Outbox báo failed hoặc Sent không có thư; ASK khi chưa phân biệt được committed/absent |
| User | Primary historical giữ 5% error/10% look-alike, delay60s; live ASK ghi escalation/unresolved; oracle/synthetic-user sensitivity riêng. Không gọi simulated user là live human study |
| Setup | L00–L09, HF qua .env, tối đa 1 H100 80GB,2 services resident,1→2→4 AVD theo E18; setup chưa chạy |

## 2. Quyết định cho từng nhóm vấn đề

### R01 — Giữ paper nhưng phân biệt mức hoàn thành

**Nguồn:** R1-W1/W2, R3-W1, R4-W1/W3, meta-review.

**Chốt:** draft có khối lượng mô phỏng đáng kể và 149 app trials C2, chưa có agent/control runtime hoàn chỉnh trong checkout. Dùng chúng làm baseline lịch sử; bổ sung host wrapper và agent pilot là bước phát triển gần draft nhất. Không gọi 149 app trials là 149 agent runs. Review nói rig đã có ở nơi khác; checkout này không có `shared-android`, nên thời gian setup chưa thể mặc định chỉ vài giờ.

**Phương án dự phòng:** nếu rig gốc không phục hồi được, dựng rig theo protocol cũ và ghi rõ independent reimplementation. Nếu không đủ dữ liệu để chứng nhận 1% thì giữ validation ở mức characterization, không đổi tên pilot thành certification. **Đóng bằng:** E00/E19/E20.

### R02 — Tách server commitment khỏi GUI visibility

**Nguồn:** mô hình `X=1{T<infinity}` xung đột với K-9 đã commit nhưng không hiển thị; phát hiện bổ sung trong report.

**Chốt bảo toàn model của draft:** giữ `X_paper=1{T<infinity}` và các theorem trong domain eventual visibility vốn có. Grader thực phải ghi thêm `X_backend` độc lập; committed-but-unobservable là challenge **ngoài domain đồng nhất X/visibility**. Không đổi toàn bộ theorem thành một bảo đảm mới chỉ bằng thay ký hiệu X trong plan.

Với runtime thực, decision dựa trên backend-commit semantics chỉ được gắn guarantee khi adapter/proof E09 bao phủ never-visible mass; nếu không thì ASK/PENDING và ghi outside-domain. Ghi `T_vis` và right-censoring độc lập server receipt. Pending không phải absent; finite horizon không chứng minh vô hạn. Đây là correction semantics tối thiểu cần công bố sau results, không viết lại paper trong lượt này. **Đóng bằng:** E09/E11/E13.

### R03 — Sửa clock bằng recovery origin theo lớp

**Nguồn:** R1-W5, R2-W2, meta bắt buộc 1.

**Chốt correction tối thiểu:** giữ `t0=ISSUED` của draft; ghi `d_e=r_e-t0`, dùng deadline `t0+d_e+w_c=r_e+w_c` khi bảng hiệu chuẩn là recovery-to-visible. Đây là cộng downtime vào cùng wait path, không đổi thứ tự/nhánh Algorithm 1. Chọn mốc quan sát được `r_e` theo protocol trước khi đọc verdict: agent-only chết nhưng app/network không đổi dùng ISSUED; app chết dùng relaunch intent có xác nhận; network cut dùng restore; combined dùng mốc cuối cùng đáp ứng cả relaunch và restore. Định nghĩa `T_c=max(0,t_visible-r_e)` và `G_c(w)=P(T_c>w|X=1,c)`. Không lấy downtime trước `r_e` trừ vào wait. Read dùng để kết luận absent chỉ sau `r_e+w`; không biết origin/class hoặc có fault mới thì dùng fallback bảo thủ hoặc ASK.

Biến đổi cần rà chứng minh: với hop-1 đủ điều kiện và độc lập với `T_c` sau conditioning, `P(retry|X=1,c) <= B_c(tau)+q_h,c G_c(w1)+G_c(w0)+K_total*delta`. Không có hop-1 dùng `B_c(tau)+G_c(w0)+K_total*delta`. Mỗi term phải dùng cùng origin và cùng population. Không chứng minh được độc lập hop-1/lag thì **bỏ relaxed wait**, dùng một unconditional wait cho mọi nhánh với toàn bộ lag share; joint không tự chứng minh độc lập giữa hop-1 và lag.

**Cách B:** hiệu chuẩn trực tiếp ISSUED-to-visible gồm toàn bộ downtime, keyed thêm điều kiện recovery. Hợp lệ nhưng thu dữ liệu tốn hơn, dễ drift; chỉ làm ablation. **Không chọn:** dùng bảng relaunch nhưng chờ từ ISSUED. CSV hiện có cho sai lệch 5 s: product/joint `P_v=18.82/29.93%`; 15 s: ` 43.77/46.42%`; correct-origin dòng có `P_v=0` trong simulation tương ứng, không phải bằng chứng thực tế. **Đóng bằng:** E03/E10/E20.

### R04 — Tính đủ unique labels, pilot, holdout và lag

**Nguồn:** R1-D3, R2-W3/D2, R3-W3/W4, meta bắt buộc 2.

**Chốt:** ghi bốn số riêng: nguồn đo thực duy nhất, verdict labels sinh/đo, pilot/holdout, lag entries sinh/đo. `N_LAG=20000` hiện là bootstrap/model draws; 5.000 verdict effects hiện gồm 500 pilot và 4.500 joint holdout. Không ghi 5.000 holdout nếu chưa thu thêm pilot. Lag và verdict có thể dùng chung committed effect khi thiết kế suy luận cho phép; không bắt tách đôi vô ích, nhưng phải kê overlap bằng effect IDs.

Historical simulation giữ **đúng** 2k/5k verdict và 20k lag của từng tag; không đổi primary result trước tái lập. Tied-budget2k/5k là analysis bắt buộc để trả review;10k/20k chỉ giữ existing sensitivity tags, không yêu cầu grid hoặc real corpus mới. Không bỏ historical untied arm. `lag5k` hiện product hỏi 60.29%, joint 30.60%; `lag2k` cả hai 100%. Headline 12.7% chỉ giữ như kết quả historical configuration có đủ provenance, chưa dùng làm acceptance threshold.

Empirical B0=320 effects,4 configs×2 outcomes×40, split10 dev/30 eval mỗi group=80/240. Đây là characterization, không runtime certificate. CERT-1 là recipe tùy chọn500pilot+5000holdout/outcome=11000effects cho một stratum, không tắt requirement calibration coverage của C-guard. V6 yêu cầu E09 tính actual K_total/budgets/censoring và fixed n trước collection; 5000 không luôn đủ. Ví dụ targetlag.002/K55 cần5453zero-exceedance samples; K55 chưa là K thực. Không full-factorial quota, bootstrap thành iid hoặc collect-until-pass. **Đóng bằng:** E04/E08/E09/E18.

### R05 — Joint không miễn nhiễm unseen tails

**Nguồn:** R2-W4, meta bắt buộc 3.

**Chốt:** giữ tail stress và báo cả failures. Tái lập existing2k/5k logged/unlogged; bổ sung đúng 2.9225% ở5k theo meta-review. Các tail masses khác chỉ trong existing tags/targeted sanity, không full Cartesian sweep. 2.9225% là pooled upper bound từ 0/101 trong một thiết kế cụ thể; không phải tail đo được hay cận riêng mỗi class.

Biện pháp triển khai sát draft: giữ `Wmax=120s`, unknown-tail/never-visible không đủ chứng nhận thì hỏi; lấy lag độc lập, ghi right-censoring và kiểm tra shift. Nếu upper bound phần không quan sát đã lớn hơn lag budget thì không thể tạo finite wait hợp lệ chỉ bằng suy diễn. Thu thêm dữ liệu hoặc giảm autonomy; không cắt tail để lấy ask đẹp. `tail5` hiện joint `P_v=2.012%`, CP 2.317%, ask 13.73%. **Đóng bằng:** E05/E10/E11/E29.

### R06 — Một hệ thống, mode lựa chọn theo điều kiện

**Nguồn:** R4-W2/W4, R1-D6, meta bắt buộc 6.

**Chốt:** joint là primary candidate; product chỉ khi A2 có cơ sở cấu trúc, source khi độc lập giữa các source còn tách biệt có cơ sở. Trên measured Element cùng timeline, không mặc định product deployable vì 0 co-failure. G2 monitoring và ASK là các nhánh của cùng controller, không phải thay toàn bộ phương pháp bằng luật.

Cách giảm ask hợp lệ để thử trên development: tăng unique labels trong budget; cải thiện freshness/navigation để giảm BOT; tận dụng qualified hop-1; shared verdict/lag corpus; đọc committed sớm **chỉ ở một ablation được calibration/proof bao quát**, có beta accounting cho mọi look. Cấu hình baseline giữ đúng draft trước. Không chọn mode sau khi nhìn final test. **Đóng bằng:** E04/E06/E14/E20.

### R07 — Equal-data comparison, không overbuild live baselines

**Nguồn:** meta bắt buộc4, current simulator có policy-specific RNG.

**Chốt:** giữ full historical catalog/reproduction trước corrections. Source chia shared worlds nhưng prng riêng theo policy index; paired-world analysis cần units/splits và dependence assumptions đúng; không tự coi McNemar invalid vì policy-specific noise. Không gọi đó là identical noisy observations. Ghi đúng coupling, không tự sửa generator/law/McNemar chỉ vì noise khác. Common-noise sensitivity optional nếu cần; không xâyimagebank vô hạn hoặcép livecounterfactual.

M0 native/M8joint vẫn trong spec; mainC-native chỉ native400, A-guard20integration. M1always-ask analytic/reference, M2–M7 simulation/replay; C-guard nếu qualify thêm 200 protected+12M5vettedcases, không 84extra/7policies. Equal-data rule dùng cùng raw development và calibration labels/lag information mà joint dùng, kể cả CERT-1 khi bật; freeze trước independent eval, không chỉ80dev choM5và11kchojoint; không tune từ B0 eval. Replay không hợpschedule thì chỉ simulation, không gọi làlive.

Nếuparity, ASK-only hoặcjoint không certify, báo đúng và cost, không épbaseline thua. **Đóng bằng:** E06/E07/E14/E20, evidence type/scope rõ.

### R08 — Native trước, paired outcomes và protected gate

**Nguồn:** review yêu cầu ≥10actual interrupted K-9sends/một agent; draft§7.8 nêu5 agents/40 tasks.

**Chốt:** A-dev=10 nofault dev,A-native=20 native scheduled K-9committed/lost-ACK targets(10Sent/10no-Sent), A-guard=20protectedintegration sau ledger/clock gates. Native không đợi controllerhoànchỉnh hoặc4adapters. Requirement review chỉ đóngkhi≥10validfault/actualcommitted cases, không chỉ 20run IDs. Native memory/restart giữ framework behavior, không hinttruth/resend/chèncheckpointpolicy mới.

C-native400=5×40×(nativeinterrupted+native nofault),40 tasks gồm20X1/I3 và20X0/I2 targets; T5/class/outcome, P6/6/4/4 vì local apps chỉ applicable kill faults. Actualtruth/fate quyết định denominator. Đây làbalanced benchmark, không ước lượngnatural outcome prior. Reasoningfailures không loạiqua nofault score hoặcrerun.

C-guard200 protected+12vetted startup OFF tới khi setup/calibration coverage/controls freeze. Đây là required paper stage; missing data phải có acquisition plan, không borrowbootstrap/B0eval. Unsupported→ASK giữ denominator; valid data nhưng ASK-heavy là negative result, không chỉ enable positive region. Native-only chưa hoàn tất full paper study. **Đóng bằng:** E19/E20, [matrix](codex/study-matrix.md).

### R09 — Hoàn thiện host runtime trước foreground service

**Nguồn:** R1-W2, R4-W3, architecture.

**Chốt:** kế hoạch build sau này gồm action interceptor, stable effect ID, durable ledger, nonce/digest snapshot, GUI reader, origin recorder, calibration loader, planner dispatch, ASK/PENDING resume và foreground recheck. Giữ agent unmodified ở policy; wrapper giữ interface action/observation. Backend grader nằm ngoài đường quyết định.

Recompose/retry của cùng workflow-step phải nối về original effect/attempt và reuse nonce; không tự cấp effect ID mới để vượt outstanding/COMMITTED guard. Structured plan dùng step ID; free-form intent attribution chưa chắc chắn thì ASK/PENDING thay vì đoán đó là effect mới. Hai task người dùng cố ý yêu cầu cùng content vẫn có identity riêng. E02/E20 phải có cả hai controls.

Ledger hiện `INSERT OR REPLACE` có thể reset COMMITTED; issue missing ID không fail; settle/candidates chưa đủ state recovery. Phải có transition guards, insert idempotence, serialization, attempts ledger và restart reconciliation. Một crash sau durable issue nhưng trước tap phải để trạng thái ambiguous; không tự giả rằng tap đã/không xảy ra. **Đóng bằng:** E02/E20/E21/E22. On-device service là extension riêng E24, không báo đã built.

### R10 — Báo lỗi tổng hợp đúng mẫu số

**Nguồn:** R2-W1, meta bắt buộc 9.

**Chốt:** báo `P_v`, `L_v`, `q1=P(ask|X=1)`, `q0=P(ask|X=0)`, lỗi final duplicate/loss, unresolved và completion. Với một effect, khi mọi nguồn lỗi bổ sung đã tách, `P(dup|X=1) <= min(1,alpha+q1*e1+r1)` và `P(loss|X=0) <= min(1,beta+q0*e0+r0)`. `r1/r0` bao gồm app/dispatch/classifier/retry failure ngoài contract; không mặc định bằng 0 trong end-to-end.

Chuyển sang vô điều kiện dùng prior `pi`: phần do duplicate khi original committed nhân `pi`; loss khi original absent nhân ` 1-pi`; còn các đường outcome khác phải cộng riêng. Không dùng overall workflow ask thay cho `q1/q0`; zero outcome denominator phải N/A, không max(1,n) để inrate0. Multi-effect cần per-effect budget và union bound; reporting clustered theo workflow.

CSV hiện thiếu conditional asks để tính composed bound đúng cho Table 4; con số `0.05*72.9%` chỉ là minh họa, không phải tính xong cận. Thu event-level outputs rồi tính. Oracle-user ablation cô lập controller; user-error sensitivity báo riêng. **Đóng bằng:** E08/E20/E28/E30.

### R11 — Không sửa nhầm delta theo class; sửa asymmetric budget

**Nguồn:** R2-W6, meta rất nên làm; đối chiếu `planner_sim.py:1465–1471`, ` 04-theory.tex:118–127`.

**Chốt:** phản biện “chưa chia số lớp” không còn đúng với code hiện tại: `keyed='all'` đã chia thêm `len(CLASSES)`, theory nói K nhân số lớp. Giữ cơ chế này và thêm trace budget để trình bày rõ. Known class dùng bound của class; unknown product dùng maxima, unknown joint dùng intersection các vùng. Sai class không tương đương unknown class và phải test riêng.

Lỗi thật cần sửa trong bước implementation sau: code lấy `alpha/(10*K)`, theory lấy `min(alpha,beta)/(10*K)`. Hiện alpha=beta nên không đổi các dòng đó; test beta<alpha để tránh vượt loss-calibration budget. K phải đếm đúng bound/action/region thực sự dùng, không copy 11/8/5 khi thêm early read, handover hay version selection. **Đóng bằng:** E07/E09.

### R12 — Handover/Monitor phải nằm trong stopping-region contract

**Nguồn:** R2-W5/D3, Algorithm 1.

**Chốt:** mỗi epoch chỉ handover một lần từ hop-1 sang end-to-end, reset score một lần; union stopping region bao gồm các cấu hình có/không hop-1 và VLM skip. Lịch sử audit vẫn giữ nguyên, không xóa evidence mâu thuẫn. Failed/stuck UI không phải proof original không thể commit. Pending chuyển nhánh vẫn không được retry nếu original còn có thể apply mà chưa được bound bao phủ.

Đo false-terminal Monitor, late commit, dedup-horizon gần hết, controller crash/resume. Không re-use ngầm beta/risk cho vô hạn terminal looks. Khi contract chưa bao quát thì ASK/PENDING. **Đóng bằng:** E02/E09/E20/E28.

### R13 — Ghi rõ assumptions của lý thuyết và đọc lại

**Nguồn:** R2-W7/D6, R3-D3.

**Chốt:** tách cổ điển i.i.d. view + lag/read independence của Thm 4.1(c, d) khỏi general runtime. Joint bỏ A2 giữa families, vẫn cần matching calibration population và protocol reads/stopping. Repeated poll không được tính thành independent label. Zero co-failure không xác nhận A2. Giữ fixed-sequence joint với pilot tách holdout; không cáo buộc adaptive-threshold invalid khi thứ tự vùng đã cố định đúng thiết kế.

CertifiedWait hiện chọn exceedance count theo `(n,delta,budget)` rồi lấy order statistic; không cần sửa thành Bonferroni theo mọi threshold chỉ vì chọn wait từ sample. Cần kiểm tra i.i.d./censoring/measurement clock thực, không sửa nhầm thủ tục tolerance-bound. **Đóng bằng:** E09/E14/E15.

### R14 — Nonce: giữ cơ chế, chốt visible opt-in và attribution

**Nguồn:** R1-W4, meta bắt buộc 7.

**Chốt:** default private-only như design. Historical/A/B K-9 giữ subject `gx:...` để bám campaign và ghi visible opt-in; P17–P20 final chọn mail body theo app table của draft, nếu đã có opt-in. Không có opt-in thì nonce OFF, dùng các families còn admissible hoặc ASK. Subject/body, nonce ON/OFF và backend là configs có provenance/calibration riêng; không áp field của campaign cũ cho final bằng mặc định. Bảng app ghi actual field và candidate field riêng. No-nonce/digest-only/exact-content controls dùng dev fixtures và historical ablations, không thêm cohort lớn; không âm thầm strip tag khỏi grader rồi coi content nguyên vẹn.

Nonce giúp nhận dạng, không phải idempotency key server. Retry cùng nonce nhưng có thể là request mới. Match cần đúng account/recipient/room, outgoing status và thời gian. Digest tăng count có thể do concurrent send, reorder/edit/delete; thiếu snapshot/attribution mơ hồ phải BOT. **Đóng bằng:** E14/E26.

### R15 — Cost/attempt budget và data có mục đích

**Nguồn:** reviewer đòi measuredfull-cycle/cost5k, không đòimasscollection.

**Chốt:** defaultA50+B320+108 targets+C-native400=878scheduled attempts. Max1instrumentationretry/case, globalcap88extra, max966 attempts; scientific/model failures không rerun. C-guardOFF thêm 212scheduled nếu enable, vẫn globalretrycap88→max1178 không CERT-1. Counts làmixed execution units, không iidn.

E18 dùng 80B0 dev, load1/2/4chia 20/20/40, cộngactualrequestcost từ A-dev/devadapters; freeze rồi mới eval240. Khôngp95precision từ nít, không benchmarkH100 bằng specpeak. Tảimodels theo stage, nativeA4/A5 không giữ V1 dư trên GPU; offlineexact-inputVLMcache không tăng n.

40keffects/app hoặc CERT-1 11k là cost scenarios/candidate recipe, không default quota và không bảo đảm đủ coverage. Protected study vẫn phải có calibration acquisition/coverage plan; không chờ bật recipe CERT-1 mới xem requirement này. Scripted/agentstates khác thì không transfercertificate. Khôngrútlatefollowuphoặcbudget1%cho sốđẹp. **Đóng bằng:** E18/E04 và attempt/costledger.

### R16 — ANR/missingness và censoring

**Nguồn:** R1-D4, R3-W7/D4, missing attempts trong SUMMARY.

**Chốt:** lập attempted-trial ledger trước thao tác, giữ ANR/arm-miss/respawn/discard. Khôi phục 7 lost Element attempts và 4 C1 discards nếu có log; unknown vẫn unknown. Review yêu cầu gán ANR đã commit thành censored là hợp lý khi biết commit và không thấy visibility trong follow-up, nhưng không tự gán commit cho attempt chưa có truth.

First-visible đã thấy rồi thì dừng sau đó không làm endpoint đó bị censored. Tuy nhiên C2 không theo dõi mọi trial đủ 120 s/300 s; late duplicates cần horizon riêng. Report completed subset, intention-to-run và best/worst-case bounds. **Đóng bằng:** E00/E10/E17.

### R17 — GUI-only, BOT và stale source

**Nguồn:** R1-D2, R3-D6, architecture/security.

**Chốt:** probe đọc GUI Outbox, không đọc database app khác. Server/DB chỉ dành calibration/injector/grader. Package/activity/window/account/room/timeline/anchor/freshness không xác minh được → BOT. Thử re-navigation một lần có cost và fresh view identity; không spam reread để coi như thêm độc lập.

Đưa stale-forwarder và stale-digest pilot vào failure corpus có provenance; count historical events theo log, không tạo mẫu số mới. Giữ co-failure/BOT riêng. **Đóng bằng:** E14/E20/E21/E26.

### R18 — Đo đúng outstanding request, không nhầm retry-ACK-before-fault

**Nguồn:** R1-D5, R3-W7, C2 mechanism.

**Chốt:** barrier đặt sau backend commit và trước client nhận ACK; fault có receipt riêng. Tách clean response-drop, sticky response-drop và withheld timeout. Mỗi trial reset queue/backend để không carry-over. `/sync` reconciliation trước client ACK là evidence end-to-end; không biến Element indicator thành lag-free hop-1.

Giữ 60 standard cells như đã đo; không đổi mô tả thành crash trước retry ACK. Thêm causal cells theo E12. **Đóng bằng:** E10/E12/E17.

### R19 — K-9 action audit và thay lag giả định bằng phép đo

**Nguồn:** R3-W2, conflict `sendmsgs_tapped=0` của 12 no-Sent lost-reply trials.

**Chốt:** không khẳng định toàn bộ 20 trials đều explicit Send-messages khi 12 no-Sent chưa có tap evidence. Chạy action audit có UI receipt, tách Sync/Send messages/no action/recompose. Đo unattended queued delivery ≥20 phút với terminal follow-up; không gọi temporarily queued là absent. `U(45,900)` chỉ là assumed-law sensitivity cho đến khi có survival data thật.

Giữ 20/20 scripted GUI-redo duplicate là observation đúng phạm vi; không suy ra tỷ lệ LLM resend. Precision 28.91–65.85% thuộc simulation, không measured mail-dup probability. **Đóng bằng:** E13/E19.

### R20 — Android faults và foreground service

**Nguồn:** R1-W2/W6/D1, R3-W7, meta nice-to-have.

**Chốt:** agent process death, controller death, app `kill -9`, force-stop và network là events khác nhau. Ghi PID trước/sau, process exit và restart. `am kill` không làm app chết thì ghi NOOP, không relabel LMK. LMK cần memory-pressure trace; Doze/App Standby phải chứng minh state đã vào và đã thoát theo [Android Developers](https://developer.android.com/training/monitoring-device-state/doze-standby#testing_doze_and_app_standby).

Đợt chính là host topology; phone/foreground-service overhead là extension sau E20. Nếu giữ claim on-device thì E24/E25 trở thành bắt buộc trước kết luận đó. H3 không mặc định force-stop phá G2, vì Element/DAVx 5 hiện phục hồi. **Đóng core bằng:** E22/E23; E24/E25 chỉ phải thực hiện khi mở phone/power claims.

### R21 — Verifier đo riêng, không thành empirical certificate

**Nguồn:** R1-W7/H2 planned study.

**Chốt:** historicalVLM-off giữ code; V1Qwen7BBF16 đo200selected heldoutB0 effects(100/outcome từ 120/outcome), không 200cohort mới. Tốiđa3availableviewcalls/effect, onecall/view, skiplook-alike/BOT như draft. Sameinputhash cached choofflineanalysis, không cacheliveactions/acrosseffects.

B0 eval không tune thresholds hoặcexportbound; tinyCP/loaderfixtures synthetic được gắn nhãn. C-native không gọi recovery verifier; paired final vẫn giữ V1 resident allocation theo matched topology khi framework cần engine riêng. A-guard safeintegration và C-guardconditional giữ familylogic. V2OFF. Error/correlation CI cóthểinconclusive; không inferA2 từ nonsignificance hoặcsameweights. **Đóng bằng:** E15/E20.

### R22 — G2 có scope và thời hạn; không đồng nhất nonce với key

**Nguồn:** R2-D3/D5, dedup horizon.

**Chốt:** pin app/backend versions, account/device/endpoint/resource; `D_dedup` là ký hiệu đề xuất sau này để tránh lẫn KL `D0/D1`. Same key, same scope, within horizon khác GUI redo tạo key mới. Matrix spec xác định device/endpoint scope, không cam kết mọi server có retention 24 h. [Matrix transaction identifiers](https://spec.matrix.org/latest/client-server-api/#transaction-identifiers).

Historical timestamp aging giữ nhãn intervention; natural ≥24 h sequence là extension bắt buộc nếu nâng thành measured natural retention. Gần horizon và original còn pending thì controller không tự tạo request mới. **Đóng bằng:** E12/E16/E20.

### R23 — Zero-error plug-in và kiểm tra độc lập

**Nguồn:** R3-W1/D1/D4, meta bắt buộc 8.

**Chốt:** Table 4 là fitted-law simulation; 0/99 observed wrong không phải rate thật 0. Giữ plug-in law để tái lập, thêm uncertainty envelope từ effect-level observations và day/load-heldout data. Không tự thay tất cả bằng CP upper rồi coi đó là true app distribution; đó chỉ là conservative sensitivity.

Old C1/C2 đã được xem để dựng hypotheses nên chỉ là discovery/historical. Development mới chọn parser/navigation/parameters, B0 evaluation fresh không dùng để tune hoặc certify. Fresh calibration cho protected domains được thu theo acquisition plan riêng sau E09, với pilot/regions và independent evaluation design đã freeze. CERT-1 chỉ là một candidate recipe, không switch bật/tắt toàn bộ calibration requirement. Bootstrap source effects vẫn đi cùng split gốc. **Đóng bằng:** E08/E10/E11/E14/E20.

### R24 — Pooling/drift: chưa có test thì không gộp tùy ý

**Nguồn:** R3-W4, limitation joint region test.

**Chốt:** primary data keyed app/backend version, device/ABI, locale, reader/model, fault subtype. Pooling cùng stratum chỉ khi protocol và exchangeability có cơ sở. Version mới dùng calibration mới hoặc fall back ASK; không dùng “200 samples không reject drift” để chứng nhận không drift.

Extension so family-rate shift với joint-dependence shift, giữ marginal rates không đổi nhưng đổi cofailures, report detection power/type-II và fail-closed behavior. **Đóng bằng:** E07/E29.

### R25 — Reproducibility, artifact và nguồn tải

**Nguồn:** R3-W8/D7, meta bắt buộc 10.

**Chốt:** phục hồi original rig/APK/environment theo hashes trước; không thay `latest`. Nếu đổi ARM64/macOS sang AMD64/Windows thì gọi portability replication, không byte-identical timing reproduction. Ship nguồn, configs, raw/derived mapping, fixtures test account, manifest; scrub host identifiers ở bản xuất, giữ bản raw private để đối chiếu. Không xóa provenance gốc.

Repo public không tự đồng nghĩa anonymous artifact. Trong lượt này chỉ lên plan package; upload/publication để bước nộp riêng. Không viết link đã tồn tại khi chưa có. Danh mục nguồn tải ở [codex/setup-data.md](codex/setup-data.md). **Đóng bằng:** E00/E01.

### R26 — Statistics, seeds và quantiles

**Nguồn:** R3-D2/D5, meta nice-to-have seed variance.

**Chốt:** outcomes và denominators theo effect/workflow/class; missing/BOT không bị bỏ khỏi bảng chính. Small-n lag báo tất cả điểm + min/median/max, p90 nếu có phải kèm n và method. Với n=20, thứ hạng p90 phụ thuộc quantile convention; không mặc định reviewer nói “điểm lớn thứ hai” là định nghĩa duy nhất.

Primary budgets giữ 1%; observed 0.5% khi nominal alpha=0.1 không được gọi guarantee 0.5%. Existing 5 seeds không thay empirical 5 independent devices. Nested auxiliary simulation E08:3 calibration fits×3 eval seeds trên 3 headline configs, historical5 seeds không đổi; paired workflow/block inference và Holm cho comparisons đã định. Số stress violations tách point estimate vượt budget và upper CI chưa certify, không đếm hai loại như nhau. **Đóng bằng:** E01/E08/E09.

### R27 — Saga/KKT giữ đúng tầng evidence

**Nguồn:** R2-D4, workflow layer.

**Chốt:** giữ simulation/exact union-budget và KKT của draft; uniform là ablation. MainA/B/C thiết kế một effect chính/task để không phải xây saga engine ngoài yêu cầu revision. Full saga/compensation runtime là E28 extension OFF; khi mở vẫn KKT primary, mỗi compensation là effect mới có ledger/budget. Không nói simulation đã verify runtime. **Đóng bằng:** E28 reproduction; runtime claim chỉ sau traces riêng. E33 LP optional.

### R28 — Khôi phục full app coverage theo draft

**Nguồn:** §7.8 nêu40 tasks trên app table, không chỉ ba measured stacks; user yêu cầu càng sát paper càng tốt.

**Chốt:** Paper target dùng P01–P40 cho10app/variant entries, bốn task proposals mỗi entry; allocation là lựa chọn plan, không quota do paper quy định. T01–T40 là prototype/review-core. Không tự chạy cả T400 và P400. Required E31 hoàn thiện package/fixtures/grader/reset, E32 viết MockBank-A/B tối thiểu; cập nhậtv7 đã định danh Pro Expense từ source pin, còn binary/UI phải kiểm, không silent substitute. Local-only apps chỉ applicable persistence/kill faults; coverage P6/6/4/4 mỗi outcome, không fake network fault.

Full coverage và E20/H4 không bị gộp với phone/E2EE/full saga extensions. Có thể chạy A/B trước trong lúc giải quyết dependencies, nhưng chưa được gọi paper device-study đã hoàn tất. **Đóng kế hoạch bằng:** [matrix§8](codex/study-matrix.md#8-p01p40-registry-chính-cho-paper_draft), [paper alignment](codex/paper-alignment.md), E31/E32 và input ownership.

### R29 — Presentation/title/readability xử lý sau results

**Nguồn:** toàn bộ R4-W3–W6/D1–D9 và phần readability, meta khuyến nghị cấu trúc.

**Chốt:** đưa vào backlog, chưa viết lại paper. Sau thí nghiệm: thống nhất mode, provenance mỗi số, giải thích budgeted exactly-once là guarantee có điều kiện, measurement-first evaluation, min/median/max, vocabulary đơn giản; giữ 12-page constraint để bước biên tập sau xử lý. Citation Gray/Reuter/Bailis chỉ optional và phải verify trước thêm. Không xem dấu câu/văn phong là bằng chứng fabrication.

R2 yêu cầu independence assumptions không phải chỉ presentation; đã xử lý ở R13. R4 đề nghị rút theory không có nghĩa bỏ cơ chế certification. **Đóng bằng:** artifacts từ E03–E20; chỉnh manuscript là task tương lai ngoài lượt này.

### R30 — Các lỗi code/runner thật cần sửa trước rerun

**Nguồn:** đối chiếu report với source, bổ sung review.

**Chốt kế hoạch:** sửa `sample_size.n_rate` bằng tìm minimum có chứng minh theo từng interval `ceil(p*n)=k` hoặc exhaustive search hữu hạn đã kiểm reference; không bisection hàm không đơn điệu. Đây là conservative overestimate, không cáo buộc guarantee hiện tại unsafe vì riêng lỗi này. Giữ n_zero, kiểm pilot/holdout và asymmetric delta. Ví dụ audit có `n=193` đã thỏa ô product alpha=.01, p=.01 dù CSV in 221; cần independent regression trước regenerate.

Các lỗi được phát hiện ở review: max(1,n) pseudo-rate, unchecked child exits/REAL4, destructive renderer init và build nuốt lỗi. Chúng đã được sửa theo implementation update dưới đây. `bench_ledger.py` vẫn phải chạy POSIX đúng domain, không đổi Windows termination thành SIGKILL; `saga_het.csv` chưa truy được active generator nên giữ orphan/unverified, không kéo vào claim mới.

**Trạng thái implementation:** minimum search/delta/N/A/guards/isolated runner/REAL4/render rollback/build fail-fast đã sửa và có references/regression/full artifact run. E01 còn archived source/output discrepancy, E02 còn actual Android/agent boundaries, E09 còn full stopping/domain/acquisition K_total; E34 chưa fresh full TeX compile. [Chi tiết](codex/code-fixes.md). Không dùng component PASS để đóng cả experiment.

### R31 — Commit classifier và dispatch security

**Nguồn:** R1-W2, design classifier/foreground check.

**Chốt:** pilot recovery dùng commit points được annotate và trace rõ để tách hiệu quả planner khỏi classifier. Sau đó E21 đánh giá automatic classifier trên locale/label/icon/confirmation khác; report false negatives là unprotected effects, không biến thành success của recovery. Recheck package/activity/window/account ngay trước nonce write, retry, compensation và user prompt; root/backend access chỉ thuộc test apparatus.

**Đóng bằng:** E21/E22; classifier chưa đạt thì không mở claim bảo vệ mọi risky tap tự động.

### R32 — Một H100, fidelity và stopping rules

**Nguồn:** user yêu cầu thêm review loops về performance/scale/overengineering.

**Chốt:** [plan§1](codex/plan.md#1-những-gì-giữ-nguyên-từ-paper) giữ Algorithm1/clock/K_total/alpha-beta1%. V6 giữ full P40/H4 của v5, sửa các chi tiết vận hành, không dùng review-core làm đích thay thế. Bỏ cal-smoke320/live7-arm matrix không cần thiết; chưa gọi optimum khi chưa E18.

Model7BBF16/sourcepins giữ nguyên. TảiQwen trước A,UI-TARS trước A3/A4,GUI-Owl trước A5; engine theo checkpoint, không theo role. AgentProg workflow/executor/V1 share Qwen, locator dùng UI-TARS:2engines, không3. Core chỉ1→2→4AVD, bỏ nhánh8. Native-only dev A4/A5 dùng modelđơn; final paired giữ matched topology. Context32k/upstream image/history/processor-parser giữ nguyên, không silent truncate; OOM giảm workers trước input. Không claim fit/quality chưa đo.

Milestone878 attempts, retrycap88; paper subtotal1090/max1178 trước calibration gồm C-guard200+12sentinels. Startup false flags không bỏ H4/app catalogue. Calibration acquisition/domain/proof và paired controls phải freeze trước final; unknown→ASK, không score-based eligibility. One commit-slot ID thay semantic-intent framework. **Đóng bằng:** E00/E01/E19/E20/E31/E32, S13–S15, L00–L09 và [paper alignment](codex/paper-alignment.md).

## 3. Ma trận bao phủ review

`W` là điểm yếu đánh số; `D` là nhận xét chi tiết đánh số trong review. Câu hỏi của reviewer được trả bằng cùng resolution và outputs thí nghiệm, không cần một thí nghiệm trùng lặp.

| Nhóm review | Resolution bao phủ |
|---|---|
| R1-W1..W7 | R08; R09/R20/R31; R28; R14; R03; R20; R21 |
| R1-D1..D8 | R20; R17; R15; R16; R18/R13; R06; R28; R03/R15/R26 |
| R2-W1..W7 | R10; R03; R04; R05; R12; R11; R13 |
| R2-D1..D6 | R29; R04/R13; R18/R22; R27; R22; R13/R24 |
| R3-W1..W8 | R23; R19/R26; R04; R15; R07; R23/R13; R18/R20; R25 |
| R3-D1..D7 | R23; R26; R13/R17; R23/R16; R26; R17; R25/R30 |
| R4-W1..W6 | R08; R06/R07; R01/R20/R29; R06/R29; R10/R29; R29 |
| R4-D1..D9 | R29 cho toàn bộ; D5 thêm R07; D8 thêm R06/R28 |
| Meta 10 bắt buộc | R03; R04; R05; R07; R08; R06; R14; R23; R10; R25 |
| Meta rất nên làm | R29; R29; R29; R15; R11; R17; R26; R22; R29; R26 |
| Meta nice-to-have | R20; R26; R23/E10; R28/E27; R29 |
| Readability §1–5 | R29, backlog sau results; không bỏ vấn đề kỹ thuật nằm dưới cách diễn đạt |
| Conflict thêm từ audit | R02/R09/R11/R12/R14/R16/R19/R30/R31/R32 |

## 4. Chưa thể tự xác nhận thay tác giả

Models/protocol/quy mô đã chọn; các đầu vào cần xác minh khi triển khai được ghi gate/owner trong review-loop, không giả đã hoàn tất:

1. Vị trí snapshot `shared-android`, AVD/backends/APK gốc và raw screenshots/trees còn giữ. Nếu thiếu thì đánh nhãn reconstruction, không giả vờ exact reproduction.
2. HF snapshot access/token nếu cần, license và receipts từng shard; upstream-reference API access nếu mở arm đó. HF-main7B đã chọn; không có dependency72B hoặc multi-GPU.
3. Server1 H100 80GB/250GB RAM; CPU/KVM/NVMe/Android stratum phải kiểm trước triển khai. Phone chỉ khi mởE24, không dependency core.
4. Original missing-attempt/K-9 tap evidence; nếu không còn, E13/E17 đo lại và historical item vẫn unverified.
5. Fixtures/reset/graders cho P01–P40/toàn catalogue và model-binding patches còn phải implement; ba measured stacks là điểm bắt đầu. V7 đã xác minh Pro Expense source/package/candidateAPK, còn binary và actual UI trước full coverage.

## 5. Tài liệu vận hành

- [Plan và thứ tự triển khai](codex/plan.md).
- [Nguồn tải, setup, preprocessing và split](codex/setup-data.md).
- [Runbook server đầy đủ L00–L09 và Hugging Face qua .env](codex/setup-server.md).
- [Smoke tests, cổng mở campaign và cách thử nhiều phương án](codex/smoke-tests.md).
- [Từng thí nghiệm E00–E34: mục tiêu, quy mô, expected và fallback](codex/experiments.md).
- [Cấu trúc repo hiện tại và cấu trúc dự kiến](codex/structure.md).
- [Checklist trạng thái đã có artifact / chưa tái lập / chưa chạy](codex/checklist.md).

Thêm: [model/checkpoint/inference matrix](codex/models.md), [40 tasks và scoped study matrix](codex/study-matrix.md), [biên bản review nhiều vòng](codex/review-loop.md).

## 6. V5 completion boundary

[Đối chiếu paper](codex/paper-alignment.md) supersede kết luận v4 rằng review-core/native-only đủ cho mục tiêu full draft. E20/H4 và app catalogue là required roadmap; chỉ physical/OEM/power/E2EE/human/full-saga/pooling/LP lớn là extension theo claim. Chưa có execution evidence cho các stages mới; null/inconclusive được giữ và không đổi budget1% hay pipeline để tạo score.

Milestone878 và runtime2–6ngày không bao gồm calibration/extra app implementation. Paper scheduled subtotal1090 chưa có tổng calendar đáng tin cho đến E18/coverage acquisition. Chưa sửa manuscript/code/raw.

## 7. V6: review thêm và các resolve còn mở

Biên bản vòng13–16 ở [review-loop](codex/review-loop.md#vòng-13--đối-chiếu-lại-draft-pdf). Giữ 878/1090, năm frameworks/40 tasks, các E/R/S/L IDs; không thêm pipeline hoặc campaign. A/B mail giữ GreenMail, P17–P20 final chọn Postfix/IMAP như draft, pins chưa có. E31 phải xác minh actual WorkManager outbox/G2 và force-stop slots cho H3; LMK không thay H3. Không eligible case→NOT_TESTED.

E21 classifier freeze trước B0eval, calibration acquisition theo coverage/actual n, role routing hai engines và load1/2/4 được làm rõ. Sau review, R30 core fixes đã được triển khai/kiểm theo ủy quyền mới: minimum193, checked runner cóREAL4, fail-fast build, guardedledger. Giữ E01/E02/E09partial vì còn provenance/live integration/proof-domain, không còn mô tả các bug vừa sửa là vẫn hiện hữu. [Evidence](codex/code-fixes.md).

Inputs cần tác giả/implementer xác minh: Pro Expense binary/capability (source identity đã resolvev7); historical missing raw/source revision cho archived aggregates; Postfix/IMAP và APK capabilities; WorkManager eligibility; server CPU/KVM/SSD/model serving; actual calibration coverage/n/cost. Người dùng xác nhận original rig không còn, đã dựng reconstruction trong `testbed/`; historical provenance không được giả phục hồi. Checkout không có collab bundle nên notebook audit chưa xác minh; không xây framework mới để lấp bundle.
