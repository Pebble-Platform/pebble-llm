# Bài báo mới 2023–2026 — bổ sung cho stream finetuning-message

> Các bài **chưa có** trong `finetuning-message/` (01–23), giới hạn **chỉ 2023–2026**, sát Pebble
> (multi-task emotion + VAD intensity + sentiment + safety/crisis trên text mental-health, backbone NeoBERT).
> Bài mới nên **citation thấp** → xếp theo **độ sát Pebble + venue**, không theo cited. Biên soạn 2026-06-20,
> agent `research-paper` (3 góc: emotion-LLM / MTL+mental-health / dataset-benchmark). ⚠ Một số là preprint
> (arXiv/medRxiv) chưa peer-review — đánh dấu rõ.

---

## A. Nhóm 1 — Hệ thống / phương pháp emotion + mental-health (gần Pebble nhất)

| # | Bài | Năm | Venue | Vì sao sát Pebble |
|---|---|---:|---|---|
| R1 | **HMT-BB** — Hybrid Multi-Task BERT+BiLSTM (Parmar & Tiwari) | 2025 | Arabian J. Sci. Eng. (Springer) | **3 head cùng lúc: emotion cls + intensity + VAD regression** — gần cấu trúc Pebble nhất từ sau Ghosh 2022 |
| R2 | **Hierarchical Dual-Head** trên MentalRoBERTa (Yang et al.) | 2025 | IEEE BigData | Head **CORAL ordinal + classification** trên encoder chung + freeze 50% layer ≈ severity head + staged-unfreeze của Pebble |
| R3 | **CRADLE Bench** — clinician-annotated crisis benchmark (Byun et al.) | 2026 | EACL | 7 loại crisis + nhãn temporal; LLM-ensemble auto-label ≈ silver label; đúng bài toán recall của safety head |
| R4 | **Rao et al.** — multi-label crisis ở hotline tâm lý | 2026 | PLOS Digital Health | Transcript hotline thật, đa nhãn risk; text > audio — đúng setting deploy của Pebble |
| R5 | **MentaLLaMA / IMHI** (Yang et al.) | 2024 | WWW (ACM) | 105K mẫu ChatGPT-annotated, 8 task MH — **tiền lệ trực tiếp của distillation Gemini→NeoBERT** |
| R6 | **DepressionEmo** (Rahman et al.) | 2024 | J. Affective Disorders | Reddit, 8 cảm xúc gồm **suicide-intent** — gần nhất với (emotion head + safety head) cùng label space; CC BY 4.0 |

---

### Analysis — R1 HMT-BB (BERT+BiLSTM, Parmar & Tiwari, 2025)
- **Overlap:** 42% (adjacent) — D1=2, D2=0, D3=1, D4=0, D5=1, D6=0, D7=2
- **Closest on:** D1 (emotion cls + intensity + VAD regression trên 1 encoder chung — đúng cấu trúc head dị thể của Pebble) và D7 (backbone BERT).
- **Best point (Design lesson):** VAD regression từ text có **trần rất lệch theo trục** — Pearson Valence **0.698** ≫ Arousal **0.399** > Dominance **0.298** (EmoBank); emotion-cls acc 92.44% (EmoInt). → không phải chiều liên tục nào cũng học được từ text như nhau.
  - **How to apply to Pebble:** đặt kỳ vọng/đánh giá riêng cho từng head liên tục — trục kiểu *dominance* có trần ~0.30 Pearson, nên cân nhắc down-weight hoặc loại bỏ chiều liên tục khó trước khi tốn công, và dùng các con số này làm **baseline tham chiếu** cho head severity/energy.
- **Caveats:** Phần method + cơ chế cân bằng loss (D5) **bị paywall** (Springer) → score D5 độ tin cậy thấp; chưa xác nhận có dùng uncertainty/GradNorm hay trọng số tĩnh. Venue (Arabian J. Sci. Eng.) hạng vừa, không phải top-tier NLP. Domain general (tweets), không phải mental-health.
- **Kết luận xếp tier:** 42% = *adjacent*, không phải *core* (≥70%). → **nên hạ R1 từ Tier 1a xuống Tier 2** trong [`CURATED-keep-list-vi.md`](CURATED-keep-list-vi.md): giữ làm *baseline/design-lesson* cho head liên tục, không phải hệ-gần-nhất để bám theo.

---

## B. Nhóm 2 — Phương pháp cân bằng MTL mới (D-B của Pebble)

| # | Bài | Năm | Venue | Đóng góp |
|---|---|---:|---|---|
| R7 | **FAMO** — Fast Adaptive Multitask Optimization (Liu et al.) | 2023 | NeurIPS | Cân bằng loss **O(1)** không lưu gradient — bản rẻ của GradNorm; đã có trong LibMTL |
| R8 | **DB-MTL** — Dual-Balancing MTL (Lin et al.) | 2025 | Neural Networks (Elsevier) | **Log-transform loss** + chuẩn hóa gradient — trị thẳng lệch scale MSE/CE/BCE của Pebble |
| R9 | **UW-ANA** — Analytical Uncertainty Weighting (Kirchdorfer et al.) | 2025 | IJCV (Springer) | Trọng số uncertainty **dạng đóng**, ổn định hơn Kendall (tốt cho data nhỏ) |
| R10 | **MTLComb** — Regression+Classification MTL (Cao et al.) ⚠preprint | 2024 | arXiv | Chứng minh **cộng thẳng loss reg+cls là biased** — lý lẽ toán học cho weighting của Pebble |
| R11 | **AutoMixAlign** — minimax data mixing (Corrado et al.) | 2025 | ACL | Minimax giữ task không tụt dưới sàn — khung cho ràng buộc recall-floor safety head |

