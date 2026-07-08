---
spec_id: "HELIX-ARCH-006"
status: "Frozen"
version: "1.0.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-06"
dependencies: ["HELIX-ARCH-000", "HELIX-ARCH-003", "HELIX-ARCH-004", "HELIX-ARCH-005"]
related_adr: ["ADR-0001", "ADR-0002", "ADR-0003", "ADR-0004"]
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Frozen"
---

# HELIX-ARCH-006: Component Architecture

This document defines the logical component architecture of the Helix Governance Operating System. It details the boundaries, responsibilities, input/output structures, dependencies, failure behaviors, and scaling strategies for all major system blocks.

---

## 1. Executive Summary

Helix is decomposed into discrete, logical components designed to isolate failures, maintain domain consistency, and enable modular scalability. This document details the 14 building blocks that form the logical core of Helix.

Each component corresponds to a specific bounded context or utility layer within the system context. To keep Helix technology-neutral, these components are defined conceptually without reference to specific communication protocols, token formats, database engine names, or hardware-specific acceleration types.

---

## 2. Core Components Registry

```
  ┌───────────────────────────────────────────────────────────┐
  │                        API Gateway                        │
  └─────────────────────────────┬─────────────────────────────┘
                                ▼
  ┌───────────────────────┬───────────┬───────────────────────┐
  │   Citizen Intake      │ Identity  │    Administration     │
  └──────────┬────────────┴───────────┴───────────┬───────────┘
             │                                    │
             ▼                                    ▼
  ┌───────────────────────┐           ┌───────────────────────┐
  │    Workflow Engine    │◄──────────│ AI Orchestrator (Advy)│
  └──────────┬────────────┘           └───────────┬───────────┘
             │                                    │
  ┌──────────┼────────────┬───────────┬───────────┼───────────┐
  │          ▼            ▼           ▼           ▼           │
  │    Notification    Knowledge    Plugin    Dec Intelligence│
  │      Service        Service    Runtime     Service / Audit│
  └───────────────────────────────────────────────────────────┘
```

### 2.1. API Gateway
* **Responsibility:** Acts as the single entrance boundary for all external user interfaces and connection endpoints. Handles authentication verification, request routing, rate limiting, and cross-boundary request controls.
* **Inputs:** External requests from client applications.
* **Outputs:** Routed internal service requests, client-facing responses.
* **Dependencies:** Identity Service (session and authentication token validation).
* **Owned Domain:** None (Infrastructure/Routing edge).
* **Events Produced:** `AccessLogGenerated` (via Audit service interceptor).
* **Events Consumed:** `RoleAssigned` (used to update authorization routing maps).
* **Failure Behaviour:** Run in redundant configurations behind a global load balancer. If an API Gateway instance fails, traffic is failover routed to active instances. If all gateways are offline, client portals fallback to local storage queues.
* **Scaling Strategy:** Stateless, scaled horizontally based on active request throughput and concurrent connection counts.

### 2.2. Identity Service
* **Responsibility:** Governs authentication, registration, user profiles, and Role-Based Access Control (RBAC) definitions. Issues, revokes, and validates security tokens.
* **Inputs:** Login credentials, external identity claims, permission modification commands.
* **Outputs:** Signed identity tokens, user profile schemas, verification status.
* **Dependencies:** Operational data store (user credentials).
* **Owned Domain:** User Accounts, Security Roles, User Sessions.
* **Events Produced:** `RoleAssigned`.
* **Events Consumed:** `CitizenOptedOut` (purges credentials and session states).
* **Failure Behaviour:** Active identity tokens are cryptographically self-contained. Caching of active tokens at the API Gateway layer ensures that if the Identity Service goes offline, existing active sessions continue executing, but new authentication requests will fail.
* **Scaling Strategy:** Read-heavy service. Employs distributed caching of roles and permissions to scale read operations horizontally.

### 2.3. Citizen Intake
* **Responsibility:** Ingests raw communications from edge messaging connectors (text, audio reports, or images). Validates edge signatures, strips potentially malicious payloads, registers media assets, and publishes standardized ingestion envelopes.
* **Inputs:** Edge gateway callbacks, file binary streams.
* **Outputs:** Ingested raw reports, file references.
* **Dependencies:** Media Service (storing raw assets).
* **Owned Domain:** Raw Submissions, Ingestion Channels.
* **Events Produced:** `CitizenReportSubmitted`.
* **Events Consumed:** None.
* **Failure Behaviour:** Inbound messages are buffered by external messaging platforms during temporary intake downtime. The service handles failures gracefully by returning standard receipt statuses to upstream connectors, allowing them to manage retry intervals.
* **Scaling Strategy:** High-throughput, stateless. Scaled horizontally based on message ingestion queues.

