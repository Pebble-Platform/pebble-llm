// Gold-set audition (change 011, qc-protocol §2.1 step 2) — owner-only.
//
// Step 1 (three-way agreement + stratified draw) is already done by
// pick_gold_candidates.py. This screen is step 2, the part that CANNOT be automated:
// the owner listens and keeps only the clips that are obvious.
//
// Rows start as "keep" because they survived three-way agreement — the job is to DROP
// the unclear ones. But a row is only counted as confirmed once its audio has actually
// been played, and saving warns about unheard rows: otherwise "listen to each one"
// quietly degrades into clicking save, and the QC gate ends up resting on clips nobody
// ever checked.

const $ = (id) => document.getElementById(id);
let rows = [];
let cur = 0;
let audio = null;

const render = () => {
  $("rows").innerHTML = rows
    .map(
      (r, i) => `<tr class="${i === cur ? "cur" : ""}${r.keep ? "" : " drop"}" data-i="${i}">
        <td class="emo">${r.emotion}</td>
        <td class="key">${r.key}</td>
        <td class="act">
          <button class="play${r.heard ? " heard" : ""}" data-a="play">
            ${r.heard ? "▶ nghe lại" : "▶ nghe"}</button>
          <button class="keep" data-on="${r.keep ? 1 : 0}" data-a="toggle">
            ${r.keep ? "giữ" : "loại"}</button>
          ${r.keep && !r.heard ? '<span class="unheard">chưa nghe</span>' : ""}
        </td>
      </tr>`,
    )
    .join("");

  const keep = rows.filter((r) => r.keep);
  const unheard = keep.filter((r) => !r.heard).length;
  const byClass = {};
  for (const r of keep) byClass[r.emotion] = (byClass[r.emotion] || 0) + 1;
  $("counts").innerHTML =
    `giữ <b>${keep.length}</b> / ${rows.length}` +
    (unheard ? ` · <b style="color:#dc2626">${unheard} chưa nghe</b>` : "") +
    " · " +
    Object.entries(byClass)
      .map(([k, v]) => `${k} ${v}`)
      .join(" · ");
  document.querySelector("tr.cur")?.scrollIntoView({ block: "nearest" });
};

const play = (i) => {
  cur = i;
  audio?.pause();
  audio = new Audio(rows[i].wav);
  audio.play().catch(() => {});
  rows[i].heard = true;
  render();
};

const move = (d) => {
  cur = Math.max(0, Math.min(rows.length - 1, cur + d));
  render();
};

const toggle = (i) => {
  rows[i].keep = !rows[i].keep;
  cur = i;
  render();
};

$("rows").addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  const tr = e.target.closest("tr");
  if (!tr) return;
  const i = Number(tr.dataset.i);
  if (btn?.dataset.a === "play") play(i);
  else if (btn?.dataset.a === "toggle") toggle(i);
  else {
    cur = i;
    render();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.altKey || e.metaKey) return;
  const k = e.key.toLowerCase();
  if (e.code === "Space") {
    e.preventDefault();
    play(cur);
  } else if (k === "k") {
    rows[cur].keep = true;
    move(1);
  } else if (k === "d") {
    rows[cur].keep = false;
    move(1);
  } else if (k === "j" || k === "n" || e.key === "ArrowDown") {
    e.preventDefault();
    move(1);
  } else if (k === "p" || e.key === "ArrowUp") {
    e.preventDefault();
    move(-1);
  }
});

$("save").addEventListener("click", async () => {
  const keep = rows.filter((r) => r.keep);
  const unheard = keep.filter((r) => !r.heard);
  if (unheard.length) {
    const ok = confirm(
      `${unheard.length} clip được GIỮ nhưng chưa nghe.\n\n` +
        "Gold chưa nghe là gold không kiểm chứng — cả QC gate sẽ dựa lên nó.\n" +
        "Vẫn ghi?",
    );
    if (!ok) return;
  }
  try {
    const r = await fetch("/gold-set", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keys: keep.map((x) => x.key) }),
    });
    if (!r.ok) throw new Error(r.status);
    const j = await r.json();
    $("msg").textContent = `đã ghi ${j.written} dòng → gold-set.txt`;
  } catch {
    $("msg").textContent = "ghi lỗi — xem log server";
  }
});

fetch("/gold-candidates")
  .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
  .then((d) => {
    rows = d.map((r) => ({ ...r, heard: false }));
    render();
  })
  .catch(() => {
    $("counts").textContent =
      "Chưa có gold-candidates.tsv — chạy scripts/vietnamese-ser/pick_gold_candidates.py trước.";
  });
