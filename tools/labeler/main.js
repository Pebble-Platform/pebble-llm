/* Composition root: wire DOM events to actions/view, keyboard, and boot. */

import { $, EMOKEYS, S } from "./state.js";
import { drawWave, fillSpk, loadEpisodes, renderEmoRow, selectClip, updateSplitBtnLabel, xToTime } from "./view.js";
import { confirmGold, detectRecap, dismissRecap, exportCsv, exportZip, markRecap, saveCut, saveExcise, saveSplit, toggleReject, undoCut } from "./actions.js";

/* ---------- buttons ---------- */
$("reload").onclick = loadEpisodes;
$("recapbtn").onclick = detectRecap;
$("recap-mark").onclick = markRecap;
$("recap-dismiss").onclick = dismissRecap;
$("confirm").onclick = confirmGold;
$("rejbtn").onclick = toggleReject;
$("cutsave").onclick = saveCut;
$("excisesave").onclick = saveExcise;
$("cutundo").onclick = undoCut;
$("splitdo").onclick = saveSplit;
$("expcsv").onclick = exportCsv;
$("expzip").onclick = exportZip;
$("next").onclick = () => selectClip(Math.min(S.clips.length - 1, S.curIdx + 1));
$("prev").onclick = () => selectClip(Math.max(0, S.curIdx - 1));
$("play").onclick = () => (S.audio.paused ? S.audio.play() : S.audio.pause());

/* ---------- cut / split mode toggles ---------- */
$("cutbtn").onclick = () => {
  if (!S.audioBuf) return;
  S.cutMode = !S.cutMode; S.cutSel = null;
  $("cutbtn").classList.toggle("primary", S.cutMode);
  $("cutinfo").textContent = S.cutMode ? "kéo chọn đoạn — ✔ lưu cắt = GIỮ đoạn đó · ⌦ bỏ giữa = XOÁ đoạn đó" : "";
  drawWave();
};
$("splitbtn").onclick = () => {
  if (!S.audioBuf) return;
  S.splitMode = !S.splitMode; S.splitPoints = []; S.cutMode = false; S.cutSel = null;
  $("splitbtn").classList.toggle("primary", S.splitMode);
  $("cutbtn").classList.remove("primary");
  $("cutinfo").textContent = S.splitMode ? "click trên sóng để thêm điểm chia (click lại điểm để bỏ)" : "";
  updateSplitBtnLabel();
  drawWave();
};

/* ---------- waveform mouse ---------- */
$("wave").addEventListener("mousedown", (e) => {
  if (S.splitMode && S.audioBuf) {
    const t = xToTime(e), dur = S.audioBuf.duration || 1, W = $("wave").clientWidth || 1;
    const pxThresh = 6, tThresh = (pxThresh / W) * dur; // click near an existing marker removes it
    const idx = S.splitPoints.findIndex((p) => Math.abs(p - t) < tThresh);
    if (idx >= 0) S.splitPoints.splice(idx, 1);
    else { S.splitPoints.push(t); S.splitPoints.sort((a, b) => a - b); }
    $("cutinfo").textContent = S.splitPoints.length
      ? `điểm chia: ${S.splitPoints.map((p) => p.toFixed(2)).join(", ")}s`
      : "click trên sóng để thêm điểm chia (click lại điểm để bỏ)";
    updateSplitBtnLabel();
    drawWave();
    return;
  }
  if (!S.audioBuf) return;
  if (!S.cutMode) { S.audio.currentTime = xToTime(e); drawWave(); return; } // normal mode → seek playhead
  S.cutDrag = true; const t = xToTime(e); S.cutSel = { a: t, b: t }; drawWave();
});
$("wave").addEventListener("mousemove", (e) => {
  if (!S.cutDrag) return;
  S.cutSel.b = xToTime(e);
  $("cutinfo").textContent = `giữ ${Math.min(S.cutSel.a, S.cutSel.b).toFixed(2)}–${Math.max(S.cutSel.a, S.cutSel.b).toFixed(2)}s`;
  drawWave();
});
window.addEventListener("mouseup", () => { S.cutDrag = false; });
window.addEventListener("resize", drawWave);

/* ---------- speaker "＋ mới" (F6) ---------- */
$("g-spk").onchange = () => {
  if ($("g-spk").value !== "__new__") return;
  const s = (prompt("speaker id mới:") || "").trim();
  if (s) { if (!S.epSpeakers.includes(s)) S.epSpeakers.push(s); fillSpk(s); } else fillSpk("");
};

/* ---------- keyboard ---------- */
window.addEventListener("keydown", (e) => {
  if (/input|select|textarea/i.test(e.target.tagName)) return;
  if (e.code === "Space") { e.preventDefault(); $("play").click(); }
  else if (e.key >= "1" && e.key <= "7") { S.curEmotion = EMOKEYS[+e.key - 1]; renderEmoRow(); }
  else if (e.key === "Enter") confirmGold();
  else if (e.key.toLowerCase() === "n") selectClip(Math.min(S.clips.length - 1, S.curIdx + 1));
  else if (e.key.toLowerCase() === "p") selectClip(Math.max(0, S.curIdx - 1));
});

/* ---------- boot ---------- */
loadEpisodes();
