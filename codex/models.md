# Model và inference cho một H100 — h100-plan-v6

## Material Passport

- Revision2026-11-08, plan only; chưa tải weights/serve/benchmark. Một H100 80GB/250GB RAM.
- Draft nêu framework agents, không chốt backbone/precision/checkpoint. 72B/32B ở v2 là lựa chọn plan tự thêm.
- Chọn official BF167B để không cần tensor-parallel nhiều GPU hoặc quantization. Đây là phương án phù hợp tài nguyên, chưa chứng minh accuracy tối ưu.

## 1. Năm agent và verifier

| ID | Framework giữ theo draft | HF-main | Contract |
|---|---|---|---|
| A1 | M3A | Qwen/Qwen2.5-VL-7B-Instruct | Giữ reflection/history/action space; screenshot+a11y/SoM |
| A2 | T3A | Cùng Qwen7B | Chỉ text/a11y, không gửi ảnh; giữ text-only algorithm |
| A3 | AgentProg | Qwen7B workflow+executor, UI-TARS-1.5-7B locator | Giữ Semantic Task Program/PC/belief/context pruning; binding patch có diff |
| A4 | UI-TARS-1.5 | ByteDance-Seed/UI-TARS-1.5-7B | Official mobile prompt, history/action parser, tọa độ đúng processor |
| A5 | Mobile-Agent-v3 | mPLUG/GUI-Owl-7B | Giữ multi-agent planning/progress/reflection/memory; không gọi single loop GUI-Owl là Mobile-Agent-v3 |
| V1 | GhostEffect verifier | Qwen/Qwen2.5-VL-7B-Instruct | Role riêng present/absent/BOT, không action, không backend truth/reasoning của agent |
| V2 | Sensitivity OFF | GUI-Owl-7B đã tải cho A5 | Chỉ đọc một subset diagnostic củaB, không calibration/live sweep mới |

V1 dùng chung weights không chứng minh independence. Joint whole-effect calibration là candidate; không lấy nhiều replies thành independent labels. B0 chỉ characterization, không tạo empirical certificate; A-guard cóthểASK100%; task competence, verifier error và empirical risk là ba chỉ tiêu khác nhau.

HF-main là **backbone variant**, không tái lập điểm Gemini của M3A/AgentProg. Native/protected dùng cùng prompts/weights/precision/binding patch. Không claim7B ngang72B. Dev S09 phát hiện wiring hoặc competence yếu; sửa wiring trên dev, giữ model errors. Nếu cần đổi model thì revision trước freeze, không âm thầm đổi sau final.

## 2. Source và checkpoint pins

| Source | Commit |
|---|---|
| AndroidWorld | 55ddaf5edc6f6c25673aed343907d5b9dca66f84 |
| AgentProg | ef5e2998ac2defa86e0dc4c13e7e00d595e1e7cf |
| UI-TARS code | 582f3a7ea5d285ee8ed9e2e84048d1ab01453c49 |
| Mobile-Agent code | c4cd0a8f9ddedad24dd8a3daf3a56ca69343849f |

| HF repo | Revision SHA | Source/runtime tensor metadata |
|---|---|---|
| Qwen/Qwen2.5-VL-7B-Instruct | cc594898137f460bfe9f0759e9844b3ce807cfb5 | 8.292B parameters, khoảng 16.6GB tensor bytes |
| ByteDance-Seed/UI-TARS-1.5-7B | 683d002dd99d8f95104d31e70391a39348857f4e | HF API:8.292B F32 parameters (~33.2GB source tensor bytes); runtime cast BF16 (~16.6GB), ghi receipt |
| mPLUG/GUI-Owl-7B | 7c1644c0288da07435a485701d0fea0ac353f38a | 8.297B parameters, khoảng 16.6GB tensor bytes |

Hai SHA7B mới và metadata kiểm qua HF API ngày 2026-11-08; UI-TARS pin giữ từ v2, F32 metadata được kiểm lại. Chưa có shard hashes/download receipts. Các tên7B là official product names; tensor totals có vision components nên không mặc định đúng 7B params.

