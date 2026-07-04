# Pebble-LLM — ViEmoSpeech

**ViEmoSpeech**: xây corpus cảm xúc giọng nói tiếng Việt đầu tiên đạt đủ 4 tiêu chí —
**nói tự do · đa lớp (+VA, +distress) · có lớp thanh điệu âm tiết · license rõ (CC-BY)** —
từ phim truyền hình VN, bằng pipeline đo lường được; và bài báo phương pháp
**tone×emotion bimodal SER** xây trên nó.

> Intent & ràng buộc cứng: [`docs/intent/constraints.md`](docs/intent/constraints.md) ·
> Quy trình làm việc: [`WORKFLOW.md`](WORKFLOW.md) ·
> Thiết kế corpus: [`docs/papers/vietnamese-ser/04-pioneer-corpus-design.md`](docs/papers/vietnamese-ser/04-pioneer-corpus-design.md) ·
> Kế hoạch scale: [`docs/papers/vietnamese-ser/05-scale-plan.md`](docs/papers/vietnamese-ser/05-scale-plan.md)
>
> **Pivot 2026-07-04:** các chương trình trước (text ordinal suicide-risk, voice
> crisis affect, product classifier v1–v3) đã đóng băng tại [`archive/`](archive/)
> — xem `archive/README.md`. Phương pháp luận của chúng (weak-label teachers +
> gold nhỏ chuẩn + honest gold-holdout + kỷ luật provenance) là nền của chương trình này.

## Pipeline (đã chứng minh trọn vẹn trên 1 tập phim — pilot ep01)

```
video tập phim
  → Demucs (tách nhạc) → silero VAD → cắt tại ranh giới đổi người nói (pyannote turn-split v2)
  → PhoWhisper ASR + align YouTube caption
  → 2 LLM teacher gán nhãn (emotion 7 lớp + V/A + distress) + flag đa-giọng-theo-text
  → weak pool: clip đơn-giọng-verified + nhãn + speaker id
```

Số đo pilot (tập 35.6′): **155 utterance sạch / 8.6 phút**; κ 2-teacher **0.697**;
điểm mù diarization đo được **11.4%**. Chi tiết: `docs/tasks/vn-tv-ser-pilot.md`.

## Cấu trúc

| Đường dẫn | Vai trò |
|---|---|
| `docs/intent/` | Ràng buộc bất biến (I1–I6): media không bao giờ vào git/release, provenance nhãn, đơn-giọng, speaker-disjoint |
| `docs/papers/vietnamese-ser/` | Scoping research + corpus design + scale plan |
| `docs/tasks/` | Tracking docs + các implement plan đã thực thi (provenance) |
| `scripts/vietnamese-ser/` | Pipeline local (extract / align / weak-label / prompt versioned) |
| `kaggle/vietnamese-ser/` | Kernel batch GPU (P100, stack pin) |
| `archive/` | Các chương trình tiền nhiệm, đóng băng — không lint, không sửa |

## Chạy

```powershell
# env tooling
uv sync --dev && make check

# env pipeline (một lần) — xem scripts/vietnamese-ser/README.md
uv venv .venv-vnser && .venv-vnser\Scripts\activate
uv pip install demucs silero-vad "transformers[torch]" soundfile pyannote.audio

# pilot 1 tập
make pilot-extract EP=data/vietnamese-ser/raw/ep01.mp3 HF_TOKEN=hf_xxx
```

**Media tập phim và mọi output audio nằm trong `data/**` (gitignored) — không bao giờ commit.**
