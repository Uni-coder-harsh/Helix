---
status: "Frozen"
version: "1.0.0"
owner: "@harsh"
reviewers: "Architecture Review Board"
last_updated: "2026-07-05"
dependencies: ["HELIX-SPEC-000"]
related_adr: []
related_rfc: []
related_requirements: []
doc_type: "Explanation"
diataxis_category: "Explanation"
lifecycle: "Frozen"
---

# The Helix Constitution: The Twelve Laws of Helix

The Helix Constitution defines the non-negotiable core laws that govern the product development, system architecture, and engineering culture of Project Helix. Every contributor must read, understand, and adhere to these laws before contributing to the codebase or documentation.

---

## The Twelve Laws

### Law 1: Citizens should never learn government workflows.
**Government workflows must adapt to the citizen.**
Public systems must be designed around the citizen's existing capabilities, languages, and channels. The citizen should never be forced to navigate departmental siloes, download proprietary applications, or understand bureaucratic jargon. Interface flexibility is the system's responsibility; compliance is handled under the hood.

### Law 2: Every recommendation must be explainable.
**No black-box recommendations.**
Any automated response draft, issue categorization, or prioritization score must be accompanied by its logical trace and direct policy citations. If the logic cannot be traced back to verified data or policy documents, the recommendation is structurally invalid and must not be presented to administrators.

### Law 3: Every decision must preserve human authority.
**AI recommends, never decides.**
No automated routine possesses the authority to commit public funds, dispatch services, deploy personnel, or publish official communications autonomously. Helix acts as a cognitive amplifier. All transactional modifications must be approved and signed off by an authenticated human operator.

### Law 4: Every interaction strengthens institutional memory.
**Capture context continuously.**
Every grievance resolution, community interaction, and policy update must feed back into a persistent, privacy-preserving Knowledge Graph. This cumulative memory ensures that knowledge is not lost when public office staff rotates, providing incoming officials with years of context immediately.

### Law 5: Configuration over customization.
**Adapt dynamically, code statically.**
All geographic, linguistic, regulatory, and procedural differences between deployment sites must be handled via configuration layers, templates, and dynamic schemas. Code modifications should only happen to introduce new core features or optimizations, never to customize the system for a specific constituency.

### Law 6: Plugins over forks.
**Extend via interfaces.**
Integrations with third-party messaging services, AI models, vector stores, and transaction systems must use defined, sandboxed plugin boundaries. We do not fork the repository or modify the core orchestration services to adapt to regional provider differences.

### Law 7: No duplicated truth.
**Ensure absolute consistency.**
Every data entity, system state, and policy model must reside in a single, authoritative database or index. Redundant caching or duplicate state machines are prohibited across microservices to prevent data drift and out-of-sync states.

### Law 8: Evidence before intelligence.
**Grounded facts over speculative reasoning.**
Helix prioritizes verified evidence (e.g., geolocated media, direct policy texts) over speculative AI outputs. If a retrieved set of context documents is insufficient to construct a factual, verifiable answer, the system is prohibited from answering or extrapolating.

### Law 9: Accessibility is mandatory.
**Equitable design by default.**
Access to public services is a fundamental right. Helix administrative consoles and citizen integration flows must natively support speech interfaces, screen readers, high contrast, and simplified user pathways, conforming strictly to WCAG 2.2 AAA guidelines.

### Law 10: Everything observable.
**No blind spots in execution.**
Every transaction, API call, message routing, and model execution trace must export telemetry data. Latency spans, error rates, queue depths, and AI confidence levels must be monitorable in real-time.

### Law 11: Documentation is part of the product.
**No specification, no implementation.**
Documentation is not an afterthought; it is an active deliverable. Changes to the codebase are considered incomplete until the corresponding specs, references, and manuals are updated and compiled in the Engineering Portal.

### Law 12: Production quality from Day One.
**No temporary hacks in production branches.**
All code committed to the repository must feature type compliance, comprehensive testing, secure credentials management, and lint compliance. We do not compromise codebase integrity for short-term convenience.
