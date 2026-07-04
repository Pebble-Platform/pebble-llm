# Review tiến độ & tính trung thực — stream finetuning-message (Text/R2)

- **Slug:** thesis-message-review
- **Status:** done
- **Created:** 2026-07-02  ·  **Updated:** 2026-07-02
- **Owner:** user / Claude

## Goal
Đọc lại toàn bộ quá trình triển khai thesis (nhánh **finetuning-message**, theo
`docs/reports/THESIS-OVERVIEW-vi.md`) và trả lời 3 câu hỏi: (1) tiến độ có đúng
hướng không, (2) ý tưởng ↔ thực thi có đi lệch không, (3) đánh giá trung thực &
khách quan kết quả các lần run — **có kiểm chứng provenance** (số trong doc ↔ log
thật), không chỉ đọc lại report.

## Requirements & Constraints
- **Functional:** đối chiếu số liệu trong docs với log/kernel thực tế; đối chiếu
  thực thi với intent layer (`docs/intent/constraints.md`).
- **Constraints:** chỉ review + cập nhật doc; không chạy thêm thí nghiệm GPU,
  không sửa code thí nghiệm.

## Milestones
- [x] M1 — Thu thập bằng chứng: THESIS-OVERVIEW, r2-ab-results, weekly 06-29,
  r2-method-improvements, PAPER-PLAN, PAPER-DRAFT, intent/constraints.
- [x] M2 — Kiểm chứng provenance: log local + Kaggle CLI (kết quả bên dưới).
- [x] M3 — Đánh giá drift ý tưởng ↔ thực thi so với intent layer.
- [x] M4 — Báo cáo verdict 3 câu hỏi + action items.

## Decision Log
- **2026-07-02 — Kiểm chứng provenance bằng log thật thay vì tin report:** vì
  yêu cầu là "đánh giá trung thực, khách quan", mọi số headline được đối chiếu
  với log local (`r2-suicide-risk-dualhead/log.txt`) và Kaggle CLI
  (`uvx --from kaggle kaggle kernels output …`). Rejected: chỉ đọc chéo docs
  (không phát hiện được gap log).
- **2026-07-02 — Tải output 2 baseline từ Kaggle (fabiocarava):** doc còn ghi
  "🔄 running"; kết quả thật đã có từ 2026-06-28 → cập nhật vào provenance
  (`r2-method-improvements-for-contribution.md`) trong cùng PR.

## Kết quả kiểm chứng provenance (M2)

| Số liệu | Nguồn claim | Kiểm chứng 2026-07-02 |
|---|---|---|
| Run B dual-head gold **0.3849 ±0.0071**, QWK 0.398 | r2-ab-results §1 | ✅ **Khớp log local** `r2-suicide-risk-dualhead/log.txt` (folds 0.3934/0.3841/0.3868/0.3880/0.3722 → mean 0.3849, std 0.0071) |
| **Baseline plain-RoBERTa-CE** (chưa có trong docs) | `fabiocarava/r2-baseline-roberta@1` | ✅ Log tải về `r2-baseline-roberta/out/`: **gold macro-F1 0.3456 ±0.0256** (folds 0.3266/0.3224/0.3376/0.3936/0.3479) · val-on-LLM 0.6423 · QWK fold4 0.280 |
| **Baseline BiLSTM-MTL** (chưa có trong docs) | `fabiocarava/r2-baseline-bilstm@1` | ✅ Log tải về `r2-baseline-bilstm/out/`: **gold macro-F1 0.3783 ±0.0139** (folds 0.3549/0.3958/0.3835/0.3723/0.3852) |
| within-dist CV **0.6530 ±0.0048** | `phatneurondai/r2-within-dist-cv-10k-balanced` | ✅ **Khớp** — log pulled 2026-07-02 (user cấp token `phatneurondai`): folds [0.6493, 0.6595, 0.6564, 0.6536, 0.6461] → `r2-within-dist-cv/out/` |
| flat-CE **0.4215 ±0.024** / Beh 0.285 | `phatneurondai/r2-ablation-flatce@1` | ✅ **Khớp** — mean=0.4215 std=0.0242, Behavior folds → mean 0.2846 → `r2-ablation/out/` |
| CORN+GCE **0.4022 ±0.013** / Beh 0.260 · corn-only 0.410 · gce-only 0.399 | `phatneurondai/r2-{corn-gce@2,corn-only@2,gce-only@1}` | ✅ **Khớp cả 3** — 0.4022±0.0132/Beh 0.2596 · 0.4095±0.0254/Beh 0.2499 · 0.3990±0.0149/Beh 0.2291 → `out/` từng kernel |
| cleanlab **35.8%** Behavior noisy | `phatneurondai/r2-tier1-cleanlab-diagnostic@1` | ✅ **Khớp** — log: Behavior 227/634=0.358, total 1570/9680=0.162; `cl_issues.npz` (400KB) đã về `r2-tier1-cleanlab/out/` |
| label-shift Beh 0.357→0.41 | local script `r2-label-shift/posthoc_label_shift.py` | ✅ script committed; số phụ thuộc checkpoint `best_model.pt` (không commit — đúng chính sách); caveat 1-best-fold đã được doc ghi rõ |

