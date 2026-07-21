## ADR-004 — Độ bền & khôi phục cho label DB của labeler (`state.jsonl`)

**Date:** 2026-07-21 · **Status:** proposed (nháp — user chọn "viết ADR trước",
hardening/SQLite **chưa build**; git-versioning **để ngỏ**).
**Resolves:** quyết định user 2026-07-21 ("research cách lưu database hiệu quả, để
vầy khá nguy hiểm") — sau 2 lần suýt mất data khi refactor labeler.
**Ràng buộc:** hướng B/C dưới đây chạm **I1 (media legality)** → phần git-versioning
là call **intent-layer**, ADR này chỉ nêu, không tự quyết.

**Context.** Nhãn của corpus sống trong **một file** `tools/labeler` ghi vào:
`data/vietnamese-ser/episodes/state.jsonl` (~827 dòng, ~450 KB, 1 JSON/dòng, khoá
`(epKey, id)`). Server FastAPI (127.0.0.1, 1 annotator) **nạp cả file vào RAM**
(`store.STATE`) lúc khởi động và **ghi đè cả file** mỗi mutation (`store.save()`:
tmp → `os.replace`, atomic). Ghi thưa (người click từng clip). Các sự cố đã xảy ra:

1. **Clobber 2-writer:** server giữ `STATE` trong RAM; sửa file trên đĩa (vd
   migration) khi server còn chạy → lần `save()` kế **đè mất** sửa. `threading.Lock`
   (`store.py`) chỉ chặn trong-process, **không** chặn tiến trình OS thứ 2.
2. **Không rollback theo thời điểm:** lịch sử code (git) và data (`state.jsonl`)
   tách rời; không "quay về 17:00 hôm qua".
3. **Backup yếu:** chỉ `.bak-<ts>` thủ công; không xoay vòng, không off-machine.
4. `data/**` gitignored (I1) ⇒ không version, không diff, không remote.

**Nhận định then chốt:** `os.replace` **đã** atomic ⇒ hỏng-ghi-nửa-chừng **không**
phải rủi ro thật. Rủi ro thật = **(a) 2 writer** + **(b) không rollback** — cả hai
sửa rẻ. Và khác media/audio (cấm tuyệt đối), **bản thân nhãn là artifact CC-BY sẽ
release** (đã ship lên Kaggle manifest) ⇒ *về pháp lý* nhãn versionable — nhưng chạm
blanket-ignore `data/**` nên là quyết định policy, không phải kỹ thuật.

**Decision (đề xuất — chờ duyệt):**

1. **Hôm nay, không đổi format (chặn rủi ro thật):** thêm vào `store.py`
   (i) **lock file** (`state.jsonl.lock`) giữ suốt đời process — `set_root`/serve
   **từ chối** nếu lock đang giữ → diệt hẳn sự cố #1; (ii) **backup xoay vòng**:
   snapshot `state.jsonl` có timestamp vào `backups/` mỗi `save()` (hoặc mỗi N phút),
   giữ **N bản gần nhất** → point-in-time recovery (sự cố #2–4). Giữ nguyên
   `tmp→os.replace`. **Mọi writer offline** (vd
   `scripts/vietnamese-ser/migrate_labeler_demographics.py`) **phải tôn trọng lock**
   (nay nó ghi thẳng `state.jsonl`, bypass `store.save()` — chính là writer thứ 2).
2. **Bước bền dài hạn (không gấp, không blocking):** migrate sang **SQLite** stdlib
   `sqlite3`, `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL`. Ở 827 dòng là
   migration trong ngày (1 bảng khoá `(epKey,id)`, `INSERT` 1 lần từ JSONL). Được:
   transaction thật (update theo *dòng*, hết clobber-cả-file), `PRAGMA
   integrity_check` làm health-check định kỳ, hot-backup `VACUUM INTO` khi app mở.
   Vẫn export jsonl/csv cho pipeline. Đây là store chính thức; JSONL-hardening là
   chặn tạm.
3. **Loại:** **Postgres** (service/port/credential cho 1 người local — thừa,
   nghịch simplicity-first) và **Litestream** (giá trị chính là replication
   off-machine liên tục — machinery lớn hơn nhu cầu). Không thêm.
4. **[MỞ — chờ human, I1] Git-version file nhãn:** cho lịch sử/rollback/off-site
   miễn phí trên một artifact *releasable*. Nếu duyệt: làm **additive** (commit
   snapshot **tách** khỏi file working, JSON **sort key** để diff nghĩa lý), **không**
   thay lock+rotation+SQLite. Pitfall: chạm `data/**` gitignore; diff chỉ hữu ích nếu
   key ổn định; không tự giải quyết sự cố #1. **User 2026-07-21: để sau.**

**Consequences (bán kính ảnh hưởng):**

| Chết | Còn nguyên | Đổi |
|---|---|---|
| "1 file JSONL + backup thủ công" là toàn bộ độ bền | **§1 Media legality / I1** (data vẫn local; hardening không đổi ranh giới release) | Store: JSONL full-rewrite → (tạm) JSONL+lock+rotation → (đích) SQLite WAL |
| Nhóm lỗi clobber 2-writer (sau khi có lock) | Pipeline export (`build_kaggle_gold.py` đọc jsonl — SQLite vẫn export jsonl) | Backup: thủ công → xoay vòng tự động (+3-2-1 nếu thêm off-machine) |

**Bằng chứng (research 2026-07-21):**
- SQLite WAL + `synchronous=NORMAL` an toàn crash cho 1 writer, chỉ có thể mất
  **transaction cuối** khi mất điện (không hỏng DB); cần `FULL` nếu không chấp nhận
  mất 1 record. [WAL — sqlite.org](https://sqlite.org/wal.html).
- Hot-backup khi app mở: Backup API / `VACUUM INTO` chạy an toàn trên DB sống.
  [Online Backup API](https://sqlite.org/c3ref/backup_finish.html) ·
  [Backup strategies for SQLite, oldmoe.blog 2024](https://oldmoe.blog/2024/04/30/backup-strategies-for-sqlite-in-production/).
- 1-writer cross-process: lock file advisory (`filelock`) hoặc PID/port check là
  pattern chuẩn Python. [filelock docs](https://py-filelock.readthedocs.io/).
- Git-as-DB: ổn cho text nhỏ append-mostly muốn free history, nhưng chỉ hữu ích khi
  ghi sorted-order; không thay guarantee transaction.
  [So You Want Git for Data?, DoltHub 2020](https://www.dolthub.com/blog/2020-03-06-so-you-want-git-for-data/).
- Backup hygiene: **3-2-1** (3 bản, 2 media, 1 off-site), verify restore.
  [3-2-1 rule](https://captainpragmatic.com/blog/why-3-2-1-backup-rule-still-works/).

**Caveats / rủi ro:**
- Lock file **advisory** — chỉ hiệu lực nếu **mọi** entry point (server, migration
  scripts) đều tôn trọng; script bypass `store.py` vẫn clobber được.
- WAL cần **local filesystem** (không network share) để khoá đúng — hiện đúng
  (`data/vietnamese-ser/episodes/`), kiểm lại nếu đổi máy label.
- `synchronous=NORMAL` có thể mất **transaction cuối** khi mất điện (không hỏng);
  người click từng clip → làm lại 1 nhãn, chấp nhận được. Cần `FULL` nếu không.

**Provenance:** research agent 2026-07-21 (task-researcher, 8 nguồn) + quyết định
user cùng ngày qua hỏi-đáp: "viết ADR trước" (chưa build), git-versioning "để sau".
