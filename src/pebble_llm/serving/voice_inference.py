"""Inference wrapper for the voice affect model (voice extension).

Loads a Kaggle-trained artifact bundle (config.json + emotion_head.pt +
safety_head.pt) and a frozen speech encoder, then classifies a raw waveform.
Reuses the multi-task head architectures from models.heads so the serving
heads are bit-for-bit the ones trained in the notebook.

Artifact bundle layout (produced by kaggle/voice/pebble-voice-backbone, cell 5):
    artifact_<backbone>/
      config.json        backbone id, embed_dim, emotions, distress, threshold, ...
      emotion_head.pt     EmotionHead state_dict
      safety_head.pt      SafetyHead state_dict
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from pebble_llm.models.heads import EmotionHead, SafetyHead
from pebble_llm.serving.voice_schemas import VoiceClassifyResponse


def load_waveform(raw: bytes, target_sr: int, max_samples: int) -> np.ndarray:
    """Decode uploaded audio bytes -> mono float32 at target_sr, padded/truncated."""
    import soundfile as sf
    import torchaudio

    wav, sr = sf.read(io.BytesIO(raw), dtype="float32", always_2d=True)
    wav = wav.mean(axis=1)  # mono
    if sr != target_sr:
        wav = torchaudio.functional.resample(torch.from_numpy(wav), sr, target_sr).numpy()
    if len(wav) >= max_samples:
        wav = wav[:max_samples]
    else:
        wav = np.pad(wav, (0, max_samples - len(wav)))
    return wav.astype(np.float32)


class VoiceClassifier:
    def __init__(self, artifact_dir: str | Path, device: str = "cpu"):
        self.dir = Path(artifact_dir)
        self.device = torch.device(device)
        self.cfg = json.loads((self.dir / "config.json").read_text())
        self.emotions: list[str] = self.cfg["emotions"]
        self.threshold: float = self.cfg["safety_threshold"]
        self.sr: int = self.cfg["sample_rate"]
        self.max_samples: int = self.cfg["max_samples"]
        dim: int = self.cfg["embed_dim"]

        self._embed = self._build_backbone()

        self.emotion_head = EmotionHead(dim, len(self.emotions), head_dim=self.cfg["head_dim"])
        self.safety_head = SafetyHead(dim, head_dim=self.cfg["safety_head_dim"])
        self.emotion_head.load_state_dict(torch.load(self.dir / "emotion_head.pt", map_location="cpu"))
        self.safety_head.load_state_dict(torch.load(self.dir / "safety_head.pt", map_location="cpu"))
        self.emotion_head.to(self.device).eval()
        self.safety_head.to(self.device).eval()

    def _build_backbone(self):
        name = self.cfg["backbone"]
        if name == "emotion2vec":
            from funasr import AutoModel as FunASR  # heavy; only if this bundle needs it
            import soundfile as sf
            import tempfile, os

            # hub="hf" avoids the modelscope-CN "not registered" download failure.
            try:
                model = FunASR(model="iic/emotion2vec_base", hub="hf", disable_update=True)
            except Exception:
                from huggingface_hub import snapshot_download
                model = FunASR(model=snapshot_download("emotion2vec/emotion2vec_base"),
                               disable_update=True)

            def embed(wav: np.ndarray) -> torch.Tensor:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    sf.write(tf.name, wav, self.sr)
                    path = tf.name
                r = model.generate(path, granularity="utterance", extract_embedding=True,
                                   output_dir=None)
                os.remove(path)
                return torch.tensor(r[0]["feats"], dtype=torch.float, device=self.device)

            return embed

        # default: WavLM-family via transformers (mean-pool last_hidden_state)
        from transformers import AutoFeatureExtractor, WavLMModel

        fe = AutoFeatureExtractor.from_pretrained(self.cfg["backbone_hf_id"])
        enc = WavLMModel.from_pretrained(self.cfg["backbone_hf_id"]).to(self.device).eval()

        @torch.no_grad()
        def embed(wav: np.ndarray) -> torch.Tensor:
            inp = fe(wav, sampling_rate=self.sr, return_tensors="pt")
            inp = {k: v.to(self.device) for k, v in inp.items()}
            h = enc(**inp).last_hidden_state  # (1, T, dim)
            return h.mean(dim=1).squeeze(0)

        return embed

    @torch.no_grad()
    def classify(self, waveform: np.ndarray) -> VoiceClassifyResponse:
        emb = self._embed(waveform).unsqueeze(0)  # (1, dim)
        probs = F.softmax(self.emotion_head(emb), dim=-1).squeeze(0).cpu().numpy()
        distress = float(torch.sigmoid(self.safety_head(emb)).item())
        top = int(probs.argmax())
        return VoiceClassifyResponse(
            detectedEmotion=self.emotions[top],
            emotionProbs={e: round(float(p), 4) for e, p in zip(self.emotions, probs)},
            distressScore=round(distress, 4),
            safetyFlag=distress >= self.threshold,
            backbone=self.cfg["backbone"],
        )
