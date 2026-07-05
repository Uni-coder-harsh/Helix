---
owner: "@harsh"
version: "0.1.0"
status: "Draft"
last_updated: "2026-07-05"
reviewer: "@harsh"
dependencies: []
---

# Architecture Overview

This page serves as the entry point for the architectural designs of Project Helix.

> [!NOTE]
> System design, microservices division, and microservices contracts will be finalized in **Phase 2: Architecture**.

## Architectural Decisions

All architectural decisions are formally documented using **Architecture Decision Records (ADRs)** located in [adr/](file:///home/harsh/Desktop/CodeNova/Helix/adr/).

### ADR Catalog

| ADR ID | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| `ADR-001` | _(Placeholder for first ADR)_ | Proposed | 2026-07-05 |

## C4 Model

We use the C4 Model format (Context, Containers, Components, Code) to document the software architecture.

### Level 1: System Context Diagram

```mermaid
graph TD
    User([Helix User]) -->|Uses| Helix[Helix System]
    Helix -->|Retrieves data| DB[(Helix Knowledge Store)]
    Helix -->|Queries| LLM[Large Language Model Provider]
```
