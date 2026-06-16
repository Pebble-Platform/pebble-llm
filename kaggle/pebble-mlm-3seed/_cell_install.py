# Cell 1 — pinned NeoBERT stack (Kaggle default torch 2.10 drops sm_60 -> P100 crash).
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
get_ipython().system('pip install -q torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 xformers==0.0.28.post3 --index-url https://download.pytorch.org/whl/cu121')
get_ipython().system('pip install -q transformers==4.48.2 sentencepiece')
print("install cell done")
