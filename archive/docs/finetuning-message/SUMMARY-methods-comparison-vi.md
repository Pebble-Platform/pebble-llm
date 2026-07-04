# Bảng tổng hợp & so sánh phương pháp — Finetuning message cho nhận diện cảm xúc

> Tổng hợp 23 bài báo trong stream `finetuning-message/` (01–23), đọc lại từ các dossier phân tích sẵn.
> Mục tiêu: so sánh **phương pháp** (backbone, kỹ thuật cốt lõi, cách cân bằng multi-task, hàm loss, dataset, kết quả)
> và rút ra điều Pebble có thể áp dụng. Bối cảnh Pebble: multi-task **emotion + VAD intensity + sentiment** trên
> nền **NeoBERT**, dữ liệu mental-health/crisis. Biên soạn 2026-06-20.

---

## A. Bảng tổng hợp đầy đủ (23 bài)

| # | Bài / Venue-Năm | Task | Backbone | Phương pháp cốt lõi | Cân bằng MTL | Loss | Dataset | Kết quả chính | Pebble dùng được gì |
|---|---|---|---|---|---|---|---|---|---|
| **01** | FAIIR, npj Digit. Med. 2025 | Phân loại đa nhãn 19-tag crisis | Longformer (ensemble 3 model) | Domain-adaptive MLM + ngưỡng riêng từng tag + priority-prefix | — (1 task chính) | BCE | KHP crisis SMS (~780k hội thoại) | AUROC 0.94, F1 0.64, recall 0.81 | Tuning ngưỡng theo tần suất, MLM in-domain, lớp luật escalation |
| **02** | Ghosh VAD multitask, IPM 2023 | Emotion đa nhãn + intensity | BERT | Transformer hỗ trợ bằng VAD-lexicon | Trọng số tĩnh (0.3/0.3/1.0) | BCE (emotion) + MSE (intensity) | CEASE-v2.0 (4,932 câu, 325 thư tuyệt mệnh) | Emotion MR 65.25%, +8.78% vs SOTA | Head phân loại + liên tục chung trên corpus nhỏ |
| **03** | Pathak CFN, ACM TCH 2025 | MH-disorder + emotion + sentiment (tri-task) | BERT-family (MentalBERT) | Core Fusion Network (shared–private fusion) | Trọng số tĩnh hand-tuned | Weighted-sum CE | MotiVAte mở rộng (~7k, silver ER/SA) | 89.12% acc MHD-ID | Tri-task > bi/uni: emotion+sentiment phụ trợ task chính |
| **04** | Emo Pillars, Findings ACL 2025 | Emotion đa nhãn 28-class | RoBERTa-large (student); Mistral-7B teacher | Distillation từ LLM-teacher trên data tổng hợp | — (1 head BCE) | BCE trên nhãn teacher đã ngưỡng hóa | ~400k synthetic + GoEmotions/ISEAR/IEMOCAP | GoEmotions macro-F1 0.55 SOTA | Ngưỡng expressiveness 0.3; protocol sweep 0.05–0.95 |
| **05** | Sharma EPITOME, EMNLP 2020 | Empathy thứ bậc (3 cơ chế) + trích rationale | RoBERTa-base bi-encoder + cross-attn | 2 encoder domain-MLM + bi-encoder cross-attentive | Trọng số scalar tĩnh (λ_EI=1, λ_RE=0.5) | CE (EI) + token-BCE (RE) | EPITOME (10,143 cặp TalkLife+Reddit) | EI macro-F1 0.67–0.74; IOU-F1 ≤0.86 | Task phụ rationale + domain-adaptive MLM |
| **06** | Kendall Uncertainty Weighting, CVPR 2018 | Depth regression + segmentation | CNN (ResNet-101/DeepLabV3) | Trọng số loss = uncertainty homoscedastic học được | log-variance per-task `s` học được | `exp(−s)·Lᵢ + s/2` (Gaussian NLL) | NYUv2 | Seg IoU 43.1→46.6 (+3.5) | Học trọng số head thay cho tune λ; floor an toàn |
| **07** | GradNorm, ICML 2018 | Regression + classification hỗn hợp | VGG16 SegNet, ResNet-50-FCN | Cân bằng norm gradient chuẩn hóa ở layer chia sẻ | `wᵢ` học được, 1 knob α | L1 GradNorm trên độ lớn gradient | NYUv2, MTFL | Bằng grid-search trong 1 lần chạy; α=1.5 | Cân bằng gradient scale-free trên `[CLS]`; floor `w_safety` |
| **08** | PCGrad (Gradient Surgery), NeurIPS 2020 | Vision cls/seg + multi-task RL | Task-agnostic (MTAN, routing) | Chiếu gradient xung đột lên mặt phẳng pháp tuyến | Giải xung đột hướng, không có trọng số loss | Kế thừa loss gốc + projection | CelebA, NYUv2, CIFAR-100, Meta-World | NYUv2 mIoU 17.15→20.17 | Thêm "arm" xử lý hướng; bảo vệ head crisis khỏi bị chiếu |
| **09** | Nash-MTL, ICML 2022 | Vision seg/depth + hồi quy phân tử + RL | Task-agnostic | Kết hợp gradient bằng nghiệm mặc cả Nash | Giải `GᵀGα=1/α`; bất biến scale | Tích log-utility | NYUv2, CityScapes, QM9, MT10 | NYUv2 Δm% = −4.04 (duy nhất vượt single-task) | Arm bất biến scale; Nash-MTL-k cho budget Kaggle |
| **10** | LibMTL, JMLR 2023 | Công cụ MTL (mọi chiến lược) | Backbone-agnostic | API thống nhất Weighting/Architecture (27+8 method) | Hoán đổi qua flag (EW/UW/GradNorm/PCGrad/Nash) | `loss_fn` per-task tự cấp (MSE/CE/BCE) | NYUv2, Office, QM9 | Không method nào trội tuyệt đối; EW tuned mạnh | Chạy cả ablation bằng flag; subclass SafetyFloorWeighting |
| **11** | Revisit MTL Imbalance, 2025 | Benchmark dense-prediction MTL | ResNet/HRNet/ViT | Benchmark MTO + luật rẻ AvgNorm (gradient-norm) | AvgNorm `wᵢ=‖Σ∇‖/‖∇ᵢ‖` | Rescale theo norm gradient | NYUD-v2, PASCAL, Replica | AvgNorm +0.37 Δm% ≈ grid search; MGDA sụp −7.19 | Tune static-λ làm null hypothesis; AvgNorm rẻ |
| **12** | MentalBERT, LREC 2022 | Single-task depression/stress/ideation | BERT/RoBERTa-base (~110M) | Continued-pretraining MLM trên Reddit MH | — (single-task) | MLM + `[CLS]`→MLP fine-tune | 8 benchmark (SWMH, eRisk18, CLPsych15…) | MentalRoBERTa eRisk 93.38 F1 | MLM ngắn cho NeoBERT trên text MH; split-LR 1e-5/3e-5 |
| **13** | PGKD distillation, EMNLP 2024 | Phân loại topic đa lớp | BERT-base student; Claude-3 teacher | Vòng distillation chủ động nhắm lỗi (hard negatives) | — (single-task) | CE phẳng | AG-News, Yahoo, Huffington, AMZN | AMZN acc 0.320→0.443; student vượt teacher | Vòng FN-targeted Gemini→NeoBERT silver cho recall an toàn |
| **14** | Semi-Sup Label Smoothing C-SSRS, 2024 | Phân loại nguy cơ tự sát 5-class | CNN 1-D từ đầu | MC-Dropout (T=100) làm mềm nhãn / tự gán lại | — | CE trên nhãn đã làm mềm | Reddit C-SSRS, 500 users (đã có) | Acc 0.4312→0.5233 | MC-Dropout làm mềm silver Gemini; động lực ordinal loss |
| **15** | Suicidal Risk Hybrid, ASONAM 2025 | Suicide-severity 4-class (post) | RoBERTa-base ⊕ TF-IDF+PCA | Ghép CLS RoBERTa với feature TF-IDF→PCA | — | CE | 2,999 post Reddit + HKPU 500 | Weighted-F1 0.7512 (hybrid ~vô ích) | Kết quả âm: bỏ ghép TF-IDF; dùng ordinal loss + recall floor |
| **16** | LLM Reasoning C-SSRS, 2025 | Chấm ordinal 7-point zero-shot | LLM đóng băng (Claude/GPT/Gemini…) + SVM | Chain-of-thought zero-shot, output JSON; không fine-tune | — | Không (inference) | ~1,200 post r/SuicideWatch, κ=0.82 | Claude F1 0.7505; Mistral MAE 0.4398 | Lỗi adjacent → ordinal loss + QWK/MAE; prior chất lượng Gemini-teacher |
| **17** | RSD-15K, IEEE ICME 2025 | C-SSRS 4-class user-level, temporal | RoBERTa/DeBERTa + temporal-attn | Corpus lớn theo thời gian; nhãn = post mới nhất | — | Head phân loại thường | RSD-15K 14,613 post (KHÔNG lấy được) | DeBERTa 76% acc / 77% macro-F1 | Ontology C-SSRS 4-class + QC annotation κ=0.72 |
| **18** | WASSA@IITK, WASSA 2021 | Emotion cls + empathy/distress regression | ELECTRA-large | Encoder chung, 2 head regression + 1 head CE emotion | **Tổng MSE không trọng số (λ=1,1)** | MSE (reg) + CE (emotion) | WASSA 2021 essays (đã có) | Empathy r=0.533; emotion macro-F1 0.5528 (hạng 1) | **Hệ gần nhất**: reg+cls trên 1 encoder; baseline uniform-sum phải vượt |
| **19** | NCUEE-NLP, WASSA 2023 | Empathy/distress/emotion-intensity regression | RoBERTa, RoBERTa-Twitter, EmoBERTa | 3 backbone affect-adapted, ensemble trung bình | — (model riêng) | Regression (tối ưu Pearson) | WASSA 2023 | Track 2 Pearson 0.4178 (hạng 1/9) | Init affect-adapted nâng regression tới +22% rel; metric Pearson |
| **20** | ULMFiT, ACL 2018 | Text classification (transfer) | AWD-LSTM | Gradual unfreezing + discriminative LR + STLR | — (single-task) | CE | TREC/IMDb/AG/DBpedia/Yelp | IMDb error 4.6 (−43.9% rel) | Lịch freeze→unfreeze theo tầng + LR riêng cho NeoBERT |
| **21** | RecAdam, EMNLP 2020 | Fine-tune chống quên thảm họa | BERT/ALBERT | Anchor bậc 2 về θ* + annealing sigmoid (data-free) | λ(t) sigmoid recall vs target | λ(t)·L_T + (1−λ(t))·½γΣ(θ−θ*)² | GLUE (8 task) | BERT-base+RecAdam 84.3 > BERT-large 84.1 | Thay AdamW drop-in để bảo vệ warm-start trên tập nhỏ |
| **22** | ModernBERT, 2024 | Backbone encoder (NLU/retrieval/code) | ModernBERT (149M/395M) | RoPE + GeGLU + local-global attn + unpadding | — | MLM (mask 30%, không NSP) | 2T tokens; eval GLUE/BEIR | GLUE-base 88.4 (vượt DeBERTaV3-base) | Baseline backbone đối đầu NeoBERT; mask rate 30% |
| **23** | ESConv, ACL 2021 | Sinh hội thoại hỗ trợ cảm xúc + dataset | BlenderBot-small / DialoGPT-small | Framework ESC (3 giai đoạn × 8 chiến lược) | — | CE sinh, điều kiện theo strategy | ESConv (1,300 hội thoại / 38K lượt) | Cường độ trung bình 4.04→2.14 | Slice calibration emotion + intensity 1–5 (CC-BY-NC, research-only) |

