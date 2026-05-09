.PHONY: install-dev lint format test lint-front build-front

install-dev:
	cd backend && uv sync --group dev
	cd frontend && pnpm install

lint:
	cd backend && uv run mypy app
	cd backend && uv run black --check app

lint-front:
	cd frontend && pnpm lint

build-front:
	cd frontend && pnpm build

format:
	cd backend && uv run black app

test:
	cd backend && uv run pytest
