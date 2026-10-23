SHELL := /bin/bash
.DEFAULT_GOAL := dev
ROOT := $(CURDIR)
PORT ?= 8000
export UV_CACHE_DIR := $(ROOT)/.cache/uv
export UV_PYTHON_INSTALL_DIR := $(ROOT)/.cache/python
export COREPACK_HOME := $(ROOT)/.cache/corepack
export npm_config_cache := $(ROOT)/.cache/npm

.PHONY: install dev test build serve report
install:
	uv sync --frozen
	pnpm --dir web install --frozen-lockfile --store-dir "$(ROOT)/.cache/pnpm"

dev: install
	@trap 'kill $$api_pid 2>/dev/null || true' EXIT INT TERM; \
	uv run uvicorn outcome_ledger.api:app --host 127.0.0.1 --port $(PORT) --reload & api_pid=$$!; \
	API_PORT=$(PORT) pnpm --dir web dev

test:
	uv run pytest
	uv run ruff check
	pnpm --dir web test

build:
	pnpm --dir web build

serve:
	uv run uvicorn outcome_ledger.api:app --host 127.0.0.1 --port $(PORT)

report:
	uv run python -m outcome_ledger report --json
