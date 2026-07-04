"""Multi-model voice affect tester — a small web UI to pick a model + a sample and run it.

Built to test the emotion2vec reproduction (and the backbone pilot) end-to-end, but
designed to be the *common* tester: it discovers every artifact bundle under a few roots,
reads each `config.json` to figure out the head topology, and lets you choose which model
to run from a dropdown. Add a new `artifact_*/` folder anywhere under a known root and it
shows up automatically.

Run (CPU, local):

    PYTHONPATH=src .venv-voice/bin/uvicorn pebble_llm.serving.voice_tester:app --port 8080

Then open http://localhost:8080 .

Supported head topologies (auto-detected from config.json):
  - "superb-frame"  -> repro v2: Linear->ReLU->masked-mean(frames)->Linear   (emotion only)
  - "superb"        -> repro v1: mean-pool -> Linear->ReLU->Linear            (emotion only)
  - pilot           -> EmotionHead + SafetyHead (config has `safety_threshold`)

emotion2vec bundles need `funasr` installed; if it's absent the model is listed but flagged
unavailable (WavLM bundles run with just transformers).
"""

from __future__ import annotations

import importlib.util
import io
import json
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

REPO_ROOT = Path(__file__).resolve().parents[3]
STATIC = Path(__file__).resolve().parent / "static"

# roots scanned for artifact_* bundles, with a human run-label per root.
ARTIFACT_ROOTS = [
    ("kaggle/voice/pebble-emotion2vec-repro/out2", "repro-v2", "Repro v2 (frame-pool)"),
    ("kaggle/voice/pebble-emotion2vec-repro/out", "repro-v1", "Repro v1 (utt-pool)"),
    ("kaggle/voice/pebble-voice-backbone/out", "pilot", "Pilot (emotion+safety)"),
    ("artifacts/voice", "local", "Local artifact"),
]

# RAVDESS filename field 3 (emotion) -> label.
RAVDESS_EMO = {1: "neutral", 2: "calm", 3: "happy", 4: "sad",
               5: "angry", 6: "fearful", 7: "disgust", 8: "surprised"}


# --------------------------------------------------------------------------- heads
class SuperbSeqHead(nn.Module):  # repro v1 (pooled input)
    def __init__(self, dim, n, hid):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(dim, hid), nn.ReLU(), nn.Linear(hid, n))

    def forward(self, x):
        return self.net(x)


class SuperbFrameHead(nn.Module):  # repro v2 (frame input, pool after first linear)
    def __init__(self, dim, n, hid):
        super().__init__()
        self.pre = nn.Linear(dim, hid)
        self.post = nn.Linear(hid, n)

    def forward(self, x):  # x (T, dim), all frames valid for a single clip
        h = F.relu(self.pre(x))
        return self.post(h.mean(0))


def _head_kind(cfg: dict) -> str:
    h = cfg.get("head")
    if h in ("superb", "superb-frame"):
        return h
    if "safety_threshold" in cfg:
        return "pilot"
    return "superb"


# --------------------------------------------------------------------------- registry
def discover_models() -> dict[str, dict]:
    models: dict[str, dict] = {}
    for rel, runtag, runlabel in ARTIFACT_ROOTS:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for cfg_path in sorted(root.glob("artifact_*/config.json")):
            cfg = json.loads(cfg_path.read_text())
            backbone = cfg.get("backbone", "unknown")
            kind = _head_kind(cfg)
            needs = "funasr" if backbone == "emotion2vec" else None
            available = needs is None or importlib.util.find_spec(needs) is not None
            mid = f"{runtag}--{backbone}"
            models[mid] = {
                "id": mid,
                "label": f"{backbone} — {runlabel}",
                "dir": str(cfg_path.parent),
                "backbone": backbone,
                "head": kind,
                "emotions": cfg["emotions"],
                "needs": needs,
                "available": available,
            }
    return models


