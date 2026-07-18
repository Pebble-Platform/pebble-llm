/* User actions triggered from the UI: label/recut/split/reject + export.
   Talks to the api layer and asks the view layer to re-render. */

import { $, gk, S } from "./state.js";
import * as api from "./api.js";
import { loadEpisodes, renderSidebar, renderTable, reopenClip, selectClip } from "./view.js";

/* ---------- label (F1) ---------- */
export async function confirmGold() {
  if (S.curIdx < 0) return;
  if (!S.curEmotion) { $("g-status").textContent = "⚠ chọn emotion trước (phím 1–7)"; $("g-status").className = "flag"; return; }
  if (!$("g-val").value || !$("g-aro").value) { $("g-status").textContent = "⚠ chọn valence + arousal"; $("g-status").className = "flag"; return; }
  const c = S.clips[S.curIdx];
  const body = {
    emotion: S.curEmotion, valence: +$("g-val").value, arousal: +$("g-aro").value,
    gold_text: $("g-text").value.trim(),
    speaker: $("g-spk").value === "__new__" ? "" : $("g-spk").value,
    annotator: ($("annotator").value || "human").trim() || "human",
  };
  let rec;
  try { rec = await api.saveGold(S.curEp, c.id, body); }
  catch { $("g-status").textContent = "⚠ lưu lỗi (server?)"; $("g-status").className = "flag"; return; }
  const isNew = !S.gold[gk(S.curEp, c.id)];
  S.gold[gk(S.curEp, c.id)] = rec;
  if (isNew && S.episodes[S.curEp]) S.episodes[S.curEp].done = (S.episodes[S.curEp].done || 0) + 1;
  renderSidebar();
  const nextTodo = S.clips.findIndex((cc, i) => i > S.curIdx && !S.gold[gk(S.curEp, cc.id)]);
  if (nextTodo >= 0) selectClip(nextTodo);
  else { renderTable(); $("g-status").textContent = "✓ đã lưu"; $("g-status").className = "st-done"; }
}

/* ---------- reject (F3) ---------- */
export async function toggleReject() {
  if (S.curIdx < 0) return;
  const c = S.clips[S.curIdx], g = S.gold[gk(S.curEp, c.id)], rejecting = !(g && g.rejected);
  let rec;
  try { rec = rejecting ? await api.reject(S.curEp, c.id, $("rej-reason").value) : await api.rejectUndo(S.curEp, c.id); }
  catch { $("g-status").textContent = "⚠ lỗi reject"; $("g-status").className = "flag"; return; }
  S.gold[gk(S.curEp, c.id)] = rec;
  await loadEpisodes(); // refresh done/rejected counts từ server
  if (rejecting) {
    const nx = S.clips.findIndex((cc, i) => i > S.curIdx && !S.gold[gk(S.curEp, cc.id)]);
    selectClip(nx >= 0 ? nx : S.curIdx);
  } else selectClip(S.curIdx);
}

/* ---------- recut (F1) ---------- */
export async function saveCut() {
  if (!S.cutMode || !S.cutSel || !S.audioBuf) { $("cutinfo").textContent = "bấm ✂ cắt rồi kéo chọn"; return; }
  const a = Math.min(S.cutSel.a, S.cutSel.b), b = Math.max(S.cutSel.a, S.cutSel.b);
  if (b - a < 0.05) { $("cutinfo").textContent = "đoạn quá ngắn"; return; }
  const c = S.clips[S.curIdx];
  try { await api.recut(S.curEp, c.id, { a, b, text: $("g-text").value.trim() }); }
  catch { $("cutinfo").textContent = "⚠ cắt lỗi"; return; }
  await reopenClip();
}

export async function undoCut() {
  const c = S.clips[S.curIdx];
  try { await api.recutUndo(S.curEp, c.id); }
  catch { $("cutinfo").textContent = "⚠ không có bản gốc"; return; }
  await reopenClip();
}

