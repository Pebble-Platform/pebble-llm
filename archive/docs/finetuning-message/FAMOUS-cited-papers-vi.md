# Bài báo nổi tiếng, citation cao — bổ sung cho stream finetuning-message

> Các bài **chưa có** trong `finetuning-message/` (01–23), được tìm thêm theo yêu cầu: ưu tiên **IEEE / venue lớn**
> (ACL, EMNLP, NAACL, AAAI, JMLR, npj, ICWSM…) và **lượng cited cao**. Citation count là xấp xỉ theo
> Semantic Scholar / SciSpace tại ~06/2026 — đánh dấu *approx* khi không xác nhận trực tiếp được.
> Biên soạn 2026-06-20 bằng agent `research-paper` (3 góc: emotion-text / dataset-lexicon / MTL+mental-health).

---

## A. Bảng xếp hạng theo citation (cao → thấp)

| # | Bài / Năm | Venue | ~Cited | Nhóm | Đóng góp / Method |
|---|---|---:|---:|---|---|
| F1 | Collobert & Weston — NLP (Almost) from Scratch, 2011 | JMLR | ~6,800* | MTL kiến trúc | Shared encoder + task-head — tổ tiên của MTL-NLP |
| F2 | Ruder — Overview of Multi-Task Learning in DNNs, 2017 | arXiv (survey) | ~3,307 | MTL survey | Taxonomy hard/soft sharing, auxiliary task, loss-weighting |
| F3 | NRC EmoLex (Mohammad & Turney), 2013 | Computational Intelligence | ~2,511 | Lexicon | 14,181 từ × 8 cảm xúc Plutchik + 2 sentiment (BWS) |
| F4 | MT-DNN (Liu et al.), 2019 | ACL | ~2,000–2,500* | MTL kiến trúc | Fine-tune BERT đồng thời 9 task GLUE, head theo loại task |
| F5 | Warriner et al. — VAD norms 13,915 từ, 2013 | Behavior Research Methods | ~1,869 | VAD norms | Chuẩn tâm lý ngôn ngữ cho Valence/Arousal/Dominance |
| F6 | SemEval-2018 Task 1 — Affect in Tweets (Mohammad), 2018 | SemEval/NAACL | ~500–1,700* | Benchmark | Đồng thời intensity **regression** + ordinal + emotion cls |
| F7 | De Choudhury et al. — Predicting Depression via Social Media, 2013 | ICWSM (AAAI) | ~1,000–1,200* | Mental-health | Bài nền tảng phát hiện trầm cảm từ mạng xã hội |
| F8 | BERTweet (Nguyen et al.), 2020 | EMNLP demo | ~1,009* | Backbone | BERT pretrain 850M tweet — encoder domain social media |
| F9 | EmpatheticDialogues (Rashkin et al.), 2019 | ACL | ~913–950 | Dataset | 25K hội thoại đồng cảm, 32 nhãn cảm xúc |
| F10 | GoEmotions (Demszky et al.), 2020 | ACL | ~899 | Dataset | 58K comment Reddit, 27+1 nhãn — nguồn warm-start taxonomy |
| F11 | TweetEval (Barbieri et al.), 2020 | Findings EMNLP | ~832 | Benchmark MTL | 7 task tweet trên 1 encoder RoBERTa chia sẻ |
| F12 | DialogueRNN (Majumder et al.), 2019 | AAAI | ~641 | ERC | RNN theo dõi state speaker/global/emotion |
| F13 | Joint Many-Task (Hashimoto et al.), 2017 | EMNLP | ~600–700* | MTL kiến trúc | Mạng phân tầng theo độ phức tạp ngôn ngữ |
| F14 | DialogueGCN (Ghosal et al.), 2019 | EMNLP-IJCNLP | ~595 | ERC | GCN quan hệ, ngữ cảnh speaker-aware |
| F15 | NRC-VAD Lexicon (Mohammad), 2018 | ACL | ~524 | Lexicon VAD | 20K từ chấm VAD bằng Best-Worst Scaling |
| F16 | Yates, Cohan & Goharian — Self-Harm Risk in Forums, 2017 | EMNLP | ~350–450* | Mental-health | CNN/LSTM phân tầng, đánh giá rủi ro mức user |
| F17 | EmoBank (Buechel & Hahn), 2017 | EACL | ~300–400* | Dataset VAD | 10K câu chú thích VAD, writer vs reader perspective |
| F18 | EmoContext — SemEval-2019 Task 3 (Chatterjee et al.), 2019 | SemEval/NAACL | ~273–302 | Benchmark | Phát hiện cảm xúc ngữ cảnh 3 lượt hội thoại |
| F19 | SMHD (Cohan et al.), 2018 | COLING | ~165 | Dataset MH | 240K user Reddit, 9 bệnh tâm lý, đa nhãn |
| F20 | STATENet (Sawhney et al.), 2020 | EMNLP | ~92–200* | Mental-health | Transformer time-aware cho phát hiện ý định tự sát |
| F21 | Chen, Zhang & Yang — MTL in NLP: An Overview, 2024 | ACM Comp. Surveys | ~75 | MTL survey | Survey MTL-NLP mới nhất (4 lớp kiến trúc) |

