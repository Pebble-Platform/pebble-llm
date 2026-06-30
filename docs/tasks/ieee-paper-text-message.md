# IEEE Bài 1 (Text/Message) — viết draft theo chuẩn IEEE

- **Slug:** ieee-paper-text-message
- **Status:** done (draft hoàn chỉnh; M8 baseline+κ deferred — điền sau khi chạy/khôi phục, không chặn)
- **Created:** 2026-06-28 · **Updated:** 2026-06-29
- **Owner:** Fabio / Claude
- **IDD:** đây là execution của **change 001 phase-6** (`docs/spec/changes/001-initial-build/phase-6-paper-and-ethics.md`).

## Goal
Viết **draft hoàn chỉnh bài báo IEEE Bài 1** (*Weakly-Supervised Augmentation for Ordinal Suicide-Risk Classification: An Honest Gold-Holdout Study*) ở **Markdown** (convert LaTeX IEEEtran sau), dùng toàn bộ số liệu đã verify, đánh dấu rõ `[TODO κ]` + `[TODO baseline]` cho phần chưa có (KHÔNG bịa số). "Done" = file `docs/papers/finetuning-message/PAPER-DRAFT-text-ordinal-suicide.md` đủ 7 mục IEEE + abstract + references, mọi số cite được kernel/log.

## Requirements & Constraints
- **Format:** Markdown draft (quyết 2026-06-28), cấu trúc IEEE double-column ~6–10 trang; convert IEEEtran sau.
- **Số liệu:** chỉ dùng số đã verify (provenance trong `r2-method-improvements-for-contribution.md`); placeholder cho κ + baseline.
- **Trung thực (ràng buộc lõi):** gold-holdout; nêu thẳng finding "flat-CE > ordinal trên gold"; không claim cùng benchmark gated.
- **Non-goals:** compile LaTeX; chạy thêm thí nghiệm (baseline đang chạy riêng); khôi phục tập overlap κ (data task khác).

