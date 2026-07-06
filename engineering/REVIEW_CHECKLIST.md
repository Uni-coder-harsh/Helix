# Code Review & Validation Checklist

All changes must satisfy this checklist prior to being reviewed, merged, or frozen.

## 1. Architectural Guardrails
- [ ] **Boundary Check:** No direct cross-module database joins or imports between services.
- [ ] **Single Writer Rule:** A service must only write to its own owned tables. Other services read via replicas or events.
- [ ] **Advisory AI Invariant:** AI Orchestrator must not write state updates directly; it only yields suggestions. The Workflow Engine remains the sole state authority.
- [ ] **No Leakage:** Interfaces use abstract terms (*Query*, *Command*, *Request*, *Event*) rather than transport details.

## 2. Code Quality & Standards
- [ ] **Lint and Format:** Code runs and passes `ruff check .` and `black --check .`.
- [ ] **Type Safety:** Code passes `mypy` type validations without implicit `Any` overrides.
- [ ] **No Placeholders:** Code contains no open `TODO` statements or blank structures. Mocks must return deterministic outputs.

## 3. Definition of Done (DoD)
- [ ] Packages compile and build successfully.
- [ ] Test coverage checks pass for both domain models and APIs.
- [ ] Health status endpoints work correctly.
- [ ] Docker configuration compiles and builds locally.
- [ ] Progress logs (`progress.md`) and engineering memory files updated.
- [ ] Integration verified on target branch.
