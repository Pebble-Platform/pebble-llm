# κ người–người (emotion) — vòng soát mù change 014 · `nhinguyen`

> Sinh bởi `scripts/vietnamese-ser/gold_review_kappa.py`. Chỉ **emotion** là mù
> (người soát chốt trước khi thấy nhãn owner). V/A lộ ra ngay sau khi chốt rồi chỉ
> được sửa ⇒ **bị neo, không có κ V/A**. Người soát **thấy transcript** (khác `rate.html`).

- Lượt soát: 344 · loại (rejected): 0 · trước khi code mù land (2026-09-11T07:53:41+00:00): 1 ⇒ **n = 343**
- Mẫu: phần đầu của hàng đợi đã xáo trộn `review-candidates.tsv` (change 011).

## 1. Headline

| cặp | n | trùng thô | Cohen κ | 95% CI (bootstrap) | α nominal |
|---|--:|--:|--:|---|--:|
| owner ↔ nhinguyen (mù) | 343 | 60.1% | **0.513** | [0.454, 0.572] | 0.511 |
| ↳ độ nhạy: gồm cả lượt trước cutoff | 344 | 60.2% | **0.514** | [0.457, 0.573] | 0.512 |

## 2. So với vòng có neo (cùng clip)

> `vyphan` soát theo giao thức cũ (thấy nhãn owner trước). **Khác người VÀ
> khác giao thức** ⇒ chênh lệch dưới đây *gợi ý* độ lớn của neo, không đo sạch nó.

| cặp | n | trùng thô | Cohen κ | 95% CI (bootstrap) | α nominal |
|---|--:|--:|--:|---|--:|
| owner ↔ vyphan (có neo) | 343 | 81.0% | **0.765** | [0.715, 0.814] | 0.765 |
| vyphan (có neo) ↔ nhinguyen (mù) | 343 | 60.3% | **0.509** | [0.451, 0.573] | 0.507 |

## 3. κ theo từng lớp (one-vs-rest, owner ↔ mù)

| lớp | owner n | mù n | κ |
|---|--:|--:|--:|
| joy | 68 | 49 | 0.641 |
| sadness | 35 | 29 | 0.621 |
| anger | 60 | 87 | 0.631 |
| fear_anxiety | 37 | 47 | 0.377 |
| surprise | 15 | 34 | 0.326 |
| disgust | 28 | 4 | 0.107 |
| neutral | 100 | 93 | 0.503 |

## 4. Ma trận nhầm (hàng = owner, cột = mù)

| owner \ mù | joy | sadness | anger | fear_anxiety | surprise | disgust | neutral |
|---|--:|--:|--:|--:|--:|--:|--:|
| joy | 41 | 1 | 3 | 1 | 9 | 0 | 13 |
| sadness | 0 | 21 | 5 | 7 | 0 | 0 | 2 |
| anger | 0 | 0 | 52 | 3 | 0 | 0 | 5 |
| fear_anxiety | 0 | 1 | 9 | 19 | 6 | 1 | 1 |
| surprise | 2 | 1 | 0 | 1 | 9 | 0 | 2 |
| disgust | 2 | 2 | 10 | 1 | 3 | 2 | 8 |
| neutral | 4 | 3 | 8 | 15 | 7 | 1 | 62 |
