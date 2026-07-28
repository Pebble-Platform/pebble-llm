// Annotator rating screen (change 011, M4) — deliberately the smallest surface that
// can collect one judgment.
//
// BLIND BY CONSTRUCTION, and that is the point (see change 011 README):
//   * no transcript      — this corpus is about the VOICE; text drags judgment toward
//                          what was said instead of how it was said;
//   * no teacher hints   — ADR-003 lets the owner see them; an anchored second rater
//                          would make kappa meaningless;
//   * no owner label, no other annotator's label, no episode/clip id, no clip table.
// Audio is addressed by QUEUE POSITION only (/rate/clip/<seq>.wav), so the annotator
// never learns a clip identity and cannot enumerate (ADR-005 safeguards #2/#4).

const EMOTIONS = [
  ["joy", "vui"], ["sadness", "buồn"], ["anger", "giận"], ["fear_anxiety", "sợ / lo"],
  ["surprise", "bất ngờ"], ["disgust", "ghê tởm"], ["neutral", "trung tính"],
];

// Token arrives once in the URL, then lives in this tab only. Stripped from the
// address bar immediately so it is not left in screenshots or shoulder-surfed.
const url = new URL(location.href);
const token = url.searchParams.get("t") || sessionStorage.getItem("vt") || "";
if (url.searchParams.has("t")) {
  sessionStorage.setItem("vt", token);
  history.replaceState(null, "", url.pathname);
}

const $ = (id) => document.getElementById(id);
const app = $("app"), msg = $("msg");
const S = { seq: null, emotion: "", valence: null, arousal: null, listenMs: 0, sending: false };
let audio = null, playStart = 0;

const api = async (path, opts = {}) => {
  const r = await fetch(path, {
    ...opts,
    headers: { "X-Token": token, "Content-Type": "application/json", ...(opts.headers || {}) },
  });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
};

// ---------- option buttons ----------
function buildOptions() {
  $("emo").innerHTML = EMOTIONS.map(
    ([v, label], i) =>
      `<button data-k="emotion" data-v="${v}" aria-pressed="false">${label}<kbd>${i + 1}</kbd></button>`,
  ).join("");
  for (const k of ["val", "aro"]) {
    $(k).innerHTML = [1, 2, 3, 4, 5]
      .map((n) => `<button data-k="${k === "val" ? "valence" : "arousal"}" data-v="${n}"
                   aria-pressed="false">${n}</button>`)
      .join("");
  }
  document.querySelectorAll("[data-k]").forEach((b) =>
    b.addEventListener("click", () => pick(b.dataset.k, b.dataset.v)),
  );
}

function pick(key, value) {
  S[key] = key === "emotion" ? value : Number(value);
  for (const b of document.querySelectorAll(`[data-k="${key}"]`)) {
    b.setAttribute("aria-pressed", String(b.dataset.v === String(value)));
  }
  $("send").disabled = !(S.emotion && S.valence && S.arousal);
}

// ---------- audio: play time is measured, not guessed (QC protocol 2.3) ----------
function play() {
  if (S.seq === null) return;
  if (!audio) {
    audio = new Audio(`/rate/clip/${S.seq}.wav?t=${encodeURIComponent(token)}`);
    audio.addEventListener("play", () => (playStart = performance.now()));
    const stop = () => {
      if (playStart) S.listenMs += Math.round(performance.now() - playStart);
      playStart = 0;
    };
    audio.addEventListener("pause", stop);
    audio.addEventListener("ended", stop);
  }
  audio.currentTime = 0;
  audio.play().catch(() => {});
}

// ---------- queue ----------
async function load() {
  const st = await api("/rate/next");
  $("who").textContent = `${st.done} / ${st.total}`;
  if (st.seq === null) {
    app.hidden = true;
    msg.hidden = false;
    msg.innerHTML = `<b>Xong rồi — cảm ơn anh/chị!</b><br>
      <span style="color:#6b7280">Đã gán ${st.done} clip. Có thể đóng tab.</span>`;
    return;
  }
  Object.assign(S, { seq: st.seq, emotion: "", valence: null, arousal: null, listenMs: 0 });
  audio = null;
  document.querySelectorAll("[data-k]").forEach((b) => b.setAttribute("aria-pressed", "false"));
  $("send").disabled = true;
  $("skipbox").style.display = "none";
  msg.hidden = true;
  app.hidden = false;
  play(); // autoplay; the browser may block it, hence the visible Nghe button
}

async function submit(body) {
  if (S.sending) return;
  S.sending = true;
  try {
    await api(`/rate/${S.seq}`, { method: "POST", body: JSON.stringify(body) });
    await load();
  } catch {
    alert("Không lưu được — kiểm tra kết nối rồi thử lại.");
  } finally {
    S.sending = false;
  }
}

const send = () =>
  !$("send").disabled &&
  submit({
    emotion: S.emotion,
    valence: S.valence,
    arousal: S.arousal,
    listen_ms: S.listenMs,
  });

// ---------- wiring ----------
buildOptions();
$("play").addEventListener("click", play);
$("send").addEventListener("click", send);
$("skip").addEventListener("click", () => {
  const box = $("skipbox");
  box.style.display = box.style.display === "block" ? "none" : "block";
});
$("skipgo").addEventListener("click", () =>
  submit({ skip_reason: $("skipwhy").value, listen_ms: S.listenMs }),
);

document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "SELECT" || e.ctrlKey || e.altKey || e.metaKey) return;
  if (e.code === "Space") {
    e.preventDefault();
    play();
  } else if (e.key === "Enter") {
    send();
  } else if (e.key >= "1" && e.key <= "7") {
    pick("emotion", EMOTIONS[Number(e.key) - 1][0]);
  }
});

load().catch(() => {
  msg.innerHTML = `<b>Không truy cập được.</b><br>
    <span style="color:#6b7280">Đường link có thể sai hoặc đã hết hạn —
    nhắn cho người phụ trách để lấy link mới.</span>`;
});
