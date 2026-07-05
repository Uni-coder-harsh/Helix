---
spec_id: "HELIX-ARCH-003"
status: "Draft"
version: "0.1.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-05"
dependencies: ["HELIX-ARCH-002"]
related_adr: []
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Draft"
---

# HELIX-ARCH-003: C4 Level 2 Container Diagram

This specification defines the C4 Level 2 Container Diagram for Helix. It details the system's logical runtime units, their responsibilities, dependencies, interfaces, and persistence store divisions.

---

## 1. C4 Container Diagram (Mermaid)

This diagram shows the runtime containers composing Helix, grouped into functional boundaries:

```mermaid
flowchart TB
    %% Styling Definitions
    classDef container fill:#1261A0,stroke:#0A4275,color:#FFFFFF,stroke-width:2px;
    classDef db fill:#00758F,stroke:#004D5E,color:#FFFFFF,stroke-width:2px;
    classDef boundary stroke:#333,stroke-dasharray: 5 5,fill:none;

    %% Subgraphs for Logical Boundaries
    subgraph FrontendBound [Frontend Containers]
        AP["Admin Portal<br/><i>SPA</i>"] ::: container
        CP["Citizen Portal<br/><i>SPA</i>"] ::: container
        MA["Mobile App<br/><i>Mobile Client</i>"] ::: container
    end

    subgraph EdgeBound [Edge Containers]
        WAC["WhatsApp Connector<br/><i>Service</i>"] ::: container
        SMC["SMS Connector<br/><i>Service</i>"] ::: container
        EMC["Email Connector<br/><i>Service</i>"] ::: container
    end

    subgraph PlatformBound [Platform Containers]
        GW["API Gateway<br/><i>Service</i>"] ::: container
        ID["Identity Service<br/><i>Service</i>"] ::: container
        MON["Monitoring Service<br/><i>Service</i>"] ::: container
        LOG["Logging Service<br/><i>Service</i>"] ::: container
    end

    subgraph CoreBound [Core Containers]
        WE["Workflow Engine<br/><i>Service</i>"] ::: container
        AO["AI Orchestrator<br/><i>Service</i>"] ::: container
        PR["Plugin Runtime<br/><i>Service</i>"] ::: container
        NE["Notification Engine<br/><i>Service</i>"] ::: container
    end

    subgraph DataBound [Data Store Containers]
        ODB["Operational DB<br/><i>Relational Database</i>"] ::: db
        KG["Knowledge Graph<br/><i>Graph/Vector Store</i>"] ::: db
        OBJ["Object Storage<br/><i>File Store</i>"] ::: db
        ANL["Analytics Platform<br/><i>Data Warehouse</i>"] ::: db
    end

    %% Routing connections
    CP -->|Sends requests| GW
    AP -->|Sends requests| GW
    MA -->|Sends requests| GW
    WAC -->|Forwards raw reports| GW
    SMC -->|Forwards raw alerts| GW
    EMC -->|Forwards raw mail| GW

    %% Gateway to Platform / Core Routing
    GW -->|Authenticates credentials| ID
    GW -->|Routes operational events| WE
    GW -->|Routes query requests| AO

    %% Core Container Interactions
    WE -->|Reads / Writes state| ODB
    WE -->|Propagates facts & checks history| KG
    WE -->|Triggers custom step hooks| PR
    WE -->|Enqueues alerts| NE

    AO -->|Queries grounding policy circulars| KG
    AO -->|Invokes external model tasks| PR

    NE -->|Dispatches messages| WAC
    NE -->|Dispatches text alerts| SMC
    NE -->|Dispatches summary digests| EMC

    PR -->|Saves and loads images / documents| OBJ
    ANL -->|Reads metrics| ODB
    ANL -->|Aggregates performance outcomes| KG

    %% Apply graph styles
    style FrontendBound fill:#F8F9FA,stroke:#6C757D,stroke-width:2px;
    style EdgeBound fill:#F1F3F5,stroke:#495057,stroke-width:2px;
    style PlatformBound fill:#E9ECEF,stroke:#343A40,stroke-width:2px;
    style CoreBound fill:#FFE8CC,stroke:#FD7E14,stroke-width:2px;
    style DataBound fill:#E3FAF5,stroke:#0CA678,stroke-width:2px;
```

