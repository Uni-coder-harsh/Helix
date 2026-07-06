# Next Task: RFC for First Vertical Feature Slice

## Description
Prior to writing code for active business logic, we must write a compact RFC outlining the database schema, event triggers, and API contracts required for our first vertical slice.

## The Vertical Slice Goal
Verify the complete life cycle of an issue:
1. **Citizen submits an issue** (Intake boundary validates payload).
2. **Issue ingested and triaged** (Governance Service engine runs state transition).
3. **AI recommendation generated** (AI Platform Service computes policy context, checks compliance safety, and returns grounding score).
4. **Officer reviews proposal** (Officer Panel dashboard views recommendations and confirms triage).
5. **Issue progresses to Assigned/In-Progress** (Governance state update dispatched).
6. **Dashboard updates** (Decision intelligence captures status, updating live heatmaps).

## Definition of Done (DoD)
- [ ] RFC written and approved by Chief Architect.
- [ ] Database migrations defined for Governance Service transactional state tables.
- [ ] API endpoints defined for intake, recommendation list, decision signing, and analytics summaries.
- [ ] In-memory or network event bus routes events seamlessly between modules.
- [ ] Direct integration tests written mapping the entire workflow slice.
