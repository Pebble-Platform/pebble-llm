# Pilot: cắt thoại sạch từ phim truyền hình VN cho corpus SER

- **Slug:** vn-tv-ser-pilot
- **Status:** in-progress
- **Created:** 2026-07-03  ·  **Updated:** 2026-07-03
- **Owner:** user / Claude

## Goal
Chạy pilot kỹ thuật trên **1 tập phim truyền hình VN** để đo **sản lượng thoại sạch
thực tế** (yield): từ 1 tập ~45 phút thu được bao nhiêu phút utterance đơn-người-nói
2–10s kèm transcript. Con số này quyết định GO/NO-GO cho việc xây corpus từ nguồn
phim dài tập (thay số ước lượng "30–50 phút/100 phút" trong
`docs/papers/vietnamese-ser/04-pioneer-corpus-design.md`).

## Requirements & Constraints
- **Functional:** pipeline video → audio → tách nhạc (Demucs) → VAD (silero) →
  cắt utterance 2–10s → PhoWhisper transcript → báo cáo yield. Diarization
  (pyannote) là tầng tùy chọn (model gated, cần HF token).
- **Constraints:** file phim + audio đầu ra **không bao giờ commit** (nằm trong
  `data/**` gitignored — cùng chính sách clinical data). Máy user không có GPU →
  pipeline phải chạy được CPU cho 1 tập (chậm chấp nhận được); scale sau này
  chuyển Kaggle. Không phát hành audio thô ra ngoài (phương án B design doc §4).

## Milestones
- [x] M1 — Pilot script + README — chạy được từng stage, cache theo stage.
- [x] M2 — `ep01.mp3` (phim gia đình VN, 35.6 phút) → chạy full pipeline OK, exit 0.
- [x] M3 — Báo cáo yield: **33%** (11.9/35.6 phút), 158 utterance, median 3.9s;
  transcript 158/158 có chữ (0 rỗng), đọc mẫu ~18 đoạn: thoại hội thoại mạch lạc.
- [x] M3-đánh giá đầy đủ (2026-07-03, đọc cả 158 + phân tích định lượng): **PASS**.
  Text: 6/158 (3.8%) loop-hallucination (Whisper lặp vô hạn trên tiếng CƯỜI/KHÓC
  — seg00034 "hả…", seg00105 "hớ…", seg00049, seg00109, seg00148; + seg00010
  borderline nói lắp thật) + 2 `unk` — TẤT CẢ bắt tự động được bằng rule
  `max_run≥5 | chars/s>28 | TTR<0.3`; lọc xong giữ **11.3/11.9 phút (95%)** →
  yield hiệu dụng ~32%. Tốc độ nói clean median 3.9 từ/s (p10–p90: 2.6–5.3) =
  chuẩn hội thoại. Audio: RMS median −25.3 dBFS (p10–p90: −28…−22), **0 clip
  clipping, 0 clip quá nhỏ** — mức âm đồng đều sau Demucs. Nội dung: đa dạng
  cảm xúc thật (giận dữ seg00063–67/113–114 · hoảng loạn seg00051 · lo âu
  57–58 · đau buồn · cười · đe dọa 139–152 · tán tỉnh 129–138). 2 vấn đề mang
  sang M4/M5: (a) **nhiều utterance chứa 2 lượt nói Q&A** (chưa diarization) —
  nhãn cảm xúc "của ai?" → cần pyannote khi scale; (b) **ASR sai THANH ĐIỆU
  đúng ở đoạn cảm xúc mạnh** (seg00113/114: "mày→máy/mây, tao→tháo" khi quát) —
  rủi ro nhánh text bị nhiễu hệ thống ở high-arousal, đồng thời là bằng chứng
  sớm cho chính giả thuyết tone×emotion của paper.
