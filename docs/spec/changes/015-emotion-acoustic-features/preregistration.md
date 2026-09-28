# Pre-registration — Đặc trưng âm học của cảm xúc (change 015)

> **Văn bản này phải được commit và ĐÔNG CỨNG trước khi chạy script phân tích.**
> Trích đặc trưng (`extract_emotion_features.py`) không chứa lựa chọn phân tích nào nên
> được phép chạy trước. Sau khi đông cứng, mọi thay đổi ghi thành mục có ngày ở §9.
>
> Phiên bản 1 · 2026-09-27 · [change 015](README.md) · trạng thái: **ĐÔNG CỨNG 2026-09-27**
>
> Owner duyệt 2026-09-27: D1 (gender × age_group), D2 và D3 theo đề xuất, chỉ 2 series.

## 0. Vì sao phải pre-register

Có 88 đặc trưng × 3 target, cộng 25 layer × 2 eval × 2 head. Chỉ cần chọn "đặc trưng nổi
bật nhất" hoặc "layer tốt nhất" **sau khi** nhìn kết quả là đủ để tìm ra một câu chuyện
đẹp chỉ từ nhiễu. Chọn layer theo đỉnh của đường cong OOF chính là dùng tập test để chọn
mô hình. §4.2 chặn điều đó bằng cách chọn layer **bên trong** fold train.

## 1. Câu hỏi & giả thuyết

**Câu 1 (eGeMAPS, mô tả + 3 giả thuyết có hướng, chốt trước):**

- **H1a:** arousal tương quan **dương** với F0 trung bình (`F0semitoneFrom27.5Hz_sma3nz_amean`)
  và loudness (`loudness_sma3_amean`). **Đúng** khi cả hai có ρ > 0 và q < 0.05. Đây là
  phát hiện kinh điển về arousal; nếu ta **không** thấy nó thì nghi pipeline (Demucs, cắt
  clip) trước khi nghi lý thuyết.
- **H1b:** tín hiệu valence yếu hơn arousal: max |ρ| với valence < max |ρ| với arousal
  trên 88 đặc trưng.
- **H1c:** có ≥1 đặc trưng **chất giọng** với |ρ| ≥ 0.1 **và** q < 0.05 với valence.
  "Chất giọng" (D2) = đúng 10 cột eGeMAPS: `amean` và `stddevNorm` của `jitterLocal`,
  `shimmerLocaldB`, `HNRdBACF`, `logRelF0-H1-H2`, `logRelF0-H1-A3` (hậu tố `_sma3nz_`). Nếu đúng thì trong âm học vẫn còn một kênh valence mà
  nhánh 013 có thể tận dụng; nếu sai thì củng cố luận điểm "valence phải lấy từ text".

**Câu 2 (layer WavLM):**

- **H2:** layer được chọn bằng inner-CV cho macro-F1 emotion LOSO cao hơn layer 24
  (baseline).
- **H0:** không khác biệt, tức layer cuối đã đủ và baseline giữ nguyên.

## 2. Tập clip — cố định, 1324

Bộ lọc giống `build_kaggle_gold.py`: có `emotion` người gán, không `rejected`, không
`multi` (I3). Snapshot `state.db` được chốt tại thời điểm chạy trích đặc trưng; `n` và
git commit ghi trong `config.json`. Không thêm clip sau khi đông cứng.

| | |
|---|--:|
| chay-tron-thanh-xuan | 1060 |
| ve-nha-di-con | 264 |

**Loại trừ đã chốt trước (owner đồng ý 2026-09-27):** chỉ lấy 2 series trên, tức đúng tập
mà baseline đánh giá. Clip của series label sau (`cay-tao-no-hoa`, 6 clip ngày
2026-09-27) bị loại, vì một series vài clip sẽ thành một fold LOSO gần như rỗng. Bộ lọc
nằm ở hằng `SERIES` trong script và được ghi lại trong `config.json`.

## 3. Phân tích eGeMAPS (Câu 1)

