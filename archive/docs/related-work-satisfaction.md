# Related Work — User Satisfaction Estimation từ Next-Turn

> **Mục đích.** Prior art cho một hướng pivot khả dĩ của project: **ước lượng độ hài lòng của user sau mỗi lượt chat với AI**, suy ra từ *message kế tiếp* của user (implicit feedback). Use case: hệ thống chat với AI; sau mỗi câu trả lời của AI, dựa vào phản ứng ở lượt sau (rephrase, sửa lại, bực bội, cảm ơn, bỏ ngang) để biết câu trả lời trước có làm user hài lòng không.
>
> **Vì sao xét pivot này từ `r2-suicide-risk-dualhead`.** Về cỗ máy ML hai bài toán giống ~60–70%: cùng là fine-tune một text-encoder + (multi-)classification head để suy ra một *trạng thái cảm xúc/thái độ từ text hội thoại ngắn*. Kiến trúc **dual-head** và **ordinal head** của project chuyển sang gần như nguyên vẹn. Khác biệt thật nằm ở (1) **nguồn nhãn** — satisfaction phải suy từ tín hiệu implicit nhiễu, không có nhãn lâm sàng sẵn — và (2) **input là cặp/hội thoại** `[câu trả lời AI] [SEP] [lượt kế tiếp của user]`, không phải đơn message.
>
> **Compiled:** 2026-06-25

---

## Dimensions xếp hạng (đã chỉnh cho pivot này)

1. **Encoder + multi-head (MTL)** cho satisfaction — khớp trực tiếp dual-head của project
2. **USE từ next-turn / implicit feedback** (rephrase, frustration, gratitude) đúng use case
3. **Dataset có nhãn satisfaction** turn-level dùng được để khởi động
4. **LLM teacher → encoder student** (silver-label distillation) — pattern Pebble vốn dùng
5. **Encoder backbone** (BERT/RoBERTa/hierarchical transformer) cỡ ~250M

---

## Paper 1 — USDA: Sequential Dialogue Act Modeling for USE  ⭐ sát nhất