- [ ] M4 — (nếu yield ≥ ~25%/tập) weak-label thử 1 tập bằng LLM trên transcript → đo phân bố nhãn.
- [x] M5 — CHUẨN BỊ scale xong (2026-07-03, Opus agent theo
  `docs/tasks/m5-scale-implement-plan.md`; verify độc lập: metadata JSON hợp lệ,
  kernel compile OK, số học khớp): `docs/papers/vietnamese-ser/05-scale-plan.md`
  (3 kịch bản; khuyến nghị **P1 = 3 bộ/120 tập → 23.8h thoại sạch/~18k utt
  ≈ 7.5× ViSEC**; 36 GPU-h ≈ 2 tuần quota; label 2-teacher ~$22 Batch API;
  target cũ "50–100h" = 250–500 tập → không khả thi, đã sửa §3 design doc thành
  target v2 chờ chốt) + kernel `kaggle/vietnamese-ser/vnser-extract/` (pin torch
  2.5.1/pyannote 3.x, HF token qua Kaggle Secrets, smoke 60s local PASS, CHƯA
  push) + shortlist 8 phim (top-3: Sống chung với mẹ chồng 34t · Về nhà đi con
  85t · Gạo nếp gạo tẻ 109t — đều chỉ có caption auto/ASR).
  ⚠ Chờ USER quyết: (a) chốt kịch bản P1?, (b) phương án compute — upload media
  lên Kaggle private dataset (rủi ro pháp lý bên-thứ-ba, nêu ở 05 §rủi ro) hay
  local GPU; (c) 0.30 GPU-h/tập là ước lượng — batch Kaggle đầu sẽ chốt số thật.

## Decision Log
- **2026-07-03 — pyannote 4.x: `token=` + đưa waveform in-memory, né torchcodec:**
  pyannote.audio 4.x (a) bỏ kwarg `use_auth_token` → dùng `token=`; (b) decode
  file bằng torchcodec — DLL không load trên máy này (cùng gốc FFmpeg full_build
  như vụ demucs). Fix trong `stage_diar`: `sf.read` → `pipe({"waveform": tensor,
  "sample_rate": sr})` (không cho pyannote tự đọc file), và
  `getattr(diar, "speaker_diarization", diar)` phòng 4.x đổi kiểu output.
  Rejected: hạ pyannote <4 (kéo theo xung đột torch/torchaudio đã pin).
- **2026-07-03 — Fix crash cuối run trên Windows (`print(report)`):** report chứa
  ký tự tiếng Việt (`ổ` `ư`…) → stdout cp1252 của Windows raise
  `UnicodeEncodeError`, làm script exit 1 DÙ mọi output đã ghi xong (report.md
  ghi bằng utf-8 ở dòng trước). Thêm `sys.stdout.reconfigure(encoding="utf-8")`
  đầu `main()` (`pilot_extract.py:183`). Rejected: bọc try/except quanh print
  (giấu lỗi, không fix gốc). Khi tự chạy script kiểm tra tiếng Việt cũng cần
  `PYTHONIOENCODING=utf-8`.
- **2026-07-03 — Audio I/O qua `soundfile` shim, KHÔNG dùng torchcodec:**
  torchaudio 2.11 (venv `.venv-vnser`, cặp torch 2.12.1) đã bỏ backend I/O nội bộ
  và ủy thác toàn bộ cho `torchcodec`, làm `demucs` (torchaudio.save) và `silero`
  (torchaudio.load) chết với `ModuleNotFoundError: torchcodec`. Đã thử cài
  torchcodec 0.14.0 → DLL `libtorchcodec_core8.dll` không load được vì FFmpeg trên
  máy là bản `full_build` tĩnh (không có shared DLL avcodec/avformat…). Chọn shim
  `torchaudio.load/save` → `soundfile` (đã có sẵn trong venv, gói kèm libsndfile,
  không cần FFmpeg): `scripts/vietnamese-ser/sitecustomize.py`, kích hoạt bằng
  `PYTHONPATH=scripts/vietnamese-ser` (Python tự import `sitecustomize` lúc khởi
  động → phủ cả tiến trình con demucs, không sửa `pilot_extract.py`). Rejected:
  (a) cài FFmpeg shared DLL + set PATH cho subprocess — nhiều mắt xích, dễ vỡ;
  (b) hạ torchaudio < 2.9 — kéo theo hạ torch, rủi ro vỡ demucs/transformers 5.12.
