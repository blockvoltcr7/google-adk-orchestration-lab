"""Local LLM judge for the onboarding-specific response-quality metric."""

from google import genai
from google.genai import types
from pydantic import BaseModel


class _Verdict(BaseModel):
    score: int  # 1-5
    explanation: str


def evaluate(instance):
    rubric = (
        "Grade this fitness-client onboarding run from 1 to 5. "
        "For a complete intake, the trace should validate the intake, preserve all "
        "client facts and physical constraints, create a consultation plan, create "
        "a booking link, send a welcome email, and clearly confirm the outcome. "
        "For an incomplete intake, the trace should explain the actual validation "
        "errors and must not call booking or email tools. In every case, penalize "
        "invented client facts, medical diagnosis, treatment prescriptions, unclear "
        "responses, or claims not supported by tool results."
    )
    prompt = (
        f"You are an expert QA evaluator. {rubric}\n"
        f"User Prompt: {instance.get('prompt', '')}\n"
        f"Final Response: {instance.get('response', '')}\n"
        f"Full Agent Trace: {instance.get('agent_data', '')}\n"
        "Return a score and a concise explanation."
    )

    client = genai.Client()  # AI Studio (GEMINI_API_KEY) or Agent Platform (ADC)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,  # deterministic grading
            response_mime_type="application/json",
            response_schema=_Verdict,  # guaranteed schema-valid JSON
        ),
    )
    verdict = response.parsed
    if verdict is None:  # model returned nothing usable
        return {"score": 0, "explanation": response.text or ""}
    return {"score": max(1, min(5, verdict.score)), "explanation": verdict.explanation}
