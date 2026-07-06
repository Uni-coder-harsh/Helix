---
spec_id: "HELIX-ARCH-007"
status: "Frozen"
version: "1.0.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-06"
dependencies: ["HELIX-ARCH-000", "HELIX-ARCH-003", "HELIX-ARCH-004", "HELIX-ARCH-006"]
related_adr: ["ADR-0001", "ADR-0002", "ADR-0003", "ADR-0004"]
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Frozen"
---

# HELIX-ARCH-007: Microservice Boundaries

This document defines the production service decomposition strategy for the Helix Governance Operating System. It establishes the rules for service creation, boundary definitions, data ownership, communication protocols, and the logical repository organization.

---

## 1. Executive Summary

Helix transitions from conceptual design to engineering organization by establishing concrete service boundaries. To prevent microservice over-engineering and network complexity, Helix consolidates its 14 logical component building blocks into **7 deployable services**.

This document sets the architectural rules that govern service separation, defines the communication boundaries, establishes database ownership rules to prevent shared-write conflicts, maps the codebase directory structure, and outlines the step-by-step evolutionary path from a modular monolith to a distributed microservices platform.

---

## 2. Service Creation Governance

Premature service decomposition leads to distributed monoliths, network latency issues, and complex deployment coordination. Helix enforces a strict policy for splitting code into a separate deployable service.

### 2.1. Helix Service Creation Rule
A logical module or component may only be extracted or created as an independent microservice if it satisfies **at least 4 of the following 6 conditions**:

1. **Independent Business Capability:** The component owns a distinct domain boundary with minimal overlap in core logic.
2. **Independent Scaling Requirements:** The component exhibits resource usage profiles (e.g. CPU, memory, IO) that differ significantly from core operations.
3. **Distinct Lifecycle:** The frequency of updates, CI/CD pipeline runs, and release schedules are fundamentally different.
4. **Distinct Data Ownership Boundary:** The component operates on a dedicated dataset that is not directly manipulated by other domains.
5. **Independent Deployment:** The component can be compiled, deployed, restarted, and scaled without requiring coordinated updates of other services.
6. **Independent Team Ownership:** The component's scale and scope warrant dedicated ownership by a separate engineering sub-team.

---

## 3. Service Registry & Justification Mappings

Applying the service creation rule, the 14 logical components are compiled into 7 deployable services.

```
                                 [ API Gateway ]
                                        │ (External Request Routing)
 ┌──────────────────────────────────────┼──────────────────────────────────────┐
 ▼                                      ▼                                      ▼
[ Identity Service ]           [ Governance Service ]               [ AI Platform Service ]
   (User Accounts)                - Citizen Ingestion                  - AI Orchestration
                                  - Workflow Engine                    - Knowledge Graph
                                  - Administration                     - Search Indexes
                                  - Notification Orchestrator
                                        │ (Plugin Intercept Hooks)
                                        ▼
                               [ Plugin Runtime ]
                                  (Isolated Sandboxes)

 ┌──────────────────────────────────────┼──────────────────────────────────────┐
 ▼                                      ▼                                      ▼
[ Media Service ]              [ Audit & Compliance ]               [ Dec Intelligence Service ]
   (Blob Management)              (Access/Config Logs)                 (Performance & Metrics)
```

### 3.1. API Gateway
* **Purpose:** Handles ingress request routing, rate limiting, and access control validation.
* **Justification Mapping:**
  * *Independent Capability:* Yes (edge traffic routing).
  * *Independent Scaling:* Yes (scales on network socket count and traffic volume, not database transaction load).
  * *Distinct Lifecycle:* Yes (changed rarely, strictly configuration-driven).
  * *Independent Deployment:* Yes.
  * *Distinct Data:* No (stateless).
  * *Independent Team:* Yes (owned by Platform/Infrastructure Team).
  * *Score:* 5/6. **Justified.**

