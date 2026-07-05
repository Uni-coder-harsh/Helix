# Contributing to Helix

Welcome! We are excited that you want to contribute to Helix.

As a disciplined engineering project, we follow a rigorous development process to maintain consistency, prevent architectural drift, and ensure high-quality software. Please read these guidelines before making any contributions.

## Core Engineering Philosophy

* **No Vibe Coding:** Every commit has a reason. Every document has an owner. Every service has a contract. Every API is designed before implementation.
* **Specification First:** Implementation only begins after a specification or document (e.g., PRD, ADR, RFC) has been reviewed, approved, and frozen.
* **Review Pipeline:** No AI-generated code or document is committed directly. Everything follows:
  $$\text{Generate} \rightarrow \text{Review} \rightarrow \text{Refine} \rightarrow \text{Approve} \rightarrow \text{Commit}$$

---

## Helix Development Lifecycle

When working on a feature or component, align your tasks with the roadmap phases:
1. **Phase 0:** Foundation (Infrastructure setup & templates)
2. **Phase 1:** Product Engineering (Vision, PRD, User journeys)
3. **Phase 2:** Architecture (C4 model, ADRs, RFCs)
4. **Phase 3:** Data Engineering (Schemas, storage, indexes)
5. **Phase 4:** AI Engineering (Agents, prompts, evaluations)
6. **Phase 5:** Infrastructure (DevOps, Docker, CI/CD)
7. **Phase 6:** Development (Implementation & Unit tests)
8. **Phase 7:** Production Hardening (Security, Scalability, Observability)
9. **Phase 8:** Pilot & Deployment (Release, Demos, Presentation)

---

## Development Workflow

### 1. Issue & Branch Strategy
- Find an existing issue or open a new one.
- Use issue-specific branch naming conventions:
  - `feature/issue-<number>-<short-description>`
  - `bugfix/issue-<number>-<short-description>`
  - `docs/issue-<number>-<short-description>`
  - `infra/issue-<number>-<short-description>`

### 2. Local Environment Setup
Ensure you have the pre-requisite developer tools configured:
1. Initialize a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### 3. Coding & Documentation Standards
- Write clean, self-documenting code with type annotations (`mypy` compliant).
- Use `ruff` and `black` for formatting and linting.
- Add/update tests under `tests/`.
- Document key design decisions via Architecture Decision Records (ADRs) under `adr/` or Requests for Comments (RFCs) under `rfc/`.
- Update the Helix Engineering Portal documentation in the `docs/` folder.

### 4. Progress Logging
- Every developer must log their progress inside `progress.md` with a unique log ID, timestamp, phase, action description, and status.

### 5. Submitting a Pull Request (PR)
- Ensure all CI/CD checks (formatting, tests, type checking) pass locally.
- Write a clear, descriptive PR title and fill out the pull request template.
- Link the pull request to the relevant issue.
- Request review from codeowners.
