---
spec_id: "HELIX-ARCH-002"
status: "Draft"
version: "0.1.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-05"
dependencies: ["HELIX-ARCH-001"]
related_adr: []
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Draft"
---

# HELIX-ARCH-002: C4 Level 1 Context Diagram

This specification defines the C4 Level 1 System Context Diagram for the Helix Governance Operating System. It visualizes the system's runtime boundaries, external systems, and logical user interactions.

---

## 1. C4 Context Diagram (Mermaid)

This diagram renders natively inside the documentation portal. It models the Helix boundary and all direct actors and external integrations.

```mermaid
flowchart TB
    %% Styling Definitions
    classDef actor fill:#1261A0,stroke:#0A4275,color:#FFFFFF,stroke-width:2px;
    classDef core fill:#D44000,stroke:#A30000,color:#FFFFFF,stroke-width:2px;
    classDef ext fill:#5C6B73,stroke:#3E4A50,color:#FFFFFF,stroke-width:2px;
    classDef boundary stroke:#333,stroke-dasharray: 5 5,fill:none;

    %% Actors
    Cit[Citizen<br/><i>Person</i>] ::: actor
    Rep[Representative<br/><i>Person</i>] ::: actor
    Off[Officer<br/><i>Person</i>] ::: actor
    Fld[Field Engineer<br/><i>Person</i>] ::: actor
    DAd[District Administrator<br/><i>Person</i>] ::: actor
    PAd[Platform Administrator<br/><i>Person</i>] ::: actor
    Dev[Developer<br/><i>Person</i>] ::: actor

    %% Ingestion/Notification Intermediaries
    WA[WhatsApp API<br/><i>System</i>] ::: ext
    SMS[SMS Gateway<br/><i>System</i>] ::: ext
    EM[Email Gateway<br/><i>System</i>] ::: ext

    %% Government & Knowledge Integrations
    GIS[Gov GIS & Asset Registry<br/><i>System</i>] ::: ext
    OD[Gov Open Data Portal<br/><i>System</i>] ::: ext
    Cen[Census Demographics<br/><i>System</i>] ::: ext
    Wth[Weather API<br/><i>System</i>] ::: ext
    Sat[Satellite Imagery<br/><i>System</i>] ::: ext
    Pol[Policy Circular Repo<br/><i>System</i>] ::: ext
    Ntf[Push Notification Provider<br/><i>System</i>] ::: ext

    %% Helix Core System Boundary
    subgraph HelixBoundary [Helix System Boundary]
        HOS[Helix Governance OS<br/><i>Core Operating System</i>] ::: core
    end

    %% Citizen Interactions
    Cit -->|Submits reports to| WA
    Cit -->|Submits simple text to| SMS
    Cit -->|Submits circular forms to| EM

    %% Channel Intermediaries to Core
    WA <-->|Forwards inputs / Status alerts| HOS
    SMS <-->|Forwards text / SMS updates| HOS
    EM <-->|Mails documents / Digest reports| HOS

    %% Human Console Interactions
    Rep <-->|Views dashboards & Audits outcomes| HOS
    Off <-->|Triages, views drafts & signs decisions| HOS
    Fld <-->|Pulls task lists & uploads repair photos| HOS
    DAd -->|Configures local priority parameters| HOS
    PAd -->|Configures deployments & secrets| HOS
    Dev -->|Builds custom plugins & extends APIs| HOS

    %% Core to External Queries
    HOS -->|Queries municipal budget limits| OD
    HOS -->|Validates asset locations| GIS
    HOS -->|Validates voter contexts| Cen
    HOS -->|Retrieves climate status metrics| Wth
    HOS -->|Verifies site layouts & landscapes| Sat
    HOS -->|Scrapes policy regulations for RAG| Pol
    HOS -->|Triggers device push notifications| Ntf

    %% Apply graph styles
    style HelixBoundary fill:#FFF5F0,stroke:#D44000,stroke-width:2px;
```

---

## 2. C4 Context Diagram (PlantUML)

This version-controlled C4-PlantUML code block serves as our industry-standard documentation source for generating PDF briefs, presentation slides, or printing architectural blueprints.

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

title System Context Diagram for Helix Governance Operating System

