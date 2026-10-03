/* Manual segmentation page (cắt thủ công, segment.html?ep=<epKey>): for episodes
   losing context to the auto VAD∩turn cut. Click a YouTube-script block → the
   de-musiced vocals of that block plus one neighbour block each side load as a
   waveform; drag on it to pick the clip span. "＋ đoạn trước/sau" widen the view
   one block at a time. Each span → a new clip (cut from vocals), optionally
   labeled at once. Auto clips are kept (non-destructive). */

import { $, dialectFor, EMO, EMOKEYS, esc } from "./state.js";
import { createSegment, getScript, segmentAudioUrl } from "./api.js";

const fmt = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

const q = new URLSearchParams(location.search);
const EP = q.get("ep") || "";
const ac = new (window.AudioContext || window.webkitAudioContext)();
const audio = new Audio(); // plays the loaded view; currentTime is relative to view.a
let script = []; // YouTube srt blocks [{start,end,text}]
let dur = 0; // full-audio duration
let pick = null; // {i0,i1} blocks clicked (shift-click extends)
let view = null; // {v0,v1,a,b,buf} loaded window = blocks v0..v1 = episode seconds [a,b]
let sel = null; // {a,b} clip span in episode seconds, inside the view
let drag = null; // {t0,x0} mousedown on the waveform
let textKey = ""; // blocks the seed text came from — reseed only when they change
let stopAt = null; // episode second where "nghe vùng chọn" stops
let rafId = null;

async function boot() {
  if (!EP) { $("seg-status").textContent = "⚠ thiếu ?ep=<epKey> — mở từ nút ✂ trong labeler"; return; }
  document.title = "Cắt thủ công — " + EP;
  $("seg-title").textContent = "Cắt thủ công — " + EP;
  $("annotator").value = q.get("annotator") || "human";
  $("seg-status").textContent = "đang tải script…";
  try {
    const d = await getScript(EP);
    script = d.blocks || []; dur = d.duration || 0;
    $("seg-status").textContent = script.length ? `${script.length} block · ${fmt(dur)}` : "";
  } catch { $("seg-status").textContent = "⚠ không tải được script"; }
  renderScript();
  resetForm();
}

function renderScript() {
  $("seg-script").innerHTML = script.length
    ? script.map((b, i) => `<div class="seg-blk" data-i="${i}"><span class="t">${fmt(b.start)}–${fmt(b.end)}</span>${esc(b.text)}</div>`).join("")
    : '<div class="muted" style="padding:8px">Không có script YouTube (.srt) cho tập này.</div>';
  $("seg-script").querySelectorAll(".seg-blk").forEach((el) =>
    (el.onclick = (e) => pickBlock(+el.dataset.i, e.shiftKey)),
  );
  // copy = text only: drop the M:SS–M:SS stamps, join lines with a space
  $("seg-script").oncopy = (e) => {
    const t = getSelection().toString().replace(/\d+:\d\d–\d+:\d\d/g, " ").replace(/\s+/g, " ").trim();
    e.clipboardData.setData("text/plain", t);
    e.preventDefault();
  };
}

// click = that block is the clip, ±1 neighbour loaded as context; shift-click merges
function pickBlock(i, extend) {
  pick = extend && pick ? { i0: Math.min(pick.i0, i), i1: Math.max(pick.i1, i) } : { i0: i, i1: i };
  sel = { a: script[pick.i0].start, b: script[pick.i1].end };
  loadView(pick.i0 - 1, pick.i1 + 1);
}

async function loadView(v0, v1) {
  v0 = Math.max(0, v0); v1 = Math.min(script.length - 1, v1);
  const a = script[v0].start, b = dur ? Math.min(script[v1].end, dur) : script[v1].end;
  const v = (view = { v0, v1, a, b, buf: null });
  audio.pause();
  if (sel) sel = { a: Math.max(sel.a, a), b: Math.min(sel.b, b) };
  onSel();
  $("seg-prev").disabled = v0 === 0;
  $("seg-next").disabled = v1 === script.length - 1;
  try {
    const r = await fetch(segmentAudioUrl(EP, a, b, 0));
    if (!r.ok) throw new Error("http " + r.status);
    const bytes = await r.arrayBuffer();
    if (view !== v) return; // a newer pick superseded this load
    URL.revokeObjectURL(audio.src);
    audio.src = URL.createObjectURL(new Blob([bytes], { type: "audio/wav" })); // Blob copies; decode detaches
    v.buf = await ac.decodeAudioData(bytes);
  } catch { if (view === v) $("seg-info").textContent = "⚠ không tải được audio"; }
  draw();
}

