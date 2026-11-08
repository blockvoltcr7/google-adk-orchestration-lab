"""ADK Composition root for the explicit fan-in graph with JoinNode."""

from google.adk.apps import App
from google.adk.workflow import Workflow, START, JoinNode
from app.nodes import (
    analyze_financials,
    evaluate_competitors,
    audit_compliance,
    synthesize_executive_dossier,
)

gather_diligence = JoinNode(name="gather_diligence")

root_agent = Workflow(
    name="due_diligence_graph",
    description="Explicit fan-out and JoinNode barrier for multi-source due diligence",
    edges=[
        (START, analyze_financials, gather_diligence),
        (START, evaluate_competitors, gather_diligence),
        (START, audit_compliance, gather_diligence),
        (gather_diligence, synthesize_executive_dossier),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