- **Authors / Year / Venue:** Yang Deng, Wenxuan Zhang, Wai Lam, Hong Cheng, Helen Meng. **WWW 2022 (The Web Conference)**.
- **Link:** [arXiv:2202.02912](https://arxiv.org/abs/2202.02912) · **Access:** open
- **Summary:** Hierarchical Transformer encode toàn bộ ngữ cảnh hội thoại; **multi-task** jointly học *User Satisfaction Estimation* + *Dialogue Act Recognition*, khai thác chuỗi chuyển dịch dialogue-act. Có 2 biến thể (supervised / unsupervised) + 2 chiến lược task-adaptive pre-training. Validate trên 4 dataset goal-oriented; vượt baseline ổn định.
- **Closeness:** D1 (rất mạnh — đúng "encoder + 2 head trên ngữ cảnh hội thoại"), D2 (mạnh), D5 (mạnh).
- **Why it matters here:** Gần như đúng kiến trúc project đã có. Map thẳng: đổi head *dialogue-act* → head *sentiment/emotion*, giữ head *satisfaction*. **Baseline #1 để bám theo.**

## Paper 2 — STMAN: Speaker Turn-Aware Multi-Task Adversarial Net (USE + Sentiment)  ⭐

- **Authors / Year:** Kaisong Song, Yangyang Kang, Jiawei Liu, Xurui Li, Changlong Sun, Xiaozhong Liu. **2024** (preprint).
- **Link:** [arXiv:2410.09556](https://arxiv.org/abs/2410.09556) · **Access:** open
- **Summary:** Joint **USE (dialogue-level) + Sentiment Analysis (utterance-level)** — hai head ở hai mức hạt khác nhau, cộng adversarial task-discriminator (làm biểu diễn task-specific) + speaker-turn interaction (trích đặc trưng chung bổ trợ). Đánh giá trên 2 dataset hội thoại dịch vụ thực.
- **Closeness:** D1 (rất mạnh — đúng combo *satisfaction + sentiment* dual-head), D2 (mạnh).
- **Why it matters here:** Bằng chứng học thuật rằng **dual-head satisfaction + sentiment** bổ trợ nhau — chính phương án transfer đề xuất cho project.

## Paper 3 — USS: Simulating User Satisfaction (dataset)

- **Authors / Year / Venue:** Weiwei Sun et al. **SIGIR 2021**.
- **Link:** [arXiv:2105.03748](https://arxiv.org/abs/2105.03748) · **Access:** open
- **Summary:** Bộ nhãn satisfaction quy mô lớn, turn-level: ~6.8k annotation cho 500 dialog (CCPE) + ~12.5k cho 1000 dialog (MultiWOZ), kèm các domain khác. Vốn tạo cho user simulation nhưng dùng được như dataset USE chuẩn nhất hiện có.
- **Closeness:** D3 (rất mạnh — dataset gold turn-level), D2 (mạnh).
- **Why it matters here:** **Nguồn nhãn vàng để khởi động**, giải đúng "vấn đề số 1" (lấy nhãn). Train/đánh giá ở đây trước khi sang dữ liệu sản phẩm thật.

## Paper 4 — User Feedback in Human-LLM Dialogues: "noisy as a learning signal"

- **Authors / Year / Venue:** Yuhan Liu, Michael J.Q. Zhang, Eunsol Choi. **EMNLP 2025**.
- **Link:** [arXiv:2507.23158](https://arxiv.org/abs/2507.23158) · **Access:** open
- **Summary:** Trích **implicit feedback từ next turn** trên WildChat & LMSYS (dialog thực với LLM). Kết luận: tín hiệu này *hữu ích để hiểu user nhưng nhiễu khi dùng làm signal huấn luyện* — giúp ở câu hỏi ngắn/curated (MTBench) nhưng không ở câu dài/phức tạp (WildBench).
- **Closeness:** D2 (rất mạnh — đúng y use case: LLM chat, suy từ lượt kế tiếp).
- **Why it matters here:** **Cảnh báo phương pháp luận then chốt** — đừng coi nhãn implicit là sạch. Định hình thiết kế label-noise handling, calibration, và cách validate.

## Paper 5 — SPUR: Interpretable USE with LLMs

- **Authors / Year:** Ying-Chun Lin, Jennifer Neville, Jack W. Stokes et al. **2024** (preprint).
- **Link:** [arXiv:2403.12388](https://arxiv.org/abs/2403.12388) · **Access:** open
- **Summary:** **SPUR** dùng LLM + iterative prompting (rubric có giám sát từ ví dụ gán nhãn) để trích tín hiệu satisfaction; vượt embedding-based; áp cho cả ChatGPT lẫn chatbot task-oriented; cho điểm kèm rubric diễn giải được.
- **Closeness:** D4 (mạnh — LLM teacher), D2 (mạnh).
- **Why it matters here:** Dùng làm **teacher/silver-labeler** để distill nhãn satisfaction cho encoder student — đúng pattern "LLM teacher → smaller student" Pebble vốn dùng.

## Paper 6 — User Frustration Detection in Task-Oriented Dialog

- **Year / Venue:** **COLING 2025 (Industry Track)**.
- **Link:** [ACL Anthology 2025.coling-industry.23](https://aclanthology.org/2025.coling-industry.23.pdf) · **Access:** open
- **Summary:** Phát hiện frustration/dissatisfaction kể cả khi không có ngôn ngữ tiêu cực rõ — termination, interruption, abandonment, error-correcting language ("no, …", "I said …"), reformulation.
- **Closeness:** D2 (mạnh — catalog tín hiệu implicit cụ thể).
- **Why it matters here:** Danh mục **tín hiệu next-turn cụ thể** để feature/heuristic hoá nhãn yếu.

### Bổ sung (chưa đọc sâu, độ tin cậy thấp hơn)
- *Schema-Guided USS* — [arXiv:2305.16798](https://arxiv.org/pdf/2305.16798) (2023)
- *CAUSE — Counterfactual Assessment of USE* — [arXiv:2403.19056](https://arxiv.org/pdf/2403.19056) (2024)
- *Personalized Turn-Level User Conversation Satisfaction Benchmark* — [arXiv:2605.29711](https://arxiv.org/html/2605.29711) (2026, **cần xác minh** — id rất mới)

---

## Synthesis

Bám **USDA (#1)** làm xương kiến trúc (encoder + dual-head trên ngữ cảnh hội thoại — đúng cái project đã có), **STMAN (#2)** chứng minh combo *satisfaction + sentiment* dual-head hoạt động, lấy nhãn khởi động từ **USS (#3)**, và đọc kỹ **#4 (EMNLP'25)** vì nó cảnh báo đúng rủi ro lớn nhất của use case "suy từ lượt kế tiếp": **nhãn implicit rất nhiễu**. **SPUR (#5)** cho con đường sinh nhãn bằng LLM teacher để bù thiếu nhãn.

**Kết luận transfer:** topic này có related-work chín muồi và kiến trúc dual-head/encoder của project chuyển sang gần như nguyên vẹn — không phải làm lại từ đầu. Khoảng trống còn mở để đóng góp: xử lý **label-noise của implicit next-turn feedback** một cách có nguyên tắc (đúng chỗ #4 bỏ ngỏ).