## C. Nhóm 3 — Fine-tuning strategy / LLM cho emotion & MH

| # | Bài | Năm | Venue | Đóng góp |
|---|---|---:|---|---|
| R12 | **Kermani et al.** — Fine-tune vs Prompt vs RAG cho MH text | 2025 | CLPsych @ NAACL | Fine-tune 91% emotion / 80% MH vs prompt 40–68% → **lý do chọn fine-tune encoder thay vì prompting** |
| R13 | **Belay et al.** — Evaluating LLMs multi-label emotion (EthioEmo) | 2025 | COLING | Encoder nhỏ fine-tuned **vẫn ngang/hơn decoder LLM lớn** → biện minh chọn NeoBERT 250M |
| R14 | **Lotus @ SemEval-2025 Task 11** (Ranjbar & Baghbani) | 2025 | SemEval @ ACL | LLM sinh giải thích → nối vào input → fine-tune RoBERTa (1 bước distillation); MacroF1 0.74 |
| R15 | **EICL** — Emotion In-Context Learning (Ren et al.) | 2025 | CIKM | Chọn exemplar **tương đồng cảm xúc** + soft-label; upper-bound "prompting làm được gì" |
| R16 | **Multi-label MH trên MultiWD** (Hsieh et al.) | 2025 | Scientific Reports (Nature) | Prompt-ensemble + auxiliary self-supervised; 6 chiều wellness đa nhãn |
| R17 | **Arcan** — LoRA/QLoRA vs DPO/ORPO cho MH ⚠preprint | 2026 | arXiv | So sánh PEFT có hệ thống; "không method nào trội" → biện minh ablation của Pebble |

## D. Nhóm 4 — Dataset / Benchmark mới (so điểm + nguồn nhãn)

| # | Bài | Năm | Venue | Nội dung & access |
|---|---|---:|---|---|
| R18 | **SemEval-2025 Task 11 — BRIGHTER** (Muhammad et al.) | 2025 | SemEval @ ACL | Đa nhãn emotion + **intensity 4 mức**, 30+ ngôn ngữ; **track English intensity mở** — sát head emotion+intensity của Pebble. → `find-dataset` |
| R19 | **WASSA 2023 Shared Task** (Barriere et al.) | 2023 | WASSA @ ACL | Empathy/distress regression + emotion cls cùng corpus (bản 2021 đã có là khác) |
| R20 | **WASSA 2024 Shared Task** (Giorgi et al.) | 2024 | WASSA @ ACL | Thêm track hội thoại **người–LLM agent** — gần domain Pebble (user nói với agent) |
| R21 | **CLPsych 2024 Shared Task** (Chim et al.) | 2024 | CLPsych @ EACL | Suicidality 3 mức (Low/Mod/High) + trích evidence; UMD Reddit (gated, requestable). → calibrate safety head |
| R22 | **CLPsych 2025 Shared Task** (Tseriotou et al.) | 2025 | CLPsych @ NAACL | **Well-being score 1–10 (regression)** + self-state — sát head liên tục severity/socialIsolation |
| R23 | **SemEval-2024 Task 10 — EDiReF** (Kumar et al.) | 2024 | SemEval @ NAACL | ERC + emotion-flip reasoning, code-mixed Hi-En; subtask English để ablation head emotion |
| R24 | **Weber et al.** — crisis detection chatbot thật ⚠medRxiv | 2026 | medRxiv (chưa review) | 200 đoạn chatbot thật, sensitivity 0.99, latency <1s — biện minh recall-floor + real-time |

---

## E. Top ưu tiên xử lý tiếp (sát Pebble nhất)
1. **R1 HMT-BB** + **R2 Hierarchical Dual-Head** — hai kiến trúc 2025 gần cấu trúc multi-head Pebble nhất → `/analysis-paper`, cần full-PDF.
2. **R8 DB-MTL** + **R9 UW-ANA** + **R10 MTLComb** — bộ ba trị thẳng lệch scale MSE/CE/BCE và biện minh weighting → bổ sung vào bảng ablation cân bằng MTL.
3. **R18 BRIGHTER (SemEval-2025 T11)** + **R22 CLPsych 2025** — benchmark công khai cho head emotion+intensity và head regression → `/find-dataset`.
4. **R5 MentaLLaMA/IMHI** + **R3 CRADLE Bench** — tiền lệ trực tiếp cho distillation LLM-teacher và benchmark safety → `/analysis-paper`.
5. **R6 DepressionEmo** (CC BY 4.0) — tải ngay được → `/find-dataset`.

> So với bộ kinh điển trong `FAMOUS-cited-papers-vi.md`: nhóm này MỚI (2023–2026), citation thấp nhưng **sát
> phương pháp/đề bài Pebble hơn**. Ưu tiên cho báo cáo phần "recent related work". ⚠ Verify lại năm + venue +
> trạng thái preprint trước khi đưa vào bản chính.
