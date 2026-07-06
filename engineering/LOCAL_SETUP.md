# Local Development Setup Guide

Follow these steps to configure your local development environment for the Helix platform.

## Prerequisites
* **Python:** 3.12 or 3.13 (Python 3.13 recommended)
* **Node.js:** 18 or 20 (Node 20 LTS recommended)
* **Docker & Docker Compose**
* **uv:** Fast Python package installer and resolver (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

---

## 1. Initial Setup

Clone the repository and copy the environment variables template:

```bash
# Copy local env template
cp .env.example .env
```

Open `.env` and fill in necessary API keys (like `GEMINI_API_KEY`) if integrating real providers. The default sqlite configuration will run all mock engines automatically.

---

## 2. Syncing Package Dependencies

Helix uses `uv` workspaces for fast, isolated backend packages, and `npm` for frontend code:

```bash
# Sync Python virtual environment and backend workspace members
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## 3. Running Code Verification (Lint & Test)

All code checks and test runs are fully automated via the root `Makefile`:

```bash
# Run backend and frontend lint checks
make lint

# Auto-format and clean python codebase
make format

# Run complete pytest and frontend build verification suites
make test
```

---

## 4. Launching Local Services

To start the entire local stack (FastAPI reload dev server and Next.js frontend console):

```bash
make dev
```

* **FastAPI Backend Swagger Console:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **FastAPI Backend Health Status:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)
* **Next.js Frontend Console:** [http://localhost:3000](http://localhost:3000)

Alternatively, launch the local service infrastructure using Docker:

```bash
# Start Docker backend environment
make docker-up
```
