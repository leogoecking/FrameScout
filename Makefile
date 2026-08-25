.PHONY: help up down restart logs ps test test-api test-web lint format typecheck health clean

help:
	@echo "FrameScout Makefile Commands:"
	@echo "  make up          - Inicia todos os serviços via Docker Compose"
	@echo "  make down        - Para todos os serviços"
	@echo "  make restart     - Reinicia os containers"
	@echo "  make logs        - Exibe os logs dos containers"
	@echo "  make ps          - Lista os containers e status de saúde"
	@echo "  make test        - Executa todos os testes (pytest + vitest)"
	@echo "  make test-api    - Executa testes do backend (pytest)"
	@echo "  make test-web    - Executa testes do frontend (vitest)"
	@echo "  make lint        - Roda linters (ruff + eslint)"
	@echo "  make format      - Formata código (ruff format)"
	@echo "  make typecheck   - Checagem estática de tipos (mypy + tsc)"
	@echo "  make health      - Testa os endpoints de healthcheck da API"
	@echo "  make clean       - Remove caches e volumes"

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

test: test-api test-web

test-api:
	.venv/bin/pytest -v

test-web:
	cd apps/web && npm run test

lint:
	.venv/bin/ruff check services/api
	cd apps/web && npm run lint

format:
	.venv/bin/ruff format services/api
	.venv/bin/ruff check --fix services/api

typecheck:
	.venv/bin/mypy --config-file mypy.ini services/api/app
	cd apps/web && npm run typecheck

health:
	@echo "--- Liveness Probe ---"
	@curl -s http://localhost:8000/health/live || echo "API offline"
	@echo ""
	@echo "--- Detailed Health ---"
	@curl -s http://localhost:8000/health || echo "API offline"
	@echo ""

clean:
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