---

## B. So sánh theo trục phương pháp (cái Pebble quan tâm nhất)

### B1. Kiến trúc task: single-task vs multi-task vs tri-task
| Kiểu | Bài | Ghi chú |
|---|---|---|
| Single-task | 01, 12, 13, 14, 20, 21, 22 | Encoder + 1 head; nền tảng cho backbone/distillation/staged-FT |
| Multi-task (cls + regression) | **02, 18**, 06, 07 | Gần Pebble nhất: kết hợp head phân loại + head liên tục |
| Tri-task (cls + cls + cls) | **03** | Emotion + sentiment phụ trợ task disorder-ID |
| Multi-mechanism + rationale | 05 | Empathy 3 cơ chế + trích đoạn lý do |
| Ensemble model riêng | 19 | Không chia sẻ encoder, average ensemble |

### B2. Cách cân bằng multi-task (D-B của Pebble)
| Nhóm | Bài | Bản chất |
|---|---|---|
| **Tổng không trọng số / tĩnh** | **18** (uniform), 02/03/05 (tĩnh tay) | Baseline cần vượt — 18 thắng shared task chỉ bằng tổng MSE |
| Trọng số học được (uncertainty) | 06 | log-variance per-task |
| Cân bằng gradient | 07 (norm), 11 (AvgNorm), 08 (projection) | Tác động trực tiếp lên gradient layer chia sẻ |
| Tối ưu hóa game-theory | 09 (Nash) | Bất biến scale, vượt single-task |
| Công cụ/ablation | 10 (LibMTL) | Hoán đổi mọi chiến lược bằng flag |
> **Bài học chính (từ SYNTHESIS):** novelty "principled balancing" của Pebble phải đánh bại **uniform-sum**;
> lý do chính đáng để cân trọng số là **lệch scale MSE+CE** (mà bài 18 không gặp vì cộng 2 MSE cùng scale).

