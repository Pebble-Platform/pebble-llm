"""Kaggle GPU smoke test for NeoBERT — Phase 5, Task 0.

Run this on a Kaggle notebook with a GPU accelerator (T4 x2 or P100) BEFORE
investing in any training code. It retires the environment risk: can NeoBERT load
and run a forward pass on Kaggle's free GPU?

What the vendored modeling code actually needs (src/pebble_llm/models/_neobert_vendor/model.py):
  - xformers      REQUIRED — unguarded top-level `from xformers.ops import SwiGLU`.
  - torch >= 2.4  REQUIRED — the model uses `nn.RMSNorm` (added in torch 2.4).
  - flash_attn    OPTIONAL — only used for PACKED sequences (the cu_seqlens path).
                  Standard padded batches fall back to torch SDPA, so a missing /
                  unbuildable flash_attn is NOT a blocker for v1 training.

Usage on Kaggle (turn the accelerator ON first):
    # VALIDATED matched stack (2026-06-05). Kaggle's default torch 2.10 stack does NOT
    # work: it dropped sm_60 (P100) kernels AND is too new for NeoBERT (NaN/load errors).
    # NeoBERT's config records transformers_version 4.48.2; the torch family must share
    # one build so the C++ ops register. This combo gives RESULT: GO on a P100.
    !pip install -q torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 xformers==0.0.28.post3 \
        --index-url https://download.pytorch.org/whl/cu121
    !pip install -q transformers==4.48.2
    !python kaggle_smoke_test.py          # if uploaded as a utility script
  -- or paste this file's body into a single cell and run it.

Exit code 0 = GO (training path is viable). Non-zero = NO-GO (see failed stage).
"""

from __future__ import annotations

import sys
import traceback

# Pinned NeoBERT revision — MUST match config.py (ModelConfig.revision) and
# scripts/vendor_neobert.py (PINNED_REVISION).
MODEL_NAME = "chandar-lab/NeoBERT"
PINNED_REVISION = "5424c8efeea6491b151d62dee55a752165407430"
HIDDEN_SIZE = 768  # expected last_hidden_state width

results: list[tuple[str, str, str]] = []  # (stage, status, detail)


def record(stage: str, status: str, detail: str = "") -> None:
    results.append((stage, status, detail))
    print(f"[{status:4}] {stage}" + (f" — {detail}" if detail else ""))


