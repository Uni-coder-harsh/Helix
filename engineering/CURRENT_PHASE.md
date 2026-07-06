# Current Phase: Phase 2 — Engineering Foundation

We are establishing the core codebase scaffolding, directory layout, workspace package settings, common models, abstractions, and developer environments.

## Milestones & Status
- [x] **Milestone 1:** Repository Skeleton & Workspace Setup (`helix-backend` with `uv` configuration, Pydantic loading, structlog logging, telemetry setup, and database outbox persistence).
- [x] **Milestone 2:** Shared Domain (`backend/shared/domain` and `backend/shared/contracts` containing DDD Aggregate Roots, Value Objects, Commands, Queries, and 21 state machine events).
- [x] **Milestone 3:** Frontend Dashboard Shells (Next.js 14, Tailwind, and shadcn/ui dashboard shells for Citizen and Officer roles, live map preview, and analytics layout).
- [x] **Milestone 4:** AI Platform Foundation (`ai_platform` package with LLM and provider abstractions, prompt registry, cosine-similarity RAG search, safety guards, confidence scorer, and test evaluation suite).
- [ ] **Milestone 5:** First End-to-End Vertical Slice (Submitting, triaging, recommendation, and Officer dashboard updates).

## Development Cadence
Work is parallelized into branches and consolidated via integration PRs before being tested and frozen.
