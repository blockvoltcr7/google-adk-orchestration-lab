"""Dynamic orchestration root using @node(rerun_on_resume=True) and ctx.run_node."""

import json
from typing import Any
from google.adk.apps import App
from google.adk.workflow import node
from app.models import BatchDocumentInput
from app.nodes import analyze_section, synthesize_batch


def _parse_input(raw: Any) -> BatchDocumentInput:
    if isinstance(raw, dict):
        return BatchDocumentInput.model_validate(raw)
    text = getattr(raw, "text", None)
    if text is None and hasattr(raw, "parts"):
        text = "".join(getattr(p, "text", "") or "" for p in raw.parts)
    elif not isinstance(text, str):
        text = str(raw)
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        data = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            data = json.loads(text[start : end + 1])
        else:
            data = {
                "doc_id": "DOC-99",
                "title": "Default Document",
                "sections": [{"section_index": 1, "heading": "Intro", "content": "Clean text"}],
            }
    return BatchDocumentInput.model_validate(data)


@node(name="dynamic_batch_orchestrator", rerun_on_resume=True)
async def dynamic_batch_orchestrator(ctx, node_input: Any):
    """Dynamic orchestrator: schedules variable number of child nodes based on runtime input."""
    doc = _parse_input(node_input)

    results = []
    for section in doc.sections:
        # ctx.run_node handles child node invocation, checkpointing, and replay caching
        analysis = await ctx.run_node(analyze_section, node_input=section.model_dump())
        results.append(analysis)

    summary = await ctx.run_node(
        synthesize_batch,
        node_input={
            "doc_id": doc.doc_id,
            "title": doc.title,
            "analyses": results,
        },
    )
    return summary


root_agent = dynamic_batch_orchestrator

app = App(
    root_agent=root_agent,
    name="app",
)
