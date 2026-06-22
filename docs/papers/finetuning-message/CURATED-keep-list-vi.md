# Danh sách lọc chất lượng — bài đáng giữ lại tham khảo (stream finetuning-message)

> Lọc trên TẤT CẢ nguồn: **01–23** (đã có trong repo) + **F1–F21** kinh điển ([`FAMOUS-cited-papers-vi.md`](FAMOUS-cited-papers-vi.md))
> + **R1–R24** mới 2023–2026 ([`RECENT-2023-2026-papers-vi.md`](RECENT-2023-2026-papers-vi.md)).
> Tiêu chí giữ: ① venue mạnh + đã peer-review · ② sát phương pháp/đề bài Pebble · ③ không trùng/lỗi thời · ④ dataset lấy được.
> Biên soạn 2026-06-20. ⚠ = preprint chưa peer-review (giữ nhưng cite thận trọng).

---

## TIER 1 — Cốt lõi, phải giữ (đọc kỹ / cite chính)

### 1a. Hệ thống gần Pebble nhất (kiến trúc multi-head emotion + liên tục)
| ID | Bài | Venue/Năm | Vai trò |
|---|---|---|---|
| **02** | Ghosh VAD multitask (CEASE) | IPM 2023 | Reg+cls trên suicide notes — closest system gốc |
| **18** | WASSA@IITK | WASSA 2021 | **Baseline phải vượt**: reg+cls 1 encoder, uniform-sum |
| **R2** | Hierarchical Dual-Head / MentalRoBERTa | IEEE BigData 2025 | CORAL ordinal + cls + freeze layer ≈ severity head + staged-unfreeze |
| **03** | Pathak CFN | ACM TCH 2025 | Tri-task: emotion+sentiment bổ trợ MH disorder |
| **F4** | MT-DNN | ACL 2019 | Tiền lệ kiến trúc BERT+multi-task — baseline cite-and-beat |

### 1b. Cân bằng MTL (D-B) — bộ phương pháp để ablation
| ID | Bài | Venue/Năm | Vai trò |
|---|---|---|---|
| **06** | Kendall Uncertainty Weighting | CVPR 2018 | Trọng số học được — arm kinh điển |
| **07** | GradNorm | ICML 2018 | Cân bằng gradient-norm |
| **08** | PCGrad | NeurIPS 2020 | Xử lý xung đột hướng gradient |
| **09** | Nash-MTL | ICML 2022 | Kết hợp gradient bất biến scale |
| **R7** | FAMO | NeurIPS 2023 | Cân bằng O(1) — bản rẻ GradNorm |
| **R8** | DB-MTL | Neural Networks 2025 | **Log-transform loss** — trị lệch scale MSE/CE/BCE của Pebble |
| **R9** | UW-ANA | IJCV 2025 | Uncertainty weighting dạng đóng, ổn định hơn Kendall |
| **10** | LibMTL | JMLR 2023 | Công cụ chạy cả ablation bằng flag |

### 1c. Distillation LLM-teacher (D-F — tạo silver label)
| ID | Bài | Venue/Năm | Vai trò |
|---|---|---|---|
| **04** | Emo Pillars | ACL Findings 2025 | Distillation LLM + protocol ngưỡng |
| **R5** | MentaLLaMA / IMHI | WWW 2024 | **Tiền lệ trực tiếp**: LLM-teacher annotate 8 task MH |
| **13** | PGKD | EMNLP 2024 | Vòng distillation nhắm lỗi (hard negatives) |

### 1d. Safety / crisis head (D-G/D-H)
| ID | Bài | Venue/Năm | Vai trò |
|---|---|---|---|
| **R3** | CRADLE Bench | EACL 2026 | Benchmark crisis lâm sàng + recall-floor |
| **F20** | STATENet | EMNLP 2020 | Transformer crisis-detection gần safety head nhất |
| **12** | MentalBERT | LREC 2022 | MLM domain MH cho encoder |

### 1e. Dataset / benchmark cốt lõi (so điểm + nguồn nhãn)
| ID | Bài | Venue/Năm | Access |
|---|---|---|---|
| **F10** | GoEmotions | ACL 2020 | Mở — **nguồn warm-start taxonomy** |
| **F6** | SemEval-2018 Task 1 (Affect in Tweets) | NAACL 2018 | Mở — **benchmark reg+cls + metric Pearson** |
| **R18** | SemEval-2025 Task 11 (BRIGHTER) | ACL 2025 | English intensity mở — emotion+intensity |
| **R22** | CLPsych 2025 (well-being 1–10 regression) | NAACL 2025 | Requestable — sát head liên tục |
| **R21** | CLPsych 2024 (suicidality 3 mức) | EACL 2024 | UMD Reddit (gated) — calibrate safety |
| **R6** | DepressionEmo | JAD 2024 | **CC BY 4.0 — tải ngay** |
| **F15** | NRC-VAD Lexicon | ACL 2018 | Mở — đã dùng trong bài 02 |
| **23** | ESConv | ACL 2021 | CC-BY-NC — slice calibration (research-only) |

---

## TIER 2 — Giữ làm ngữ cảnh / citation phụ

