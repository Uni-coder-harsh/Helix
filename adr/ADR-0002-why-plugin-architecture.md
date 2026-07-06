# ADR-0002: Why Plugin Architecture?

## Status
Accepted

## Date
2026-07-06

## Context
Helix aims to be a generic, open-source Governance Operating System. However, every city, municipality, and state has unique operational rules, department boundaries, external legacy databases, and communication channels.
The system needs to accommodate these localized requirements without cluttering the core codebase with custom, city-specific logic.

We require an extensibility model that supports:
* **Isolation:** Third-party extensions must not crash the core workflow engine.
* **Security:** Unverified code must not run with high-privilege access to critical systems.
* **Ease of Deployment:** Cities should be able to activate or deactivate features at runtime.

## Alternatives Considered

### Alternative 1: Core Customization (Branching & Hardcoding)
* **Description:** Forking the repository for each municipality and hardcoding their unique integrations (e.g. Bangalore fork, Mumbai fork).
* **Pros:** Simple to implement initially; no interface abstraction layer needed.
* **Cons:** Creating a maintenance nightmare; impossible to propagate core updates or security patches to forked repos; fragmented codebase.

### Alternative 2: Webhook-based Extension Model
* **Description:** The core system calls external HTTP webhooks exposed by localized services when specific workflow events occur.
* **Pros:** Standard web standard; simple for external services to host.
* **Cons:** High latency; relies heavily on external network stability; does not support complex workflow control or state-injected hooks easily.

### Alternative 3: Isolated Plugin Runtime (WebAssembly / Sandboxed Subprocesses)
* **Description:** The system defines explicit hook interfaces. Third-party logic is packaged as plugins that execute within an isolated container or WASM sandbox managed by the Plugin Runtime.
* **Pros:** Strong security boundary; code execution is deterministic; core is insulated from plugin failures; standard lifecycle interfaces.
* **Cons:** Extra complexity in packaging, distribution, and runtime sandboxing; data serialization overhead.

## Decision
We chose **Isolated Plugin Architecture (via Sandboxed Plugin Runtime)** as the extensibility model for Helix.

By isolating localization logic:
1. The Helix core remains clean, light, and technology-neutral.
2. Municipalities can safely write extensions in multiple languages (compiling to WASM or running in lightweight sidecar runtimes) to connect to legacy databases.
3. System stability is protected—if a plugin hangs or throws an error, the core Workflow Engine captures the failure, defaults to fallback logic, and continues operating.

## Consequences
* **Positive:**
  * Zero-downtime upgrades: Plugins can be loaded, upgraded, or disabled dynamically.
  * Shared ecosystem: Standard plugins (e.g. standard email integrations) can be shared across municipalities.
  * Security auditing: We can enforce strict sandbox resource and capability boundaries.
* **Negative/Trade-offs:**
  * Upfront design cost: We must specify and maintain strict Plugin SDK interfaces and contract versioning.
  * Performance overhead of sandboxed cross-boundary serialization.