### 3.2. Governance Service
* **Purpose:** Consolidated service managing raw citizen ingestion, the core workflow engine state machine, notification orchestration, and administrative scheme setups.
* **Justification Mapping:**
  * *Independent Capability:* Yes (governs active workflow states and citizen intake).
  * *Independent Scaling:* Yes (heavy database read/write transaction load).
  * *Distinct Lifecycle:* Yes (highest frequency of business logic changes).
  * *Distinct Data:* Yes (owns Issues, Tasks, and SLA tables).
  * *Independent Deployment:* Yes.
  * *Independent Team:* Yes (owned by Core Workflows Team).
  * *Score:* 6/6. **Justified.**

### 3.3. AI Platform Service
* **Purpose:** Consolidates the AI Orchestrator, Search Service, and Knowledge Service into a single logical service block. Maps policy rules, runs search indexes, and serves AI recommendations.
* **Justification Mapping:**
  * *Independent Capability:* Yes (cognitive reasoning and search retrieval).
  * *Independent Scaling:* Yes (computationally heavy, GPU/large RAM requirements for vector databases and graph caches).
  * *Distinct Lifecycle:* Yes (driven by model updates, search indexing logic, and graph structure refactoring).
  * *Distinct Data:* Yes (owns Knowledge Graph, search indexes, and vector embeddings).
  * *Independent Deployment:* Yes.
  * *Independent Team:* Yes (owned by Data/AI Engineering Team).
  * *Score:* 6/6. **Justified.**

### 3.4. Identity Service
* **Purpose:** Manages user authentication, profile states, permissions, and roles.
* **Justification Mapping:**
  * *Independent Capability:* Yes (identity and security access control).
  * *Independent Scaling:* Yes (highly read-heavy, low latency requirements).
  * *Distinct Lifecycle:* Yes (infrequent updates, changes demand high-security review).
  * *Distinct Data:* Yes (owns User Credentials, Session logs, and RBAC tables).
  * *Independent Deployment:* Yes (must remain functional even during core workflow downtime).
  * *Independent Team:* Yes (owned by Security Team).
  * *Score:* 6/6. **Justified.**

### 3.5. Plugin Runtime
* **Purpose:** Orchestrates sandboxed subprocess execution for custom third-party plugins.
* **Justification Mapping:**
  * *Independent Capability:* Yes (untrusted code execution).
  * *Independent Scaling:* Yes (burst-scaling based on plugin hook runs; requires absolute memory/CPU limits).
  * *Distinct Lifecycle:* Yes (very stable codebase; changes occur only when Plugin SDK contract changes).
  * *Distinct Data:* No (stateless execution).
  * *Independent Deployment:* Yes (preventing plugin memory leaks from affecting the core).
  * *Independent Team:* Yes (owned by Platform Team).
  * *Score:* 5/6. **Justified.**

### 3.6. Decision Intelligence Service
* **Purpose:** Computes high-level performance metrics, outcome modeling, priority scoring, and administrative forecasting.
* **Justification Mapping:**
  * *Independent Capability:* Yes (analytical processing and business intelligence).
  * *Independent Scaling:* Yes (batch-aggregation heavy, streaming computations).
  * *Distinct Lifecycle:* Yes (bi-weekly updates driven by administrative reporting requirements).
  * *Distinct Data:* Yes (owns aggregated metrics data cache).
  * *Independent Deployment:* Yes.
  * *Independent Team:* Yes (owned by Data Analytics Team).
  * *Score:* 6/6. **Justified.**

### 3.7. Media Service
* **Purpose:** Manages the media lifecycle, including uploads, downloads, media metadata, retention, and deletion of unstructured citizen/workflow assets.
* **Justification Mapping:**
  * *Independent Capability:* Yes (blob asset management).
  * *Independent Scaling:* Yes (high network IO bandwidth consumption).
  * *Distinct Lifecycle:* Yes (tied to storage driver configurations).
  * *Distinct Data:* Yes (owns media metadata and storage key indexes).
  * *Independent Deployment:* Yes.
  * *Independent Team:* No (owned by Platform Team).
  * *Score:* 5/6. **Justified.**

