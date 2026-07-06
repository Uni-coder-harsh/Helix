# ADR-0004: Why Human-in-the-Loop AI?

## Status
Accepted

## Date
2026-07-06

## Context
Helix integrates AI (Large Language Models, Embeddings, Clustering models) to handle high-volume citizen reports, automate classification, and suggest optimal resolution pathways. However, AI systems can hallucinate, exhibit bias, or misunderstand nuanced local contexts.
Because Helix governs public resources and legal timelines:
* Purely automated decisions lack public trust and legal accountability.
* Inappropriate automated routing can waste critical municipal engineer hours.
* The Helix Constitution (specifically Law 3: Human Oversight) mandates that AI must never hold final executive authority.

## Alternatives Considered

### Alternative 1: Fully Automated AI Decision Making (No Human Intervention)
* **Description:** AI classifies reports, assigns municipal departments, schedules tasks, and marks issues as resolved without human approval.
* **Pros:** Extremely fast; low operational cost; high throughput.
* **Cons:** High risk of incorrect actions; zero audit accountability; violates municipal legal frameworks; prone to malicious prompt injection or spoofing.

### Alternative 2: Traditional Rule-Based Hardcoding (No AI Orchestration)
* **Description:** Rely solely on hardcoded logic, keyword matching, and static lookup tables to route and process issues.
* **Pros:** Deterministic; fully understandable logic.
* **Cons:** Fragile; cannot handle unstructured multi-media data (audio files, images, conversational dialects) which represent the majority of citizen submissions.

### Alternative 3: Human-in-the-Loop (HITL) AI-Assisted Orchestration
* **Description:** AI operates as a processing and recommendation engine. It processes raw inputs, generates recommended routings, drafts replies, and clusters similar reports, but presents these as suggestions to a human operator for validation, rejection, or modification.
* **Pros:** High throughput of unstructured inputs combined with the safety, accountability, and corrective input of human officers; continuous learning loop as human overrides train downstream models.
* **Cons:** Slower processing times compared to fully automated pipelines; higher staff headcount needed for operational validation.

## Decision
We chose **Human-in-the-Loop (HITL) AI-Assisted Orchestration** as the design model for Helix.

By architecting AI services as advisory engines rather than controllers:
1. Every executive state change (e.g. `DepartmentAssigned`, `DecisionApproved`) requires explicit human signatures or validation.
2. AI-generated suggestions are clearly demarcated in the data stores and UI, and are traceable back to the source data.
3. If an AI service fails, the workflow gracefully falls back to a standard manual triage queue.

## Consequences
* **Positive:**
  * Compliance with legal standards and the Helix Constitution.
  * Robustness against prompt injection: even if an adversary tricks the AI, a human operator acts as a firewall.
  * Quality improvement: human corrections provide labelled training data to refine classification models over time.
* **Negative/Trade-offs:**
  * We must design explicit queue management portals for human operators to review and confirm AI outputs.
  * System latency is bounded by human reaction time rather than computer clock cycles.