---

## 2. C4 Container Diagram (PlantUML)

This version-controlled model defines the C4 Container structure:

```plantuml
@startuml
' In production, vendor this library locally to avoid external build dependencies:
' !include C4_Container.puml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

title Container Diagram for Helix Governance Operating System

System_Boundary(frontend, "Frontend Containers") {
    Container(admin_portal, "Admin Portal", "SPA / HTML / JS", "Web console for officers to triage issues, edit responses, and sign decisions.")
    Container(citizen_portal, "Citizen Portal", "SPA / HTML / JS", "Web portal for citizens to submit reports and track status.")
    Container(mobile_app, "Mobile App", "Mobile App / JS", "Mobile client for field engineers to view task queues and upload repair photos.")
}

System_Boundary(edge, "Edge Containers") {
    Container(whatsapp_conn, "WhatsApp Connector", "Service", "Processes incoming WhatsApp payloads and forwards requests; handles status delivery.")
    Container(sms_conn, "SMS Connector", "Service", "Carrier client for backup intake texts and dispatching alerts.")
    Container(email_conn, "Email Connector", "Service", "Ingests circular files and sends summary mail reports.")
}

System_Boundary(platform, "Platform Services") {
    Container(api_gateway, "API Gateway", "Reverse Proxy / Service", "Single entry point for client channels; enforces routing, authentication, and rate limits.")
    Container(identity_svc, "Identity Service", "OAuth2 / Directory Service", "Authenticates administrators, officers, and engineers; validates role capabilities.")
    Container(monitoring_svc, "Monitoring Service", "Telemetry Service", "Gathers system performance metrics across containers.")
    Container(logging_svc, "Logging Service", "Telemetry Service", "Aggregates execution logs and traces.")
}

System_Boundary(core, "Core Containers") {
    Container(workflow_eng, "Workflow Engine", "Stateful Service", "Manages lifecycle transitions of Issues, Tasks, Workflows, and Decisions.")
    Container(ai_orch, "AI Orchestrator", "Service", "Coordinates classification, policy semantic query retrieval, and drafting recommendations.")
    Container(plugin_rt, "Plugin Runtime", "Service Sandbox", "Loads and runs isolated regional bindings and model connectors dynamically.")
    Container(notification_eng, "Notification Engine", "Service Queue", "Resolves channel routing rules and schedules notifications to citizens and officers.")
}

System_Boundary(data, "Data Store Containers") {
    ContainerDb(operational_db, "Operational Database", "Relational Database", "Stores persistent states for Issues, Tasks, Accounts, and Decisions.")
    ContainerDb(knowledge_graph, "Knowledge Graph", "Graph/Vector Database", "Maintains constituency mappings, assets, policy documents, and vector search embeddings.")
    Container(object_storage, "Object Storage", "File Storage", "Persists unstructured media uploads (citizen photos, official circular PDFs).")
    Container(analytics_platform, "Analytics Platform", "Data Warehouse", "Compiles outcomes, timings, and metrics to report historical constituency trends.")
}

Rel(citizen_portal, api_gateway, "Sends queries and reports to")
Rel(admin_portal, api_gateway, "Queries status and updates state via")
Rel(mobile_app, api_gateway, "Uploads repair evidence via")

Rel(whatsapp_conn, api_gateway, "Forwards parsed messages to")
Rel(sms_conn, api_gateway, "Forwards text alerts to")
Rel(email_conn, api_gateway, "Forwards files to")

Rel(api_gateway, identity_svc, "Validates client credentials via")
Rel(api_gateway, workflow_eng, "Dispatches operational actions to")
Rel(api_gateway, ai_orch, "Requests recommendations and drafts from")

Rel(workflow_eng, operational_db, "Reads and writes transactional state in")
Rel(workflow_eng, knowledge_graph, "Propagates entities and reads history from")
Rel(workflow_eng, plugin_rt, "Invokes customized state logic via")
Rel(workflow_eng, notification_eng, "Triggers notification dispatch requests to")

Rel(ai_orch, knowledge_graph, "Queries policy facts from")
Rel(ai_orch, plugin_rt, "Executes model calls via")

Rel(notification_eng, whatsapp_conn, "Routes notifications through")
Rel(notification_eng, sms_conn, "Routes text alerts through")
Rel(notification_eng, email_conn, "Routes reports through")

Rel(plugin_rt, object_storage, "Stores and retrieves media objects from")
Rel(analytics_platform, operational_db, "Extracts metrics from")
Rel(analytics_platform, knowledge_graph, "Correlates outcomes from")

@enduml
```

