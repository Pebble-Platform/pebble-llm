## ADR-002 — Test set speaker-disjoint theo whole-series (không per-speaker / per-episode)

**Date:** 2026-07-07 · **Status:** proposed (phương pháp đã chốt; series cụ thể
còn mở). **Resolves:** `tools/labeler/SPEC.md` lỗ spec #1; invariant I4.

> **Khung sau [ADR-003](ADR-003-human-labels-drop-weak-supervision.md):** bỏ
> weak-supervision ⇒ hết phân biệt "gold vs weak pool". ADR này đọc là
> **test-split vs train-split** của corpus toàn-human; core (hold-out
> whole-series) không đổi.

**Context:** I4 đòi *test speakers ∩ train speakers = ∅* và splits
speaker-disjoint. Nhưng `speaker_id` trong pipeline là nhãn **diarization
per-episode-local** của pyannote, KHÔNG phải danh tính diễn viên toàn cục: cùng
một diễn viên tái xuất dưới id khác ở tập khác, và một cluster có thể hút nhiều
giọng khác nhau ("cụm hút", `docs/tasks/vn-tv-ser-pilot.md:198-207`). Vì vậy:
- Hold-out theo **bare `speaker_id`** sẽ **pass giả** — check disjoint xanh trong
  khi cùng giọng thật rò vào cả train lẫn test.
- Hold-out theo **episode** cũng không đủ — dàn cast chính của phim TV xuất hiện
  ở *mọi* tập cùng series; giữ ep09 để test còn train ep01–08 vẫn lộ chính diễn
  viên đó.

**Decision:** **hold out nguyên một (hoặc nhiều) series** làm **test set**; series
đó **không** được đưa vào train. Disjointness được bảo đảm **theo cấu trúc** ở
mức series, khỏi cần resolve danh tính chéo-tập.
- Audit unit = khoá phức **`(series, ep, speaker_id)`**; `state.jsonl` mang
  `speaker` (+ `series`, `episode`) → `tests/invariants/test_speaker_disjoint.py`
  (I4, chưa tồn tại; thuộc change 001) assert được.
- Kích thước: sàn **≥50 clip ở lớp emotion hiếm nhất**, target **80–100** trước
  khi báo per-class UAR/macro-F1 (binomial CI trên macro-F1: n≈44→±13pp,
  n≈80–100→~±9–10pp). Có thể dùng bất đồng teacher-gợi-ý để **ưu tiên** clip
  annotate trước, nhưng **backfill cân bằng lớp** — không để sampling quyết định
  phân bố lớp cuối.

**Evidence:**
- MSP-Podcast (SER benchmark lớn nhất) — partition Test2 hold out nguyên **117
  show**, loại mọi segment của các show đó khỏi phần còn lại, đúng để né việc
  resolve speaker per-segment ([arXiv:2509.09791](https://arxiv.org/html/2509.09791v1)).
- IEMOCAP leave-one-session-out; leakage do random utterance-split ghi nhận ở
  ~50% nghiên cứu IEMOCAP cũ ([arXiv:2307.10814](https://arxiv.org/pdf/2307.10814)).
- Sàn N/lớp: binomial CI trên macro-F1 ([Applied Intelligence 2021](https://link.springer.com/article/10.1007/s10489-021-02635-5));
  EMO-DB (7 lớp, lớp hiếm nhất n≈44) vẫn được coi là đủ dùng.

**Consequences:**
- Labeler ghi `series/episode/speaker` vào `state.jsonl` (cột `speaker` đọc từ
  `transcripts.csv`, header `id,start,end,dur,speaker,clip` — fix #1 đã áp dụng).
- Build corpus/train (`build_kaggle_dataset.py`) phải **loại series test** khỏi
  train — ràng buộc chưa thực thi.
- **Quyết định của người (scope, chưa chốt):** series nào làm test set; kế hoạch
  P1 (3 series) có chừa sẵn 1 series không dùng để train không.
- **Rủi ro chưa verify:** giả định các series khác nhau không chung diễn viên.
  Mitigation rẻ: liếc credits/cast của series test vs series train trước khi chốt,
  thay vì tin vào id. Nếu series test lệch phân bố emotion (vd không có cảnh giận),
  kéo thêm tập từ *cùng* series test — vẫn an toàn I4, chỉ tốn annotation hơn.
