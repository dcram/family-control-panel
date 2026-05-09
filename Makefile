.PHONY: install-dev lint format test

install-dev:
	cd backend && uv sync --group dev
	@[ -d frontend ] && (cd frontend && pnpm install) || echo "frontend/ pas encore créé, ignoré"

lint:
	cd backend && uv run mypy app
	cd backend && uv run black --check app

format:
	cd backend && uv run black app

test:
	cd backend && uv run pytest