// blocks the selection mostly covers → seed text + highlight
function covered() {
  if (!sel || !view) return [];
  const out = [];
  for (let i = view.v0; i <= view.v1; i++) {
    const b = script[i], ov = Math.min(b.end, sel.b) - Math.max(b.start, sel.a);
    if (ov > 0.5 * Math.min(b.end - b.start, sel.b - sel.a)) out.push(i);
  }
  return out;
}

function onSel() {
  $("seg-info").textContent = sel
    ? `${fmt(sel.a)}–${fmt(sel.b)} (${sel.a.toFixed(1)}–${sel.b.toFixed(1)}s · ${(sel.b - sel.a).toFixed(2)}s)`
    : "chưa chọn vùng";
  const ids = covered(), key = ids.join(",");
  if (key !== textKey) { textKey = key; $("seg-text").value = ids.map((i) => script[i].text).join(" "); }
  $("seg-script").querySelectorAll(".seg-blk").forEach((el) => {
    const i = +el.dataset.i;
    el.classList.toggle("view", !!view && i >= view.v0 && i <= view.v1);
    el.classList.toggle("sel", ids.includes(i));
  });
  draw();
}

function draw() {
  const cv = $("seg-wave"), ctx = cv.getContext("2d");
  cv.width = cv.clientWidth; cv.height = cv.clientHeight;
  const W = cv.width, H = cv.height, mid = H / 2;
  ctx.clearRect(0, 0, W, H);
  if (!view) return;
  const X = (t) => ((t - view.a) / (view.b - view.a)) * W;
  if (sel) { ctx.fillStyle = "rgba(74,144,226,0.28)"; ctx.fillRect(X(sel.a), 0, Math.max(1, X(sel.b) - X(sel.a)), H); }
  // script block boundaries + start stamps
  ctx.strokeStyle = "#3a404d"; ctx.fillStyle = "#9aa0aa"; ctx.font = "10px ui-monospace,monospace";
  for (let i = view.v0; i <= view.v1; i++) {
    const x = Math.round(X(script[i].start)) + 0.5;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    ctx.fillText(fmt(script[i].start), x + 3, 11);
  }
  if (!view.buf) return;
  const d = view.buf.getChannelData(0), spp = d.length / W;
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
  const px = X(view.a + audio.currentTime);
  ctx.strokeStyle = "#fff"; ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
}

/* ---------- waveform mouse: drag = select clip span, plain click = move playhead ---------- */
const toT = (e) => {
  const r = $("seg-wave").getBoundingClientRect();
  return view.a + Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * (view.b - view.a);
};
$("seg-wave").addEventListener("mousedown", (e) => {
  if (view && view.buf) drag = { t0: toT(e), x0: e.clientX };
});
window.addEventListener("mousemove", (e) => {
  if (!drag || Math.abs(e.clientX - drag.x0) < 4) return;
  const t = toT(e);
  sel = { a: Math.min(drag.t0, t), b: Math.max(drag.t0, t) };
  onSel();
});
window.addEventListener("mouseup", (e) => {
  if (drag && Math.abs(e.clientX - drag.x0) < 4) { audio.currentTime = drag.t0 - view.a; draw(); }
  drag = null;
});
window.addEventListener("resize", draw);

/* ---------- playback ---------- */
function loop() {
  if (stopAt != null && view.a + audio.currentTime >= stopAt) audio.pause();
  draw();
  rafId = requestAnimationFrame(loop);
}
audio.onplay = loop;
audio.onpause = audio.onended = () => {
  cancelAnimationFrame(rafId); stopAt = null; draw();
  $("seg-playall").textContent = "▶ phát"; $("seg-play").textContent = "▶ nghe vùng chọn";
};

