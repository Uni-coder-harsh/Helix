import pytest

from services.governance.application.decision_brief.alternatives import (
    AlternativesEvaluator,
)
from services.governance.application.decision_brief.confidence import ConfidenceScorer
from services.governance.application.decision_brief.engine import DecisionBriefEngine
from services.governance.application.decision_brief.evidence import EvidenceExtractor
from services.governance.application.decision_brief.explanation import (
    ExplanationGenerator,
)


def test_confidence_scorer_deterministic_signals():
    # Test case 1: High signal values (high duplicate count, matched policy, nearby assets, large population)
    context_high = {
        "duplicate_count": 18,
        "matched_policy": "Sanitation Policy",
        "matched_scheme": "Swachh Bharat",
        "nearby_assets": ["School A"],
        "affected_population": 4320,
    }
    res_high = ConfidenceScorer.compute_confidence(context_high, llm_confidence=0.95)
    # 25 (dups) + 25 (policy) + 25 (assets) + 15 (pop) + 9 (llm) = 99
    assert res_high["overall"] == 99
    assert res_high["signals"]["duplicates"] == 25

    # Test case 2: Low signal values (no duplicates, no policy/scheme, no assets, no population)
    context_low = {"duplicate_count": 0, "nearby_assets": [], "affected_population": 0}
    res_low = ConfidenceScorer.compute_confidence(context_low, llm_confidence=0.0)
    assert res_low["overall"] == 50
    assert res_low["signals"]["duplicates"] == 5


def test_evidence_extractor():
    context = {
        "duplicate_count": 5,
        "nearby_assets": ["Govt School B", "Park Alpha"],
        "matched_policy": "Road Code 2023",
        "affected_population": 350,
    }
    evidence = EvidenceExtractor.extract_evidence(context)
    assert any("5 duplicate complaints" in ev["statement"] for ev in evidence)
    assert any("2 civic assets" in ev["statement"] for ev in evidence)
    assert any("Road Code 2023" in ev["statement"] for ev in evidence)
    assert any("350 citizens" in ev["statement"] for ev in evidence)

    # Asset extraction schema
    assets = EvidenceExtractor.get_nearby_assets(context)
    assert len(assets) == 2
    assert assets[0]["name"] == "Govt School B"
    assert assets[0]["type"] == "school"


def test_alternatives_evaluator():
    alts_sanit = AlternativesEvaluator.get_alternatives(
        "Water Supply & Sanitation", "Broken water pipe leak"
    )
    assert len(alts_sanit) == 3
    # Check recommended flag is present and maps correctly
    assert any(
        alt["is_recommended"] for alt in alts_sanit if "Capital" in alt["option_name"]
    )
    assert "confidence" in alts_sanit[0]
    assert "expected_impact" in alts_sanit[0]

    alts_roads = AlternativesEvaluator.get_alternatives(
        "Roads & Sidewalks", "Massive pothole cluster"
    )
    assert len(alts_roads) == 3
    assert any(
        alt["is_recommended"] for alt in alts_roads if "Overlay" in alt["option_name"]
    )


@pytest.mark.asyncio
async def test_explanation_generator_fallback():
    # When LLM is unavailable or offline
    generator = ExplanationGenerator()
    generator.llm = None  # Force offline fallback

    res = await generator.generate_explanation(
        category="Water Supply & Sanitation",
        title="Pipe Burst",
        description="Water leak drainage issue",
        context={},
    )

    assert "reasoning" in res
    assert "follow_up_actions" in res
    assert len(res["reasoning"]) > 0
    assert len(res["follow_up_actions"]["immediate"]) > 0
    assert res["llm_confidence"] == 0.94


@pytest.mark.asyncio
async def test_decision_brief_engine():
    engine = DecisionBriefEngine()
    issue = {
        "id": "mock-uuid-9999",
        "title": "Severe Water Leakage Shivaji Nagar",
        "description": "Massive water pipe leak pooling inside play school ground.",
        "category": "Water Supply & Sanitation",
        "latitude": 12.9755,
        "longitude": 77.5955,
        "status": "INGESTED",
        "priority": "HIGH",
    }

    brief = await engine.generate_brief(issue)

    # Assert JSON schema outputs
    assert brief["problem"]["id"] == "mock-uuid-9999"
    assert brief["problem"]["priority"] == "HIGH"
    assert len(brief["evidence"]) > 0
    assert len(brief["nearby_assets"]) > 0
    assert brief["confidence"]["overall"] > 50
    assert "reasoning" in brief
    assert "follow_up_actions" in brief
    assert "alternative_actions" in brief
    assert "brief_id" in brief
    assert "version" in brief
    assert "generated_at" in brief