\* citation xấp xỉ / chưa xác nhận con số chính xác.

---

## B. Chi tiết theo nhóm + liên quan tới Pebble

### Nhóm 1 — Kiến trúc & lý thuyết MTL (cite-and-frame)
- **F1 Collobert & Weston 2011** — [JMLR](https://jmlr.org/papers/v12/collobert11a.html). Citation nền của shared-encoder MTL. *Pebble:* citation gốc cho kiến trúc encoder chung + nhiều head.
- **F4 MT-DNN 2019** — [ACL P19-1441](https://aclanthology.org/P19-1441/) · [arXiv:1901.11504](https://arxiv.org/abs/1901.11504). **Tiền lệ trực tiếp nhất**: BERT + multi-task fine-tune, head theo loại task. *Pebble:* baseline kiến trúc phải vượt.
- **F2 Ruder 2017** — [arXiv:1706.05098](https://arxiv.org/abs/1706.05098). Survey thuật ngữ MTL. *Pebble:* cite để định khung related-work.
- **F13 Joint Many-Task 2017** — [EMNLP D17-1206](https://aclanthology.org/D17-1206/). Phân tầng task theo độ phức tạp. *Pebble:* lý do cho lịch staged freeze/unfreeze.
- **F21 Chen et al. 2024** — [ACM CSUR](https://dl.acm.org/doi/10.1145/3663363) · [preprint](https://arxiv.org/pdf/2204.03508). Survey MTL-NLP mới nhất. *Pebble:* định vị đóng góp loss-balancing trong SOTA 2024.

### Nhóm 2 — Dataset / Lexicon cảm xúc & VAD (nguồn nhãn + benchmark)
- **F3 NRC EmoLex 2013** — [arXiv:1308.6297](https://arxiv.org/abs/1308.6297). Lexicon cảm xúc phổ biến nhất. *Pebble:* baseline taxonomy categorical.
- **F5 Warriner 2013** — [Springer DOI](https://link.springer.com/article/10.3758/s13428-012-0314-x). Chuẩn VAD lớn nhất tiền-NRC. *Pebble:* ground-truth cho head regression VAD.
- **F15 NRC-VAD 2018** — [ACL P18-1017](https://aclanthology.org/P18-1017/). Lexicon VAD chất lượng cao (đã dùng trong Ghosh/bài 02). *Pebble:* tín hiệu lexicon cho head liên tục.
- **F10 GoEmotions 2020** — [ACL 2020.acl-main.372](https://aclanthology.org/2020.acl-main.372/) · [arXiv:2005.00547](https://arxiv.org/abs/2005.00547). **Nguồn warm-start taxonomy của Pebble**; baseline BERT macro-F1 0.43 là sàn phải vượt.
- **F9 EmpatheticDialogues 2019** — [ACL P19-1534](https://aclanthology.org/P19-1534/). Nguồn transfer in-domain, 32 nhãn cảm xúc. *Pebble:* calibrate silver label + head emotion.
- **F17 EmoBank 2017** — [EACL E17-2092](https://aclanthology.org/E17-2092/). VAD mức câu. *Pebble:* corpus đánh giá output VAD liên tục.

### Nhóm 3 — Benchmark đo cảm xúc (so điểm)
- **F6 SemEval-2018 Task 1** — [ACL S18-1001](https://aclanthology.org/S18-1001/). **Shared task duy nhất ghép regression intensity + emotion cls** — gần cấu trúc head dị thể của Pebble nhất; định metric Pearson-r.
- **F11 TweetEval 2020** — [Findings EMNLP](https://aclanthology.org/2020.findings-emnlp.148/) · [arXiv:2010.12421](https://arxiv.org/abs/2010.12421). Tiền lệ multi-task 1 encoder RoBERTa cho 7 task social text; backbone RoBERTa-Twitter là baseline đối đầu NeoBERT.
- **F18 EmoContext 2019** — [ACL S19-2005](https://aclanthology.org/S19-2005/). Cảm xúc ngữ cảnh 3 lượt (dùng trong Emo Pillars). *Pebble:* benchmark phụ hẹp hơn GoEmotions.
- **F12 DialogueRNN 2019** — [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/4657) & **F14 DialogueGCN 2019** — [EMNLP D19-1015](https://aclanthology.org/D19-1015/). Cặp baseline ERC ngữ cảnh hội thoại — phương án "vì sao không mô hình lịch sử hội thoại" mà Pebble (single-turn) chủ động đánh đổi.

### Nhóm 4 — Backbone & Mental-health NLP (safety head)
- **F8 BERTweet 2020** — [EMNLP demo](https://aclanthology.org/2020.emnlp-demos.2/) · [HF](https://huggingface.co/vinai/bertweet-base). Encoder domain social media. *Pebble:* baseline backbone cho split Reddit/Twitter, đối đầu NeoBERT.
- **F7 De Choudhury 2013** — [ICWSM](https://ojs.aaai.org/index.php/ICWSM/article/view/14432). Bài nền phát hiện trầm cảm từ mạng xã hội. *Pebble:* citation định khung mental-health NLP.
- **F16 Yates et al. 2017** — [EMNLP D17-1322](https://aclanthology.org/D17-1322/). Baseline tiền-transformer cho head safety nhị phân (đánh giá mức user).
- **F20 STATENet 2020** — [EMNLP 2020.emnlp-main.619](https://aclanthology.org/2020.emnlp-main.619/). **Gần head safety của Pebble nhất**: transformer time-aware phát hiện ý định tự sát. → nên cho `analysis-paper`.
- **F19 SMHD 2018** — [COLING C18-1126](https://aclanthology.org/C18-1126/) · [dataset](https://ir.cs.georgetown.edu/resources/smhd.html). Benchmark đa nhãn 9 bệnh tâm lý. → nên cho `find-dataset` kiểm tra license.

---

## C. Đề xuất ưu tiên xử lý tiếp
1. **F4 MT-DNN** và **F6 SemEval-2018 Task 1** — tiền lệ kiến trúc + benchmark gần Pebble nhất → chạy `/analysis-paper` để chấm overlap.
2. **F20 STATENet** và **F16 Yates 2017** — baseline mạnh nhất cho head safety → `/analysis-paper`.
3. **F19 SMHD** — kiểm tra license/gate qua `/find-dataset` (multi-label MH benchmark).
4. **F10 GoEmotions, F6 SemEval-2018, F15 NRC-VAD** — citation bắt buộc cho phần taxonomy + head liên tục.

> Lưu ý: con số citation là xấp xỉ tại 06/2026, một số bị chặn fetch trực tiếp (đánh dấu *). Nên verify lại trước khi
> đưa vào báo cáo chính thức.