Person(citizen, "Citizen", "A community member submitting local issues or applying for welfare benefits.")
Person(representative, "Representative", "Elected political leader (MP/MLA) tracking constituency progress.")
Person(officer, "Officer", "Administrative officer reviewing reports, triaging issues, and signing decisions.")
Person(field_engineer, "Field Engineer", "Field technician resolving repair tasks and uploading evidence.")
Person(district_admin, "District Administrator", "Office manager maintaining policy documents and task priorities.")
Person(platform_admin, "Platform Administrator", "System operator configuring deployments, secrets, and telemetry.")
Person(developer, "Developer", "Software engineer building custom plugins and system integration extensions.")

System(helix, "Helix", "Governance Operating System. Ingests unstructured inputs, grounds policy circulars, tracks workflow state, and acts as decision support.")

System_Ext(whatsapp, "WhatsApp API", "External messaging connector forwarding citizen queries.")
System_Ext(sms, "SMS Gateway", "External carrier gateway for fallback ingestion and text alerts.")
System_Ext(email, "Email Gateway", "SMTP circular ingest and officer digest mail server.")
System_Ext(opendata, "Gov Open Data", "Public database supplying municipal budget and project records.")
System_Ext(gis, "Gov GIS & Asset Registry", "Government directory listing physical public assets (pipes, roads).")
System_Ext(census, "Census Database", "Official demographics directory for verification of voter context.")
System_Ext(weather, "Weather API", "Climate service supplying data for issue ranking.")
System_Ext(satellite, "Satellite Services", "Physical geography imagery database for site validation.")
System_Ext(notifications, "Push Provider", "Third-party notification system (Firebase, APNS) for mobile apps.")
System_Ext(policy_repo, "Policy Circulars Database", "Gazette circular files supplying grounding facts for recommendation RAG.")

Rel(citizen, whatsapp, "Sends text, audio, and photo reports to")
Rel(citizen, sms, "Submits simple alerts to")
Rel(citizen, email, "Mails circular applications to")

Rel(whatsapp, helix, "Forwards citizen messages to", "JSON/HTTPS")
Rel(sms, helix, "Forwards text alerts to", "HTTPS")
Rel(email, helix, "Forwards mail documents to", "SMTP/HTTPS")

Rel(helix, whatsapp, "Dispatches status alerts back to", "HTTPS")
Rel(helix, sms, "Dispatches verification codes to", "HTTPS")
Rel(helix, email, "Dispatches digest reports to", "HTTPS")

Rel_R(representative, helix, "Monitors dashboards and audits outcomes via", "Web/HTTPS")
Rel_L(officer, helix, "Triages issues, reviews drafts, and signs off via", "Web/HTTPS")
Rel_D(field_engineer, helix, "Updates task orders and posts completion photos to", "HTTPS")
Rel_U(district_admin, helix, "Uploads policy documents and priority files to", "HTTPS")
Rel_U(platform_admin, helix, "Configures environment, secrets, and monitors telemetry on", "HTTPS")
Rel_U(developer, helix, "Implements plugins and consumes API contracts of", "Plugin SDK / HTTP")

Rel(helix, opendata, "Queries budget limits and projects from", "JSON/HTTPS")
Rel(helix, gis, "Verifies asset details and location records from", "JSON/HTTPS")
Rel(helix, census, "Validates registration and demographic files in", "JSON/HTTPS")
Rel(helix, weather, "Retrieves weather conditions from", "JSON/HTTPS")
Rel(helix, satellite, "Loads site layouts and image maps from", "JSON/HTTPS")
Rel(helix, notifications, "Requests push notifications from", "HTTPS")
Rel(helix, policy_repo, "Scrapes circular text updates from", "HTTPS")

