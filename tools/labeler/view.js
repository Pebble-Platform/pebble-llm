/* View layer: waveform/audio drawing + sidebar/table/emo/speaker rendering +
   episode load / clip select. Reads & writes S; calls the api layer. */

import { $, EMO, EMOKEYS, esc, gk, S } from "./state.js";
import { clipUrl, getEpisode, getEpisodes } from "./api.js";

/* ---------- waveform + audio ---------- */
export function drawWave() {
  const cv = $("wave"), ctx = cv.getContext("2d");
  cv.width = cv.clientWidth; cv.height = cv.clientHeight;
  const W = cv.width, H = cv.height, mid = H / 2;
  ctx.clearRect(0, 0, W, H);
  if (!S.audioBuf) return;
  const d = S.audioBuf.getChannelData(0), spp = d.length / W;
  ctx.strokeStyle = "#6b8fb5"; ctx.beginPath();
  for (let x = 0; x < W; x++) {
    let mn = 1, mx = -1;
    const a = Math.floor(x * spp), b = Math.floor((x + 1) * spp);
    for (let i = a; i < b; i++) { const v = d[i]; if (v < mn) mn = v; if (v > mx) mx = v; }
    if (mn > mx) { mn = 0; mx = 0; }
    ctx.moveTo(x + 0.5, mid - mx * mid * 0.95);
    ctx.lineTo(x + 0.5, mid - mn * mid * 0.95);
  }
  ctx.stroke();
  if (S.cutSel && S.audioBuf.duration) {
    const x0 = Math.min(S.cutSel.a, S.cutSel.b) / S.audioBuf.duration * W;
    const x1 = Math.max(S.cutSel.a, S.cutSel.b) / S.audioBuf.duration * W;
    ctx.fillStyle = "rgba(74,144,226,0.28)"; ctx.fillRect(x0, 0, Math.max(1, x1 - x0), H);
  }
  if (S.splitMode && S.splitPoints.length && S.audioBuf.duration) {
    ctx.strokeStyle = "#e0a83a"; ctx.lineWidth = 2;
    for (const t of S.splitPoints) {
      const px = t / S.audioBuf.duration * W;
      ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
    }
    ctx.lineWidth = 1;
  }
  if (S.audioBuf.duration) {
    const px = S.audio.currentTime / S.audioBuf.duration * W;
    ctx.strokeStyle = "#fff"; ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
  }
}

export function loop() { drawWave(); S.rafId = requestAnimationFrame(loop); }

/* split (F5) button label: "chia (k+1)" while in split mode, static otherwise */
export function updateSplitBtnLabel() {
  $("splitdo").textContent = S.splitMode ? `✔ chia (${S.splitPoints.length + 1})` : "✔ chia";
}

export function xToTime(e) {
  const r = $("wave").getBoundingClientRect();
  const x = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
  return x * (S.audioBuf ? S.audioBuf.duration : 0);
}

S.audio.onplay = () => loop();
S.audio.onpause = () => { cancelAnimationFrame(S.rafId); drawWave(); };

/* ---------- sidebar / progress ---------- */
export function updateProg() {
  let d = 0, t = 0;
  for (const ep of Object.values(S.episodes)) { d += ep.done || 0; t += ep.total - (ep.rejected || 0); }
  $("prog").textContent = t ? `· Σ ${d}/${t} (${Math.round((d / t) * 100)}%)` : "";
}

export function renderSidebar() {
  const bySeries = {};
  for (const [k, ep] of Object.entries(S.episodes)) (bySeries[ep.series] ??= []).push([k, ep]);
  const el = $("sidebar"); el.innerHTML = "";
  for (const [series, eps] of Object.entries(bySeries)) {
    const h = document.createElement("div"); h.className = "series"; h.textContent = series;
    el.appendChild(h);
    eps.sort((a, b) => a[1].epName.localeCompare(b[1].epName, undefined, { numeric: true }));
    for (const [k, ep] of eps) {
      const rej = ep.rejected || 0, done = ep.done || 0, eff = ep.total - rej;
      const d = document.createElement("div");
      d.className = "epitem" + (k === S.curEp ? " active" : "");
      d.innerHTML = `<span>${ep.epName}</span><span class="badge ${done === eff && eff ? "done" : ""}">${done}/${eff}${rej ? ` ⚑${rej}` : ""}</span>`;
      d.onclick = () => openEpisode(k);
      el.appendChild(d);
    }
  }
  updateProg();
}

