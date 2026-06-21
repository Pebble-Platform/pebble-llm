# Cell 6 — demo inference on held-out fold-0 test clips, for EVERY backbone that ran
# (incl. emotion2vec, which can't run locally without funasr). Reuses the already-extracted
# frame features + the fold-0 trained head — no re-extraction. Prints a table and saves
# demo_predictions.json + demo.html so the result is viewable from the Kaggle output.
DEMO_PER_CLASS = 2
tr0, va0, te0 = split_80_10_10(y_all, BASE_SEED + 0)        # fold-0 test = unseen by the head
sel = []
for c in range(N_EMO):
    sel += [i for i in te0 if y_all[i] == c][:DEMO_PER_CLASS]
sel = sorted(sel)
print(f"=== Demo inference on {len(sel)} held-out fold-0 test clips ===")

rows = []
for name, head in artifacts.items():
    Xg = torch.tensor(BACKBONES[name]["X"][sel], dtype=torch.float, device=DEVICE)
    mg = mask_all[sel]
    head.eval()
    with torch.no_grad():
        probs = torch.softmax(head(Xg, mg), dim=-1).cpu().numpy()
    print(f"\n[{name}]")
    for k, idx in enumerate(sel):
        p = probs[k]; top = int(p.argmax()); ok = top == int(y_all[idx])
        rows.append({"backbone": name, "idx": int(idx), "truth": EMOTIONS[y_all[idx]],
                     "pred": EMOTIONS[top], "p": round(float(p[top]), 3), "correct": ok})
        print(f"  {'OK ' if ok else 'XX '} idx={idx:4d} truth={EMOTIONS[y_all[idx]]:9s} "
              f"pred={EMOTIONS[top]:9s} p={p[top]:.3f}")
    acc = np.mean([r["correct"] for r in rows if r["backbone"] == name])
    print(f"  demo acc ({len(sel)} clips) = {acc:.2f}")

with open(f"{ART}/demo_predictions.json", "w") as f:
    json.dump(rows, f, indent=2)

# minimal static HTML view (download from the kernel output and open locally).
def _html(rows):
    head = ("<style>body{font:14px system-ui;background:#0f1419;color:#e6edf3;padding:20px}"
            "table{border-collapse:collapse}td,th{border:1px solid #2a3340;padding:6px 10px}"
            ".ok{color:#3fb950}.xx{color:#d29922}</style>")
    body = "<h2>emotion2vec reproduction — demo predictions (Kaggle)</h2>"
    for name in sorted({r["backbone"] for r in rows}):
        rs = [r for r in rows if r["backbone"] == name]
        acc = np.mean([r["correct"] for r in rs])
        body += f"<h3>{name} — demo acc {acc:.2f}</h3><table><tr><th>idx</th><th>truth</th><th>pred</th><th>p</th></tr>"
        for r in rs:
            cls = "ok" if r["correct"] else "xx"
            body += (f"<tr><td>{r['idx']}</td><td>{r['truth']}</td>"
                     f"<td class={cls}>{r['pred']} {'✓' if r['correct'] else '✗'}</td><td>{r['p']:.3f}</td></tr>")
        body += "</table>"
    return f"<!doctype html><html><head><meta charset=utf-8>{head}</head><body>{body}</body></html>"

with open(f"{ART}/demo.html", "w") as f:
    f.write(_html(rows))
print("\nsaved: demo_predictions.json, demo.html")
