# Change 015 — Đặc trưng âm học của cảm xúc (eGeMAPS + probe theo layer WavLM)

- **Status:** **draft (2026-09-27)** — script trích đặc trưng đã có và đã smoke-test;
  [`preregistration.md`](preregistration.md) **chưa đông cứng** (3 quyết định chờ owner,
  §"Cần owner quyết"). Chưa chạy phân tích nào, chưa có số.
- **Owner:** user / Claude
- **Depends on:** [004](../004-vnser-training/README.md) (baseline dùng layer cuối của
  WavLM) · [012](../012-label-quality-ablation/preregistration.md) (head, seed, cách gộp
  seed, paired bootstrap — dùng lại nguyên)

## Hai câu hỏi

1. **Đặc trưng âm học nào mang thông tin cảm xúc trên ViEmoSpeech?** Dùng bộ 88 đặc
   trưng eGeMAPS (ngữ điệu · chất giọng · phổ), là thứ đọc được bằng ngữ âm học.
2. **Thông tin cảm xúc nằm ở layer nào của WavLM-Large?** Baseline hiện chỉ dùng
   `last_hidden_state`, tức layer 24. Nếu một layer giữa tốt hơn thì đây là cải tiến rẻ
   nhất có thể: không cần thêm nhãn, không cần nhánh text.

## Vì sao làm trước bimodal (013)

- Valence LOSO gần sàn (CCC 0.071–0.091) trong khi arousal khá hơn
  ([`training-baseline.md`](../../capabilities/training-baseline.md)). Câu 1 kiểm tra
  trực tiếp xem trong âm học **có** tín hiệu valence nào không, hay chỉ có arousal. Đó là
  bằng chứng mà 013 đang viện dẫn nhưng chưa đo.
- Câu 2 xác lập bậc thang speech-only **mạnh nhất** trước khi đo delta của bimodal. So
  bimodal với một baseline yếu một cách không cần thiết sẽ thổi phồng delta.

## Văn bản & code

| File | Việc |
|---|---|
| [`preregistration.md`](preregistration.md) | Giao thức + quy tắc quyết định, **phải đông cứng trước khi chạy phân tích** |
| `scripts/vietnamese-ser/extract_emotion_features.py` | Trích eGeMAPS (88) + WavLM 25 layer, mean-pool, cho mọi clip sạch. **Không** chứa lựa chọn phân tích nào. Đã smoke-test 5 clip: 0 NaN, layer 24 == `last_hidden_state` |
| `scripts/vietnamese-ser/analyze_emotion_features.py` | *(chưa viết, viết sau khi đông cứng)* thống kê §3 + probe §4 → `docs/reports/015/` |

Output nằm ở `data/vietnamese-ser/features/015/` (gitignored): `egemaps.csv` (metadata +
88 cột, **không** có text), `wavlm_layers.npz` (`[N, 25, 1024]`), `config.json`
(provenance: phiên bản openSMILE/transformers, git commit, bộ lọc).

Chạy (local CPU, ~25–30 phút cho 1324 clip / 76.6 phút audio, **cắm sạc**):

```
PYTHONIOENCODING=utf-8 PYTHONPATH=scripts/vietnamese-ser \
  .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/extract_emotion_features.py
```

Mỗi stage bỏ qua nếu file output đã có, nên nếu bị ngắt giữa chừng thì chạy lại là tiếp
tục được. Cần `opensmile` trong `.venv-vnser`
(`uv pip install --python .venv-vnser/Scripts/python.exe opensmile`, đã cài 2.6.0).

## Phạm vi

**Trong:** 1324 clip nhãn người sạch (chay-tron-thanh-xuan 1060 · ve-nha-di-con 264) ·
eGeMAPS functionals · WavLM-Large đóng băng, mọi layer · linear probe · cùng hai eval
(GroupKFold(ep) + LOSO) như baseline.

**Ngoài:**
- **Chuẩn hoá theo thanh điệu.** Đây là câu hỏi tiếng Việt thật sự (F0 và phonation vừa
  mang thanh điệu vừa mang cảm xúc, vn-06), nhưng nó cần nhãn thanh điệu theo âm tiết,
  mà `state.db` chưa có (013 Q2). Kết quả eGeMAPS ở đây vì vậy **lẫn** hiệu ứng thanh
  điệu, và phải ghi rõ điều đó khi báo cáo.
- **So sánh phương ngữ:** cả 1324 clip đều là `north`, nên không có gì để so.
- Fine-tune backbone, đổi backbone, nhánh text. Trộn trọng số các layer (kiểu SUPERB)
  cũng để ngoài vì là một head mới, không phải phép đo.

## Nợ đã biết trước khi chạy

- **Single annotator** (ADR-003). κ owner↔mù = 0.513 (014), nên mọi số ở đây là pilot,
  không phải headline (I6).
- **Danh tính speaker gần như không có.** Trường `speaker` có ở 555/1324 clip, nhưng chỉ
  **251** clip là tên nhân vật do người gán, và cả 251 clip đều thuộc chay-tron-thanh-xuan.
  304 clip còn lại (263 ve-nha-di-con + 41 chay-tron) là ID thô của pyannote (`SPEAKER_07`).
  ID này chỉ duy nhất **trong một tập**: cùng `SPEAKER_01` ở ep01 và ep02 chưa chắc là một
  người. `gender` có ở 1323/1324. Đây là căn cứ của D1.
- **Clip không độc lập** (cùng speaker, cùng tập), nên p-value của §3 lạc quan. Kết luận
  đọc trên **effect size**, còn p-value chỉ để lọc.
