#!/usr/bin/env bash
# Repopulate the PUBLIC datasets the pebble-mlm-ablation-3seed notebook uses, from
# their original sources, into this folder. Run from data/finetuning-message/external/:  bash download.sh
# NOTE: esconv/ and cssrs/ are NOT fetched here — they are obtained separately
# (mental-health content with access terms; ask the team for the provisioning steps).
set -e
cd "$(dirname "$0")"

# ---------- GoEmotions (emotion task = simplified; MLM corpus = raw) ----------
GO="https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data"
GCS="https://storage.googleapis.com/gresearch/goemotions/data/full_dataset"
mkdir -p goemotions/simplified goemotions/raw
for f in train.tsv dev.tsv test.tsv emotions.txt; do curl -fsSL -o "goemotions/simplified/$f" "$GO/$f"; done
for n in 1 2 3; do curl -fsSL -o "goemotions/raw/goemotions_$n.csv" "$GCS/goemotions_$n.csv"; done

# ---------- SemEval-2018 EI-reg (severity task) ----------
EI="https://raw.githubusercontent.com/cbaziotis/ntua-slp-semeval2018/master/datasets/task1/EI-reg"
mkdir -p semeval2018-eireg
for emo in anger fear joy sadness; do for split in train dev; do
  curl -fsSL -o "semeval2018-eireg/EI-reg-En-${emo}-${split}.txt" "$EI/EI-reg-En-${emo}-${split}.txt"
done; done

# ---------- tweet_eval (MLM corpus) ----------
TE="https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets"
for sub in emotion sentiment offensive hate irony; do
  mkdir -p "tweeteval/$sub"
  for part in train val test; do
    curl -fsSL -o "tweeteval/$sub/${part}_text.txt"   "$TE/$sub/${part}_text.txt"
    curl -fsSL -o "tweeteval/$sub/${part}_labels.txt" "$TE/$sub/${part}_labels.txt"
  done
  curl -fsSL -o "tweeteval/$sub/mapping.txt" "$TE/$sub/mapping.txt"
done

echo "done. Now serve the viewer:  py -m http.server 8765   then open http://127.0.0.1:8765/index.html"
