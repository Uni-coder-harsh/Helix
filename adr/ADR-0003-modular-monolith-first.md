# ADR-0003: Modular Monolith First

## Status
Accepted

## Date
2026-07-06

## Context
Designing a distributed microservice system on day one introduces immediate development friction (network failures, testing complexity, deployment overhead, event schema migrations). For a team starting a new product or a hackathon prototype:
* Speed of execution is critical.
* Refactoring boundaries inside a single codebase is significantly easier than changing network interfaces.
* Local development setup must be fast and reliable.

## Alternatives Considered

### Alternative 1: Microservices from Day One
* **Description:** Developing and running all 7 services as separate processes communicating over the network from the very beginning.
* **Pros:** Strict boundary enforcement from the start.
* **Cons:** Extremely slow development cycle; local setup requires running 7 services plus databases; high debugging friction.

### Alternative 2: Standard Monolith (Loose Structure)
* **Description:** A single application with no internal separation of modules.
* **Pros:** Fastest to build initially.
* **Cons:** High risk of spaghetti code; circular imports; database tables tightly coupled, making future separation impossible.

### Alternative 3: Modular Monolith First
* **Description:** Develop all 7 services as distinct, isolated packages inside a single monorepo. They communicate via local in-memory event buses and process boundaries. Database schemas are separated logically.
* **Pros:** Rapid local development; simple single-process deployment; clear boundaries that allow extraction into microservices (Phase 2/3) with minimal code refactoring.
* **Cons:** Requires strict discipline to prevent developers from bypassing module boundaries via direct imports.

## Decision
We chose **Alternative 3: Modular Monolith First** for Phase 1 of Helix.

We will develop Helix within a single repository using distinct package boundaries. Database tables are grouped into isolated schemas, and direct cross-module database queries or code imports are strictly forbidden (and checked via linter/compiler rules). Communication between modules is routed through an in-memory event bus or abstract service interfaces.

## Consequences
* **Positive:**
  * Hackathon-friendly setup: single database, single command to run the entire backend.
  * Simple debugging and local testing.
  * Refactoring boundaries is fast and painless.
* **Negative/Trade-offs:**
  * Requires strict automated boundary checks (linting, module import limits) to prevent boundary erosion.
