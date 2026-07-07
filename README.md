# Helix

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](pyproject.toml)
[![Pre-Commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](.pre-commit-config.yaml)

Helix is a highly disciplined, specifications-first engineering framework designed for building reliable, modular AI systems, datasets, and agents.

---

## 🛠️ The Helix Engineering Philosophy

> **"We are NOT going to vibe code Helix. We are going to engineer Helix."**

To prevent architectural drift and keep the project aligned with enterprise standards:
1. **Every commit has a reason.**
2. **Every document has an owner.**
3. **Every service has a contract.**
4. **Every API is designed before implementation.**

### Development Lifecycle

Helix is developed sequentially through 9 clear phases. Implementation (coding) only starts in Phase 6, after the prior designs have been frozen.

```
PHASE 0: Foundation (We are here)
   │
   ▼
PHASE 1: Product Engineering
   │
   ▼
PHASE 2: Architecture
   │
   ▼
PHASE 3: Data Engineering
   │
   ▼
PHASE 4: AI System Design
   │
   ▼
PHASE 5: Infrastructure
   │
   ▼
PHASE 6: Development (Coding starts here)
   │
   ▼
PHASE 7: Production Hardening
   │
   ▼
PHASE 8: Pilot Deployment
```

---

## 📂 Repository Directory Tour

- [docs/](file:///home/harsh/Desktop/CodeNova/Helix/docs/) — Documentation portal source (MkDocs Material)
- [architecture/](file:///home/harsh/Desktop/CodeNova/Helix/architecture/) — High-level system design & diagrams
- [adr/](file:///home/harsh/Desktop/CodeNova/Helix/adr/) — Architecture Decision Records (ADRs)
- [rfc/](file:///home/harsh/Desktop/CodeNova/Helix/rfc/) — Requests for Comments (RFCs)
- [backend/](file:///home/harsh/Desktop/CodeNova/Helix/backend/) — Backend FastAPI modular monolith service
- [frontend/](file:///home/harsh/Desktop/CodeNova/Helix/frontend/) — Next.js operational dashboards
- [deployments/](file:///home/harsh/Desktop/CodeNova/Helix/deployments/) — Kubernetes manifests and docker compose configurations
- [plugins/](file:///home/harsh/Desktop/CodeNova/Helix/plugins/) — Plugin configurations & definitions
- [demo-data/](file:///home/harsh/Desktop/CodeNova/Helix/demo-data/) — Synthesized realistic demo dataset & seed scripts
- [scripts/](file:///home/harsh/Desktop/CodeNova/Helix/scripts/) — Automation and CI tooling helper scripts
- [tools/](file:///home/harsh/Desktop/CodeNova/Helix/tools/) — Internal developer tooling
- [tests/](file:///home/harsh/Desktop/CodeNova/Helix/tests/) — Unit, integration, and security test suites

---

## 🚀 Getting Started

Check out [getting_started.md](file:///home/harsh/Desktop/CodeNova/Helix/docs/getting_started.md) for complete instructions.

### Quick Local Dev Environment Setup:

```bash
# 1. Setup virtual env
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Setup pre-commit hooks
pre-commit install
```

### Run the Engineering Portal Local Server:

```bash
mkdocs serve
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🤝 Contributing

Contributions must follow the strict review pipeline. Please review the [CONTRIBUTING.md](file:///home/harsh/Desktop/CodeNova/Helix/CONTRIBUTING.md) guide before opening a pull request.
