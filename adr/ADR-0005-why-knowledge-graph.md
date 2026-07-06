# ADR-0005: Why Knowledge Graph?

## Status
Accepted

## Date
2026-07-06

## Context
Civic governance information is deeply interconnected. A citizen's report exists in a specific ward, links to a public infrastructure asset, is governed by municipal policy circulars, relies on public funding schemes, and is assigned to a department official.
To build an effective governance system, we must:
* **Trace Systemic Issues:** Identify when twenty individual water complaints are actually caused by a single broken water main upstream.
* **Ground AI Recommendations:** Ground LLM queries in actual policy documents, department jurisdictions, and historical precedents to prevent AI hallucinations.
* **Evaluate Program Outcomes:** Measure the long-term impact of municipal schemes on specific geographical sectors.

## Alternatives Considered

### Alternative 1: Pure Relational Database (SQL-Only)
* **Description:** Storing all structural relations in a standard relational database with foreign key relationships.
* **Pros:** Highly understood technology; strict transaction guarantees; easy to run standard operational queries.
* **Cons:** Running multi-hop recursive queries (e.g. "Find all officers who have worked on issues related to schemes that are funded by budget X") results in extremely slow, complex SQL JOIN statements; rigid schemas make it hard to dynamically add new entity types (e.g. a new civic asset class).

### Alternative 2: Pure Vector Database
* **Description:** Storing all documents, reports, and policies as vector embeddings and querying them via cosine similarity.
* **Pros:** Easy to set up for simple semantic search or basic RAG.
* **Cons:** Completely lacks structure; cannot trace logical chains of authority (e.g. "Officer A reports to Officer B who manages Ward C"); semantic retrieval often brings back irrelevant context and fails to respect legal boundaries.

### Alternative 3: Polyglot Persistence (Operational Relational DB + Knowledge Graph)
* **Description:** Using a standard relational database for high-write operational transactions (e.g. logging active tasks, user sessions), and propagating facts asynchronously to a Knowledge Graph (Graph Database) to model deep connections, policy rules, and hierarchical relationships.
* **Pros:** The best of both worlds: robust ACID transactions for day-to-day operations and highly performant, flexible relationship traversals for AI grounding, systemic clustering, and analytics.
* **Cons:** Added complexity of running, sync-maintaining, and securing two separate database systems.

## Decision
We chose **Polyglot Persistence with a Knowledge Graph** as the primary relational query and grounding mechanism.

By maintaining a graph-structured model of the governance domain:
1. The **AI Orchestrator** can perform Graph-Retrieval Augmented Generation (Graph-RAG), ensuring that it answers user questions by navigating actual legal policy nodes rather than guessing.
2. The **Analytics Service** can easily run graph clustering algorithms to group isolated citizen reports into parent systemic problems.
3. Municipal administrators can visualize and audit the connections between funding, departments, and citizen satisfaction across geographical regions.

## Consequences
* **Positive:**
  * High-performance, multi-hop relationship queries that are impossible or slow in standard SQL.
  * Flexibility to dynamically add new entities, policy changes, and geographic boundaries without executing complex database schema migrations.
  * High-trust, grounded AI outputs via structured context retrieval.
* **Negative/Trade-offs:**
  * Sync overhead: Changes in the operational database must be replicated to the Knowledge Graph asynchronously (via events).
  * Double querying: Developers must learn to query both databases and write synchronization/reconciliation logic.
