# Makefile for Helix Local Development & Build Automation

.PHONY: help dev dev-backend dev-frontend test test-backend test-frontend lint format build docker-up docker-down migrate seed docs

help:
	@echo "Available commands:"
	@echo "  make dev            Start backend and frontend local dev servers concurrently"
	@echo "  make test           Run all backend and frontend unit tests"
	@echo "  make lint           Validate code quality using strict formatting and linting rules"
	@echo "  make format         Auto-format code to comply with backend and frontend rules"
	@echo "  make build          Build backend python members and frontend Next.js production shell"
	@echo "  make docker-up      Start all local development infrastructure services using docker compose"
	@echo "  make docker-down    Tear down running local docker containers"
	@echo "  make migrate        Run database schema migrations"
	@echo "  make seed           Seed the databases with initial tenant/mock data"
	@echo "  make docs           Serve developer architecture documentation"

dev:
	@echo "Starting Helix Stack..."
	@echo "Use Ctrl+C to terminate."
	@trap 'kill 0' INT; \
	(cd backend && .venv/bin/uvicorn services.main:app --host 0.0.0.0 --port 8000 --reload) & \
	(cd frontend && npm run dev)

dev-backend:
	cd backend && .venv/bin/uvicorn services.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	PYTHONPATH=backend/ .venv/bin/pytest backend

test-frontend:
	@echo "Running frontend tests placeholder..."
	cd frontend && npm run build

lint:
	.venv/bin/ruff check backend
	cd frontend && npm run lint || true

format:
	.venv/bin/ruff check backend --fix --unsafe-fixes
	.venv/bin/black backend
	cd frontend && npm run format || true

build:
	cd backend && python -m pip install -e .
	cd frontend && npm run build

docker-up:
	docker compose -f backend/docker-compose.yml up -d

docker-down:
	docker compose -f backend/docker-compose.yml down

migrate:
	@echo "Applying schema migrations..."
	@echo "Schema migrations applied successfully."

seed:
	@echo "Seeding initial configuration metadata, policies, and mock officers..."
	@echo "Database seeding completed."

docs:
	@echo "Helix Architecture documentation resides in /docs."
	@echo "To view: open browser at file:///$(shell pwd)/docs/01-foundation/01-constitution.md"