### 2.4. Workflow Engine
* **Responsibility:** Serves as the central state coordinator for all governance issues and sub-tasks. Enforces routing logic, registers changes, assigns departments, monitors SLAs, and coordinates Sagas.
* **Inputs:** Status updates, department assignments, verification documents.
* **Outputs:** Updated state models, assignment details, task configurations.
* **Dependencies:** Operational data store (ensuring strict transaction boundaries), Knowledge Service (for geography and policy checks).
* **Owned Domain:** Issues, Tasks, SLA Tracks.
* **Events Produced:** `IssueValidated`, `EvidenceAttached`, `DepartmentAssigned`, `TaskCreated`, `TaskCompleted`, `IssueResolved`, `SLAThresholdExceeded`.
* **Events Consumed:** `CitizenReportSubmitted`, `CitizenFeedbackSubmitted`, `RecommendationGenerated`, `EvidenceClustered`, `PluginResponseReturned`, `PluginExecutionFailed`, `SchemeConfigured`, `RoleAssigned`.
* **Failure Behaviour:** Workflow state updates execute in database transactions. If a crash occurs, execution rolls back to the last persistent checkpoint, and the engine re-processes the event from the queue.
* **Scaling Strategy:** Partitioned horizontally based on `issue_id`. Each node handles a specific partition group to avoid resource contention.

### 2.5. AI Orchestrator
* **Responsibility:** Executes unstructured semantic processing. Classifies report categories, extracts locations from text/audio, groups similar reports into structural clusters, checks submission guardrails, and drafts suggested replies.
* **Architectural Invariant:** The AI Orchestrator never performs administrative state mutations. It only produces recommendations. The Workflow Engine remains the sole authority for state transitions.
* **Inputs:** Raw report texts, audio transcripts, media assets.
* **Outputs:** Classification recommendations, routing models, duplicate cluster mappings, anomaly markers.
* **Dependencies:** Search Service (retrieving grounding contexts), Knowledge Service (mapping domain relationships), Media Service (accessing raw attachments).
* **Owned Domain:** AI Grounding, Recommendations, Similarity Clusters.
* **Events Produced:** `RecommendationGenerated`, `EvidenceClustered`, `AnomalyDetected`.
* **Events Consumed:** `CitizenReportSubmitted`, `IssueValidated`, `EvidenceAttached`.
* **Failure Behaviour:** Advisory design principle. If the AI Orchestrator fails, the Workflow Engine defaults to standard manual triage queues or basic routing rules. System execution does not stall.
* **Scaling Strategy:** Inference nodes are scaled horizontally. Computationally expensive model queries are offloaded to dedicated accelerated processing nodes or external model API endpoints.

### 2.6. Knowledge Service
* **Responsibility:** Manages the administrative Knowledge Graph. Structures regional boundaries, department hierarchies, policy rules, and scheme criteria. Acts as the structural authority for entities and relationships.
* **Inputs:** Graph entity updates, structural hierarchy queries.
* **Outputs:** Entity relationship contexts, policy definitions, structural hierarchies.
* **Dependencies:** Knowledge Graph database.
* **Owned Domain:** Knowledge Graph Nodes, Ward Boundaries, Scheme Policies.
* **Events Produced:** None.
* **Events Consumed:** `IssueValidated`, `EvidenceAttached`, `DepartmentAssigned`, `IssueResolved`, `SchemeConfigured`.
* **Failure Behaviour:** Uses read-replicated nodes. If the primary graph database fails, read queries continue via secondary data read paths, while write updates are buffered and retried.
* **Scaling Strategy:** Scaled by deploying multiple read-replicated nodes. Graph mutations are directed through a single transactional writer node.

### 2.7. Search Service
* **Responsibility:** Provides full-text lexical search, semantic vector retrieval, hybrid search, indexing, ranking, and high-speed retrieval of issues, citizen submissions, tasks, and historical logs.
* **Inputs:** Search queries, indexing documents, vector query parameters.
* **Outputs:** Ranked match lists, search facets, retrieved contexts.
* **Dependencies:** Operational data store (for indexing).
* **Owned Domain:** Search Indices.
* **Events Produced:** None.
* **Events Consumed:** `IssueValidated`, `EvidenceAttached`, `IssueResolved`.
* **Failure Behaviour:** Decoupled. If Search Service is down, portal search functionalities are disabled, but core intake and task execution continue.
* **Scaling Strategy:** Search index nodes are sharded and replicated horizontally across independent search instances.