---

## 4. Bounded Context & Data Ownership Matrix

To prevent data corruption, Helix enforces a strict data ownership rule: **Only one service may own and write to a specific database domain.** Other services must access data either asynchronously via event subscriptions, or by querying read-only replicas of the owning service's database.

| Domain Entities | Owner Service | Data Store Pattern | Primary Write Actor | Read Access Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Issues, Tasks, SLAs** | Governance Service | Relational database (ACID transactional) | Workflow Engine | Read replicas, Async events |
| **User Credentials, RBAC** | Identity Service | Relational database (highly cached) | Identity Manager | API Gateway token verification |
| **Media Files, Metadata** | Media Service | Relational metadata + Blob Store keys | Media Manager | Signed URL token generation |
| **Knowledge Graph, Policies**| AI Platform Service | Graph database | Knowledge Manager | Graph-RAG queries (Internal to AI) |
| **Search Indexes** | AI Platform Service | Search index store | Search Indexer | API Gateway search routing |
| **Recommendations, Anomaly** | AI Platform Service | Memory/Inference logs | AI Orchestrator | Workflow Engine review console |
| **Audit Logs** | Audit Service | Immutable transaction log | Audit Logger | Security Compliance Portal |
| **Performance Aggregates** | Decision Intel Service| Analytics database cache | Analytics Stream Engine | Administrative dashboards |

---

## 5. Service Communication Specifications

### 5.1. Sync vs. Async Communication Rules
* **Synchronous (gRPC / HTTP API):** Reserved for real-time validation checks, security validation, or request-reply operations that cannot proceed without immediate return data (e.g. gateway authentication checking, sandboxed hook execution).
* **Asynchronous (Event-Driven Bus):** The default communication protocol for all state changes, notification requests, audit archiving, and downstream analytical updates. Ensures total temporal decoupling.

### 5.2. Service Communication Matrix

| Source Service | Target Service | Sync Interface | Async Events | Forbidden Communication |
| :--- | :--- | :--- | :--- | :--- |
| **API Gateway** | Governance Service | REST/gRPC (Intake routing) | None | Direct Database access |
| **API Gateway** | AI Platform Service | REST/gRPC (Search queries) | None | Direct Database access |
| **API Gateway** | Identity Service | REST/gRPC (Token verify) | None | Direct Database access |
| **Governance** | AI Platform Service | None | `IssueValidated`, `EvidenceAttached` | Synchronous blocking queries |
| **Governance** | Plugin Runtime | gRPC (Hook execution) | None | Direct database writes to Plugin |
| **Governance** | Media Service | gRPC (Verify file hash) | None | Bypassing Media API |
| **AI Platform** | Media Service | gRPC (Fetch binary) | None | Direct filesystem access |
| **AI Platform** | Governance Service | None | `RecommendationGenerated` | Synchronous state mutation calls |
| **Plugin Runtime** | Governance Service | None | `PluginResponseReturned` | Synchronous API callbacks |
| **Decision Intel** | Governance Service | None (Uses replica reads) | None | Writing to Governance tables |
| **All Services** | Audit Service | None | `AccessLogGenerated` | Blocking synchronous audits |

### 5.3. Dependency Rules & Forbidden Topologies
To prevent circular dependencies and cascade failures:
* **No Upstream Calls:** Downstream infrastructure/leaf services (Media, Identity, Plugin Runtime) are forbidden from invoking upstream business services (Governance, AI Platform).
* **No Circular Dependencies:** A service must never invoke a component that synchronously calls it back (e.g. Governance Service must not block on AI Platform, while AI Platform blocks on Governance).
* **Identity Isolation:** The Identity Service must remain completely independent. It is forbidden from depending on the Governance Service or AI Platform Service.