---

## 3. Container Definitions

### 3.1. Frontend Containers

#### CON-001: Admin Portal
* **Purpose:** Triage and verification interface for government officers and district administrators.
* **Responsibilities:**
  * Displays queue summaries and prioritized task lists.
  * Captures officer edits on AI recommendation response drafts.
  * Submits cryptographic transaction signatures for status transitions.
* **Interfaces:** Outgoing HTTP JSON requests to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-002: Citizen Portal
* **Purpose:** Web-based report ingestion and progress tracking client for citizens.
* **Responsibilities:**
  * Captures issue text description and geolocation indicators.
  * Displays history status updates.
* **Interfaces:** Outgoing HTTP JSON requests to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-003: Mobile App
* **Purpose:** On-site task coordination app for field engineers.
* **Responsibilities:**
  * Exposes task queue lists and location navigation targets.
  * Captures geotagged completion photos and status validations.
* **Interfaces:** Outgoing HTTP JSON requests to the API Gateway.
* **Dependencies:** API Gateway.

---

### 3.2. Edge Containers

#### CON-004: WhatsApp Connector
* **Purpose:** Interface bridge for citizen interactions via WhatsApp.
* **Responsibilities:**
  * Listens to WhatsApp webhook events, parsing incoming media payloads.
  * Dispatches scheduled alert templates to citizens.
* **Interfaces:** Ingress HTTP webhooks; egress HTTP JSON requests to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-005: SMS Connector
* **Purpose:** Text network carrier gateway adapter.
* **Responsibilities:**
  * Parses simple text reports and forwards payload schemas.
  * Sends text notifications.
* **Interfaces:** HTTP callback handlers; egress HTTP to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-006: Email Connector
* **Purpose:** SMTP mail ingestion and digest distribution node.
* **Responsibilities:**
  * Parses circular attachments from incoming mail.
  * Distributes digest mail circular summaries to officers.
* **Interfaces:** SMTP handlers; egress HTTP to the API Gateway.
* **Dependencies:** API Gateway.

---

### 3.3. Platform Containers

#### CON-007: API Gateway
* **Purpose:** Unified gateway facade and routing proxy.
* **Responsibilities:**
  * Validates identity headers against the Identity Service.
  * Implements rate-limits and backpressure guards.
  * Routes traffic to core workflow engines and orchestrators.
* **Interfaces:** Ingress HTTPS endpoint; egress routing paths to internal containers.
* **Dependencies:** Identity Service, Workflow Engine, AI Orchestrator.

#### CON-008: Identity Service
* **Purpose:** Identity and directory store integration adapter.
* **Responsibilities:**
  * Resolves administrative login tokens.
  * Maps users to role and department directories.
* **Interfaces:** Core internal RPC lookup.
* **Dependencies:** None.

#### CON-009: Monitoring Service
* **Purpose:** Operational metrics collector.
* **Responsibilities:**
  * Aggregates CPU, memory, and performance metrics across containers.
* **Interfaces:** Pull metrics scraping endpoints.
* **Dependencies:** Core Services.

#### CON-010: Logging Service
* **Purpose:** Aggregated logging and trace sink.
* **Responsibilities:**
  * Ingests trace logs to capture distributed transaction context paths.
* **Interfaces:** Log capture streams.
* **Dependencies:** Core Services.

---

### 3.4. Core Containers

#### CON-011: Workflow Engine
* **Purpose:** Orchestration engine for Issue and Task state paths.
* **Responsibilities:**
  * Enforces state machine definitions.
  * Records signed approvals to transition issue states.
  * Emits event transaction records.
* **Interfaces:** Core internal REST/gRPC endpoints.
* **Dependencies:** Operational Database, Knowledge Graph, Plugin Runtime, Notification Engine.

