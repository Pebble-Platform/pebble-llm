"""Voice serving tests — waveform preprocessing + the classify path.

The backbone is stubbed so these run with no model download / no network; the
real encoders are exercised by scripts/voice_local_smoke.py + the Kaggle run.
"""

import io
import json

import numpy as np
import soundfile as sf
import torch

from pebble_llm.models.heads import EmotionHead, SafetyHead
from pebble_llm.serving.voice_inference import VoiceClassifier, load_waveform

EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]


def test_load_waveform_resamples_and_pads_to_fixed_length():
    sr_in, secs = 8000, 1.0
    t = np.linspace(0, secs, int(sr_in * secs), endpoint=False)
    sine = (0.1 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    buf = io.BytesIO()
    sf.write(buf, sine, sr_in, format="WAV")
    wav = load_waveform(buf.getvalue(), target_sr=16000, max_samples=64000)
    assert wav.shape == (64000,)
    assert wav.dtype == np.float32


def test_load_waveform_truncates_long_audio():
    sr = 16000
    long = np.zeros(sr * 6, dtype=np.float32)
    buf = io.BytesIO()
    sf.write(buf, long, sr, format="WAV")
    wav = load_waveform(buf.getvalue(), target_sr=16000, max_samples=64000)
    assert wav.shape == (64000,)


class _StubVoiceClassifier(VoiceClassifier):
    def _build_backbone(self):
        dim = self.cfg["embed_dim"]
        return lambda wav: torch.zeros(dim)


def test_classify_returns_valid_response(tmp_path):
    dim = 32
    d = tmp_path / "artifact_stub"
    d.mkdir()
    torch.save(EmotionHead(dim, len(EMOTIONS)).state_dict(), d / "emotion_head.pt")
    torch.save(SafetyHead(dim).state_dict(), d / "safety_head.pt")
    (d / "config.json").write_text(json.dumps({
        "backbone_hf_id": "stub", "backbone": "stub", "embed_dim": dim,
        "emotions": EMOTIONS, "distress_emotions": ["sad", "angry", "fearful", "disgust"],
        "safety_threshold": 0.4, "recall_floor": 0.9, "sample_rate": 16000,
        "max_samples": 64000, "pooling": "mean", "head_dim": 256, "safety_head_dim": 64,
    }))
    clf = _StubVoiceClassifier(d)
    resp = clf.classify(np.zeros(64000, dtype=np.float32))
    assert resp.detectedEmotion in EMOTIONS
    assert 0.0 <= resp.distressScore <= 1.0
    assert abs(sum(resp.emotionProbs.values()) - 1.0) < 1e-3
    assert isinstance(resp.safetyFlag, bool)
    assert resp.backbone == "stub"
