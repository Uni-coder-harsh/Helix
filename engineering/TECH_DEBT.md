# Technical Debt Registry

This registry tracks code shortcuts, mock layers, and configurations deferred for later sprints to optimize velocity during the initial prototyping phase.

| Item ID | Date Logged | Description | Location | Impact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEBT-001** | 2026-07-06 | **Pydantic/Ruff Ignored Warnings** | Ignored Ruff rules (A002, B024, N818, E501, ARG, RET, SIM, PTH, UP, F401, E402) globally to support subagent style patterns. | `pyproject.toml` | Low (requires periodic audit) | Open |
| **DEBT-002** | 2026-07-06 | **Mock LLM Provider** | LLM responses in the AI validation suite use deterministic string matchers and mock embeddings instead of real API calls. | `backend/services/ai-platform/` | Medium (must be replaced by adapter keys) | Open |
| **DEBT-003** | 2026-07-06 | **In-memory RAG Vector Store** | Policy lookup uses basic cosine similarity over python arrays instead of a persistent vector database. | `backend/services/ai-platform/src/ai_platform/core/rag.py` | Low (sufficient for MVP scale) | Open |
| **DEBT-004** | 2026-07-06 | **Mock Frontend State** | Dashboards use a static mock dataset for analytics and map coordinate markers. | `frontend/src/lib/mock-data.ts` | High (requires endpoint fetching integrations) | Open |
