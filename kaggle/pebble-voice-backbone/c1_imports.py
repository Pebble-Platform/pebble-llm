# Cell 1 — imports & config.
# Experiment: FROZEN speech-encoder backbone selection for crisis-sensitive affect.
#   emotion2vec (primary) vs WavLM-Large (baseline), Pebble's heterogeneous heads
#   (emotion softmax + a high-distress recall head), RAVDESS, 3 seeds, paired delta.
# Mirrors the repo's pebble-mlm-3seed methodology: mean +/- std + per-seed delta.
import os, json, random, warnings, tempfile
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import f1_score, recall_score, precision_score

print("torch", torch.__version__, "| cuda", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ART = "/kaggle/working"
SR = 16000
MAX_SEC = 4.0
MAX_SAMPLES = int(SR * MAX_SEC)
SEEDS = [13, 42, 1337]                 # matches repo config.py
TRAIN_ACTORS = set(range(1, 21))       # speaker-independent split (actors 1-20 train)
VAL_ACTORS = set(range(21, 25))        # actors 21-24 val
PROBE_EPOCHS, PROBE_LR, HEAD_DIM = 60, 1e-3, 256
RECALL_FLOOR = 0.90                    # Pebble's safety-head recall-floor framing (voice proxy)
SAFETY_POS_WEIGHT = 3.0               # up-weight the distress positive class (high-recall)

EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
EMO2ID = {e: i for i, e in enumerate(EMOTIONS)}
N_EMO = len(EMOTIONS)
# Distress = the high-arousal / negative-valence emotions -> the safety-head analogue.
DISTRESS = {"sad", "angry", "fearful", "disgust"}

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

print(f"emotions={EMOTIONS}\ndistress(positive)={sorted(DISTRESS)} | seeds={SEEDS}")
