"""ADK Composition root for the conditional ticket routing graph."""

from google.adk.apps import App
from google.adk.workflow import Workflow, START, DEFAULT_ROUTE
from app.nodes import (
    triage_ticket,
    handle_billing,
    handle_technical,
    handle_account,
    handle_fallback,
    format_ticket_resolution,
)

root_agent = Workflow(
    name="service_desk_router_graph",
    description="Conditional routing graph for enterprise ticket triage",
    edges=[
        (START, triage_ticket),
        (
            triage_ticket,
            {
                "billing": handle_billing,
                "technical": handle_technical,
                "account": handle_account,
                DEFAULT_ROUTE: handle_fallback,
            },
        ),
        (handle_billing, format_ticket_resolution),
        (handle_technical, format_ticket_resolution),
        (handle_account, format_ticket_resolution),
        (handle_fallback, format_ticket_resolution),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