- **2026-07-03 — Nguồn = phim truyền hình dài tập (user chốt):** thoại dày, nhạc
  thưa hơn điện ảnh, một bộ 30–40 tập giải bài toán quy mô. Rejected: phim điện
  ảnh (yield thấp, nhạc nền dày), phim lồng tiếng (giọng đọc đè cảm xúc gốc).
- **2026-07-03 — VAD mặc định = silero, diarization pyannote là opt-in:** silero
  không gated, nhẹ, đủ cho đo yield; pyannote/speaker-diarization-3.1 gated (cần
  HF token + accept điều khoản) → bật bằng `--hf-token` để đo thêm độ thuần
  đơn-người-nói. Rejected: bắt buộc pyannote ngay (chặn pilot vì thủ tục token).
- **2026-07-03 — Cắt utterance từ stem vocals (sau Demucs), không từ audio gốc:**
  mục tiêu là thoại sạch cho SER; giữ cả đường dẫn audio gốc trong metadata để
  sau này cắt lại nếu cần (Demucs có thể để artifact). `--cut-source original`
  để so sánh.
- **2026-07-03 — Venv riêng `.venv-vnser`:** demucs/pyannote/transformers nặng và
  dễ conflict; không đụng venv chính của repo (theo pattern `.venv-voice` có sẵn).

## Open Questions
- [x] Yield thực tế ≥ 25%/tập không? → **CÓ: 33%** trên ep01 (M2–M3). GO.
- [x] PhoWhisper-base đủ tốt trên thoại phim hay cần -medium? → **ĐÓNG (M4b,
  2026-07-03): base đủ.** Similarity vs YouTube mean 87.2/median 90.5; lỗi tập
  trung ở ~14 đoạn sim<70 (loop cười/khóc + quát sai thanh điệu) — vá bằng cột
  `text_youtube` trong `transcripts_yt.csv` thay vì đổi model ASR. Khi scale:
  bộ nào có YouTube caption thì luôn tải kèm (nguồn text tốt hơn, miễn phí).
- [ ] Demucs artifact có làm hỏng đặc trưng âm học cảm xúc không? → so sánh
  `--cut-source vocals` vs `original` ở M4 (nghe mẫu + teacher disagreement).

## Completed Work
- 2026-07-03 — M1: `scripts/vietnamese-ser/pilot_extract.py` (pipeline 5 stage,
  cache từng stage, chạy lại an toàn) + `scripts/vietnamese-ser/README.md`
  (setup `.venv-vnser`, ffmpeg, HF token, thời gian chạy CPU dự kiến).
- 2026-07-03 — Gỡ blocker torchcodec: `scripts/vietnamese-ser/sitecustomize.py`
  shim `torchaudio.load/save` → `soundfile`; chạy pipeline bằng
  `PYTHONPATH=scripts/vietnamese-ser python … pilot_extract.py`. Đã xác nhận
  demucs (subprocess) chạy qua stage tách nhạc không còn lỗi torchcodec.
- 2026-07-03 — M2+M3 XONG: chạy full pipeline `ep01.mp3` → exit 0.
  Output `data/vietnamese-ser/pilot/ep01/`: `report.md` (yield **33%**, 11.9/35.6
  phút, 158 utterance median 3.9s), `segments.csv`, `clips/` (158 wav 16 kHz),
  `transcripts.csv` (158/158 có chữ). Fix crash cuối run (stdout utf-8,
  `pilot_extract.py:183`). Chưa chạy pyannote diarization (không có `--hf-token`).

