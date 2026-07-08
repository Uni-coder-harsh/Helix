# Getting Started

This guide covers setting up the Helix project for local development. It has been synchronized to match the exact stack and commands used in the active repository.

## Prerequisites

Ensure you have the following installed before beginning:

- **Node.js**: v20 or newer
- **Python**: v3.12 or newer
- **Package Managers**: `npm` (for Node) and `pip` or `uv` (for Python)
- **Database**: PostgreSQL (Local or Remote, e.g. Neon)
- **Docker**: (Optional) For running infrastructure services locally

## Repository Structure

```text
Helix/
├── backend/            # FastAPI Backend
├── frontend/           # Next.js App Router Frontend
├── docs/               # MkDocs Portal (You are here)
├── Makefile            # Automation commands
└── mkdocs.yml          # Docs config
```

## Backend Setup (FastAPI)

Helix uses a Python async backend powered by FastAPI.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in your PostgreSQL `DATABASE_URL` and `GEMINI_API_KEY`.
5. Run the server:
   ```bash
   uvicorn services.main:app --reload
   ```

## Frontend Setup (Next.js)

Helix uses a modern React frontend powered by Next.js 14 and TailwindCSS.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   Copy `.env.example` to `.env.local`. Set `NEXT_PUBLIC_API_URL` to point to your backend.
4. Run the development server:
   ```bash
   npm run dev
   ```

## Using the Makefile

For convenience, Helix includes a `Makefile` at the root of the repository to automate common tasks:

- `make dev`: Start both the backend and frontend development servers concurrently.
- `make lint`: Run code linters (`ruff` and `eslint`).
- `make format`: Auto-format Python code using `ruff` and `black`.
- `make docker-up`: Start local infrastructure via Docker.

## Running Tests

To execute tests for the backend (using Pytest) and build the frontend, you can use:

```bash
make test
```
