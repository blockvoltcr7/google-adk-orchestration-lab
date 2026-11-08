"""Tests for the deterministic graph-route evaluation metric."""

import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parents[1] / "eval"
sys.path.insert(0, str(EVAL_DIR))

from graph_route_policy import evaluate  # noqa: E402


def _instance(case_id: str, authors_and_text: list[tuple[str, str]]) -> dict:
    return {
        "eval_case_id": case_id,
        "agent_data": {
            "turns": [
                {
                    "turn_index": 0,
                    "events": [
                        {
                            "author": author,
                            "content": {"parts": [{"text": text}]},
                        }
                        for author, text in authors_and_text
                    ],
                }
            ]
        },
    }


def test_valid_route_metric_requires_specialists_and_success_evidence() -> None:
    result = evaluate(
        _instance(
            "complete_intake_valid_route",
            [
                (
                    "consultation_agent",
                    "Jordan Lee reported previous knee discomfort.",
                ),
                (
                    "welcome_agent",
                    "Use https://booking.example.com/fitness-consultation/example",
                ),
                (
                    "fitness_onboarding_graph",
                    "Jordan Lee onboarding. Local placeholder welcome email: sent.",
                ),
            ],
        )
    )
    assert result["score"] == 1


def test_invalid_route_metric_rejects_specialist_or_side_effect_evidence() -> None:
    result = evaluate(
        _instance(
            "incomplete_intake_invalid_route",
            [
                (
                    "fitness_onboarding_graph",
                    "The intake needs correction. email: field is required",
                )
            ],
        )
    )
    assert result["score"] == 1

    wrong_route = evaluate(
        _instance(
            "incomplete_intake_invalid_route",
            [
                ("consultation_agent", "A plan"),
                (
                    "fitness_onboarding_graph",
                    "The intake needs correction. email: field is required",
                ),
            ],
        )
    )
    assert wrong_route["score"] == 0
