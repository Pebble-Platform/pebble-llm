/* All server calls in one place (backend = server.py). Leaf module: no imports. */

const path = (k) => k.split("/").map(encodeURIComponent).join("/");

export const clipUrl = (k, id) => "/clip/" + path(k) + "/" + id + ".wav";

async function post(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body != null ? JSON.stringify(body) : null,
  });
  if (!r.ok) throw new Error("http " + r.status);
  return r.json();
}

export const getEpisodes = () => fetch("/episodes").then((r) => r.json());
export const getEpisode = (k) => fetch("/episode/" + path(k)).then((r) => r.json());
export const getGold = () => fetch("/gold").then((r) => r.json());

export const saveGold = (k, id, body) => post("/gold/" + path(k) + "/" + id, body);
export const recut = (k, id, body) => post("/recut/" + path(k) + "/" + id, body);
export const recutUndo = (k, id) => post("/recut/" + path(k) + "/" + id + "/undo");
export const reject = (k, id, reason) => post("/reject/" + path(k) + "/" + id, { reason });
export const rejectUndo = (k, id) => post("/reject/" + path(k) + "/" + id + "/undo");
export const split = (k, id, t) => post("/split/" + path(k) + "/" + id, { t });