@enduml
```

---

## 3. Relationship Details

This section outlines the business intent, protocols, and payloads of the context relationships:

### 3.1. Human Interactions with Helix
* **Citizen $\rightarrow$ Ingest Intermediaries:** Citizens transmit reports asynchronously. Protocols are channel-dependent (WhatsApp API, GSM SMS, SMTP mail). No structural Helix authorization credentials are required at this stage.
* **Representative $\leftrightarrow$ Helix:** Read-only access to constituency performance metrics and outcomes. Access requires authenticated identity tokens over HTTPS.
* **Officer $\leftrightarrow$ Helix:** Full read-write triage workstation context. Officers approve AI drafts, sign decisions, and delegate task items. High-speed keyboard-driven events are processed over secure HTTPS websockets.
* **Field Engineer $\leftrightarrow$ Helix:** Updates field tasks from mobile interfaces. Sends repair verification data (geotagged images, operator notes) over HTTPS streams.
* **District Administrator $\rightarrow$ Helix:** Push parameters and settings. district admins write policy files, update officer routing directories, and modify local prioritizations via configuration files.
* **Platform Administrator $\leftrightarrow$ Helix:** Deploys software packages, provisions access keys, sets up environment configurations, and gathers performance telemetry.
* **Developer $\leftrightarrow$ Helix:** Builds plugin packages, checks API models, and implements external bindings via the Plugin SDK interface boundaries.

### 3.2. Helix Core to External Integrations
* **Helix $\rightarrow$ Government GIS / Asset Registry:** Read-only query to match an issue's geo-coordinates against municipal asset databases. Checks if the target pipe, road, or utility is registered under government domain responsibility.
* **Helix $\rightarrow$ Policy Circular Repository:** Aggregates gazette records and regulatory texts. The scrapped files are parsed into vector segments to support the ground verification process.
* **Helix $\rightarrow$ Weather & Satellite Systems:** Imports data streams to calculate risk metrics. For example, satellite image scans provide proof of road erosion, while weather alerts flag flood-prone assets.
* **Helix $\rightarrow$ Census / Demographic Registries:** Validates citizen registration attributes to check if the applicant lives within the administrative boundaries required for a scheme.

---

## 4. Trust Boundary Explanations

Helix isolates platform components into three clear trust tiers:
* **The Public Ingestion Boundary:** WhatsApp, SMS, and Email systems belong to the Public Zone. Payload verification filters, input size limiters, and PII scanners run at this boundary to clean all incoming strings before they enter internal queues.
* **The Administrative Workstation Boundary:** The officer dashboard web consoles communicate across a secure Government LAN/WAN boundary. Sessions require Multi-Factor Authentication (MFA), and all transactions are cryptographically signed.
* **The Internal Operational Core:** Direct connection routes between services, databases, and message brokers are isolated within a private virtual network. No external IP route may reach these databases directly.

---

## 5. Architectural Assumptions
* **Availability of Intermediaries:** We assume the WhatsApp Business API, SMS Carrier networks, and SMTP mail servers are operational. Helix handles external outages by buffering citizen requests in local ingestion queue vaults.
* **Open Geospatial Coordinates:** We assume mapping services (e.g. OpenStreetMap) are accessible to convert citizen coordinate inputs into administrative wards and panchayat polygons.
* **Standardized Government Identity Tokens:** We assume the administrative client implements identity protocols (OAuth2, SAML, or Active Directory) to verify administrator credentials.

---

## 6. Architectural Constraints
* **PII Governance:** Under law-mandated citizen privacy criteria, sensitive identifier strings must be masked before text segments are passed to external AI model endpoints.
* **Low Network Latency Fallbacks:** In low-bandwidth areas (rural districts), Helix client portals must load simplified pages, disabling map layers and auto-draft pre-rendering while preserving basic keyboard workflows.
* **Read-Only Integration Rules:** Government asset databases and census files are accessed strictly as read-only systems. Helix must not modify external state directly.

---

## 7. Design Rationale
* **Mermaid & PlantUML Dual Specification:** We maintain both configurations to serve different needs. Mermaid renders directly in our browser-based documentation portal. PlantUML is kept as our version-controlled industry standard to generate PDF specifications, presentation slides, and formal architecture models.
* **Boundary Ingestion Decoupling:** Decoupling intake channels (WhatsApp/SMS) from core classification workflows prevents system outages. A sudden surge in WhatsApp messages will buffer inside the ingestion queue, protecting downstream classification microservices from overload.

---

## 8. Design Validation Checklist

* [ ] **Charter Alignment:** Directly matches the core principles defined in `HELIX-SPEC-000`.
* [ ] **Constitution Alignment:** Conforms to all Twelve Laws of the Helix Constitution.
* [ ] **C4 Standard Conformity:** Follows C4 C-Level mapping templates (Actors, Systems, Boundaries, Relationships).
* [ ] **Diagram Sync:** Mermaid and PlantUML models show identical actors, external systems, and relationship names.
* [ ] **Domain Vocabulary Sync:** All labels match the definitions in the frozen `HELIX-DOMAIN-001` (Citizen, Officer, Representative, Asset, Department, Location, Decision).
* [ ] **No Tech Specifications:** Avoids referencing databases, programming languages, and host platforms.
* [ ] **Checklist Compliance:** Ends with this validation gate.
