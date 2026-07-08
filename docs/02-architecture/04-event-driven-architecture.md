---
spec_id: "HELIX-ARCH-004"
status: "Frozen"
version: "1.0.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-06"
dependencies: ["HELIX-ARCH-000", "HELIX-DOMAIN-001"]
related_adr: ["ADR-0001"]
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Frozen"
---

# HELIX-ARCH-004: Event-Driven Architecture

This document defines the event-driven philosophy, core architectural principles, and lifecycle patterns that serve as the backbone for the Helix Governance Operating System.

---

## 1. Executive Summary

Helix is a distributed, extensible operating system designed to manage public governance workflows at societal scale. Because governance relies on trust, compliance, and multi-party oversight, the system's foundational communication mechanism must be immutable, highly auditable, and decoupled.

This specification establishes the **Helix Event-Driven Architecture (EDA)**. Helix treats all domain transitions—from a citizen reporting an issue on WhatsApp to an administrative officer approving a budget assignment—as first-class, immutable events. By decoupling event producers from consumers, Helix guarantees scalability, operational resilience, and the plug-and-play integration of external tools, AI orchestrators, and community-driven extensions.

---

## 2. Why Event-Driven Architecture

Traditional request-response (synchronous) architectures are ill-suited for governance systems due to tight coupling, poor fault tolerance, and lack of auditability. Helix adopts an event-driven architecture for the following key reasons:

```
[Citizen Input] ──► (WhatsApp Connector)
                           │
                           ▼  [IssueCreated]
               ┌───────────────────────┐
               │    Helix Event Bus    │
               └───────────┬───────────┘
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     (Workflow Engine) (Analytics) (Audit & Compliance)
```

1. **Temporal and Spatial Decoupling:** In public governance, workflows do not happen in real time. A citizen's report may wait hours for validation, days for routing, and weeks for completion. Decoupling ensures that if one service (e.g., the AI Orchestrator) is temporarily unavailable, the rest of the ingestion and processing flow remains operational.
2. **Immutable Audit Trails:** Democracy requires accountability. By capturing every state change as an immutable event, Helix provides a built-in historical ledger. We do not just store the *current* state of an issue; we store the entire sequence of events that led to that state.
3. **Extensibility via Plugins:** External departments, non-governmental organizations, and civic-tech groups must be able to hook into Helix without altering its core. An event-driven model allows plugins to subscribe to specific events (e.g., `DecisionApproved`) and act on them independently.
4. **Resilient AI and Human-in-the-Loop Integration:** AI recommendation generation and human reviews are inherently asynchronous and vary in execution speed. Events allow smooth transitions between automated processing and manual oversight without blocking active system threads.

---

## 3. Event Design Principles

All events in Helix must adhere to the following four structural principles:

* **Immutability:** Once an event is published to the event stream, it cannot be altered, deleted, or recalled. Corrective actions must be represented by new, subsequent events.
* **Singularity of Fact:** Each event represents a single, distinct occurrence in the past tense (e.g., `EvidenceAttached`, not `AttachEvidenceAndNotify`).
* **Self-Containment (State-Carrying):** Helix uses the **Event-Carried State Transfer** pattern. Events must carry sufficient context (e.g., identifiers, status transitions, key metadata) to allow consumers to perform their logical duties without needing to call back to the producer for details.
* **Strict Contract Compliance:** Every event payload must adhere to a defined schema version. Unstructured or malformed payloads are rejected at the ingestion boundary.

---

## 4. Event Lifecycle

The lifecycle of a Helix event consists of five logical phases, ensuring secure and predictable propagation across the platform:

```
[Producer] ──► [Schema Validation] ──► [Ingestion & Ordering] ──► [Routing] ──► [Consumer Processing]
```

1. **Schema Validation:** The producer constructs the event. Prior to publication, the event payload is validated against the active schema version registered in the Event Catalog.
2. **Ingestion & Ordering:** The event is written to the immutable event log. During ingestion, the platform assigns a global timestamp, a unique event ID, and an ordering key (e.g., `issue_id`) to ensure sequential consistency.
3. **Routing:** The event bus routes the event to all active channels and subscription groups that have registered an interest.
4. **Consumer Processing:** Subscribed consumers read the event asynchronously. Consumers process the event within their own transaction boundaries, updating their local state.
5. **Auditing & Archival:** The event is permanently preserved in the cold storage event store for compliance, compliance auditing, and future replay capability.