- [x] **Turn-aware cutting v1→v2 XONG (2026-07-03, 2 vòng Opus theo
  `turn-split-implement-plan.md` + `turn-split-v2-implement-plan.md`; verify độc lập khớp):**
  v1 (cắt toàn cục tại VAD∩turns) lợi ích ròng = 0 — yield sụp 11.9→5.5 phút vì
  3 bệnh đo được: turns vụn (895 turns, avg 1.13s), lỗ "" phá chuỗi X-""-X
  (vùng đơn co 5.5→3.4), MIN_UTT=2.0 giết câu đáp ngắn. v2 fix T1–T4 (premerge
  turns <0.6s · region đơn-speaker giữ nguyên · nhập lỗ "" vào hàng xóm, DROP
  là barrier · MIN_UTT_TURN=1.5) → **175 utt / 10.3 phút đơn-giọng-verified**
  (vùng đơn phục hồi đủ 5.53 + cứu 4.73/6.4 phút đa-giọng = **+87% material
  đơn-giọng so với chỉ lọc baseline**). Kernel scale: turn-split default BẬT
  khi có HF_TOKEN. **Hệ quả scale P1 (120 tập): ~20.6h / ~21k utt đơn-giọng** —
  gần giữ nguyên ước tính 23.8h của 05-scale-plan. Output verify:
  `ep01-turnsplit2/` (v1 giữ ở `ep01-turnsplit/` làm chứng cứ so sánh).

- 2026-07-04 — Tải dữ liệu scale (Về nhà đi con):
  `scripts/vietnamese-ser/download_youtube.py` (yt-dlp, cài trong `.venv-vnser`).
  Map số tập từ TITLE (`Tập N`), KHÔNG theo playlist-index — playlist này **đảo
  ngược** (index 1 = Tập 85 … index 85 = Tập 01), `--playlist-items 2-10` sẽ sai.
  Đã tải **Tập 02–10** → `data/vietnamese-ser/raw/ve-nha-di-con/epNN.mp3` (+ VN
  caption `epNN.vi.srt` — series NÀY CÓ phụ đề vi thật, nguồn text tốt hơn
  PhoWhisper, khớp quyết định M4b) + `.download-archive.txt` (resume). exit 0,
  9/9 mp3 + 9/9 srt. Lưu ý: Tập 01 = `ep01.mp3` đã xử lý = video `8U5jz8uE2bA`.

- [x] **M4c XONG (2026-07-04) — weak-label vòng 2 + text-filter điểm mù diarization
  (báo cáo: `ep01-turnsplit2/m4c_report.md`):** prompt v2 thêm
  `multi_speaker_suspect` (LLM đọc ngữ nghĩa lượt lời, có anti-pattern "mày/tao
  một người quát"); ASR 175 clip (fix torchcodec sync từ kernel về
  `pilot_extract.py`) + align YouTube (bỏ hardcode 158). Kết quả:
  **κ vòng 2 = 0.697 (từ 0.584)** — xác nhận định lượng turn-split cải thiện chất
  lượng đơn vị dữ liệu; **điểm mù diarization đo được: 20/175 = 11.4%** (OR 2
  teacher; Opus nhạy hơn 19 vs 7); **weak-pool ep01 sạch cuối: 155 utt / 8.6
  phút** (đơn-giọng audio + text-verified + nhãn 2 teacher). Distress đồng thuận:
  4 đoạn. Chiếu P1: **~18.6k utt train-ready / ~17h** sau mọi tầng lọc.

- 2026-07-05 — Tải bộ 2 (Chạy Trốn Thanh Xuân): tổng quát
  `download_youtube.py` sang **numbering `Tập X.Y`** (key = tuple `(tập, phần)`,
  chọn range bằng so sánh tuple → `1.1-3.2` phủ đúng 8 video kể cả 1.3/2.3; range
  int `2-10` cũ vẫn chạy). Tải **Tập 1.1–10.2** → `chay-tron-thanh-xuan/epNN_P.mp3`
  (22/22 mp3 + 22/22 srt vi). Playlist cũng đảo ngược (1.1 ở cuối) — map theo
  title xử lý tự động. Phần ngắn (~13–22 phút/video). Từ Tập 3 mỗi tập có 2 phần.