- **Chuẩn hoá trước khi thống kê:** z-score từng đặc trưng trong nhóm **(gender ×
  age_group)** (D1, owner chốt 2026-09-27). Mục đích là loại bỏ khác biệt giữa giọng
  người với nhau. Không chuẩn hoá thì "F0 cao" chủ yếu chỉ đo tỉ lệ nữ/nam và già/trẻ
  trong từng lớp.
  - **Nhóm < 20 clip gộp vào nhóm tuổi liền kề cùng giới:** `teen` → `young_adult`,
    `senior` → `middle_aged` khi nhóm senior của giới đó < 20. Theo số đếm ngày
    2026-09-27, `female/teen` (4) gộp vào `female/young_adult`, `female/senior` (16) gộp
    vào `female/middle_aged`, còn `male/senior` (25) giữ nguyên. Quy tắc áp máy móc trên
    số đếm thật của snapshot trong `config.json`.
  - Clip thiếu gender hoặc age_group bị loại khỏi §3 (1 clip theo số đếm hôm nay). Clip
    đó vẫn có mặt trong §4.
  - **Không** chuẩn hoá theo series. Khác biệt thu âm/mix giữa các phim vì vậy **còn lại**
    trong đặc trưng §3 và phải được ghi khi báo cáo.
- Với mỗi đặc trưng trong 88:
  - Kruskal–Wallis trên 7 lớp emotion, effect size **ε²**;
  - Spearman ρ với valence và với arousal.
- **Hiệu chỉnh đa phép thử:** Benjamini–Hochberg q < 0.05 trên cả 88 × 3 = 264 phép thử.
- **Báo cáo:** đủ 88 dòng (không chỉ top-k), gom theo nhóm. **Chất giọng** = 10 cột của
  H1c. **Ngữ điệu** = cột bắt đầu bằng `F0semitone`, `loudness`, `equivalentSoundLevel`,
  và các cột nhịp (`VoicedSegmentsPerSec`, `MeanVoicedSegmentLengthSec`,
  `StddevVoicedSegmentLengthSec`, `MeanUnvoicedSegmentLength`,
  `StddevUnvoicedSegmentLength`). **Phổ** = phần còn lại (MFCC, formant, alpha ratio,
  Hammarberg, slope, flux).
  Kèm bảng trung vị (đã chuẩn hoá) theo lớp cho các đặc trưng ở H1a/H1c.
- Kết luận đọc trên **effect size**. p-value chỉ dùng để lọc, vì clip không độc lập.

## 4. Probe theo layer WavLM (Câu 2)

Giữ nguyên thiết lập đông cứng ở [012 §10](../012-label-quality-ablation/preregistration.md):
`Linear` head, Adam lr 1e-3, weight_decay 1e-4, 200 epoch (emotion) / 300 (affect),
weighted-CE, CCC loss, seed 0–9, gộp seed theo modal emotion / trung bình V/A. Hai eval:
GroupKFold(ep) 5 fold (lạc quan) và **LOSO theo series (trung thực, dùng cho §5)**.

### 4.1 Đường cong mô tả

Với mỗi layer ℓ ∈ 0..24, tính macro-F1, UAR, CCC valence, CCC arousal ở cả hai eval.
Báo cáo đủ 25 điểm kèm CI. Đây là **mô tả**, không phải căn cứ quyết định: layer có đỉnh
trên đường này đã được chọn bằng chính tập test.

### 4.2 So sánh quyết định: layer chọn trong fold vs layer 24

Trong mỗi fold ngoài của LOSO, layer ℓ\* được chọn **chỉ bằng series train**: inner
GroupKFold(ep) min(5, số tập) fold trên series đó (chay-tron-thanh-xuan 17 tập → 5 fold;
ve-nha-di-con chỉ 3 tập → 3 fold, và tập nhỏ nhất chỉ 20 clip nên việc chọn ℓ\* khi train
trên ve-nha-di-con sẽ nhiễu), lấy layer có macro-F1 inner-OOF cao nhất (hoà thì
chọn layer lớn hơn, gần baseline hơn). Head được train lại trên toàn bộ series train ở
ℓ\*, rồi dự đoán series test. Nhánh so sánh dùng layer 24 cố định với cùng fold và cùng
seed.

