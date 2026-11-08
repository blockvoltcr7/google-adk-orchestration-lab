"""Graph-aware local LLM judge for onboarding response quality."""

import json
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class _Verdict(BaseModel):
    passed: bool
    score: int = Field(ge=1, le=5)
    explanation: str


def _build_prompt(instance: dict[str, Any]) -> str:
    """Build the judge prompt with explicit ADK graph trace semantics."""
    return (
        "Evaluate this qualified fitness-client onboarding graph on a 1-5 scale. "
        "Google ADK graph traces omit deterministic function nodes from conversational "
        "events, so do not require function_call parts. Infer successful local booking "
        "and email nodes only when the final response contains their production-shaped "
        "placeholder results and the trace follows the expected agent route.\n\n"
        "A passing valid case must: show consultation_agent then welcome_agent then the "
        "root response; preserve the supplied name, goal, and physical constraints; "
        "include a booking.example.com URL; label booking and email as local placeholder "
        "results; and avoid diagnosis, treatment, or invented facts.\n"
        "A passing invalid case must: contain only the root response; identify missing "
        "fields; contain no booking URL or sent-email claim; and avoid exposing an email "
        "address or unnecessary personal details.\n\n"
        f"Case id: {instance.get('eval_case_id')}\n"
        f"User prompt: {json.dumps(instance.get('prompt'), default=str)}\n"
        f"Final response: {json.dumps(instance.get('response'), default=str)}\n"
        f"Full graph trace: {json.dumps(instance.get('agent_data'), default=str)}\n"
    )


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    """Judge graph-aware response quality using the configured Gemini backend."""
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=_build_prompt(instance),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=_Verdict,
        ),
    )
    verdict = response.parsed
    if verdict is None:
        return {"score": 0, "explanation": response.text or "No judge response"}
    return {
        "score": 1 if verdict.passed and verdict.score >= 4 else 0,
        "explanation": f"{verdict.score}/5: {verdict.explanation}",
    }
