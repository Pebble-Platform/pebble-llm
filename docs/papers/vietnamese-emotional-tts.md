# Sinh giọng nói tiếng Việt có cảm xúc (emotional TTS): paper, tool, và cách làm với data hiện có

- **Ngày:** 2026-10-09 · **Loại:** ghi chú research (không phải spec, không phải kết quả)
- **Trạng thái:** khảo sát xong; **chưa có quyết định** làm hay không (xem §5)

> ⚠ **Ngoài scope hiện tại.** `docs/intent/constraints.md` chỉ có corpus + SER method paper
> trong "Scope (in)". Mở nhánh TTS là **quyết định của người** ở tầng intent, không phải
> việc phụ của một PR. File này chỉ gom bằng chứng để quyết.

---

## 1. Paper nên đọc

### 1.1 Trực tiếp về tiếng Việt (rất ít; gần như chỉ xoay quanh VLSP 2022)

| Paper | Nội dung | Ghi chú |
|---|---|---|
| VLSP 2022, task Emotional Speech Synthesis | 2 sub-task: (1) TTS cảm xúc 1 speaker có data cảm xúc; (2) chuyển cảm xúc sang speaker chỉ có data trung tính | Benchmark công khai duy nhất cho TTS cảm xúc tiếng Việt. Kích thước dataset: chưa xác minh |
| [An Empirical Study on Learning Latent Representations for ESS](https://arxiv.org/abs/2606.14922) (Dang Quang & Ngo Quang, arXiv 2026) | FastSpeech 2 + speaker embedding + prosody bottleneck, giải cả 2 sub-task VLSP 2022 | Abstract không có số định lượng |
| [The VNPT-IT emotion transplantation approach for VLSP 2022](https://vjs.ac.vn/jcc/article/view/18236) (JCC) | Ghép cảm xúc từ speaker nguồn sang speaker đích, kèm pipeline tiền xử lý | Gần sub-task 2 nhất |
| [Emotional Vietnamese Speech Synthesis Using Style-Transfer Learning](https://www.researchgate.net/publication/361366465_Emotional_Vietnamese_Speech_Synthesis_Using_Style-Transfer_Learning) | Flowtron học latent cảm xúc + Tacotron 2; 5 cảm xúc, giọng nam + nữ | Data rất nhỏ; baseline sớm |
| [Zero-Shot TTS for Vietnamese / PhoAudiobook](https://arxiv.org/abs/2506.01322) (ACL 2025) | 941 giờ; so sánh VALL-E, VoiceCraft, XTTS-v2 trên tiếng Việt | Không về cảm xúc, nhưng là nền zero-shot tiếng Việt |
| [Modeling Vietnamese Speech Prosody…](https://www.researchgate.net/publication/315544836_Modeling_Vietnamese_Speech_Prosody_A_Step-by-Step_Approach_Towards_an_Expressive_Speech_Synthesis_System) | Ngữ điệu tiếng Việt (6 thanh, phân đoạn ngữ điệu) cho TTS biểu cảm | Nền ngữ âm |

### 1.2 Thanh điệu × cảm xúc (khớp hướng tone×emotion của repo)

- **Wen et al., Emotional Mandarin Speech Synthesis with Tone Nucleus Model**
  ([Interspeech 2011](https://www.isca-archive.org/interspeech_2011/wen11b_interspeech.html)):
  chỉ biến đổi F0 ở *nhân thanh* của mỗi âm tiết để thêm cảm xúc mà thanh không méo.
  Áp dụng được thẳng cho tiếng Việt.
- [Cross-linguistic emotional prosody control](https://arxiv.org/pdf/2508.02038v3): chỉnh
  pitch/energy ở mức từ khóa trong FastSpeech 2, so sánh tiếng Trung (cao độ phân biệt từ)
  với tiếng Anh (cao độ cho ngữ điệu).
- Bằng chứng ngữ âm đã có trong repo: [vn-13 Chang 2023](vietnamese-ser/13-chang-mandarin-tone-emotion.vi.md).

### 1.3 Emotional TTS hiện đại (tiếng Anh/Trung; đọc để lấy kiến trúc)

| Paper | Ý chính |
|---|---|
| [Towards Controllable Speech Synthesis in the Era of LLMs](https://arxiv.org/abs/2412.06602) (EMNLP 2025, survey) | Bản đồ toàn cảnh. **Đọc đầu tiên** |
| [EmoVoice](https://arxiv.org/abs/2504.12867) | TTS dựa trên LLM, điều khiển cảm xúc bằng câu mô tả tự do; EmoVoice-DB 40 giờ tiếng Anh |
| [IndexTTS2](https://arxiv.org/abs/2506.21619) (AAAI) | Tách cảm xúc khỏi giọng: clone giọng A với cảm xúc B |
| [EmoSphere++](https://arxiv.org/abs/2411.02625) | Điều khiển loại + cường độ cảm xúc bằng vector cầu; không cần nhãn cường độ |
| [EmoSteer-TTS](https://arxiv.org/abs/2508.03543) | **Training-free**: activation steering trên F5-TTS / E2-TTS / CosyVoice2 (xem §4) |
| [EmoShift](https://arxiv.org/html/2601.22873) | Activation steering nhẹ hơn cho TTS cảm xúc |
| [CoCoEmo](https://arxiv.org/pdf/2602.03420) (ICML 2026) | Trộn nhiều cảm xúc trong một câu bằng activation steering |
| [Exploring Transfer Learning for Low Resource Emotional TTS](https://arxiv.org/abs/1901.04276) (Tits & El Haddad, IntelliSys 2019) | Fine-tune TTS trung tính bằng data cảm xúc nhỏ (xem §4) |
| [Efficient Emotion and Speaker Adaptation… Partial Fine-Tuning](https://arxiv.org/abs/2501.14273) | Chỉ fine-tune ~8% tham số, ngang full fine-tune, ít quên hơn |
| [Emilia](https://arxiv.org/abs/2501.15907) | Dataset TTS 101k giờ lấy từ audio "in-the-wild"; pipeline giống hệt pipeline của repo (xem §4) |
| [The False Resonance](https://arxiv.org/pdf/2604.26347) (Interspeech 2026) | Cảnh báo: emotion2vec cosine similarity thưởng cho việc *bắt chước âm học*, lệch với đánh giá của người |

---

## 2. Tool thực tế

### 2.1 Thương mại

| Tool | Tiếng Việt | Điều khiển cảm xúc |
|---|---|---|
| [Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts) (Google Cloud) | **vi-VN GA** (theo tài liệu chính thức) | Prompt ngôn ngữ tự nhiên + tag `[sigh]`, `[laughing]`, `[whispering]`… |
| [MiniMax Speech-02](https://www.minimax.io/news/speech-02-series) | Có | Tham số `emotion`: happy / sad / angry / fearful / disgusted / surprised / neutral |
| [ElevenLabs v3](https://elevenlabs.io/text-to-speech/vietnamese) | Có | Audio tag trong văn bản |
| OpenAI gpt-4o-mini-tts | Chưa xác minh chất lượng thanh điệu tiếng Việt | Câu `instructions` mô tả cảm xúc |
| [Vbee](https://vbee.vn/) | Có (giọng Bắc/Nam) | Style cảm xúc có sẵn, không điều khiển tự do |

### 2.2 Mã nguồn mở cho tiếng Việt

| Model | Cảm xúc |
|---|---|
| [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) v2 / v3 Turbo | Chỉ có tag phi ngôn ngữ `[cười]`, `[thở dài]`, `[hắng giọng]` (thử nghiệm). v4 không mở mã |
| [F5-TTS-Vietnamese](https://github.com/nguyenthienhy/F5-TTS-Vietnamese) ([HF 100h](https://huggingface.co/hynt/F5-TTS-Vietnamese-100h)) | Không có điều khiển; cảm xúc "lây" từ audio tham chiếu. Code MIT |
| [ZeroTTS](https://github.com/nguyenhungplatform/ZeroTTS), [valtec-tts](https://github.com/tronghieuit/valtec-tts), viXTTS | Clone giọng zero-shot, không điều khiển cảm xúc (số chất lượng là tác giả tự báo cáo) |

**Không hỗ trợ tiếng Việt chính thức:** CosyVoice 3, Fish Audio OpenAudio S1.
IndexTTS2: chỉ tiếng Trung + Anh.

---

## 3. Data đang có (đo 2026-10-09)

Đếm bằng query **read-only** trên `data/vietnamese-ser/episodes/state.db` và file wav.
Query viết tay, không phải script đã commit, nên **chỉ dùng để lập kế hoạch, không trích
làm kết quả**. Clip "dùng được" = không bị reject, có nhãn emotion, không cờ `multi`,
không phải clip cha đã bị tách.

| Chỉ số | Giá trị |
|---|---|
| Clip có nhãn dùng được | **1.420 clip ≈ 1,36 giờ** (chay-tron 1060 · ve-nha 343 · cay-tao 17) |
| Độ dài clip p10 / p50 / p90 | 1,8 s / 3,1 s / 5,7 s |
| Phút theo cảm xúc | neutral 22,4 · anger 15,2 · joy 14,8 · sadness 10,3 · fear_anxiety 8,0 · disgust 7,2 · surprise 3,8 |
| Số clip theo cảm xúc | neutral 385 · anger 277 · joy 246 · sadness 169 · fear_anxiety 145 · disgust 116 · surprise 82 |
| Transcript người sửa (`gold_text`) | 1.420 / 1.420 |
| Valence / arousal | 1.420 / 1.420 |
| Speaker id | **865 trống**, 304 là ID thô của pyannote (chỉ duy nhất trong một tập), 251 có tên (13 người) |
| Speaker nhiều nhất | Vy: 59 clip = **4,3 phút**, rải trên 7 cảm xúc |
| Giới / phương ngữ | nữ 913 · nam 506 / Bắc 1404 · Nam 16 |
| Chất lượng audio | **16 kHz mono**, cắt từ stem vocals của Demucs (audio phim TV) |
| Tổng clip đã cắt (cả chưa nhãn) | 2.826 clip ≈ 2,81 giờ, từ 42 tập (`audio_full.wav` cũng là 16 kHz) |

---

## 4. Dẫn chứng: data này đủ cho hướng nào

| Hướng | Data cần (theo dẫn chứng) | Data có | Kết luận |
|---|---|---|---|
| **Train / fine-tune TTS tiếng Việt mới** | 10–100+ giờ cho ngôn ngữ mới ([thảo luận F5-TTS](https://github.com/SWivid/F5-TTS/discussions/1168)); F5-TTS-Vietnamese dùng 100 h → ~1000 h ([repo](https://github.com/nguyenthienhy/F5-TTS-Vietnamese)) | 1,36 h | ❌ Thiếu 1–3 bậc độ lớn. Mà cũng không cần: model tiếng Việt đã có sẵn |
| **Fine-tune theo từng cảm xúc, 1 speaker** (Tits 2019) | 15–36 phút **mỗi cảm xúc**, **1 speaker**, thu trong phòng tiêu âm (EmoV-DB: amused 15', angry 19', disgusted 29', neutral 23', sleepy 36'). Train từ đầu với 20' → không nghe ra chữ; fine-tune từ model pretrained → nghe ra chữ và người nghe nhận ra cảm xúc | Tổng mỗi cảm xúc 3,8–22 phút nhưng rải trên nhiều người; **1 speaker tối đa 4,3 phút cho cả 7 cảm xúc**; audio TV qua Demucs | ❌ Theo từng speaker thì thiếu ~10× và chất lượng thu thấp hơn hẳn |
| **Fine-tune có điều kiện cảm xúc, nhiều speaker** (nhãn hoặc V/A làm điều kiện) | Chưa có số chuẩn cho tiếng Việt. Ngưỡng 10 h ở dòng 1 là cận dưới hợp lý | 1,36 h | ⚠ Chưa đủ. Kế hoạch scale P1 (`vietnamese-ser/05-scale-plan.md`: ~23,8 h thoại sạch) mới chạm mức này, và **nút cổ chai là gán nhãn** |
| **Activation steering, training-free** ([EmoSteer-TTS](https://arxiv.org/abs/2508.03543)) | Không train. Vector cảm xúc tính từ **6.900 câu có nhãn** (11 corpus, 6 cảm xúc + neutral, ≈1k câu/lớp), áp vào **F5-TTS** ở mỗi 5 tầng DiT | 82–385 câu/lớp, có nhãn người, nhiều speaker | ✅ **Cùng bậc độ lớn** (ít hơn 3–12×). F5-TTS-Vietnamese cùng kiến trúc → khả thi. Rủi ro: chưa ai thử trên tiếng Việt / ít câu hơn. Code: arXiv v3 ghi "release upon acceptance", **chưa tìm thấy repo** → có thể phải tự cài |
| **Zero-shot + audio tham chiếu cảm xúc** | Không train. Model zero-shot tái tạo prosody của prompt (IndexTTS2 mô tả điều này cho mode tự do); emotion và giọng **dính nhau** (IndexTTS2 phải tách riêng mới đổi được) | Clip có nhãn đã đủ để chọn prompt theo cảm xúc | ✅ Làm được ngay, nhưng giọng sinh ra = **giọng diễn viên** |
| **Dùng làm thước đo** (đánh giá TTS cảm xúc tiếng Việt) | Paper hiện tại dùng emotion2vec E-SIM ([EmoVoice](https://arxiv.org/abs/2504.12867), [CoCoEmo](https://arxiv.org/pdf/2602.03420)), nhưng [False Resonance](https://arxiv.org/pdf/2604.26347) cho thấy E-SIM thưởng cho bắt chước âm học → cần người đánh giá | Labeler + annotator đã mời; SER baseline 5 lớp B = 0,351 macro-F1 (ADR-006); chú thích thanh điệu từng âm tiết | ✅ Lợi thế thật sự của repo: **đánh giá mù bằng người** + **kiểm tra thanh điệu có bị méo không**. SER 0,351 quá yếu để làm giám khảo một mình |

Hai dẫn chứng phụ:

- **Pipeline đúng loại.** [Emilia-Pipe](https://arxiv.org/abs/2501.15907) gồm chuẩn hoá →
  tách nguồn → diarization → VAD → ASR → lọc, giống hệt pipeline `pilot_extract.py`.
  Emilia cho thấy data in-the-wild làm giọng sinh ra tự nhiên, giống hội thoại hơn data
  audiobook. Khoảng cách là **quy mô** (101k h so với 2,8 h), không phải cách làm.
- **Sample rate.** Clip đang ở 16 kHz, trong khi F5-TTS dùng vocoder 24 kHz. Với steering hay
  prompt thì 16 kHz chấp nhận được (chỉ dùng để tính activation hoặc làm prompt). Nếu sau
  này fine-tune thì phải cắt lại từ nguồn gốc ở sample rate cao hơn.

---

## 5. Đề xuất (xếp theo mức khả thi với data hiện có)

1. **Steering trên F5-TTS-Vietnamese (hướng nghiên cứu).** Tính vector cảm xúc từ clip có nhãn
   người (chỉ dùng speaker thuộc tập train), sinh câu mới, rồi đo:
   - (a) WER bằng PhoWhisper;
   - (b) **người nghe mù** đoán cảm xúc trong labeler;
   - (c) **thanh điệu có bị đổi không**, so với chú thích thanh điệu.

   Ý (c) nối thẳng vào giả thuyết tone×emotion. Đây là thứ mới mà paper tiếng Anh/Trung không có.
2. **Zero-shot + prompt cảm xúc (làm ngay, không train).** Hợp làm baseline cho hướng 1.
   Chỉ dùng nội bộ, vì giọng sinh ra là giọng diễn viên.
3. **API thương mại (Gemini-TTS / MiniMax).** Nếu mục tiêu là *có giọng cảm xúc* chứ không
   phải *nghiên cứu*. Corpus và annotator dùng để chấm.
4. **Fine-tune có điều kiện cảm xúc.** Hoãn đến khi data có nhãn đạt ≥ ~10 h.

### Cần người quyết trước khi làm

- **Scope (intent):** thêm TTS vào "Scope (in)" hay không.
- **Pháp lý / đạo đức:** constraint 1 cấm phát hành audio. Audio sinh ra bằng **giọng diễn
  viên thật** (hướng 2) là clone giọng người có thể nhận diện, kể cả khi chỉ dùng nội bộ.
  Vector steering (hướng 1) là đặc trưng tổng hợp trên nhiều speaker, gần với "features" được
  phép phát hành hơn. Nhưng phát hành hay không vẫn phải được quyết rõ ràng, không suy diễn.
- **Tiêu chí thành công** cho hướng 1 (ví dụ: tỉ lệ người nghe đoán đúng cảm xúc cao hơn mức
  ngẫu nhiên; WER không tăng quá X; tỉ lệ đổi thanh không quá Y). Phải chốt trong một
  pre-registration (change mới) **trước khi** chạy, theo cách đã làm ở change 015.

---

## 6. Bổ sung 2026-10-09: ứng viên kho giọng và phim test (sau pivot lồng tiếng)

Các quyết định đã chốt nằm ở `docs/intent/constraints.md` §4. Phần này chỉ gom ứng viên.

### 6.1 Kho giọng: dataset giọng Việt mở

Điều kiện theo constraints §2.2: (a) license cho phép nghiên cứu và công bố paper, và
(b) giọng được thu âm cho chính dataset đó, không phải cào từ nguồn khác.

| Dataset | Quy mô | License | (b) thu cho dataset? | Kết luận |
|---|---|---|---|---|
| [Common Voice vi](https://mfa-models.readthedocs.io/en/latest/corpus/Vietnamese/Common%20Voice%20Vietnamese%20v17_0.html) (v17) | 5,91 h · 5.068 câu · 150 người | CC0 | ✅ Người đóng góp tự đọc và hiến tặng giọng | ✅ Căn cứ đồng ý rõ nhất, nhưng ít data mỗi người và chất lượng thu không đều ([bàn về dùng CV cho TTS](https://arxiv.org/pdf/2210.06370)) |
| [VIVOS](https://github.com/lienlt10/awesome-vietnamese-speech-datasets) | 15 h · 65 người, đọc trong phòng thu | CC-BY-NC-SA-4.0 | ✅ Thu cho dataset | ✅ Dùng được cho paper (phi thương mại) |
| [FOSD](https://data.mendeley.com/datasets/k9sxg2twv4) (FPT) | ~30 h · 25.921 câu; [nam ~10,5 h](https://data.mendeley.com/datasets/3zz6txz35t) · [nữ ~9,5 h](https://data.mendeley.com/datasets/4gzzc9k49n) | "FPT Public License": **cần đọc điều khoản** | ✅ Thu cho dataset | ⚠ Nhiều giờ mỗi giọng nhất, hợp làm giọng chính. Phải kiểm license |
| [viVoice](https://github.com/Mr-Jack-Tung/viVoice) | ~1000 h | CC-BY-NC-SA-4.0 | ❌ Cào từ 186 kênh YouTube | ❌ Không đạt (b). Có thể dùng làm data *train* nền, nhưng không làm giọng phát ra |
| [PhoAudiobook](https://huggingface.co/datasets/thivux/phoaudiobook) | 941 h | Chỉ nghiên cứu/giáo dục, cấm phân phối | ❌ Sách nói | ❌ Tương tự viVoice |
| [viet-tts-dataset](https://huggingface.co/datasets/ntt123/viet-tts-dataset) | 35,9 h | Chỉ nghiên cứu | ❌ Giọng tổng hợp của Google TTS | ❌ |

**Lỗ hổng (D12):** cả ba dataset hợp lệ đều là **người lớn đọc văn bản trung tính**.
Không có giọng trẻ em, và không có cảm xúc. Cảm xúc phải học từ ViEmoSpeech rồi chuyển sang
các giọng này. Đây chính là sub-task 2 của VLSP 2022 (§1.1).

### 6.2 Phim test: hoạt hình giàu cảm xúc

Tiêu chí:
1. Nhiều cảm xúc rõ rệt, khớp bộ nhãn 7 lớp.
2. **Có bản lồng tiếng Việt chính thức**, dùng làm mốc so sánh do người diễn, và có thể chép
   lại thành kịch bản kèm khung thời gian (D11).
3. Nhiều thoại, nhiều nhân vật.

| Phim | Bản lồng tiếng Việt | Vì sao hợp |
|---|---|---|
| **Inside Out** (2015) | ✅ Chiếu rạp 21/8/2015, có bản 2D lồng tiếng ([vi.wikipedia](https://vi.wikipedia.org/wiki/Nh%E1%BB%AFng_m%E1%BA%A3nh_gh%C3%A9p_c%E1%BA%A3m_x%C3%BAc)) | Nhân vật *là* cảm xúc: Joy, Sadness, Anger, Disgust, Fear khớp gần 1:1 với joy / sadness / anger / disgust / fear_anxiety của corpus |
| **Inside Out 2** (2024) | ✅ Có diễn viên lồng tiếng Việt ([vi.wikipedia](https://vi.wikipedia.org/wiki/Nh%E1%BB%AFng_m%E1%BA%A3nh_gh%C3%A9p_c%E1%BA%A3m_x%C3%BAc_2)) | Thêm Anxiety, Embarrassment, Ennui, Envy, giàu sắc thái hơn |
| **Encanto** (2021) | ✅ Lồng tiếng qua CGV ([vi.wikipedia](https://vi.wikipedia.org/wiki/Encanto:_V%C3%B9ng_%C4%91%E1%BA%A5t_th%E1%BA%A7n_k%E1%BB%B3)) | Xung đột gia đình, nhiều nhân vật. Nhược điểm: nhiều đoạn hát (phải loại) |
| Coco · Elemental · Turning Red · Zootopia · Moana · Kung Fu Panda 4 · Doraemon (movie) | ⚠ Chưa xác minh bản lồng tiếng Việt | Giàu cảm xúc. Doraemon và Kung Fu Panda 4 có doanh thu rạp Việt lớn ([VnExpress](https://vnexpress.net/hoat-hinh-doraemon-lap-ky-luc-rap-viet-4753206.html), [Báo Lào Cai](https://baolaocai.vn/phim-thieu-nhi-ngoai-doc-chiem-rap-viet-post384731.html)) |

Đề xuất: **Inside Out làm phim test chính**, Inside Out 2 làm phim test phụ. Nhưng hai phim
cùng loạt nên cần chú ý: theo constraints §2.6, nếu một phim dùng để phát triển thì phim
kia **không** được coi là tập test độc lập về nhân vật.
