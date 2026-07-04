"""Voice model tester — Hugging Face Space (Docker) entrypoint.

Self-contained FastAPI app that serves the emotion2vec / WavLM reproduction heads on the
cloud so a local client can call them over HTTP. Standalone (no pebble_llm import) so the
Space builds from this folder alone. funasr installs cleanly on the Space's Linux image, so
**emotion2vec runs here** even though it can't run on the Intel-mac local env.

Models discovered from $VOICE_TESTER_ROOTS (default ./models), samples from
$VOICE_TESTER_SAMPLES (default ./samples). Backbone weights download from HF Hub at boot.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

HERE = Path(__file__).resolve().parent
ROOTS = [Path(p) for p in os.environ.get("VOICE_TESTER_ROOTS", str(HERE / "models")).split(":")]
SAMPLE_DIR = Path(os.environ.get("VOICE_TESTER_SAMPLES", str(HERE / "samples")))
STATIC = HERE / "static"

RAVDESS_EMO = {1: "neutral", 2: "calm", 3: "happy", 4: "sad",
               5: "angry", 6: "fearful", 7: "disgust", 8: "surprised"}


class SuperbSeqHead(nn.Module):       # repro v1 (pooled input)
    def __init__(self, dim, n, hid):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(dim, hid), nn.ReLU(), nn.Linear(hid, n))

    def forward(self, x):
        return self.net(x)


class SuperbFrameHead(nn.Module):     # repro v2 (frame input, pool after first linear)
    def __init__(self, dim, n, hid):
        super().__init__()
        self.pre = nn.Linear(dim, hid)
        self.post = nn.Linear(hid, n)

    def forward(self, x):             # x (T, dim)
        h = F.relu(self.pre(x))
        return self.post(h.mean(0))


def discover_models() -> dict[str, dict]:
    models: dict[str, dict] = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for cfg_path in sorted(root.glob("artifact_*/config.json")):
            cfg = json.loads(cfg_path.read_text())
            backbone = cfg.get("backbone", "unknown")
            kind = cfg.get("head", "superb")
            needs = "funasr" if backbone == "emotion2vec" else None
            available = needs is None or importlib.util.find_spec(needs) is not None
            mid = f"{cfg_path.parent.name.replace('artifact_', '')}--{kind}"
            models[mid] = {"id": mid, "label": f"{backbone} · {kind}", "dir": str(cfg_path.parent),
                           "backbone": backbone, "head": kind, "emotions": cfg["emotions"],
                           "needs": needs, "available": available}
    return models


def discover_samples() -> dict[str, dict]:
    samples: dict[str, dict] = {}
    if SAMPLE_DIR.exists():
        for wav in sorted(SAMPLE_DIR.glob("*.wav")):
            parts = wav.stem.split("-")
            truth = None
            if len(parts) >= 3 and parts[0] == "03" and parts[2].isdigit():
                truth = RAVDESS_EMO.get(int(parts[2]))
            sid = wav.stem
            samples[sid] = {"id": sid, "label": (f"RAVDESS · {truth}" if truth else wav.stem),
                            "truth": truth, "path": str(wav)}
    return samples


def _load_wav(src, sr: int, max_samples: int, frame_mode: bool) -> np.ndarray:
    import soundfile as sf
    import torchaudio
    buf = io.BytesIO(src) if isinstance(src, bytes) else src
    wav, fsr = sf.read(buf, dtype="float32", always_2d=True)
    wav = wav.mean(axis=1)
    if fsr != sr:
        wav = torchaudio.functional.resample(torch.from_numpy(wav), fsr, sr).numpy()
    wav = wav[:max_samples]
    if not frame_mode and len(wav) < max_samples:
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
        HeadCls = SuperbFrameHead if self.frame_mode else SuperbSeqHead
        self.head = HeadCls(dim, len(self.emotions), self.cfg["head_dim"])
        self.head.load_state_dict(torch.load(self.dir / "emotion_head.pt", map_location="cpu"))
        self.head.eval()

    def _build_backbone(self):
        if self.cfg["backbone"] == "emotion2vec":
            from funasr import AutoModel as FunASR
            import soundfile as sf
            import tempfile
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
                return torch.tensor(np.asarray(r[0]["feats"], dtype=np.float32))
            return embed

        from transformers import AutoFeatureExtractor, WavLMModel
        fe = AutoFeatureExtractor.from_pretrained(self.cfg["backbone_hf_id"])
        enc = WavLMModel.from_pretrained(self.cfg["backbone_hf_id"]).eval()

        @torch.no_grad()
        def embed(wav):
            inp = fe(wav, sampling_rate=self.sr, return_tensors="pt")
            h = enc(**inp).last_hidden_state.squeeze(0)
            return h if self.frame_mode else h.mean(0)
        return embed

    @torch.no_grad()
    def infer(self, wav: np.ndarray) -> dict:
        t0 = time.time()
        emb = self._embed(wav)
        logits = self.head(emb) if self.frame_mode else self.head(emb.unsqueeze(0)).squeeze(0)
        probs = F.softmax(logits, dim=-1).numpy()
        top = int(probs.argmax())
        return {"emotion": self.emotions[top],
                "probs": {e: round(float(p), 4) for e, p in zip(self.emotions, probs)},
                "latency_ms": round((time.time() - t0) * 1000)}


@lru_cache(maxsize=8)
def get_runner(model_id: str) -> Runner:
    models = discover_models()
    if model_id not in models:
        raise HTTPException(404, f"unknown model {model_id}")
    if not models[model_id]["available"]:
        raise HTTPException(409, f"model needs '{models[model_id]['needs']}' (not installed)")
    return Runner(models[model_id])


app = FastAPI(title="Pebble Voice Model Tester", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/models")
def api_models():
    return JSONResponse(list(discover_models().values()))


@app.get("/api/samples")
def api_samples():
    return JSONResponse([{k: v for k, v in s.items() if k != "path"}
                         for s in discover_samples().values()])


@app.get("/api/sample-audio/{sample_id}")
def api_sample_audio(sample_id: str):
    s = discover_samples().get(sample_id)
    if not s:
        raise HTTPException(404, "unknown sample")
    return FileResponse(s["path"], media_type="audio/wav")


@app.post("/api/infer")
async def api_infer(model_id: str = Form(...), sample_id: str = Form(None),
                    file: UploadFile = File(None)):
    runner = get_runner(model_id)
    if file is not None:
        raw = await file.read()
        if not raw:
            raise HTTPException(400, "empty upload")
        wav, truth = _load_wav(raw, runner.sr, runner.max_samples, runner.frame_mode), None
    elif sample_id:
        s = discover_samples().get(sample_id)
        if not s:
            raise HTTPException(404, "unknown sample")
        wav, truth = _load_wav(s["path"], runner.sr, runner.max_samples, runner.frame_mode), s["truth"]
    else:
        raise HTTPException(400, "provide sample_id or file")
    result = runner.infer(wav)
    result.update({"model": runner.meta["label"], "backbone": runner.cfg["backbone"],
                   "head": runner.kind, "truth": truth})
    return JSONResponse(result)
