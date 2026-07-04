# Cell 1 — imports & config.
# VOICE MTL HEADS (thesis extension, NOT a paper reproduction).
#   Frozen encoder -> a SHARED SUPERB trunk -> THREE heads:
#     - emotion   : Linear(256, 8)  cross-entropy        (WA/UA/WF1)
#     - affect    : Linear(256, 2)  CCC on valence+arousal
#     - crisis    : Linear(256, 1)  BCE under a HARD recall floor
#   balanced by Kendall et al. (CVPR 2018) homoscedastic uncertainty weighting.
# RAVDESS has no continuous/crisis labels, so the two NEW heads learn PROXY targets:
#   valence/arousal from a fixed Russell (1980) circumplex map of the 8 emotions, and
#   crisis = the high-distress emotion set. This validates the multi-head + recall-floor
#   MECHANICS on the reproduction's frozen features; real CCC/crisis numbers need the
#   continuous/clinical sets (MSP-Podcast A/V/D, DAIC). See docs/tasks/voice-mtl-heads.md.
import os, json, random, warnings, tempfile
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
from sklearn.model_selection import train_test_split

print("torch", torch.__version__, "| cuda", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ART = "/kaggle/working"
SR = 16000
MAX_SEC = 5.0                          # RAVDESS clips ~3-5s; 5s covers virtually all
MAX_SAMPLES = int(SR * MAX_SEC)
FRAME_HOP = 320                        # both encoders downsample 16kHz->50Hz (320x)
T_MAX = MAX_SAMPLES // FRAME_HOP        # 250 frames; frame-level feats (T x d)

N_FOLDS = 10                           # random 10-fold CV (same protocol as the repro)
SPLIT = (0.80, 0.10, 0.10)            # 80/10/10 train/val/test per fold
BASE_SEED = 42
PROBE_EPOCHS, PROBE_LR, HEAD_DIM, WD = 100, 1e-3, 256, 1e-4
RECALL_FLOOR = 0.90                     # hard crisis-recall floor (thesis novelty mechanic)

# RAVDESS 8 emotions, canonical id order (filename code 01..08 -> 0..7).
EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
EMO2ID = {e: i for i, e in enumerate(EMOTIONS)}
N_EMO = len(EMOTIONS)

# PROXY targets for the two new heads (RAVDESS has no continuous/crisis labels):
#   Russell (1980) circumplex (valence, arousal) in [-1, 1] per emotion.
VALENCE_AROUSAL = {
    "neutral":  (0.0,  0.0), "calm":    (0.4, -0.6), "happy":   (0.8,  0.5),
    "sad":     (-0.6, -0.4), "angry":  (-0.6,  0.8), "fearful": (-0.6,  0.6),
    "disgust": (-0.7,  0.2), "surprised": (0.3,  0.7),
}
#   crisis / high-distress proxy -> safety head positive class.
CRISIS = {"angry", "fearful", "sad", "disgust"}
VA = np.array([VALENCE_AROUSAL[e] for e in EMOTIONS], dtype=np.float32)        # (8, 2)
SAFE = np.array([1.0 if e in CRISIS else 0.0 for e in EMOTIONS], dtype=np.float32)  # (8,)

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

print(f"emotions={EMOTIONS}\nfolds={N_FOLDS} split={SPLIT} base_seed={BASE_SEED} "
      f"probe(ep={PROBE_EPOCHS},lr={PROBE_LR},hid={HEAD_DIM}) | recall_floor={RECALL_FLOOR} "
      f"| crisis={sorted(CRISIS)}")
