.PHONY: install leaderboard flyer lint format typecheck

install:
	uv sync
	uv run playwright install chromium

flyer:
	uv run python flyer/export.py

leaderboard:
	uv run leaderboard

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

typecheck:
	uv run mypy src/