- 2026-07-05 — Fix YouTube **HTTP 403** + làm `download_youtube.py` chịu lỗi:
  giữa batch 4.1–10.2, video ep08_2 bị `403 Forbidden` ở luồng audio (yt-dlp báo
  "extractor specified to use impersonation, but no target available" vì thiếu JS
  runtime). Cài **`curl_cffi`** vào `.venv-vnser` → yt-dlp có target giả lập
  trình duyệt, retry qua ngay. Đồng thời: vòng lặp tải giờ **bắt lỗi từng video,
  bỏ qua + báo cuối** (một video hỏng không giết cả batch — quan trọng cho scale
  120 tập) + `--retries 10`. Chạy lại (archive skip 9 video đã xong) → đủ 22/22.

## Remaining Action Items
- [ ] Chạy pipeline cho Tập 02–10 (`ve-nha-di-con/epNN.mp3`) — cân nhắc dùng
  `--turn-split --hf-token` + nạp `epNN.vi.srt` làm nguồn text thay ASR.
- [ ] Chạy pipeline cho `chay-tron-thanh-xuan/epNN_P.mp3` (22 phần, 1.1–10.2).
- [x] ~~User đặt tập vào `data/vietnamese-ser/raw/`~~ → `ep01.mp3` đã có, chạy xong.
- [x] ~~Chạy `pilot_extract.py` → report.md~~ → yield 33%, GO.
- [x] ~~Đọc mẫu ~20 đoạn~~ → transcript mạch lạc, ghi vào M3 / Open Questions.
- [ ] **(tùy chọn) Nghe** 5–10 clip wav để xác nhận độ sạch âm thanh sau Demucs
  (yield số đã đạt; nghe để kiểm artifact trước khi cam kết scale).
- [ ] **M4-chuẩn bị (mới, 2026-07-03):** user đã tải `youtube_transcripts.txt`
  (256 block; ~227 có chữ + 29 `[âm nhạc]/[Vỗ tay]`). So sánh cho thấy YouTube
  auto-caption **tốt hơn PhoWhisper-base rõ rệt** (bắt đúng "mày/tao" chỗ
  seg00113 sai thanh điệu; có thoại thật ở chỗ seg00034 loop). Việc: script
  align block YouTube ↔ 158 segment theo timestamp overlap → (a) text sạch hơn
  cho weak-label, (b) tính **WER PhoWhisper vs YouTube** (trả lời open question
  base-vs-medium), (c) thay text 8 đoạn flagged. Lưu ý: YouTube caption cũng là
  ASR (không phải gold), timestamp mức block. Chênh 158 vs 227: ta chỉ cắt thoại
  sạch 2–10s sau tách nhạc (11.9 min) vs caption phủ cả thoại-đè-nhạc (~26 min)
  — by design; muốn vớt thêm thì nâng model Demucs, không phải sửa VAD.
- [x] **M4a — weak-label 2 teacher XONG (2026-07-03):** Opus + Sonnet qua Claude Code
  subagent (không cần API key; prompt versioned `scripts/vietnamese-ser/m4_prompt.md`;
  scale sau này dùng `m4_weak_label.py` + Batch API). Kết quả `.../ep01/m4_report.md`:
  **κ=0.584**, raw 69%, |Δvalence|=0.24, distress-agree 98%. Phân bố đa dạng
  (anger/fear/joy/sadness đều có mặt — phim gia đình cho phổ cảm xúc như kỳ vọng).
  Phát hiện: bất đồng có hệ thống (28/49 = Opus-neutral → Sonnet-emotion) = lệch
  ngưỡng, không lệch loại — đo được, hiệu chỉnh được. 109 nhãn đồng thuận = silver;
  49 bất đồng = ứng viên gold (disagreement sampling).
