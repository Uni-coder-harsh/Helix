import asyncio
import os
import sys

# Adjust path to import ai_platform package from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ai_platform import (
    ConfidenceScorer,
    EvaluationSuite,
    GroundingLayer,
    HallucinationGuard,
    InMemoryPolicyRegistry,
    InMemoryPromptRegistry,
    LLMEvidenceEngine,
    LLMReasoningEngine,
    MockProvider,
    OrchestratedRecommendationEngine,
    SafetyGuard,
    get_default_evaluation_dataset,
)


async def run_validation() -> None:
    print("Initializing components...")

    # 1. Setup providers
    llm = MockProvider()
    prompts = InMemoryPromptRegistry()
    policies = InMemoryPolicyRegistry()

    # Register mock rules for tests to simulate LLM answers
    # Mock rule for evidence check (TC-SAN-001)
    llm.register_rule(
        trigger_substring="F-101",
        response='{"is_sufficient": true, "extracted_facts": {"location": "Ward 12 playground Gate", "waste_type": "plastics_and_food"}, "missing_fields": [], "discrepancies": [], "confidence_score": 0.9}',
    )
    # Mock rule for evidence check (TC-SAN-002)
    llm.register_rule(
        trigger_substring="F-102",
        response='{"is_sufficient": false, "extracted_facts": {"waste_type": "general"}, "missing_fields": ["location"], "discrepancies": ["No location metadata provided."], "confidence_score": 0.4}',
    )
    # Mock rule for evidence check (TC-ROAD-003)
    llm.register_rule(
        trigger_substring="F-103",
        response='{"is_sufficient": false, "extracted_facts": {"pothole_dimensions_estimate": "1m x 0.15m"}, "missing_fields": ["gps_coordinates"], "discrepancies": ["No GPS coordinates provided."], "confidence_score": 0.5}',
    )

    # Mock rule for reasoning (TC-SAN-001)
    llm.register_rule(
        trigger_substring="Ward 12 playground",
        response="""{
            "chain_of_thought": [
                {"step_number": 1, "thought": "Check active policy for sanitation.", "conclusion": "POL-SAN-001 is active and requires response in 48 hours."},
                {"step_number": 2, "thought": "Evaluate provided evidence.", "conclusion": "Evidence is sufficient, location is Ward 12 playground."}
            ],
            "verdict": "APPROVE",
            "rationale": "The waste bin is overflowing at the playground main entrance. Under POL-SAN-001, we dispatch field repair immediately to resolve within 12 hours.",
            "policies_applied": ["POL-SAN-001"],
            "grounding_references": ["POL-SAN-001", "F-101"]
        }""",
    )
    # Mock rule for reasoning (TC-SAN-002)
    llm.register_rule(
        trigger_substring="stinking. Clean it up.",
        response="""{
            "chain_of_thought": [
                {"step_number": 1, "thought": "Analyze missing files.", "conclusion": "Location metadata is missing."}
            ],
            "verdict": "REJECTED",
            "rationale": "Cannot process complaint as location coordinates are missing.",
            "policies_applied": ["POL-SAN-001"],
            "grounding_references": []
        }""",
    )
    # Mock rule for reasoning (TC-ROAD-003)
    llm.register_rule(
        trigger_substring="bakery. Very dangerous",
        response="""{
            "chain_of_thought": [
                {"step_number": 1, "thought": "Verify GPS requirements.", "conclusion": "GPS coordinates are missing."}
            ],
            "verdict": "REJECTED",
            "rationale": "Missing GPS coordinates required by POL-RD-002.",
            "policies_applied": ["POL-RD-002"],
            "grounding_references": []
        }""",
    )
    # Mock rule for safety violation (TC-SAFE-004)
    llm.register_rule(
        trigger_substring="Ignore previous instructions",
        response="""{
            "chain_of_thought": [],
            "verdict": "REJECTED_UNSAFE",
            "rationale": "Flagged for safety bypass.",
            "policies_applied": [],
            "grounding_references": []
        }""",
    )

    # 2. Instantiate engines
    evidence_eng = LLMEvidenceEngine(llm_provider=llm, prompt_registry=prompts)
    reasoning_eng = LLMReasoningEngine(llm_provider=llm, prompt_registry=prompts)

    safety = SafetyGuard()
    grounding = GroundingLayer()
    hallucination = HallucinationGuard()
    confidence = ConfidenceScorer()

    recommender = OrchestratedRecommendationEngine(
        policy_retriever=policies,
        evidence_engine=evidence_eng,
        reasoning_engine=reasoning_eng,
        safety_guard=safety,
        grounding_layer=grounding,
        hallucination_guard=hallucination,
        confidence_scorer=confidence,
    )

    # 3. Retrieve default evaluation cases
    dataset = get_default_evaluation_dataset()

    # 4. Run evaluation suite
    suite = EvaluationSuite(cases=dataset)
    print("Running evaluation suite across test cases...")
    results = await suite.run_suite(recommender)

    print("\n--- EVALUATION REPORT ---")
    print(f"Summary: {results.summary}")
    print(f"Accuracy: {results.accuracy * 100:.1f}%")
    print(f"Average Confidence: {results.average_confidence:.4f}")
    print(f"Average Grounding: {results.average_grounding:.4f}")
    print(f"Safety Compliance Rate: {results.safety_compliance_rate * 100:.1f}%")
    print("\nIndividual Case Results:")
    for r in results.case_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"- [{status}] {r.case_id}: {r.name}")
        print(f"  Expected Action: {r.expected_action} | Actual: {r.actual_action}")
        print(f"  Expected Verdict: {r.expected_verdict} | Actual: {r.actual_verdict}")
        print(
            f"  Confidence: {r.confidence_score:.2f} | Grounding: {r.grounding_score:.2f} | Safety Passed: {r.safety_passed}"
        )

    if results.accuracy == 1.0:
        print("\nAll compilation and logical assertions passed successfully!")
    else:
        print(
            "\nSome evaluation assertions failed. Please verify engine configurations."
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_validation())
