---
owner: "@harsh"
version: "0.1.0"
status: "Draft"
last_updated: "2026-07-05"
reviewer: "@harsh"
dependencies: []
---

# Getting Started

Welcome to Project Helix! Follow these instructions to set up your environment and run the Helix Engineering Portal locally.

## Development Environment Setup

### 1. Prerequisites
- **Python:** Version 3.13 or newer
- **Git:** Version 2.40 or newer

### 2. Standard Installation
Initialize the virtual environment and install standard development and documentation dependencies:

```bash
# Clone the repository (if not already done)
# git clone <repo_url> Helix && cd Helix

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Running the Helix Engineering Portal Locally

The engineering portal is compiled using MkDocs Material. To serve it locally for interactive editing:

```bash
mkdocs serve
```

Once the server is running, open your browser and navigate to:
[http://localhost:8000](http://localhost:8000)

## Repository Structure

```text
helix/
├── docs/             # Documentation portal source
├── architecture/     # Architecture specification & C4 models
├── adr/              # Architecture Decision Records (ADRs)
├── rfc/              # Requests for Comments (RFCs)
├── research/         # Research notes and whitepapers
├── services/         # Microservices source code
├── agents/           # AI Agent definitions & logic
├── plugins/          # Plugin definitions & extensions
├── sdk/              # Client SDK code
├── infra/            # Terraform, Docker, and Kubernetes configuration
├── deployments/      # Production deployment manifests
├── frontend/         # Web dashboard frontend
├── mobile/           # Mobile app client
├── datasets/         # Knowledge graphs and schemas
├── ml/               # Machine Learning model training scripts
├── shared/           # Common utilities and libraries
├── scripts/          # Developer tooling scripts
├── tools/            # Local developer utilities
├── tests/            # Test suites
└── .github/          # CI/CD workflows and issue templates
```
