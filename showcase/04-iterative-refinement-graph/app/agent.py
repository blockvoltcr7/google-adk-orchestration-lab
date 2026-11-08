"""ADK Composition root for the cyclic iterative refinement graph."""

from google.adk.apps import App
from google.adk.workflow import Workflow, START
from app.nodes import (
    draft_specification,
    evaluate_spec_quality,
    publish_specification,
)

root_agent = Workflow(
    name="spec_refinement_graph",
    description="Iterative refinement cyclic graph with evaluation gate and loop guards",
    edges=[
        (START, draft_specification),
        (draft_specification, evaluate_spec_quality),
        (
            evaluate_spec_quality,
            {
                "refine": draft_specification,
                "publish": publish_specification,
            },
        ),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
