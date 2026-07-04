# Block s1 — imports, seed, config
# Scaled MLM isolation ablation: adapt encoder ONCE on a BIG separate in-domain
# corpus, then fine-tune BOTH arms across 3 seeds -> mean +/- std + paired delta.
import os, random, warnings, urllib.request
warnings.filterwarnings("ignore")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset as TorchDataset
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import f1_score
from datasets import load_dataset
from transformers import AutoModel, AutoModelForMaskedLM, AutoTokenizer

print("torch", torch.__version__, "| cuda", torch.cuda.is_available(),
      "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu")

def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

DEVICE   = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL    = "chandar-lab/NeoBERT"
REVISION = "5424c8efeea6491b151d62dee55a752165407430"
MAX_LEN, BATCH = 64, 32
# --- MLM adaptation budget: BIG separate corpus, standard 15% masking ---
MLM_EPOCHS, MLM_MASK_PROB, MLM_CORPUS_CAP = 2, 0.15, 80000
FT_EPOCHS, FT_PER_POOL = 3, 2500
EMO_VAL_N, SEV_VAL_N = 1000, 600
SEEDS = [13, 42, 1337]
EIREG_NEG = {"anger", "fear", "sadness"}
EIREG_EMOS = ["anger", "fear", "joy", "sadness"]
ART = "/kaggle/working"
set_seed(SEEDS[0])
print(f"config ready | mask={MLM_MASK_PROB} corpus_cap={MLM_CORPUS_CAP} mlm_epochs={MLM_EPOCHS} | device {DEVICE}")
