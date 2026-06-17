"""Tiny local web UI for the shipped Pebble model.

Loads the model once (via infer.py), then serves a single page + a /analyze
JSON endpoint. Stdlib only — no extra deps.

    python serve.py            # http://127.0.0.1:8000
    python serve.py 8080       # custom port
"""
import sys, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from infer import analyze  # loads model on import

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pebble — emotion & severity</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; }
  h1 { font-size: 1.3rem; margin-bottom: .2rem; }
  .sub { color: #888; font-size: .85rem; margin-bottom: 1.2rem; }
  textarea { width: 100%; min-height: 90px; font-size: 1rem; padding: 10px; box-sizing: border-box;
             border: 1px solid #aaa6; border-radius: 8px; resize: vertical; }
  button { margin-top: 10px; padding: 9px 20px; font-size: 1rem; border: 0; border-radius: 8px;
           background: #4f46e5; color: #fff; cursor: pointer; }
  button:disabled { opacity: .5; cursor: default; }
  #out { margin-top: 24px; }
  .sev-label { display: flex; justify-content: space-between; font-size: .85rem; color: #888; }
  .bar { height: 14px; border-radius: 7px; background: #8884; overflow: hidden; margin: 4px 0 18px; }
  .bar > span { display: block; height: 100%; border-radius: 7px; }
  .emo { display: grid; grid-template-columns: 120px 1fr 52px; align-items: center; gap: 8px; margin: 6px 0; }
  .emo .track { height: 10px; background: #8883; border-radius: 5px; overflow: hidden; }
  .emo .track > span { display: block; height: 100%; background: #4f46e5; }
  .emo .pct { text-align: right; font-variant-numeric: tabular-nums; color: #888; font-size: .85rem; }
  .name { font-size: .9rem; }
</style></head>
<body>
  <h1>Pebble — emotion &amp; severity</h1>
  <div class="sub">NeoBERT fine-tune (MLM-off, seed 42) · 28 GoEmotions classes · severity 0–1 · English, short text</div>
  <textarea id="t" placeholder="Type a sentence…">I can't do this anymore, nothing matters</textarea><br>
  <button id="go">Analyze</button>
  <div id="out"></div>
<script>
const go = document.getElementById('go'), t = document.getElementById('t'), out = document.getElementById('out');
function sevColor(s){ const h = (1 - s) * 120; return `hsl(${h} 70% 45%)`; }
async function run(){
  const text = t.value.trim(); if(!text) return;
  go.disabled = true; go.textContent = '…';
  try {
    const r = await fetch('/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})});
    const d = await r.json();
    const max = Math.max(...d.emotions.map(e => e[1]), 0.001);
    out.innerHTML =
      `<div class="sev-label"><span>severity</span><b>${d.severity.toFixed(3)}</b></div>`
      + `<div class="bar"><span style="width:${(d.severity*100).toFixed(1)}%;background:${sevColor(d.severity)}"></span></div>`
      + d.emotions.map(([name,p]) =>
          `<div class="emo"><span class="name">${name}</span>`
          + `<span class="track"><span style="width:${(p/max*100).toFixed(1)}%"></span></span>`
          + `<span class="pct">${(p*100).toFixed(1)}%</span></div>`).join('');
  } catch(e){ out.textContent = 'error: ' + e; }
  go.disabled = false; go.textContent = 'Analyze';
}
go.onclick = run;
t.addEventListener('keydown', e => { if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)) run(); });
</script>
</body></html>"""


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/analyze":
            return self._send(404, b"not found", "text/plain")
        n = int(self.headers.get("Content-Length", 0))
        try:
            text = json.loads(self.rfile.read(n))["text"]
            body = json.dumps(analyze(text, topk=5)).encode("utf-8")
            self._send(200, body, "application/json")
        except Exception as e:
            self._send(400, json.dumps({"error": str(e)}).encode("utf-8"), "application/json")

    def log_message(self, *a):  # quiet
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
print(f"serving on http://127.0.0.1:{port}  (Ctrl+C to stop)")
ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