def discover_samples() -> dict[str, dict]:
    samples: dict[str, dict] = {}
    # one RAVDESS clip per emotion from a held-out actor (truth known from filename).
    ravdess = REPO_ROOT / "data/voice/external/ravdess"
    if ravdess.exists():
        for emo_code, emo in RAVDESS_EMO.items():
            hit = None
            for actor in ("Actor_21", "Actor_22", "Actor_23", "Actor_24"):
                cand = sorted((ravdess / actor).glob(f"03-01-{emo_code:02d}-*.wav"))
                if cand:
                    hit = cand[0]
                    break
            if hit:
                sid = f"ravdess-{emo}"
                samples[sid] = {"id": sid, "label": f"RAVDESS · {emo}", "truth": emo,
                                "path": str(hit)}
    # bundled sample_val.wav from each run dir.
    for rel, runtag, _ in ARTIFACT_ROOTS:
        wav = REPO_ROOT / rel / "sample_val.wav"
        if wav.exists():
            sid = f"sample-{runtag}"
            samples[sid] = {"id": sid, "label": f"bundled · {runtag}", "truth": None,
                            "path": str(wav)}
    return samples


# --------------------------------------------------------------------------- runner
def _load_wav(path_or_bytes, sr: int, max_samples: int, frame_mode: bool) -> np.ndarray:
    import soundfile as sf
    import torchaudio
    src = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
    wav, fsr = sf.read(src, dtype="float32", always_2d=True)
    wav = wav.mean(axis=1)
    if fsr != sr:
        wav = torchaudio.functional.resample(torch.from_numpy(wav), fsr, sr).numpy()
    wav = wav[:max_samples]
    if not frame_mode and len(wav) < max_samples:  # pooled heads were trained on padded clips
        wav = np.pad(wav, (0, max_samples - len(wav)))
    return wav.astype(np.float32)


class Runner:
    def __init__(self, meta: dict):
        self.meta = meta
        self.dir = Path(meta["dir"])
        self.cfg = json.loads((self.dir / "config.json").read_text())
        self.kind = meta["head"]
        self.emotions = meta["emotions"]
        self.sr = self.cfg["sample_rate"]
        self.max_samples = self.cfg["max_samples"]
        self.frame_mode = self.kind == "superb-frame"
        dim = self.cfg["embed_dim"]
        self._embed = self._build_backbone()

        if self.kind == "superb-frame":
            self.head = SuperbFrameHead(dim, len(self.emotions), self.cfg["head_dim"])
            self.head.load_state_dict(torch.load(self.dir / "emotion_head.pt", map_location="cpu"))
            self.head.eval()
            self.safety = None
        elif self.kind == "superb":
            self.head = SuperbSeqHead(dim, len(self.emotions), self.cfg["head_dim"])
            self.head.load_state_dict(torch.load(self.dir / "emotion_head.pt", map_location="cpu"))
            self.head.eval()
            self.safety = None
        else:  # pilot: emotion + safety
            from pebble_llm.models.heads import EmotionHead, SafetyHead
            self.head = EmotionHead(dim, len(self.emotions), head_dim=self.cfg["head_dim"])
            self.safety = SafetyHead(dim, head_dim=self.cfg.get("safety_head_dim", 64))
            self.head.load_state_dict(torch.load(self.dir / "emotion_head.pt", map_location="cpu"))
            self.safety.load_state_dict(torch.load(self.dir / "safety_head.pt", map_location="cpu"))
            self.head.eval(); self.safety.eval()
            self.threshold = self.cfg.get("safety_threshold", 0.5)

    def _build_backbone(self):
        backbone = self.cfg["backbone"]
        if backbone == "emotion2vec":
            from funasr import AutoModel as FunASR
            import soundfile as sf
            import os, tempfile
            try:
                model = FunASR(model="iic/emotion2vec_base", hub="hf", disable_update=True)
            except Exception:
                from huggingface_hub import snapshot_download
                model = FunASR(model=snapshot_download("emotion2vec/emotion2vec_base"),
                               disable_update=True)
            gran = "frame" if self.frame_mode else "utterance"

            def embed(wav):
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    sf.write(tf.name, wav, self.sr); path = tf.name
                r = model.generate(path, granularity=gran, extract_embedding=True, output_dir=None)
                os.remove(path)
                f = torch.tensor(np.asarray(r[0]["feats"], dtype=np.float32))
                return f  # (T,dim) for frame, (dim,) for utterance
            return embed

        from transformers import AutoFeatureExtractor, WavLMModel
        fe = AutoFeatureExtractor.from_pretrained(self.cfg["backbone_hf_id"])
        enc = WavLMModel.from_pretrained(self.cfg["backbone_hf_id"]).eval()

        @torch.no_grad()
        def embed(wav):
            inp = fe(wav, sampling_rate=self.sr, return_tensors="pt")
            h = enc(**inp).last_hidden_state.squeeze(0)  # (T, dim)
            return h if self.frame_mode else h.mean(0)   # (T,dim) or (dim,)
        return embed

    @torch.no_grad()
    def infer(self, wav: np.ndarray) -> dict:
        t0 = time.time()
        emb = self._embed(wav)
        if self.kind == "superb-frame":
            logits = self.head(emb)                       # head pools frames internally
        else:
            logits = self.head(emb.unsqueeze(0)).squeeze(0)
        probs = F.softmax(logits, dim=-1).numpy()
        top = int(probs.argmax())
        out = {"emotion": self.emotions[top],
               "probs": {e: round(float(p), 4) for e, p in zip(self.emotions, probs)},
               "latency_ms": round((time.time() - t0) * 1000)}
        if self.safety is not None:
            distress = float(torch.sigmoid(self.safety(emb.unsqueeze(0))).item())
            out["distress"] = round(distress, 4)
            out["safety_flag"] = distress >= self.threshold
        return out