- [x] **Diarization ep01 XONG (2026-07-03, pyannote community-1 qua 3 cửa gated):**
  **86/158 (54%) đơn-người-nói** · 56 đoạn 2 giọng · 14 đoạn 3 giọng · 2 đoạn 4 giọng;
  **18 giọng** trong tập. ⚠ **Caveat trung thực:** 54% là ước lượng LẠC QUAN —
  ví dụ đối chứng: seg00010 (hội thoại cô↔Thư, 2 giọng nữ) bị gộp thành 1
  speaker (SPEAKER_17, cụm lớn nhất 67 lần xuất hiện — nghi "cụm hút" gộp nhiều
  giọng nữ giống nhau). Giọng nữ tương tự trong phim gia đình là failure mode
  chính của embedding clustering. → Hướng xử lý: (a) cắt theo speaker-turn vẫn
  đáng làm cho 72 đoạn multi-speaker đã phát hiện; (b) **text-turn splitting
  (LLM đọc xưng hô cô/cháu trên YouTube text) bắt được đúng chỗ audio mù** —
  củng cố thiết kế kết hợp 2 nguồn; (c) thử `min/max_speakers` + threshold khi scale.
- [x] **M4b — align YouTube XONG (2026-07-03, Opus agent theo plan
  `docs/tasks/m4b-align-youtube-plan.md`; verify độc lập pass):**
  `align_youtube.py` + `transcripts_yt.csv` (158/158 coverage 100%, 0 rỗng) +
  `m4b_wer_report.md`. Similarity PhoWhisper↔YouTube: mean **87.2**, median 90.5
  (p10 71.8); proxy-WER tập sạch (n=10): **~0.31**. Spot-check: seg00034 nhận
  được thoại thật thay loop (sim 41.6 → tự tố cáo đoạn hỏng); seg00113 chứa
  "mày không xứng đáng". **Kết luận:** PhoWhisper-base đủ cho weak-label mức
  utterance; **không cần -medium**; dùng cột `text_youtube` vá các đoạn sim thấp
  (<70 ≈ 14 đoạn). Caveat giữ nguyên: YouTube cũng là ASR, không phải gold.
- [ ] **M4c (tùy chọn):** gán nhãn lại 2-teacher trên `text_youtube` → so κ với
  vòng PhoWhisper; so sánh `--cut-source vocals` vs `original` cho câu hỏi artifact.
- [ ] **M5:** quyết định scale (số tập/bộ, port Kaggle) + cập nhật số thật (33%)
  vào `docs/papers/vietnamese-ser/04-pioneer-corpus-design.md`.

## Scale batch chuẩn bị (2026-07-04)
- **Dataset layout v2 (series-based):** `raw/<series>/epNN.*` ·
  `episodes/<series>/epNN/` (canonical ep01 = bản turn-split v2 + labels r2,
  chuyển từ `pilot/ep01-turnsplit2`) · `_pilot-history/` (ep01 baseline +
  turn-split v1 + smoke — bằng chứng so sánh). Media ep02–ep10 + caption `.vi.srt`
  đã tải đủ (`download_youtube.py` của user, series **Về nhà đi con**).
- **`run_batch.py` mới:** chạy tuần tự resumable ep02–ep10; convert SRT→caption
  với auto-detect kiểu rolling của YouTube auto-sub (test ep02: 536 block,
  0 trùng liền kề); dry-run ep01 → skip đúng, summary.csv chuẩn (175/10.3′/175).
- **Open question mới — recap giữa các tập:** ep02 mở đầu bằng recap cảnh ep01
  (trùng nguyên văn thoại). Khi gộp corpus cần cơ chế khử trùng lặp xuyên tập
  (text-match giữa các ep liền kề, hoặc bỏ ~90s đầu mỗi tập) — quyết ở batch 1.