## Milestones
- [x] M1 — Tracking doc + chốt outline IEEE (7 mục) từ PAPER-PLAN §4
- [x] M2 — Draft §I Introduction + §II Related Work
- [x] M3 — Draft §III Method (dual-head · CORN+GCE · label-shift · ordinal-CL · gold-holdout)
- [x] M4 — Draft §IV Data & LLM-labeling (+ `[TODO κ]`)
- [x] M5 — Draft §V Experiments (3-protocol + within-dist + ablation 2×2 + `[TODO baseline]` + per-class + label-shift + ordinal-CL)
- [x] M6 — Draft §VI Limitations & Ethics + §VII Conclusion + Abstract + Index Terms
- [x] M7 — References (numbered IEEE; notes 12–17/42–57 + Yang'25 + CORN/GCE/Menon/Saerens/Northcutt)
- [x] M8a — **Table III baseline ĐIỀN XONG (2026-06-29):** plain-RoBERTa-CE 0.346/0.169/0.292 · BiLSTM-MTL 0.378/0.181/0.396 (`fabiocarava/r2-baseline-{roberta,bilstm}@1`). Cả 2 yếu nhất macro → arch của ta thắng.
- [ ] M8b — κ + confusion (§IV) vẫn **deferred** (chờ overlap set).

## Decision Log
- **2026-06-29 — Chốt draft là "file hoàn chỉnh"; baseline + κ là 2 ô deferred điền sau (user):** draft đủ 7 mục + abstract + references là deliverable; Table III baseline + §IV κ điền sau khi run/overlap-set sẵn — KHÔNG bịa số, KHÔNG đổi số khác. Đã ghi "Draft status: complete, 2 cells deferred" ở đầu file draft. Rejected: re-run baseline ngay (2 run fabio kẹt queue >24h, không GPU; account decision để sau).
- **2026-06-28 — Format = Markdown draft, convert LaTeX sau:** dễ review/sửa nội dung trước; LaTeX là bước cơ học sau khi nội dung chốt. (User chọn.)
- **2026-06-28 — Draft ngay + placeholder cho κ/baseline:** baseline xong trong vài giờ; κ cần khôi phục overlap set (data-provenance, owner TBD) → không chặn việc draft phần còn lại. Không bịa số. (User chọn.)
- **2026-06-28 — Artifact ở `docs/papers/finetuning-message/PAPER-DRAFT-*.md`:** capability `paper-and-reporting` đặt paper ở `docs/papers/`; PLAN giữ nguyên, DRAFT là file mới.

## Open Questions
<!-- resolved 2026-06-29: baseline deferred per user → see Decision Log; không còn câu hỏi chặn. -->
- [x] ~~Baseline chạy account nào~~ → **DEFERRED** (user: "viết thành file hoàn chỉnh, phần này thêm sau khi chạy xong").
  2 run fabio kẹt queue (no GPU slot) — để placeholder, điền sau khi chạy được.

## Research Findings
<!-- (chưa cần — viết là synthesis nguyên liệu đã verify) -->

## Completed Work
- 2026-06-28 — M1: tracking doc + outline (mục dưới).
- 2026-06-28 — M2–M7: **draft đầy đủ 7 mục IEEE + Abstract + Index Terms + References** →
  `docs/papers/finetuning-message/PAPER-DRAFT-text-ordinal-suicide.md`. Mọi số dùng số đã verify
  (3-protocol, within-dist 0.653, ablation 2×2, label-shift, ordinal-CL 35.8%); `[TODO κ]` + `[TODO baseline]`
  đánh dấu rõ, không bịa. Honest finding flat-CE>ordinal nêu thẳng (Abstract, §V-D, §VI).
- 2026-06-29 — Đóng long-task ở mức **draft hoàn chỉnh**. Phát hiện 2 run baseline fabio **kẹt queue >24h**
  (no GPU slot, no output) → M8 deferred theo quyết định user. Thêm "Draft status" ở đầu file draft; Status → done.

## Outline IEEE (chốt M1)
1. **Abstract** + **Index Terms**
2. **I. Introduction** — ordinal suicide-risk + gold lâm sàng khan hiếm; câu hỏi nhãn-LLM augment trung thực; 3 đóng góp.
3. **II. Related Work** — CSSRS screening (14–17); weak/distant + LLM-as-annotator (16,13,04); ordinal (CORAL 48, CORN 49); noise-robust loss (Focal 51, GCE); confident learning (46); label shift (Menon/Saerens); MentalBERT/RoBERTa (12).
4. **III. Method** — A dual-head (post→seq); B **CORN+GCE**; C **label-shift correction**; D **ordinal-aware CL**; E **gold-holdout protocol**.
5. **IV. Data & LLM-labeling** — CSSRS-500 gold + av9ash + scrape; pipeline (single-LLM, conf≥0.6); `[TODO κ + confusion]`; de-identification/ethics.
6. **V. Experiments** — setup; bảng 3-protocol (gold-CV 0.19 / within-LLM 0.67 / cross-to-gold 0.385); within-dist 0.653 > 0.510; ablation 2×2 + flat-CE; `[TODO baseline]`; per-class; label-shift; ordinal-CL diagnostic.
7. **VI. Limitations & Ethics** — single-LLM, Behavior hiếm, gold lệch protocol (Δt=0), ethics scrape.
8. **VII. Conclusion.** + **References.**

## Remaining Action Items (deferred — không chặn; long-task đã done ở mức draft)
- [ ] M8a: re-run 2 baseline khi quota/account rõ (fabio kẹt queue) → điền Table III + capability `evaluation-protocol` + phase-5 row #4 → ✅.
- [ ] M8b: đo Cohen's κ + confusion khi khôi phục được overlap set → điền §IV + phase-4.
- [ ] (tùy chọn) convert draft → LaTeX IEEEtran khi nội dung chốt.
</content>