/* ---------- clip table ---------- */
function tLbl(x) {
  return x
    ? `${x.emotion} V${x.valence}A${x.arousal}${x.distress === "True" || x.distress === true || x.distress === "true" ? " ☂" : ""}`
    : "—";
}

export function renderTable() {
  const tb = $("cliptable");
  if (!S.clips.length) {
    tb.innerHTML = '<tbody><tr><td class="empty">Tập này không có clip</td></tr></tbody>';
    return;
  }
  const rows = S.clips.map((c, i) => {
    const g = S.gold[gk(S.curEp, c.id)];
    const txt = (g && g.gold_text) || c.asr || "";
    return `<tr class="clip${i === S.curIdx ? " active" : ""}${S.recapIds.has(c.id) ? " recap" : ""}" ${g && g.rejected ? 'style="opacity:.45"' : ""} data-i="${i}">
      <td>${i === S.curIdx ? "▶" : ""}</td>
      <td>${c.id}</td><td>${(c.end - c.start).toFixed(1)}s</td>
      <td class="txt" title="${esc(txt)}">${esc(txt) || "<i class=muted>—</i>"}</td>
      <td>${c.disagree ? "<span class=flag>☠ khác</span>" : ""}</td>
      <td>${g && g.rejected ? "<span class=flag>⚑ loại</span>" : g && g.emotion ? `<span class="st-done">✓ ${g.emotion}</span>` : '<span class="st-todo">chưa</span>'}${g && g.recut ? " <span class=flag>✂</span>" : ""}</td>
      <td>${g && g.valence != null ? g.valence : "—"}</td>
      <td>${g && g.arousal != null ? g.arousal : "—"}</td>
    </tr>`;
  }).join("");
  tb.innerHTML = `<thead><tr><th></th><th>id</th><th>dur</th><th>gold text</th><th></th><th>gold</th><th>V</th><th>A</th></tr></thead><tbody>${rows}</tbody>`;
  tb.querySelectorAll("tr.clip").forEach((tr) => (tr.onclick = () => selectClip(+tr.dataset.i)));
}

export function renderEmoRow() {
  $("emorow").innerHTML = EMOKEYS.map((e, i) =>
    `<div class="emobtn ${e === S.curEmotion ? "sel" : ""}" data-e="${e}" style="background:${e === S.curEmotion ? EMO[e] : "transparent"};border-color:${EMO[e]}"><span class="dot" style="background:${EMO[e]}"></span>${e}<span class="kbd">${i + 1}</span></div>`
  ).join("");
  $("emorow").querySelectorAll(".emobtn").forEach((b) => (b.onclick = () => { S.curEmotion = b.dataset.e; renderEmoRow(); }));
}

/* ---------- speaker dropdown (F6) ---------- */
export function fillSpk(cur) {
  cur = cur || "";
  if (cur && !S.epSpeakers.includes(cur)) S.epSpeakers.push(cur);
  $("g-spk").innerHTML = ['<option value="">—</option>']
    .concat(S.epSpeakers.map((s) => `<option${s === cur ? " selected" : ""}>${esc(s)}</option>`))
    .concat('<option value="__new__">＋ mới…</option>')
    .join("");
  $("g-spk").value = cur;
}

/* ---------- load / open / select ---------- */
export async function loadEpisodes() {
  let list;
  try { list = await getEpisodes(); }
  catch { $("loaded").textContent = "không nối được backend (chạy server.py?)"; return; }
  S.episodes = {};
  for (const e of list)
    S.episodes[e.epKey] = { series: e.series, epName: e.epName, total: e.total, done: e.done || 0, rejected: e.rejected || 0 };
  $("loaded").textContent = list.length ? `${list.length} phần tập` : "không thấy tập nào";
  renderSidebar();
}