### 2.8. Notification Service
* **Responsibility:** Coordinates outbound citizen and administrator communications. Hydrates message templates, manages channel selection (chat messaging, SMS, Email), and ensures delivery confirmation logs.
* **Inputs:** Notification templates, target parameters, contact metadata.
* **Outputs:** Hydrated message texts, gateway payloads.
* **Dependencies:** External communication gateways.
* **Owned Domain:** Message Templates, Dispatch Logs.
* **Events Produced:** `DispatchSucceeded`, `DispatchFailed`.
* **Events Consumed:** `AlertEnqueued`, `CitizenOptedOut`.
* **Failure Behaviour:** If an external gateway fails, the service attempts delivery on alternative channels or queues the event for a backoff-retry loop.
* **Scaling Strategy:** Scaled horizontally. Workloads are sharded by recipient ID to prevent message ordering violations.

### 2.9. Plugin Runtime
* **Responsibility:** Runs third-party plugins in isolated sandboxes. Manages dynamic loading, passes event context, limits resources, and captures execution metrics.
* **Inputs:** Hook configuration files, context mapping payloads.
* **Outputs:** Execution data returns, error logs, trace metrics.
* **Dependencies:** Media Service (downloading packaged plugin modules).
* **Owned Domain:** Sandbox Registrations, Hook Interfaces.
* **Events Produced:** `PluginResponseReturned`, `PluginExecutionFailed`.
* **Events Consumed:** `HookTriggered`.
* **Failure Behaviour:** If a plugin crashes or times out, the Runtime terminates the specific sandbox, logs diagnostic data, and publishes `PluginExecutionFailed`. Core platform memory remains isolated.
* **Scaling Strategy:** Scale execution worker pools horizontally based on active hook traffic.

### 2.10. Audit Service
* **Responsibility:** Provides cryptographically secured, immutable audit entries for administrative actions, data exports, and configuration changes.
* **Inputs:** Access request contexts, audit parameters.
* **Outputs:** Cryptographic hashes, compliance reports.
* **Dependencies:** Immutable storage layer.
* **Owned Domain:** Access Logs, Configuration overrides.
* **Events Produced:** `AccessLogGenerated`.
* **Events Consumed:** `SchemaChanged`, `AccessLogGenerated` (archiving self), `SystemConfigOverridden`.
* **Failure Behaviour:** Fail-secure. If the Audit Service cannot persist logs, the API Gateway blocks all administrative mutations until logging integrity is restored.
* **Scaling Strategy:** Optimised for high-speed writes. Sharded by actor context ID.

### 2.11. Decision Intelligence Service
* **Responsibility:** Computes high-level performance indicators, outcomes, SLAs, and decision metrics. Aggregates satisfaction feedback and operational reports. Provides analytical insight to support administrative decision-making (dashboards act as consumers of this intelligence).
* **Inputs:** Multi-service metrics, feedback ratings, operational stats.
* **Outputs:** Aggregated performance outcomes, trend analysis, trend projections.
* **Dependencies:** Replicas of operational and graph databases.
* **Owned Domain:** Performance Metrics, Outcome Logs.
* **Events Produced:** None.
* **Events Consumed:** `CitizenFeedbackSubmitted`, `DepartmentAssigned`, `TaskCompleted`, `IssueResolved`, `SLAThresholdExceeded`, `DispatchSucceeded`.
* **Failure Behaviour:** Isolated. Failure does not impact operational workflows. Dashboards show cached/stale data until recovery.
* **Scaling Strategy:** Uses streaming aggregates. Scales out analytics ingestion nodes separately from query API instances.

### 2.12. Administration Service
* **Responsibility:** Handles administrative configurations: registering schemes, setting organizational boundaries, adjusting SLA allocations, and defining system configurations.
* **Inputs:** Settings updates, policy forms.
* **Outputs:** Scheme configuration definitions.
* **Dependencies:** Operational database storage.
* **Owned Domain:** System Properties, Scheme settings.
* **Events Produced:** `SchemeConfigured`, `SystemConfigOverridden`.
* **Events Consumed:** None.
* **Failure Behaviour:** Configurations are versioned in database tables. If an update fails, changes are rejected, and the system rolls back to the last active configuration snapshot.
* **Scaling Strategy:** Low transactional volume. Deployed in a simple two-node configuration.

### 2.13. Configuration Service
* **Responsibility:** Central repository for system-wide environment variables, secrets management, and real-time feature flag variables.
* **Inputs:** Bootstrapping configuration queries, toggle configurations.
* **Outputs:** Config definitions, feature toggles.
* **Dependencies:** Distributed consensus coordinator.
* **Owned Domain:** Environment Settings, Feature Flags.
* **Events Produced:** None.
* **Events Consumed:** `SystemConfigOverridden` (triggers configuration cache refresh).
* **Failure Behaviour:** Read configurations are cached locally in memory by each service container during bootstrapping. If the Configuration Service goes down, services run on local caches, but configurations cannot be updated.
* **Scaling Strategy:** Read-heavy, heavily cached, using transactional consensus nodes.

