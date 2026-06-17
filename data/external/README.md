# External datasets — `pebble-mlm-ablation-3seed`

Downloaded from **original sources** (not the HF mirror) for manual review.
The **data files are gitignored** (`data/external/**` — PII / mental-health content);
only the viewer tooling (`index.html`, `README.md`, `download.sh`) is committed.
Maps 1:1 to the Kaggle notebook `kaggle/pebble-mlm-ablation-3seed/`.

## Quick start (for a fresh clone)

```bash
cd data/external
bash download.sh                 # fetch the public datasets (goemotions/eireg/tweeteval)
py -m http.server 8765           # serve (the viewer uses fetch → needs HTTP, not file://)
# open http://127.0.0.1:8765/index.html
```

`download.sh` does **not** fetch `esconv/` or `cssrs/` (mental-health content with access
terms) — obtain those separately from the team. The viewer still shows ESConv if present.

## What each is used for

| Folder | Source | Used in notebook | Role |
|---|---|---|---|
| `goemotions/simplified/` | google-research GitHub | `s2_data.py` (`go_emotions "simplified"`) | **emotion task** train/val (43,410 / 5,426), 28 classes |
| `goemotions/raw/` | gresearch GCS bucket | `s3_mlm_corpus.py` (`go_emotions "raw"`) | MLM corpus source (211k rows = 1 comment × N annotators → ~9k unique after dedup) |
| `semeval2018-eireg/` | ntua-slp-semeval2018 GitHub | `s2_data.py` (`eireg()`) | **severity task** train/dev (7,102 / 1,464) |
| `tweeteval/{emotion,sentiment,offensive,hate,irony}/` | cardiffnlp/tweeteval GitHub | `s3_mlm_corpus.py` (`tweet_eval`) | MLM corpus source (~71k of the 80k corpus) |

## File formats

**`goemotions/simplified/*.tsv`** — `text \t comma-separated label ids \t comment_id`
Label id → name in `emotions.txt` (index 0..27; `27 = neutral`). Multi-label possible
(the notebook takes the **first** label, neutral if empty).
```
My favourite food is anything I didn't have to cook myself.	27	eebbqej
WHY THE FUCK IS BAYLESS ISOING	2	eezlygj          # 2 = anger
```

**`goemotions/raw/goemotions_{1,2,3}.csv`** — full annotation table: `text,id,author,subreddit,...`
+ one 0/1 column per emotion + `example_very_unclear`. Same comment appears once per
annotator → why dedup collapses 211k → ~9k unique texts.

**`semeval2018-eireg/EI-reg-En-<emo>-<split>.txt`** — TSV: `ID \t Tweet \t Affect Dimension \t Intensity Score`
`Intensity Score ∈ [0,1]`. Notebook keeps the score for **anger/fear/sadness**, sets
**joy → 0.0** (joy is not distress). `severity` = intensity of negative affect.
```
2017-En-10264	@xandraaa5 ... #offended	anger	0.562
```

**`tweeteval/<subset>/{train,val,test}_{text,labels}.txt`** — parallel line files
(line *i* of `_text` ↔ line *i* of `_labels`); `mapping.txt` = label id → name.
Only the **text** is used for MLM (labels ignored). Subsets `offensive`/`hate` are
toxicity, not emotion — the suspected cause of the severity regression hit (see
`docs/improvement-plan-from-deep-read.md` §1.3).

## Row counts (verified against the run log)

```
goemotions simplified : train 43,410 | dev 5,426 | test 5,427
semeval EI-reg (En)    : train 7,102  | dev 1,464   (anger+fear+joy+sadness)
tweeteval train_text   : emotion 3,257 · sentiment 45,615 · offensive 11,916 · hate 9,000 · irony 2,862
```
