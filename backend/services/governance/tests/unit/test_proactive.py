from helix_platform.persistence import SessionLocal
from services.governance.application.proactive import ProactiveIntelligenceService
from services.governance.infrastructure.queries import SQLAlchemyGovernanceQueryService


def test_proactive_briefing_generation() -> None:
    db = SessionLocal()
    query_svc = SQLAlchemyGovernanceQueryService(db)
    proactive_svc = ProactiveIntelligenceService(query_svc)

    briefing = proactive_svc.get_morning_briefing()

    assert briefing["overall_health_score"] == 78
    assert "Central Bengaluru" in briefing["constituency"]
    assert "Good Morning MLA" in briefing["morning_brief"]
    assert len(briefing["category_forecasts"]) == 3
    assert len(briefing["risk_alerts"]) >= 0