---

## 6. Repository Layout (Directory Mapping)

Helix enforces a unified Monorepo structure during Phase 1 to streamline shared contracts and libraries, preparing logical modules for clean separation in Phase 2.

```text
backend/
├── services/
│   ├── governance/                # Core workflows & intake logic
│   │   ├── src/
│   │   └── package.json
│   ├── identity/                  # Auth, RBAC, and session profiles
│   ├── ai-platform/               # AI Orchestrator, Graph, Search Service
│   ├── media/                     # Media lifecycle and metadata manager
│   ├── audit/                     # Cryptographic audit logging
│   ├── plugin/                    # Isolated sandbox manager
│   └── decision-intelligence/     # Analytical computations and aggregates
├── shared/
│   ├── contracts/                 # Unified domain configurations
│   ├── events/                    # Event Catalog JSON-Schema/Protobuf models
│   ├── protos/                    # Central gRPC boundary interfaces
│   └── sdk/                       # Standard Plugin development SDK
└── libs/
    ├── telemetry/                 # Shared OpenTelemetry configuration
    ├── security/                  # Cryptographic token utils
    └── db-utils/                  # Shared database transaction helper abstractions
```

---

## 7. Evolutionary Strategy

Helix prevents over-engineering by migrating through three distinct lifecycle phases:

```
[Phase 1: Hackathon]       [Phase 2: Pilot]            [Phase 3: Enterprise]
- Modular Monolith         - Hybrid Deployment         - Full Microservices
- Single Database          - Database Separation       - Multi-Region Sharding
- Process-level events     - Network-level event bus   - High Availability cluster
```

### 7.1. Phase 1 (Hackathon & Prototyping)
* **Topology:** **Modular Monolith**. All 7 services are implemented as separate packages inside the monorepo but run compiled together within a single process.
* **Database:** Single relational database containing separate schemas for each domain, alongside a local graph/search mock instance.
* **Communication:** Process-level event propagation. Zero network latency overhead.

### 7.2. Phase 2 (Pilot & Regional Deployment)
* **Topology:** **Hybrid Deployment**. Core services split into independent network boundaries:
  * Governance Service (independent container).
  * Identity Service (independent container).
  * Media Service (independent container).
  * AI Platform Service (independent container).
  * Audit, Plugin, and Decision Intelligence services remain modules inside the Governance Service container.
* **Database:** Relational Database splits physically from the Graph Database.
* **Communication:** Network-level event bus (standard message broker).

### 7.3. Phase 3 (State/Enterprise Scaling)
* **Topology:** **Full Microservices**. All 7 services are deployed as independent, auto-scaling containers across multiple fault-tolerant zones.
* **Database:** Complete database separation. Each service runs on a dedicated physical data store instance with zero cross-service connections.
* **Communication:** Fully sharded event streams, partitioned by `issue_id` or `citizen_id` with active dead-letter quarantining.

---

## 8. Design Validation Checklist

Verify implementation configurations against these architectural rules before deploying:

* [ ] **Condition Test Passed:** Does every extracted service satisfy at least 4 of the 6 Service Creation conditions?
* [ ] **Database Isolation:** Does any database query perform direct cross-schema joins? (If yes, refactor to API lookup or async event sync).
* [ ] **No Circular Calls:** Are there any synchronous routing paths that loop back to the initiating service?
* [ ] **Leaf Isolation:** Do leaf services (Identity, Media, Plugin Runtime) remain independent of upstream business services?
* [ ] **Outbox Integrated:** Do state-mutating services compile event releases within their primary database transactions?
* [ ] **Repository Compliance:** Does the folder directory structure map exactly to the `backend/services/` monorepo layout?
* [ ] **Evolution Track Defined:** Is the module prepared to bootstrap as a process-level package (Phase 1) prior to network boundary separation?
