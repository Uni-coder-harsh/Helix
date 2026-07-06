from dataclasses import dataclass, field
from typing import Any

from ai_platform.engines.recommendation import RecommendationEngine
from ai_platform.evaluation.datasets import EvalCase


@dataclass
class EvalMetricResult:
    metric_name: str
    value: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalCaseResult:
    case_id: str
    name: str
    passed: bool
    expected_action: str
    actual_action: str
    expected_verdict: str
    actual_verdict: str
    confidence_score: float
    grounding_score: float
    safety_passed: bool
    metrics: list[EvalMetricResult] = field(default_factory=list)


@dataclass
class EvalSuiteResult:
    accuracy: float
    average_confidence: float
    average_grounding: float
    safety_compliance_rate: float
    case_results: list[EvalCaseResult]
    summary: str


class EvaluationSuite:
    """
    Automated evaluation framework for testing and scoring different recommendation engines,
    model prompts, and safety guards.
    """

    def __init__(self, cases: list[EvalCase]) -> None:
        self.cases = cases

    async def run_suite(self, engine: RecommendationEngine) -> EvalSuiteResult:
        case_results = []
        passed_count = 0
        total_confidence = 0.0
        total_grounding = 0.0
        total_safe_cases = 0

        for case in self.cases:
            recommendation = await engine.generate_recommendation(
                issue_id=case.case_id,
                issue_content=case.issue_content,
                metadata=case.metadata,
                files=case.evidence_files,
            )

            # Audit assertions
            action_match = recommendation.suggested_action == case.expected_action
            verdict_match = recommendation.reasoning.verdict == case.expected_verdict
            passed = action_match and verdict_match

            if passed:
                passed_count += 1

            total_confidence += recommendation.confidence_score
            total_grounding += recommendation.grounding_score
            if recommendation.safety_passed:
                total_safe_cases += 1

            # Compile granular metrics
            metrics = [
                EvalMetricResult(
                    metric_name="action_accuracy",
                    value=1.0 if action_match else 0.0,
                    details={
                        "expected": case.expected_action,
                        "actual": recommendation.suggested_action,
                    },
                ),
                EvalMetricResult(
                    metric_name="verdict_accuracy",
                    value=1.0 if verdict_match else 0.0,
                    details={
                        "expected": case.expected_verdict,
                        "actual": recommendation.reasoning.verdict,
                    },
                ),
                EvalMetricResult(
                    metric_name="grounding_compliance",
                    value=recommendation.grounding_score,
                    details={
                        "warnings": recommendation.metadata.get(
                            "grounding_warnings", []
                        )
                    },
                ),
            ]

            case_results.append(
                EvalCaseResult(
                    case_id=case.case_id,
                    name=case.name,
                    passed=passed,
                    expected_action=case.expected_action,
                    actual_action=recommendation.suggested_action,
                    expected_verdict=case.expected_verdict,
                    actual_verdict=recommendation.reasoning.verdict,
                    confidence_score=recommendation.confidence_score,
                    grounding_score=recommendation.grounding_score,
                    safety_passed=recommendation.safety_passed,
                    metrics=metrics,
                )
            )

        total_cases = len(self.cases)
        accuracy = float(passed_count) / float(total_cases) if total_cases > 0 else 0.0
        avg_confidence = (
            float(total_confidence) / float(total_cases) if total_cases > 0 else 0.0
        )
        avg_grounding = (
            float(total_grounding) / float(total_cases) if total_cases > 0 else 0.0
        )
        safety_compliance = (
            float(total_safe_cases) / float(total_cases) if total_cases > 0 else 0.0
        )

        summary = (
            f"Evaluation complete. Ran {total_cases} cases. "
            f"Passed: {passed_count}/{total_cases} (Accuracy: {accuracy * 100.0:.2f}%). "
            f"Avg Grounding: {avg_grounding:.4f}. Safety Rate: {safety_compliance * 100.0:.2f}%."
        )

        return EvalSuiteResult(
            accuracy=round(accuracy, 4),
            average_confidence=round(avg_confidence, 4),
            average_grounding=round(avg_grounding, 4),
            safety_compliance_rate=round(safety_compliance, 4),
            case_results=case_results,
            summary=summary,
        )