/* ---------- excise middle chunk (removes selection, keeps ONE clip) ---------- */
export async function saveExcise() {
  if (!S.cutMode || !S.cutSel || !S.audioBuf) { $("cutinfo").textContent = "bấm ✂ cắt rồi kéo chọn đoạn cần bỏ"; return; }
  const a = Math.min(S.cutSel.a, S.cutSel.b), b = Math.max(S.cutSel.a, S.cutSel.b);
  if (b - a < 0.05) { $("cutinfo").textContent = "đoạn quá ngắn"; return; }
  if (a < 0.05 || b > S.audioBuf.duration - 0.05) { $("cutinfo").textContent = "đoạn bỏ phải nằm GIỮA (dùng ✔ lưu cắt cho mép)"; return; }
  const c = S.clips[S.curIdx];
  try { await api.excise(S.curEp, c.id, { a, b, text: $("g-text").value.trim() }); }
  catch { $("cutinfo").textContent = "⚠ bỏ giữa lỗi"; return; }
  await reopenClip();
}

/* ---------- split (F5) ---------- */
export async function saveSplit() {
  if (!S.splitMode || !S.splitPoints.length || !S.audioBuf) { $("cutinfo").textContent = "bấm ⁄ chia rồi click điểm"; return; }
  const ts = [...S.splitPoints].sort((a, b) => a - b);
  if (ts[0] < 0.05 || ts[ts.length - 1] > S.audioBuf.duration - 0.05) { $("cutinfo").textContent = "điểm chia quá sát mép"; return; }
  const c = S.clips[S.curIdx];
  let res;
  try { res = await api.split(S.curEp, c.id, ts); }
  catch { $("cutinfo").textContent = "⚠ chia lỗi"; return; }
  S.splitMode = false; S.splitPoints = []; $("splitbtn").classList.remove("primary");
  const firstChild = res.children && res.children[0] && res.children[0].id;
  await loadEpisodes();
  await reopenClip(firstChild);
}

/* ---------- detect + bulk-mark duplicate recap (change 006) ---------- */
export async function detectRecap() {
  if (!S.curEp) return;
  const info = $("recap-info");
  $("recap-panel").classList.remove("hidden");
  $("recap-mark").style.display = "none";
  info.textContent = "đang dò recap so với tập trước…";
  let r;
  try { r = await api.detectRecap(S.curEp); }
  catch { info.textContent = "⚠ lỗi dò recap"; return; }
  if (r.detail) { info.textContent = "⚠ " + r.detail; return; } // 404/err body {detail}
  S.recap = r; S.recapIds = new Set(r.clip_ids || []);
  renderTable();
  if (!S.recapIds.size) {
    info.textContent = `không thấy clip trùng (điểm ${r.score}, ${r.run_s}s)`;
    return;
  }
  const cs = r.cur_span, ps = r.prev_span, tag = r.matched ? "TRÙNG" : "nghi ngờ (điểm thấp)";
  info.textContent = `${tag}: ${S.recapIds.size} clip [${cs[0]}–${cs[1]}s] ≈ ${r.prev_epKey} [${ps[0]}–${ps[1]}s] · điểm ${r.score}, ${r.run_s}s`;
  $("recap-mark").style.display = "";
  $("recap-mark").textContent = `✓ đánh dấu trùng (${S.recapIds.size})`;
  const i = S.clips.findIndex((c) => S.recapIds.has(c.id)); // jump so user can listen first
  if (i >= 0) selectClip(i);
}

export async function markRecap() {
  const r = S.recap;
  if (!r || !S.recapIds.size) return;
  const dup = { epKey: r.prev_epKey, t0: r.prev_span[0], t1: r.prev_span[1] };
  try { await api.rejectBulk(S.curEp, [...S.recapIds], "duplicate", dup); }
  catch { $("recap-info").textContent = "⚠ lỗi đánh dấu"; return; }
  dismissRecap();
  await loadEpisodes();
  await reopenClip();
}

export function dismissRecap() {
  S.recap = null; S.recapIds = new Set();
  $("recap-panel").classList.add("hidden");
  renderTable();
}

