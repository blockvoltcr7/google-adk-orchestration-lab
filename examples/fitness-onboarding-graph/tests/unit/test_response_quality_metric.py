"""Tests for graph-aware judge prompt construction."""

import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parents[1] / "eval"
sys.path.insert(0, str(EVAL_DIR))

from onboarding_response_quality import _build_prompt  # noqa: E402


def test_judge_prompt_documents_graph_trace_semantics() -> None:
    prompt = _build_prompt(
        {
            "eval_case_id": "complete_intake_valid_route",
            "prompt": {"role": "user"},
            "response": {"role": "model"},
            "agent_data": {"turns": []},
        }
    )

    assert "omit deterministic function nodes" in prompt
    assert "do not require function_call parts" in prompt
    assert "local placeholder" in prompt