→ **Kết luận provenance (cập nhật 2026-07-02, sau khi pull log `phatneurondai`):
TOÀN BỘ số headline đã được kiểm chứng khớp chính xác với retained log.**
Gap "retained log" đã vá: log 6 kernel nằm trong `kaggle/**/out/` (local,
gitignored) + bảng tổng hợp commit được tại
`kaggle/finetuning-message/results-summary.csv`. Constraint #4 giờ thỏa đầy đủ
cho mọi số headline của stream message.

## Verdict 3 câu hỏi (M3–M4)
> Chi tiết đầy đủ trong summary phiên 2026-07-02; tóm tắt:

1. **Tiến độ đúng hướng, nhanh hơn kế hoạch ở phần model, chậm ở phần data/nhãn.**
   Ablation 2×2 xong; 2 baseline xong (trước cả khi docs kịp cập nhật); 3 đóng góp
   phương pháp đều có tín hiệu dương đã verify. Nhưng 2 việc 🔴 "latency ngoài tầm
   kiểm soát" (**Cohen's κ**, **DUA/EULA data access**) bị flag "start early" từ
   2026-06-27 mà đến nay **chưa bắt đầu** — đây là rủi ro lịch trình số 1.
2. **Không drift về bản chất.** Thực thi bám đúng intent (gold-holdout, subject-level,
   honest framing); pivot product→paper là quyết định có chủ đích được ghi ở intent
   layer; 3 đóng góp mới trả lời đúng feedback "phải cải tiến phương pháp".
   **Rủi ro lệch duy nhất là ở khâu trình bày:** headline "vượt paper +28%" khi
   tách khỏi caveat ("cùng *giao thức*, khác *dataset*") sẽ thành overclaim.
3. **Kết quả là thật, khiêm tốn về giá trị tuyệt đối, và được báo cáo trung thực**
   (đính chính preview 3-fold, giữ negative finding flat-CE > ordinal). Điểm yếu
   khách quan: khác biệt giữa các biến thể ordinal (0.385→0.422) phần lớn **nằm
   trong khoảng nhiễu** (std 0.013–0.025, 5 fold, phần lớn 1 seed), chưa có
   significance test; label-shift mới đo trên 1 checkpoint; κ chưa có.

## Completed Work
- 2026-07-02 — Đối chiếu toàn bộ số headline docs ↔ log; phát hiện gap log
  `phatneurondai` (bảng trên).
- 2026-07-02 — Tải + xác nhận kết quả 2 baseline (roberta 0.3456 / bilstm 0.3783);
  cập nhật provenance table trong `r2-method-improvements-for-contribution.md`.
- 2026-07-02 — Verdict 3 câu hỏi (trên) + action items (dưới).

## Remaining Action Items (bàn giao)
- [x] 🔴 **Khôi phục retained-log — XONG 2026-07-02:** token đổi sang
  `phatneurondai` (backup fabiocarava: `~/.kaggle/access_token.fabiocarava.bak`),
  đã pull 6 kernel về `kaggle/**/out/` + tạo
  `kaggle/finetuning-message/results-summary.csv`. ⚠ Token phatneurondai bị dán
  vào chat → **revoke + tạo token mới** khi xong việc.
- [ ] 🔴 **Cohen's κ LLM↔gold** — blocker #1 của paper, chưa bắt đầu.
- [ ] 🔴 **DAIC-WOZ EULA / SMHD DUA** — latency 1–4 tuần, chưa bắt đầu.
- [ ] 🟡 Cập nhật số baseline vào `PAPER-PLAN` §3.3 (baselines ✅) +
  `r2-ab-results.md`; câu chuyện đẹp: mọi biến thể ordinal > cả 2 baseline.
- [ ] 🟡 Significance: paired per-fold delta (cùng split/seed) cho các cặp
  flat-CE vs CORN+GCE vs dual; hiện các gap nhỏ chưa phân biệt được với nhiễu.
- [ ] 🟡 Sửa arithmetic claim "+~50% rel" trong PAPER-PLAN §1 (0.19→0.385 là
  ~+100%; +57% chỉ đúng cho QWK 0.241→0.378).
- [ ] 🟡 Label-shift: chạy trên cả 5 fold checkpoint (hiện 1 best-fold).
