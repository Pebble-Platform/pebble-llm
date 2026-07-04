# M4b Implement Plan — Align YouTube caption ↔ pilot segments + đo chất lượng PhoWhisper

- **Executor:** Opus agent · **Ngày:** 2026-07-03 · **Người viết plan:** session chính
- **Goal:** tạo `transcripts_yt.csv` (text YouTube align theo timestamp cho 158 segment) +
  `m4b_wer_report.md` (đo chất lượng PhoWhisper-base so với YouTube reference) — trả lời
  open question "PhoWhisper-base đủ tốt hay cần -medium?" trong `docs/tasks/vn-tv-ser-pilot.md`.

## Bối cảnh 30 giây

Pipeline pilot đã cắt 1 tập phim thành 158 utterance (`segments.csv`) và transcribe bằng
PhoWhisper-base (`transcripts.csv`). User tải thêm caption YouTube của cùng tập
(`youtube_transcripts.txt`) — chất lượng text TỐT HƠN PhoWhisper (đúng dấu thanh, có dấu câu)
nhưng cắt theo block phụ đề ~5–9s, không theo utterance. Việc của bạn: khớp hai nguồn theo thời gian.

## Input (tất cả trong `data/vietnamese-ser/pilot/ep01/`)

1. **`segments.csv`** — `id,start,end,dur,clip` (158 dòng; start/end tính bằng GIÂY, float).
2. **`transcripts.csv`** — `id,start,end,text` (PhoWhisper, 158 dòng, cùng id).
3. **`youtube_transcripts.txt`** — 256 dòng, MỖI DÒNG một block. Format ĐẶC BIỆT, parse cẩn thận:
   - Dòng bắt đầu bằng `M:SS` rồi DÍNH LIỀN bản chữ dài của cùng mốc thời gian, rồi text.
   - Ví dụ thật (4 biến thể — regex phải qua CẢ 4):
     - `0:4242 seconds: Thế nào? Tốt chứ.` (chỉ seconds)
     - `1:031 minute, 3 seconds: Bác sao hôm nay...` (minute số ít + seconds)
     - `3:003 minutes, ấy nhờ bố nhiều ấy...` (minutes + KHÔNG có phần seconds, KHÔNG có dấu `:` trước text)
     - `35:0035 minutes, Con buôn bán...` (như trên, phút 2 chữ số)
   - Regex gợi ý: `^(\d+):(\d{2})` lấy start = M*60+SS; phần còn lại bỏ prefix
     `\d+ minutes?, ` (nếu có) rồi `\d+ seconds?: ` (nếu có) → còn lại là text. Strip.
   - Block `[âm nhạc]` / `[Vỗ tay]` (có thể viết hoa khác nhau) = KHÔNG phải thoại → đánh dấu non-speech.
   - **End của block = start của block kế tiếp** (caption liên tục); block cuối end = 2136s.
   - Sau khi parse: assert số block == 256, số block non-speech ≈ 29, start đơn điệu tăng.

## Các bước

### B1 — Script `scripts/vietnamese-ser/align_youtube.py`
CLI: `--pilot-dir data/vietnamese-ser/pilot/ep01` (default đó luôn). Python thuần + `rapidfuzz`
(chạy bằng `uv run --with rapidfuzz python ...`). **Windows gotcha bắt buộc:** dòng đầu `main()`
phải có `sys.stdout.reconfigure(encoding="utf-8")` — stdout cp1252 sẽ crash với tiếng Việt.

### B2 — Align
Với mỗi segment `[s,e]`: lấy mọi speech-block YouTube có overlap với `[s-1.0, e+1.0]`
(caption timing thô, cần tolerance ±1s). `text_youtube` = nối các block theo thứ tự, cách nhau 1 space.
Ghi số block dùng (`n_yt_blocks`). Segment không khớp block nào → `text_youtube` rỗng, `n_yt_blocks=0`.

