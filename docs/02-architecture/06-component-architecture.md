---
spec_id: "HELIX-ARCH-006"
status: "Draft"
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
lifecycle: "Draft"
---

# HELIX-ARCH-006: Component Architecture

This document defines the logical component architecture of the Helix Governance Operating System. It details the boundaries, responsibilities, input/output structures, dependencies, failure behaviors, and scaling strategies for all major system blocks.

---

## 1. Executive Summary

Helix is decomposed into discrete, logical components designed to isolate failures, maintain domain consistency, and enable modular scalability. This document details the 14 building blocks that form the logical core of Helix.

Each component corresponds to a specific bounded context or utility layer within the system context. To keep Helix technology-independent, these components are defined conceptually without reference to specific frameworks, database engines, or container runtimes.

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
  │    Notification    Knowledge    Plugin      Audit     Search  │
  └───────────────────────────────────────────────────────────┘
```

### 2.1. API Gateway
* **Responsibility:** Acts as the single entrance boundary for all external user interfaces and connection endpoints. Handles authentication token validation, request routing, rate limiting, and cross-origin resource sharing (CORS) enforcement.
* **Inputs:** External HTTP/gRPC API requests from client applications (Portals, Mobile, Edge Connectors).
* **Outputs:** Routed internal payloads, client-facing JSON/gRPC responses.
* **Dependencies:** Identity Service (session and token validation).
* **Owned Domain:** None (Infrastructure/Routing edge).
* **Events Produced:** `AccessLogGenerated` (via Audit service interceptor).
* **Events Consumed:** `RoleAssigned` (used to update authorization routing maps).
* **Failure Behaviour:** Run in active-active high-availability groups behind a geo-balanced DNS load balancer. If an API Gateway node fails, traffic failover is handled immediately at the DNS level. If all gateways are offline, client portals fallback to local storage queues.
* **Scaling Strategy:** Stateless, scaled horizontally based on active connection throughput, bandwidth, and concurrency limits.

### 2.2. Identity Service
* **Responsibility:** Governs authentication, registration, user profiles, and Role-Based Access Control (RBAC) definitions. Issues, revokes, and validates security tokens.
* **Inputs:** Sign-up details, credentials, third-party authentication tokens (OAuth/OIDC), permission modification commands.
* **Outputs:** Signed access tokens (JWTs), user information schemas, verification status.
* **Dependencies:** Relational database storage (user authentication tables).
* **Owned Domain:** User Accounts, Security Roles, User Sessions.
* **Events Produced:** `RoleAssigned`.
* **Events Consumed:** `CitizenOptedOut` (triggers immediate purge of personal profiles and session states).
* **Failure Behaviour:** Active access tokens are cryptographically self-contained. Caching of active tokens at the API Gateway layer ensures that if the Identity Service goes offline, existing active sessions continue executing, but new sign-ins will fail.
* **Scaling Strategy:** Read-heavy service. Employs aggressive distributed caching of roles and configurations to scale read operations horizontally.

### 2.3. Citizen Intake
* **Responsibility:** Ingests raw communications from edge messaging connectors (WhatsApp, SMS, Email, web portals). Validates edge signatures, strips potentially malicious payloads, registers media assets, and publishes standardized ingestion envelopes.
* **Inputs:** Edge gateway webhooks, file binary streams.
* **Outputs:** Ingested raw reports, file references.
* **Dependencies:** Object Storage (storing raw assets).
* **Owned Domain:** Raw Submissions, Ingestion Channels.
* **Events Produced:** `CitizenReportSubmitted`.
* **Events Consumed:** None.
* **Failure Behaviour:** Incoming messages are buffered by external messaging gateways (e.g., WhatsApp Business, Twilio) during temporary intakes downtime. The service handles failures gracefully by returning standard receipt statuses to gateways, letting them manage retry intervals.
* **Scaling Strategy:** High-throughput, stateless. Scaled horizontally based on message ingestion queues.

### 2.4. Workflow Engine
* **Responsibility:** Serves as the central state coordinator for all governance issues and sub-tasks. Enforces routing logic, registers changes, assigns departments, monitors SLAs, and coordinates Sagas.
* **Inputs:** Status updates, department assignments, verification documents.
* **Outputs:** Updated state models, assignment details, task configurations.
* **Dependencies:** Relational operational data store (ensuring strict ACID transactional state updates), Knowledge Service (for geography and policy checks).
* **Owned Domain:** Issues, Tasks, SLA Tracks.
* **Events Produced:** `IssueValidated`, `EvidenceAttached`, `DepartmentAssigned`, `TaskCreated`, `TaskCompleted`, `IssueResolved`, `SLAThresholdExceeded`.
* **Events Consumed:** `CitizenReportSubmitted`, `CitizenFeedbackSubmitted`, `RecommendationGenerated`, `EvidenceClustered`, `PluginResponseReturned`, `PluginExecutionFailed`, `SchemeConfigured`, `RoleAssigned`.
* **Failure Behaviour:** Workflow state updates execute in database transactions. If a crash occurs, execution rolls back to the last persistent checkpoint, and the engine re-processes the event from the queue.
* **Scaling Strategy:** Partitioned horizontally based on `issue_id`. Each node handles a specific partition group to avoid resource contention.

### 2.5. AI Orchestrator
* **Responsibility:** Executes unstructured semantic processing. Classifies report categories, extracts locations from text/audio, groups similar reports into structural clusters, checks submission guardrails, and drafts suggested replies.
* **Inputs:** Raw report texts, audio transcripts, media assets.
* **Outputs:** Classification recommendations, routing models, duplicate cluster mappings, anomaly markers.
* **Dependencies:** Knowledge Service (retrieving grounding graphs), Object Storage (accessing raw attachments).
* **Owned Domain:** AI Grounding, Recommendations, Similarity Clusters.
* **Events Produced:** `RecommendationGenerated`, `EvidenceClustered`, `AnomalyDetected`.
* **Events Consumed:** `CitizenReportSubmitted`, `IssueValidated`, `EvidenceAttached`.
* **Failure Behaviour:** Advisory design principle. If the AI Orchestrator fails, the Workflow Engine defaults to standard manual triage queues or basic lookup routing. System execution does not stall.
* **Scaling Strategy:** Inference nodes are scaled horizontally. Computationally expensive model queries are offloaded to dedicated GPU-backed workers or external model API endpoints.

### 2.6. Knowledge Service
* **Responsibility:** Manages the administrative Knowledge Graph. Structures regional boundaries, department hierarchies, policy rules, and scheme criteria. Integrates semantic vector indices for Graph-RAG queries.
* **Inputs:** Graph entity updates, path search terms, vector query vectors.
* **Outputs:** Structured contexts, policy definitions, path traversals.
* **Dependencies:** Knowledge Graph database.
* **Owned Domain:** Knowledge Graph Nodes, Ward Boundaries, Scheme Policies.
* **Events Produced:** None.
* **Events Consumed:** `IssueValidated`, `EvidenceAttached`, `DepartmentAssigned`, `IssueResolved`, `SchemeConfigured`.
* **Failure Behaviour:** Read-heavy. Employs read-replicas. If the master graph database fails, read operations (including AI grounding lookups) continue via replicas, while write updates are buffered and retried.
* **Scaling Strategy:** Scaled by deploying multiple read-replicas. Graph mutations are directed through a single transactional writer node.

### 2.7. Notification Service
* **Responsibility:** Coordinates outbound citizen and administrator communications. Hydrates message templates, manages channel selection (WhatsApp, SMS, Email), and ensures delivery confirmation logs.
* **Inputs:** Notification templates, target parameters, contact metadata.
* **Outputs:** Hydrated message texts, gateway payloads.
* **Dependencies:** External SMS/Email/WhatsApp communication gateways.
* **Owned Domain:** Message Templates, Dispatch Logs.
* **Events Produced:** `DispatchSucceeded`, `DispatchFailed`.
* **Events Consumed:** `AlertEnqueued`, `CitizenOptedOut`.
* **Failure Behaviour:** If an external gateway fails (e.g., SMS provider outage), the service attempts delivery on alternative channels (e.g., WhatsApp) or queues the event for a backoff-retry loop.
* **Scaling Strategy:** Scaled horizontally. Workloads are sharded by recipient ID to prevent message ordering violations.

### 2.8. Plugin Runtime
* **Responsibility:** Runs third-party plugins in isolated sandboxes. Manages dynamic loading, passes event context, limits CPU/Memory resources, and captures execution metrics.
* **Inputs:** Hook configuration files, context mapping payloads.
* **Outputs:** Execution data returns, error logs, trace metrics.
* **Dependencies:** Object Storage (downloading packaged plugin modules).
* **Owned Domain:** Sandbox Registrations, Hook Interfaces.
* **Events Produced:** `PluginResponseReturned`, `PluginExecutionFailed`.
* **Events Consumed:** `HookTriggered`.
* **Failure Behaviour:** If a plugin crashes, throws an unhandled exception, or exceeds limits, the Runtime terminates the specific sandbox, logs the stack trace, and publishes `PluginExecutionFailed` to prompt Workflow Engine defaults. Core platform memory remains isolated.
* **Scaling Strategy:** Scale execution worker pools horizontally based on active hook traffic.

### 2.9. Audit Service
* **Responsibility:** Creates cryptographically secured, immutable audit entries for administrative actions, data exports, and configuration changes.
* **Inputs:** Access context parameters, audit entries.
* **Outputs:** Cryptographic hashes, compliance reports.
* **Dependencies:** Write-Once-Read-Many (WORM) storage.
* **Owned Domain:** Access Logs, Configuration overrides.
* **Events Produced:** `AccessLogGenerated`.
* **Events Consumed:** `SchemaChanged`, `AccessLogGenerated` (archiving self), `SystemConfigOverridden`.
* **Failure Behaviour:** Fail-secure. If the Audit Service cannot persist logs (due to storage failures), the API Gateway blocks all administrative mutations until logging integrity is restored.
* **Scaling Strategy:** Optimised for high-speed writes. Sharded by actor context ID.

### 2.10. Analytics Service
* **Responsibility:** Aggregates metrics, checks SLA thresholds, compiles performance analytics, and updates administrative data dashboards.
* **Inputs:** Multi-service database logs, analytical query metrics.
* **Outputs:** Metric aggregates, performance reports, prediction metrics.
* **Dependencies:** Read-replicas of operational and graph databases.
* **Owned Domain:** Performance Metrics, Outcome Logs.
* **Events Produced:** None.
* **Events Consumed:** `CitizenFeedbackSubmitted`, `DepartmentAssigned`, `TaskCompleted`, `IssueResolved`, `SLAThresholdExceeded`, `DispatchSucceeded`.
* **Failure Behaviour:** Completely isolated from operational workflows. If down, dashboard data is cached and stale, but no workflow logic is halted.
* **Scaling Strategy:** Uses streaming aggregates. Scales out analytics ingestion nodes separately from query API instances.

### 2.11. Administration Service
* **Responsibility:** Handles administrative configurations: registering schemes, setting organizational boundaries, adjusting SLA allocations, and defining system configurations.
* **Inputs:** Settings updates, policy forms.
* **Outputs:** Scheme configuration definitions.
* **Dependencies:** Relational database storage.
* **Owned Domain:** System Properties, Scheme settings.
* **Events Produced:** `SchemeConfigured`, `SystemConfigOverridden`.
* **Events Consumed:** None.
* **Failure Behaviour:** Configurations are versioned in database tables. If an update fails, changes are rejected, and the system rolls back to the last active configuration configuration snapshot.
* **Scaling Strategy:** Low transactional volume. Deployed in a simple two-node High Availability cluster.

### 2.12. Configuration Service
* **Responsibility:** Central repository for system-wide environment variables, secrets management, and real-time feature flag variables.
* **Inputs:** Bootstrapping configuration queries, toggle configurations.
* **Outputs:** Config definitions, feature toggles.
* **Dependencies:** Distributed consensus engine.
* **Owned Domain:** Environment Settings, Feature Flags.
* **Events Produced:** None.
* **Events Consumed:** `SystemConfigOverridden` (triggers configuration cache refresh).
* **Failure Behaviour:** Read configurations are cached locally in memory by each service container during bootstrapping. If the Configuration Service goes down, services run on local caches, but configurations cannot be updated.
* **Scaling Strategy:** Read-heavy, heavily cached, using transactional consensus nodes.

### 2.13. Object Storage
* **Responsibility:** Manages raw unstructured binary objects (e.g. photos, voice reports, PDF guidelines, plugin execution packages).
* **Inputs:** Binary upload streams, key query strings.
* **Outputs:** Static URLs, byte download streams.
* **Dependencies:** None.
* **Owned Domain:** Unstructured Assets.
* **Events Produced:** `EvidenceAttached` (via context wrappers).
* **Events Consumed:** `CitizenOptedOut` (commands deletion of files containing citizen data).
* **Failure Behaviour:** Mirroring. If a storage node or zone fails, requests are served from redundant read-replicated zones.
* **Scaling Strategy:** Decoupled. Storage scales out horizontally. Static media requests are offloaded to edge cache networks.

### 2.14. Search Service
* **Responsibility:** Ingests document summaries and index markers, providing high-speed, full-text semantic searching capabilities for operators.
* **Inputs:** Structured documents, text queries.
* **Outputs:** Matches, facets.
* **Dependencies:** Operational database (for initial indexing).
* **Owned Domain:** Search Index data.
* **Events Produced:** None.
* **Events Consumed:** `IssueValidated`, `EvidenceAttached`, `IssueResolved`.
* **Failure Behaviour:** If down, portal search boxes fail, but the Workflow Engine and Citizen Intake continue to execute. Fallback directs basic queries to the operational database.
* **Scaling Strategy:** Search indexes are sharded and replicated horizontally across independent nodes.

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
| **Notification Service**| Alert Dispatch | `EVT-402`, `EVT-403` | `EVT-401`, `EVT-103` | `ADR-0001` | `ARCH-003`, `ARCH-005` |
| **Plugin Runtime** | Sandboxing | `EVT-702`, `EVT-703` | `EVT-701` | `ADR-0002` | `ARCH-003`, `ARCH-005` |
| **Audit Service** | System Security | `EVT-602` | `EVT-601`, `EVT-602`, `EVT-603` | `ADR-0001` | `ARCH-003`, `ARCH-005` |
| **Analytics Service** | Performance | None | `EVT-102`, `EVT-203`, `EVT-205`, `EVT-206`, `EVT-402`, `EVT-503` | `ADR-0001` | `ARCH-003`, `ARCH-005` |
| **Admin Service** | Configuration | `EVT-501`, `EVT-603` | None | None | `ARCH-003`, `ARCH-005` |
| **Config Service** | Feature Flags | None | `EVT-603` | None | `ARCH-003` |
| **Object Storage** | Blob Storage | `EVT-202` | `EVT-103` | None | `ARCH-003` |
| **Search Service** | Search Indices | None | `EVT-201`, `EVT-202`, `EVT-206` | None | `ARCH-003` |

---

## 4. Design Validation Checklist

Before freezing any downstream implementation design, verify the component layout against these checks:

* [ ] **Bounded Isolation:** Does the component interact only through defined events or REST/gRPC gateways, avoiding shared database writes?
* [ ] **Stateless Target:** Are components designed as stateless services (excluding specific database adapters) to allow simple horizontal scaling?
* [ ] **Graceful Degradation:** If dependent services (such as AI Orchestrator or Notification Service) are down, can the component complete its core processing?
* [ ] **Audit Interception:** Are all write modifications or sensitive PII reads routed to trigger corresponding Audit events?
* [ ] **Traceability Confirmed:** Are all event consumer definitions in the component registered in the parent Event Catalog (`ARCH-005`)?
* [ ] **Local Cache Strategy:** Do components cache configuration parameters locally to maintain survival capabilities during configuration outages?
* [ ] **Outbox Integrated:** Do state-mutating components implement transactional outbox patterns to guarantee at-least-once event delivery?
* [ ] **Crypto-Shredding Compliance:** Can storage-heavy components (Object Storage, Relational DBs) isolate and destroy records mapped to an opted-out `citizen_id`?
