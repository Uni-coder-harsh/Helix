import json
from typing import Any

import pytest
from ai_platform.core.llm import LLMMessage, LLMProvider, LLMResponse

from helix_platform.persistence import SessionLocal
from services.governance.application.copilot import (
    GovernanceCopilotService,
    ResponseValidator,
)
from services.governance.application.knowledge_service import KnowledgeService
from services.governance.infrastructure.knowledge.stores import (
    InMemoryAdministrativeHierarchy,
    InMemoryAssetStore,
    InMemoryDepartmentStore,
    InMemoryKnowledgeSearch,
    InMemoryPolicyStore,
    InMemorySchemeStore,
)
from services.governance.infrastructure.queries import SQLAlchemyGovernanceQueryService


class MockLLMProvider(LLMProvider):
    """Mock LLM Provider returning structured JSON payloads for testing."""

    async def generate(
        self, messages: list[LLMMessage], _config: dict[str, Any] | None = None
    ) -> LLMResponse:
        user_msg = messages[-1].content

        # Formulate structured JSON response
        data = {
            "summary": f"Mocked response for prompt action: {user_msg.splitlines()[0]}",
            "evidence": ["Evidence Item A", "Evidence Item B"],
            "citations": ["Regulation XYZ", "Swachh Bharat Abhiyan Scheme"],
            "confidence": 0.98,
            "recommendations": ["Action step 1", "Action step 2"],
            "alternatives": ["Alternative Option A", "Alternative Option B"],
            "warnings": ["Warning SLA boundary check"],
        }
        return LLMResponse(
            content=json.dumps(data),
            raw_response={"status": "mocked"},
            usage={"total_tokens": 100},
            model_name="mock-model",
        )


@pytest.fixture
def mock_copilot_service() -> GovernanceCopilotService:
    policy_store = InMemoryPolicyStore()
    scheme_store = InMemorySchemeStore()
    asset_store = InMemoryAssetStore()
    hierarchy = InMemoryAdministrativeHierarchy()
    dept_store = InMemoryDepartmentStore()
    search = InMemoryKnowledgeSearch(policy_store, scheme_store, asset_store)

    knowledge_svc = KnowledgeService(
        policies=policy_store,
        schemes=scheme_store,
        assets=asset_store,
        hierarchy=hierarchy,
        departments=dept_store,
        search=search,
    )

    db = SessionLocal()
    query_svc = SQLAlchemyGovernanceQueryService(db)

    # Inject mock LLM Provider to avoid internet/API requirements
    return GovernanceCopilotService(
        knowledge_service=knowledge_svc,
        query_service=query_svc,
        llm_provider=MockLLMProvider(),
    )


@pytest.mark.asyncio
async def test_copilot_decision_summary(
    mock_copilot_service: GovernanceCopilotService,
) -> None:
    res = await mock_copilot_service.execute_query(action="decision_summary")
    assert (
        "Mocked response for prompt action: ACTION: DECISION_SUMMARY" in res["summary"]
    )
    assert res["confidence"] == 0.98
    assert len(res["evidence"]) == 2
    assert "📜 Enforced Policy: `Regulation XYZ`" in res["citations"]
    assert "💰 Linked Scheme: `Swachh Bharat Abhiyan Scheme`" in res["citations"]


@pytest.mark.asyncio
async def test_copilot_meeting_notes(
    mock_copilot_service: GovernanceCopilotService,
) -> None:
    res = await mock_copilot_service.execute_query(action="meeting_brief")
    assert "ACTION: MEETING_BRIEF" in res["summary"]


@pytest.mark.asyncio
async def test_copilot_citizen_reply(
    mock_copilot_service: GovernanceCopilotService,
) -> None:
    # Set up mock issue in SQLite memory db to retrieve it
    db = SessionLocal()
    query_svc = SQLAlchemyGovernanceQueryService(db)
    issues = query_svc.list_pending_issues()

    if issues:
        issue_id = str(issues[0]["id"])
        res = await mock_copilot_service.execute_query(
            action="citizen_reply",
            issue_id=issue_id,
            query_details={"language": "Kannada"},
        )
        assert "ACTION: CITIZEN_REPLY" in res["summary"]


def test_response_validator_fallback() -> None:
    bad_json = "{invalid json structure}"
    parsed = ResponseValidator.validate_and_parse(bad_json)
    assert parsed["confidence"] == 0.90
    assert "Simulated Copilot response" in parsed["summary"]
    assert len(parsed["citations"]) == 2