### B3 — Đo chất lượng PhoWhisper vs YouTube
YouTube block dài hơn segment → so sánh phải là **infix matching**, KHÔNG phải WER trực tiếp
(WER trực tiếp sẽ phạt oan phần text YouTube thừa hai đầu). Làm 2 mức:
1. **Per-segment similarity:** normalize cả 2 vế (lowercase, bỏ dấu câu `.,?!…:"'-`, gộp
   whitespace — GIỮ dấu thanh tiếng Việt), rồi `rapidfuzz.fuzz.partial_ratio(text_youtube_norm,
   text_phowhisper_norm)` → cột `sim` (0–100). Chỉ tính khi cả 2 vế không rỗng.
2. **Proxy-WER trên tập sạch:** với các segment có `n_yt_blocks == 1` VÀ tỉ lệ độ dài từ
   `len(hyp_words)/len(ref_words)` trong [0.7, 1.3] (block ôm sát segment) → tính word-level
   `rapidfuzz.distance.Levenshtein.normalized_distance(ref_words, hyp_words)` = proxy-WER.
   Báo cáo n của tập sạch + mean/median.

### B4 — Outputs (đều trong pilot dir; KHÔNG commit — data/ gitignored)
1. **`transcripts_yt.csv`**: `id,start,end,text_phowhisper,text_youtube,n_yt_blocks,sim`
   (158 dòng, đúng thứ tự segments.csv; sim 1 chữ số thập phân, rỗng nếu không tính được).
2. **`m4b_wer_report.md`** gồm:
   - Thống kê parse: tổng block / speech / non-speech; coverage: bao nhiêu / 158 segment có ≥1 block.
   - Phân bố `sim`: mean, median, p10, p25; histogram chữ (bins 0-50/50-70/70-85/85-95/95-100).
   - Proxy-WER tập sạch (B3.2): n, mean, median.
   - **Bảng 15 segment sim thấp nhất**: id, sim, 2 text cạnh nhau (cắt 80 ký tự) — để người đọc thấy lỗi loại gì.
   - **Bảng riêng cho 8 đoạn đã flag ở M3** (`seg00010 seg00018 seg00034 seg00045 seg00049
     seg00105 seg00109 seg00148`): text PhoWhisper vs text YouTube — YouTube có cứu được không?
   - Verdict 3–5 câu: PhoWhisper-base đủ cho weak-label chưa, chỗ nào nên dùng text YouTube thay,
     có đáng chạy -medium không. NÊU RÕ caveat: YouTube caption cũng là ASR, không phải gold.

## Ràng buộc

- KHÔNG sửa `docs/tasks/*` (session chính giữ quyền ghi tracking doc). KHÔNG commit git.
- KHÔNG sửa các file có sẵn trong pilot dir — chỉ TẠO 2 file output mới + 1 script mới.
- Chạy mọi lệnh python với `PYTHONIOENCODING=utf-8`.

## Verify trước khi báo xong (bắt buộc)

1. `transcripts_yt.csv` đủ 158 dòng, id khớp thứ tự `segments.csv`.
2. Spot-check 3 mốc biết trước: (a) seg00009/seg00010 (143–155s) phải map vào vùng block
   `2:24`–`2:33` (nội dung "Ơ Thư hả cháu…"); (b) seg00034 (515–519s ≈ 8:35) phải nhận text
   YouTube quanh `8:34` ("Liệu hả? Hàng của tao ở đâu…") thay vì loop "hả hả hả";
   (c) seg00113 (~1380s ≈ 22:59) text YouTube phải chứa "mày không xứng đáng".
3. Coverage ≥ 90% segment có block (nếu thấp hơn → bug parse timestamp, tự sửa trước khi báo).
4. Script chạy lại idempotent (ghi đè output cũ, không crash).

## Báo cáo cuối (final message của agent)

≤15 dòng: coverage, mean/median sim, proxy-WER (n=?), 3 spot-check pass/fail, verdict 1 câu,
đường dẫn 2 file output + script.