- **Δ = macro-F1(ℓ\*) − macro-F1(24)**, LOSO, 10 seed gộp, **paired bootstrap** 1000 lần
  trên cùng 1324 clip (cùng chỉ số resample cho hai nhánh, giống 012 §5).
- Báo cáo kèm ℓ\* của từng fold ngoài × seed. Nếu ℓ\* nhảy lung tung giữa các fold thì
  bản thân điều đó đã là một kết quả.

### 4.3 eGeMAPS làm feature probe (mô tả)

Probe cùng head trên 88 đặc trưng eGeMAPS (z-score theo fold train). Đặt cạnh layer 24
để biết âm học thủ công đi được bao xa so với SSL. Không có quy tắc quyết định cho mục này.

## 5. Quy tắc quyết định — chốt trước

Đọc trên Δ ở §4.2 (macro-F1 emotion, LOSO, 10 seed):

| Điều kiện | Kết luận | Hành động |
|---|---|---|
| Δ ≥ **+0.02** và CI 95% **không chứa 0** | layer giữa tốt hơn rõ | change sau đổi feature của kernel baseline sang quy trình chọn layer trong fold, cập nhật `training-baseline.md` |
| \|Δ\| < 0.02 **hoặc** CI chứa 0 | **H0** | giữ layer 24; báo cáo đường cong như kết quả mô tả |
| Δ ≤ −0.02 và CI không chứa 0 | chọn trong fold tệ hơn | giữ layer 24; ghi nhận inner-CV không ổn định ở cỡ mẫu này |

Ngưỡng 0.02 lấy lại từ 012 §7 (cùng thước đo, cùng lý do). Câu 1 **không** có quy tắc
hành động: H1a–H1c được báo đúng / sai nguyên trạng.

## 6. Điều này **không** thiết lập

- **Không** phải headline accuracy (I6): nhãn single-annotator, κ owner↔mù 0.513.
- **Không** tách được cảm xúc khỏi thanh điệu. Mọi đặc trưng F0/phonation ở đây lẫn cả hai.
  Không được viết "đặc trưng X mang cảm xúc" mà thiếu câu này.
- **Không** khái quát ra ngoài phương ngữ Bắc (1324/1324 clip `north`).

## 7. Báo cáo bất kể kết quả

`docs/reports/015/` gồm `egemaps_stats.md` (đủ 88 dòng), `layer_probe.md` (25 layer × 2
eval + Δ §4.2 + ℓ\* theo fold) và `metrics.json`. Mỗi số truy về
`analyze_emotion_features.py` và `config.json` của lần trích (I5). Kết quả null báo
nguyên trạng.

## 8. Quyết định của owner (đã chốt 2026-09-27)

| # | Câu hỏi | Đề xuất | Phương án khác |
|---|---|---|---|
| **D1** | Chuẩn hoá §3 theo nhóm nào? | ✅ **Đã chốt 2026-09-27: (gender × age_group)**, gộp nhóm < 20 clip (xem §3). Không chuẩn hoá theo series, không có kiểm tra per-speaker. | *(đã cân nhắc: series × gender; per-speaker trên 251 clip có tên nhân vật)* |
| **D2** | Đại diện của chất giọng cho H1c | ✅ **Đã chốt 2026-09-27:** 5 nhóm như §1 (jitter · shimmer · HNR · H1–H2 · H1–A3), 10 cột | Thêm alpha ratio / Hammarberg (thiên về phổ nhưng hay dùng cho voice quality) |
| **D3** | Có cần §4.2 (inner-CV) không, hay chỉ cần đường cong mô tả §4.1? | ✅ **Đã chốt 2026-09-27: cần.** Không có nó thì không được đổi baseline | Chỉ §4.1, và chấp nhận rằng mọi đề xuất đổi layer đều phải qua một change mới |

## 9. Sửa đổi sau khi đông cứng

*(chưa có)*
