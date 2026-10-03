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
export const DIALECT_VI = { north: "Bắc", central: "Trung", south: "Nam" };
// A whole production is shot in one region, so the dialect default belongs to the
// SERIES, not the tool. Kept in code (not the gitignored data root) so the default
// applied to any label is recoverable from git history.
export const SERIES_DIALECT = { "cay-tao-no-hoa": "south" };
export const dialectFor = (series) => SERIES_DIALECT[series] || "north";
export const curDialect = () => dialectFor((S.episodes[S.curEp] || {}).series);

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
};
