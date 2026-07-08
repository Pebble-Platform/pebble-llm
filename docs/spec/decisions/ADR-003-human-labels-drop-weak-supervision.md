## ADR-003 — Bỏ weak-supervision: nhãn HUMAN là nguồn sự thật (teacher chỉ còn gợi ý)

**Date:** 2026-07-07 · **Status:** accepted (quyết định user) — *các sửa intent
kéo theo đang CHỜ human apply, xem cuối*.
**Resolves:** quyết định user 2026-07-07 ("label model không dùng nữa, lấy human
làm chuẩn, human toàn bộ — do độ chính xác"). **Supersedes** khung
weak-supervision của repo. **Ràng buộc:** đây là thay đổi **intent-layer**.

**Context:** pipeline hiện gán nhãn weak bằng 2 LLM teacher (Opus/Sonnet) rồi
giữ một gold nhỏ để eval. User đánh giá độ chính xác nhãn teacher không đủ và
quyết định **con người gán nhãn toàn bộ corpus**; nhãn teacher thôi làm nhãn
huấn luyện/tham chiếu. Đây đổi bản chất đóng góp: từ "weak-label + gold nhỏ +
honest weak-supervision" → **"corpus SER tiếng Việt gán nhãn người, đa lớp,
tone-annotated, CC-BY"** — sạch/dễ phòng thủ hơn, đổi lại **nhỏ hơn** (chi phí
hand-label tuyến tính theo số clip).

**Decision:**
1. **Nhãn human là nguồn sự thật duy nhất** (emotion/V/A/distress/multi +
   `gold_text`). Nhãn 2-teacher **không còn** là nhãn train hay reference eval.
2. **Teacher giữ lại CHỈ như gợi ý** (mờ, read-only, **không pre-fill**) trong
   labeler để tăng tốc; human luôn tự quyết. Pipeline `m4_weak_label.py` giữ để
   sinh gợi ý cho tập mới.
3. **Single-pass** (1 annotator/clip) ở giai đoạn này; **chưa đo κ human–human**
   (known gap, ghi rõ — không giấu).
4. Corpus thành **toàn human**; split **train/dev/test đều human**, vẫn
   **speaker-disjoint** ([ADR-002](ADR-002-whole-series-speaker-disjoint-gold.md)
   sống, đổi khung "gold vs weak" → "test-split vs train-split").

**Consequences (bán kính ảnh hưởng):**

| Chết | Còn nguyên | Đổi ý nghĩa |
|---|---|---|
| 2-teacher là nhãn (m4 làm label source), khái niệm weak pool, cờ OR 2-teacher | **§1 Media legality** | Gold set → **chính là corpus** |
| **§4 Honest weak-supervision**; **I6** (κ teacher ≠ accuracy; cấm train+eval cùng label-source) | **§2/I3 Single-speaker**, **§3/I4 Speaker-disjoint** (về *data*, không về *label* → sống) | Provenance §5: `annotator id + ts` thay `model id`; chất lượng nhãn đo bằng **κ human–human** (khi làm) |

- **[ADR-001](ADR-001-blind-gold-annotation.md) bị superseded phần lớn:** tiền
  đề "leakage vì gold chấm chính teacher" biến mất (teacher không còn bị chấm).
  Còn lại là **caveat chất lượng**: hiện gợi ý teacher (dù mờ, không pre-fill)
  vẫn có thể *neo* nhãn human (Schroeder ACL 2025: chỉ cần *hiển thị* đã kéo
  overlap 40%→81–87%). ⇒ **nếu sau này báo teacher như một baseline SER**, so
  sánh đó **không hợp lệ** vì nhãn human đã bị neo — phải ghi rõ.
- **Known gaps (ghi, không giấu):** (1) single-pass ⇒ **chưa có số độ tin cậy
  nhãn** (κ/α human–human) để báo trong paper; (2) anchoring caveat ở trên.
  - *Khi double-annotate (further work):* metric = Cohen's κ (2 rater, emotion
    categorical), Fleiss' κ (≥3), **weighted κ / Krippendorff's α ordinal** cho
    V/A 1–5; annotator mù nhau; gold nhỏ ⇒ double toàn bộ hay subset lớn cố định.
    Refs: Artstein & Poesio, *Comput. Linguistics* 2008
    ([J08-4004](https://aclanthology.org/J08-4004/)); Mathet et al., EACL 2014
    ([E14-1058](https://aclanthology.org/E14-1058/)).
- **Scale = quyết định ngân sách:** ~3611 utt hiện có → ~15–30 h/annotator/pass;
  18k utt → ~75–150 h. **Cần chốt corpus-size mục tiêu** theo người thật.

**Sửa intent kéo theo (ĐỀ XUẤT — chờ human apply, không tự sửa):**
- `docs/intent/constraints.md` **§4**: viết lại từ "≥2 teacher độc lập, teacher
  disagreement, held-out gold" → "nhãn do người gán, nguồn sự thật duy nhất;
  provenance = annotator id + ts". Cân nhắc Scope(in) "gold protocol" → "human
  annotation protocol".
- `docs/intent/invariants.md` **I6**: retire/viết lại (không còn teacher κ);
  **I4** giữ, đổi chữ "gold speakers ∩ weak-pool" → "test speakers ∩ train".
- `docs/spec/capabilities/extraction-pipeline.md` **bước 7–8**: "weak-label
  2-teacher + weak pool" → "human labeling; corpus = clip human-labeled".

**Provenance:** quyết định qua hỏi-đáp user 2026-07-07 (4 lựa chọn: phạm vi =
"human toàn bộ"; teacher = "giữ gợi ý mờ"; chất lượng = "single-pass, chưa κ").
