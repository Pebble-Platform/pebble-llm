// Per-clip comparison of every rater's judgment (change 011) — owner-only.
//
// iaa_report.py answers "how much do raters agree overall"; this answers "what did
// everyone actually say about THIS clip", which is where you look when a class scores
// badly and you want to know whether the clips are ambiguous or the guideline is.
//
// Disagreeing clips sort first (server-side): the agreeing ones need no attention.

const $ = (id) => document.getElementById(id);
let data = { annotators: [], rows: [] };
let filter = "all";
let audio = null;

const cell = (answers, majority) => {
  if (!answers?.length) return '<td class="cell"><span class="va">—</span></td>';
  const one = (a) => {
    if (a.skip) return `<span class="skip">⊘ ${a.skip}</span>`;
    const va = a.valence == null ? "" : ` <span class="va">V${a.valence} A${a.arousal}</span>`;
    return `<b>${a.emotion}</b>${va}`;
  };
  const differs = answers[0].emotion && answers[0].emotion !== majority;
  const extra = answers.slice(1).map((a) => `<span class="dup">${one(a)}</span>`).join("");
  return `<td class="cell${differs ? " diff" : ""}">${one(answers[0])}${extra}</td>`;
};

const passes = (r) => {
  if (filter === "diff") return !r.unanimous;
  if (filter === "none") return r.majority === "no_agreement";
  if (filter === "skip") return Object.values(r.ratings).some((a) => a.some((x) => x.skip));
  if (filter === "dup") return Object.values(r.ratings).some((a) => a.length > 1);
  return true;
};

function render() {
  const anns = data.annotators;
  $("thead").innerHTML =
    "<tr><th>clip</th><th>owner</th>" +
    anns.map((a) => `<th>${a}</th>`).join("") +
    "<th>đa số</th><th></th></tr>";

  const shown = data.rows.filter(passes);
  $("rows").innerHTML = shown
    .map((r) => {
      const maj = r.majority;
      const tags = r.kind.filter((k) => k !== "normal").map((k) => `<span class="tag">${k}</span>`).join("");
      return `<tr class="${r.unanimous ? "una" : ""}">
        <td class="key">${r.key}${tags}</td>
        ${cell(r.owner.emotion ? [r.owner] : [], maj)}
        ${anns.map((a) => cell(r.ratings[a], maj)).join("")}
        <td class="maj${maj === "no_agreement" ? " none" : ""}">${maj}
          <span class="va">${r.n_votes} phiếu</span></td>
        <td><button data-wav="${r.wav}">▶</button></td>
      </tr>`;
    })
    .join("");

  const tot = data.rows.length;
  const dis = data.rows.filter((r) => !r.unanimous).length;
  const na = data.rows.filter((r) => r.majority === "no_agreement").length;
  $("counts").innerHTML =
    `hiện <b>${shown.length}</b> / ${tot} clip · bất đồng <b>${dis}</b> ` +
    `(${tot ? ((100 * dis) / tot).toFixed(1) : 0}%) · no_agreement <b>${na}</b> · ` +
    `rater: ${anns.join(", ") || "(chưa có)"}`;
}

$("rows").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-wav]");
  if (!b) return;
  audio?.pause();
  audio = new Audio(b.dataset.wav);
  audio.play().catch(() => {});
});

document.querySelector(".filters").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-f]");
  if (!b) return;
  filter = b.dataset.f;
  for (const x of document.querySelectorAll("[data-f]")) {
    x.setAttribute("aria-pressed", String(x === b));
  }
  render();
});

fetch("/review")
  .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
  .then((d) => {
    data = d;
    if (!d.rows.length) {
      $("counts").textContent =
        "Chưa có lượt gán nào — chạy một vòng label trước (xem RUNBOOK.md).";
      return;
    }
    render();
  })
  .catch(() => {
    $("counts").textContent = "Không tải được /review.";
  });
