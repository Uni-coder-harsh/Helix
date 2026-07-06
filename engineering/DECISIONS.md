# Architectural Decisions

This document registers critical design and integration choices made during the Helix implementation cycle.

| Decision ID | Date | Title | Rationale | Status | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEC-001** | 2026-07-06 | **Event-Driven Outbox** | Decouples event propagation from database transactions ensuring transactional consistency. | Accepted | [ADR-0001](file:///home/harsh/Desktop/CodeNova/Helix/adr/ADR-0001-why-event-driven-architecture.md) |
| **DEC-002** | 2026-07-06 | **7 Services Consolidation** | Prevents operational overhead by combining 14 logical blocks into 7 microservice containers. | Accepted | [ADR-0002](file:///home/harsh/Desktop/CodeNova/Helix/adr/ADR-0002-microservice-strategy.md) |
| **DEC-003** | 2026-07-06 | **Modular Monolith First** | Maximizes prototyping velocity by packaging services in a single repository sharing local event buses. | Accepted | [ADR-0003](file:///home/harsh/Desktop/CodeNova/Helix/adr/ADR-0003-modular-monolith-first.md) |
| **DEC-004** | 2026-07-06 | **Namespace Renaming** | Renamed `platform/` package to `helix_platform/` to resolve namespace shadowing with the standard `platform` module. | Accepted | N/A |
| **DEC-005** | 2026-07-06 | **Keyword-only Dataclasses** | Enabled `kw_only=True` on Command and Query dataclasses to support attribute inheritance with default values. | Accepted | N/A |
