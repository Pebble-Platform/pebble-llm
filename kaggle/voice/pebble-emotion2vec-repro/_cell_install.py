# Cell 0 — pinned audio stack (P100 = sm_60; Kaggle default torch drops it -> crash).
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
# torchvision pinned to match torch 2.5.1 — else transformers' lazy torchvision import
# fails with "operator torchvision::nms does not exist" and WavLM won't load.
get_ipython().system('pip install -q torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121')
get_ipython().system('pip install -q transformers==4.48.2 datasets==3.2.0 librosa soundfile scikit-learn scipy')
# emotion2vec route (primary/repro backbone). Heavy dep tree; usage is guarded so a
# failed install/import only skips the emotion2vec arm — WavLM still produces a result.
get_ipython().system('pip install -q funasr modelscope || echo "funasr install failed -> emotion2vec arm will be skipped"')
print("install cell done")