---

## 5. Event Producers

An **Event Producer** is any logical component, connector, or service that detects a state change or completes a task and publishes a corresponding event.

* **Responsibility:** Producers are solely responsible for compiling the event payload, ensuring payload schema compliance, and providing the correct ordering key.
* **Decoupling:** Producers must have no knowledge of which services or plugins consume their events. They must never assume that an event will trigger an immediate synchronous reaction.
* **Outbox Pattern:** To guarantee that local database updates and event publications are atomic, producers should utilize transactional outbox patterns, preventing dual-write failures. The Outbox Pattern is a recommended implementation strategy, not an architectural requirement. Alternative mechanisms that provide equivalent transactional guarantees are acceptable.

---

## 6. Event Consumers

An **Event Consumer** is any service, database indexer, notification sender, or plugin that subscribes to one or more event streams to perform downstream logic.

* **Subscription Isolation:** Consumers maintain their own read offsets. If a consumer crashes, it resumes reading from its last acknowledged position upon recovery.
* **Parallelism:** Consumers can scale horizontally by forming consumer groups. The event bus distributes events across group instances using the event's ordering key, ensuring that events with the same key are processed by a single consumer instance in order.
* **Backpressure Handling:** Consumers must control their own consumption rate. If downstream databases or external services slow down, the consumer slows its pull rate without impacting the event log or other consumers.

---

## 7. Event Categories

Helix divides its domain events into seven functional categories. Below are concrete examples of events in each category:

### 7.1. Citizen Events
* `CitizenReportSubmitted`: Triggered when a citizen uploads a report (text, audio, image) via WhatsApp, SMS, or the Citizen Portal.
* `CitizenFeedbackReceived`: Triggered when a citizen rates a completed resolution.
* `CitizenOptedOut`: Triggered when a user requests deletion of contact data or withdraws consent.

### 7.2. Workflow Events
* `IssueValidated`: Generated when a raw submission is validated as a legitimate civic issue.
* `EvidenceAttached`: Generated when photos, geo-locations, or documents are appended to an active issue.
* `DepartmentAssigned`: Triggered when a workflow transitions ownership to a municipal department.
* `TaskCompleted`: Generated when field agents log that physical work is finished.

### 7.3. AI Events
* `RecommendationGenerated`: Published when the AI Orchestrator suggests a routing target or resolution plan.
* `EvidenceClustered`: Triggered when machine learning groups multiple individual reports into a single systemic problem.
* `AnomalyDetected`: Published when AI validation flags potential fraudulent activity or policy contradictions.

### 7.4. Notification Events
* `AlertEnqueued`: Generated when a notification is queued for delivery.
* `DispatchSucceeded`: Triggered when an SMS, WhatsApp message, or Email is successfully sent.
* `NotificationFailed`: Published if a delivery channel fails (e.g., invalid phone number).

### 7.5. Administration Events
* `SchemeConfigured`: Triggered when a new public scheme or policy rule is registered in the system.
* `RoleAssigned`: Generated when an administrator modifies user permissions or department boundaries.
* `SLAThresholdExceeded`: Published when an issue fails to be resolved within the legally mandated time limit.

### 7.6. Audit Events
* `SchemaChanged`: Triggered when the contract/schema of an event is officially updated.
* `AccessLogGenerated`: Generated when sensitive citizen PII is accessed or exported by an operator.
* `SystemConfigOverridden`: Published when critical runtime constants are modified.

### 7.7. Plugin Events
* `HookTriggered`: Generated when a core workflow phase calls a registered third-party extension hook.
* `PluginResponseReturned`: Published when a plugin successfully returns its output to the core coordinator.
* `PluginExecutionFailed`: Generated if a plugin times out or returns an uncaught error code.

---

## 8. Event Ownership

To maintain architectural sanity, event definitions are strictly bound to domain context boundaries:

* **Bounded Context Ownership:** The microservice or component that serves as the authority for a domain entity owns the schema definition for all events related to that entity. For example, the *Workflow Engine* owns the `IssueValidated` event schema.
* **Contract Evolution:** If a consuming service requires additional data inside an event, it cannot directly modify the payload. It must submit a request to the owning service team, who will govern the schema update via the Event Catalog and Schema Registry.

---

## 9. Event Versioning Strategy

As the Helix system evolves, event structures will change. We manage this evolution using a dual-versioning strategy:

