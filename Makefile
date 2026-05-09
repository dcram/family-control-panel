.PHONY: install-dev lint format test

install-dev:
	cd backend && uv sync --group dev
	cd frontend && pnpm install

lint:
	cd backend && uv run mypy app
	cd backend && uv run black --check app

format:
	cd backend && uv run black app

test:
	cd backend && uv run pytest