## Labeling ep02–05 + Kaggle dataset pilot (2026-07-05)
- **8 subagent (Opus+Sonnet × ep02–05) gán nhãn xong**, 877 utt tổng (cùng ep01):
  κ theo tập = 0.697 / 0.554 / 0.485 / 0.513 / 0.650 (mean ~0.58 — dao động theo
  nội dung tập; so sánh cùng-tập ep01 0.584→0.697 vẫn là bằng chứng turn-split);
  OR-flag đa-giọng 55/877 (6.3%) → **clean 822 (94%)**; consensus emotion 627 (72%);
  distress OR 24. Pattern lặp: Opus flag nhạy hơn Sonnet (vd ep05: 9 vs 0).
- **Kaggle dataset PRIVATE đã push:** `phatneurondai/viemospeech-pilot`
  (877 clips 16kHz + manifest.csv hợp nhất [2 teacher + consensus + is_clean]
  + README; script: `scripts/vietnamese-ser/build_kaggle_dataset.py`).
  Media là derivative có bản quyền → intent I1: KHÔNG BAO GIỜ chuyển public.
- Còn lại: ep06–08 đã extract chưa label; ep09–10 đang extract (detached batch);
  bước kế: kernel training pilot (WavLM probe trên is_clean + emotion_consensus).

## Corpus 10 tập hoàn chỉnh + Kaggle dataset v2 (2026-07-05)
- **Extract batch 10/10 xong** (detached run): 1,638 utt / 92.9 phút đơn-giọng,
  trung bình 164 utt / 9.3 phút/tập (range 123–212). Chiếu P1-120 tập:
  ~19.7k utt / 18.6h → ~18.5k clean — khớp dự phóng ep01.
- **Label 2-teacher đủ 10/10 tập** (18 subagent tổng): 1,638 utt →
  **clean 1,555 (95%)** · consensus 1,198 (73%) · distress-OR 71.
  κ per-tập 0.485–0.697, **mean 0.610**. Phân bố consensus-clean:
  neutral 581 · anger 239 · joy 135 · sadness 98 · fear 68 · disgust 6 · surprise 4
  (2 lớp hiếm — sẽ là thách thức train, đúng kỳ vọng phim gia đình).
  ep08 = tập giàu distress nhất (cha bạo hành: Opus 16 vs Sonnet 17 — hội tụ độc lập).
- **Kaggle dataset v2 đã push:** `phatneurondai/viemospeech-pilot` (PRIVATE) —
  1,638 clips + manifest hợp nhất. Sẵn sàng cho kernel training pilot.

## Định nghĩa "tập hoàn thành" (user chốt, 2026-07-05)
Một tập/phần chỉ được tính HOÀN THÀNH khi đủ CẢ BA: (1) extract (segments +
clips + transcripts), (2) align caption (`transcripts_yt.csv`), (3) **label
2-teacher validate xong** (`labels_opus.csv` + `labels_sonnet.csv` đủ dòng,
đúng enum). Extract-xong-chưa-label = "đang làm dở". Vận hành: label rolling —
phần nào extract xong thì spawn 2 teacher ngay, không đợi trọn batch.

## Series 2 "Chạy trốn thanh xuân" — rolling progress (2026-07-05)
- Raw đủ 22 phần (ep01_1→ep10_2, mỗi tập 2–3 phần). `run_batch --episodes all`
  (discovery mode mới). Sự cố ep01_1 (ffmpeg mồ côi từ dry-run → wav cụt →
  cache trap) đã dọn + vá atomic-write (`d2fa456`).
- **5 phần đầu HOÀN THÀNH theo tiêu chí mới** (extract+align+label validated):
  380 utt · clean 341 (90%) · consensus 295 (**78%** vs 73% series 1) ·
  **κ mean 0.675** (0.642–0.720 — CAO hơn series 1: 0.610) · distress-OR 10.
  Mật độ thoại cao hơn (~5.5 vs ~4.6 utt/phút); phổ cảm xúc "nóng" hơn
  (anger/joy nhiều hơn, neutral ít hơn) — đúng giá trị đa dạng hóa của series 2.
- Đang chạy: extract ep03_1/03_2 (batch detached) → sau đó relaunch vét
  ep01_1 + ep04_1→ep10_2; label rolling theo watcher.
