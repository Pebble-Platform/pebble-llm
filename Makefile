.PHONY: help install lint format check pilot-extract pilot-label

help:
	@echo "Targets:"
	@echo "  install        uv sync (tooling env only; pipeline env = .venv-vnser, see scripts/vietnamese-ser/README.md)"
	@echo "  lint           ruff check (archive/ excluded)"
	@echo "  format         ruff format"
	@echo "  check          lint + format-check"
	@echo "  pilot-extract  run the extraction pipeline on one episode (needs .venv-vnser)"
	@echo "  pilot-label    dual-teacher weak-label via API (needs ANTHROPIC_API_KEY)"

install:
	uv sync --dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

check: lint
	uv run ruff format --check .

# EP=data/vietnamese-ser/raw/ep01.mp3  HF_TOKEN=hf_xxx
pilot-extract:
	PYTHONPATH=scripts/vietnamese-ser PYTHONIOENCODING=utf-8 .venv-vnser/Scripts/python.exe \
		scripts/vietnamese-ser/pilot_extract.py --input $(EP) --turn-split --hf-token $(HF_TOKEN)

# TRANSCRIPTS=data/vietnamese-ser/pilot/<ep>/transcripts_yt.csv
pilot-label:
	PYTHONIOENCODING=utf-8 uv run --with anthropic --with pydantic python \
		scripts/vietnamese-ser/m4_weak_label.py --transcripts $(TRANSCRIPTS)