### 2.14. Media Service
* **Responsibility:** Manages the media lifecycle: uploads, downloads, media metadata, retention, and deletion of unstructured assets (such as photos, voice reports, compiled WebAssembly plugin packages).
* **Inputs:** Binary upload streams, file retrieval identifiers.
* **Outputs:** Asset URLs, byte download streams.
* **Dependencies:** Blob/object storage infrastructure.
* **Owned Domain:** Unstructured Assets, Media metadata.
* **Events Produced:** `EvidenceAttached` (triggered contextually).
* **Events Consumed:** `CitizenOptedOut` (commands deletion of files containing citizen data).
* **Failure Behaviour:** Redundant storage configuration. If a storage node or zone fails, requests are served from mirrored zones.
* **Scaling Strategy:** Storage nodes scale out horizontally. Static media requests are offloaded to edge cache networks.

---

## 3. Traceability Matrix

This matrix maps every core component to its owned domain boundaries, events, architectural decision records, and parent specifications.

| Component | Bounded Domain | Events Produced | Events Consumed | Related ADRs | Parent Specifications |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **API Gateway** | Routing Boundary | `EVT-602` | `EVT-502` | `ADR-0001` | `ARCH-001`, `ARCH-002`, `ARCH-003` |
| **Identity Service** | User Accounts | `EVT-502` | `EVT-103` | None | `ARCH-003` |
| **Citizen Intake** | Intake Ingestion | `EVT-101` | None | `ADR-0001` | `ARCH-001`, `ARCH-002`, `ARCH-003` |
| **Workflow Engine** | Issues & Tasks | `EVT-201` to `EVT-206`, `EVT-503` | `EVT-101`, `EVT-102`, `EVT-301`, `EVT-302`, `EVT-501`, `EVT-502`, `EVT-702`, `EVT-703` | `ADR-0001` | `ARCH-003`, `ARCH-004`, `ARCH-005` |
| **AI Orchestrator** | AI Grounding | `EVT-301` to `EVT-303` | `EVT-101`, `EVT-201`, `EVT-202` | `ADR-0003`, `ADR-0004` | `ARCH-003`, `ARCH-004`, `ARCH-005` |
| **Knowledge Service** | Knowledge Graph | None | `EVT-201`, `EVT-202`, `EVT-203`, `EVT-206`, `EVT-501` | `ADR-0004` | `ARCH-003`, `ARCH-004`, `ARCH-005` |
| **Search Service** | Search Indices | None | `EVT-201`, `EVT-202`, `EVT-206` | None | `ARCH-003` |
| **Notification Service**| Alert Dispatch | `EVT-402`, `EVT-403` | `EVT-401`, `EVT-103` | `ADR-0001` | `ARCH-003`, `ARCH-005` |
| **Plugin Runtime** | Sandboxing | `EVT-702`, `EVT-703` | `EVT-701` | `ADR-0002` | `ARCH-003`, `ARCH-005` |
| **Audit Service** | System Security | `EVT-602` | `EVT-601`, `EVT-602`, `EVT-603` | `ADR-0001` | `ARCH-003`, `ARCH-005` |
| **Decision Intel Service**| Performance | None | `EVT-102`, `EVT-203`, `EVT-205`, `EVT-206`, `EVT-402`, `EVT-503` | `ADR-0001` | `ARCH-003`, `ARCH-005` |
| **Admin Service** | Configuration | `EVT-501`, `EVT-603` | None | None | `ARCH-003`, `ARCH-005` |
| **Config Service** | Feature Flags | None | `EVT-603` | None | `ARCH-003` |
| **Media Service** | Media Files | `EVT-202` | `EVT-103` | None | `ARCH-003` |

---

## 4. Design Validation Checklist

Before freezing any downstream implementation design, verify the component layout against these checks:

* [ ] **Bounded Isolation:** Does the component interact only through defined events or API gateways, avoiding shared database writes?
* [ ] **Stateless Target:** Are components designed as stateless services (excluding specific database adapters) to allow simple horizontal scaling?
* [ ] **Graceful Degradation:** If dependent services (such as AI Orchestrator or Notification Service) are down, can the component complete its core processing?
* [ ] **Audit Interception:** Are all write modifications or sensitive PII reads routed to trigger corresponding Audit events?
* [ ] **Traceability Confirmed:** Are all event consumer definitions in the component registered in the parent Event Catalog (`ARCH-005`)?
* [ ] **Local Cache Strategy:** Do components cache configuration parameters locally to maintain survival capabilities during configuration outages?
* [ ] **Outbox Integrated:** Do state-mutating components implement transactional outbox patterns to guarantee at-least-once event delivery?
* [ ] **Crypto-Shredding Compliance:** Can storage-heavy components (Media Service, Relational DBs) isolate and destroy records mapped to an opted-out `citizen_id`?
