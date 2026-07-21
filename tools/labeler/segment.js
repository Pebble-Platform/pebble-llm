/* Manual segmentation (cắt thủ công): for episodes losing context to the auto
   VAD∩turn cut, view the full de-musiced audio via the YouTube script and pick
   spans by hand. Each span → a new clip (cut from vocals) seeded with the YT text,
   dropped into the clip table to label. Auto clips are kept (non-destructive). */

import { $, esc, S } from "./state.js";
import { createSegment, getScript, segmentAudioUrl } from "./api.js";
import { reopenClip } from "./view.js";

const fmt = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

export async function openSegment() {
  if (!S.curEp) return;
  $("segment").classList.remove("hidden");
  $("seg-title").textContent = "Cắt thủ công — " + S.curEp;
  $("seg-status").textContent = "đang tải script…";
  S.script = []; S.segDur = 0;
  try {
    const d = await getScript(S.curEp);
    S.script = d.blocks || []; S.segDur = d.duration || 0;
  } catch { $("seg-status").textContent = "⚠ không tải được script"; }
  renderScript();
  $("seg-status").textContent = S.script.length ? `${S.script.length} block · ${fmt(S.segDur)}` : "";
  clearSel();
}

export function closeSegment() {
  $("segment").classList.add("hidden");
  S.segAudio.pause();
}

function renderScript() {
  $("seg-script").innerHTML = S.script.length
    ? S.script.map((b, i) => `<div class="seg-blk" data-i="${i}"><span class="t">${fmt(b.start)}–${fmt(b.end)}</span>${esc(b.text)}</div>`).join("")
    : '<div class="muted" style="padding:8px">Không có script YouTube (.srt) cho tập này — cắt bằng tai qua ± ngữ cảnh.</div>';
  $("seg-script").querySelectorAll(".seg-blk").forEach((el) =>
    (el.onclick = (e) => pickBlock(+el.dataset.i, e.shiftKey)),
  );
}

function pickBlock(i, extend) {
  if (extend && S.segSel) {
    S.segSel.i0 = Math.min(S.segSel.i0, i);
    S.segSel.i1 = Math.max(S.segSel.i1, i);
  } else {
    S.segSel = { i0: i, i1: i, a: 0, b: 0, text: "" };
  }
  const s = S.segSel;
  s.a = S.script[s.i0].start; s.b = S.script[s.i1].end;
  s.text = S.script.slice(s.i0, s.i1 + 1).map((x) => x.text).join(" ");
  $("seg-text").value = s.text;
  markSel();
  refreshSel();
}

function markSel() {
  $("seg-script").querySelectorAll(".seg-blk").forEach((el) => {
    const i = +el.dataset.i;
    el.classList.toggle("sel", !!S.segSel && i >= S.segSel.i0 && i <= S.segSel.i1);
  });
}

export function nudge(edge, d) {
  const s = S.segSel;
  if (!s) return;
  if (edge === "a") s.a = Math.max(0, Math.min(s.a + d, s.b - 0.1));
  else s.b = Math.max(s.a + 0.1, S.segDur ? Math.min(s.b + d, S.segDur) : s.b + d);
  refreshSel();
}

async function refreshSel() {
  const s = S.segSel;
  if (!s) { $("seg-info").textContent = "chưa chọn vùng"; S.segBuf = null; drawSegWave(); return; }
  $("seg-info").textContent = `${fmt(s.a)}–${fmt(s.b)} (${s.a.toFixed(1)}–${s.b.toFixed(1)}s · ${(s.b - s.a).toFixed(2)}s)`;
  try {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    S.segBuf = await ac.decodeAudioData(await (await fetch(segmentAudioUrl(S.curEp, s.a, s.b, 0))).arrayBuffer());
  } catch { S.segBuf = null; }
  drawSegWave();
}

function drawSegWave() {
  const cv = $("seg-wave"), ctx = cv.getContext("2d");
  cv.width = cv.clientWidth; cv.height = cv.clientHeight;
  const W = cv.width, H = cv.height, mid = H / 2;
  ctx.clearRect(0, 0, W, H);
  if (!S.segBuf) return;
  const d = S.segBuf.getChannelData(0), spp = d.length / W;
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
}

export function playSel() {
  const s = S.segSel;
  if (!s) return;
  if (!S.segAudio.paused) { S.segAudio.pause(); return; }
  const pad = +$("seg-pad").value || 0;
  S.segAudio.src = segmentAudioUrl(S.curEp, s.a, s.b, pad) + "&v=" + Date.now();
  S.segAudio.play().catch(() => {});
}

export async function createSeg() {
  const s = S.segSel;
  if (!s) { $("seg-status").textContent = "chọn vùng trước"; return; }
  try { await createSegment(S.curEp, { a: s.a, b: s.b, text: $("seg-text").value.trim() }); }
  catch { $("seg-status").textContent = "⚠ tạo clip lỗi"; return; }
  $("seg-status").textContent = `✓ đã tạo clip ${s.a.toFixed(1)}–${s.b.toFixed(1)}s`;
  clearSel();
  await reopenClip(); // refresh the table behind the overlay — new clip appears
}

function clearSel() {
  S.segSel = null; S.segBuf = null;
  $("seg-text").value = ""; $("seg-info").textContent = "chưa chọn vùng";
  markSel(); drawSegWave();
}
