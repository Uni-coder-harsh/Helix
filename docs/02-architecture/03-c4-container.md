---
spec_id: "HELIX-ARCH-003"
status: "Frozen"
version: "1.0.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-06"
dependencies: ["HELIX-ARCH-002"]
related_adr: ["ADR-0001"]
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Frozen"
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
    subgraph FrontendBound ["Frontend Containers"]
        AP["Admin Portal (SPA)"]
        CP["Citizen Portal (SPA)"]
        MA["Mobile App (Mobile Client)"]
    end

    subgraph EdgeBound ["Edge Containers"]
        WAC["WhatsApp Connector (Service)"]
        SMC["SMS Connector (Service)"]
        EMC["Email Connector (Service)"]
    end

    subgraph PlatformBound ["Platform Containers"]
        GW["API Gateway (Service)"]
        ID["Identity Service (Service)"]
    end

    subgraph CoreBound ["Core Containers"]
        WE["Workflow Engine (Service)"]
        AO["AI Orchestrator (Service)"]
        PR["Plugin Runtime (Service)"]
        NE["Notification Engine (Service)"]
    end

    subgraph DataBound ["Data Store Containers"]
        ODB["Operational DB (Relational Database)"]
        KG["Knowledge Graph (Graph Database)"]
        OBJ["Object Storage (File Store)"]
    end

    subgraph AnalyticsBound ["Analytics Containers"]
        ANL["Analytics Platform (Processing Engine)"]
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
    WE -->|Propagates facts and checks history| KG
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

    %% Apply Style Classes
    class AP,CP,MA,WAC,SMC,EMC,GW,ID,WE,AO,PR,NE,ANL container;
    class ODB,KG,OBJ db;

    %% Apply graph styles
    style FrontendBound fill:#F8F9FA,stroke:#6C757D,stroke-width:2px;
    style EdgeBound fill:#F1F3F5,stroke:#495057,stroke-width:2px;
    style PlatformBound fill:#E9ECEF,stroke:#343A40,stroke-width:2px;
    style CoreBound fill:#FFE8CC,stroke:#FD7E14,stroke-width:2px;
    style DataBound fill:#E3FAF5,stroke:#0CA678,stroke-width:2px;
    style AnalyticsBound fill:#E8F5E9,stroke:#2B8A3E,stroke-width:2px;
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
}

System_Boundary(core, "Core Containers") {
    Container(workflow_eng, "Workflow Engine", "Stateful Service", "Manages lifecycle transitions of Issues, Tasks, Workflows, and Decisions.")
    Container(ai_orch, "AI Orchestrator", "Service", "Coordinates classification, policy semantic query retrieval, and drafting recommendations.")
    Container(plugin_rt, "Plugin Runtime", "Service Sandbox", "Loads and runs isolated regional bindings dynamically.")
    Container(notification_eng, "Notification Engine", "Service Queue", "Resolves channel routing rules and schedules notifications to citizens and officers.")
}

System_Boundary(data, "Data Store Containers") {
    ContainerDb(operational_db, "Operational Database", "Relational Database", "Stores persistent states for Issues, Tasks, Accounts, and Decisions.")
    ContainerDb(knowledge_graph, "Knowledge Graph", "Graph/Vector Database", "Maintains constituency mappings, assets, policy documents, and vector search embeddings.")
    Container(object_storage, "Object Storage", "File Storage", "Persists unstructured media uploads (citizen photos, official circular PDFs).")
}