```
Event Name: "IssueValidated"
┌─────────────────────────┐
│ Metadata Header         │ ──► Schema Version (e.g., "1.2.0")
├─────────────────────────┤
│ Payload                 │ ──► Backward compatible additions only
└─────────────────────────┘
```

1. **Schema Versioning:** Every event header must contain a schema version string (using Semantic Versioning, e.g., `1.2.0`).
2. **Backward-Compatible Changes (Minor/Patch):** Adding optional fields, adding metadata headers, or renaming internal structures via aliases are minor/patch changes. Consumers must ignore unrecognized fields rather than crash (Robustness Principle).
3. **Breaking Changes (Major):** Removing fields, changing field types (e.g., string to integer), or changing structural meaning are breaking changes. In these cases:
   - A new major schema version is published (e.g., `2.0.0`).
   - The event name remains the same, but the header version flag shifts.
   - For transition periods, the producer must dual-publish both the old major version and new major version, or the event bus must support transformation adapters.

---

## 10. Event Ordering Philosophy

In a distributed environment, global event ordering is impossible without severely sacrificing availability and latency. Helix balances this trade-off using **Key-Based Ordering**:

* **No Global Order:** Events are not globally ordered across the entire platform.
* **Strict Partitioned Order:** Events sharing the same **Ordering Key** are guaranteed to be delivered and processed in the exact order they were written.
* **Determining Keys:** The ordering key must match the core operational entity. For example, the ordering key for all workflow events is the `issue_id`. This guarantees that `IssueValidated` is always processed before `EvidenceAttached` and `DecisionApproved` for any single issue, even if events for *different* issues are processed concurrently.

---

## 11. Idempotency Principles

In distributed systems, networks can fail during message acknowledgements, leading to duplicate delivery (at-least-once delivery semantics). Helix assumes an **At-Least-Once Delivery Model**, which requires all event consumers to be strictly **idempotent**.

* **Unique Event Identifiers:** Every event is generated with a cryptographically secure, unique UUID (the `event_id`) in its metadata header.
* **Idempotency Keys:** Transactions that modify database state must check if the `event_id` has already been processed.
* **State Guarding:** Consumers should check current entity state before applying mutations. For instance, if an event consumer receives `DepartmentAssigned` but the local database indicates the department has already been assigned and worked on, the consumer must silently ignore the event and acknowledge receipt.
* **Outbox Deduplication:** Consumer persistence layers must maintain a dedup-log (or transaction log) of recently processed event IDs for a retention window (e.g., 7 days) to filter out duplicate network packets.

---

## 12. Retry Philosophy

Temporary network drops, lock contentions, or downstream API timeouts must not stall the event delivery pipeline. Helix employs a non-blocking retry hierarchy:

```
[Main Event Stream]
       │
       ▼ (Process Fails)
[Retry Channel (Exp Backoff + Jitter)] ──► Max Retries Exceeded? ──► [Dead Letter Queue]
```

1. **Immediate Retry:** For transient local failures (e.g., database lock acquisition), the consumer may retry up to 3 times with sub-second intervals.
2. **Delayed Retry Channel:** If the failure persists, the consumer must capture the event, log the error, and push it to a secondary retry channel. The consumer then acknowledges the event on the main stream to avoid blocking subsequent events.
3. **Exponential Backoff with Jitter:** The retry channel processes the failed event using exponential backoff (e.g., 2s, 4s, 8s, 16s...) with added random jitter. This prevents "thundering herd" patterns against downstream dependencies.
4. **Max Retry Boundary:** Events are limited to a maximum number of retries (typically 5 to 10). If the maximum limit is reached, the event transitions to the Dead Letter Queue.

---

## 13. Dead Letter Strategy

A **Dead Letter Queue (DLQ)** is a specialized quarantine store for messages that cannot be processed successfully after exhausting all retries, or that fail validation due to corruption.

* **Isolation:** Each logical event consumer must have its own dedicated DLQ to prevent debugging confusion.
* **Enrichment:** When moving an event to the DLQ, the framework must wrap the original event with a metadata envelope containing:
  - The consuming service name and host ID.
  - The timestamp of the failure.
  - The exact exception stack trace or failure reason.
  - The number of retry attempts made.
* **No Auto-Discard:** DLQ events must never be automatically discarded. They must persist until manual intervention or automated diagnostic playbooks resolve them.
* **Alerting:** Writing to a DLQ triggers high-priority operational alerts for the engineering team.
* **Operational Portal:** Administrators must be provided with tools to inspect DLQ payloads, fix code or downstream data conditions, and re-enqueue the event for processing.

