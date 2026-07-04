"""Track B feasibility spike: export NeoBERT to INT8 ONNX for CPU serving (§4, OQ6).

UNPROVEN for NeoBERT — RoPE, SwiGLU, RMSNorm and the custom `trust_remote_code`
attention must all trace and quantize cleanly. TIMEBOX this. If it fails, stay on
Track A (GPU FP16) or fall back to ModernBERT (proven CPU/ONNX path) before Gemini.
"""

from __future__ import annotations

from pebble_llm.utils.logging import get_logger

logger = get_logger("export_onnx")


def main() -> None:
    logger.info("ONNX export is a timeboxed feasibility spike — see §4 Track B / OQ6.")
    raise SystemExit("Not implemented — feasibility spike, not a plan.")


if __name__ == "__main__":
    main()