Official cards: [Qwen7B](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct), [UI-TARS1.5-7B](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B), [GUI-Owl7B](https://huggingface.co/mPLUG/GUI-Owl-7B). Source roles: [AndroidWorld](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/agents/README.md), [AgentProg](https://github.com/MobileLLM/AgentProg/tree/ef5e2998ac2defa86e0dc4c13e7e00d595e1e7cf), [Mobile-Agent-v3](https://github.com/X-PLUG/MobileAgent/tree/c4cd0a8f9ddedad24dd8a3daf3a56ca69343849f/Mobile-Agent-v3).

AgentProg .env/README locator và request hard-code Doubao lệch nhau; core_config dùng Gemini cho workflow/executor. Phải patch endpoint/model binding sang HF-main, pin diff và actual returned model identity. Không chỉ đổi alias rồi giữ upstream call. UI-TARS public7B khác research service; API upstream-reference mặc định OFF, không cần API để chạy plan.

## 3. Single-GPU serving theo stage

- A-native và A-guard: chỉ Qwen7B; role verifier dùng cùng weights nhưng không nhận agent reasoning/truth.
- B0 offline verifier: Qwen, chỉ đọc 200 selected heldout effects, một call/view.
- Native-only development/review_core: A1/A2 Qwen; A3 Qwen+UI-TARS locator; A4 UI-TARS đơn; A5 GUI-Owl đơn. Paper final C0/C-guard dùng matched topology ở mục8; A4/A5 controls giữ allocation của V1 engine dù không gọi recovery verifier.
- C-guard OFF tới readiness; nếu enable, topology theo bảng mục8. A3 dùng chung Qwen engine cho workflow/executor/V1, thêm UI-TARS locator; tối đa hai checkpoint engines. Không tạo engine riêng cho mỗi role.

Mộtservice memory fraction≤.85; hai service starting fractions .45+.45,tổng≤.90. Tensor parallel1, fullBF16. KV/vision/CUDA/runtime peak phải S15 đo; ưu tiên giảm global concurrency/AVD trước khi đổi inputs/dtype. Một H100 chưa được benchmark, không hứadual enginesworstcasefit chỉ từ weights.

Tải theo nhu cầu: Qwen trước A, UI-TARS trước A3/A4, GUI-Owl trước A5. Không bắt chờ tải/harness đầy đủ ba model để chạy 20 native K-9. Pin SHAs giữ như§2; không upgrade giữa cohort.

Bắt đầu1 AVD; E18 đo2/4, chọn load rồifreeze. Global2in-flight requests,max_num_seqs2/service làstarting limits, scheduler giữ states/contexts riêng. Native baseline không chờclassifier/guardedledger mà chỉ cần observation-only tracer và fault/grader receipts.

## 4. Inference fidelity, không giảm input tùy tiện

| Tham số | Primary v6, giữ inference recipe v4/v5 |
|---|---|
| Runtime | vLLM0.11.0 base; pin image/dependencies sau compatibility smoke, Transformers reference khi cần |
| Dtype | Official snapshots, BF16 inference; UI-TARS sourceF32 cast ghi rõ. KhôngGGUF/AWQ/GPTQ |
| Context | 32.768 tổnginput/output; giữ framework context pruning/native history. Overflow log/fail, không âmthầm cắtprogram/PC |
| Decode | temperature0/top_p1, một candidate; ghi common-backbone variant so với upstream stochastic settings |
| Output | action/reflection/executor2048, AgentProg program4096, verifier256; saturation kiểm trên dev trước freeze |
| M3A/Qwen | Screenshot+a11y/SoM và native per-role history; processor từ pinned HF snapshot, không global pixel cap1M |
| T3A | Text/a11y only, zero image tokens, dùng cùng Qwen service |
| UI-TARS | GiữMOBILE_USE/history/action parser từ sourcepin; resolved min/max pixels củaimage processor phải truyền cùng vào coordinate parser, không dùng hai defaults khác nhau |
| GUI-Owl | Pinned multi-agent cookbook; hỗtrợ history đến 5 images với official5-image recipe min_pixels3136/max_pixels3211264 khirole cần; không ép mọi role dùng 5ảnh |
| Admission | MAX_IMAGES_PER_REQUEST=5 làstarting ceiling, không lệnhxóaảnh. Nếu pinned recipe cần hơn thìverify/tăng trước freeze hoặc fail readiness, không silent truncate |
| Verifier | List/detail/search ba calls riêng, mỗi view một lần nếu available; skip/look-alike/BOT đúng paper |
| Requests | Global2inflight và seq2/service banđầu; giảm concurrency trước đụnghistory/resolution;max4 AVD |

V3 dùng cap16k/2ảnh/maxpixel1M cho mọibaseline là một memoryvariant không cần thiết, cóthểthay đổi behavior. V4ưu tiênupstream image/history recipe, giảm workers/batch nếu peakmemory thiếu. Không suy chấtlượng giữ nguyên chỉ vì model cùng SHA; S14 phải kiểm input/tọađộ/history và small-text fixtures.

Nguồn: [GUI-Owl official deployment recipes](https://huggingface.co/mPLUG/GUI-Owl-7B), [UI-TARS source pin](https://github.com/bytedance/UI-TARS/tree/582f3a7ea5d285ee8ed9e2e84048d1ab01453c49), [vLLM0.11 memory controls](https://docs.vllm.ai/en/v0.11.0/configuration/conserving_memory.html). Recipe làspecified input protocol, không evidence đã loadtest trên H100.

### Cache để giảm inference mà không giả dữ liệu

Offline memoization key=(effectID,viewID,screenshotHash,modelSHA,prompt/processorHash,decode). Same tuple chỉ gọiVLM một lần; repeatedanalysis reuseoutput và báo cachehit. Không tăng n, không cachelookup dựa trên truth, không dùng cachedaction củaepisode khác hoặcảnhsaupolicy thay đổi state làmcounterfactual.

HTTP retry không đồng nghĩa retrycommit. Mỗirequest/attempt cóID, actiondispatcher phải guard duplicate. V1sameweights không tạoindependence vớiagent/families; smallB0 không được exportcertificate.

## 5. HF qua .env và freeze

Dùng [.env.example](.env.example) làm template project-root .env, nạp trước importHF. snapshot_download nhận repo_id/SHA/token/local_dir từ config, lưu dưới codex/models; toàn bộ caches dưới project. Không log token/real .env; export allowlist nonsecret config thôi. Xác minh shards/index/tokenizer/processor/license/hash, rồi offline reload; không fallback Inference Provider/API trả phí khi thiếu local file.

Mỗi A/V role freeze source/patch/model SHA, processor/prompt/parser, dtype/image/history/decode, actual returned model ID và load/concurrency. Không gọi setup/model fit là bảo đảm completion hoặc risk. [HF download](https://huggingface.co/docs/huggingface_hub/guides/download), [HF environment](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables).

## 6. Native-only và paired topology

Native-only development chạy model đơn khi không cần V1. Với paper_draft final, native/protected của paired study dùng cùng engine allocation/services để so latency/cost công bằng; không so native .85 single-engine với protected .45+.45 rồi gán toàn bộ chênh lệch cho thuật toán. Đổi singleton→dual topology cần restart với config mới và verify actual allocations trước cohort. Không bật C-guard sau khi đọc native final; config khác cần studyversion/native controls mới. Native-only final chỉ dành cho explicit review_core study, không tự fallback của paper target.

## 7. Paper-target và model completion boundary

V6 giữ nguyên IDs/SHA/dtype/recipes. STUDY_TARGET=paper_draft dùng P01–P40; hf-main7B là backbone variant, không khẳng định upstream published score. Calibration dùng V1 phải đúng model/processor/prompt/domain; agent/framework không có certificate phù hợp→ASK, vẫn giữ trong paper task distribution.

C-guard là required paper stage sau readiness; startup false flag không xóa end-to-end/H4. Full task registry/pins/calibration coverage ở [paper alignment](paper-alignment.md). E18 chỉ xét 1/2/4 AVD trong core; chọn theo throughput và resource gates, không mở load8 ở revision này.

## 8. Topology thực thi v6

| Framework/stage | Checkpoint engines cần resident | Routing |
|---|---|---|
| A1 M3A / A2 T3A, native hoặc protected | Qwen | Agent và V1 gọi cùng engine bằng request/prompt/history riêng; T3A không gửi ảnh |
| A3 AgentProg, native hoặc protected | Qwen + UI-TARS | Qwen phục vụ workflow/executor và V1; UI-TARS chỉ locator. Không tạo engine V1 thứ ba |
| A4 UI-TARS, native-only development | UI-TARS | Không load Qwen idle |
| A4 paired C0/C-guard | UI-TARS + Qwen | Qwen phục vụ V1; native matched control giữ cùng allocation |
| A5 Mobile-Agent-v3, native-only development | GUI-Owl | Các native roles dùng engine theo pinned framework; không đổi thành một single-loop agent |
| A5 paired C0/C-guard | GUI-Owl + Qwen | Qwen phục vụ V1; native matched control giữ cùng allocation |
| B0/E15 offline verifier | Qwen | Không cần agent engine; không phát sinh live action |

Memory fractions: singleton .85; dual .45+.45 là starting allocations, phải đo S15 cho đúng profile. A1/A2 không load hai bản Qwen giống hệt nhau chỉ để tách role. Chỉ share model engine, không share agent reasoning/state/truth với verifier; không dùng chung weights làm bằng chứng independence. Calibration vẫn theo actual whole-effect/domain.

Đây là lựa chọn thiết kế cần adapter/serving smoke, chưa là benchmark. vLLM nhận prompts/messages theo từng request qua [server API](https://docs.vllm.ai/en/v0.11.0/serving/openai_compatible_server.html); [memory controls](https://docs.vllm.ai/en/v0.11.0/configuration/conserving_memory.html) cung cấp giới hạn context/concurrency. Các tài liệu đó không chứng minh full recipe fit trên H100. Không thêm hệ thống routing service mới: role→endpoint mapping trong config là đủ.