### B3. Hàm loss & xử lý ordinal (D-C)
- Phân loại: BCE đa nhãn (01, 02, 04, 05-RE), CE phẳng (03, 13, 14, 15, 18-emotion).
- Liên tục: MSE (02, 18), regression tối ưu Pearson (19).
- **Ordinal/C-SSRS:** 14/15/16/17 đều có lỗi **adjacent-level** nhưng phần lớn vẫn dùng CE phẳng → Pebble nên dùng
  **ordinal-CE/CORN hoặc regression+MSE**, báo cáo **MAE/QWK** thay vì chỉ accuracy.

### B4. Domain adaptation & lịch fine-tuning (D-D/D-E)
- Domain-adaptive MLM: 01, 05, 12 (đều +1–3 F1) → MLM ngắn cho NeoBERT trên text MH.
- Staged fine-tuning: 20 (gradual unfreeze, **head-only là tệ nhất**), 21 (RecAdam chống quên).
- Affect-adapted init: 19 (+tới 22% rel cho regression).

### B5. Backbone (D-A)
| Bài | Backbone | Liên quan |
|---|---|---|
| 22 | ModernBERT | Đối thủ baseline trực tiếp của NeoBERT (không có benchmark chung → phải test nội bộ) |
| 12 | MentalBERT/RoBERTa | MLM domain MH |
| 04/05/15/17/18/19 | RoBERTa/ELECTRA/DeBERTa | Encoder phổ biến cho affect |
| 01 | Longformer | Văn bản dài |

### B6. Distillation từ LLM (D-F — tạo silver label)
| Bài | Teacher | Cơ chế |
|---|---|---|
| 04 | Mistral-7B | Sinh data tổng hợp + nhãn mềm, ngưỡng hóa |
| 13 | Claude-3 Sonnet | Vòng lặp nhắm lỗi (hard negatives) — student vượt teacher |
| 16 | LLM đóng băng | Zero-shot CoT làm prior chất lượng nhãn |

---

## C. Ba điểm rút gọn cho Pebble
1. **Baseline phải là uniform-sum MTL (bài 18)**, không phải single-task — đây là hệ công bố gần Pebble nhất và nó
   thắng chỉ bằng tổng MSE không trọng số. Lý do cân trọng số = lệch scale MSE+CE.
2. **C-SSRS = bài học method, không phải leaderboard** (14–17 dùng 4 dataset/ontology khác nhau, không so sánh được):
   lỗi adjacent → ordinal loss + MAE/QWK + recall floor cho lớp nguy cơ.
3. **Fine-tuning: tránh đóng băng encoder** (ULMFiT cho thấy head-only tệ nhất); dùng gradual unfreeze + discriminative
   LR, cân nhắc RecAdam + MLM domain ngắn.
