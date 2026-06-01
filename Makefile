.PHONY: help install lint format type test check data pretrain train eval serve docker-build

help:
	@echo "Targets:"
	@echo "  install      uv sync (incl. dev group)"
	@echo "  lint         ruff check"
	@echo "  format       ruff format"
	@echo "  type         mypy src"
	@echo "  test         pytest"
	@echo "  check        lint + type + test"
	@echo "  data         prepare_dataset.py (download external + build splits)"
	@echo "  pretrain     emotion-head pre-training on GoEmotions"
	@echo "  train        multi-task fine-tune on Pebble data"
	@echo "  eval         evaluate on Protocol B test set"
	@echo "  serve        run FastAPI /classify locally"
	@echo "  docker-build build the serving image"

install:
	uv sync --all-extras --dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

type:
	uv run mypy src

test:
	uv run pytest

check: lint type test

data:
	uv run python scripts/prepare_dataset.py

pretrain:
	uv run python scripts/run_pretrain.py --config configs/training/pretrain_emotion.yaml

train:
	uv run python scripts/run_train.py --config configs/training/multitask.yaml

eval:
	uv run python scripts/run_eval.py --config configs/training/multitask.yaml

serve:
	uv run uvicorn pebble_llm.serving.app:app --reload --host 0.0.0.0 --port 8080

docker-build:
	docker build -f serving/Dockerfile -t pebble-classifier:local .
