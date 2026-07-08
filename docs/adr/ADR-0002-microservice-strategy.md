# ADR-0002: Microservice Strategy

## Status
Accepted

## Date
2026-07-06

## Context
In planning the production topology of Helix, we identified 14 logical component building blocks (API Gateway, Identity, Intake, Workflow Engine, AI Orchestrator, Knowledge Service, Search, Notifications, Plugin Runtime, Audit, Analytics, Administration, Configuration, Media).
If every single component is deployed as an independent microservice, it would create:
* Severe operational complexity (handling 14 separate repositories, pipelines, and deployments).
* Network latency overhead (multi-hop synchronous and asynchronous calls across 14 services).
* Hard-to-trace debugging cycles and distributed transactions.
* Premature optimization before scaling bottlenecks are identified.

## Alternatives Considered

### Alternative 1: 14 Microservices (One per Component)
* **Description:** Deploying each component as a standalone microservice with its own database.
* **Pros:** Complete isolation and maximum modular scaling.
* **Cons:** Over-engineered; high infrastructure cost; massive deployment complexity; excessive network overhead.

### Alternative 2: Monolithic Topology
* **Description:** Packing all 14 components into a single deployable service container.
* **Pros:** Easiest to develop and deploy; zero network latency.
* **Cons:** Hard to scale AI/Search components separately (which require high resource profiles) from low-resource CRUD features; poor isolation (untrusted plugins could crash the entire application).

### Alternative 3: 7 Consolidated Microservices
* **Description:** Grouping logically related components into 7 deployable services: API Gateway, Governance Service (Intake, Workflow Engine, Notification Orchestration, Admin), AI Platform Service (AI Orchestrator, Search, Knowledge), Identity Service, Plugin Runtime, Decision Intelligence Service, and Media Service.
* **Pros:** Highly balanced; keeps the operational footprints manageable; isolates unstable/untrusted runtimes (Plugin Runtime) and high-compute tasks (AI Platform) while keeping transactional state features together (Governance).
* **Cons:** Medium complexity; requires careful domain boundary design within consolidated services.

## Decision
We chose **Alternative 3: 7 Consolidated Microservices**.

We enforce the **Helix Service Creation Rule** (requiring a service to satisfy at least 4 of 6 capability, scaling, data lifecycle, deployment, and team ownership criteria) to justify each boundary. This provides the modularity we need without microservice bloat.

## Consequences
* **Positive:**
  * Clean team boundaries and code organization.
  * Accelerated processing resource isolation (AI Platform Service can run on dedicated nodes).
  * Sandboxing isolation (Plugin Runtime failure does not affect core workflows).
* **Negative/Trade-offs:**
  * Logical components inside the same service (like Workflow Engine and Administration in Governance Service) must maintain internal modular separation to allow future extraction if required.
