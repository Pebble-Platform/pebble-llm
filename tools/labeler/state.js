/* Shared kernel: constants, DOM/format helpers, and the one mutable state object.
   Every module reads/writes S.<field> (import bindings can't be reassigned). */

export const EMO = {
  joy: "#f6c744", sadness: "#4a78c4", anger: "#d64545", fear_anxiety: "#8a5cd6",
  surprise: "#38b2a3", disgust: "#8a9a3a", neutral: "#8a8f98",
};
export const EMOKEYS = Object.keys(EMO); // index -> emotion, key 1..7

export const $ = (id) => document.getElementById(id);
export const gk = (ep, id) => ep + "\t" + id;
export const esc = (s) =>
  (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

export const S = {
  episodes: {}, // epKey -> {series,epName,total,done,rejected}
  gold: {}, // "epKey\tid" -> saved record (cache of state.jsonl)
  curEp: null,
  clips: [],
  curIdx: -1,
  curEmotion: null,
  cutMode: false, cutSel: null, cutDrag: false, // recut (F1)
  splitMode: false, splitPoints: [], // split (F5) — multiple cut points, kept ascending
  epSpeakers: [], // speaker dropdown (F6)
  recap: null, recapIds: new Set(), // detect-recap (change 006): last result + clip ids to mark
  audio: new Audio(),
  audioBuf: null,
  rafId: null,
};