| ID | Bài | Venue/Năm | Vì sao giữ (phụ) |
|---|---|---|---|
| **R1** | HMT-BB (BERT+BiLSTM) | Springer 2025 | **Hạ từ Tier 1a (overlap 42%)** — baseline/design-lesson cho head liên tục: VAD Pearson V0.70≫A0.40>D0.30 |
| **01** | FAIIR | npj Dig.Med 2025 | Hệ crisis-line đa nhãn — bài học threshold + escalation |
| **05** | Sharma EPITOME empathy | EMNLP 2020 | Task phụ rationale + domain-MLM |
| **19** | NCUEE WASSA | WASSA 2023 | Affect-adapted init nâng regression |
| **11** | MTL imbalance revisit | 2025 | Tune static-λ làm null hypothesis (AvgNorm) |
| **R10** ⚠ | MTLComb (reg+cls) | arXiv 2024 | Chứng minh cộng thẳng loss reg+cls là biased |
| **R11** | AutoMixAlign | ACL 2025 | Minimax cho ràng buộc recall-floor |
| **R12** | Kermani fine-tune vs prompt vs RAG | CLPsych 2025 | Lý lẽ chọn fine-tune thay prompting |
| **R13** | Belay eval LLM multi-label emotion | COLING 2025 | Lý lẽ chọn encoder nhỏ (NeoBERT) |
| **20** | ULMFiT | ACL 2018 | Nguồn cho gradual unfreeze (head-only là tệ nhất) |
| **21** | RecAdam | EMNLP 2020 | Chống quên khi fine-tune tập nhỏ |
| **F2** | Ruder MTL survey | 2017 | Khung thuật ngữ MTL |
| **F21** | Chen MTL-NLP survey | ACM CSUR 2024 | Survey MTL-NLP mới nhất |
| **F1** | Collobert NLP from scratch | JMLR 2011 | Citation gốc shared-encoder MTL |
| **F13** | Joint Many-Task | EMNLP 2017 | Task hierarchy → lý do staged training |
| **F3** | NRC EmoLex | 2013 | Lexicon categorical baseline |
| **F5** | Warriner VAD norms | 2013 | Ground-truth VAD |
| **F17** | EmoBank | EACL 2017 | VAD mức câu (đánh giá) |
| **F9** | EmpatheticDialogues | ACL 2019 | Dataset transfer in-domain |
| **F11** | TweetEval | EMNLP 2020 | Tiền lệ multi-task 1 encoder |
| **F8** | BERTweet | EMNLP 2020 | Backbone baseline social text |
| **F19** | SMHD | COLING 2018 | Benchmark đa nhãn MH (kiểm license) |
| **F16** | Yates self-harm forums | EMNLP 2017 | Baseline tiền-transformer safety |
| **F7** | De Choudhury depression | ICWSM 2013 | Citation framing MH-NLP |
| **R4** | Rao hotline crisis | PLOS DH 2026 | Hệ deploy gần Pebble (text>audio) |
| **R16** | Multi-label MH MultiWD | Sci.Reports 2025 | Prompt-ensemble + auxiliary self-sup |
| **R19/R20** | WASSA 2023 / 2024 | WASSA 2023/24 | Bản mới của benchmark empathy reg+cls |

---

## TIER 3 — Hạ ưu tiên / lưu trữ (không cần đọc kỹ)

| ID | Bài | Lý do hạ |
|---|---|---|
| **14** | C-SSRS label-smoothing | Chỉ giữ **bài học method** (ordinal loss), không phải leaderboard; CNN-1D lỗi thời |
| **15** | C-SSRS hybrid | Kết quả âm (TF-IDF concat vô ích) — chỉ lấy bài học "đừng làm" |
| **16** | LLM C-SSRS screening | Hữu ích như prior chất lượng nhãn, không phải method để adopt |
| **17** | RSD-15K | **Dataset không lấy được (404)** — chỉ giữ ontology 4-class làm tham chiếu |
| **22** | ModernBERT | Overlap 8%; chỉ là baseline backbone, không benchmark chung với NeoBERT |
| **F12/F14** | DialogueRNN / DialogueGCN | ERC ngữ cảnh hội thoại — Pebble single-turn chủ động không làm |
| **F18** | EmoContext | Benchmark hẹp (4 class), đã gián tiếp qua Emo Pillars |
| **R14** | Lotus SemEval-2025 | Workshop system paper — minh họa, không phải method chính |
| **R15** | EICL (in-context) | Upper-bound prompting, không phải hướng fine-tune của Pebble |
| **R23** | SemEval-2024 Task 10 EDiReF | Code-mixed Hi-En + emotion-flip — lệch domain |
| **R17** ⚠ | Arcan LoRA/QLoRA vs DPO | Preprint, "không method nào trội" — kết luận yếu |
| **R24** ⚠ | Weber chatbot medRxiv | Chưa peer-review; chỉ trích 1 con số sensitivity/latency |

---

## Tóm tắt số lượng
- **Tier 1 (cốt lõi):** 28 bài — đọc kỹ, cite chính.
- **Tier 2 (ngữ cảnh):** 25 bài — citation phụ.
- **Tier 3 (lưu trữ):** 12 bài — tham chiếu khi cần, không ưu tiên.

> **Nguyên tắc lọc đã áp dụng:** giữ bài (a) ở venue đã peer-review mạnh HOẶC (b) sát trực tiếp một quyết định mở của
> Pebble (D-A…D-H). Hạ bài trùng lặp, lỗi thời, dataset không lấy được, hoặc preprint kết luận yếu. ⚠ verify lại
> năm/venue/trạng thái preprint của các bài 2025–2026 trước khi đưa vào báo cáo chính.
