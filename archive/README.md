# Archive — các chương trình tiền nhiệm (đóng băng 2026-07-04)

Quyết định pivot của chủ dự án (2026-07-04): repo tập trung vào **ViEmoSpeech**
(corpus SER tiếng Việt + bimodal tone×emotion). Mọi thứ không thuộc stream
`vietnamese-ser` được chuyển nguyên trạng vào đây — **không xóa gì**; git history
đầy đủ; khôi phục = `git mv` ngược lại (hoặc đọc tại chỗ).

**Trạng thái khi đóng băng** (chi tiết trong từng tracking doc tại `docs/tasks/`):

| Chương trình | Nằm ở | Trạng thái lúc đóng băng |
|---|---|---|
| **Text — ordinal suicide-risk (thesis stream 1)** | `docs/finetuning-message/`(papers) · `kaggle/finetuning-message/` · `docs/tasks/r2-*`, `thesis-*` · `docs/reports/` · `scripts/r2_*` | 3 đóng góp phương pháp đã verify (CORN+GCE · label-shift · ordinal-CL), ablation 2×2 + 2 baseline xong, mọi số khớp retained-log (`kaggle/finetuning-message/results-summary.csv`); draft IEEE viết dở; blocker còn lại: Cohen's κ LLM↔gold, ethics section |
| **Voice — crisis-sensitive affect (thesis stream 2)** | `docs/voice/`(papers) · `kaggle/pebble-voice-backbone/` · `docs/tasks/voice-*` · `scripts/voice_*` | Backbone chọn xong (WavLM > emotion2vec, 3/3 seed); crisis head precision 0.617 @ recall≥0.90; MTL M3 kernel build xong chưa chạy; blocker: MSP-Podcast/DAIC-WOZ access |
| **Product classifier v1–v3** | `src/`, `serving/`, `deploy/`, `configs/`, `annotation/`, `notebooks/`, `tests/`, `pebble-finetuning-strategy-v3.md`, `progress.md` | Foundation code + chiến lược; dừng ở Phase 5, chưa train sản phẩm |

Những gì chương trình mới **kế thừa** từ đây: giao thức gold-holdout trung thực,
recipe weak-label nhiều-teacher + đo κ, kỷ luật provenance (số → log → kernel),
hạ tầng Kaggle pin-stack, và recall-floor cho distress head.

⚠ Code trong archive **không được bảo trì và không được lint/CI** (`extend-exclude`
trong `pyproject.toml`). Đường dẫn nội bộ trong các doc archive có thể đã lệch
sau khi di chuyển — đọc như tài liệu lịch sử, đừng chạy như hướng dẫn hiện hành.