/* ---------- export (raw state dump; Kaggle export = phase 4) ---------- */
const COLS = ["id", "series", "episode", "speaker", "start", "end", "gold_emotion", "gold_valence",
  "gold_arousal", "gold_distress", "gold_text", "opus_emotion", "sonnet_emotion",
  "teacher_agree", "note", "annotator"];

async function goldRows() {
  let recs = []; try { recs = await api.getGold(); } catch {}
  return recs.map((g) => ({ k: g.epKey, ep: { series: g.series, epName: g.episode }, id: g.id, g }));
}

function csvCell(v) { v = String(v); return /[",\r\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }

async function buildCSV() {
  const out = await goldRows();
  const rows = [COLS];
  for (const { ep, id, g } of out) {
    const agree = g.opus && g.sonnet ? g.opus === g.sonnet : "";
    rows.push([id, ep.series, ep.epName, g.speaker ?? "", g.start ?? "", g.end ?? "", g.emotion,
      g.valence, g.arousal, g.distress, g.gold_text || "", g.opus || "", g.sonnet || "", agree, g.note || "", g.annotator || ""]);
  }
  return { csv: rows.map((r) => r.map(csvCell).join(",")).join("\r\n"), n: out.length };
}

function dl(blob, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = name; a.click();
}

export async function exportCsv() {
  const { csv, n } = await buildCSV();
  if (!n) return alert("Chưa có nhãn nào");
  dl(new Blob(["﻿" + csv], { type: "text/csv" }), "gold.csv");
}

export async function exportZip() {
  const out = await goldRows();
  if (!out.length) return alert("Chưa có nhãn nào");
  const { csv } = await buildCSV();
  const files = [{ name: "gold.csv", data: new TextEncoder().encode("﻿" + csv) }];
  for (const { k, ep, id } of out) {
    const buf = await (await fetch(api.clipUrl(k, id))).arrayBuffer();
    files.push({ name: `${ep.epName}__${id}.wav`, data: new Uint8Array(buf) });
  }
  dl(new Blob([makeZip(files)], { type: "application/zip" }), "gold_bundle.zip");
}

/* store-only ZIP (verified) */
const CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function crc32(u8) { let c = 0xffffffff; for (let i = 0; i < u8.length; i++) c = CRC[(c ^ u8[i]) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }
function makeZip(files) {
  const enc = new TextEncoder(), parts = [], central = []; let offset = 0;
  for (const f of files) {
    const name = enc.encode(f.name), data = f.data, crc = crc32(data);
    const lh = new DataView(new ArrayBuffer(30));
    lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true); lh.setUint32(14, crc, true);
    lh.setUint32(18, data.length, true); lh.setUint32(22, data.length, true); lh.setUint16(26, name.length, true);
    parts.push(new Uint8Array(lh.buffer), name, data);
    const cd = new DataView(new ArrayBuffer(46));
    cd.setUint32(0, 0x02014b50, true); cd.setUint16(4, 20, true); cd.setUint16(6, 20, true);
    cd.setUint32(16, crc, true); cd.setUint32(20, data.length, true); cd.setUint32(24, data.length, true);
    cd.setUint16(28, name.length, true); cd.setUint32(42, offset, true);
    central.push(new Uint8Array(cd.buffer), name); offset += 30 + name.length + data.length;
  }
  let cdSize = 0; central.forEach((p) => (cdSize += p.length));
  const eocd = new DataView(new ArrayBuffer(22));
  eocd.setUint32(0, 0x06054b50, true); eocd.setUint16(8, files.length, true); eocd.setUint16(10, files.length, true);
  eocd.setUint32(12, cdSize, true); eocd.setUint32(16, offset, true);
  const all = [...parts, ...central, new Uint8Array(eocd.buffer)];
  let total = 0; all.forEach((p) => (total += p.length));
  const out = new Uint8Array(total); let o = 0; all.forEach((p) => { out.set(p, o); o += p.length; });
  return out;
}
