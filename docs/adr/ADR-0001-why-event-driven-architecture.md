# ADR-0001: Why Event-Driven Architecture?

## Status
Accepted

## Date
2026-07-06

## Context
Helix is designed to run public governance workflows at a municipal and state level. The system handles citizen inputs (e.g. issues submitted via WhatsApp, SMS, web portals) and coordinates multi-department response workflows.
The requirements include:
* **High Auditability:** Every state change and decision must be loggable and transparent.
* **Temporal Decoupling:** Governance processes are slow-running, with human steps taking days or weeks.
* **Extensibility:** Municipalities must be able to deploy custom plugins and department systems without modifying the core platform.
* **Resilience:** The failure of one subsystem (such as AI suggestions or SMS dispatch) must not prevent the intake of citizen reports.

## Alternatives Considered

### Alternative 1: Monolithic Orchestration (Synchronous / Direct Database Writes)
* **Description:** A single large application where all modules (ingestion, workflow, notifications, plugins) communicate via direct function calls or share a single operational database.
* **Pros:** Simpler to develop initially; strict ACID transactions across all modules.
* **Cons:** Single point of failure; hard to scale components independently; plugins cannot easily hook into events without code modifications; no historic ledger of state transitions (only current state).

### Alternative 2: Synchronous Microservices (gRPC / HTTP API-Driven)
* **Description:** A microservice mesh where services communicate using blocking RPC calls (e.g., HTTP/gRPC).
* **Pros:** Decoupled codebase; services can be developed in different languages.
* **Cons:** Cascading failures (if the Notification service is down, the Ingestion service fails to process reports); complex circuit-breaking logic; tight coupling of APIs between services.

### Alternative 3: Event-Driven Architecture (Asynchronous Message Broker / Event Sourced Core)
* **Description:** Services communicate via asynchronous, immutable events. All core transitions are logged as events and pushed to interest-based subscribers.
* **Pros:** Total spatial and temporal decoupling; resilient to service down-time; native audit log of all historical events; scalable via parallel consumer groups; plug-and-play architecture for plugins.
* **Cons:** Eventual consistency; higher complexity in distributed state tracking; ordering and idempotency must be handled in application logic.

## Decision
We chose **Event-Driven Architecture (EDA)** as the communication and integration backbone of Helix.

By modeling the system state as a stream of immutable facts:
1. We align directly with the nature of civic governance (which is event-driven by default).
2. We establish a bulletproof, tamper-evident audit ledger required by public institutions.
3. We allow third-party plug-ins to extend the system without risk to the core engine.

## Consequences
* **Positive:**
  * Subsystems can fail independently without blocking citizen intake.
  * Audit logs are built into the fabric of the application (rather than being an afterthought).
  * We can replay historical events to rebuild database indices, migrate database technologies, or debug issues in a local environment.
* **Negative/Trade-offs:**
  * Distributed transactions are replaced by the Saga Pattern, requiring compensating actions when steps fail.
  * Consumers must implement idempotency handling to prevent double-processing.
  * System state is eventually consistent, meaning frontend clients must handle asynchronous updates.
