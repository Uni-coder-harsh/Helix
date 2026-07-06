import uuid

import pytest

from services.governance.application.intelligence import (
    EvidenceAggregator,
    ImpactEngine,
    PriorityEngine,
    RecommendationBuilder,
    UrgencyEngine,
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
from shared.domain.enums import Priority


@pytest.fixture
def test_knowledge_service() -> KnowledgeService:
    policy_store = InMemoryPolicyStore()
    scheme_store = InMemorySchemeStore()
    asset_store = InMemoryAssetStore()
    hierarchy = InMemoryAdministrativeHierarchy()
    dept_store = InMemoryDepartmentStore()
    search_engine = InMemoryKnowledgeSearch(policy_store, scheme_store, asset_store)

    return KnowledgeService(
        policies=policy_store,
        schemes=scheme_store,
        assets=asset_store,
        hierarchy=hierarchy,
        departments=dept_store,
        search=search_engine,
    )


def test_urgency_engine_calculation(test_knowledge_service: KnowledgeService) -> None:
    engine = UrgencyEngine(test_knowledge_service)
    # Proximity near playground coordinates (12.9716, 77.5946)
    score = engine.calculate_urgency("sanitation", 12.9716, 77.5946)
    assert score == pytest.approx(0.9)  # 0.4 base + 0.3 category + 0.2 asset proximity


def test_impact_engine_evaluation(test_knowledge_service: KnowledgeService) -> None:
    engine = ImpactEngine(test_knowledge_service)
    impact = engine.estimate_impact("roads", 12.9750, 77.5990)
    assert impact["affected_population"] == 1200
    assert impact["impact_level"] == "HIGH"


def test_priority_engine_resolution() -> None:
    # High urgency + High impact -> High Priority
    p1 = PriorityEngine.determine_priority(0.9, "HIGH")
    assert p1 == Priority.HIGH

    # Low urgency + Low impact -> Low Priority
    p2 = PriorityEngine.determine_priority(0.3, "LOW")
    assert p2 == Priority.LOW


def test_evidence_aggregation(test_knowledge_service: KnowledgeService) -> None:
    aggregator = EvidenceAggregator(test_knowledge_service)
    evidence = aggregator.aggregate_evidence("sanitation", 12.9716, 77.5946)
    assert len(evidence) > 0
    assert any("Asset Proximity" in ev for ev in evidence)


def test_recommendation_builder_generation(
    test_knowledge_service: KnowledgeService,
) -> None:
    builder = RecommendationBuilder(test_knowledge_service)
    issue_id = uuid.uuid4()
    recommendation = builder.build_recommendation(
        issue_id=issue_id,
        category="sanitation",
        latitude=12.9716,
        longitude=77.5946,
    )

    assert recommendation["priority"] == Priority.HIGH
    assert recommendation["suggested_department"] == "Municipal Sanitation Department"
    assert recommendation["confidence"] == 0.95
    assert len(recommendation["supporting_evidence"]) > 0
    assert "Sanitation Waste Management" in recommendation["reasoning_chain"]