#### CON-012: AI Orchestrator
* **Purpose:** Coordination logic for recommendation pipelines.
* **Responsibilities:**
  * Directs incoming messages to classification modules.
  * Fetches grounding facts from the Knowledge Graph.
  * Requests text generation from the Plugin Runtime.
* **Interfaces:** Core internal REST/gRPC endpoints.
* **Dependencies:** Knowledge Graph, Plugin Runtime.

#### CON-013: Plugin Runtime
* **Purpose:** Isolated execution sandbox for external plugin tasks.
* **Responsibilities:**
  * Loads external provider interfaces dynamically.
  * Executes out-of-process model execution calls.
* **Interfaces:** Abstract plugin SDK loop interfaces.
* **Dependencies:** Object Storage.

#### CON-014: Notification Engine
* **Purpose:** Delivery scheduler for citizen and officer messages.
* **Responsibilities:**
  * Resolves user contact channel preferences.
  * Schedules alerts and manages retry parameters.
* **Interfaces:** Event listeners and queue handlers.
* **Dependencies:** WhatsApp Connector, SMS Connector, Email Connector.

---

### 3.5. Data Store Containers

#### CON-015: Operational Database
* **Purpose:** Structured storage for operational transactions.
* **Responsibilities:**
  * Guarantees ACID transactional compliance for Issues and Tasks.
* **Interfaces:** Database client query protocols.
* **Dependencies:** None.

#### CON-016: Knowledge Graph
* **Purpose:** Entity topology and policy vector semantic registry.
* **Responsibilities:**
  * Stores constituency networks, assets, and policy regulations.
  * Provides vector search indexes.
* **Interfaces:** Database client query protocols.
* **Dependencies:** None.

#### CON-017: Object Storage
* **Purpose:** Blob file repository.
* **Responsibilities:**
  * Stores binary circular PDFs and upload verification images.
* **Interfaces:** Simple storage query endpoints.
* **Dependencies:** None.

#### CON-018: Analytics Platform
* **Purpose:** Aggregation warehouse for outcome statistics.
* **Responsibilities:**
  * Compiles metrics to calculate historical constituency performance patterns.
* **Interfaces:** SQL/Query data views.
* **Dependencies:** Operational Database, Knowledge Graph.

---

## 4. Architectural Assumptions
* **Gateway Decoupling:** We assume the API Gateway isolates the core services from any external-facing routing parameters.
* **State Decoupling:** We assume operational transactions (Operational DB) and context embeddings (Knowledge Graph) are kept in isolated, decoupled containers.
* **Trace Standard Integrity:** We assume all core containers carry distributed tracing context propagation headers across execution boundaries.

---

## 5. Architectural Constraints
* **PII Leakage Boundary:** The API Gateway and Ingestion Connectors must execute PII masking operations before routing text payloads to core containers.
* **Permissive Licenses:** All core and platform containers must be constructed utilizing components that are free from copyleft license restrictions.
* **Isolation of Plugins:** The Plugin Runtime must sandbox third-party plugin executions to prevent memory or process failure cascades into the core engines.

---

## 6. Design Decisions
* **API Gateway Routing Pattern:** Integrating a single API Gateway protects internal services from direct public traffic, standardizes request sanitization, and centralizes rate-limiting guards.
* **decoupled Analytics Store:** Separating the Analytics database from the primary Operational database prevents reporting queries from degrading transactional workflow execution performance.

---

## 7. Design Validation Checklist

* [ ] **Charter Alignment:** Directly matches the core principles defined in `HELIX-SPEC-000`.
* [ ] **Constitution Alignment:** Conforms to all Twelve Laws of the Helix Constitution.
* [ ] **C4 Level 2 Standards:** Identifies distinct container boundaries (Frontend, Edge, Platform, Core, Data).
* [ ] **Diagram Sync:** Mermaid and PlantUML models display identical container definitions and relations.
* [ ] **UML & Markdown Sync:** Attributes listed in the text match definitions inside the visual schemas.
* [ ] **No Microservices Internal Detail:** Avoids discussing internal components, code classes, packages, or specific vendor technologies.
* [ ] **Checklist Compliance:** Ends with this validation gate.