System_Boundary(analytics, "Analytics Containers") {
    Container(analytics_platform, "Analytics Platform", "Processing Engine", "Compiles outcomes, timings, and metrics to report historical constituency trends.")
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
  * Submits transaction signatures for status transitions.
* **Interfaces:** Outgoing requests to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-002: Citizen Portal
* **Purpose:** Web-based report ingestion and progress tracking client for citizens.
* **Responsibilities:**
  * Captures issue text description and geolocation indicators.
  * Displays history status updates.
* **Interfaces:** Outgoing requests to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-003: Mobile App
* **Purpose:** On-site task coordination app for field engineers.
* **Responsibilities:**
  * Exposes task queue lists and location navigation targets.
  * Captures geotagged completion photos and status validations.
* **Interfaces:** Outgoing requests to the API Gateway.
* **Dependencies:** API Gateway.

---

### 3.2. Edge Containers

#### CON-004: WhatsApp Connector
* **Purpose:** Interface bridge for citizen interactions via WhatsApp.
* **Responsibilities:**
  * Listens to WhatsApp events, parsing incoming media payloads.
  * Dispatches scheduled alert templates to citizens.
* **Interfaces:** Ingress webhooks; egress requests to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-005: SMS Connector
* **Purpose:** Text network carrier gateway adapter.
* **Responsibilities:**
  * Parses simple text reports and forwards payload schemas.
  * Sends text notifications.
* **Interfaces:** Carrier callback handlers; egress HTTP to the API Gateway.
* **Dependencies:** API Gateway.

#### CON-006: Email Connector
* **Purpose:** Mail ingestion and digest distribution node.
* **Responsibilities:**
  * Parses circular attachments from incoming mail.
  * Distributes digest mail circular summaries to officers.
* **Interfaces:** Mail handlers; egress HTTP to the API Gateway.
* **Dependencies:** API Gateway.

---

### 3.3. Platform Containers

> [!NOTE]
> Operational infrastructure tooling (e.g. logging engines, tracing sinks, performance telemetry collection agents) is excluded from the application container schema. These concerns are managed inside `HELIX-ARCH-008: Deployment Architecture`.

#### CON-007: API Gateway
* **Purpose:** Unified gateway facade and routing proxy.
* **Responsibilities:**
  * Validates identity headers against the Identity Service.
  * Implements rate-limits and backpressure guards.
  * Routes traffic to core workflow engines and orchestrators.
* **Interfaces:** Ingress public endpoints; egress routing paths to internal containers.
* **Dependencies:** Identity Service, Workflow Engine, AI Orchestrator.

#### CON-008: Identity Service
* **Purpose:** Identity and directory store integration adapter.
* **Responsibilities:**
  * Resolves administrative login tokens.
  * Maps users to role and department directories.
* **Interfaces:** Core internal RPC lookup.
* **Dependencies:** None.

---

### 3.4. Core Containers

#### CON-009: Workflow Engine
* **Purpose:** Orchestration engine for Issue and Task state paths.
* **Responsibilities:**
  * Enforces state machine definitions.
  * Records signed approvals to transition issue states.
  * Emits event transaction records.
* **Interfaces:** Core internal service endpoints.
* **Dependencies:** Operational Database, Knowledge Graph, Plugin Runtime, Notification Engine.

#### CON-010: AI Orchestrator
* **Purpose:** Coordination logic for recommendation pipelines.
* **Responsibilities:**
  * Directs incoming messages to classification modules.
  * Fetches grounding facts from the Knowledge Graph.
  * Requests text generation from the Plugin Runtime.
* **Interfaces:** Core internal service endpoints.
* **Dependencies:** Knowledge Graph, Plugin Runtime.

#### CON-011: Plugin Runtime
* **Purpose:** Isolated execution sandbox for external plugin tasks.
* **Responsibilities:**
  * Loads external provider interfaces dynamically.
  * Executes model execution calls.
* **Interfaces:** Abstract plugin SDK loop interfaces.
* **Dependencies:** Object Storage.

#### CON-012: Notification Engine
* **Purpose:** Delivery scheduler for citizen and officer messages.
* **Responsibilities:**
  * Resolves user contact channel preferences.
  * Schedules alerts and manages retry parameters.
* **Interfaces:** Event listeners and queue handlers.
* **Dependencies:** WhatsApp Connector, SMS Connector, Email Connector.

---

### 3.5. Data Store Containers

#### CON-013: Operational Database
* **Purpose:** Structured storage for operational transactions.
* **Responsibilities:**
  * Guarantees ACID transactional compliance for Issues and Tasks.
* **Interfaces:** Database client query protocols.
* **Dependencies:** None.

#### CON-014: Knowledge Graph
* **Purpose:** Entity topology and policy vector semantic registry.
* **Responsibilities:**
  * Maintains constituency networks, assets, and policy regulations.
  * Provides vector search indexes.
* **Interfaces:** Database client query protocols.
* **Dependencies:** None.
* **Traceability:**
  > [!NOTE]
  > Future versions of the architecture may separate vector semantic indexing from the graph storage container.

#### CON-015: Object Storage
* **Purpose:** Blob file repository.
* **Responsibilities:**
  * Stores binary circular PDFs and upload verification images.
* **Interfaces:** Simple storage query endpoints.
* **Dependencies:** None.

---

### 3.6. Analytics Containers

#### CON-016: Analytics Platform
* **Purpose:** Analytical query and report processing engine.
* **Responsibilities:**
  * Extracts metrics from the Operational Database.
  * Aggregates outcome statistics from the Knowledge Graph.
  * Renders report queries indicating historical constituency performance patterns.
* **Interfaces:** Internal query client APIs.
* **Dependencies:** Operational Database, Knowledge Graph.

---

## 4. Architectural Assumptions
* **Gateway Decoupling:** We assume the API Gateway isolates the core services from any external-facing routing parameters.
* **State Decoupling:** We assume operational transactions (Operational DB) and context embeddings (Knowledge Graph) are kept in isolated, decoupled containers.
* **Trace Standard Integrity:** We assume all core containers carry distributed tracing context propagation headers across execution boundaries.

---

## 5. Architectural Constraints
* **PII Leakage Boundary:** The API Gateway and Ingestion Connectors must execute PII masking operations before routing payloads to core containers.
* **Permissive Licenses:** All core and platform containers must be constructed utilizing components that are free from copyleft license restrictions.
* **Isolation of Plugins:** The Plugin Runtime must sandbox third-party plugin executions to prevent memory or process failure cascades into the core engines.

---

## 6. Design Decisions
* **API Gateway Routing Pattern:** Integrating a single API Gateway protects internal services from direct public traffic, standardizes request sanitization, and centralizes rate-limiting guards.
* **Decoupled Analytics Container:** Separating analytical calculations from primary data repositories protects database performance from reporting query execution peaks.

---

## 7. Design Validation Checklist

* [ ] **Charter Alignment:** Directly matches the core principles defined in `HELIX-SPEC-000`.
* [ ] **Constitution Alignment:** Conforms to all Twelve Laws of the Helix Constitution.
* [ ] **C4 Level 2 Standards:** Identifies distinct container boundaries (Frontend, Edge, Platform, Core, Data, Analytics).
* [ ] **Diagram Sync:** Mermaid and PlantUML models display identical container definitions and relations.
* [ ] **UML and Markdown Sync:** Attributes listed in the text match definitions inside the visual schemas.
* [ ] **No Microservices Internal Detail:** Avoids discussing internal components, code classes, packages, or specific vendor technologies.
* [ ] **Checklist Compliance:** Ends with this validation gate.
