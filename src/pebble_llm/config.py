"""Typed config loading.

Configs live as YAML under ``configs/`` (Hydra-style groups). We load them with
OmegaConf and validate into pydantic models so the rest of the code gets typed,
autocompleted access instead of dict lookups.
"""

from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf
from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    raw_dir: Path = Path("data/finetuning-message/raw")
    processed_dir: Path = Path("data/finetuning-message/processed")
    external_dir: Path = Path("data/finetuning-message/external")
    max_seq_length: int = 256  # current msg + last 3 messages; NeoBERT supports 4096
    context_window: int = 3  # number of prior messages to interleave
    val_size: int = 500
    test_size: int = 500
    seed: int = 42


class ModelConfig(BaseModel):
    name: str = "chandar-lab/NeoBERT"
    revision: str = "5424c8efeea6491b151d62dee55a752165407430"  # pinned 2026-05-29 (§6.1 Step 0)
    trust_remote_code: bool = True
    hidden_size: int = 768
    head_hidden_dim: int = 256
    dropout: float = 0.1
    # v1 reuse-labels scope: only severity is learned (SemEval/WASSA intensity transfer).
    # energy/socialIsolation/receptivity have no public labels → Decision-Engine heuristics.
    score_dims: list[str] = Field(default_factory=lambda: ["severity"])
    num_emotion_labels: int = 12


class TrainingConfig(BaseModel):
    output_dir: Path = Path("checkpoints/neobert-multitask")
    batch_size: int = 16
    epochs: int = 5
    freeze_encoder_epochs: int = 2  # heads-only warmup (§5.3 mitigation)
    lr_encoder: float = 5e-6
    lr_heads: float = 2e-5
    weight_decay: float = 0.01
    # multi-task loss weights (§6.1 Step 2)
    loss_weight_score: float = 1.0
    loss_weight_emotion: float = 1.0
    loss_weight_safety: float = 2.0
    safety_pos_weight: float = 10.0
    early_stopping_patience: int = 3
    eval_every_steps: int = 100
    seeds: list[int] = Field(default_factory=lambda: [13, 42, 1337])  # report mean ± std
    fp16: bool = True


class ServingConfig(BaseModel):
    checkpoint_path: Path = Path("checkpoints/neobert-multitask/best")
    device: str = "cuda"  # "cpu" only valid with a successful ONNX export (Track B spike)
    onnx: bool = False
    max_batch_size: int = 8


class Config(BaseModel):
    data: DataConfig = Field(default_factory=DataConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    serving: ServingConfig = Field(default_factory=ServingConfig)


def load_config(path: str | Path) -> Config:
    """Load a YAML config file (with OmegaConf interpolation) into a typed ``Config``."""
    raw = OmegaConf.load(path)
    resolved = OmegaConf.to_container(raw, resolve=True)
    return Config.model_validate(resolved)
