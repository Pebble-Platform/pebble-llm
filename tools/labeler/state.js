/* Shared kernel: constants, DOM/format helpers, and the one mutable state object.
   Every module reads/writes S.<field> (import bindings can't be reassigned). */

export const EMO = {
  joy: "#f6c744", sadness: "#4a78c4", anger: "#d64545", fear_anxiety: "#8a5cd6",
  surprise: "#38b2a3", disgust: "#8a9a3a", neutral: "#8a8f98",
};
export const EMOKEYS = Object.keys(EMO); // index -> emotion, key 1..7

// stored code -> Vietnamese label (mirrors the <select> options in index.html)
export const GENDER_VI = { female: "nữ", male: "nam" };
export const AGE_VI = {
  child: "trẻ em", teen: "thiếu niên", young_adult: "thanh niên",
  middle_aged: "trung niên", senior: "cao tuổi",
};

export const $ = (id) => document.getElementById(id);
export const gk = (ep, id) => ep + "\t" + id;
export const esc = (s) =>
  (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

export const S = {
  episodes: {}, // epKey -> {series,epName,total,done,rejected}
  gold: {}, // "epKey\tid" -> saved record (cache of state.db)
  curEp: null,
  clips: [],
  curIdx: -1,
  curEmotion: null,
  cutMode: false, cutSel: null, cutDrag: false, // recut (F1)
  splitMode: false, splitPoints: [], // split (F5) — multiple cut points, kept ascending
  selIds: new Set(), // multi-select for bulk-remove (loại nhiều clip) — clip ids checked in the table
  audio: new Audio(),
  audioBuf: null,
  rafId: null,
  preview: new Audio(), // context preview (±pad s from full episode audio) — separate from clip audio
  // manual segmentation (cắt thủ công): pick spans on full de-musiced audio via YT script
  script: [], // YouTube srt blocks [{start,end,text}]
  segDur: 0, // full-audio duration
  segSel: null, // current span {i0,i1,a,b,text} (i0..i1 = selected script blocks)
  segBuf: null, // selection waveform buffer
  segAudio: new Audio(), // selection preview player (separate from clip/context)
};
