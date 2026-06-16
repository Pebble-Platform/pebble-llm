# Block 1 — imports, seed, config
import os, re, math, random, copy, warnings, urllib.request
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

SEED = 42
def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)
set_seed(SEED)

DEVICE   = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL    = "chandar-lab/NeoBERT"
REVISION = "5424c8efeea6491b151d62dee55a752165407430"
MAX_LEN, BATCH = 64, 32
MLM_EPOCHS, MLM_MASK_PROB, MLM_CORPUS_CAP = 2, 0.30, 12000
FT_EPOCHS, FT_PER_POOL = 3, 2500
EMO_VAL_N, SEV_VAL_N = 1000, 600
EIREG_NEG = {"anger", "fear", "sadness"}
EIREG_EMOS = ["anger", "fear", "joy", "sadness"]
ART = "/kaggle/working"
print("config ready | device", DEVICE)
