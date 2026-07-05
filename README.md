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
- [research/](file:///home/harsh/Desktop/CodeNova/Helix/research/) — Research papers, benchmarks, and notes
- [services/](file:///home/harsh/Desktop/CodeNova/Helix/services/) — Backend microservices
- [agents/](file:///home/harsh/Desktop/CodeNova/Helix/agents/) — AI Agents, prompt templates, evaluation configs
- [plugins/](file:///home/harsh/Desktop/CodeNova/Helix/plugins/) — Plugin configurations & definitions
- [sdk/](file:///home/harsh/Desktop/CodeNova/Helix/sdk/) — Developer Client SDKs
- [infra/](file:///home/harsh/Desktop/CodeNova/Helix/infra/) — Terraform, cloud run, IAM configurations
- [deployments/](file:///home/harsh/Desktop/CodeNova/Helix/deployments/) — Kubernetes manifests and docker compose files
- [frontend/](file:///home/harsh/Desktop/CodeNova/Helix/frontend/) — Dashboards and web portals
- [mobile/](file:///home/harsh/Desktop/CodeNova/Helix/mobile/) — Mobile applications
- [datasets/](file:///home/harsh/Desktop/CodeNova/Helix/datasets/) — DB schemas, Graph database configurations
- [ml/](file:///home/harsh/Desktop/CodeNova/Helix/ml/) — Model training notebooks and weights tracking
- [shared/](file:///home/harsh/Desktop/CodeNova/Helix/shared/) — Shared helper functions and base structures
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