export async function openEpisode(epKey) {
  S.curEp = epKey;
  S.recap = null; S.recapIds = new Set(); $("recap-panel").classList.add("hidden"); // clear stale recap
  let data = { clips: [], speakers: [] };
  try { data = await getEpisode(epKey); } catch {}
  S.clips = data.clips || []; S.epSpeakers = (data.speakers || []).slice();
  for (const c of S.clips) if (c.gold) S.gold[gk(epKey, c.id)] = c.gold;
  renderSidebar(); renderTable(); S.curIdx = -1;
  const firstTodo = S.clips.findIndex((c) => !S.gold[gk(epKey, c.id)]);
  selectClip(firstTodo < 0 ? 0 : firstTodo);
}

export async function selectClip(i) {
  if (i < 0 || i >= S.clips.length) return;
  S.curIdx = i; const c = S.clips[i];
  $("detail").classList.remove("hidden");
  $("clipid").textContent = c.id;
  $("cliptime").textContent = `${c.start.toFixed(1)}–${c.end.toFixed(1)}s`;
  $("tx-asr").textContent = c.asr || "—"; $("tx-yt").textContent = c.yt || "—";
  $("th-opus").innerHTML = c.opus ? tLbl(c.opus) : "—";
  $("th-sonnet").innerHTML = c.sonnet ? tLbl(c.sonnet) : "—";
  $("th-flag").innerHTML = c.disagree ? '<span class="disagree">☠ 2 teacher bất đồng emotion</span>' : "";
  // load saved human label if any — KHÔNG pre-fill từ teacher (ADR-003)
  const g = S.gold[gk(S.curEp, c.id)]; const labeled = !!(g && g.emotion);
  S.curEmotion = labeled ? g.emotion : null;
  $("g-val").value = labeled ? g.valence : ""; $("g-aro").value = labeled ? g.arousal : "";
  $("g-text").value = g && g.gold_text ? g.gold_text : c.asr || "";
  $("g-status").textContent = labeled ? "✓ đã lưu" : "chưa gán";
  $("g-status").className = labeled ? "st-done" : "muted";
  S.cutMode = false; S.cutSel = null; $("cutbtn").classList.remove("primary");
  S.splitMode = false; S.splitPoints = []; $("splitbtn").classList.remove("primary"); updateSplitBtnLabel();
  $("cutinfo").textContent = g && g.recut ? "✂ đã recut" : "";
  fillSpk(g && g.speaker != null ? g.speaker : c.speaker || "");
  const rj = !!(g && g.rejected);
  $("rej-reason").value = (g && g.reject_reason) || "multi_speaker";
  $("rejbtn").textContent = rj ? "↺ bỏ loại" : "⚑ loại";
  if (rj) { $("g-status").textContent = "⚑ đã loại: " + (g.reject_reason || ""); $("g-status").className = "flag"; }
  renderEmoRow(); renderTable();
  // audio + waveform — cache-bust ?v= (đổi theo ts/biên) để <audio> nạp lại bản
  // trimmed sau recut/split (gán src=URL-y-hệt sẽ KHÔNG reload dù server no-store)
  const v = (g && g.ts) || `${c.start}_${c.end}`;
  const url = clipUrl(S.curEp, c.id) + "?v=" + encodeURIComponent(v);
  S.audio.src = url;
  try {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    S.audioBuf = await ac.decodeAudioData(await (await fetch(url)).arrayBuffer());
    drawWave();
  } catch { S.audioBuf = null; }
}

export async function reopenClip(targetId) {
  const id = targetId || S.clips[S.curIdx]?.id, i = S.curIdx;
  try {
    const data = await getEpisode(S.curEp);
    S.clips = data.clips || []; S.epSpeakers = (data.speakers || []).slice();
    for (const c of S.clips) if (c.gold) S.gold[gk(S.curEp, c.id)] = c.gold;
  } catch {}
  const ni = S.clips.findIndex((c) => c.id === id);
  selectClip(ni < 0 ? Math.min(i, S.clips.length - 1) : ni);
}