---

## 14. Event Replay Strategy

Because the event stream stores the history of facts, we can recover and rebuild state by replaying events:

* **Read Model Recreation:** If a database schema changes or a new analytics model is introduced, Helix can spin up a new database instance and replay events from the genesis timestamp to rebuild the index from scratch.
* **Disaster Recovery:** In the event of catastrophic data corruption, we can restore database snapshots from a known good date and replay subsequent events to recover without data loss.
* **Time-Travel Debugging:** Developers can spin up a local container environment and replay a specific sequence of production events to trace and debug complex workflow issues in isolation.

---

## 15. Long Running Workflows

Public governance workflows are long-running state machines spanning days or months. We govern these using the **Saga Pattern**:

```
            [Orchestrator: Workflow Engine]
             /            |            \
    (Assign Dept)   (Attach Evidence)   (Notify Citizen)
```

* **Choreographed Sagas:** For simple, short chains of interactions, components interact implicitly (e.g., Service A emits Event A, Service B listens and emits Event B).
* **Orchestrated Sagas (Helix Standard):** For core governance workflows, Helix uses Orchestrated Sagas managed by the **Workflow Engine**. The Workflow Engine acts as the coordinator. It listens to domain events, tracks the overall progress state of an issue, and publishes command-like events (e.g., `AssignDepartmentCommand`) to direct individual services.
* **Compensating Transactions:** Sagas do not use traditional database locks. If a step fails halfway (e.g., the assigned department rejects the task because of an incorrect boundary assignment), the Orchestrator emits compensating events to roll back the logical state (e.g., emitting `DepartmentAssignmentReverted`) and alerts operators to re-route.

---

## 16. Event Security

Because governance events carry citizen reports and administrative decisions, they are a primary target for security and privacy vectors:

* **PII Protection (Crypto Shredding):** Personal Identifiable Information (PII) inside events must be encrypted using keys specific to that citizen. If a citizen invokes their "right to be forgotten" (Helix Law 5), the system deletes their specific decryption key, rendering the historical event payload unreadable ("crypto-shredded") without altering the immutable event log. Legal retention requirements may override deletion requests where required by applicable law.
* **Transport Encryption:** All events in transit across logical containers must be encrypted using mutual Transport Layer Security (mTLS).
* **Access Control Lists (ACLs):** Consumers must be authenticated and authorized. The event bus enforces ACLs determining which containers can write to and read from specific event channels.
* **Digital Signatures:** Critical events (such as `DecisionApproved` or `RoleAssigned`) must be cryptographically signed by the producing container or user identity, preventing spoofing or tampering within the cluster.

---

## 17. Event Governance

With hundreds of events flowing across the system, strict governance is mandatory to prevent dependency chaos:

* **Event Catalog:** A single, schema-documented repository that lists every active event type, its purpose, its owner, its schema definitions, and consumer dependencies.
* **Schema Registry Enforcement:** The event bus integrates with a schema registry. When a producer attempts to publish, the event bus validates the schema version identifier. Publications that do not match the registry are blocked.
* **Deprecation Policy:** When an event is replaced, its schema is marked as "Deprecated." It must remain active and supported for a minimum duration (e.g., two minor releases) before being removed, allowing downstream consumers time to migrate.

---

## 18. Design Validation Checklist

Before freezing any downstream component or microservice specification, the architect must validate it against this checklist:

* [ ] **Immutable History:** Does the component design assume that database records can be updated without generating a corresponding historical event? (If yes, redesign to emit events).
* [ ] **Idempotent Consumers:** Can every event consumer handle the exact same event payload multiple times without creating duplicate side-effects?
* [ ] **Error Isolation:** Are retries non-blocking? Is there a dedicated Dead Letter Queue configured for every consumer class?
* [ ] **Partition Key Specified:** Does every event schema specify an appropriate ordering key (e.g., `issue_id`) to ensure sequence consistency?
* [ ] **PII Classification:** Are fields containing personal data flagged and encrypted using the tenant/user keys to support crypto-shredding?
* [ ] **Broker Independence:** Does the design rely on specific broker features (like native Kafka transactions or RabbitMQ exchanges), or is it abstract enough to be implemented on any modern message transport?
* [ ] **Compensating Logic:** For multi-step workflows, is there a clear compensating path documented if downstream steps fail?