@lru_cache(maxsize=8)
def get_runner(model_id: str) -> Runner:
    models = discover_models()
    if model_id not in models:
        raise HTTPException(404, f"unknown model {model_id}")
    meta = models[model_id]
    if not meta["available"]:
        raise HTTPException(409, f"model needs '{meta['needs']}' which is not installed")
    return Runner(meta)


# --------------------------------------------------------------------------- app
app = FastAPI(title="Pebble Voice Model Tester", version="0.1.0")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "voice_tester.html")


@app.get("/api/models")
def api_models() -> JSONResponse:
    return JSONResponse(list(discover_models().values()))


@app.get("/api/samples")
def api_samples() -> JSONResponse:
    pub = [{k: v for k, v in s.items() if k != "path"} for s in discover_samples().values()]
    return JSONResponse(pub)


@app.get("/api/sample-audio/{sample_id}")
def api_sample_audio(sample_id: str) -> FileResponse:
    s = discover_samples().get(sample_id)
    if not s:
        raise HTTPException(404, "unknown sample")
    return FileResponse(s["path"], media_type="audio/wav")


@app.post("/api/infer")
async def api_infer(model_id: str = Form(...), sample_id: str = Form(None),
                    file: UploadFile = File(None)) -> JSONResponse:
    runner = get_runner(model_id)
    if file is not None:
        raw = await file.read()
        if not raw:
            raise HTTPException(400, "empty upload")
        wav = _load_wav(raw, runner.sr, runner.max_samples, runner.frame_mode)
        truth = None
    elif sample_id:
        s = discover_samples().get(sample_id)
        if not s:
            raise HTTPException(404, "unknown sample")
        wav = _load_wav(s["path"], runner.sr, runner.max_samples, runner.frame_mode)
        truth = s["truth"]
    else:
        raise HTTPException(400, "provide sample_id or file")
    result = runner.infer(wav)
    result.update({"model": runner.meta["label"], "backbone": runner.cfg["backbone"],
                   "head": runner.kind, "truth": truth})
    return JSONResponse(result)