def main() -> int:
    # --- Stage 1: torch + CUDA + GPU info -----------------------------------
    try:
        import torch

        major, minor = (int(x) for x in torch.__version__.split(".")[:2])
        torch_ok = (major, minor) >= (2, 4)
        record(
            "torch >= 2.4 (RMSNorm)",
            "PASS" if torch_ok else "FAIL",
            f"torch {torch.__version__}" + ("" if torch_ok else " — RMSNorm needs >= 2.4"),
        )
        if not torch.cuda.is_available():
            record("CUDA available", "FAIL", "no GPU — enable the Kaggle accelerator")
            return _summary(blocker=True)
        cap = torch.cuda.get_device_capability(0)
        name = torch.cuda.get_device_name(0)
        record("CUDA available", "PASS", f"{name} (sm_{cap[0]}{cap[1]})")
        # FlashAttention-2 needs sm_80+; T4=sm_75, P100=sm_60 → FA2 unsupported, but optional.
        if cap[0] < 8:
            record("FlashAttention-2 support", "INFO", f"sm_{cap[0]}{cap[1]} < sm_80 — FA2 N/A, SDPA used (fine)")
    except Exception:
        record("torch import", "FAIL", traceback.format_exc().splitlines()[-1])
        return _summary(blocker=True)

    # --- Stage 2: xformers SwiGLU (REQUIRED hard dep) -----------------------
    try:
        from xformers.ops import SwiGLU  # noqa: F401

        record("xformers SwiGLU import", "PASS", "")
    except Exception:
        record(
            "xformers SwiGLU import",
            "FAIL",
            "REQUIRED — `pip install xformers` matching this torch/CUDA. " + traceback.format_exc().splitlines()[-1],
        )
        return _summary(blocker=True)

    # --- Stage 3: flash_attn (OPTIONAL — informational only) ----------------
    try:
        from flash_attn.flash_attn_interface import flash_attn_varlen_func  # noqa: F401

        record("flash_attn import", "INFO", "available — packed-sequence training possible")
    except Exception:
        record("flash_attn import", "INFO", "absent — OK, padded batches use SDPA (not a blocker)")

    # --- Stage 4: load NeoBERT at the pinned revision -----------------------
    try:
        from transformers import AutoModel, AutoTokenizer

        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, revision=PINNED_REVISION)
        except Exception:
            # NeoBERT uses the bert-base-uncased tokenizer per its config.
            tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
            record("tokenizer", "INFO", "fell back to google-bert/bert-base-uncased")

        model = AutoModel.from_pretrained(
            MODEL_NAME, revision=PINNED_REVISION, trust_remote_code=True
        )
        model = model.to("cuda").eval()
        n_params = sum(p.numel() for p in model.parameters())
        record("load NeoBERT @ pinned rev", "PASS", f"{n_params / 1e6:.0f}M params, trust_remote_code=True")
    except Exception:
        record("load NeoBERT @ pinned rev", "FAIL", traceback.format_exc().splitlines()[-1])
        return _summary(blocker=True)

    # --- Stage 5: forward pass on a padded batch (SDPA path) ----------------
    texts = [
        "i feel completely overwhelmed and i can't sleep at night",
        "thanks so much, today was actually a really good day",
    ]
    enc = tokenizer(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
    input_ids = enc["input_ids"].to("cuda")
    attention_mask = enc["attention_mask"].to("cuda")
    expected_shape = (len(texts), input_ids.shape[1], HIDDEN_SIZE)

    # fp32 forward. On failure we print the FULL traceback and re-run the SAME
    # forward on CPU to isolate a GPU-kernel/compat problem from a model-code bug.
    def _forward_report(device: str) -> bool:
        m = model.to(device).eval()
        ii, am = input_ids.to(device), attention_mask.to(device)
        with torch.no_grad():
            out = m(input_ids=ii, attention_mask=am)
        h = out.last_hidden_state
        shape = tuple(h.shape)
        has_nan = bool(torch.isnan(h).any())
        ok = shape == expected_shape and not has_nan
        record(
            f"forward fp32 [{device}]",
            "PASS" if ok else "FAIL",
            f"out={shape} expected={expected_shape} hidden_size={model.config.hidden_size}"
            + (" — contains NaN" if has_nan else ""),
        )
        return ok

    try:
        gpu_ok = _forward_report("cuda")
    except Exception:
        record("forward fp32 [cuda]", "FAIL", "raised — full traceback below")
        traceback.print_exc()
        gpu_ok = False

    if not gpu_ok:
        # Same forward on CPU: PASS here ⇒ GPU-specific; FAIL here ⇒ model-code issue.
        try:
            cpu_ok = _forward_report("cpu")
            record(
                "forward fp32 [cpu] isolation",
                "INFO",
                "CPU OK → GPU-specific issue" if cpu_ok else "CPU also failed → model-code issue",
            )
        except Exception:
            record("forward fp32 [cpu] isolation", "INFO", "CPU raised — full traceback below")
            traceback.print_exc()
        return _summary(blocker=True)
    model.to("cuda")

    # fp16 autocast forward (training uses fp16=True per TrainingConfig)
    try:
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
            out16 = model(input_ids=input_ids, attention_mask=attention_mask)
        h16 = out16.last_hidden_state
        ok16 = tuple(h16.shape) == expected_shape and not torch.isnan(h16.float()).any()
        record("forward fp16 (autocast)", "PASS" if ok16 else "WARN",
               "ok" if ok16 else "fp16 produced NaN/bad shape — train in fp32 if this persists")
    except Exception:
        record("forward fp16 (autocast)", "WARN", "fp16 failed — fall back to fp32: "
               + traceback.format_exc().splitlines()[-1])

    # --- Stage 6: tiny backward pass (confirms autograd + SwiGLU grads) -----
    try:
        model.train()
        out = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = out.last_hidden_state[:, 0, :].pow(2).mean()  # dummy loss on [CLS]
        loss.backward()
        has_grad = any(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
        record("backward pass", "PASS" if has_grad else "FAIL",
               "gradients finite" if has_grad else "no finite gradients")
    except Exception:
        record("backward pass", "FAIL", "raised — full traceback below")
        traceback.print_exc()
        return _summary(blocker=True)

    return _summary(blocker=False)


def _summary(blocker: bool) -> int:
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY")
    print("=" * 60)
    for stage, status, detail in results:
        print(f"  {status:4}  {stage}" + (f"  ({detail})" if detail else ""))
    failed = [s for s, st, _ in results if st == "FAIL"]
    if blocker or failed:
        print(f"\n  RESULT: NO-GO — failed: {', '.join(failed) or 'see above'}")
        return 1
    print("\n  RESULT: GO — NeoBERT loads, forward + backward run on this GPU.")
    print("  Next: Phase 5 Task 1 (dataset prep) / Task 3 (emotion-head pretrain).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