function playAll() {
  if (!view || !view.buf) return;
  if (!audio.paused) { audio.pause(); return; }
  $("seg-playall").textContent = "⏸ dừng";
  audio.play().catch(() => {});
}

function playSel() {
  if (!sel || !view || !view.buf) return;
  if (!audio.paused) { audio.pause(); return; }
  audio.currentTime = sel.a - view.a; stopAt = sel.b;
  $("seg-play").textContent = "⏸ dừng";
  audio.play().catch(() => {});
}

let gain; // volume boost (>1×), built lazily on first slider drag (a user gesture)
$("gain").oninput = () => {
  const v = +$("gain").value;
  $("gainval").textContent = v.toFixed(1) + "×";
  if (!gain) { gain = ac.createGain(); gain.connect(ac.destination); ac.createMediaElementSource(audio).connect(gain); }
  ac.resume();
  gain.gain.value = v;
};

/* ---------- create clip ---------- */
async function createSeg() {
  if (!sel) { $("seg-status").textContent = "chọn vùng trước"; return; }
  const labelNow = $("seg-label-now").checked;
  if (labelNow && (!$("seg-emotion").value || !$("seg-val").value || !$("seg-aro").value)) {
    $("seg-status").textContent = "⚠ chọn emotion + valence + arousal";
    return;
  }
  const body = { a: sel.a, b: sel.b, text: $("seg-text").value.trim(), label_now: labelNow };
  if (labelNow) Object.assign(body, {
    emotion: $("seg-emotion").value,
    valence: +$("seg-val").value,
    arousal: +$("seg-aro").value,
    gender: $("seg-gender").value,
    age_group: $("seg-age").value,
    dialect: $("seg-dialect").value,
    annotator: ($("annotator").value || "human").trim() || "human",
  });
  let rec;
  try { rec = await createSegment(EP, body); }
  catch { $("seg-status").textContent = "⚠ tạo clip lỗi"; return; }
  $("seg-status").textContent = `✓ đã tạo${labelNow ? " + label" : ""} clip ${rec.id} ${sel.a.toFixed(1)}–${sel.b.toFixed(1)}s`;
  sel = null; textKey = ""; // keep the view loaded: the next clip is usually right beside this one
  resetForm(); onSel();
}

function resetForm() {
  $("seg-text").value = "";
  for (const id of ["seg-emotion", "seg-val", "seg-aro", "seg-gender", "seg-age"]) $(id).value = "";
  $("seg-dialect").value = dialectFor(EP.split("/").slice(0, -1).join("/")); // series = epKey's parent dir
  renderSegEmo();
}

// same colored 7-button row as the main labeler (view.js renderEmoRow); value lives in #seg-emotion
function renderSegEmo() {
  const cur = $("seg-emotion").value;
  $("seg-emorow").innerHTML = EMOKEYS.map((e) =>
    `<div class="emobtn ${e === cur ? "sel" : ""}" data-e="${e}" style="background:${e === cur ? EMO[e] : "transparent"};border-color:${EMO[e]}"><span class="dot" style="background:${EMO[e]}"></span>${e}</div>`
  ).join("");
  $("seg-emorow").querySelectorAll(".emobtn").forEach((b) => (b.onclick = () => { $("seg-emotion").value = b.dataset.e; renderSegEmo(); }));
}

/* ---------- wiring ---------- */
$("seg-prev").onclick = () => view && loadView(view.v0 - 1, view.v1);
$("seg-next").onclick = () => view && loadView(view.v0, view.v1 + 1);
$("seg-playall").onclick = playAll;
$("seg-play").onclick = playSel;
$("seg-create").onclick = createSeg;
$("seg-label-now").onchange = () => {
  const enabled = $("seg-label-now").checked;
  for (const id of ["seg-emotion", "seg-val", "seg-aro", "seg-gender", "seg-age", "seg-dialect"]) $(id).disabled = !enabled;
  $("seg-create").textContent = enabled ? "＋ tạo clip + label" : "＋ tạo clip để label sau";
};
window.addEventListener("keydown", (e) => {
  if (/input|select|textarea|button/i.test(e.target.tagName)) return;
  if (e.code === "Space") { e.preventDefault(); playAll(); }
});

boot();
