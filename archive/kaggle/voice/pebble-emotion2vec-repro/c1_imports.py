# Cell 1 — imports & config.
# REPRODUCTION of emotion2vec (Ma et al., ACL Findings 2024), Table 3 RAVDESS row.
#   Frozen encoder + SUPERB linear probe -> WA/UA/WF1, compared to the paper's
#   emotion2vec RAVDESS = WA 82.43 / UA 82.86 / WF1 82.39.
# Protocol (researched, see docs/tasks/emotion2vec-reproduction.md):
#   - all 1440 RAVDESS speech clips, all 8 classes
#   - random 10-fold CV, each fold a fresh stratified 80/10/10 train/val/test split
#   - SUPERB head: Linear(d,256) -> ReLU -> Linear(256,8), frozen single-layer feats, CE
#   - report mean +/- std of per-fold test WA/UA/WF1
import os, json, random, warnings, tempfile
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

print("torch", torch.__version__, "| cuda", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ART = "/kaggle/working"
SR = 16000
MAX_SEC = 5.0                          # RAVDESS clips ~3-5s; 5s covers virtually all
MAX_SAMPLES = int(SR * MAX_SEC)
FRAME_HOP = 320                        # both encoders downsample 16kHz->50Hz (320x)
T_MAX = MAX_SAMPLES // FRAME_HOP        # 250 frames; v2 keeps frame-level feats (T x d)

N_FOLDS = 10                           # paper: random 10-fold CV
SPLIT = (0.80, 0.10, 0.10)            # paper: 80/10/10 train/val/test per fold
BASE_SEED = 42                         # emotion2vec downstream config seed
PROBE_EPOCHS, PROBE_LR, HEAD_DIM, WD = 100, 1e-3, 256, 1e-4

# RAVDESS 8 emotions, canonical id order (filename code 01..08 -> 0..7).
EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
EMO2ID = {e: i for i, e in enumerate(EMOTIONS)}
N_EMO = len(EMOTIONS)

# Paper Table 3 reference (emotion2vec, RAVDESS, frozen linear probe).
PAPER = {"emotion2vec": {"WA": 82.43, "UA": 82.86, "WF1": 82.39},
         # paper Table 3 comparators (different WavLM variant: base, not large):
         "wavlm-base(paper)": {"WA": 37.01, "UA": None, "WF1": None},
         "data2vec2.0(paper)": {"WA": 81.04, "UA": None, "WF1": None}}

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

print(f"emotions={EMOTIONS}\nfolds={N_FOLDS} split={SPLIT} base_seed={BASE_SEED} "
      f"probe(ep={PROBE_EPOCHS},lr={PROBE_LR},hid={HEAD_DIM}) | v2 frame-level T_MAX={T_MAX}")
